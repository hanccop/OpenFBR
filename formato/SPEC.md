# FBR — Football Replay Format · Especificación v1.0

> **Football Replay Format (FBR)** es un formato JSON abierto para la **reconstrucción y
> reproducción ligera de partidos de fútbol mediante keyframes dispersos e interpolación
> determinista**. Ese es su alcance: **el estado espacial de un partido a lo largo del tiempo**.
> Todo lo demás (biografías, estadísticas, uniformes, analítica) es **extensión** opcional
> (ver `FBR-EXTENSIONS-DRAFT.md`).
>
> **Estado:** propuesta libre y abierta (*draft*). No es un estándar oficial. Autor único
> (ver §8: gobernanza honesta).
>
> **Qué lo hace distinto** (no "otro formato de datos de fútbol"): es **autorable a mano** y
> **legible en diff de Git**; se reproduce **en el navegador sin motor gráfico**; pesa
> **órdenes de magnitud menos** que un archivo de tracking (keyframes dispersos vs. muestreo
> por frame); y está pensado para ser **generado automáticamente** (visión por computador, IA,
> EPTS) tanto como escrito por una persona.
>
> **FBR *no* es "el PGN del fútbol".** El ajedrez es discreto y determinista; el fútbol es
> continuo y con 22 agentes simultáneos. FBR no pretende una notación completa y canónica del
> juego, sino una **reconstrucción espacial reproducible**: aproximada por diseño, honesta
> sobre su imprecisión (ver `confidence`, §5.11).

---

## 1. Filosofía y alcance

El fútbol es continuo y con 22 agentes simultáneos, así que **ninguna** notación
captura "todo". Cada formato elige una **capa**:

| Capa | Qué describe | Estándares/prior art |
|------|--------------|----------------------|
| Eventos | Acciones con balón (pase, remate…) con x,y,t | SPADL, StatsBomb, Opta |
| Tracking | Posición de cada jugador 10–25 Hz | FIFA/FC Barcelona EPTS |
| **Replay (FBR)** | **Recorrido reproducible por keyframes, autorable a mano** | *este documento* |

FBR se sitúa en la capa de **replay/animación**: describe *dónde está cada actor a
lo largo del tiempo* mediante **keyframes dispersos** (no una muestra por frame), de
modo que una persona pueda escribirlo sin un sistema de tracking, y cualquier visor
compatible pueda reproducirlo.

**FBR no compite** con SPADL/EPTS: es una capa complementaria, pensada para
entrenamiento, educación, periodismo y aficionados. Se recomienda que las
implementaciones ofrezcan conversores desde/hacia el ecosistema existente
(p. ej. `kloppy`), para interoperar en vez de competir.

---

## 2. Principios de diseño

1. **Legible por humanos.** JSON plano; nombres de campo en inglés (canónico).
2. **Disperso.** Se guardan *keyframes clave*; el visor interpola linealmente entre ellos.
3. **Autoexplicativo.** El archivo declara su sistema de coordenadas y unidad de tiempo.
4. **Versionado.** Todo archivo declara `format` y `version`.
5. **Interoperable.** Estructura cercana a convenciones comunes; convertible a otros formatos.

---

## 2.1 Terminología y conformidad

Las palabras clave **DEBE / NO DEBE / DEBERÍA / PUEDE** (MUST / MUST NOT / SHOULD / MAY) se
interpretan según RFC 2119/8174 cuando aparecen en mayúsculas.

- **actor** — entidad con posición: un *slot* de jugador, el balón o un oficial.
- **slot** — posición de la alineación (`actors[].id`, p. ej. `CI7`); lo ocupan personas.
- **persona** — ser humano con `person_id` estable en `teams[].squad`.
- **keyframe** — muestra `[t, x, y]`; el estado entre keyframes se **interpola** (§5.5).
- **track** — sucesión de keyframes de un actor.
- **perfil** — subconjunto de conformidad declarado en `profile` (§2.3).

Un archivo es **conforme a FBR Core** si valida contra el schema estructural (§7, capa 1),
satisface los **invariantes normativos** (§7.1) y **no** usa claves fuera del núcleo (§2.3).
Un **reproductor conforme** DEBE implementar la interpolación de §5.5 y el modelo de
orientación de §3.1; DEBE ignorar sin fallar cualquier clave de extensión que no soporte.

## 2.2 Núcleo, extensiones y perfiles

FBR se divide en un **núcleo** pequeño y estable (estado espacial + eventos mínimos) y
**extensiones** opcionales (identidad rica, uniformes, analítica, assets, eventos tácticos,
física del balón). La lista canónica de qué es núcleo y qué es extensión, y el *gate* de
entrada al núcleo, viven en **`FBR-EXTENSIONS-DRAFT.md`**.

## 2.3 Perfiles (`profile`)

`profile` es una **pista** de conformidad (no cambia el schema):

| Perfil | Contenido |
|--------|-----------|
| `core` | Solo núcleo: posiciones + eventos mínimos. Máxima interoperabilidad. |
| `extended` | Núcleo + identidad/stats, kit, staff, analytics, render. |
| `broadcast` | `extended` + assets (referencias a medios). |
| `tracking` | Núcleo con keyframes **densos** (autogenerados por visión/EPTS). |

---

## 3. Sistema de coordenadas

- **Origen `(0,0)`** = esquina del fondo del equipo **local** (`home`). El equipo `home`
  **ataca hacia `x=1`** (de izquierda a derecha si se mira con `home` abajo).
- `x` corre a lo **largo** del campo: `0` = línea de gol del equipo local (`home`),
  `1` = línea de gol del visitante (`away`).
