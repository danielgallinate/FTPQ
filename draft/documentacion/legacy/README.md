# Legacy — PDE SFTP Validator (TUI + BD)

Documentación del **proyecto anterior**. Referencia para reutilizar ideas; **no** es alcance de PDE Desktop fase 0–2.

| Archivo origen | Descripción |
|----------------|-------------|
| [QA_HANDOFF.md](./QA_HANDOFF.md) | Checklist QA del validator portable |
| [CONFIG_SCREEN.md](./CONFIG_SCREEN.md) | Manual pantalla F4 TUI |
| [WINDOWS.md](./WINDOWS.md) | WSL + Windows nativo (validator) |
| [PDE_DESKTOP_PROTOTYPE.md](./PDE_DESKTOP_PROTOTYPE.md) | Plan corto que derivó en handoff desktop |

## Qué reutilizar vs no portar

| Reutilizar | No portar (fase 0–2) |
|------------|-------------------|
| Lógica paramiko SFTP | Postgres / F7 SFTP↔DB |
| Patrones pandas archivo local | Textual TUI |
| Concepto perfiles entorno | `.env` sección BD |
| Lecciones VPN / Transfer | WSL como requisito |

## Migración mental QA

| Validator TUI | PDE Desktop |
|---------------|-------------|
| F4 → edit `.env` | UI → perfil JSON |
| `./run_tui.sh` | `./run.sh` / `.\run.ps1` |
| F7 global scan | Fuera de alcance |
| `--check` BD+SFTP | test_auth SFTP only |

Ver [paso-01-entender](../paso-01-entender/README.md) para la visión del producto nuevo.
