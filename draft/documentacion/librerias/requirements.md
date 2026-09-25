# Librerías y dependencias

Stack Python acordado para PDE Desktop.

---

## requirements.txt (producción mínima)

```text
paramiko>=3.4.0
pandas>=2.0.0
python-dotenv>=1.0.0    # opcional; overrides dev
flet>=0.24.0            # si UI = Flet (ajustar si PySide6)
```

### Si UI = PySide6 (alternativa)

```text
PySide6>=6.6.0
# quitar flet
```

---

## requirements-dev.txt

```text
-r requirements.txt
pytest>=8.0.0
ruff>=0.4.0
mypy>=1.10.0
jsonschema>=4.0.0       # validar perfiles JSON (Fase 1)
pre-commit>=3.0.0       # opcional
pyinstaller>=6.0.0      # empaquetado
```

---

## Dependencias explícitamente excluidas (fase 0–2)

```text
# NO instalar en este proyecto hasta fase futura:
# psycopg2 / psycopg2-binary
# snowflake-connector-python
# textual
```

Enforcement: rule `.cursor/rules/scope-no-db.mdc` + revisión en PR.

---

## Librerías opcionales (fase posterior)

| Paquete | Cuándo |
|---------|--------|
| `cryptography` | Cifrar perfiles con secretos en tránsito |
| `platformdirs` | Rutas config usuario Win/Mac estándar |
| `polars` | Si pandas no escala en lote F16 |

---

## Versiones Python

| Entorno | Mínimo |
|---------|--------|
| Desarrollo | 3.11 |
| CI | 3.11, 3.12 (matriz opcional) |
| Empaquetado | Misma versión usada en build |

---

## Mapa librería → funcionalidad

| Paquete | Fxx |
|---------|-----|
| paramiko | F01, F05–F10 |
| pandas | F11–F16 |
| flet / PySide6 | F06–F09, UI perfiles F17–F19 |
| jsonschema | Validación perfiles |
| pyinstaller | F20 |

---

## Instalación por plataforma

```bash
# macOS / Linux
./setup.sh
```

```powershell
# Windows
.\setup.ps1
```

Ambos crean `.venv` local (no commitear).
