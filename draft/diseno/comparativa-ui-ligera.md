# Comparativa UI — ligera + visual (investigación 2026-07)

> Objetivo: **runtime ligero**, stack **simple**, **sin recortar** wallpaper + outline + paletas futuras.

---

## Resumen ejecutivo

| Opción | Peso app* | Visual (wallpaper+outline) | Docs | Mantenimiento | Veredicto |
|--------|-----------|----------------------------|------|---------------|-----------|
| **[Slint](https://slint.dev/)** | **~35–55 MB** | Excelente nativo | Muy buena | Alto (23k⭐) | **Recomendada** |
| PySide6 | 80–120 MB | Excelente (QSS) | Muy buena | Alto (Qt) | Plan B estable |
| Flet | 30–80 MB+ | Buena | Media | Medio | Descartada (peso/arranque) |
| CustomTkinter | 15–25 MB | Pobre (sin capas) | Media | Medio | Descartada (visual) |
| Dear PyGui | 15–25 MB | Media (texturas) | Media | Medio | Descartada (UX tool) |
| Bootstack / Plushie | ? | Prometedor | Alpha | Bajo | Muy inmaduro |
| Tauri + web | 250 MB+ | Excelente CSS | Buena | Alto | Pesado; 2 stacks |

\*Estimado PyInstaller one-folder con Python 3.11 + paramiko + pandas + UI. Slint incluye wheel ~7–13 MB.

---

## 1. Slint — recomendación principal

**Qué es:** toolkit declarativo nativo (Rust). UI en archivos `.slint`; lógica SFTP en Python.

### Por qué encaja con tu diseño

| Requisito | Slint |
|-----------|-------|
| Wallpaper modificable | `Image { source: @image-url(...); image-fit: cover; }` en capa 0 |
| Scrim | `Rectangle { opacity: 48%; background: #000; }` |
| Solo bordes + texto | `Rectangle { background: transparent; border-width: 2px; border-color: ... }` |
| Mono B/N → paletas | **Global palette** + cambio runtime de colores |
| Contraste | `opacity` por capa; paleta clara/oscura según luminancia (Python) |
| Tabla explorador SFTP | `StandardTableView` o `ListView` custom outline |
| Ligero | Binario Rust ~6 MB hello-world; sin arrastrar Qt completo |

Documentación: [docs.slint.dev](https://docs.slint.dev) — elementos Rectangle, Image, StandardTableView, theming.

### Arquitectura propuesta

```text
ui/
  slint/
    app-window.slint      # capas wallpaper + scrim + chrome
    components/
      outline-panel.slint
      outline-table.slint
      connection-bar.slint
  theme/
    contrast.py             # luminancia wallpaper → palette
    palettes/
      mono-dark.slint
      mono-light.slint
  app.py                    # slint.load_file; callbacks a core/
core/                       # ISftpBrowser (sin cambios)
```

Python beta: [Slint Python docs](https://docs.slint.dev/latest/docs/python/slint/) — API estable “mostly”; pin versión exacta.

### Riesgos

| Riesgo | Mitigación |
|--------|------------|
| Python en beta | Pin `slint==1.x.x`; wrapper fino; tests UI headless |
| Dos lenguajes (.slint + py) | UI solo en `.slint`; SFTP 100% Python |
| Skia renderer infla binario | Usar renderer **software/femtovg** default, no Skia (~23 MB extra) |

### Tamaño

- Slint hello-world release: ~3–6 MB (Rust)
- Wheel Python slint: ~7–13 MB ([PyPI](https://pypi.org/project/slint/))
- App PDE Desktop estimada: **35–55 MB** (vs PySide6 80–120 MB con mismo pandas/paramiko)

---

## 2. PySide6 — plan B (máxima estabilidad)

Elegir si **beta Slint es inaceptable** para QA corporativo.

| Pros | Contras |
|------|---------|
| Python puro en UI | +40–70 MB vs Slint |
| QSS transparent+border maduro | Arranque ~2 s |
| QFileDialog, QTableView probados | LGPL (OK comercial) |

Optimización: PyInstaller `--onedir`, excluir QtWebEngine, Qt3D, etc.

Referencia: [PySide6 vs Electron ~118 MB](https://dev.to/kerfiq/pyside6-vs-electron-why-i-shipped-a-118-mb-windows-desktop-tool-not-a-250-mb-cross-platform-one-2gfl)

---

## 3. Descartadas (y por qué)

### Flet
- Empaquetado **52–80 MB** solo hello-world en versiones recientes ([issue #3048](https://github.com/flet-dev/flet/issues/3048))
- Arranque lento; motor Flutter completo
- No cumple “ligera” aunque visualmente moderna

### CustomTkinter
- **15–25 MB** — la más ligera ([Whittl docs](https://lyndeneftoda.com/docs/features/choosing-a-target/))
- Tk no soporta bien **wallpaper + paneles transparentes + bordes** pixel-perfect
- Visual limitado → no cumple “no ahorramos en lo visual”

### Dear PyGui
- ~15–25 MB, GPU-accelerated
- Estética “tool/debug”, no app producto
- Bugs resize/memoria Windows ([#2477](https://github.com/hoffstadt/DearPyGui/issues/2477))
- Wallpaper posible vía textura, no modelo de capas limpio

### Bootstack / Plushie / Zolt
- Pre-1.0, comunidad minúscula, API inestable
- No para handoff PDE con agentes y QA

### Tauri / Electron
- Visual top; **no ligero** (Electron ~243 MB)
- Sidecar Python para SFTP = complejidad extra

---

## 4. Decisión recomendada

```text
┌─────────────────────────────────────────┐
│  Slint (.slint UI + Python core)        │
│  Renderer: software/femtovg (no Skia)   │
│  Theme: Global palette mono → color     │
└─────────────────────────────────────────┘
         ↓ si beta bloquea QA
┌─────────────────────────────────────────┐
│  PySide6 + ThemeEngine QSS (plan B)     │
└─────────────────────────────────────────┘
```

---

## 5. PoC mínima (validar antes de commit)

1. `app-window.slint`: Image wallpaper + Rectangle scrim + outline panel + StandardTableView 3 columnas
2. `app.py`: cargar listing mock JSON → modelo tabla
3. Cambiar wallpaper en runtime → `contrast.py` recalcula palette
4. PyInstaller one-folder → medir MB Mac + Win
5. Criterio: **< 60 MB**, contraste WCAG, tabla fluida 500 filas

---

## 6. Impacto en repo

| Antes (draft PySide6) | Ahora (Slint) |
|-----------------------|---------------|
| `ui/theme/qt_engine.py` | `ui/theme/slint_palette.py` |
| QSS strings | `.slint` + Global palette |
| `PySide6` en requirements | `slint` en requirements |

`core/`, `adapters/`, skills SFTP: **sin cambios**.

---

## 7. ADR pendiente

**UI-002:** Adoptar Slint como toolkit UI con Python bindings beta.  
Fallback documentado: PySide6.

Al aprobar → mover a `documentacion/ui/adr/0002-slint-toolkit.md`
