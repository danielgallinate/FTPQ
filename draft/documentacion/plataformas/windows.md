# Windows — PDE Desktop (nativo)

**Prioridad PDE Desktop:** PowerShell nativo. **No** requiere WSL.

> El validator anterior recomendaba WSL ([legacy/WINDOWS.md](../legacy/WINDOWS.md)).  
> Este proyecto invierte esa prioridad para QA WorkSpace.

---

## Requisitos

| Requisito | Detalle |
|-----------|---------|
| Windows | 10/11 |
| Python | 3.11+ desde [python.org](https://www.python.org/downloads/) — marcar **Add to PATH** |
| PowerShell | Windows Terminal recomendado |
| VPN | Corporativa (Windows) |
| Llaves | `C:\Users\<YOU>\.ssh\` |

---

## Instalación rápida

```powershell
cd C:\path\to\pde-desktop
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # si scripts bloqueados
.\setup.ps1
.\setup.ps1 -Dev
```

---

## Ejecución

```powershell
.\run.ps1

# Mock sin VPN
$env:PDE_DESKTOP_MOCK = "1"
.\run.ps1

# Tests
.\setup.ps1 -Dev
.\.venv\Scripts\activate
pytest -q
```

---

## Llaves SSH en Windows

```text
C:\Users\YOUR_USER\.ssh\my_key_rsa
```

Perfil JSON (ambas formas válidas):

```json
"private_key_path": "C:\\Users\\YOUR_USER\\.ssh\\my_key_rsa"
```

o:

```json
"private_key_path": "~/.ssh/my_key_rsa"
```

No existe `chmod 600`: restringir permisos en Propiedades → Seguridad (solo tu usuario).

---

## Paridad con macOS

| macOS | Windows |
|-------|---------|
| `./setup.sh` | `.\setup.ps1` |
| `./setup.sh --dev` | `.\setup.ps1 -Dev` |
| `./run.sh` | `.\run.ps1` |
| `PDE_DESKTOP_MOCK=1 ./run.sh` | `$env:PDE_DESKTOP_MOCK=1; .\run.ps1` |

**Regla:** todo script nuevo en `scripts/*.sh` → equivalente `scripts/*.ps1`.

---

## Reinicio de aplicación

Al guardar perfil o cambiar llave, la UI debe reiniciar el proceso con **`subprocess`**, no `os.execv` solo (comportamiento distinto en Windows).

---

## Build portable

```powershell
.\scripts\build.ps1
# Salida: dist\pde-desktop\
```

Antivirus puede alertar sobre PyInstaller — documentar hash del zip para QA.

---

## WSL (solo referencia legacy)

Si necesitas el **validator TUI** anterior, usa WSL según [legacy/WINDOWS.md](../legacy/WINDOWS.md).  
No es requisito para PDE Desktop.

---

## Troubleshooting

| Síntoma | Acción |
|---------|--------|
| Scripts disabled | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `py` no encontrado | Reinstalar Python con PATH o usar `python` |
| SFTP timeout | VPN Windows activa |
| Rutas con `\` | Usar `pathlib.Path` en código; JSON con `\\` o `/` |

**Ver también:** [macOS](./macos.md)
