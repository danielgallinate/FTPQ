# Paso 3 — Infraestructura

Arquitectura, stack, proceso, empaquetado y layout del repo.

---

## Arquitectura de capas

```text
┌─────────────────────────────────────┐
│  ui/          Flet o PySide6        │  ← hilo principal
├─────────────────────────────────────┤
│  adapters/    paramiko, pandas      │  ← workers / threads
├─────────────────────────────────────┤
│  core/        contratos + dominio   │  ← SIN import de UI
└─────────────────────────────────────┘
```

**Regla dura:** `core/` no importa `flet`, `PySide6`, ni `paramiko` directamente en interfaces públicas; solo define protocolos/contratos.

---

## Proceso y memoria

| Aspecto | Decisión |
|---------|----------|
| Procesos | Un proceso principal (app desktop) |
| Hilos | UI main; SFTP y pandas en worker threads |
| Sesión SFTP | Una activa; cerrar al cambiar perfil o llave |
| pandas | Import lazy al abrir pestaña Análisis |

### RAM estimada

| Modo | RAM aprox. |
|------|------------|
| Solo SFTP | 130–200 MB |
| SFTP + pandas | 180–350 MB (según CSV) |
| Ejecutable empaquetado | 120–200 MB (one-folder) |

---

## Stack mínimo

Ver detalle en [librerias/requirements.md](../librerias/requirements.md).

| Dimensión | Elección actual | Alternativa |
|-----------|-----------------|-------------|
| Runtime | Python 3.11+ | — |
| SFTP | paramiko ≥3.4 | — |
| Análisis | pandas ≥2.0 | polars, pyarrow |
| UI | **Flet** (recomendado prototipo) | PySide6 |
| Empaquetado | **PyInstaller** (recomendado) | flet build |
| Config | Perfiles JSON | .env + JSON (híbrido) |
| Tests | pytest | — |

**Prohibido en fase 0–2:** `psycopg2`, `snowflake-connector-python`, `textual`.

---

## Estructura de directorios

```text
pde-desktop/
├── .cursor/rules/
│   ├── cross-platform.mdc
│   ├── architecture.mdc
│   └── scope-no-db.mdc
├── core/
│   ├── sftp_browser.py      # ISftpBrowser
│   ├── key_store.py         # IKeyStore
│   ├── profile_store.py     # IProfileStore
│   └── file_analyzer.py     # IFileAnalyzer
├── adapters/
│   ├── paramiko_sftp.py
│   └── pandas_analyzer.py
├── ui/
│   └── flet_app/            # o pyside_app/
├── mocks/
│   ├── mock_sftp_browser.py
│   └── fixtures/
├── tests/
├── profiles/                # perfiles ejemplo (no secretos)
├── downloads/               # gitignore
├── tmp/                     # gitignore
├── setup.sh
├── run.sh
├── setup.ps1
├── run.ps1
├── requirements.txt
└── requirements-dev.txt
```

---

## Scripts de plataforma (paridad obligatoria)

| Acción | macOS / Linux | Windows |
|--------|---------------|---------|
| Setup venv + deps | `./setup.sh` | `.\setup.ps1` |
| Dev + pytest | `./setup.sh --dev` | `.\setup.ps1 -Dev` |
| Ejecutar app dev | `./run.sh` | `.\run.ps1` |
| Build portable | `./scripts/build.sh` | `.\scripts\build.ps1` |

Cualquier script nuevo en `.sh` debe tener equivalente `.ps1` (regla Cursor).

---

## Empaquetado

### Objetivo QA
Entregar zip con carpeta ejecutable (one-folder PyInstaller) o `.app` / `.exe` según plataforma.

### Contenido del paquete
- Binario + dependencias embebidas  
- Perfiles de ejemplo **sin** llaves privadas  
- README corto de arranque  

### Excluir del zip
- `.venv`, `.env`, llaves SSH, reports locales  

---

## CI / calidad (recomendado)

| Herramienta | Uso |
|-------------|-----|
| ruff | Lint |
| mypy | Tipos en `core/` |
| pytest | Unit + integración con mocks |
| pre-commit | Hooks opcionales |

---

## Plataformas

- [macOS](../plataformas/macos.md) — `./setup.sh`, `~/.ssh`  
- [Windows](../plataformas/windows.md) — `.\setup.ps1`, **sin WSL requerido**  

> **Nota:** La guía `WINDOWS.md` del validator anterior describe WSL como path A.  
> **PDE Desktop invierte la prioridad:** Windows nativo primero; WSL solo referencia legacy.

**Anterior:** [Paso 2](../paso-02-funcionalidades/README.md) · **Siguiente:** [Paso 4 — Mocks](../paso-04-mocks/README.md)
