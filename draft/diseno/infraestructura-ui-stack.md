# Infraestructura UI — stack para wallpaper + outline

> **Estado:** draft — recomendación para aprobación

Requisito clave: **imagen de fondo modificable** + **UI solo texto y bordes** con **contraste reactivo** + camino a **paletas**.

---

## 1. Criterios de evaluación

| Criterio | Peso |
|----------|------|
| Capas fondo / scrim / chrome | Alto |
| Bordes sólidos + fondos transparentes | Alto |
| Tablas SFTP (muchas filas) | Alto |
| Theme tokens (mono → color) | Alto |
| Empaquetado Win/Mac portable | Medio |
| Velocidad prototipo | Medio |

---

## 2. Opciones

### A — PySide6 (Qt6) — **Recomendada**

```text
ui/
  theme/engine.py      # genera QSS desde YAML tokens
  theme/contrast.py    # luminancia wallpaper → chrome mode
  layers/background.py # QLabel / QStackedWidget fondo
  widgets/outline/     # subclasses con QSS transparent
  app.py               # QApplication + ThemeEngine.apply()
```

| Pros | Contras |
|------|---------|
| QSS maduro: `border`, `background: transparent` | Más boilerplate que Flet |
| `QTableView` performante para explorador | Curva aprendizaje |
| `QPalette` + stylesheets dinámicos | PyInstaller ~80–120 MB |
| Wallpaper en widget raíz estable | |
| File picker nativo (S09) trivial | |

**Contraste:** regenerar QSS al cambiar wallpaper/mode. Scrim = `QWidget` hijo full-rect con `background-color: rgba(...)`.

---

### B — Flet (Flutter lite)

```text
ui/flet_app/
  page.bgcolor + Stack([Image, Container scrim, Column chrome])
```

| Pros | Contras |
|------|---------|
| Prototipo rápido | Transparencias/bordes menos predecibles |
| Python puro | Tablas grandes más lentas |
| `flet build` empaquetado | ThemeEngine custom más hacky |
| | Contraste dinámico limitado |

**Veredicto:** viable MVP **solo si** priorizas velocidad sobre tablas y QSS fino. No ideal para “solo líneas y letras” pixel-perfect.

---

### C — Tauri 2 + Web (HTML/CSS)

```text
src/styles/tokens.css
background-image + ::backdrop + CSS variables
mix-blend-mode en bordes (experimental)
```

| Pros | Contras |
|------|---------|
| **Mejor** modelo capas CSS | Dos stacks (Rust + sidecar Python SFTP) |
| `backdrop-filter`, variables nativas | Complejidad repo |
| Diseño mono → color trivial | IPC SFTP |

**Veredicto:** mejor diseño visual puro; peor alineación con handoff Python monolito.

---

## 3. Recomendación (actualizada tras investigación)

Ver análisis completo: [comparativa-ui-ligera.md](./comparativa-ui-ligera.md)

```text
┌─────────────────────────────────────────┐
│  Slint — UI .slint + Python core        │
│  Ligero (~35–55 MB) + visual nativo     │
│  wallpaper / border / opacity / palette │
└─────────────────────────────────────────┘
         ↓ fallback si beta Python bloquea
┌─────────────────────────────────────────┐
│  PySide6 + ThemeEngine QSS              │
└─────────────────────────────────────────┘
```

**Descartadas para este proyecto:** Flet (peso/arranque), CustomTkinter (sin capas visuales), Dear PyGui (UX tool), frameworks alpha (Bootstack/Plushie).

