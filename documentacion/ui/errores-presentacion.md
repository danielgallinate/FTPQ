# UI — Presentación de errores SFTP

Mapeo **SftpError → mensaje usuario**. La app **no termina** (U-R10).

| Error core | Mensaje usuario (ejemplo) | Acción sugerida |
|------------|---------------------------|-----------------|
| `SftpConnectionError` (timeout) | Tiempo de conexión agotado (30 s) | Revisar VPN; reintentar |
| `SftpConnectionError` (banner) | No se pudo establecer canal SSH | VPN; whitelist IP |
| `SftpAuthError` | Autenticación rechazada | Usuario y llave en Configuración |
| `KeyNotFoundError` | Llave privada no encontrada | Ruta en Configuración / Llaves |
| `SftpPathError` | Ruta remota no existe | Revisar carpeta inicial |
| `PreviewNotSupported` | Vista previa no disponible | Descargar archivo |
| `PreviewTooLarge` | Archivo demasiado grande para preview | Descargar o aumentar límite en perfil |

**Reglas:**
- Sin secretos en UI (R25)
- Botón Cerrar / OK siempre disponible
- Tras error de conexión: sesión `disconnected` o `error`; menús siguen activos

Técnico: [`../sftp/errores.md`](../sftp/errores.md)
