# FTPQ — línea de desarrollo

**Origen:** copia de `SFTP TOOL` congelado en **1.0.0 estable** (2026-07-17).

| Carpeta | Rol |
|---------|-----|
| `SFTP TOOL/` | **No tocar** — referencia estable |
| `FTPQ/` | Desarrollo activo |

Spec oficial: [`documentacion/linea-desarrollo.md`](documentacion/linea-desarrollo.md)

## Primer uso

```bash
cd "/Users/daniel.gallinate/repositorios/FTPQ"
./scripts/setup.sh
./scripts/run_ui.sh
```

Abrir **solo esta carpeta** en Cursor (cerrar `SFTP TOOL`).

## Versión

Antes del primer commit de dev, actualizar `ui/version.py` (ej. `1.1.0-dev`).

## Limpieza pendiente (opcional)

Esta copia trae artefactos que no hacen falta en dev:

- `downloads/` — datos locales de prueba
- `pde-sftp-validator-*.zip` — referencia validator
- `build-kit/` — resto pre-1.0.0
- `download.jpeg` — archivo suelto en raíz

Eliminar cuando ordenes el repo.
