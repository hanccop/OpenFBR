# FBR — Núcleo y extensiones (borrador `ext/0.1`)

> Este documento acompaña a `SPEC.md`. Define qué pertenece al **núcleo** estable de
> **Football Replay Format (FBR)** y qué es **extensión** opcional. Su propósito es mantener
> el núcleo pequeño (la crítica recurrente: FBR estaba creciendo hacia una base de datos de
> fútbol). El núcleo describe **una sola cosa**: el estado espacial reproducible de un partido.

## 1. Responsabilidad única del núcleo

> **FBR Core describe únicamente el estado espacial de un partido a lo largo del tiempo,
> mediante keyframes dispersos e interpolación determinista.**

Todo lo que no sea *posición en el tiempo* + los pocos *eventos* necesarios para rotular la
línea de tiempo (gol, tarjeta, cambio, remate, estado del balón) es **extensión**.

Regla de tamaño: el núcleo apunta a **≤ 20 claves** significativas. Antes de agregar una clave
al núcleo debe cumplirse el **gate** (§4).

## 2. Qué es núcleo (`FBR Core`)

| Bloque | Claves de núcleo |
|--------|------------------|
| Cabecera | `format`, `version`, `schema_version`, `profile` |
| `meta` | `source` (y, si aplica, `date`, `score`) |
| `pitch` | `length_m`, `width_m`, `coordinates`, `orientation` |
| `teams[]` | `id`, `name`, `lineup` (rol→id de slot) |
| `actors[]` | `id`, `type`, `role`, `anchor`, `position`, `occupants[]` (`person`,`from`,`to`) |
| `time` | `unit`, `kickoff`, `duration`, `periods[]` |
| `tracks[]` | `actor`, `keyframes` (`[t,x,y]`), `interpolation` |
| `events[]` | `t`, `type` ∈ {`goal`,`card`,`substitution`,`shot`,`cooling-break`,`ball-state`}, `team`, `actor`, `assist`, `subs[]`, `card`, `subtype`, `state`, `confidence`, `detail` |
| identidad | `teams[].squad[]` **solo** `{id, number, name}` (lo mínimo para resolver `person_id`) |

El núcleo **no** incluye biografías, estadísticas, uniformes, cuerpo técnico, analítica,
render, assets, ni eventos tácticos.

## 3. Extensiones (`ext/0.1`, opcionales)

Cada extensión es un conjunto de claves con un espacio propio. Un visor que no la entienda
**debe ignorarla** sin romperse.

| Extensión | Claves | Motivación |
|-----------|--------|-----------|
| `ext.identity` | `squad[].bio`, `squad[].stats`, `squad[].role` | Ficha del jugador (edad, club, rating…). |
| `ext.kit` | `teams[].kit` (`shirt/shorts/socks/split/pattern/boots`), `color`, `code` | Dibujar el uniforme. |
| `ext.staff` | `teams[].coach`, `teams[].staff`, `teams[].formation` | Cuerpo técnico y formación nominal. |
| `ext.analytics` | `analytics.team.*`, `analytics.possession` | Totales y línea de posesión. |
| `ext.render` | `render.*` | Sugerencias de visualización (no afectan datos). |
| `ext.assets` | `assets.*` | URLs a escudos, fotos, video, modelos 3D (**nunca** binarios embebidos). |
| `ext.tactical` | `events[].type` ∈ {`pass`,`cross`,`dribble`,`tackle`,`interception`,`foul`,`offside`,`ball-change`,`other`}, `sequence_id`, `play_id` | Anotación por acción, estilo SPADL/StatsBomb. |
| `ext.ball_physics` | keyframe/track del balón con `z`, `spin`, `trajectory` (`linear`/`parabolic`) | El balón no es un actor plano: parábolas de pase largo, altura, efecto. **Propuesto, aún no en el schema.** |
| `ext.freeform` | objeto `extensions{}` | Cajón reservado (firmas, IA, metadatos privados). |

## 4. Gate de entrada al núcleo (YAGNI)

Ninguna clave nueva entra al **núcleo** sin cumplir las **tres** condiciones:

1. **Caso de uso documentado** — por qué un reproductor *espacial* la necesita (no "estaría bueno").
2. **Ejemplo que la ejercite** — un `.fbr.json` real (no de laboratorio) que la use.
3. **Soporte en el visor de referencia** — que la consuma de forma no trivial (no "la ignora sin romperse").

Mientras una capacidad no cumpla las tres, vive aquí, en `ext/`, versionada aparte del núcleo.

## 5. Perfiles

Un archivo declara su perfil en `profile` (pista, no cambia el schema):

- **`core`** — solo núcleo (§2). Máxima interoperabilidad.
- **`extended`** — núcleo + `ext.identity`, `ext.kit`, `ext.staff`, `ext.analytics`, `ext.render`.
- **`broadcast`** — `extended` + `ext.assets` (referencias a medios) para reproducción rica.
- **`tracking`** — núcleo con keyframes **densos** (alta frecuencia, típicamente autogenerados por visión/EPTS); mismo schema, distinta densidad y procedencia.

`partido-78.fbr.json` es `profile: "extended"`.
