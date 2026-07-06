> **Estructura del visor (v1.0):**
> - `index.html` — **reproductor FBR genérico**: lee cualquier `.fbr.json` (botón «Cargar otro .fbr.json»)
>   y arranca con el partido 78 embebido. Es el visor de referencia.
> - `legacy/demo-civ-nor.html` — el demo original hecho a mano (CIV–Noruega). Se conserva como
>   referencia histórica y como *fixture* de la simulación de QA. No es el visor principal.

# Simulación de partido — Ficha de Mundial (prototipo)

> **Estado:** privado · interno · prototipo conceptual
> **No publicar ni compartir fuera del equipo** hasta definir la estrategia de presentación.

Visor de referencia del formato FBR: un **replay táctico 2D** con identidad propia («FBR Replay»).
Reproduce el movimiento de los 22 jugadores y el balón a lo largo del partido con un deslizador de
tiempo, como un *replay* navegable.

Partido de referencia: **Côte d'Ivoire 1–2 Noruega**, FIFA World Cup 2026, Octavos (Round of 32),
30 de junio de 2026, Dallas Stadium (AT&T Stadium, Arlington).

---

## Cómo ver la demo

1. Abre `prototipo/index.html` en cualquier navegador (doble clic). No requiere instalación ni internet.
2. La cancha sale **vertical por defecto** (formato móvil). Arriba del campo hay un botón para cambiar a **horizontal**.
3. Pulsa *play* o arrastra el **deslizador** para ver el partido avanzar.
4. Toca los puntos de la línea de tiempo (goles, tarjeta, cambios, remates) para saltar a cada jugada.
5. Teclado: barra espaciadora = play/pausa, flechas ←/→ = saltar 15 segundos.

---

## Estructura del repositorio

```
.
├── README.md            Este archivo
├── LICENSE              MIT (código) · LICENSE-SPEC  CC-BY-4.0 (especificación)
├── AVISO-LEGAL.md       Marcas y datos de terceros, no afiliación
├── .gitignore
├── prototipo/
│   └── index.html       La demo (HTML autocontenido)
├── propuesta/
│   ├── propuesta.md     One-pager / deck (por completar)
│   └── demo.mp4         Video corto de la demo (por agregar)
├── datos/
│   ├── partido-78.json  Eventos, alineaciones y posiciones (por agregar)
│   └── esquema-er.png   Diagrama de la base de datos (por agregar)
└── backend/             Para producción (futuro)
    ├── esquema.sql      CREATE TABLE de las tablas
    └── api.md           Especificación de endpoints
```

Hoy solo `prototipo/` está completo. El resto son carpetas reservadas que se llenan a medida que avanza el proyecto.

---

## Qué es real y qué es reconstruido

Importante tenerlo claro para cualquier presentación:

- **Real (verificado con prensa):** marcador, goleadores y minutos (Nusa 39', Amad Diallo 74',
  Haaland 86'), amonestación a Nusa (45+1'), cambios, alineaciones, sede y técnicos.
- **Reconstruido (ilustrativo):** las *trayectorias* minuto a minuto de jugadores y balón, y el
  minuto aproximado de los remates. En producción esto vendría del **dato de seguimiento (tracking)**
  que ya generan los partidos, no de una recreación.

---

## Fuente de datos (en producción)

Las posiciones que alimentan esta simulación no se capturan con GPS en un Mundial. El seguimiento es
**óptico**: en el Mundial 2026, cada estadio usa 16 cámaras que registran ~29 puntos del cuerpo de cada
jugador unas 50 veces por segundo, generando más de 150 millones de puntos por partido (proveedor: Hawk-Eye;
infraestructura: Lenovo). El balón oficial (Trionda) suma un sensor interno a 500 Hz para el instante exacto
de cada toque. El GPS (chalecos EPTS) sí se usa, pero sobre todo en entrenamientos y partidos de club, no como
fuente del tracking oficial del torneo.

Implicación para la propuesta: estos datos **ya existen** en cada partido. La idea no es capturarlos de nuevo,
sino reutilizar ese tracking (vía las tablas `frame`/`position`) para convertir la pestaña estática
«Rendimiento» en el replay navegable. El editor manual del prototipo queda para crear muestras o corregir;
el volumen real (millones de puntos) se ingesta automáticamente, no se teclea.

---

## Próximos pasos

1. Pulir y probar en celular.
2. Incrustar el aviso legal en la demo.
3. Grabar un video corto (1–2 min) → `propuesta/demo.mp4`.
4. Proteger autoría: commits fechados, documento de concepto firmado, repo privado.
5. Armar `propuesta/propuesta.md` (problema, solución, demo, valor, datos, PI).
6. Validar con otras personas.
7. Definir objetivo (adopción del formato / contratación / desarrollo propio).
8. Elegir canal oficial y revisión legal de políticas de "envío de ideas".
9. Presentar.
10. (Si se construye) licenciar el tracking y montar API + backend (`backend/`).

---

## Propiedad intelectual y confidencialidad

El código y el diseño originales de este repositorio están protegidos por derecho de autor de forma
automática desde su creación (en Perú, Decreto Legislativo N.° 822). El registro ante la Dirección de
Derecho de Autor del INDECOPI es opcional y declarativo, pero sirve como medio de prueba.

Este proyecto usa **marcas y datos de terceros** (FIFA, nombres de jugadores y selecciones) con fines
ilustrativos. El visor tiene **diseño propio** y **no reproduce interfaces de terceros**. Ver
[`AVISO-LEGAL.md`](AVISO-LEGAL.md) y [`LICENSE`](LICENSE).

Mantener el repositorio en **privado**. El historial de commits (con fecha y autor) es parte de la
prueba de autoría: usa mensajes de commit claros.

> Nota: este documento no constituye asesoría legal. Antes de presentar la propuesta formalmente,
> conviene la revisión de un abogado de propiedad intelectual.

---

**Autor:** [Tu nombre completo]  ·  **Año:** 2026  ·  **Lugar:** Perú
