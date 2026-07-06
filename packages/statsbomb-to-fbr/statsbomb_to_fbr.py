#!/usr/bin/env python3
"""
statsbomb_to_fbr.py — convierte un partido de StatsBomb Open Data al formato FBR 1.0
con el modelo de identidad completo de FBR (persona / slot / ocupación).

Mapeo:
  · 11 SLOTS por equipo (H01..H11 / A01..A11), como en el estándar: el slot es la
    "camiseta en cancha"; las sustituciones cambian a su ocupante, no crean actores.
  · El track de un slot = keyframes del titular hasta el cambio + keyframes del
    suplente después (posiciones on-ball de los eventos de cada persona).
  · Eventos: goles, tarjetas y sustituciones (con `subs` {in, out, slot}).
  · El marcador se recomputa de los goles. La tanda de penales se excluye.

Limitación honesta: son posiciones ON-BALL (los datos de eventos no traen tracking
continuo); entre toques, FBR interpola. Es el caso de uso disperso del formato.

Uso:
  python3 statsbomb_to_fbr.py <events.json> <lineups.json> \
      --home "Argentina" --away "France" --date 2022-12-18 \
      --match-id 3869685 --competition "FIFA World Cup 2022" --out partido.fbr.json
"""
import argparse, json, sys

def norm_xy(loc, flipped=False):
    x, y = loc[0], loc[1]
    if flipped: x, y = 120.0-x, 80.0-y          # StatsBomb da coordenadas en el marco del
    return round(x/120.0, 4), round(y/80.0, 4)  # equipo del evento; volteamos al visitante
def t_of(e): return e.get("minute", 0)*60 + e.get("second", 0)
def dedup(kfs):
    out={}
    for t,x,y in sorted(kfs, key=lambda k:k[0]): out[t]=[t,x,y]
    return list(out.values())

