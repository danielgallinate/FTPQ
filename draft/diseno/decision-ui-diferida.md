# ¿Decidir UI ahora o avanzar antes?

> **Promovido** a [`../../documentacion/ui/decision-ui-diferida.md`](../../documentacion/ui/decision-ui-diferida.md) — 2026-07-14.  
> Este archivo queda como borrador histórico; editar la versión oficial.

> Análisis de reversibilidad y orden de trabajo — 2026-07-14

---

## Respuesta corta

**Sí, podéis avanzar mucho antes de elegir Slint / PySide6 / NiceGUI.**  
**Sí, es posible cambiar de UI después**, si respetáis una regla: **toda la lógica vive en `core/` + `adapters/`; `ui/` es una capa fina.**

La decisión UI **no bloquea** SFTP ni pandas en backend.  
Lo que **sí** conviene decidir pronto (no toolkit, sino **contrato visual**): wallpaper + scrim + outline mono — eso ya está en draft y es portable entre toolkits.

---

## Qué se puede cambiar después (fácil → difícil)

| Capa | Cambiar UI después | Esfuerzo |
|------|-------------------|----------|
| `core/` contratos SFTP/pandas | **No tocar** — independiente del toolkit | — |
| `adapters/paramiko`, `pandas` | **No tocar** | — |
| `mocks/`, `tests/` SFTP | **No tocar** | — |
| Perfiles JSON (`sftp`, reglas) | **No tocar** | — |
| `ui/theme/tokens/*.yaml` | Reutilizar valores; cambiar **motor** (QSS vs .slint vs CSS) | Bajo |
| Pantallas wireframes (U-01…) | Misma funcionalidad, otro renderer | Medio |
| Carpeta `ui/` completa | Reescribir presentación | **Alto pero acotado** |
| Empaquetado PyInstaller | Ajustar hiddenimports / deps | Medio |

```text
                    ┌─────────────┐
  NO se tira        │ core/       │  ISftpBrowser, IFileAnalyzer
  al cambiar UI ──► │ adapters/   │  paramiko, pandas
                    │ tests/      │
                    └──────┬──────┘
                           │ contratos estables
                    ┌──────▼──────┐
  SÍ se rehace      │ ui/         │  Slint ↔ Qt ↔ NiceGUI
  (solo esta)       └─────────────┘
```

---

## Qué os “ata” a un toolkit (evitar al inicio)

| Anti-patrón | Consecuencia al cambiar |
|-------------|-------------------------|
| SFTP logic dentro de widgets | Reescribir todo |
| Tipos paramiko en `core/` | Acoplamiento |
| Tokens hardcodeados en UI sin YAML | Rediseño manual |
| Sin capa `ThemeEngine` protocol | Cada pantalla acoplada al toolkit |
| Mezclar `.slint` y QSS en `core/` | Caos |

**Regla:** `ui/` importa `core`; `core/` nunca importa toolkit.

---

## Qué avanzar SIN decidir UI

### Fase A — Ahora (paralelo al draft visual)

| # | Entregable | Módulo |
|---|------------|--------|
| 1 | Cerrar spec SFTP (`documentacion/sftp/`) | SFTP |
| 2 | `core/sftp_*.py` contratos + errores tipados | SFTP |
| 3 | `MockSftpBrowser` + fixtures | SFTP |
| 4 | `ParamikoSftpBrowser` + tests sin VPN | SFTP |
| 5 | Schema perfil JSON `sftp` | SFTP |
| 6 | `setup.sh` / `setup.ps1`, `run` con **CLI mínima** o headless | infra |
| 7 | Wireframes en draft (pantallas U-01–U-06, **sin código**) | UI draft |
| 8 | Tokens mono YAML (ya en draft) | UI draft |

**CLI/headless:** `./run.sh --sftp-test`, `--list path` — valida S05–S09 sin GUI. Patrón del validator (`test-sftp-login.sh`).

### Fase B — Spec pandas (después SFTP core)

| # | Entregable |
|---|------------|
| 1 | `documentacion/pandas/` funcionalidades + restricciones |
| 2 | `IFileAnalyzer` + mock |
| 3 | Sin UI |

### Fase C — Recién aquí: decisión toolkit + PoC

| # | Entregable |
|---|------------|
| 1 | PoC 1 pantalla (explorador) en **1** toolkit |
| 2 | Medir peso, arranque, tabla 500 filas |
| 3 | ADR UI-002 |

---

## Comparativa: cambiar UI a mitad de proyecto

| De → A | Qué se reutiliza | Qué se pierde |
|--------|------------------|---------------|
| PySide6 → Slint | 100% core/adapters/tests; tokens; wireframes | QSS, widgets Qt |
| Slint → PySide6 | 100% core; `.slint` como referencia visual | archivos `.slint` |
| Cualquiera → NiceGUI | core; tokens → CSS variables | código nativo previo |
| CustomTkinter → otro | solo core | casi toda UI |

**Coste típico** si hiciste bien la separación: **2–4 semanas** re-skin pantallas, no rehacer SFTP.

**Coste** si mezclaste lógica en UI: **meses**.

---

## Decisión visual vs decisión toolkit

Podéis **congelar ya** (sin elegir librería):

- [x] Modelo 3 capas: wallpaper → scrim → outline  
- [x] Mono B/N primero, paletas después  
- [x] U-R1: UI no contiene lógica SFTP  
- [ ] Wireframes U-01 conexión, U-02 explorador  
- [ ] `ThemeEngine` como **Protocol** en `ui/theme/protocol.py` (sin implementación)

Eso hace que Slint, PySide6 y NiceGUI implementen el **mismo contrato**.

```python
# ui/theme/protocol.py — sin PySide6 ni slint
class ThemeEngine(Protocol):
    def apply(self, tokens: TokenSet, chrome_mode: ChromeMode) -> None: ...
    def on_wallpaper_changed(self, path: Path, luminance: float) -> None: ...
```

---

## Recomendación de orden

```text
Semana 1–2   SFTP core + mocks + CLI headless     ← SIN decisión UI
Semana 2     Wireframes + tokens (draft → doc ui)  ← decisión VISUAL, no toolkit
Semana 3     PoC 1 toolkit (2 días Slint, 2 días Qt si dudáis)
Semana 3+    ADR + implementación ui/ con ganador
```

**No hace falta** PoC de los 3 toolkits en paralelo salvo que QA bloquee beta Slint.

---

## Cuándo SÍ decidir UI antes de codear

- Necesitáis **demo visual al cliente** en < 1 semana → PoC UI primero (1 toolkit).  
- Política empresa prohíbe PyPI alpha → **PySide6 6.11.1** ya, sin PoC Slint.  
- Un solo desarrollador y context-switch cuesta caro → elegir uno y no mirar atrás.

---

## Veredicto

| Pregunta | Respuesta |
|----------|-----------|
| ¿Cambiar UI después? | **Sí**, si `core/` limpio + UI delgada |
| ¿Avanzar antes? | **Sí** — SFTP completo, mocks, CLI, wireframes, tokens |
| ¿Qué no postponer? | Contrato `ThemeEngine` + wireframes U-01/U-02 (diseño, no código) |

**Siguiente paso sugerido:** implementar `core/` SFTP + runner CLI, dejar `ui/` vacío con solo `protocol.py`.
