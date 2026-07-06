# OpenFBR — Arquitectura del ecosistema

> Este documento fija la **nomenclatura** y los **límites** entre las piezas de OpenFBR. No
> especifica el contenido de Render (ver §4: está **reservado**, no escrito). Su objetivo es que
> la arquitectura sea real y estable **sin** añadir superficie que ningún consumidor pide todavía.

## 1. Nomenclatura

**OpenFBR** es el ecosistema/proyecto. **FBR** (Football Replay Format) es el formato de datos.
El ecosistema se organiza en cuatro piezas; dos son **especificaciones**, una es un **mecanismo**
y una es una **implementación** (no un estándar):

| Pieza | Qué es | Obligatorio | Estado |
|-------|--------|-------------|--------|
| **OpenFBR Core** | Especificación de **datos** del partido (`SPEC.md`) | Sí | **Existe** (v1.0) |
| **OpenFBR Render** | Especificación de **presentación** visual | No | **Reservado** — no especificado aún (§4) |
| **OpenFBR Extensions** | **Mecanismo** + *gate* para capacidades opcionales | No | **Existe** el mecanismo (`FBR-EXTENSIONS-DRAFT.md`) |
| **OpenFBR Engine** | **Implementación de referencia** (no es estándar) | — | **Existe en embrión** (visor 2D) |

Regla de oro: **Core y Render son estándares; Engine no.** El Engine interpreta los estándares;
puede haber muchos motores. Confundir "implementación de referencia" con "estándar" es un error
de categoría que este documento evita explícitamente.

## 2. Core (datos)

Describe **qué pasó espacialmente**: actores, slots, personas, `tracks`, `time`, eventos
mínimos. Es autosuficiente: un archivo Core **sin** Render es válido y completo, y un visor
mínimo lo reproduce en vista 2D por defecto. El movimiento lo define **solo** Core, mediante la
interpolación determinista normativa (SPEC §5.5). Esto es lo que ya está construido y verificado.

## 3. El *seam* Core ↔ Render (lo importante de esta nota)

La separación solo vale si el **contrato** entre ambas capas es nítido:

- Un partido = **un** archivo Core (`match.fbr.json`). La presentación = **cero o más** archivos
  Render (`render.*.json`). Relación **uno-a-muchos**: mismo Core, muchos Render (2D táctico,
  3D realista, *cartoon*, *wireframe*, retro…).
- Render **referencia** al Core (por ruta o URL) y se ancla por los **identificadores estables**
  de Core: `actors[].id`, `teams[].id`, `squad[].id`. Por eso Core insiste en ids estables (el
  modelo de identidad persona/slot no es un capricho: es lo que hace referenciable la presentación).
- **Regla dura:** *Render NO altera los datos.* Es **pura presentación**. Render decide **aspecto**
  (modelos, materiales, cámaras, luces); **nunca** posiciones, tiempos ni eventos. Si dos archivos
  Render discrepan sobre dónde está un jugador, ambos están mal: esa verdad vive en Core.
- **Determinismo preservado:** como el movimiento lo fija Core, cambiar de Render no cambia el
  replay, solo cómo se ve. Es la misma garantía que da glTF al separar geometría de materiales.

```
match.fbr.json  (Core, la verdad espacial)
   ▲     ▲     ▲
   │     │     │        (uno-a-muchos, por referencia + ids estables)
render.realista.json  render.cartoon.json  render.wireframe.json
```

## 4. Render (presentación) — **reservado, no especificado**

Cuando exista, Render contendría el "cómo se ve": modelo del estadio, modelos GLB de jugadores,
texturas, materiales, iluminación, cámaras (TV, libre, sigue-balón, dron…), animaciones, HUD y
efectos. El modelo de referencia natural es **glTF** para la capa 3D.

**Por qué no se escribe hoy.** Especificar Render es un estándar comparable en tamaño al Core, y
la disciplina del proyecto (SPEC §2.2, *gate* de extensiones) exige que nada entre sin un
consumidor real. No hay aún un motor 3D que lo ejercite. Escribir la spec de Render ahora sería
superficie sin uso — exactamente el *overengineering* que las revisiones del proyecto señalaron.
El casillero queda **reservado** con este contrato de *seam*; el contenido se especificará el día
que una implementación 3D lo pida.

## 5. Extensions (capacidades opcionales)

Ya existe el **mecanismo** (espacios de nombres `ext.*`) y el **gate** de entrada
(`FBR-EXTENSIONS-DRAFT.md`): caso de uso documentado + ejemplo real + soporte en el visor de
referencia. Capacidades como VAR, biometría, clima, audio o narración son **candidatas legítimas**,
pero se registran **cuando un uso real aparece**, no se pre-declaran. El registro abierto de
extensiones es parte de la gobernanza futura, no una lista a rellenar hoy.

## 6. Engine (implementación de referencia)

*Pipeline* conceptual:

```
JSON → Parser → Timeline → Interpolator → Scene → Renderer
```

**Hoy** el visor 2D de referencia cubre `JSON → Parser → Timeline → Interpolator → Scene(2D) →
Renderer(SVG/Canvas)`. El `Renderer` 3D y la lectura de un archivo Render son trabajo futuro,
condicionado a que exista la spec de Render (§4). El Engine es **una** implementación de
referencia; el estándar no depende de ella, y otros motores son bienvenidos.

## 7. Por qué esta línea

glTF, OpenAPI y GeoJSON maduraron con un **núcleo estable + extensiones**, y sus capas de render o
sus ecosistemas llegaron **con** implementaciones y comunidad, no antes. Los dos riesgos del
proyecto siguen siendo el **overengineering** (añadir capas sin consumidor) y la **adopción**
(falta un segundo usuario). Esta nota **reserva la arquitectura** —que es barato y correcto— sin
**llenar Render** —que es caro y prematuro—. El día que haya un motor 3D y un segundo usuario, la
arquitectura ya estará lista para recibirlos sin reescribir el Core.