- `y` corre a lo **ancho**: `0` a `1` de banda a banda.
- Valores **fuera de `[0,1]`** son válidos y representan el **circundante** (balón
  fuera, saques, asistentes por fuera de la banda). El visor decide cuánto margen dibuja.
- Si `pitch.coordinates` = `"normalized"`, `x,y ∈` (aprox.) `[-0.1, 1.1]`.
  Si = `"meters"`, `x ∈ [0, length_m]`, `y ∈ [0, width_m]`.

Conversión a metros (modo normalizado): `x_m = x · length_m`, `y_m = y · width_m`.

### 3.1 Orientación y cambio de campo (importante)

En el fútbol real los equipos **cambian de lado** en el segundo tiempo. Para evitar
ambigüedad, FBR usa por defecto un **marco lógico fijo**:

- `pitch.orientation` = `"fixed"` (**recomendado**): el equipo `home` ataca
  *siempre* hacia `x=1`, sin importar el tiempo. El autor **no invierte** las
  coordenadas al descanso; sigue anotando en el mismo marco lógico. (Es la misma
  convención de normalización de orientación que usa `kloppy`.)
- `pitch.orientation` = `"as-played"`: las coordenadas reflejan los **lados físicos**
  reales; en ese caso el lector debe invertir en el 2.º tiempo, y el archivo **debe**
  declarar `time.periods` para saber cuándo ocurre el cambio.

---

## 4. Base de tiempo

- `time.unit` = `"second"`. `t` es un número en segundos **desde el saque inicial**,
  admite decimales (p. ej. `2340`, `2340.25`).
- Los descansos y descuentos se expresan como segundos continuos de juego (a criterio
  del autor). `time.duration` es el segundo del pitido final.
- `time.periods` (opcional pero **recomendado**) delimita los tiempos:
  `[{ "period": 1, "start": 0, "end": 2760 }, { "period": 2, "start": 2760, "end": 5580 }]`.
  Es obligatorio si `pitch.orientation` = `"as-played"`.
- `time.breaks` (opcional) lista **pausas dentro del juego** que no son el entretiempo, p. ej.
  las **pausas de hidratación/enfriamiento**: `[{ "period": 1, "type": "cooling", "at": 1320, "duration": 180 }]`.
  El juego se congela y se reanuda desde el mismo punto; esos segundos se suman al descuento del
  periodo. Cada pausa puede además figurar como evento `type:"cooling-break"` en `events`.

---

## 5. Estructura del archivo

```jsonc
{
  "format": "fbr",
  "version": "0.7",
  "meta":  { … },        // metadatos del partido y del archivo (incl. score, schema, changelog)
  "pitch": { … },        // dimensiones y convención de coordenadas
  "teams": [ … ],        // dos equipos: home y away (con lineup rol→id)
  "actors":[ … ],        // jugadores (role, anchor, position, bio, stats), balón y árbitros
  "time":  { … },        // periodos, descuento y pausas (breaks)
  "tracks":[ … ],        // recorrido por actor (keyframes compactos [t,x,y])
  "events":[ … ],        // goles, tarjetas, cambios, remates, hidratación…
  "analytics": { … },    // (opcional) métricas derivadas por equipo
  "render":    { … },    // (opcional) sugerencias de visualización
  "extensions":{ … }     // (opcional) espacio reservado para módulos futuros
}
```

> **Diseño modular (v1.0).** El archivo separa lo **estático** (identidad de actores,
> equipos, cancha) de lo **dinámico** (`tracks`, `events`) y de lo **derivado/opcional**
> (`analytics`, `render`, `extensions`). Un visor puede ignorar cualquier módulo opcional
> sin perder la reproducción base. Esta estructura sintetiza las dos propuestas de evolución
> (optimización de datos + arquitectura modular) manteniendo compatibilidad hacia atrás.

### 5.1 `meta`
| Campo | Tipo | Req. | Notas |
|-------|------|------|-------|
| `match_id` | string/number | — | Id del partido |
| `competition` | string | — | p. ej. "FIFA World Cup 2026" |
| `stage` | string | — | p. ej. "Round of 32" |
| `date` | string (YYYY-MM-DD) | — | Fecha |
| `venue` | string | — | Sede |
| `score` | object | — | Marcador final: `{home, away}` |
| `source` | enum | ✔ | `manual` · `tracking` · `event-derived` |
| `author` | string | — | Autor de la reconstrucción |
| `license` | string | — | Licencia de **los datos** (p. ej. `CC-BY-4.0`) |

### 5.2 `pitch`
| Campo | Tipo | Req. | Notas |
|-------|------|------|-------|
| `length_m` | number | ✔ | Largo real (típ. 105) |
| `width_m` | number | ✔ | Ancho real (típ. 68) |
| `coordinates` | enum | ✔ | `normalized` · `meters` |
| `orientation` | enum | — | `fixed` (recom.) · `as-played`. Ver §3.1 |
| `out_of_bounds` | boolean | — | Si se permiten valores fuera de `[0,1]` |

### 5.3 `teams` (exactamente 2)
| Campo | Tipo | Req. | Notas |
|-------|------|------|-------|
| `id` | enum | ✔ | `home` · `away` |
| `name` | string | ✔ | Nombre |
| `code` | string | — | Código FIFA (CIV, NOR…) |
| `color` | string | — | Color hex |
| `formation` | string | — | p. ej. "4-2-3-1" |
| `coach` | string | — | Director técnico (DT) |
| `kit` | object | — | Uniforme: `{shirt, shorts, socks, split?}` — ver 5.3.1 |
| `staff` | array | — | Cuerpo técnico: `[{name, role}]` |
| `squad` | array | — | Registro de **personas** del equipo (v1.0): `[{id, number, name, bio?, stats?}]`. Reemplaza a `bench`; es la fuente de identidad que referencian `occupants` y `subs` (§5.7) |

