---
title: OpenFBR — Football Replay Format
---

# OpenFBR · Football Replay Format (FBR)

Formato JSON abierto para **reconstruir y reproducir el estado espacial de un partido de fútbol**
mediante *keyframes* dispersos e interpolación determinista. Ligero, legible, autorable a mano y
reproducible igual en cualquier visor.

> **Estado:** *draft* v1.0 · autor único · no es un estándar oficial.

## Learn
- [¿Por qué FBR? Visión y fundamentos de diseño](../ARCHITECTURE.md) — el *porqué* de las decisiones.
- El problema: eventos vs. *tracking* vs. *replay* (ver la especificación, §1).

## Specification
- [Especificación v1.0 (`SPEC.md`)](../formato/SPEC.md) — normativa.
- [JSON Schema oficial](../formato/fbr.schema.json) — draft 2020-12.
- [Núcleo y extensiones](../formato/FBR-EXTENSIONS-DRAFT.md) — qué es núcleo y qué no.
- [Arquitectura del ecosistema](../ARCHITECTURE.md) — Core / Render / Extensions / Engine.

## Tools
- **Visor 2D de referencia** — `prototipo/index.html` (abrir en el navegador).
- **Validador** — `formato/pruebas/validar.py` (Python) y `validate.mjs` (Node): esquema + invariantes.

## Examples
- [Partido real completo](../formato/ejemplos/partido-78.fbr.json) — Côte d'Ivoire 1–2 Noruega.
- Ejemplo mínimo — ver el `README` o la especificación, §6.

## Community
- Contribuir: [`CONTRIBUTING.md`](../CONTRIBUTING.md) · Gobernanza: [`GOVERNANCE.md`](../GOVERNANCE.md).
- Cómo citar: [`CITATION.cff`](../CITATION.cff) (DOI vía Zenodo al publicar).

## Resources
- Licencia y aviso legal: ver el `README`.
