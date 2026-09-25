# PDE Desktop — Documentación

**Línea activa FTPQ** (dev post-1.0.0): [`linea-desarrollo.md`](./linea-desarrollo.md) · Baseline: [`../release/STABLE-1.0.0.md`](../release/STABLE-1.0.0.md)

**Validador tabular local (pandas):** [`alcance-validador-tabular.md`](./alcance-validador-tabular.md)

Cada **módulo** tiene su carpeta. No mezclar SFTP, pandas ni UI en el mismo archivo.

## Regla de organización

| Qué va aquí | Qué NO va aquí |
|-------------|----------------|
| Comportamiento del dominio | Cómo se ve en pantalla → `ui/` |
| Restricciones técnicas del módulo | Reglas pandas → `pandas/` |
| Contratos / APIs del módulo | Lógica SFTP → `sftp/` |

Referencias cruzadas entre módulos: enlazar, no duplicar párrafos.

---

## Módulos

| Módulo | Carpeta | Estado (baseline 1.0.0 → dev FTPQ) |
|--------|---------|--------------------------------------|
| **SFTP** | [sftp/](./sftp/README.md) | Implementado · spec S01–S19 · job CLI `run_sftp_job.sh` |
| **Pandas** | [pandas/](./pandas/README.md) | Compare + analyzer en código · spec en curso |
| **UI** | [ui/](./ui/README.md) | PySide6 prototipo funcional · ADR toolkit diferido |
| **Plataformas** | [plataformas/README.md](./plataformas/README.md) | Mac nativo · Windows WSL2 · Python 3.12+ |
| **Línea dev** | [linea-desarrollo.md](./linea-desarrollo.md) | FTPQ vs `SFTP TOOL` congelado |
| **EMR QA** | [emr-qa/](./emr-qa/README.md) | Validador tabular local · [ADR-0002](./emr-qa/adr/0002-validador-tabular-compartible.md) · [ADR-0003 auditoría](./emr-qa/adr/0003-listo-auditoria-iso-privacidad.md) |

Congelado estable: [`../release/STABLE-1.0.0.md`](../release/STABLE-1.0.0.md)

Instalación paso a paso + ticket IT: [`../instalacion/README.md`](../instalacion/README.md)

## Skills por rol

Skills afinados en [`../skills/`](../skills/README.md).

| Rol | Skill |
|-----|-------|
| **Contexto** | `context-maintainer` — auditar/actualizar docs, skills, índices |
| Dev SFTP | `sftp-dev` |
| QA SFTP | `sftp-qa` |
| Peer review SFTP | `sftp-peer-review` |
| QA UI prototipo | `ui-qa` — checklist + `test_ui_smoke.py` |

Contexto base SFTP: [`../skills/sftp/reference.md`](../skills/sftp/reference.md)

---

## Plantilla por módulo

Cada carpeta sigue la misma forma:

```text
<modulo>/
  README.md           # índice del módulo
  funcionalidades.md  # catálogo con IDs (Sxx, Pxx, Uxx)
  restricciones.md    # límites y reglas duras
  fuera-de-alcance.md # explícitamente excluido
  criterios-exito.md  # checklist para cerrar el módulo
```

Archivos extra solo si el módulo los necesita (ej. SFTP: `contrato.md`, `errores.md`).

---

## Material archivado

Borrador previo por pasos numerados: [`../draft/`](../draft/).