#### 5.3.1 `kit` — uniforme (opcional)
Uniforme del equipo. `shirt` (camiseta), `shorts` (short) y `socks` (medias) son colores base hex.
La camiseta admite **configuraciones**, no solo un color: `pattern` (`solid`, `stripes`, `hoops`,
`sash`, `halves`, `quarters`, `pinstripes`, `checkerboard`, `gradient`), `secondary` (segundo color
del patrón), `trim` (vivos/ribetes) y `sleeves` (mangas). `boots` es el color por defecto de los
botines del equipo; cada jugador puede anularlo con `actors[].boots`.
`split` (opcional) son los porcentajes `[camiseta, short, medias]` con que un visor puede dibujar el
uniforme como **bandas dentro de la ficha del jugador** (de arriba abajo); por defecto `[58, 28, 14]`.
Como todo dato extra en FBR, **es opcional pintarlo**: un visor puede ignorarlo y usar un color plano.

```json
"kit": { "shirt": "#c8102e", "shorts": "#ffffff", "socks": "#c8102e",
         "pattern": "stripes", "secondary": "#000000", "trim": "#ffd700",
         "boots": "#111111", "split": [58, 28, 14] }
```

### 5.4 `actors`
En v1.0 un `actors[]` de tipo `player` es un **slot** (posición de la alineación), no una
persona. La identidad (nombre, dorsal, `bio`, `stats`) vive en `teams[].squad` y se enlaza por
`occupants` (ver §5.7).

| Campo | Tipo | Req. | Notas |
|-------|------|------|-------|
| `id` | string | ✔ | Único (p. ej. `CI0`, `BALL`, `REF1`) |
| `type` | enum | ✔ | `player` · `ball` · `official` |
| `team` | enum | — | `home`/`away` (solo `player`) |
| `role` | string | — | `GK`, `referee`, `assistant`, `fourth`… |
| `anchor` | object | (✔) | Posición **teórica** de la formación; obligatoria en jugadores de campo |
| `position` | object | — | Posición **base** (t=0); el movimiento real va en `tracks` |
| `occupants` | array | — | Qué **persona** (`person_id`) ocupó el slot en cada tramo; cubre `[0,duration]` (ver §5.7) |
| ~~`number` `name` `bio` `stats`~~ | — | — | **Movidos a `teams[].squad`** en v1.0 (identidad por persona) |
| ~~`active`~~ | — | — | **Obsoleto** (redundante con `occupants`) |

> **Archivo autosuficiente.** Un export completo incluye un `track` por cada jugador (no
> solo el balón), de modo que cualquier visor reproduce el replay sin lógica propia. Si un
> jugador no trae `track`, el visor puede dejarlo en su `position` base. Los recorridos
> pueden simplificarse (p. ej. Ramer–Douglas–Peucker) sin cambiar el formato.

Debe existir **al menos un** actor `type:"ball"`.

### 5.4.1 Varios balones (opcional)

A veces un balón se pierde (sale del estadio) y entra otro. FBR admite **varios**
actores `type:"ball"`, cada uno con su propio `track`. El cambio de balón vigente se marca
con un evento `type:"ball-change"`; el visor muestra, en cada instante, el balón indicado por
el último `ball-change`.

```jsonc
// dos balones, cada uno con su track; el cambio se marca como evento:
{ "id":"BALL",  "type":"ball" },
{ "id":"BALL2", "type":"ball" }
// … en events:
{ "t":3120, "type":"ball-change", "actor":"BALL2" }
```

La ventana `active` de versiones previas queda **obsoleta** (redundante con el evento
`ball-change`). Si solo hay **un** balón, no se marca nada.

### 5.4.2 Estadísticas del jugador (opcional)

En v1.0 las `stats` (y la `bio`) viven en la **persona** (`teams[].squad[]`), no en el slot.
Cada persona puede llevar un objeto `stats` con sus números **del partido**. Campos comunes:
`rating`, `minutes`, `goals`,
`assists`, `shots`, `shots_on_target`, `passes`, `accurate_passes`, `pass_accuracy`,
`tackles_won`, `fouls`, `yellow_cards`, `red_cards`. Todos opcionales; se admiten campos
adicionales (numéricos o texto).

Los **datos del jugador que no son del partido** (edad, club, nacionalidad, altura, pie
hábil) van aparte, en `bio`, para no mezclar biografía con rendimiento:

```jsonc
{ "id":"NO9","type":"player","team":"away","number":9,"name":"Haaland",
  "bio": { "age":25, "club":"Manchester City" },
  "stats": { "rating":7.0 } }
```

```jsonc
{ "id":"NO3","type":"player","team":"away","number":3,"name":"Ajer",
  "stats": { "rating":6.5, "minutes":90, "tackles_won":2, "accurate_passes":48,
             "goals":0, "assists":0, "fouls":0, "yellow_cards":0, "red_cards":0 } }
```

En un slot con cambio, las `stats` pueden ir por **ocupante** (`occupants[].stats`) para
distinguir al titular del suplente.

> **Visualización opcional (importante).** `stats` (y también la banca o el cuerpo técnico)
> es *solo dato*. El visor **no** debe pintarlo por defecto, porque satura la pantalla.
> Debe ofrecerse como una **capa que el usuario activa** (p. ej. una casilla
> "Valoraciones"), para no contaminar la vista base. La `formation` de cada equipo, en
> cambio, es un dato pequeño y puede mostrarse siempre (p. ej. "4-1-2-3").

