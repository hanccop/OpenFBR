#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de conformidad FBR — ejecuta el Plan de Pruebas (secciones 1, 3-6, 8, 11, 13).
Uso:  python3 validar.py
Sale con código 0 si el veredicto es APROBADO, 1 en caso contrario.
"""
import json, os, glob, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FMT  = os.path.dirname(HERE)                      # .../formato
SCHEMA_PATH = os.path.join(FMT, "fbr.schema.json")
VALIDOS   = sorted(glob.glob(os.path.join(HERE, "validos", "*.json")))
INVALIDOS = sorted(glob.glob(os.path.join(HERE, "invalidos", "*.json")))
I18N = os.path.join(FMT, "i18n")

SOPORTADAS = {"0.6", "0.7", "1.0"}          # versiones de esquema soportadas
COORD_MIN, COORD_MAX = -0.5, 1.5     # límites "físicos" (aun con out_of_bounds)

try:
    from jsonschema import Draft202012Validator, FormatChecker
except Exception:
    print("Falta la librería 'jsonschema' (pip install jsonschema).")
    sys.exit(2)


# ---------- utilidades ----------
def cargar(path):
    """Devuelve (doc, error_de_carga|None)."""
    try:
        txt = open(path, encoding="utf-8").read()
        if txt.strip() == "":
            return None, "archivo vacío"
        return json.loads(txt), None
    except json.JSONDecodeError as e:
        return None, f"JSON inválido: {e}"


def kf_txyxy(k):
    """Normaliza un keyframe compacto [t,x,y(,s)] o {t,x,y} → (t,x,y)."""
    if isinstance(k, list):
        return k[0], k[1], k[2]
    return k.get("t"), k.get("x"), k.get("y")


# ---------- chequeos semánticos (lo que el JSON Schema no puede expresar) ----------
def errores_semanticos(d):
    errs = []
    actors = d.get("actors", [])
    ids = [a.get("id") for a in actors]
    idset = set(ids)
    # Personas (v1.0): identidad por person_id en teams[].squad
    persons = [p.get("id") for tm in d.get("teams", []) for p in (tm.get("squad") or [])]
    personset = set(persons)
    pdup = sorted({x for x in persons if persons.count(x) > 1})
    if pdup:
        errs.append(f"person_id duplicados en squad: {', '.join(map(str, pdup))}")

    # IDs duplicados
    dup = sorted({x for x in ids if ids.count(x) > 1})
    if dup:
        errs.append(f"IDs duplicados: {', '.join(map(str, dup))}")

    dur = (d.get("time") or {}).get("duration")

    # Tracks: actor existente, orden cronológico, t en rango, coordenadas físicas
    for tr in d.get("tracks", []):
        act = tr.get("actor")
        if act not in idset:
            errs.append(f"track con actor inexistente: {act}")
        ts = [kf_txyxy(k)[0] for k in tr.get("keyframes", [])]
        if ts != sorted(ts):
            errs.append(f"keyframes fuera de orden cronológico en {act}")
        for k in tr.get("keyframes", []):
            t, x, y = kf_txyxy(k)
            if t is None or t < 0 or (dur is not None and t > dur + 1e-6):
                errs.append(f"t fuera de [0,duración] en {act}: {t}")
            if not (COORD_MIN <= x <= COORD_MAX and COORD_MIN <= y <= COORD_MAX):
                errs.append(f"coordenada imposible en {act}: ({x},{y})")

    # Eventos: orden, referencias, t en rango
    evs = d.get("events", [])
    ets = [e.get("t") for e in evs]
    if ets != sorted(ets):
        errs.append("eventos fuera de orden cronológico")
    for e in evs:
        t = e.get("t")
        if t is None or t < 0 or (dur is not None and t > dur + 1e-6):
            errs.append(f"evento fuera del partido: t={t} ({e.get('type')})")
        for ref in ("actor", "assist", "recipient"):
            if ref in e and e[ref] not in idset:
                errs.append(f"referencia inexistente en evento ({ref}={e[ref]})")
        for s in e.get("subs", []) or []:
            if s.get("slot") and s["slot"] not in idset:
                errs.append(f"slot de cambio inexistente: {s['slot']}")
            for who in ("in", "out"):
                if s.get(who) and s[who] not in personset:
                    errs.append(f"cambio referencia persona inexistente ({who}={s[who]})")

    # occupants: por cada slot, referencias válidas, sin huecos ni solapes, cubren [0,duration]
    for a in actors:
        occ = a.get("occupants")
        if not occ:
            continue
        for o in occ:
            if o.get("person") not in personset:
                errs.append(f"occupant de {a.get('id')} referencia persona inexistente: {o.get('person')}")
        tramos = sorted(occ, key=lambda o: o.get("from", 0))
        if dur is not None:
            if abs((tramos[0].get("from", 0)) - 0) > 1e-6:
                errs.append(f"occupants de {a.get('id')} no arrancan en 0")
            if abs((tramos[-1].get("to", dur)) - dur) > 1e-6:
                errs.append(f"occupants de {a.get('id')} no cubren hasta la duración")
        for i in range(len(tramos) - 1):
            if abs((tramos[i].get("to")) - (tramos[i + 1].get("from"))) > 1e-6:
                errs.append(f"occupants de {a.get('id')} con hueco/solape entre tramos")

    # substitution: el t del evento coincide con el corte del ocupante saliente
    occby = {a.get("id"): a.get("occupants") or [] for a in actors}
    for e in evs:
        if e.get("type") != "substitution":
            continue
        for s in e.get("subs", []) or []:
            slot = s.get("slot")
            occ = occby.get(slot, [])
            cortes = [o.get("to") for o in occ if o.get("to") is not None and (dur is None or o.get("to") < dur - 1e-6)]
            if not any(abs(c - e.get("t")) <= 1.0 for c in cortes):
                errs.append(f"cambio en t={e.get('t')} no coincide con el corte de occupants del slot {slot} ({cortes})")

    # lineup → 11 slots por equipo, todos existentes
    for tm in d.get("teams", []):
        lu = tm.get("lineup")
        if lu is None:
            continue
        resolved = []
        for role, v in lu.items():
            for pid in ([v] if isinstance(v, str) else v):
                resolved.append(pid)
                if pid not in idset:
                    errs.append(f"lineup apunta a id inexistente: {pid}")
        if len(resolved) != 11:
            errs.append(f"lineup de {tm.get('id')} no tiene 11 titulares (tiene {len(resolved)})")

    # date ISO 8601 (respaldo por si el validador no fuerza 'format')
    date = (d.get("meta") or {}).get("date")
    if date is not None:
        try:
            datetime.date.fromisoformat(date)
        except Exception:
            errs.append(f"fecha no ISO 8601 (YYYY-MM-DD): {date}")

    # Consistencia con el marcador
    score = (d.get("meta") or {}).get("score")
    if score:
        g = {"home": 0, "away": 0}
        for e in evs:
            if e.get("type") == "goal":
                tm = e.get("team")
                if e.get("subtype") == "own_goal":
                    tm = "away" if tm == "home" else "home"
                if tm in g:
                    g[tm] += 1
        if g["home"] != score.get("home") or g["away"] != score.get("away"):
            errs.append(f"marcador inconsistente: goles contados {g} vs meta.score {score}")

    # versión soportada
    ver = d.get("version")
    if ver not in SOPORTADAS:
        errs.append(f"versión no soportada: {ver} (soportadas: {sorted(SOPORTADAS)})")

    return errs


# ---------- i18n ----------
SECCIONES_I18N = ["roles", "events", "goal_subtypes", "cards", "periods", "ball_states", "ui"]
def revisar_i18n():
    res = {"ok": True, "detalle": []}
    files = sorted(glob.glob(os.path.join(I18N, "*.json")))
    if not files:
        return {"ok": False, "detalle": ["no hay catálogos i18n"]}
    cats = {}
    for f in files:
        lang = os.path.splitext(os.path.basename(f))[0]
        cats[lang] = json.load(open(f, encoding="utf-8"))
    base_lang = "en" if "en" in cats else sorted(cats)[0]
    def claves(c): return {(sec, k) for sec in SECCIONES_I18N for k in c.get(sec, {})}
    base = claves(cats[base_lang])
    for lang, c in cats.items():
        ks = claves(c)
        if ks != base:
            res["ok"] = False
            faltan = base - ks
            sobran = ks - base
            res["detalle"].append(f"{lang}: {len(ks)} claves, desalineado (faltan {len(faltan)}, sobran {len(sobran)})")
        else:
            res["detalle"].append(f"{lang}: {len(ks)} claves, alineado")
    return res


# ---------- ejecución ----------
def main():
    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    def validar_doc(d):
        """Devuelve lista de problemas (schema + semántica). Vacía = válido."""
        probs = [f"schema: {e.message}" for e in validator.iter_errors(d)]
        probs += [f"semántica: {m}" for m in errores_semanticos(d)]
        return probs

    print("=" * 60)
    print(" INFORME DE CONFORMIDAD FBR — Plan de Pruebas 1.0")
    print(" fecha:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 60)

    lineas = []
    def log(s=""):
        print(s); lineas.append(s)

    # --- Sección 1/3: archivos válidos deben aprobar ---
    log("\n[1] ARCHIVOS VÁLIDOS (deben aprobar)")
    ok_validos = True
    for f in VALIDOS:
        d, err = cargar(f)
        name = os.path.basename(f)
        if err:
            log(f"  ✗ {name}: NO CARGA ({err})"); ok_validos = False; continue
        probs = validar_doc(d)
        if probs:
            ok_validos = False
            log(f"  ✗ {name}: RECHAZADO indebidamente")
            for p in probs[:4]:
                log(f"        - {p}")
        else:
            log(f"  ✓ {name}: aceptado")

    # --- Sección 1/11: archivos inválidos deben rechazarse ---
    log("\n[2] ARCHIVOS INVÁLIDOS (deben rechazarse, con motivo)")
    ok_invalidos = True
    for f in INVALIDOS:
        d, err = cargar(f)
        name = os.path.basename(f)
        if err:
            log(f"  ✓ {name}: rechazado (carga) — {err}")
            continue
        probs = validar_doc(d)
        if probs:
            log(f"  ✓ {name}: rechazado — {probs[0]}")
        else:
            ok_invalidos = False
            log(f"  ✗ {name}: ACEPTADO indebidamente (no se detectó la violación)")

    # --- Sección 3: módulos funcionales presentes en el 'completo' ---
    log("\n[3] MÓDULOS FUNCIONALES (archivo completo)")
    comp_path = os.path.join(HERE, "validos", "completo.fbr.json")
    modulos = ["meta", "pitch", "teams", "actors", "time", "tracks", "events",
               "analytics", "render", "extensions"]
    ok_mod = True
    if os.path.exists(comp_path):
        comp = json.load(open(comp_path, encoding="utf-8"))
        presentes = [m for m in modulos if m in comp]
        faltan = [m for m in modulos if m not in comp]
        lineup_ok = any("lineup" in t for t in comp.get("teams", []))
        log(f"  módulos: {', '.join(presentes)}")
        if faltan: log(f"  (ausentes: {', '.join(faltan)})")
        log(f"  lineup en teams: {'sí' if lineup_ok else 'no'}")
        ok_mod = not faltan and lineup_ok
    else:
        ok_mod = False; log("  ✗ falta completo.fbr.json")

    # --- Sección 6: timeline (periodos + pausas) ---
    log("\n[6] TIMELINE")
    ok_time = True
    if os.path.exists(comp_path):
        tm = comp.get("time", {})
        per = tm.get("periods", [])
        brk = tm.get("breaks", [])
        log(f"  periodos: {len(per)} · pausas (hidratación): {len(brk)}")
        ok_time = len(per) >= 2 and len(brk) >= 1
    else:
        ok_time = False

    # --- Sección 8: i18n ---
    log("\n[8] INTERNACIONALIZACIÓN (i18n)")
    i18n = revisar_i18n()
    for dline in i18n["detalle"]:
        log(f"  {dline}")
    ok_i18n = i18n["ok"]

    # --- Veredicto (Sección 13) ---
    log("\n" + "=" * 60)
    criterios = {
        "Todos los válidos aceptados": ok_validos,
        "Todos los inválidos rechazados": ok_invalidos,
        "Módulos funcionales presentes": ok_mod,
        "Timeline con periodos y pausas": ok_time,
        "i18n alineado (en/es/fr/pt)": ok_i18n,
    }
    for k, v in criterios.items():
        log(f"  [{'OK' if v else '  '}] {k}")
    aprobado = all(criterios.values())
    veredicto = "APROBADO" if aprobado else "RECHAZADO"
    log("=" * 60)
    log(f" RESULTADO FINAL: {veredicto}")
    log("=" * 60)

    # Guardar INFORME.md
    with open(os.path.join(HERE, "INFORME.md"), "w", encoding="utf-8") as fh:
        fh.write("# Informe de conformidad FBR\n\n")
        fh.write(f"_Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n")
        fh.write(f"**Resultado final: {veredicto}**\n\n")
        fh.write("Válidos: {} · Inválidos: {}\n\n".format(len(VALIDOS), len(INVALIDOS)))
        fh.write("```\n" + "\n".join(lineas) + "\n```\n")

    sys.exit(0 if aprobado else 1)


if __name__ == "__main__":
    main()
