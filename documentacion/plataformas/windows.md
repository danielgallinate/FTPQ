# Windows — PDE Desktop 1.0.0 (WSL2)

En Windows **no** se soporta CMD/PowerShell nativo ni portable PyInstaller en 1.0.0.

Usá **WSL2** (Ubuntu u otra distro) con **Python 3.12+** y los mismos scripts `.sh` que en Mac.

---

## Requisitos

| Requisito | Detalle |
|-----------|---------|
| Windows | 10/11 con WSL2 habilitado |
| Distro Linux | Ubuntu 22.04+ recomendado |
| Python | **3.12+** dentro de WSL (`python3 --version`) |
| VPN | Conectar en **Windows** antes de usar SFTP desde WSL |
| Llaves SSH | `~/.ssh/` dentro de WSL (`chmod 600`) |

---

## Montar el repo en WSL

Ejemplo — repo en disco Windows:

```bash
cd "/mnt/c/Users/TU_USUARIO/repositorios/SFTP TOOL"
# o la ruta que uses en tu máquina
```

Evitá rutas con espacios si tu shell da problemas; si no, usa comillas como arriba.

---

## Instalación (dentro de WSL)

```bash
chmod +x scripts/setup.sh scripts/run_ui.sh
./scripts/setup.sh
```

---

## Ejecutar

```bash
./scripts/run_ui.sh
```

Mock:

```bash
PDE_DESKTOP_MOCK=1 ./scripts/run_ui.sh
```

Tests:

```bash
.venv/bin/pytest -q
```

---

## GUI en WSL

PySide6 necesita display server:

- **WSLg** (Windows 11): suele funcionar sin config extra al lanzar `./scripts/run_ui.sh`
- Si falla: comprobar actualización WSL (`wsl --update`) y drivers gráficos Windows

---

## VPN y SFTP

- Conectá la VPN corporativa en **Windows** (no solo dentro de WSL).
- Timeout SFTP → verificar VPN y perfil en `profiles/default.json`.

---

## Qué NO usar en 1.0.0

| Obsoleto | Motivo |
|----------|--------|
| `scripts\setup.cmd`, portable `.zip`, `python-embed\` | Eliminados — ver [`ARCHIVADO-INSTALADORES.md`](../../scripts/ARCHIVADO-INSTALADORES.md) |
| Build-kit copiado desde Mac | Ya no se genera en repo estable |

---

**Ver también:** [macOS nativo](./macos.md) · [Guía instalación WSL2](../../instalacion/windows-wsl2.md) · [Alcance individual](../alcance-uso-individual.md)