**Modelo de slots.** Un actor `player` representa una **posición** en la cancha, no
necesariamente a una sola persona. Si esa posición la ocupan distintos jugadores por
un cambio, se listan en `occupants` con su rango de tiempo:

```jsonc
{ "id":"CI10","type":"player","team":"home","number":19,"name":"Pépé",
  "occupants":[ { "number":19,"name":"Pépé","from":0,"to":3540 },
                { "number":15,"name":"Amad Diallo","from":3540 } ] }
```
Así, un evento que apunte a `"actor":"CI10"` se refiere a **quien ocupe ese slot** en
ese instante (p. ej. Amad Diallo marca en `t=4440`). Esto mantiene **todas las
referencias por `id`**.

### 5.5 `tracks`
Un track por actor. **Interpolación (normativa).** Entre dos keyframes consecutivos
`[t₀,x₀,y₀]` y `[t₁,x₁,y₁]`, la posición en el instante `t ∈ [t₀,t₁]` **DEBE** calcularse por
interpolación **lineal** con **velocidad constante**:

```
s = (t − t₀) / (t₁ − t₀)          # 0 ≤ s ≤ 1
x(t) = x₀ + s·(x₁ − x₀)
y(t) = y₀ + s·(y₁ − y₀)
```

Antes del primer keyframe y después del último, el actor **DEBE** mantenerse **fijo** en ese
extremo (**retención**, sin extrapolar). Con estas reglas, **dos reproductores conformes
producen exactamente el mismo movimiento** para el mismo archivo. El método por defecto es
`linear`; un track PUEDE declarar `interpolation` explícitamente. Cualquier otro método
(`spline`, `bezier`, físico) es **extensión** (`ext.ball_physics`) y no forma parte del núcleo.

**Formato de keyframe (v1.0).** Una **sola** forma: la tupla `[t, x, y]` (`t` en segundos,
`x`/`y` normalizados). El track describe **solo movimiento**; el estado del balón (fuera,
saque, gol…) **no** va en la tupla: se representa como evento `ball-state` con el mismo `t`.

```jsonc
{ "actor": "BALL", "interpolation": "linear", "keyframes": [ [2338, 0.10, 0.46], [2352, 0.50, 0.50] ] }
// estado del balón, aparte, en events:
{ "t": 2340, "type": "ball-state", "state": "out_back" }
```

> **El balón, como caso especial.** Interpolar linealmente un pase largo o un tiro con parábola
> es **incorrecto** físicamente (falta la altura `z`, el efecto y la trayectoria curva). El
> núcleo lo asume: es una reconstrucción *espacial en planta*, no un motor físico. La altura y
> la parábola son la extensión `ext.ball_physics` (propuesta), no núcleo.
```
| Campo | Tipo | Req. | Notas |
|-------|------|------|-------|
| `actor` | string | ✔ | Debe existir en `actors` |
| `keyframes` | array | ✔ | ≥1 tupla `[t,x,y]`, ordenada por `t` (v1.0: forma única; ver §5.5) |

### 5.6 `events`
| Campo | Tipo | Req. | Notas |
|-------|------|------|-------|
| `t` | number | ✔ | Segundo del evento |
| `type` | enum | ✔ | `goal` · `card` · `substitution` · `shot` · `cooling-break` · `ball-change` · `pass` · `cross` · `dribble` · `tackle` · `interception` · `foul` · `offside` · `other` |
| `team` | enum | — | `home`/`away` |
| `actor` | string | — | **id** del actor/slot principal (goleador, amonestado, slot del cambio) |
| `assist` | string | — | **id** del asistente (en `goal`) |
| `recipient` | string | — | **id** del destinatario (en `pass`) |
| `card` | enum | — | `yellow` · `second_yellow` · `red` (en `card`) |
| `in` / `out` | string | — | Nombres legibles del que entra/sale (cambio simple) |
| `subs` | array | — | Cambios del evento: `[{in, out, slot}]` (permite doble cambio en un mismo minuto) |
| `detail` | string | — | Texto libre (con emojis, para mostrar tal cual) |

> Los tipos tácticos (`pass`, `tackle`, `foul`, `offside`, `dribble`, `interception`,
> `cross`) están reservados para cuando existan datos por acción (tracking o event-data);
> una reconstrucción a mano puede omitirlos.

Ejemplos:
```jsonc
{ "t":2340, "type":"goal", "team":"away", "actor":"NO10", "assist":"NO7",
  "detail":"39' ⚽ Nusa (asist. Ødegaard)" }
{ "t":3840, "type":"substitution", "team":"home",
  "subs":[ {"in":"Wahi","out":"Inao Oulaï","slot":"CI7"},
           {"in":"Amad Diallo","out":"Bonny","slot":"CI9"} ] }
```

> **Regla de consistencia (v0.2):** las referencias a participantes van por **`id`**
> (`actor`, `assist` apuntan a un actor/slot). Los campos `in`/`out` de un cambio son
> solo etiquetas legibles; el vínculo procesable es `actor` = id del slot afectado.

### 5.7 Roles, `anchor` y `lineup`
Cada actor `player` lleva `role` (`GK`, `LB`, `CB`, `RB`, `CDM`, `CM`, `AM`, `LW`, `ST`,
`RW`…) y `anchor` (posición **teórica** de la formación). `position` es la posición
**dinámica inicial** (t=0); comparar `position`/`track` con `anchor` mide desmarques o
fuera de posición. Cada equipo puede incluir `lineup`, que mapea el rol al **id** del actor
titular (arreglo si el rol se repite):

```jsonc
"lineup": { "GK":"CI0", "LB":"CI1", "CB":["CI2","CI3"], "RB":"CI4",
            "CDM":"CI5", "CM":["CI6","CI7"], "LW":"CI8", "ST":"CI9", "RW":"CI10" }
