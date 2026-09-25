# SFTP — Restricciones

Reglas duras del módulo SFTP. IDs **Rxx**.

---

## Red y sesión

| ID | Restricción |
|----|-------------|
| **R1** | Una sesión SFTP activa por instancia de app |
| **R2** | Cerrar sesión al cambiar perfil, usuario, host o llave |
| **R3** | Operaciones SFTP en worker thread (no bloquear caller UI) |
| **R4** | Timeout conexión default: **30 s** |
| **R5** | Entorno PDE real requiere VPN |
| **R6** | `test_auth` = handshake real; no flags “verified” externos |

---

## Rutas

| ID | Restricción |
|----|-------------|
| **R7** | `pathlib.Path` + `expanduser()`; no concatenar `/` o `\` |
| **R8** | Paths remotos: POSIX |
| **R9** | Paths locales Windows: `~/.ssh` y `C:\Users\...` |
| **R10** | Normalizar `default_remote_path` (sin trailing slash ambiguo) |

---

## Preview (S08)

| ID | Restricción |
|----|-------------|
| **R11** | Solo texto plano y CSV |
| **R12** | Default max **512 KB** o **500 líneas** (primero en ocurrir) |
| **R13** | Binarios: no preview; capa SFTP devuelve error/tipo no soportado |
| **R14** | No leer archivo completo remoto si supera límite |
| **R15** | Límites configurables en perfil (`preview_max_bytes`, `preview_max_lines`) |

---

## Descarga (S09)

| ID | Restricción |
|----|-------------|
| **R16** | SFTP recibe `local_path` ya resuelto (UI elige con picker) |
| **R17** | Descarga permanente ≠ temp de preview (`downloads/` vs `tmp/preview/`) |
| **R18** | Sobrescritura local: responsabilidad UI confirmar antes de llamar |
| **R19** | Propagar error IO (disco lleno, permiso) sin tragar excepción |

---

## Llaves (S03, S11–S14)

| ID | Restricción |
|----|-------------|
| **R20** | Conexión solo con llaves **privadas** |
| **R21** | Mac/Linux: advertir permisos ≠ 600 |
| **R22** | Windows: sin chmod; documentar en UI |
| **R23** | S14: no sobrescribir key existente sin confirmación (UI) |
| **R24** | Exponer fingerprint antes de persistir perfil |

---

## Seguridad

| ID | Restricción |
|----|-------------|
| **R25** | Llaves y perfiles con secretos: fuera de git |
| **R26** | No loguear contenido remoto ni passphrases |
| **R27** | Temp preview en `tmp/preview/`; limpiar al disconnect/cierre app |

---

## Corrección vs validator (L-01)

Cambiar llave (**S03**) **siempre** cierra sesión y exige reconexión. El TUI no hacía esto con tecla K.
