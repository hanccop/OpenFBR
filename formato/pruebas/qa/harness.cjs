// Arnés de QA: carga el <script> del visor de referencia en un DOM simulado (sin navegador)
// y expone el motor en globalThis.__t para poder simular y auditar el replay desde Node.
// Uso:  const T = require('./harness.cjs');
const fs = require('fs');
const path = require('path');

const VIEWER = path.join(__dirname, '..', '..', '..', 'prototipo', 'legacy', 'demo-civ-nor.html');
const html = fs.readFileSync(VIEWER, 'utf8');

// tomar el bloque <script> principal (el más grande)
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let code = scripts.sort((a, b) => b.length - a.length)[0];

// exponer funciones internas justo antes de cerrar el IIFE
const expose = `;globalThis.__t={ballAt,scoreAt,possCI,computeFrame,actorNorm,M,dims,buildFBR,interp,refPositions,teamPositions,edited,setOrient:o=>{orient=o;},setEdits:e=>{edits=e;},clearEdits:()=>{edits={};},TMAX,W,EVENTS,I18N,applyLang,get CUR(){return CUR;}};`;
const idx = code.lastIndexOf('})();');
code = code.slice(0, idx) + expose + code.slice(idx);

// stubs mínimos de DOM/entorno (el visor no usa el navegador para calcular el replay)
function makeNode() {
  const styleP = new Proxy({}, { get: (t, p) => (['setProperty', 'removeProperty', 'getPropertyValue', 'item'].includes(p) ? () => '' : ''), set: () => true });
  return new Proxy(function () {}, {
    apply: () => makeNode(), set: () => true,
    get(t, p) {
      if (p === Symbol.toPrimitive || p === 'toString' || p === 'valueOf') return () => '';
      if (p === 'style') return styleP;
      if (p === 'classList') return { add() {}, remove() {}, toggle() {}, contains() { return false; } };
      if (p === 'dataset') return {};
      if (p === 'files') return [];
      if (p === 'children') return [];
      if (p === 'textContent' || p === 'innerHTML' || p === 'value' || p === 'className') return '';
      if (p === 'getScreenCTM') return () => ({ inverse: () => ({}) });
      if (p === 'createSVGPoint') return () => ({ x: 0, y: 0, matrixTransform: () => ({ x: 0, y: 0 }) });
      if (p === 'querySelectorAll') return () => [];
      if (p === 'querySelector' || p === 'closest') return () => makeNode();
      if (p === 'appendChild' || p === 'append') return c => c;
      if (['setAttribute', 'removeAttribute', 'addEventListener', 'removeEventListener', 'remove', 'insertBefore', 'focus', 'blur', 'click', 'setProperty'].includes(p)) return () => {};
      if (p === 'getContext') return () => ({});
      return makeNode();
    }
  });
}
const doc = {
  querySelector: () => makeNode(), querySelectorAll: () => [],
  getElementById: () => makeNode(),
  createElement: () => makeNode(), createElementNS: () => makeNode(),
  addEventListener: () => {}, body: makeNode(), documentElement: makeNode()
};
globalThis.document = doc;
globalThis.window = { addEventListener: () => {} };
globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
globalThis.alert = () => {}; globalThis.confirm = () => true;
globalThis.requestAnimationFrame = () => 0; globalThis.cancelAnimationFrame = () => {};
globalThis.performance = { now: () => 0 };
globalThis.URL = { createObjectURL: () => 'blob:' };
globalThis.Blob = function () {}; globalThis.FileReader = function () {};
globalThis.navigator = {};

let initError = null;
try { eval(code); } catch (e) { initError = e; }
if (initError) { console.error('ERROR en init del visor: ' + initError.message); process.exit(1); }
module.exports = globalThis.__t;