```

**Modelo de identidad (v1.0).** Se distinguen tres niveles, cada uno con su identificador:

1. **Persona** — un ser humano concreto. Vive en `teams[].squad`, con un `id` **estable y
   único** (p. ej. `"ci-wahi"`), su `number`, `name`, `bio` y `stats`. Es la **única** fuente
   de verdad sobre quién es quién.
2. **Slot** — una posición de la alineación (`actors[]` con `id` como `"CI7"`). Un slot no
   "es" una persona: es ocupado por personas a lo largo del tiempo.
3. **Ocupación** — `actors[].occupants` lista qué **persona** ocupó el slot en cada tramo,
   por `person_id`, cubriendo `[0, time.duration]` **sin huecos ni solapes**.

```jsonc
"teams": [{ "id":"home",
  "squad": [ { "id":"ci-inao-oulai", "number":26, "name":"Inao Oulaï", "bio":{"age":19} },
             { "id":"ci-wahi",       "number":12, "name":"Wahi",       "bio":{"age":23} } ] }]
"actors": [{ "id":"CI7", "type":"player", "role":"CM",
  "occupants": [ { "person":"ci-inao-oulai", "from":0,    "to":3840 },
                 { "person":"ci-wahi",       "from":3840, "to":6060 } ] }]
"events": [{ "t":3840, "type":"substitution",
  "subs":[ { "in":"ci-wahi", "out":"ci-inao-oulai", "slot":"CI7" } ] }]
```

Regla: **una entidad, un identificador; todo lo demás se referencia por ese id** (3.ª forma
normal). `occupants[].person`, `subs[].in/out` apuntan a `squad[].id`; `subs[].slot` y
`events[].actor` apuntan a `actors[].id`. Que estas referencias sean coherentes lo garantiza
el **validador semántico** (§7), porque JSON Schema no valida referencias cruzadas.
`bench` queda **obsoleto** (reemplazado por `squad` con ids).

### 5.8 `stats` en `basic` / `detailed`
Para uniformar, `stats` se separa en `basic` (siempre presente: `rating`, `minutes`) y
`detailed` (opcional: entradas, pases, faltas, etc.). En v1.0 las `stats` (y `bio`) viven en
la **persona** (`teams[].squad[]`), no en el slot.

```jsonc
"stats": { "basic": { "rating": 6.5, "minutes": 90 },
           "detailed": { "tackles_won": 2, "accurate_passes": 48 } }
