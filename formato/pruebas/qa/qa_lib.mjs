// Veredicto de conformidad por archivo (schema AJV + semántica), idéntico a validate.mjs.
// CLI:  node qa_lib.mjs <archivo>   ->  {"decision":"valid|invalid","reasons":[...]}
// Usado por qa_format.py para el fuzzing y la paridad Python/Node.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const HERE = dirname(fileURLToPath(import.meta.url));   // .../pruebas/qa
const FMT = join(HERE, "..", "..");                     // .../formato
const schema = JSON.parse(readFileSync(join(FMT, "fbr.schema.json"), "utf8"));
const SUPPORTED = new Set(["0.6", "0.7", "1.0"]);
const [CMIN, CMAX] = [-0.5, 1.5];

const ajv = new Ajv2020({ allErrors: false, strict: false });
addFormats(ajv);
const validate = ajv.compile(schema);

const load = (p) => {
  const txt = readFileSync(p, "utf8");
  if (txt.trim() === "") throw new Error("archivo vacío");
  return JSON.parse(txt);
};
const kf = (k) => (Array.isArray(k) ? [k[0], k[1], k[2]] : [k.t, k.x, k.y]);

function semantic(d) {
  const errs = [];
  const actors = d.actors || [];
  const ids = actors.map((a) => a.id);
  const idset = new Set(ids);
  const persons = (d.teams || []).flatMap((tm) => (tm.squad || []).map((p) => p.id));
  const personset = new Set(persons);
  const pdup = [...new Set(persons.filter((x, i) => persons.indexOf(x) !== i))];
  if (pdup.length) errs.push(`person_id duplicados en squad: ${pdup.join(", ")}`);
  const dup = [...new Set(ids.filter((x, i) => ids.indexOf(x) !== i))];
  if (dup.length) errs.push(`IDs duplicados: ${dup.join(", ")}`);
  const dur = (d.time || {}).duration;

  for (const tr of d.tracks || []) {
    if (!idset.has(tr.actor)) errs.push(`track con actor inexistente: ${tr.actor}`);
    const ts = (tr.keyframes || []).map((k) => kf(k)[0]);
    if (ts.join(",") !== [...ts].sort((a, b) => a - b).join(",")) errs.push(`keyframes fuera de orden en ${tr.actor}`);
    for (const k of tr.keyframes || []) {
      const [t, x, y] = kf(k);
      if (t == null || t < 0 || (dur != null && t > dur + 1e-6)) errs.push(`t fuera de [0,duración] en ${tr.actor}: ${t}`);
      if (!(x >= CMIN && x <= CMAX && y >= CMIN && y <= CMAX)) errs.push(`coordenada imposible en ${tr.actor}: (${x},${y})`);
    }
  }

  const evs = d.events || [];
  const ets = evs.map((e) => e.t);
  if (ets.join(",") !== [...ets].sort((a, b) => a - b).join(",")) errs.push("eventos fuera de orden cronológico");
  for (const e of evs) {
    if (e.t == null || e.t < 0 || (dur != null && e.t > dur + 1e-6)) errs.push(`evento fuera del partido: t=${e.t} (${e.type})`);
    for (const ref of ["actor", "assist", "recipient"])
      if (ref in e && !idset.has(e[ref])) errs.push(`referencia inexistente (${ref}=${e[ref]})`);
    for (const s of e.subs || []) {
      if (s.slot && !idset.has(s.slot)) errs.push(`slot inexistente: ${s.slot}`);
      for (const who of ["in", "out"]) if (s[who] && !personset.has(s[who])) errs.push(`cambio referencia persona inexistente (${who}=${s[who]})`);
    }
  }

  const occby = {};
  for (const a of actors) {
    occby[a.id] = a.occupants || [];
    const occ = a.occupants;
    if (!occ || !occ.length) continue;
    for (const o of occ) if (!personset.has(o.person)) errs.push(`occupant de ${a.id} referencia persona inexistente: ${o.person}`);
    const tr = [...occ].sort((x, y) => (x.from || 0) - (y.from || 0));
    if (dur != null) {
      if (Math.abs((tr[0].from || 0) - 0) > 1e-6) errs.push(`occupants de ${a.id} no arrancan en 0`);
      if (Math.abs((tr[tr.length - 1].to ?? dur) - dur) > 1e-6) errs.push(`occupants de ${a.id} no cubren hasta la duración`);
    }
    for (let i = 0; i < tr.length - 1; i++)
      if (Math.abs(tr[i].to - tr[i + 1].from) > 1e-6) errs.push(`occupants de ${a.id} con hueco/solape entre tramos`);
  }

  for (const e of evs) {
    if (e.type !== "substitution") continue;
    for (const s of e.subs || []) {
      const occ = occby[s.slot] || [];
      const cortes = occ.map((o) => o.to).filter((c) => c != null && (dur == null || c < dur - 1e-6));
      if (!cortes.some((c) => Math.abs(c - e.t) <= 1.0)) errs.push(`cambio en t=${e.t} no coincide con el corte de occupants del slot ${s.slot} (${cortes})`);
    }
  }

  for (const tm of d.teams || []) {
    if (!tm.lineup) continue;
    const resolved = [];
    for (const [, v] of Object.entries(tm.lineup))
      for (const pid of Array.isArray(v) ? v : [v]) {
        resolved.push(pid);
        if (!idset.has(pid)) errs.push(`lineup id inexistente: ${pid}`);
      }
    if (resolved.length !== 11) errs.push(`lineup de ${tm.id} no tiene 11 titulares (tiene ${resolved.length})`);
  }

  const date = (d.meta || {}).date;
  if (date != null && !/^\d{4}-\d{2}-\d{2}$/.test(date)) errs.push(`fecha no ISO 8601: ${date}`);

  const score = (d.meta || {}).score;
  if (score) {
    const g = { home: 0, away: 0 };
    for (const e of evs)
      if (e.type === "goal") {
        let tm = e.team;
        if (e.subtype === "own_goal") tm = tm === "home" ? "away" : "home";
        if (tm in g) g[tm]++;
      }
    if (g.home !== score.home || g.away !== score.away)
      errs.push(`marcador inconsistente: goles ${JSON.stringify(g)} vs meta.score ${JSON.stringify(score)}`);
  }

  if (!SUPPORTED.has(d.version)) errs.push(`versión no soportada: ${d.version}`);
  return errs;
}

export function problems(d) {
  const p = [];
  if (!validate(d)) for (const e of validate.errors) p.push(`schema: ${e.instancePath || "/"} ${e.message}`);
  for (const m of semantic(d)) p.push(`semántica: ${m}`);
  return p;
}

// CLI
const file = process.argv[2];
if (file) {
  let out;
  try { const d = load(file); out = { decision: problems(d).length ? "invalid" : "valid", reasons: problems(d) }; }
  catch (e) { out = { decision: "invalid", reasons: [`carga: ${e.message}`] }; }
  console.log(JSON.stringify(out));
}
