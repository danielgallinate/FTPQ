# Línea de desarrollo FTPQ

**Estado:** activa · **Baseline:** PDE Desktop **1.0.0 estable** (2026-07-17)

---

## Qué es FTPQ

Copia de trabajo para evolucionar PDE Desktop **sin tocar** el congelado de referencia.

| Carpeta | Rol |
|---------|-----|
| `SFTP TOOL/` (hermano) | **No editar** — referencia estable 1.0.0 |
| `FTPQ/` (este repo) | Desarrollo activo post-1.0.0 |

Guía rápida en raíz: [`../DEV-FORK.md`](../DEV-FORK.md)

---

## Primer uso en Cursor

1. Abrir **solo** la carpeta `FTPQ` (cerrar `SFTP TOOL` si está abierta).
2. `./scripts/setup.sh` → `./scripts/run_ui.sh`
3. Mock sin VPN: `PDE_DESKTOP_MOCK=1 ./scripts/run_ui.sh`

Plataformas: [`plataformas/README.md`](./plataformas/README.md)

---

## Baseline heredado (1.0.0)

Congelado documentado en [`../release/STABLE-1.0.0.md`](../release/STABLE-1.0.0.md):

- SFTP + file manager dual (Local A/B)
- Compare multiset (pandas)
- Visualización tabular y texto
- i18n ES/EN
- UI **PySide6** (prototipo funcional; ADR toolkit formal aún en [`ui/decision-ui-diferida.md`](./ui/decision-ui-diferida.md))
- Perfiles JSON locales (`profiles/`)

**27** archivos de test en `tests/`. Spec SFTP S01–S19 / R1–R27 en [`sftp/`](./sftp/README.md).

---

## Convenciones post-baseline

| Tema | Regla |
|------|-------|
| Versión | Tras el primer commit de dev → `ui/version.py` en canal dev (ej. `1.1.0-dev`) |
| Git | Inicializar repo en `FTPQ/`; no compartir bundles — ver [`alcance-uso-individual.md`](./alcance-uso-individual.md) |
| Contexto agentes | Entrada [`../AGENTS.md`](../AGENTS.md); mantenimiento `@context-maintainer` |
| Spec | Editar `documentacion/<modulo>/` antes de skills o código |

---

## Limpieza opcional (artefactos de la copia)

No bloquean desarrollo; eliminar cuando ordenes el repo:

- `downloads/` — datos locales de prueba (~380 MB)
- `pde-sftp-validator-*.zip` — referencia TUI (ver [`../reference/README.md`](../reference/README.md))
- `build-kit/` — resto pre-1.0.0
- `download.jpeg` — archivo suelto en raíz

---

## Prioridad sugerida (post-1.0.0)

1. Inicializar git + bump versión dev
2. Mantener tests verdes (`pytest -q`)
3. Evolucionar por módulo (SFTP / pandas / UI) con spec + skill de rol
4. No reintroducir instaladores archivados — [`../scripts/ARCHIVADO-INSTALADORES.md`](../scripts/ARCHIVADO-INSTALADORES.md)
