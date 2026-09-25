# SFTP — Herencia del PDE Validator

Qué reutilizamos del TUI y qué no entra en este módulo.

---

## Reutilizar

| Validator | SFTP Desktop |
|-----------|--------------|
| `./scripts/test-sftp-login.sh` | **S05** |
| Parte SFTP de `./run.sh --check` | **S05** (sin BD) |
| Browser listado | **S06–S07** |
| F3 descarga | **S09** |
| F4 `SFTP_USER`, `SFTP_KEY_PATH` | **S02, S03, S17** |
| `DEFAULT_FOLDER` | `default_remote_path` |
| Llaves `~/.ssh` | **S04, S11–S14** |

---

## No portar a SFTP

- Lookup `CONFIG_NAME` / `CONFIG_ID` en Postgres
- F7 scan SFTP ↔ BD
- `--check` de base de datos
- `.env` secciones 2–3 como única fuente de config

---

## Gap corregido (L-01)

Validator/sftp-lite: tecla **K** listaba/generaba llaves pero **no aplicaba** llave a la sesión SFTP.  
Desktop **S03** debe reconectar al cambiar llave.

---

## Lección L-02

Auth OK con llave de otro config → problema puede ser **Transfer**, no la llave local.  
**S05** siempre prueba contra el servidor real.

Referencias: `draft/documentacion/legacy/QA_HANDOFF.md`, `CONFIG_SCREEN.md`
