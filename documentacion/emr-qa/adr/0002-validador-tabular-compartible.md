# ADR-0002 — Validador tabular compartible

**Estado:** aceptado · **Fecha:** 2026-08-05

## Contexto

El repo evolucionó de “PDE Desktop SFTP + uso individual estricto” a un **validador local de archivos tabulares** (`emr-qa/`) con pandas. El operador ya no depende de SFTP ni de un canal formal de distribución para el flujo de QA/referencia.

La política anterior (`alcance-uso-individual.md`, regla `no-distribucion-externa.mdc`) bloqueaba empaquetado y handoff ad hoc.

## Decisión

1. **Identidad del producto activo:** ayuda para revisar textos tabulares con pandas — carga local, métricas, comparación referencia, export.
2. **Sin responsabilidad del autor** sobre uso por terceros: disclaimer explícito en documentación y reglas.
3. **Compartir y empaquetar permitidos** (zip, repo clone), excluyendo secretos y datos sensibles reales.
4. **Retirar** la regla `no-distribucion-externa.mdc`; sustituir por `alcance-validador-tabular.mdc`.
5. **SFTP** deja de ser parte del alcance normativo del agente; código legacy permanece sin promoverse como flujo principal.

## Consecuencias

- El agente puede crear zips de handoff cuando el usuario lo solicite.
- `documentacion/alcance-validador-tabular.md` es la fuente de verdad del alcance.
- Referencias antiguas a “no compartir” en docs secundarios se actualizan gradualmente; `alcance-uso-individual.md` redirige al nuevo doc.

## Referencias

- [`../README.md`](../README.md)
- [`../../alcance-validador-tabular.md`](../../alcance-validador-tabular.md)
