# AGENTS.md — PDE Desktop

Instrucciones para agentes de código en este repositorio.

## Producto

App de escritorio **SFTP + pandas**, GUI, portable Mac/Windows. **Sin Postgres** en fase 0–2.

## Leer primero

1. `documentacion/README.md`
2. `.cursor/rules/scope-no-db.mdc`

## Arquitectura

- `core/` — sin UI, sin paramiko directo en interfaces
- `adapters/` — paramiko, pandas
- `ui/` — Flet o PySide6

## Reglas no negociables

- No añadir psycopg2, snowflake, textual
- Paridad `.sh` / `.ps1`
- `test_auth()` SFTP real fuera de mock mode
- Límites preview/pandas en `memory-limits.mdc`

## Skills del proyecto

| Skill | Uso |
|-------|-----|
| `pde-handoff` | Orientación inicial |
| `pde-sftp-feature` | F01–F10 |
| `pde-pandas-feature` | F11–F16 |
| `pde-cross-platform` | Scripts y build |
| `pde-mock-mode` | Desarrollo sin VPN |

## Mock mode

```bash
PDE_DESKTOP_MOCK=1 ./run.sh
```

## Documentación detallada

Ver `documentacion/agentes/README.md` para roles de agente sugeridos.
