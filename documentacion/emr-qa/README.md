# Módulo EMR QA — validador tabular local

**Estado:** activo · **Arranque:** `./scripts/run_emr_qa_editor.sh` → `emr-qa/shell/app.py`

Validador de **archivos de texto tabulares** (CSV, TSV, PSV) con **pandas**. El objetivo central es **repetir el contrato de entrega** (columnas y tipos que BI definió), no certificar calidad de contenido. Plantillas, catálogos, referencia y métricas son extras opcionales.

Alcance global del repo: [`../alcance-validador-tabular.md`](../alcance-validador-tabular.md) · ADR: [`adr/0002-validador-tabular-compartible.md`](./adr/0002-validador-tabular-compartible.md) · Diseño auditoría: [`adr/0003-listo-auditoria-iso-privacidad.md`](./adr/0003-listo-auditoria-iso-privacidad.md)

---

## Qué es

| Capacidad | Descripción |
|-----------|-------------|
| **Abrir** | Visualizar archivo delimitado desde disco (navegador local en `~/Downloads`) |
| **Probar** | Validar filas contra plantilla (llaves, columnas, regex) |
| **Referencia** | Comparar archivo vs otro CSV de referencia (llaves + columnas) |
| **Métricas** | KPIs, tablas, gráficos, filtro NOK, pantalla completa |
| **Export** | PDF (tema claro), CSV, texto copiable |

Todo ocurre **en la máquina del operador**, sobre rutas locales que él elige. Sin SFTP, sin base de datos remota.

---

## Qué no es

- No es producto oficial ni servicio soportado por IT
- No garantiza compliance ni certificación de datos
- No sustituye pipelines de producción ni validadores regulatorios
- **No** valida calidad de datos de negocio (el contenido); valida que el archivo **sigue siendo el entregable acordado** (forma/tipos). Catálogo y referencia pueden usarse para contenido; no son el núcleo
- **No incluye** captura/scraping de pantallas web — ese enfoque está **archivado** en `emr-qa/ALPHA/` (solo referencia histórica)

---

## Flujo operativo

1. Arrancar `./scripts/run_emr_qa_editor.sh`
2. Navegar en `~/Downloads` (u otra carpeta local)
3. Doble clic en CSV/TSV → **Abrir** (visor) o **Probar** (validación)
4. Opcional: tab **Referencia** para comparar contra otro archivo
5. Exportar métricas o reporte cuando haga falta

Fixtures: [`emr-qa/fixtures/sample_encounters.csv`](../../emr-qa/fixtures/sample_encounters.csv)

---

## Documentos activos

| Archivo | Contenido |
|---------|-----------|
| [iteracion-02-funcionalidades.md](./iteracion-02-funcionalidades.md) | Abrir/Probar, tabs, template+minibase |
| [iteracion-02-template-schema.md](./iteracion-02-template-schema.md) | Schema JSON v2.0 |
| [iteracion-02-enfoque-local.md](./iteracion-02-enfoque-local.md) | Dirección local + pandas |
| [adr/0001-alcance-local-only.md](./adr/0001-alcance-local-only.md) | Sin BD remota (histórico, parcialmente superseded por ADR-0002) |
| [adr/0002-validador-tabular-compartible.md](./adr/0002-validador-tabular-compartible.md) | Identidad validador + compartir permitido |
| [adr/0003-listo-auditoria-iso-privacidad.md](./adr/0003-listo-auditoria-iso-privacidad.md) | Fase de diseño: ISO 25010, privacidad, manifiesto; no es sello certificador |
| [guion-presentacion-equipo.md](./guion-presentacion-equipo.md) | Talk track ~12 min para presentar la tool al equipo |

---

## Código activo

```text
emr-qa/
  shell/              app PySide6 (Abrir, Probar, Referencia, métricas)
  emrqa/              motor template + validación v2.0
  core/               compare referencia, métricas, transformaciones
  knowledge_bases/    plantillas de ejemplo
  fixtures/           CSV de prueba
  ALPHA/              archivo histórico — no documentar como flujo activo
```

---

## Límites de tamaño

| Contexto | Tope | Sobre el tope |
|----------|------|----------------|
| UI (`emr-qa/shell/`) | 200 MiB (`DEFAULT_MAX_BYTES`) | Abre una **muestra** de hasta 100 000 filas (`UI_SAMPLE_MAX_ROWS`); el dataset queda `sampled=True` y las métricas describen solo la muestra |
| CLI (`./scripts/run_emr_qa_job.sh`) | 1 GiB (`CLI_PANDAS_MAX_BYTES`) | Error `AnalysisTooLargeError` |

`estimated_total_rows` aproxima el total del archivo por bytes/línea leyendo solo la cabeza; es una estimación, no un conteo. El veredicto sobre el archivo completo sale del CLI.

---

## Relación con otros módulos

| Módulo | Relación |
|--------|----------|
| `ui/` | Tema, widgets tabulares, visor datos |
| `adapters/pandas_analyzer.py` | Carga y análisis de archivos |
| SFTP / PDE UI legacy | Exploración en UI. Job headless: `./scripts/run_sftp_job.sh` (existencia + descarga). EMR QA sigue validando **solo archivos locales** (`--file`). |
