# Batería de conformidad FBR

Conjunto oficial de archivos de prueba y validadores que implementan el
**Plan de Pruebas 1.0** del formato FBR. Sirve como suite de conformidad para
cualquier implementación (visores, importadores, librerías).

## Contenido

```
pruebas/
├── validos/          # deben APROBAR (mínimo, completo, multi-balón)
├── invalidos/        # deben RECHAZARSE (cada archivo rompe UNA regla)
├── validar.py        # validador de referencia (Python + jsonschema)
├── validate.mjs      # validador equivalente (Node + AJV)
├── package.json      # dependencias del validador AJV
└── INFORME.md        # último informe QA generado
```

Cada caso inválido está numerado por la regla que viola (falta de requerido,
tipo incorrecto, fuera de rango, propiedad adicional, rol fuera de enum, estado
de balón inválido, anchor ausente, sustitución sin `subs`, id duplicado,
referencia inexistente, tiempo negativo, evento fuera del partido, fecha no ISO,
marcador inconsistente, JSON inválido, archivo vacío, coordenada imposible).

## Cómo ejecutar

**Con Python** (validador de referencia; genera `INFORME.md`):

```bash
pip install jsonschema
python3 validar.py
```

**Con Node/AJV** (mismo veredicto, pensado para CI de JavaScript):

```bash
npm ci
npm test
```

Ambos validadores combinan **dos capas**:

1. **JSON Schema (draft 2020-12)** — estructura, tipos, enums, rangos, requeridos,
   `format: date`, `anchor` obligatorio en jugadores de campo, `subs` obligatorio
   en sustituciones, estado del balón como enum.
2. **Chequeos semánticos** (lo que el schema no puede expresar) — IDs duplicados,
   referencias colgantes (`actor`/`assist`/`recipient`/`slot`/`lineup`), orden
   cronológico de tracks y eventos, tiempo dentro de `[0, duración]`, coordenadas
   físicamente posibles, consistencia con el marcador y versión soportada.

Además se verifica que los catálogos i18n (`../i18n/{en,es,fr,pt}.json`) estén
alineados (mismas claves en todos los idiomas).

## Criterio de aceptación

El veredicto es **APROBADO** solo si: todos los válidos se aceptan, todos los
inválidos se rechazan, los módulos funcionales están presentes, el timeline tiene
periodos y pausas, y el i18n está alineado. Los validadores devuelven código de
salida `0` (APROBADO) o `1` (RECHAZADO), apto para integración continua
(ver `.github/workflows/fbr-ci.yml`).
