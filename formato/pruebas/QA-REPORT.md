---
title: "OpenFBR / FBR — Informe de Aseguramiento de Calidad (QA)"
subtitle: "Especificación v1.0 · validación de formato + simulación del Engine"
date: "Julio de 2026"
lang: es
---

## Resumen ejecutivo

Se ejecutó una batería de QA independiente sobre las cuatro capas del proyecto (especificación,
JSON Schema, validadores de referencia y visor/Engine). **Todas las comprobaciones pasan.** En el
proceso se **detectó y corrigió un defecto real** (fixtures de prueba desactualizados) y se
documentaron dos observaciones de baja severidad que **no** afectan al formato.

| Área | Comprobaciones | Resultado |
|------|----------------|-----------|
| Capa de formato (schema + validadores + i18n) | 7 | **PASA** |
| Simulación del Engine (visor) | 9 (incl. 35 aserciones) | **PASA** |
| Paridad Python/Node | batería (23) + fuzzing (300) | **0 divergencias** |
| Determinismo (Engine y exportador) | — | **exacto** |

**Veredicto: APTO.** El formato es internamente consistente, verificable y determinista; el
Engine reproduce el replay dentro de los invariantes esperados. Las limitaciones conocidas son de
adopción y de alcance (visor 2D, sin conversores), no de calidad del núcleo.

## Alcance y metodología

Se validó **de forma independiente**, sin confiar en la salida de un solo validador:

- **Meta-validación** del `fbr.schema.json` como JSON Schema draft 2020-12.
- **Paridad cruzada Python ↔ Node**: cada archivo se juzga con los dos validadores de referencia
  y se compara el veredicto por archivo (no solo el resultado global).
- **Motivo de rechazo**: cada archivo inválido debe rechazarse por *su* defecto, no por otro.
- **Recomputación independiente** de los invariantes de `partido-78` (marcador, cobertura de
  `occupants`, coherencia de cambios, `lineup`, rangos) con código distinto al del validador.
- **Fuzzing**: 300 mutaciones aleatorias del archivo de referencia, comparando el veredicto de
  ambos validadores.
- **Simulación**: barrido de los 6 061 segundos del partido verificando invariantes físicos,
  determinismo, y que la interpolación del Engine coincide con la fórmula normativa.

Durante la ejecución se auditaron también los propios criterios de QA: dos dieron falsa alarma
(el mensaje de error de Python no incluía la ruta; el chequeo i18n no contemplaba códigos
documentados como `examples`) y se corrigieron antes de emitir el veredicto.

## Resultados — Capa de formato

| ID | Comprobación | Resultado |
|----|--------------|-----------|
| F1 | `fbr.schema.json` es un JSON Schema draft 2020-12 válido | PASA |
| F2a | Los 3 archivos válidos son aceptados por Python **y** Node | PASA |
| F2b | Los 21 archivos inválidos son rechazados por Python **y** Node | PASA |
| F2c | Paridad Python/Node en toda la batería | PASA |
| F3 | Cada inválido se rechaza por el motivo correcto (aislado) | PASA |
| F4 | Los códigos i18n existen en el schema (enum/const/examples/descr.) | PASA |
| F5 | Los 6 catálogos i18n están alineados con `en` (canónico) | PASA |
| F6 | Invariantes de `partido-78` recomputados de forma independiente | PASA |
| F7 | Fuzzing: paridad Python/Node en 300 mutaciones (0 divergencias) | PASA |

## Resultados — Simulación del Engine (visor)

| ID | Comprobación | Resultado |
|----|--------------|-----------|
| S1 | Suite del prototipo (35 aserciones) | PASA (35/35) |
| S2 | Barrido 0..TMAX: 11+11 jugadores + balón, finitos y en rango | PASA |
| S3 | Sin teletransporte de jugadores sin balón (< 0.12/seg) | PASA (máx 0.0735/seg) |
| S4 | Determinismo: `computeFrame(t)` reproducible | PASA |
| S5 | Interpolación del Engine == fórmula lineal normativa (§5.5) | PASA (error 0.0) |
| S6 | El export del Engine valida contra ambos validadores (*dogfooding*) | PASA |
| S7 | i18n: los 6 idiomas aplican y traducen | PASA |
| S8 | Determinismo del exportador (`buildFBR` reproducible) | PASA |
| S9 | `time`: 2 periodos coherentes, `duration == TMAX` | PASA |

