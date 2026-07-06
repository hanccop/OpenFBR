// QA de simulación del Engine (visor de referencia). Barre el replay y verifica invariantes
// físicos, determinismo, que la interpolación coincide con la fórmula normativa y que el
// export del visor valida contra el schema. Sale 0 si todo pasa, 1 si no.
// Uso:  node qa_sim.cjs     (desde formato/pruebas/qa/)
const { execFileSync } = require('node:child_process');
const { writeFileSync, unlinkSync } = require('node:fs');
const path = require('node:path');
const T = require('./harness.cjs');

const R = [];
const check = (id, desc, ok, detail = '') => R.push({ id, desc, ok: !!ok, detail });
const fin = (n) => typeof n === 'number' && isFinite(n);

// S2 — barrido: 11+11 jugadores + balón, finitos y en rango, en cada segundo
let bad = 0, badEx = '';
for (let t = 0; t <= T.TMAX; t++) {
  const f = T.computeFrame(t), b = T.ballAt(t);
  if (f.ci.length !== 11 || f.no.length !== 11) { bad++; if (!badEx) badEx = `t=${t}`; continue; }
  for (const p of [...f.ci, ...f.no, b]) {
    if (!fin(p.x) || !fin(p.y) || p.x < -0.35 || p.x > 1.35 || p.y < -0.35 || p.y > 1.35) { bad++; if (!badEx) badEx = `t=${t}`; break; }
  }
}
check('S2', 'Barrido 0..TMAX: 11+11 jugadores + balón, finitos y en rango', bad === 0, bad ? `${bad} frames malos (${badEx})` : '');

// S3 — sin teletransporte de jugadores SIN balón (el portador se dibuja sobre el balón)
let maxOff = 0, maxOffAt = 0, maxCar = 0, prev = null, prevCar = null;
for (let t = 0; t <= T.TMAX; t++) {
  const f = T.computeFrame(t), b = T.ballAt(t);
  const pos = [...f.ci, ...f.no].map(p => [p.x, p.y]);
  const carKey = (typeof f.carrier === 'number') ? ((b.pos === 'CI' ? 0 : 11) + f.carrier) : null;
  if (prev) for (let i = 0; i < pos.length; i++) {
    const d = Math.hypot(pos[i][0] - prev[i][0], pos[i][1] - prev[i][1]);
    if (i === carKey || i === prevCar) { if (d > maxCar) maxCar = d; }
    else if (d > maxOff) { maxOff = d; maxOffAt = t; }
  }
  prev = pos; prevCar = carKey;
}
check('S3', 'Sin teletransporte (jugadores sin balón) < 0.12/seg', maxOff < 0.12,
  `sin balón máx=${maxOff.toFixed(4)}/seg (t=${maxOffAt}); portador máx=${maxCar.toFixed(4)}/seg (render)`);

// S4 — determinismo del Engine
let det = true;
for (const t of [0, 137, 1320, 2940, 4260, 6060])
  if (JSON.stringify(T.computeFrame(t)) !== JSON.stringify(T.computeFrame(t))) det = false;
check('S4', 'Determinismo: computeFrame(t) reproducible', det);

// S5 — interpolación del Engine == fórmula lineal normativa (§5.5), sobre el balón
let interpErr = 0;
for (let i = 0; i < T.W.length - 1; i++) {
  const [t0, x0, y0] = T.W[i], [t1, x1, y1] = T.W[i + 1];
  if (t1 - t0 < 2) continue;
  const tm = (t0 + t1) / 2, s = (tm - t0) / (t1 - t0);
  const b = T.ballAt(tm);
  interpErr = Math.max(interpErr, Math.hypot(b.x - (x0 + s * (x1 - x0)), b.y - (y0 + s * (y1 - y0))));
}
check('S5', 'Interpolación del Engine == lineal normativa', interpErr < 1e-6, `error máx=${interpErr.toExponential(2)}`);

// S6 — dogfooding: el export del Engine valida contra el schema (via qa_lib.mjs)
const fbr = T.buildFBR();
const tmp = path.join(__dirname, '_export.fbr.json');
writeFileSync(tmp, JSON.stringify(fbr, null, 2));
let verdict = { decision: 'error', reasons: [] };
try { verdict = JSON.parse(execFileSync('node', ['qa_lib.mjs', tmp], { cwd: __dirname }).toString().trim()); } catch (e) {}
unlinkSync(tmp);
check('S6', 'Dogfooding: el export del Engine valida (schema + semántica)',
  fbr.version === '1.0' && verdict.decision === 'valid', verdict.decision !== 'valid' ? String(verdict.reasons[0] || '') : '');

// S7 — i18n: los 6 idiomas aplican sin excepción
let i18nOk = true;
for (const L of ['es', 'en', 'fr', 'pt', 'de', 'it']) { try { T.applyLang(L); } catch (e) { i18nOk = false; } }
T.applyLang('es');
check('S7', 'i18n: los 6 idiomas aplican sin excepción', i18nOk);

// S8 — determinismo del exportador
check('S8', 'Determinismo del exportador (buildFBR reproducible)',
  JSON.stringify(T.buildFBR()) === JSON.stringify(T.buildFBR()));

// S9 — periodos coherentes
const tm2 = fbr.time;
check('S9', 'time: 2 periodos coherentes, duration==TMAX',
  tm2.periods.length === 2 && tm2.periods[0].type === 'first_half' && tm2.periods[1].type === 'second_half' &&
  tm2.duration === T.TMAX && tm2.periods[1].end === T.TMAX);

console.log('== QA SIMULACIÓN (Engine) ==');
let allok = true;
for (const c of R) { allok = allok && c.ok; console.log(`  [${c.ok ? 'PASS' : 'FAIL'}] ${c.id}  ${c.desc}` + (c.detail ? `  ·· ${c.detail}` : '')); }
console.log(`\nSIMULACIÓN: ${allok ? 'TODO PASA' : 'HAY FALLOS'}`);
process.exit(allok ? 0 : 1);