**Por qué Slint encaja tu diseño:**
- `Image` full-bleed = wallpaper modificable
- `Rectangle { background: transparent; border-width: 2px }` = outline mono
- `opacity` = scrim + contraste
- Global palette = mono B/N hoy, color mañana
- [StandardTableView](https://docs.slint.dev/latest/docs/slint/reference/std-widgets/views/standardtableview/) = explorador SFTP
- Docs: [docs.slint.dev](https://docs.slint.dev) · ~23k GitHub stars · releases activos

**Riesgo:** bindings Python en **beta** → pin versión + PoC antes de producción.

---

## 3b. Recomendación anterior (PySide6) — plan B

**Abstracción:** definir `ui/theme/` **sin** import PySide6 en interfaces:

```python
# ui/theme/protocol.py
class ThemeEngine(Protocol):
    def apply(self, chrome_mode: ChromeMode, tokens: TokenSet) -> None: ...
    def on_wallpaper_changed(self, path: Path, luminance: float) -> None: ...
```

Implementación `PySide6ThemeEngine` en `ui/theme/qt_engine.py`. Permite swap futuro sin tocar SFTP.

---

## 4. Arquitectura repo propuesta

```text
ui/
├── theme/
│   ├── protocol.py
│   ├── contrast.py          # luminancia, WCAG check
│   ├── loader.py            # YAML → TokenSet
│   ├── qt_engine.py         # aplica QSS
│   └── tokens/
│       ├── base.yaml
│       ├── mono-dark.yaml
│       └── mono-light.yaml
├── layers/
│   ├── wallpaper.py         # WallpaperProvider
│   └── scrim.py             # ScrimOverlay
├── widgets/
│   └── outline/
│       ├── panel.py
│       ├── button.py
│       ├── input.py
│       └── table.py           # explorador S06
├── screens/
│   ├── connection.py        # U-01
│   ├── explorer.py          # U-02
│   └── ...
├── assets/
│   └── wallpapers/
└── app.py
```

**Regla:** `ui/` importa `core/` (SFTP contratos); nunca paramiko directo.

---

## 5. ThemeEngine — flujo runtime

```text
1. App start → load tokens/mono-dark.yaml (default)
2. WallpaperProvider.load(path | default)
3. contrast.sample(wallpaper) → ChromeMode.dark | .light | user override
4. scrim.set_opacity(token + auto bump si WCAG fail)
5. qt_engine.build_qss(tokens, chrome_mode) → qApp.setStyleSheet
6. Signal wallpaper_changed → repeat 3–5
```

---

## 6. QSS patrón outline (ejemplo)

```css
OutlinePanel {
  background: transparent;
  border: 2px solid #FFFFFF;
}
OutlineButton {
  background: transparent;
  color: #FFFFFF;
  border: 2px solid #FFFFFF;
  padding: 8px 16px;
}
OutlineButton:hover {
  background: #FFFFFF;
  color: #000000;
}
QTableView {
  background: transparent;
  gridline-color: #FFFFFF;
  color: #FFFFFF;
  border: 2px solid #FFFFFF;
}
```

Valores `#FFFFFF` / `#000000` vienen de tokens, no hardcode en widgets.

---

## 7. Empaquetado

| Pieza | Notas |
|-------|-------|
| PyInstaller + PySide6 | Incluir `ui/assets/wallpapers/` |
| Win / Mac | Mismo QSS; test contraste en ambos |
| HiDPI | Qt `AA_EnableHighDpiScaling` |

---

## 8. Alternativa si rechazan PySide6

**Plan B:** Flet con Stack fijo + scrim obligatorio 50% + mono tokens limitados.  
Documentar deuda: migrar explorador a Qt si tablas >500 filas lag.

---

## 9. Decisión pendiente (ADR UI-001)

| Pregunta | Opciones |
|----------|----------|
| Toolkit | PySide6 (rec.) / Flet / Tauri |
| Scrim default | dark-chrome 48% |
| Auto contrast | fase 2 |

Al aprobar → copiar a `documentacion/ui/infraestructura.md` + ADR en `documentacion/ui/adr/`.

---

## 10. Relación con SFTP / pandas

| Capa | Responsabilidad |
|------|-----------------|
| SFTP `core/` | Datos list_dir, preview bytes |
| UI `outline/table` | Presenta RemoteEntry |
| Theme | Cómo se ven bordes/texto |
| pandas UI | Misma capa chrome; otra pantalla |

No poner lógica wallpaper en módulo SFTP.
