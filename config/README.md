# Configuración local EMR QA

## Llave de cifrado de minibase

`template_encryption.key` (generado desde **Ver → Llave**) contiene la llave AES-256 usada para cifrar la minibase de templates v2.0.

- **No commitear** este archivo (está en `.gitignore`).
- Haga backup manual si usa templates cifrados.
- Uso individual local; quien tenga repo + llave puede descifrar los JSON.
