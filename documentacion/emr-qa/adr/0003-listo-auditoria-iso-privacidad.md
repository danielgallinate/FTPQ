# ADR-0003 — Listo para auditoría (ISO 25010, privacidad, evidencia)

**Estado:** aceptado (fase de diseño; no es certificación emitida)  
**Fecha:** 2026-09-21  
**Supersede:** nada. Complementa [0002](./0002-validador-tabular-compartible.md).

## Contexto

La suite (`run_ui`, `run_emr_qa_editor`, jobs headless) revisa exports tabulares. El núcleo **no** es calidad de datos ni ceguera HIPAA: es **reproducibilidad del contrato de entrega** (forma y tipos que BI definió).

**Modelo operativo:** las reglas se crean en DEV (set QA) y el mismo job corre por CLI en superiores. La app **no clasifica PHI**: un catálogo con identificadores reales es una **circunstancia de política** (quién autorice ese job), no un defecto ni un modo de la aplicación. Se corrige con política de contenidos del catálogo/Git, no parcheando el motor.

**Divulgación:** la app no entrega al operador **más dato** del que ya tiene en disco. El visor, si se usa, es el mismo archivo local. La **salida del contrato** (CLI, manifiesto, veredicto) indica **cabeceras, existencia, conteos y códigos** — **nunca valores de celda**.

Catálogo, QA y referencia son extras. ISO/HIPAA/SOC 2 no son sello de este producto. El contexto PHI **no aplica** a la rúbrica de la app.

## Decisión

1. El veredicto oficial del núcleo (schema + llegada del archivo) afirma: *este artefacto sigue siendo el entregable que contratamos*, no *estos valores están bien*.
2. Mantener dos columnas en toda evaluación: **as-is (código)** vs **objetivo de diseño**.
3. **PHI-agnóstica.** No sabe qué es PHI. Catálogos con datos reales = política, no feature.
4. **Salida de validación:** cabeceras y existencia (y métricas agregadas), nunca payload de filas. No hay divulgación incremental respecto al archivo que el usuario ya posee.
5. **Fuera de rúbrica:** ofuscación, Safe Harbor, hashed PII. No se puntúa HIPAA sobre este producto.
6. Responder las cuatro preguntas de congelación como sigue.

### Preguntas de congelación

| # | Pregunta | Decisión |
|---|----------|----------|
| 1 | ¿Binario nativo Windows/macOS sin Python ni WSL2? | **Sí para el CLI** (`run_emr_qa_job`, `run_sftp_job`, batch) como objetivo de portabilidad. La UI PySide6 puede permanecer venv / macOS / WSL2 en una primera entrega. Reabrir congelado de 1.0.0 (PyInstaller/Nuitka) **solo** para esos puntos de entrada. No afirmar “certificación de portabilidad” hasta tener el artefacto y una prueba en Windows nativo **sin** WSL. |
| 2 | ¿Meta-schema de `job.json`? | **Sí.** JSON Schema (Draft 2020-12) para `EmrQaJob` y `SftpFetchJob`, validado **antes** de ejecutar. Los `*_col.schema.json` actuales son catálogos de columnas, no meta-schema del job. |
| 3 | ¿Trazas / salida con valores? | La **salida de contrato** no incluye datos de celda (cabeceras, existencia, conteos). No es control HIPAA: es el formato del veredicto. Catálogo con PHI se gobierna por política, no por detección en app. |
| 4 | ¿Huella del artefacto? | **Sí, SHA-256** del archivo analizado (bytes en disco), más `size_bytes` y `job_id`/`schema_id`. MD5 no es huella primaria. El veredicto queda anclado a un objeto inmutable. |

### Códigos de salida (objetivo)

Alineado al contrato de confianza (NO DATA no es fallo de CI):

| Exit | Significado |
|------|-------------|
| `0` | PASS o **NO DATA** (forma válida, cero registros) |
| `1` | FAIL de contrato (schema, catálogo, umbrales, referencia) |
| `2` | ERROR de entorno (tamaño, parseo, I/O, job inválido) |

**Deuda as-is:** `emr-qa/run_job.py` hoy devuelve `EXIT_NO_DATA = 3`. El diseño depreca 3 en favor de `0` + `status: NO_DATA` en JSON.

### Tope de tamaño (objetivo)

Pre-flight por `stat` **antes** de pandas. Cota CLI vigente en código: **1 GiB** (`CLI_PANDAS_MAX_BYTES`). Subir a 2 GiB requiere ADR de RAM (esperada **3× a 5×** el peso en disco). No documentar 2 GiB como hecho.

## Consecuencias

- Documentar matriz ISO 25010 y bordes en [`../evaluacion-iso-25010-y-cumplimiento.md`](../evaluacion-iso-25010-y-cumplimiento.md).
- Implementación posterior: meta-schema, hash en manifiesto, sanitización de errores, pre-parser CSV, empaquetado CLI. Este ADR **no** implementa esas piezas.
- Marketing interno no debe decir “certificado ISO / HIPAA / SOC 2”. Debe decir “controles de diseño alineados a…”.
- No presentar PASS de schema como “calidad de datos validada”.
- Catálogo con PHI real: **política**, no cambio de producto.
- Salida de job: cabeceras/existencia, no filas. La app no revela dato que el usuario no tuviera ya.

## Referencias

- ISO/IEC 25010:2011 (características de calidad de producto)
- HIPAA Privacy Rule (de-identificación Safe Harbor) y Security Rule (salvaguardas técnicas) — **mapeo de controles, no sello**
- AICPA TSC SOC 2 — CC6.1 / CC7.2 como *evidencia que una org podría presentar*, no Type II del autor
