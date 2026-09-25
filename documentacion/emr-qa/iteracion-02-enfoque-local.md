# Iteración 2 — Enfoque local

**Estado:** vigente (implementado en `emr-qa/shell/`) · **Fecha:** 2026-07-29

Validador de archivos tabulares locales con pandas y PySide6. La iteración 1 (captura HTML / scraper de pantallas) está **archivada** en `emr-qa/ALPHA/` — fuera del alcance activo.

---

## Decisiones acordadas

| Tema | Decisión |
|------|----------|
| **Entrada** | Archivos **locales** — CSV, TSV, PSV en disco |
| **Motor** | **pandas** + plantillas JSON v2.0 |
| **UI** | PySide6 — Abrir, Probar, Referencia, métricas |
| **SFTP / BD remota** | **Fuera de alcance** del flujo activo |
| **Apariencia** | Tema compartido con `ui/theme/` (wallpaper, chrome claro/oscuro) |

---

## Capacidades implementadas

| Capacidad | Ubicación |
|-----------|-----------|
| Navegador local | `shell/` + `core/local_browser.py` |
| Visor tabular | `ui/widgets/data_viewer.py` |
| Validación template | `emrqa/` + `shell/validation_runner.py` |
| Comparación referencia | `core/reference_compare.py` + tab Referencia |
| Métricas + PDF | `shell/qa_metrics*.py`, `shell/reference_metrics*.py` |

---

## Qué se descarta (respecto a PDE legacy)

- Módulo SFTP como flujo principal
- Panel de llaves SSH
- Conexión remota Transfer Family

*(Código legacy puede existir en el repo; no es el producto activo.)*

---

## Arquitectura

```text
emr-qa/
  shell/           app PySide6
  emrqa/           templates + validación
  core/            referencia, métricas, transforms
  reutiliza:
    ui/theme/*, ui/widgets/data_viewer
    adapters/pandas_analyzer
```

Arranque: `./scripts/run_emr_qa_editor.sh` → `emr-qa/shell/app.py`

---

## Documentos relacionados

| Archivo | Contenido |
|---------|-----------|
| [iteracion-02-funcionalidades.md](./iteracion-02-funcionalidades.md) | Funcionalidades Abrir/Probar |
| [iteracion-02-template-schema.md](./iteracion-02-template-schema.md) | Schema v2.0 |
| [README.md](./README.md) | Spec del módulo activo |
| [adr/0002-validador-tabular-compartible.md](./adr/0002-validador-tabular-compartible.md) | Alcance y distribución |

---

## Relación con otros módulos

| Módulo | Relación |
|--------|----------|
| Pandas | Core del análisis tabular |
| UI PySide6 | Shell y visor compartidos |
| SFTP legacy | Sin relación en flujo activo |
