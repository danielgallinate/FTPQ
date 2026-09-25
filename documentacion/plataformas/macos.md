# macOS — PDE Desktop 1.0.0

Desarrollo y uso en **macOS nativo** (sin WSL).

---

## Requisitos

| Requisito | Detalle |
|-----------|---------|
| macOS | 12+ recomendado |
| Python | **3.12+** (`python3 --version`) |
| VPN | Corporativa para SFTP real PDE |
| Llaves SSH | `~/.ssh/`, permisos `chmod 600` |

---

## Instalación

```bash
cd "/path/to/SFTP TOOL"
chmod +x scripts/setup.sh scripts/run_ui.sh
./scripts/setup.sh
```

Crea `.venv/` e instala `requirements.txt`.

---

## Ejecutar

```bash
./scripts/run_ui.sh
```

Mock sin VPN:

```bash
PDE_DESKTOP_MOCK=1 ./scripts/run_ui.sh
```

Tests:

```bash
.venv/bin/pytest -q
```

---

## Perfil y datos

- Perfil: `profiles/default.json` (gitignored si personalizado)
- App data: `~/.pde-desktop/`
- Descargas: ruta en perfil (`download_dir`)

---

## Llaves SSH

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/tu_llave_rsa
```

En perfil JSON:

```json
"private_key_path": "~/.ssh/tu_llave_rsa",
"ssh_keys_dir": "~/.ssh"
```

---

## Versión

Help → Versión en la app, o:

```bash
.venv/bin/python -c "from ui.version import display_version; print(display_version())"
```

Debe mostrar `1.0.0`.

---

**Ver también:** [Windows WSL2](./windows-wsl2.md) · [Guía instalación](../../instalacion/macos.md) · [Alcance individual](../alcance-uso-individual.md)
