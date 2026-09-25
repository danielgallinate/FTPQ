# Evaluación de diseño — ISO/IEC 25010, privacidad y bordes

**Fecha:** 2026-09-21  
**Estado:** diseño · **ADR:** [0003](./adr/0003-listo-auditoria-iso-privacidad.md)

Esto **no** es un certificado. Es una autoevaluación anclada al código más un objetivo industrial. Una auditoría corporativa debe poder leer la columna **As-is** y exigir la columna **Objetivo**.

**Tesis:** contrato de entrega. App PHI-agnóstica. Catálogo con datos reales = política. Salida de validación = cabeceras/existencia, no celdas. No hay más dato que el archivo que el usuario ya tenía.

**Superficies:** `./scripts/run_ui.sh` (llegada SFTP) · `./scripts/run_emr_qa_editor.sh` (diseño en DEV) · jobs headless (contrato en superiores).

---

## 1. ISO/IEC 25010

ISO 25010 describe *qué* medir. ISO 25023/25040 describen *cómo* medir en un proceso de evaluación. Aquí solo se usan las características de 25010.

| Característica | As-is (código) | Propuesta previa | Objetivo de diseño | Diagnóstico | Acción |
| --- | ---: | ---: | ---: | --- | --- |
| **Adecuación funcional** | 7.5 | 10 | 9.5 | Schema/referencia/QA existen; ∀ filas en CLI hasta 1 GiB. Faltan: manifiesto tipificado de bordes, catálogo ciego, meta-schema. Un 10 exigiría la matriz de §3 implementada. | Mantener cobertura total en CLI. No tratar la muestra UI como función de certificación. |
| **Eficiencia de desempeño** | 7.0 | 9.0 | 8.5 | Pandas in-memory; rechazo >200 MiB UI / >1 GiB CLI. No hay cota RAM publicada ni fail-fast a 2 GiB. | Documentar RAM 3×–5× disco. Pre-flight `stat` + código `FILE_SIZE_EXCEEDS_LIMIT`. Subir tope solo con ADR. |
| **Compatibilidad / portabilidad** | 6.5 | 6.5 | 8.5 (CLI) | macOS/Linux nativo; Windows = WSL2 o `windows-cli` estructural. 1.0.0 archivó PyInstaller. | Empaquetar **CLI** standalone (PyInstaller/Nuitka). UI puede seguir con venv. |
| **Operabilidad / usabilidad** | 8.0 | 8.5 | 9.0 | UI diseña; CLI ejecuta. Banner de muestra reciente. Riesgo: operador toma el grid por veredicto. | Etiqueta fija “Modo inspección — máx. 100 000 filas; veredicto = CLI”. |
| **Fiabilidad** | 7.5 | 8.0 | 9.0 | Exit 0/1/2 (+ **3** hoy si NO DATA). CSV corrupto → error genérico, no capa pre-parser. | Deprecar exit 3. Pre-parser de delimitado (comilla abierta → línea + `MALFORMED_FILE`). |
| **Seguridad** | n/a HIPAA | — | n/a | App agnóstica. Salida = cabeceras/existencia. Catálogo con datos reales = política. No hay divulgación extra vs el archivo ya en disco. | No meter detector PHI ni ofuscación en el motor. |
| **Mantenibilidad** | 8.0 | 8.5 | 9.0 | Jobs JSON + Git. Parseo por dataclasses, sin JSON Schema del job. | `job.schema.json` validado pre-flight. |

**Media as-is ≈ 7.3. Media objetivo (tras implementar ADR-0003) ≈ 8.9.** La propuesta 10/10 y 9.5 en seguridad describe el **destino**, no el producto de hoy.

---

## 2. Marcos de cumplimiento (mapeo de controles)

Ninguno de estos marcos certifica el binario por sí solo.

### A. HIPAA — **ni lo intentaré** (no aplica al puntaje)

La app no sabe qué es PHI. Un catálogo con identificadores reales es **circunstancia + política** (quién lo pone en el job y en Git). La salida de validación no lista valores. Safe Harbor y hashing de catálogos **no** son requisitos de producto.