```

### 5.9 `analytics`, `render`, `extensions` (opcionales)
- **`analytics`** — métricas derivadas. Totales por equipo en `analytics.team.{home,away}`
  (posesión, remates, pases, precisión, faltas, córners, offsides, tarjetas) y una
  **línea de posesión** `analytics.possession` = `[[t, "home"|"away"], …]` (cada punto marca
  desde qué segundo cambia la posesión). Reservado también para `xg`, mapas de calor y
  distancias cuando existan.
- **`render`** — sugerencias para el visor (no afectan los datos): `orientation`
  (`vertical`/`horizontal`), `theme`, `show_names`, `show_ratings`.
- **`assets`** — referencias opcionales a recursos externos (escudos, fotos, video, audio,
  texturas, modelos 3D). Solo URLs/rutas; **FBR no incrusta binarios**.
- **`extensions`** — objeto libre reservado para módulos futuros (firmas, IA…) sin romper
  compatibilidad. Un visor que no lo entienda debe ignorarlo.

### 5.10 Internacionalización (i18n)

**Principio: el archivo guarda códigos, no textos traducidos.** Los valores semánticos van
como **enumerados en inglés** (`role:"GK"`, `type:"goal"`, `period:"first_half"`,
`state:"out_back"`); **el visor traduce** con catálogos externos. El campo `detail` de un
evento es solo una etiqueta de conveniencia para mostrar tal cual; toda la información
procesable está en los códigos (`type`, `subtype`, `actor`, `assist`, `team`…), de modo que
un visor puede rotular en cualquier idioma **sin** `detail`.

**No se traducen:** nombres de jugadores, equipos, estadios ni árbitros.

Los catálogos oficiales viven en `formato/i18n/{en,es,fr,pt,de,it}.json`. **`en` es el idioma
canónico**: es la fuente de los códigos (no una traducción más) y el mapa contra el que se
valida la paridad de claves de todos los demás (lo chequea el validador, §7). Cada catálogo
mapea código → etiqueta para `roles`, `events`, `goal_subtypes`, `cards`, `periods`,
`ball_states` y `ui` (mensajes del visor). Ejemplo (`es.json`): `"roles":{"GK":"Arquero"}`,
`"events":{"goal":"Gol"}`.

### 5.11 Endurecimiento del esquema y cambios v1.0

Refinamientos para quitar ambigüedad e interoperar mejor:

- **`role`** es un **enumerado cerrado** (`GK, SW, CB, LB, RB, LWB, RWB, CDM, CM, CAM, LM, RM,
  LW, RW, CF, ST` + oficiales); para casos atípicos, usar el más cercano y detallar en
  `role_custom`.
- **`anchor` es obligatorio** para jugadores de campo (`role ≠ GK`).
- **`meta.date`** en **ISO 8601** (`YYYY-MM-DD`).
- **`schema_version`** en la raíz indica qué reglas aplicar (coincide con `version`).
- **`active`** y **`bench`** quedan **obsoletos** (reemplazados por `occupants` y `squad`).

**Cambios incompatibles introducidos en v1.0** (por eso el salto de `0.7` a `1.0`):

- **Identidad por `person_id`** (§5.7): `occupants` y `subs[].in/out` referencian personas de
  `teams[].squad`, no nombres libres. Es el cambio que rompe compatibilidad con `0.7`.
- **Keyframe único `[t,x,y]`** (§5.5): se elimina la forma objeto y el 4.º elemento de estado;
  el estado del balón pasa a eventos `ball-state`. Desaparece el `oneOf` del schema.
- **`confidence` con rúbrica** (abajo).

**Rúbrica de `confidence`.** No es una probabilidad estadística, sino un **nivel discreto de
fuente** — lo único que un autor humano puede reportar con honestidad. Documenta la
**imprecisión**, no la vuelve precisa:

| Valor | Criterio |
|-------|----------|
| `1.0` | Confirmado por transmisión oficial / acta arbitral (gol, tarjeta, cambio). |
| `0.8` | Visto en video, con minuto exacto confirmado. |
| `0.6` | Minuto aproximado (redondeado), evento confirmado. |
| `0.4` | Evento reconstruido de memoria / crónica, sin video. |

En `partido-78`: goles, tarjetas, cambios y pausas → `1.0`; remates con minuto aproximado →
`0.6`.

---

## 6. Ejemplos (de menor a mayor)

**6.1 Mínimo absoluto** (`profile: core`) — solo el balón moviéndose. Todo lo demás es opcional:

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

**6.2 Con dos jugadores y un gol** (`profile: core`) — un pase y remate, con 3 keyframes cada uno:

```json
{
  "format": "fbr", "version": "1.0", "profile": "core",
  "meta": { "source": "manual", "score": { "home": 1, "away": 0 } },
  "pitch": { "length_m": 105, "width_m": 68, "coordinates": "normalized", "orientation": "fixed" },
  "teams": [
    { "id": "home", "name": "Local",     "squad": [ { "id": "h-9", "number": 9, "name": "9" } ] },
    { "id": "away", "name": "Visitante", "squad": [ { "id": "a-1", "number": 1, "name": "1" } ] }
  ],
  "actors": [
    { "id": "H0", "type": "player", "team": "home", "role": "ST", "anchor": { "x": 0.75, "y": 0.5 },
      "occupants": [ { "person": "h-9", "from": 0, "to": 90 } ] },
    { "id": "A0", "type": "player", "team": "away", "role": "GK",
      "occupants": [ { "person": "a-1", "from": 0, "to": 90 } ] },
    { "id": "BALL", "type": "ball" }
  ],
  "time": { "unit": "second", "duration": 90 },
  "tracks": [
    { "actor": "H0",   "keyframes": [ [0, 0.75, 0.50], [8, 0.92, 0.50] ] },
    { "actor": "A0",   "keyframes": [ [0, 0.02, 0.50] ] },
    { "actor": "BALL", "keyframes": [ [0, 0.75, 0.50], [8, 0.98, 0.50] ] }
  ],
  "events": [
    { "t": 8, "type": "goal", "team": "home", "actor": "H0", "subtype": "normal", "confidence": 1.0 }
  ]
}
```

**6.3 Completo y real** — un partido entero, con identidad, kit, analítica e i18n, en
[`ejemplos/partido-78.fbr.json`](ejemplos/partido-78.fbr.json) (`profile: extended`).

---

## 7. Validación

FBR valida en **dos capas**, como toda spec seria (schema = forma; validador = invariantes de
negocio):

**Capa 1 — estructural.** Todo archivo debe validar contra
[`fbr.schema.json`](fbr.schema.json) (JSON Schema, draft 2020-12): tipos, enums, forma,
propiedades requeridas.

```bash
pip install jsonschema
python -c "import json,jsonschema; jsonschema.validate(json.load(open('ejemplos/partido-78.fbr.json')), json.load(open('fbr.schema.json'))); print('OK')"
```

**Capa 2 — semántica.** JSON Schema no puede expresar referencias cruzadas ni coherencia
temporal. Un **validador de referencia** (`pruebas/validar.py` y su equivalente Node
`pruebas/validate.mjs`) verifica los invariantes que el schema no alcanza:

- `id` de actores y `person_id` de `squad` **únicos**; sin duplicados.
- Toda referencia existe: `events[].actor/assist/recipient` y `subs[].slot` → `actors[].id`;
  `subs[].in/out` y `occupants[].person` → `squad[].id`.
- `occupants` de cada slot **cubren `[0, duration]` sin huecos ni solapes**.
- Cada `substitution` tiene un `t` **consistente** con el corte del ocupante saliente (±1 s).
- `lineup` de cada equipo resuelve a **exactamente 11** slots existentes.
- `tracks` con actor existente, keyframes en orden y `t`/coordenadas en rango.
- Eventos en orden y dentro del partido; `meta.date` ISO 8601; marcador coherente con los
  goles; versión soportada.
- **i18n**: `en` es canónico y todos los catálogos tienen exactamente sus mismas claves.

```bash
python3 pruebas/validar.py        # imprime pruebas/INFORME.md; exit≠0 si algo falla
node   pruebas/validate.mjs       # equivalente con AJV
```

La batería de conformidad (`pruebas/validos/`, `pruebas/invalidos/`) ejercita ambas capas:
los válidos deben aceptarse y los inválidos rechazarse, y corre en CI.

### 7.1 Invariantes (normativo)

Un archivo conforme **DEBE** cumplir (el validador de referencia hoy comprueba los marcados ✔):

- ✔ Cada `actors[].id` y cada `squad[].id` es **único**.
- ✔ Toda referencia resuelve: `events[].actor/assist/recipient`, `subs[].slot`, `tracks[].actor`
  → `actors[].id`; `subs[].in/out`, `occupants[].person` → `squad[].id`.
- ✔ Los `occupants` de un slot **cubren `[0, duration]` sin huecos ni solapes**.
- ✔ El `t` de cada `substitution` coincide (±1 s) con el corte del ocupante saliente.
- ✔ `lineup`, si está presente, resuelve a **11** slots existentes.
- ✔ Ningún evento con `t < 0` (p. ej. un cambio **antes del saque inicial** es inválido).
- ✔ Coordenadas y tiempos de keyframes dentro de rango; marcador coherente con los goles.
- Un mismo `número` **NO DEBERÍA** estar activo en dos personas simultáneamente en cancha.
- Un actor tras `card:"red"` **NO DEBERÍA** tener keyframes de movimiento posteriores.
- Con varios balones, a lo sumo **uno** debe considerarse *activo* en cada instante
  (se gestiona con `ball-change`, ext.).

Los tres últimos son **normativos** pero aún no automatizados; están en la hoja de ruta del
validador.

### 7.2 Gramática estructural (informativa)

```
Replay      ::= Meta Pitch Teams Actors Time Tracks Events Extension*
Meta        ::= source (date | score | author | license)?
Pitch       ::= length_m width_m coordinates orientation?
Teams       ::= Team{2}
Team        ::= id name lineup? squad? Extension*
Actors      ::= Actor+
Actor       ::= id type (role anchor position occupants)?          # player
              | id "ball" | id "official" role
