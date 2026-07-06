# Changelog

Todas las versiones notables de OpenFBR / FBR.
Formato basado en Keep a Changelog; versionado según SemVer.

## [1.0.0] — 2026-07

Primera versión estable del formato y su implementación de referencia.

### Formato (especificación)
- Modelo de identidad en 3 niveles (persona / slot / ocupación) en tercera forma normal.
- Keyframe único `[t, x, y]`; estado del balón vía evento `ball-state`; multi-balón vía `ball-change`.
- Interpolación **lineal normativa** (determinista): dos visores producen el mismo movimiento.
- `confidence` como rúbrica cerrada de nivel de fuente (no una probabilidad).
- `subtype` de gol **acotado** a `normal · penalty · own_goal · free_kick · header` (validado por schema).
- Validación en dos capas: JSON Schema (draft 2020-12) + invariantes semánticos.

### Implementación de referencia
- Validadores paralelos en Python (`validar.py`) y Node (`validate.mjs`), con paridad verificada.
- Batería de conformidad: 3 ejemplos válidos + 21 inválidos (cada uno aísla un defecto).
- Visor de referencia 2D («FBR Replay») con identidad propia; import/export FBR; 6 idiomas.
- **Paquete npm `fbr-validate`**: CLI y librería para validar `.fbr.json` (`npx fbr-validate`).

### QA
- Suite reproducible en `formato/pruebas/qa/`: paridad Python/Node, fuzzing (300 mutaciones),
  simulación del Engine, dogfooding. `npm run qa`.

### Legal
- Licencia dual: especificación **CC-BY-4.0** (`LICENSE-SPEC`), código **MIT** (`LICENSE`).
- Visor sin reproducir interfaces de terceros.
