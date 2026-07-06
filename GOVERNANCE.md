# Gobernanza de OpenFBR

Este documento describe cómo se toman las decisiones **hoy**, con honestidad. No promete un
proceso que todavía no existe.

## Estado actual: autor único

OpenFBR lo mantiene actualmente **una sola persona**. Las decisiones de diseño las toma el
mantenedor. Se **aceptan *issues*** (reportes, dudas, propuestas), y se agradecen, pero no hay
todavía un comité, un proceso formal de RFC ni un flujo de revisión por pares.

## Cuándo cambia esto

El proceso formal (RFC/PR con revisión) se **activará con el primer colaborador o segundo usuario
real** del formato. Ese es el hito que justifica la ceremonia; antes, sería burocracia sin quorum.

## Versionado

- **SemVer** para la especificación. Un cambio incompatible sube la versión mayor.
- El **núcleo** (SPEC §2.2) cambia **más despacio** que las **extensiones** (`ext/0.x`,
  versionadas aparte).
- Cada versión estable debería tener su esquema congelado y un ejemplo que siga validando en CI
  (compatibilidad hacia atrás como *hecho verificable*). — *pendiente.*

## Entrada de nuevas capacidades al núcleo (*gate*)

Ninguna clave nueva entra al **núcleo** sin cumplir las tres condiciones de
`formato/FBR-EXTENSIONS-DRAFT.md`: (1) caso de uso documentado, (2) ejemplo real que la ejercite,
(3) soporte en el visor de referencia. Todo lo demás vive como **extensión** hasta que las cumpla.

## Licencias

Especificación y documentación normativa bajo **CC-BY-4.0** (ver `LICENSE-SPEC`); el código de
referencia (validadores, visor, QA) bajo **MIT** (ver `LICENSE`). Es la licencia dual habitual en
estándares abiertos.
