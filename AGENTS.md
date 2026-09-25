# AGENTS.md — FTPQ (validador tabular)

## Línea de desarrollo

**Repo activo:** `FTPQ/` — validador local de **archivos tabulares** con **pandas** (módulo `emr-qa/`).  
**Referencia congelada:** `SFTP TOOL/` (no editar).

- Alcance vigente: [`documentacion/alcance-validador-tabular.md`](documentacion/alcance-validador-tabular.md)
- Diseño auditoría (ISO 25010 / privacidad, no sello): [`documentacion/emr-qa/adr/0003-listo-auditoria-iso-privacidad.md`](documentacion/emr-qa/adr/0003-listo-auditoria-iso-privacidad.md)
- Guía rápida: [`DEV-FORK.md`](DEV-FORK.md)
- Baseline histórico: [`release/STABLE-1.0.0.md`](release/STABLE-1.0.0.md)

Abrir **solo esta carpeta** en Cursor.

---

## Contexto y mantenimiento

**Analizar / actualizar contexto del repo** → `@context-maintainer`

1. **`skills/context/reference.md`** — mapa de capas (doc, skills, rules, draft)
2. **`scripts/context-audit.py`** — auditoría rápida
3. **`scripts/sync-skills.sh`** — sync `skills/` → `.cursor/skills/`

---

## Módulo activo

| Módulo | Doc | Arranque | Estado |
|--------|-----|----------|--------|
| **EMR QA** | [`documentacion/emr-qa/`](documentacion/emr-qa/README.md) | `./scripts/run_emr_qa_editor.sh` | Validador tabular, referencia, métricas, PDF |

Legacy en repo (no prioritario): SFTP, UI PDE — ver `documentacion/sftp/` solo si se toca código histórico.

---

## Reglas Cursor

`.cursor/rules/` — especialmente **`alcance-validador-tabular.mdc`**, `scope-no-db.mdc`, `emr-qa-pyside6.mdc`, `cross-platform.mdc`

---

## Alcance y disclaimer

Herramienta de **ayuda local** para revisar textos tabulares con pandas.  
**Compartir/empaquetar permitido** (sin secretos ni datos sensibles reales).  
**El autor no se hace responsable** del uso por terceros — ver [`documentacion/alcance-validador-tabular.md`](documentacion/alcance-validador-tabular.md).

**Entorno:** Mac nativo o Windows WSL2 · Python 3.12+ · `./scripts/setup.sh`

---

## Repo layout

```text
core/           ← contratos, dominio (sin PySide6)
adapters/       ← pandas, filesystem; paramiko legacy
emr-qa/         ← validador tabular (activo)
ui/             ← PySide6 compartido
documentacion/  ← spec por módulo
skills/         ← contexto compacto
draft/          ← borrador — no fuente de verdad
mocks/          ← fixtures CSV
```
