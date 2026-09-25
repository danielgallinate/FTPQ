# SFTP — Contexto PDE

Layout remoto y campos de perfil. Solo datos de conexión SFTP.

---

## Árbol remoto típico

```text
sftp://<host>/
  └── config/
        └── <profile_name>/
              ├── scheduled/
              └── requested/
```

---

## Campos perfil (sección `sftp`)

| Campo JSON | Equivalente validator | Nota |
|------------|----------------------|------|
| `profile_id` | `CONFIG_NAME` | Suele = user SFTP = carpeta bajo `config/` |
| `sftp.host` | `SFTP_HOST` | Endpoint Transfer Family |
| `sftp.port` | (22 implícito) | Default 22 |
| `sftp.user` | `SFTP_USER` | Nonprod: igual a `profile_id` |
| `sftp.private_key_path` | `SFTP_KEY_PATH` | Llave privada local |
| `sftp.ssh_keys_dir` | — | Default `~/.ssh` |
| `sftp.default_remote_path` | `DEFAULT_FOLDER` | ej. `config/<id>/scheduled` |
| `sftp.download_dir` | `DOWNLOAD_DIR` | Default local `./downloads` |

Schema: [schema-perfil.draft.json](./schema-perfil.draft.json)

---

## Entorno

- VPN corporativa
- IP en whitelist AWS Transfer Family
- Sin VPN: usar mocks (`PDE_DESKTOP_MOCK=1`), no SFTP real

---

## Archivos remotos (origen PDE)

Los CSV y demás objetos en SFTP **los produce la aplicación PDE** upstream. PDE Desktop **solo lee, lista, descarga y ayuda a encontrar** — no genera extracts ni modifica el remoto.

| Aspecto | Convención acordada |
|---------|---------------------|
| Origen | Pipeline / app PDE → SFTP (Transfer Family) |
| Rol Desktop | Lectura y asistencia al operador |
| Nombres de archivo | Tipo de documento + metadatos operacionales (fecha, tipo extract, etc.) |
| PHI en filename | **No** — convención PDE; **aceptado por compliance** |
| Contenido | Puede ser clínico; Desktop **no lo abre** en flujos metadata/asistente v1 |

Convención de nombres y alcance del asistente → [`../ui/asistente-metadata.md`](../ui/asistente-metadata.md).