Time        ::= unit kickoff? duration Period+
Tracks      ::= Track+
Track       ::= actor interpolation? Keyframe+
Keyframe    ::= "[" t x y "]"
Events      ::= Event*
Event       ::= t type CoreEventField* | t TacticalType TacticalField*   # tactical = ext
```

---

## 8. Consideraciones de estándar

### 8.1 Tipo de medio (MIME)

- **Media type propuesto:** `application/vnd.fbr+json`.
- **Extensión de archivo:** `.fbr.json`.
- **Codificación:** UTF-8 obligatoria. Los nombres propios (jugadores, equipos, estadios,
  árbitros) se preservan **sin transliterar**.
- Registro IANA: *ninguno todavía* (draft de autor único; se solicitará al madurar).

### 8.2 Serialización canónica

Para que el `diff` de Git sea significativo y dos exportadores produzcan bytes comparables,
la forma canónica **DEBERÍA**: usar JSON UTF-8 sin BOM; una tupla `[t,x,y]` por línea en
`keyframes`; claves de objeto en orden de aparición en esta spec; números sin ceros
superfluos; y `t` en segundos enteros salvo que `unit` indique otra cosa.

### 8.3 Consideraciones de seguridad

FBR es **solo datos**: no contiene binarios ni código ejecutable. `assets` (ext.) son **URLs**;
un visor **DEBE** tratarlas como no confiables (no ejecutar, respetar CORS, no exfiltrar).
Un archivo FBR puede describir hechos deportivos públicos; **no** debe usarse para almacenar
datos personales sensibles más allá de lo deportivo (nombre, dorsal, club).

### 8.4 Interoperabilidad (informativa)

FBR es una **capa de replay**, complementaria a los formatos de eventos/tracking. Mapa
conceptual para conversores (pendientes de implementar):

| Origen | Concepto origen | → FBR |
|--------|-----------------|-------|
| **kloppy** | `Player.player_id` | `squad[].id` (persona) |
| kloppy / EPTS | frames de tracking (10–25 Hz) | `tracks[].keyframes` (densos, `profile: tracking`) |
| **StatsBomb / SPADL** | evento con `location [x,y]`, `type` | `events[]` (`ext.tactical`) + `ball-state` |
| Metrica | coordenadas normalizadas `[0,1]` | directo a `x,y` (mismo convenio) |
| Opta | `qualifier`/minuto | `events[].subtype` + `confidence` por precisión de minuto |

El sentido inverso (FBR → kloppy) es viable porque el núcleo es un subconjunto espacial: se
exportan posiciones muestreadas desde los tracks. Estos conversores son **trabajo pendiente**
(ver §9); su ausencia hoy es la principal barrera de adopción, reconocida sin adornos.

---

## 9. Versionado y gobernanza

- **SemVer** para la spec. Cambios incompatibles suben la mayor (`1.0`, `2.0`); el núcleo (§2.2)
  cambia **más despacio** que las extensiones (`ext/0.x`, versionadas aparte).
- Cada versión con schema congelado **DEBERÍA** conservar un ejemplo mínimo que siga validando
  en CI (compatibilidad hacia atrás como *hecho verificable*, no como promesa). — *pendiente.*
- **Gobernanza (honesta):** actualmente **mantenido por un autor único**. Se aceptan *issues*;
  el proceso formal de PR/RFC se activará **con el primer colaborador o segundo usuario real**.
  No se promete un comité que no existe.
- **Licencias:** esta especificación y su documentación normativa se publican bajo
  **`CC-BY-4.0`** (ver `LICENSE-SPEC`); el código de referencia, bajo **`MIT`** (ver `LICENSE`).

## 10. Hoja de ruta

- [x] `v0.1` — esquema base + visor de referencia (este repo).
- [x] `v0.2` — orientación/cambio de campo, `time.periods`, modelo de slots (`occupants`),
      referencias consistentes por `id`.
- [x] `v0.3` — DT (`coach`), cuerpo técnico (`staff`), suplentes (`bench`) y **varios balones**
      (`active` + evento `ball-change`).
- [x] `v0.4` — estadísticas por jugador (`stats`: rating, minutos, pases, entradas, etc.),
      opcionales y de visualización activable.
- [x] `v0.5` — uniforme (`teams[].kit`: camiseta/short/medias + `split` de porcentajes) para
      dibujar el kit como bandas en la ficha del jugador.
- [x] `v0.6` — **archivo autosuficiente**: `actors[].position` (posición base) y un `track` por
      cada jugador (no solo el balón); biografía separada del rendimiento (`bio` vs `stats`);
      eventos **estructurados** (`team`, `actor`, `assist`, `card`, `subs[]`) además del `detail`;
      y `meta.score`.
- [x] Exportador del prototipo emite FBR `v0.6` nativo y autosuficiente.
- [x] `v0.7` — **síntesis de propuestas**: keyframes **compactos** `[t,x,y]` (+ estado del
      balón opcional); `role` + `anchor` por jugador y `lineup` rol→id por equipo; `stats`
      en `basic`/`detailed`; módulos opcionales `analytics`, `render` y `extensions`; tipos
      de evento tácticos reservados (`pass`, `tackle`, `foul`…). Compatible hacia atrás.
- [x] Exportador e importador del prototipo hablan FBR `v0.7` (leen compacto y `{t,x,y}`).
- [x] `v0.7` — **endurecimiento e i18n**: `role` y `state` del balón como **enums**;
      `anchor` obligatorio en jugadores de campo; `date` ISO 8601; `subs` obligatorio en
      cambios; eventos con `subtype`/`confidence`/`sequence_id`; `schema_version`; `analytics.possession`;
      módulo `assets`; catálogos i18n oficiales (`en/es/fr/pt`) con **códigos internos + traducción en el visor**.
- [x] **`v1.0`** — **cimientos verificables** (cambio incompatible): identidad por `person_id`
      (`squad` por equipo; `occupants` y `subs` por persona); **validador semántico** de
      invariantes (referencias, cobertura de `occupants`, coherencia de cambios, `lineup`=11);
      keyframe **único** `[t,x,y]` (estado del balón → evento `ball-state`, se elimina el
      `oneOf`); **rúbrica** de `confidence`; `en` canónico + catálogos `de`/`it` (6 idiomas);
      batería de conformidad y CI.
- [x] Exportador e importador del prototipo hablan FBR `v1.0`; el archivo de referencia se
      regenera desde el exportador y pasa ambas capas de validación.
- [ ] Visor de referencia que **lee exclusivamente** el `.fbr.json` (dogfooding, sin datos
      hardcodeados).
- [ ] `FBR-EXTENSIONS-DRAFT.md`: separar *core* estable de extensiones propuestas (gate YAGNI).
- [ ] Schemas congelados por versión (`schema/0.x/`) + fixtures de compatibilidad hacia atrás.
- [ ] Conversor `kloppy → FBR` y `FBR → kloppy`.
- [ ] Corpus de ejemplos abiertos.
- [ ] Extensión de archivo `.fbr.json` y tipo MIME propuesto.

## 11. Registro de cambios

**v1.0** — *(cambio incompatible; ver §5.7 y §5.11)*
- **Identidad por `person_id`**: `teams[].squad` registra a cada persona con id estable;
  `actors[].occupants` y `events[].subs[].in/out` referencian ese id. `bench` obsoleto.
- **Keyframe único** `[t,x,y]`: se elimina la forma objeto y el 4.º elemento de estado; el
  estado del balón se mueve a eventos `ball-state`. Desaparece el `oneOf` del schema.
- **`confidence`** con rúbrica cerrada (nivel de fuente, no probabilidad).
- **Validador semántico** de invariantes (`pruebas/validar.py`, `pruebas/validate.mjs`),
  documentado en §7 y ejercitado por la batería de conformidad en CI.
- **i18n**: `en` como catálogo canónico; se agregan `de` e `it` (6 idiomas).

**v0.5**
- `teams[].kit` = `{shirt, shorts, socks, split?}` — colores del uniforme y porcentajes
  `[camiseta, short, medias]` para pintar la ficha por bandas (por defecto `[58,28,14]`).
- `time.periods[]` admite `type` (`first_half`, `second_half`, `extra_first`, `extra_second`,
  `penalties`), `regulation_end` y `added_seconds` — así se representa el tiempo añadido de cada
  tiempo y queda **previsto el tiempo extra** para un empate en eliminatoria.
- Sigue el principio de visualización opcional: un visor puede ignorar `kit` y usar color plano.

**v0.4**
- `stats` por jugador (a nivel de actor o de `occupant`), con campos comunes y extensibles.
- Principio de **visualización opcional**: los datos extra no se pintan por defecto.

**v0.3**
- `teams[].coach` (DT), `teams[].staff` (cuerpo técnico) y `teams[].bench` (suplentes).
- Varios balones: se admite más de un actor `type:"ball"`, cada uno con ventana `active`;
  nuevo evento `ball-change` para marcar el reemplazo.

**v0.2**
- `pitch.orientation` (`fixed`/`as-played`) para resolver el **cambio de campo** al descanso.
- `time.periods` para delimitar tiempos.
- Modelo de **slots** con `occupants`: una posición puede cambiar de ocupante por un cambio.
- Regla de consistencia: participantes referenciados por **`id`** (antes los cambios usaban nombres).

**v0.1**
- Estructura base: `meta`, `pitch`, `teams`, `actors`, `time`, `tracks`, `events`.