### B. SOC 2 Type II (TSC — Security & Confidentiality)

SOC 2 Type II es un informe **sobre la organización** durante un periodo. El producto solo puede **producir evidencia** que esa org adjunte.

| Criterio | Evidencia que el diseño debe emitir |
| --- | --- |
| **CC6.1** cambios en reglas | Jobs y schemas en Git; promoción Dev → Stage → Prod **en el repo del cliente**. El historial de *este* repo no es el control de *su* producción. |
| **CC7.2** procesamiento | Manifiesto: `status`, capa (SCHEMA/CATALOG/REFERENCE), SHA-256 del CSV, SHA-256 del job, timestamp UTC, versión de motor. Determinista para el mismo par (archivo, job). |

### C. Portabilidad de ejecución

| Entorno | As-is | Objetivo |
| --- | --- | --- |
| macOS | `setup.sh` + Python 3.12 venv | CLI one-file opcional |
| Windows corporativo (WSL bloqueado) | Fricción real | CLI `.exe` sin WSL ni Python de sistema |
| `windows-cli/` | Tests estructurales, no suite completa | No sustituye el exe |

---

## 3. Matriz de bordes (requisito de manifiesto)

Estructura común objetivo:

```json
{
  "status": "PASS | FAIL | NO_DATA | REJECTED | MALFORMED_FILE",
  "layer": "PREFLIGHT | SCHEMA | CATALOG | REFERENCE | QA | ENGINE",
  "exit_code": 0,
  "artifact": { "path": "...", "sha256": "...", "size_bytes": 0 },
  "job": { "path": "...", "sha256": "..." },
  "reason_code": "FILE_SIZE_EXCEEDS_LIMIT",
  "counts": {},
  "detail": {}
}
```

`detail` **no** lleva valores de celda.

| Escenario | Comportamiento | Exit | Manifiesto |
| --- | --- | ---: | --- |
| Archivo > tope CLI (hoy 1 GiB) | Rechazo pre-flight, sin cargar pandas | 2 | `status: REJECTED`, `FILE_SIZE_EXCEEDS_LIMIT`, `max_allowed_bytes` |
| CSV malformado (comilla abierta) | Capa parseo; si hay número de línea, incluirlo | 2 | `status: MALFORMED_FILE`, `line_corrupted` opcional, sin fila |
| Columna inesperada (schema strict) | Contrato | 1 | `status: FAIL`, `layer: SCHEMA`, nombres de columnas **de esquema**, no celdas |
| 0 filas de datos, cabecera OK | NO DATA; no es fallo de calidad | **0** | `status: NO_DATA` |
| Valor fuera de catálogo | Conteos; nombres de columna; no el valor | 1 | `status: FAIL`, `layer: CATALOG`, `violations_count` |
| Job JSON inválido | Meta-schema | 2 | `status: REJECTED`, `reason: INVALID_JOB` |

**As-is:** `_result_to_json` usa `ok`/`verdict`/`messages`; no hay SHA-256 ni `reason_code` estable; NO DATA sale con exit **3**.

---

## 4. Preguntas congeladas

Ver [ADR-0003](./adr/0003-listo-auditoria-iso-privacidad.md): (1) exe CLI sí, UI después; (2) meta-schema sí; (3) sanitizar trazas sí; (4) SHA-256 del CSV sí.

---

## 5. Orden de implementación sugerido (no hecho en este ADR)

1. Manifiesto: hash, `reason_code`, exit 0 para NO DATA.  
2. Sanitizar `messages` / excepciones.  
3. JSON Schema de jobs + validación pre-flight.  
4. Pre-parser CSV malformado.  
5. (Opcional, política) no versionar catálogos con identificadores de prod — fuera del código.  
6. Empaquetado CLI Windows/macOS.

Hasta el paso 1–3, **no** usar puntuaciones 9–10 en seguridad o funcionalidad frente a auditoría.
