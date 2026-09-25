# SFTP — Funcionalidades

Catálogo exclusivo del módulo SFTP. IDs **Sxx**.

---

## Conexión y configuración

| ID | Funcionalidad | Criterio de aceptación |
|----|---------------|------------------------|
| **S01** | Conector SFTP por llave privada | Handshake SSH + canal SFTP (paramiko) |
| **S02** | Configurar host, puerto (22), usuario | Persistido en perfil JSON |
| **S03** | Selector de llave privada | Al elegir → cerrar sesión y **reconectar** |
| **S04** | Carpeta local de búsqueda de llaves | Default `~/.ssh`; campo `ssh_keys_dir` |
| **S05** | Test de conexión | Handshake real; OK/error explícito |
| **S17** | Perfil de conexión | Guardar/cargar JSON; múltiples perfiles |

---

## Exploración remota

| ID | Funcionalidad | Criterio de aceptación |
|----|---------------|------------------------|
| **S06** | Listar directorio remoto | Nombre, tipo dir/file, tamaño, fecha si hay |
| **S07** | Navegar | Entrar carpeta; subir (`..`); refrescar |
| **S08** | Previsualizar archivo remoto | Texto y CSV; límites en [restricciones.md](./restricciones.md) |
| **S09** | Descargar archivo | Stream remoto → path local (UI o job S18) |
| **S10** | Ruta remota actual | Path POSIX completo disponible para UI (breadcrumb) |
| **S18** | Job headless | JSON `kind: sftp_fetch` + `./scripts/run_sftp_job.sh`; `download: false` valida existencia solo con listado; glob o regex; token `{date}` y `--as-of YYYYMMDD`; overrides de conexión/destino; exit 0/1/2; salida JSON |
| **S19** | Descarga en secuencia | `expect[]` con glob `fnmatch`; `recursive: true` preserva carpetas, crea `{sftp_user}` y manifiesto; fail-fast o `--keep-going` |

---

## Llaves SSH

| ID | Funcionalidad | Criterio de aceptación |
|----|---------------|------------------------|
| **S11** | Descubrir llaves en carpeta | Candidatos privados; excluir `.pub` |
| **S12** | Fingerprint de llave | SHA256 de la privada seleccionada |
| **S13** | Validar llave antes de conectar | Existe, parseable, permisos (Mac/Linux) |
| **S14** | Generar par de llaves | RSA y/o ECDSA; path destino; devolver `.pub` + fingerprint |

---

## Dependencias entre funcionalidades

```text
S17 (perfil) → S02, S03, S04
S03, S02 → S05 (test)
S05 OK → S06 (listar)
S06 → S07, S08, S09
S04 → S11 → S03
S14 → S11 (nueva llave disponible)
S17 → S18 (perfil en el job, no secretos)
S18 → S06, S09, S19
```

La **UI** decide cuándo invocar cada Sxx en PDE Desktop; el job CLI invoca S18/S19 sin pantalla → [`../ui/`](../ui/) · [`./adr/0001-sftp-job-headless.md`](./adr/0001-sftp-job-headless.md).
