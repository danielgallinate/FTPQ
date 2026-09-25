# macOS — PDE Desktop

Guía de desarrollo y QA en **macOS** (también aplica a Linux con los mismos `.sh`).

---

## Requisitos

| Requisito | Detalle |
|-----------|---------|
| macOS | 12+ recomendado |
| Python | 3.11+ (`python3 --version`) |
| VPN | Corporativa para SFTP real PDE |
| Llaves SSH | `~/.ssh/`, permisos `chmod 600` |

---

## Instalación rápida (cuando exista el repo)

```bash
git clone <repo-pde-desktop>
cd pde-desktop
chmod +x setup.sh run.sh scripts/*.sh
./setup.sh
./setup.sh --dev    # opcional: pytest, ruff
```

---

## Ejecución

```bash
# Desarrollo (venv + módulo UI)
./run.sh

# Modo mock (sin VPN)
PDE_DESKTOP_MOCK=1 ./run.sh

# Tests
./setup.sh --dev && pytest -q
```

---

## Llaves SSH

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cp /path/to/delivered_key ~/.ssh/pde_example_rsa
chmod 600 ~/.ssh/pde_example_rsa
```

En perfil JSON:

```json
"private_key_path": "~/.ssh/pde_example_rsa",
"ssh_keys_dir": "~/.ssh"
```

---

## Carpetas locales (auto-creadas)

| Carpeta | Uso |
|---------|-----|
| `downloads/` | Descargas permanentes |
| `tmp/analysis/` | CSV temp para pandas |
| `profiles/` | Perfiles guardados desde UI |

---

## Build portable (Fase 0+)

```bash
./scripts/build.sh
# Salida esperada: dist/pde-desktop/ (one-folder)
```

Empaquetado `.app`:

```bash
./scripts/build.sh --mac-app
```

---

## Diferencias vs validator TUI (legacy)

| Validator TUI | PDE Desktop Mac |
|---------------|-----------------|
| `./run_tui.sh` | `./run.sh` (GUI) |
| F4 edita `.env` | UI edita perfil JSON |
| `./run.sh --check` (BD+SFTP) | Test conexión solo SFTP |

Ver [legacy/validator-macos.md](../legacy/validator-macos.md) si necesitas el flujo anterior.

---

## Troubleshooting

| Síntoma | Acción |
|---------|--------|
| `Permission denied (publickey)` | Llave correcta en perfil; `chmod 600` |
| Timeout SFTP | VPN; IP en whitelist Transfer |
| App no abre tras build | Gatekeeper → clic derecho Abrir |
| pandas lento | Archivo grande; revisar límite en perfil |

**Ver también:** [Windows](./windows.md) · [Infraestructura](../paso-03-infraestructura/README.md)