def main():
    ap = argparse.ArgumentParser(description="StatsBomb Open Data → FBR 1.0 (modelo de ocupación)")
    ap.add_argument("events"); ap.add_argument("lineups")
    ap.add_argument("--home", required=True); ap.add_argument("--away", required=True)
    ap.add_argument("--date"); ap.add_argument("--match-id"); ap.add_argument("--competition")
    ap.add_argument("--note", default="Data provided by StatsBomb Open Data (StatsBomb Open Data License).")
    ap.add_argument("--max-period", type=int, default=4)
    ap.add_argument("--out")
    a = ap.parse_args()

    E = [e for e in json.load(open(a.events, encoding="utf-8")) if e.get("period",1) <= a.max_period]
    L = json.load(open(a.lineups, encoding="utf-8"))
    side = {a.home:"home", a.away:"away"}
    if len(side)!=2: sys.exit("--home/--away deben ser distintos")
    pid = lambda p: f"sb-{p}"

    # squads (persona) y titulares desde la primera alineación (evento Starting XI)
    teams = {"home":{"id":"home","name":a.home,"squad":[]}, "away":{"id":"away","name":a.away,"squad":[]}}
    for tm in L:
        s = side.get(tm["team_name"]) or sys.exit(f"lineups no coincide: {tm['team_name']!r}")
        for p in tm["lineup"]:
            teams[s]["squad"].append({"id":pid(p["player_id"]),"number":p.get("jersey_number"),"name":p["player_name"]})
    xi = {"home":[], "away":[]}
    for e in E:
        if e["type"]["name"]=="Starting XI":
            s=side[e["team"]["name"]]
            xi[s]=[p["player"]["id"] for p in e["tactics"]["lineup"]]
    if len(xi["home"])!=11 or len(xi["away"])!=11: sys.exit("no encontré Starting XI de 11 por equipo")

    # duración (mayor t observado)
    dur = max([t_of(e) for e in E] + [0])

    # sustituciones StatsBomb: (t, side, out_player_id, in_player_id)
    sb_subs=[]
    for e in E:
        if e["type"]["name"]=="Substitution":
            sb_subs.append((t_of(e), side[e["team"]["name"]], e["player"]["id"], e["substitution"]["replacement"]["id"]))
    sb_subs.sort()

    # construir 11 slots por equipo con cadenas de ocupación
    prefix={"home":"H","away":"A"}
    slot_of={}           # player_id -> slot_id del tramo que ocupa
    occupants={}         # slot_id -> [{person,from,to}]
    slot_team={}
    lineup={"home":{}, "away":{}}
    for s in ("home","away"):
        for i,p in enumerate(xi[s], start=1):
            sid=f"{prefix[s]}{i:02d}"
            slot_of[p]=sid; slot_team[sid]=s
            occupants[sid]=[{"person":pid(p),"from":0,"to":dur}]
            lineup[s][f"P{i:02d}"]=sid
    fbr_subs=[]
    for t,s,out_p,in_p in sb_subs:
        sid=slot_of.get(out_p)
        if not sid:  # seguridad: si el que sale no está mapeado, lo reportamos y seguimos
            sys.stderr.write(f"AVISO: sustitución en t={t} de jugador sin slot ({out_p}); ignorada\n"); continue
        occupants[sid][-1]["to"]=t
        occupants[sid].append({"person":pid(in_p),"from":t,"to":dur})
        slot_of[in_p]=sid
        fbr_subs.append({"t":t,"team":s,"subs":[{"in":pid(in_p),"out":pid(out_p),"slot":sid}]})

    # keyframes por PERSONA (posiciones de sus eventos), luego ensamblar por SLOT según ocupación
    per_kf={}
    ball_kf=[]
    for e in E:
        loc=e.get("location"); p=e.get("player")
        tm=side.get((e.get("team") or {}).get("name"))
        if not loc or len(loc)<2: continue
        flp = (tm=="away")                       # marco absoluto: home ataca hacia x=1
        t=t_of(e); x,y=norm_xy(loc, flp)
        ball_kf.append((t,x,y))
        if p and tm: per_kf.setdefault(p["id"],[]).append((t,x,y))
        # el balón también VIAJA: usar end_location + duración de pases/conducciones/remates
        typ=e["type"]["name"]; end=None; edur=e.get("duration") or 0
        if typ=="Pass": end=e.get("pass",{}).get("end_location")
        elif typ=="Carry": end=e.get("carry",{}).get("end_location")
        elif typ=="Shot": end=e.get("shot",{}).get("end_location"); edur=min(edur or 0.6, 1.2)
        if end and len(end)>=2:
            ex,ey=norm_xy(end, flp)
            te=round(t+max(edur,0.3),2)
            ball_kf.append((te, ex, ey))
            if typ=="Carry" and p and tm: per_kf.setdefault(p["id"],[]).append((te, ex, ey))

    id2num={}
    for tm in L:
        for p in tm["lineup"]: id2num[p["player_id"]]=p.get("jersey_number")

    actors=[{"id":"BALL","type":"ball"}]
    tracks=[{"actor":"BALL","interpolation":"linear","keyframes":dedup(ball_kf)}]
    inv={}  # slot -> [(person_raw, from, to)] para ensamblar tracks
    for sid,occ in occupants.items():
        actors.append({"id":sid,"type":"player","team":slot_team[sid],"occupants":occ})
        kfs=[]
        for o in occ:
            raw=int(o["person"][3:])
            for (t,x,y) in per_kf.get(raw,[]):
                if o["from"]<=t<=o["to"]: kfs.append((t,x,y))
        if kfs: tracks.append({"actor":sid,"interpolation":"linear","keyframes":dedup(kfs)})

    # eventos FBR: goles, tarjetas y sustituciones
    events=[]
    score={"home":0,"away":0}
    for e in E:
        typ=e["type"]["name"]; t=t_of(e); tm=side.get((e.get("team") or {}).get("name")); pl=e.get("player")
        actor=slot_of.get(pl["id"]) if pl else None
        # ojo: slot_of refleja el ÚLTIMO tramo; para el actor del evento basta con que exista el slot
        if typ=="Shot" and e.get("shot",{}).get("outcome",{}).get("name")=="Goal" and tm:
            score[tm]+=1
            ev={"t":t,"type":"goal","team":tm,"subtype":"normal","confidence":1.0,
                "detail":f"{e.get('minute')}' {pl['name']}" if pl else f"{e.get('minute')}'"}
            if actor: ev["actor"]=actor
            events.append(ev)
        elif typ=="Shot" and tm:
            # remate no convertido: atajado / desviado / bloqueado — clave para revivir jugadas
            outc=e.get("shot",{}).get("outcome",{}).get("name","")
            xg=e.get("shot",{}).get("statsbomb_xg")
            outs={"Saved":"atajado","Blocked":"bloqueado","Off T":"desviado","Wayward":"desviado","Post":"al palo"}
            ev={"t":t,"type":"shot","team":tm,"confidence":1.0,
                "detail":f"{e.get('minute')}' remate de {pl['name']}" + (f" — {outs.get(outc,outc)}" if outc else "") + (f" (xG {xg:.2f})" if xg else "")}
            if actor: ev["actor"]=actor
            events.append(ev)
        elif typ=="Own Goal Against" and tm:
            opp="away" if tm=="home" else "home"; score[opp]+=1
            events.append({"t":t,"type":"goal","team":opp,"subtype":"own_goal","confidence":1.0,
                           "detail":f"{e.get('minute')}' (autogol)"})
        else:
            card=(e.get("foul_committed",{}) or {}).get("card") or (e.get("bad_behaviour",{}) or {}).get("card")
            if card and tm:
                ev={"t":t,"type":"card","team":tm,"confidence":1.0,
                    "detail":f"{e.get('minute')}' {card['name']}"+(f" — {pl['name']}" if pl else "")}
                if actor: ev["actor"]=actor
                events.append(ev)
    for s_ev in fbr_subs:
        d_out=next(p["name"] for tmm in teams.values() for p in tmm["squad"] if p["id"]==s_ev["subs"][0]["out"])
        d_in =next(p["name"] for tmm in teams.values() for p in tmm["squad"] if p["id"]==s_ev["subs"][0]["in"])
        events.append({"t":s_ev["t"],"type":"substitution","team":s_ev["team"],"confidence":1.0,
                       "subs":s_ev["subs"],"detail":f"{s_ev['t']//60}' sale {d_out}, entra {d_in}"})
    events.sort(key=lambda e:e["t"])

    meta={"source":"event-derived","score":score,"license":a.note}
    if a.match_id: meta["match_id"]=a.match_id
    if a.competition: meta["competition"]=a.competition
    if a.date: meta["date"]=a.date

    th=dict(teams["home"]); th["lineup"]=lineup["home"]
    ta=dict(teams["away"]); ta["lineup"]=lineup["away"]
    doc={"format":"fbr","version":"1.0","schema_version":"1.0","profile":"extended",
         "meta":meta,"pitch":{"length_m":105,"width_m":68,"coordinates":"normalized"},
         "teams":[th,ta],"actors":actors,"time":{"unit":"second","duration":dur},
         "tracks":tracks,"events":events}

    out=json.dumps(doc,ensure_ascii=False,indent=1)
    if a.out:
        open(a.out,"w",encoding="utf-8").write(out)
        sys.stderr.write(f"FBR: {a.out} · 22 slots, {len(fbr_subs)} cambios, {len(events)} eventos, "
                         f"marcador {score['home']}-{score['away']}, {dur}s\n")
    else: print(out)

if __name__=="__main__": main()
