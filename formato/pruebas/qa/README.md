# QA reproducible

Guiones que reproducen el veredicto del `QA-REPORT.md`. No dependen de un navegador.

## Requisitos
- Node ≥ 18 y las dependencias de `../` (`npm install` en `formato/pruebas`).
- Python ≥ 3.10 con `jsonschema` (`pip install jsonschema`).

## Cómo correrlo (desde esta carpeta `formato/pruebas/qa/`)

```bash
python3 qa_format.py   # F1–F7: meta-schema, paridad Python/Node, motivos, i18n, invariantes, fuzzing
node    qa_sim.cjs     # S2–S9: simulación del Engine, no-teletransporte, interpolación, dogfooding
```

Ambos salen con código 0 si todo pasa. También desde `formato/pruebas`:

```bash
npm run qa
```

## Qué hace cada uno

- **`qa_format.py`** — valida que `fbr.schema.json` es draft 2020-12; corre la batería (3 válidos + 21
  inválidos) con **ambos** validadores y compara el veredicto **por archivo** (paridad Python/Node);
  comprueba que cada inválido se rechaza por *su* motivo; verifica consistencia schema↔i18n;
  recomputa de forma **independiente** los invariantes de `partido-78`; y hace **fuzzing** de 300
  mutaciones aleatorias comprobando que Python y Node coinciden en cada una.
- **`qa_sim.cjs`** — carga el `<script>` del visor de referencia en un DOM simulado
  (`harness.cjs`, sin navegador) y **barre los 6 060 s** verificando: 22 jugadores + balón finitos y
  en rango; que ningún jugador sin balón se "teletransporta"; determinismo de `computeFrame`; que la
  interpolación del Engine coincide con la fórmula **lineal normativa** (§5.5) con error 0; que el
  export del visor **valida** contra el schema (*dogfooding*); y que los 6 idiomas aplican sin error.

## Archivos
- `harness.cjs` — carga el motor del visor **clásico** (`prototipo/legacy/demo-civ-nor.html`, la implementación de referencia rica que generó el partido 78) en Node (DOM simulado) y expone la API interna.
- `qa_lib.mjs` — veredicto de conformidad por archivo (AJV + semántica), idéntico a `../validate.mjs`.
- `qa_format.py`, `qa_sim.cjs` — las dos suites.

> Nota: `harness.cjs` es específico del visor de referencia; si cambia la estructura del `<script>`
> del visor, hay que reajustarlo. Es una herramienta de QA, no parte del estándar.
