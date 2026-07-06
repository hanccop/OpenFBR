# Contribuir a OpenFBR

Gracias por el interés. Mientras el proyecto tenga un mantenedor único (ver `GOVERNANCE.md`), la
vía es simple.

## Reportar o proponer

Abre un *issue* describiendo el caso de uso o el problema. Para propuestas de cambio al formato,
incluye **por qué** un reproductor espacial lo necesita, no solo qué sería lindo tener.

## Cambios al formato: la regla de oro

Cualquier cambio a `SPEC.md` / `fbr.schema.json` **debe** pasar las dos capas de validación y la
batería de conformidad antes de considerarse:

```bash
python3 formato/pruebas/validar.py                 # debe dar APROBADO (exit 0)
cd formato/pruebas && npm install && node validate.mjs   # idem
```

Los archivos **válidos** deben seguir aceptándose y los **inválidos** rechazándose. Si agregas una
regla, agrega también su caso válido y su caso inválido.

## Nuevas claves de núcleo

Deben cumplir el *gate* de `formato/FBR-EXTENSIONS-DRAFT.md` (caso de uso + ejemplo + soporte en el
visor). Si no lo cumplen todavía, van como **extensión** (`ext.*`), no al núcleo.

## Internacionalización

Para agregar un idioma, copia `formato/i18n/en.json` (catálogo **canónico**) y traduce **solo los
valores**, manteniendo exactamente las mismas claves. El validador verifica la paridad contra `en`.

## Estilo

Menos es más. Este proyecto se define tanto por lo que rechaza como por lo que acepta. Una
contribución que **quita** ambigüedad o superficie es tan valiosa como una que agrega capacidad.
