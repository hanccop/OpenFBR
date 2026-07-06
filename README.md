# OpenFBR · Football Replay Format (FBR)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21212697.svg)](https://doi.org/10.5281/zenodo.21212697)

**Un formato JSON abierto para reconstruir y reproducir el estado espacial de un partido de
fútbol mediante *keyframes* dispersos e interpolación determinista.**

> **Estado:** especificación abierta en *draft* (v1.0), mantenida por un autor único. No es un
> estándar oficial. Ver [`GOVERNANCE.md`](GOVERNANCE.md).

FBR describe *dónde está cada actor a lo largo del tiempo*, de forma **legible**, **autorable a
mano** y **reproducible igual en cualquier visor**. Es una capa complementaria a los formatos de
eventos (Opta, StatsBomb, SPADL) y de *tracking* (EPTS), no un competidor. El modelo de proyecto
sigue el de estándares abiertos como **glTF**, **GeoJSON** y **OpenAPI**: especificación abierta
+ implementación de referencia + validación + comunidad.

## Por qué FBR

- **Autorable a mano** y **legible en un `diff` de Git**: los cambios se ven línea a línea.
- **Reproducible en el navegador** sin motor gráfico pesado.
- **Órdenes de magnitud más liviano** que el *tracking* (keyframes dispersos vs. muestreo por frame).
- **Interoperable**: coordenadas normalizadas `[0,1]`, ids estables, convertible desde/hacia el
  ecosistema existente.
- **Honesto sobre su imprecisión**: cada evento declara el *nivel de fuente* del dato (`confidence`).

## Inicio rápido

**Ver un partido** (no requiere instalación):

```bash
# abre el visor de referencia en el navegador
open prototipo/index.html        # macOS · en Linux: xdg-open · en Windows: start
```

**Validar un archivo FBR** (dos capas: esquema + invariantes semánticos):

```bash
# Python
pip install jsonschema
python3 formato/pruebas/validar.py           # imprime INFORME.md; exit≠0 si algo falla

# Node
cd formato/pruebas && npm install && node validate.mjs
```

**El ejemplo mínimo** (todo lo demás es opcional):

```json
{
  "format": "fbr", "version": "1.0", "profile": "core",
  "meta": { "source": "manual" },
  "pitch": { "length_m": 105, "width_m": 68, "coordinates": "normalized" },
  "teams": [ { "id": "home", "name": "Local" }, { "id": "away", "name": "Visitante" } ],
  "actors": [ { "id": "BALL", "type": "ball" } ],
  "time": { "unit": "second", "duration": 90 },
  "tracks": [ { "actor": "BALL", "keyframes": [ [0, 0.5, 0.5], [5, 0.9, 0.4] ] } ],
  "events": []
}
```

## Estructura del repositorio

```
.
├── formato/                     La especificación FBR (el estándar)
│   ├── SPEC.md                  Especificación normativa v1.0
│   ├── fbr.schema.json          JSON Schema oficial (draft 2020-12)
│   ├── FBR-EXTENSIONS-DRAFT.md   Núcleo vs extensiones + gate
│   ├── i18n/                    Catálogos de idiomas (en canónico + 5)
│   ├── ejemplos/               Ejemplos (incluye un partido real completo)
│   └── pruebas/                Validadores (py + js) y batería de conformidad
├── ARCHITECTURE.md             Ecosistema: Core / Render / Extensions / Engine
├── prototipo/                  Engine/visor 2D de referencia (HTML autocontenido)
├── docs/                       Sitio de documentación (GitHub Pages)
├── CITATION.cff                Metadatos de cita (Zenodo/GitHub)
├── GOVERNANCE.md · CONTRIBUTING.md
└── LICENSE · AVISO-LEGAL.md
```

## Qué existe hoy y qué se propone

**Existe y es verificable:** la especificación v1.0, el JSON Schema, el validador semántico
(Python + Node) con batería de conformidad en CI, el visor 2D de referencia y los catálogos i18n.

**[Propuesto]** — aún no existe: un visor que lea *solo* el `.fbr.json` (sin datos incrustados),
conversores (`kloppy`, StatsBomb, EPTS), SDKs/CLI, sitio web y una capa de **Render 3D**
(reservada en `ARCHITECTURE.md`, no especificada). No se presentan como si existieran.

El verdadero cuello de botella **no es la documentación, es la adopción**: un segundo usuario, un
conversor y un corpus de ejemplos. Ese es el foco.

## Cómo citar

Ver [`CITATION.cff`](CITATION.cff). Cada versión estable debería depositarse en
[Zenodo](https://zenodo.org) para obtener un DOI citable.

## Licencia

Licencia **dual**, como es habitual en los estándares abiertos:

- **Especificación y documentación normativa** (`SPEC.md`, `fbr.schema.json`, `i18n/`, `ejemplos/`)
  → **CC-BY-4.0** (ver [`LICENSE-SPEC`](LICENSE-SPEC)).
- **Código y herramientas** (validadores, visor de referencia, QA) → **MIT** (ver [`LICENSE`](LICENSE)).

El visor de referencia tiene **identidad visual propia** y **no reproduce la interfaz de ningún
tercero** (ver `AVISO-LEGAL.md`). El formato es IP limpia y publicable.

## Aviso

Este proyecto usa marcas y datos de terceros con fines ilustrativos. Ver
[`AVISO-LEGAL.md`](AVISO-LEGAL.md). No constituye asesoría legal.