Datos destacados: la interpolación del Engine coincide con la fórmula normativa con error
**0.0** (exacto); el exportador y `computeFrame` son **byte-idénticos** entre corridas
(determinismo real, no aproximado).

## Hallazgos

**H1 — Fixtures de prueba desactualizados. Severidad: media. Estado: CORREGIDO.**
18 de los 20 archivos inválidos se habían generado a partir de una versión **anterior** del
archivo de referencia, cuando las sustituciones referenciaban por **nombre** (`out: "Holmgren
Pedersen"`) en vez de por `person_id`. Como consecuencia, esos fixtures arrastraban un error
semántico espurio ajeno al defecto que cada uno debía aislar: seguían siendo rechazados, pero por
*dos* motivos, lo que rompe el principio de que cada caso inválido pruebe **una** cosa. Se
regeneraron los 20 inválidos desde la base v1.0 limpia; ahora cada uno aísla su defecto y la
batería completa vuelve a dar **APROBADO** en ambos validadores.

**H2 — "Salto" del portador del balón. Severidad: baja (cosmética). Estado: documentado.**
La simulación detectó un desplazamiento de 0.2068/seg en `t=5815`. Al aislarlo se comprobó que es
el jugador **en posesión**, que el visor dibuja sobre el balón y que "salta" de vuelta a su
trayectoria al perder la posesión. Es un comportamiento de **render** del visor, no del dato: los
jugadores sin balón nunca superan 0.0735/seg, y el export FBR (interpolado linealmente) es
continuo. No afecta al formato ni a la validación. Mejora futura opcional: suavizar el
(des)pegue del portador en unos frames.

**H3 — `subtype` de gol como enum abierto. Severidad: baja (diseño). Estado: CORREGIDO.**
El schema definía `subtype` como *string* libre para todos los eventos. Se **cerró** el catálogo
específicamente para los goles: mediante un `if/then`, un evento `goal` solo admite
`normal · penalty · own_goal · free_kick · header` (validado por el schema y alineado con el
catálogo i18n `goal_subtypes`), mientras que para otros tipos (`foul`, `shot`, `pass`…) `subtype`
sigue siendo libre. Se añadió el fixture inválido `21_goal_subtype_invalido` para cubrir el caso.

## Reproducibilidad

Un evaluador puede reproducir **todo** el veredicto desde el repositorio:

```bash
cd formato/pruebas && npm install
npm run qa          # validate.mjs + qa/qa_format.py + qa/qa_sim.cjs

# o por separado:
python3 validar.py            # batería: 3 válidos + 21 inválidos → APROBADO (exit 0)
node    validate.mjs          # ídem con AJV                       → APROBADO (exit 0)
python3 qa/qa_format.py       # F1–F7: paridad py/node, motivos, i18n, invariantes, fuzzing 300×
node    qa/qa_sim.cjs         # S2–S9: simulación del Engine, interpolación, dogfooding
```

Los guiones de paridad, **fuzzing** y **simulación del Engine** —antes fuera del repo— ahora están
incluidos en `formato/pruebas/qa/` (con su `README.md` y el arnés `harness.cjs`), de modo que el
veredicto de este informe es **reproducible de principio a fin** sin herramientas externas.

## Veredicto

**APTO para evaluación.** Tras corregir H1, las cuatro capas son consistentes entre sí y con la
especificación; el formato es determinista y verificable en sus dos niveles (estructural y
semántico); el Engine reproduce el replay dentro de los invariantes físicos esperados. Las
observaciones restantes (H2, H3) son de baja severidad y no comprometen la integridad del
formato. Con el visor ya neutralizado (identidad propia, sin reproducir interfaces de terceros)
y las licencias resueltas (especificación CC-BY-4.0, código MIT), el riesgo de marca/IP y el de
licencia quedan cerrados. Se reitera —como en toda la documentación del proyecto— que la solidez
técnica es **necesaria pero no suficiente**: el siguiente riesgo a gestionar es de **adopción**
(un segundo usuario, conversores desde formatos de tracking), no de calidad.
