#!/usr/bin/env python3
# QA de formato FBR (reproducible): meta-schema, paridad Python/Node por archivo,
# motivo correcto de cada rechazo, consistencia i18n, invariantes independientes de
# partido-78 y fuzzing de paridad. Sale con código 0 si todo pasa, 1 si no.
#
# Uso:  python3 qa_format.py     (desde formato/pruebas/qa/)
import importlib.util, json, glob, os, subprocess, random, copy, re

HERE = os.path.dirname(os.path.abspath(__file__))          # .../pruebas/qa
PRU = os.path.dirname(HERE)                                # .../pruebas
FMT = os.path.dirname(PRU)                                 # .../formato
spec = importlib.util.spec_from_file_location('validar', os.path.join(PRU, 'validar.py'))
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
from jsonschema import Draft202012Validator, FormatChecker
schema = json.load(open(os.path.join(FMT, 'fbr.schema.json')))

R = []
def check(cid, desc, ok, detail=''): R.append((cid, desc, bool(ok), detail))

# F1 — el schema es un JSON Schema draft 2020-12 válido
try:
    Draft202012Validator.check_schema(schema); check('F1', 'Schema es draft 2020-12 válido', True)
except Exception as e:
    check('F1', 'Schema es draft 2020-12 válido', False, str(e))
pyval = Draft202012Validator(schema, format_checker=FormatChecker())

def py_verdict(path):
    d, err = V.cargar(path)
    if err: return 'invalid', [err]
    probs = ['schema: /' + '/'.join(str(p) for p in e.path) + ' ' + e.message for e in pyval.iter_errors(d)] + ['sem: ' + m for m in V.errores_semanticos(d)]
    return ('invalid' if probs else 'valid'), probs

def node_verdict(path):
    r = subprocess.run(['node', 'qa_lib.mjs', path], cwd=HERE, capture_output=True, text=True)
    try: o = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: return 'error', [r.stderr[:200]]
    return o['decision'], o['reasons']

val_files = sorted(glob.glob(os.path.join(PRU, 'validos', '*.fbr.json')))
inv_files = sorted(glob.glob(os.path.join(PRU, 'invalidos', '*.fbr.json')))

# F2 — batería + paridad Python/Node por archivo
parity_fail, valid_ok, invalid_ok, inv_reasons = [], True, True, {}
for f in val_files:
    pv, _ = py_verdict(f); nv, _ = node_verdict(f)
    if pv != 'valid' or nv != 'valid': valid_ok = False
    if pv != nv: parity_fail.append((os.path.basename(f), pv, nv))
for f in inv_files:
    pv, pr = py_verdict(f); nv, nr = node_verdict(f)
    inv_reasons[os.path.basename(f)] = (pr or nr)
    if pv != 'invalid' or nv != 'invalid': invalid_ok = False
    if pv != nv: parity_fail.append((os.path.basename(f), pv, nv))
check('F2a', f'Los {len(val_files)} válidos aceptados por py y node', valid_ok)
check('F2b', f'Los {len(inv_files)} inválidos rechazados por py y node', invalid_ok)
check('F2c', 'Paridad py/node en toda la batería', not parity_fail, '' if not parity_fail else str(parity_fail))

# F3 — cada inválido rechazado por el motivo correcto
expect = {
 '01': 'pitch', '02': 'version', '03': 'confidence', '04': 'propiedad|additional|desconoc|foo',
 '05': 'role|enum', '06': 'items|coorden|maxItems|array', '07': 'anchor', '08': 'subs|required',
 '09': 'duplicad', '10': 'referencia|inexist|zz99|nope', '11': 'negativ|t fuera|t=-', '12': 'fuera del partido|99999',
 '13': 'fecha|date|format', '14': 'marcador|score', '15': 'json|carga|parse', '16': 'vac',
 '17': 'coorden|imposible', '18': 'persona inexist', '19': 'hueco|solape|corte|occupants', '20': 'lineup|11',
 '21': 'subtype|enum|golazo|allowed',
}
reason_ok = []
for f in inv_files:
    num = os.path.basename(f)[:2]
    reasons = ' '.join(inv_reasons.get(os.path.basename(f), [])).lower()
    reason_ok.append((os.path.basename(f), bool(re.search(expect.get(num, '.'), reasons))))
check('F3', 'Cada inválido rechazado por el motivo correcto', all(h for _, h in reason_ok),
      '' if all(h for _, h in reason_ok) else 'revisar: ' + ', '.join(n for n, h in reason_ok if not h))

# F4 — códigos i18n existen en el schema (enum/const/examples/descripción)
def collect(node, acc):
    if isinstance(node, dict):
        for key in ('enum', 'examples'):
            if isinstance(node.get(key), list):
                acc.update(v for v in node[key] if isinstance(v, str))
        if isinstance(node.get('const'), str): acc.add(node['const'])
        for v in node.values(): collect(v, acc)
    elif isinstance(node, list):
        for v in node: collect(v, acc)
codes = set(); collect(schema, codes)
stext = json.dumps(schema, ensure_ascii=False)
en = json.load(open(os.path.join(FMT, 'i18n', 'en.json')))
orphans = {s: [k for k in en.get(s, {}) if k not in codes and k not in stext]
           for s in ['events', 'goal_subtypes', 'cards', 'periods', 'ball_states']}
orphans = {s: v for s, v in orphans.items() if v}
check('F4', 'Códigos i18n existen en el schema', not orphans, '' if not orphans else str(orphans))

