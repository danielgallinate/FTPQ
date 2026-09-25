# Alcance — validador de archivos tabulares

**Decisión:** 2026-08-05 · **Estado:** vigente  
**Supersede:** política “uso individual / no distribución” (2026-07-17)

---

## Qué es este proyecto

FTPQ es una **herramienta de ayuda local** para **revisar textos tabulares** (CSV, TSV y similares) usando **pandas** y una interfaz PySide6.

**Objetivo central:** reproducir un **contrato de entrega** del export — la forma que BI ya definió (columnas, títulos, tipos, nulos, presencia del archivo) — de forma repetible. No certifica **calidad de datos** ni que el contenido sea “correcto de negocio”.

**Cómo se usa:** la regla se diseña en DEV (set QA) y se aplica por CLI en superiores. La app **no sabe qué es PHI**. Meter identificadores reales en un catálogo es una **decisión de política**, no algo que el código deba detectar o ofuscar. El visor no añade un dato que no estuviera ya en el archivo del usuario. La **salida de validación** (manifiesto, CLI) habla de **cabeceras y existencia**, no de valores de celda.

En BI el tipo y el layout de salida son parte del entregable. Esta suite vuelve a comprobar ese contrato en cada corrida (mismo job, otro día, otro origen). Catálogo, reglas QA y referencia son **capacidades opcionales** que *permiten* mirar contenido; no son el propósito del producto.

Casos de uso típicos:

- Cargar un extracto delimitado desde disco
- Validar el contrato de columnas/tipos (schema)
- Opcional: plantillas, catálogos y cruce contra otro archivo
- Ver métricas, filtrar NOK y exportar reporte (PDF, CSV, texto)

Todo el procesamiento ocurre **en la máquina del operador**, sobre archivos que él elige abrir. No hay obligación de conectar a SFTP, VPN ni bases de datos remotas para usar el flujo principal (`emr-qa/`).

---

## Disclaimer de uso

Este software se entrega **tal cual**, como utilidad personal de desarrollo y revisión.

- **No** constituye producto oficial de la organización.
- **No** garantiza cumplimiento HIPAA ni clasifica PHI. Un catálogo con datos reales se corrige con **política**, no con un parche de la app. Quien corre la herramienta sobre extracts reales aplica las reglas de *su* entorno.
- **No** es un validador de calidad de datos (completeness/accuracy de negocio). El PASS del contrato no afirma que los valores sean verdaderos.
- **El mantenedor no se hace responsable** de cómo otros instalen, compartan o usen el código o paquetes derivados, ni de los archivos que decidan analizar con la herramienta.

Quien ejecuta o recibe una copia es responsable de su entorno, de los datos que carga y de las políticas que le aplican.

---

## Compartir y empaquetar

**Permitido** compartir el repositorio, un zip del código fuente o un bundle mínimo para que un colega lo pruebe en su Mac o WSL2.

Al empaquetar:

| Incluir | Excluir |
|---------|---------|
| Código fuente y `scripts/setup.sh` | `.env`, tokens, llaves privadas |
| `requirements` / lock del venv | Datos reales de pacientes o clientes |
| README con `./scripts/run_emr_qa_editor.sh` | `.venv/` (regenerar con setup) |

El agente puede ayudar a crear el zip cuando lo pidas: `./scripts/package_handoff.sh`

---

## Entorno soportado

| Plataforma | Arranque |
|------------|----------|
| macOS nativo | `./scripts/setup.sh` → `./scripts/run_emr_qa_editor.sh` |
| Windows | **WSL2** + mismos scripts `.sh` |

Requisito: **Python 3.12+**.

---

## Evaluación industrial (diseño)

Auto-score ISO/IEC 25010 y mapeo a controles HIPAA/SOC 2: [`emr-qa/evaluacion-iso-25010-y-cumplimiento.md`](./emr-qa/evaluacion-iso-25010-y-cumplimiento.md). **No** constituye certificación de un organismo. El CLI aspira a veredicto sin mostrar filas (contrato de confianza); la UI sigue siendo inspección.

## Límites técnicos (sin ADR)

Sin base de datos remota en la fase actual: no Postgres/Snowflake como dependencia del validador. Ver regla `.cursor/rules/scope-no-db.mdc`.

Código legacy SFTP/UI y captura de pantallas (`emr-qa/ALPHA/`) pueden existir como referencia histórica; **no define** el alcance del producto activo.

---

## Referencias

- Módulo activo: [`emr-qa/README.md`](./emr-qa/README.md)
- ADR redefinición: [`emr-qa/adr/0002-validador-tabular-compartible.md`](./emr-qa/adr/0002-validador-tabular-compartible.md)
- Regla Cursor: [`.cursor/rules/alcance-validador-tabular.mdc`](../.cursor/rules/alcance-validador-tabular.mdc)
