# Jobs retirados

Jobs de iteraciones anteriores que se sacaron del listado activo (2026-09-08).

Esta subcarpeta **no se lee**: el batch (`core.batch_match.list_batch_job_configs`), la
pestaña Automatización (`shell/automation_tab.py`) y el selector de esquemas buscan
`*.job.json` y `*.schema.json` solo en el nivel superior de `jobs/`.

| Job | Modo | Motivo |
|-----|------|--------|
| `qa-run2.job.json` | qa | usa los catálogos `clinic_qa`, `fisicos_qa`, `icd_qa`, que ya no existen (`catalogs/` está vacía) → `CatalogValidationError: catalog not found` |
| `qa-catalog-sample.job.json` | qa | mismo motivo |
| `qa-run.job.json` | qa | experimento con nombre autogenerado por la UI; corría PASS pero sin evaluar celdas |
| `reference-sample.job.json` | reference | ejemplo de la iteración de referencia; ya no se usa |
| `schema-sample.job.json` | schema | duplicaba `sample_encounters.job.json` (mismo `schema_id: sample_encounters`), así que la misma prueba corría dos veces |

Ninguno tenía `batch_match`, salvo `schema-sample`, que lo heredaba del mapeo compartido.

Para reactivar uno: mover el archivo al nivel superior de `jobs/` y, si es modo `qa`
con catálogos, volver a crear los catálogos que referencia en `catalogs/`.
