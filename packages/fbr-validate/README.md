# fbr-validate

Validador del **formato FBR** (Football Replay Format) — el formato JSON abierto para
reconstruir y reproducir el estado espacial de un partido de fútbol mediante *keyframes*
dispersos e interpolación determinista.

Valida en **dos capas**:

1. **Estructura** — contra el JSON Schema (draft 2020-12) incluido en el paquete.
2. **Semántica** — invariantes que el schema no puede expresar: referencias que resuelven
   (`actor`, `assist`, `subs`, `occupants`…), cobertura de `occupants` sobre `[0, duración]`
   sin huecos, coherencia del marcador con los goles, `lineup` de 11, rangos de tiempo y
   coordenadas, fecha ISO 8601 y versión soportada.

## Uso rápido (sin instalar)

```bash
npx fbr-validate match.fbr.json
```

## Instalación

```bash
npm install -g fbr-validate     # CLI global
# o como dependencia de proyecto:
npm install fbr-validate
```

## CLI

```bash
fbr-validate partido.fbr.json                 # un archivo
fbr-validate *.fbr.json                        # varios
fbr-validate --json partido.fbr.json           # salida JSON (para CI)
fbr-validate --help
```

Sale con código **0** si todos los archivos son válidos y **1** si alguno falla — apto para
usar en un *hook* de pre-commit o en CI.

Ejemplo de salida:

```
✓ partido-78.fbr.json — válido
✗ roto.fbr.json — inválido
    schema:    /events/0/confidence must be <= 1
    semántica: marcador inconsistente: goles {"home":1,"away":2} vs meta.score {"home":2,"away":2}

1/2 válidos
```

## API (librería)

```js
import { validate, validateFile } from "fbr-validate";

const r = validateFile("partido.fbr.json");
// { valid: true|false, schema: [...], semantic: [...] }

if (!r.valid) {
  console.error([...r.schema, ...r.semantic]);
  process.exit(1);
}
```

También se exporta el `schema` (el JSON Schema cargado) por si quieres compilarlo tú mismo.

## Qué NO hace

No reproduce ni renderiza el partido (eso es el visor de referencia), no convierte desde
otros formatos de *tracking* y no juzga si los datos son "reales": solo verifica que un
documento FBR sea **estructural y semánticamente conforme**.

## Licencia

MIT. La especificación del formato FBR se publica aparte bajo CC-BY-4.0.
Ver el repositorio OpenFBR.
