# SFTP — Errores técnicos

Lo que el módulo SFTP detecta y expone. **Cómo mostrarlo** → [`../ui/errores-presentacion.md`](../ui/errores-presentacion.md) (cuando exista).

---

## Tabla de errores

| Código / síntoma | Causa probable | Datos para UI |
|------------------|----------------|---------------|
| `Permission denied (publickey)` | User ≠ llave en Transfer | Sugerir revisar S03, user |
| `Private key not found` | Path inválido | Sugerir S04, S11 |
| `Error reading SSH protocol banner` | VPN off / whitelist | Sugerir VPN, retry 30s |
| `Timeout` | Red, firewall | host, timeout R4 |
| `Authentication failed` | Llave no registrada | user, fingerprint |
| `Path not found` | Ruta remota incorrecta | path intentado |
| `PreviewNotSupported` | Binario o tipo no texto/CSV | mime/ext; usar S09 |
| `PreviewTooLarge` | Supera R12 | bytes, límite perfil |

---

## Reglas

- Errores como tipos/excepciones en `core/`, no strings sueltos en UI
- No incluir secretos en mensajes de error
- L-02: auth OK con llave “cruzada” → problema servidor, no local