# F5 — 6 catálogos i18n alineados con en
cats = {os.path.basename(p)[:-5]: json.load(open(p)) for p in glob.glob(os.path.join(FMT, 'i18n', '*.json'))}
secs = ['roles', 'events', 'goal_subtypes', 'cards', 'periods', 'ball_states', 'ui']
base = {(s, k) for s in secs for k in cats['en'].get(s, {})}
mis = {l: 1 for l, c in cats.items() if {(s, k) for s in secs for k in c.get(s, {})} != base}
check('F5', f'Los {len(cats)} catálogos i18n alineados con en', not mis, '' if not mis else str(list(mis)))

# F6 — invariantes de partido-78 recomputados de forma independiente
d = json.load(open(os.path.join(FMT, 'ejemplos', 'partido-78.fbr.json')))
dur = d['time']['duration']; idset = {a['id'] for a in d['actors']}
persons = {p['id'] for tm in d['teams'] for p in tm.get('squad', [])}
ind = []
g = {'home': 0, 'away': 0}
for e in d['events']:
    if e['type'] == 'goal':
        tm = e.get('team'); tm = ('away' if tm == 'home' else 'home') if e.get('subtype') == 'own_goal' else tm
        if tm in g: g[tm] += 1
ind.append(g == d['meta']['score'])
cov = True
for a in d['actors']:
    occ = a.get('occupants')
    if not occ: continue
    if any(o['person'] not in persons for o in occ): cov = False
    tr = sorted(occ, key=lambda o: o['from'])
    if abs(tr[0]['from']) > 1e-6 or abs(tr[-1].get('to', dur) - dur) > 1e-6: cov = False
    for i in range(len(tr) - 1):
        if abs(tr[i]['to'] - tr[i + 1]['from']) > 1e-6: cov = False
ind.append(cov)
occby = {a['id']: a.get('occupants', []) for a in d['actors']}
sub = True
for e in d['events']:
    if e['type'] != 'substitution': continue
    for s in e['subs']:
        cortes = [o['to'] for o in occby.get(s['slot'], []) if o.get('to', dur) < dur - 1e-6]
        if not any(abs(c - e['t']) <= 1 for c in cortes): sub = False
        if s['in'] not in persons or s['out'] not in persons or s['slot'] not in idset: sub = False
ind.append(sub)
ind.append(all(sum(1 for r, v in tm['lineup'].items() for _ in (v if isinstance(v, list) else [v])) == 11
               for tm in d['teams'] if 'lineup' in tm))
check('F6', 'partido-78: invariantes recomputados independientemente', all(ind))

# F7 — fuzzing: 300 mutaciones, paridad py/node
random.seed(42)
base_doc = json.load(open(os.path.join(FMT, 'ejemplos', 'partido-78.fbr.json')))
tmp = os.path.join(HERE, '_fuzz.fbr.json')
def outfield(x): return next(a for a in x['actors'] if a['type'] == 'player' and a.get('role') != 'GK')
def mutate(doc):
    x = copy.deepcopy(doc); op = random.randrange(15)
    try:
        if op == 0: del x['pitch']
        elif op == 1: x['version'] = random.choice([1.0, '9.9', None])
        elif op == 2: x['events'][random.randrange(len(x['events']))]['confidence'] = random.choice([1.5, -1])
        elif op == 3: x['zzz'] = 1
        elif op == 4: outfield(x)['role'] = 'Zzz'
        elif op == 5: x['tracks'][0]['keyframes'][1] = [10, 9.9, 0.4]
        elif op == 6: [a.pop('anchor', None) for a in x['actors'] if a['type'] == 'player' and a.get('role') != 'GK'][:1]
        elif op == 7:
            for e in x['events']:
                if e['type'] == 'substitution': e.pop('subs', None); break
        elif op == 8: x['actors'][3]['id'] = x['actors'][2]['id']
        elif op == 9: next(e for e in x['events'] if e['type'] == 'goal')['actor'] = 'NOPE'
        elif op == 10: x['events'][0]['t'] = -random.randint(1, 99)
        elif op == 11: x['meta']['score'] = {'home': random.randint(3, 9), 'away': 0}
        elif op == 12:
            a = next(y for y in x['actors'] if y.get('occupants') and len(y['occupants']) == 2)
            a['occupants'][0]['to'] -= random.randint(100, 800)
        elif op == 13:
            for tm in x['teams']:
                if 'lineup' in tm: del tm['lineup'][list(tm['lineup'])[-1]]; break
        elif op == 14: next(e for e in x['events'] if e['type'] == 'goal')['subtype'] = 'golazo'
    except Exception:
        x['version'] = 'x'
    return x
disagree = 0; N = 300
for _ in range(N):
    json.dump(mutate(base_doc), open(tmp, 'w'))
    pv, _ = py_verdict(tmp); nv, _ = node_verdict(tmp)
    if pv != nv: disagree += 1
os.remove(tmp)
check('F7', f'Fuzzing: paridad py/node en {N} mutaciones', disagree == 0, '' if disagree == 0 else f'{disagree} divergencias')

print('== QA FORMATO ==')
allok = True
for cid, desc, ok, det in R:
    allok = allok and ok
    print(f'  [{"PASS" if ok else "FAIL"}] {cid}  {desc}' + (f'  ·· {det}' if det else ''))
print(f'\nFORMATO: {"TODO PASA" if allok else "HAY FALLOS"}')
import sys; sys.exit(0 if allok else 1)
