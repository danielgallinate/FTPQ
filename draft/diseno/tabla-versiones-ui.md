# Tabla comparativa UI — versiones y decisión PDE Desktop

> Fecha referencia: **2026-07-14**  
> Objetivo: **ligero + simple + visual alto** (wallpaper, outline B/N, paletas)  
> Contexto diseño: [`sistema-capas-wallpaper.md`](./sistema-capas-wallpaper.md)

---

## Leyenda puntuación (para tu caso)

| Símbolo | Significado |
|---------|-------------|
| ⭐⭐⭐ | Excelente para wallpaper + outline + tablas SFTP |
| ⭐⭐ | Viable con compromisos |
| ⭐ | Posible pero desaconsejado |
| ❌ | No cumple requisito visual o peso |

**Peso app** = estimado PyInstaller one-folder con Python 3.11 + paramiko + pandas + UI (no solo hello-world).

---

## Tabla maestra

| Framework | Versión estable (Jul 2026) | Python | Estado PyPI | ⭐ GitHub | Peso app* | Wallpaper | Outline transparente | Tabla SFTP | Docs | Mantenimiento | Nota decisión |
|-----------|---------------------------|--------|-------------|----------|-----------|-----------|---------------------|------------|------|---------------|---------------|
| **Slint** | Core **1.17.1** / Py **1.17.0b2** | ≥3.12 | Alpha (Py) | ~23k | **35–55 MB** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **#1 ligero + visual** |
| **PySide6** | **6.11.1** (May 2026) | 3.10–3.14 | Stable | Qt oficial | 80–120 MB | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **#1 estabilidad** |
| **PyQt6** | ~6.9.x (paralelo Qt) | 3.9+ | Stable | Riverbank | 80–120 MB | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Licencia GPL/comercial |
| **Flet** | **0.85.3** (dev 0.86) | ≥3.10 | Stable | ~16k | 55–85 MB | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | Motor Flutter pesado |
| **CustomTkinter** | **6.0.0** (Jun 2026) | ≥3.7 | Stable | ~13k | **15–25 MB** | ❌ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Muy ligero, **pobre capas** |
| **ttkbootstrap** | ~1.14.x | 3.x | Stable | ~1.5k | **15–25 MB** | ❌ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | Temas Tk; sin wallpaper real |
| **Tkinter** | stdlib 3.11+ | stdlib | Stable | PSF | **10–20 MB** | ❌ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Mínimo absoluto |
| **Dear PyGui** | **2.3.0** (Apr 2026) | 3.8+ | Stable | ~15k | **15–25 MB** | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | Estética tool/GPU |
| **wxPython** | **4.2.5** (Feb 2026) | ≥3.10 | Mature | ~2.5k | 40–70 MB | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Look nativo OS |
| **NiceGUI** | **3.14.0** (Jun 2026) | 3.10+ | Stable | ~16k | 40–80 MB† | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Web en ventana (pywebview) |
| **pywebview** | ~5.x (wrapper) | 3.x | Stable | ~4k | +15 MB | ⭐⭐⭐ | ⭐⭐⭐ | via HTML | ⭐⭐ | ⭐⭐ | Solo shell; tú haces HTML/CSS |
| **Kivy** | ~2.3.x | 3.8+ | Stable | ~17k | 50–90 MB | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | Touch/mobile vibe |
| **Bootstack** | **0.1.0a11** | 3.x | Alpha | ~12 | ? | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐ | Muy inmaduro |
| **Plushie** | pre-1.0 | 3.x | Pre-1.0 | ~3 | ? | ⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | Iced wrapper; alpha |
| **Textual** | 2.x | 3.x | Stable | ~24k | 15–30 MB | N/A | N/A | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **TUI** — ya descartado |

\* Rango orientativo empaquetado PDE Desktop.  
† NiceGUI incluye servidor FastAPI + Chromium embebido en native mode.

---

## Versiones exactas (pip / release)

```text
pip install slint==1.17.0b2          # Python bindings beta; core Slint 1.17.1
pip install PySide6==6.11.1
pip install flet==0.85.3
pip install customtkinter==6.0.0
pip install dearpygui==2.3.0
pip install wxPython==4.2.5
pip install nicegui==3.14.0
```

Enlaces:
- Slint: https://github.com/slint-ui/slint/releases/tag/v1.17.1
- PySide6: https://pypi.org/project/PySide6/6.11.1/
- Flet: https://pypi.org/project/flet/0.85.3/
- CustomTkinter: https://pypi.org/project/customtkinter/6.0.0/
- NiceGUI: https://github.com/zauberzeug/nicegui/releases/tag/v3.14.0

---

## Las “UI Python ligeras” que probablemente viste

### CustomTkinter 6.0.0
- **Qué es:** Tk moderno (dark mode, widgets redondeados).
- **Peso:** el más bajo del grupo (~15–25 MB).
- **Problema para PDE:** dibuja widgets **opacos** encima; no modelo wallpaper + scrim + bordes transparentes.
- **Veredicto:** ligera sí; **visual capas no**.

### ttkbootstrap / Tkinter
- Temas Bootstrap sobre Tk nativo.
- Igual limitación: sin capa imagen full-bleed bien integrada.

### Dear PyGui 2.3.0
- GPU, ~15–25 MB, muy rápida para dashboards.
- Wallpaper vía textura; estética “ImGui tool”, no app producto.
- Bugs resize Windows reportados.

### NiceGUI 3.14.0 + native mode
- `ui.run(native=True)` → ventana con **pywebview** (Chromium/WebKit).
- **Visual:** CSS completo → wallpaper + outline trivial.
- **Peso:** más que Slint (~40–80 MB); arranca servidor local.
- **Pros:** 100% Python lógica; HTML/CSS para diseño; docs excelentes.
- **Veredicto:** **#2 opción visual flexible** si aceptas stack web embebido.

### Flet 0.85.x
- Antes ligero (0.19 ~11 MB); **ahora 55–85 MB** y arranque más lento.
- No recomendado si “ligero” es criterio duro.

---

## Matriz decisión (tu proyecto)

| Prioridad | 1ª opción | 2ª opción |
|-----------|-----------|-----------|
| **Ligero + visual nativo** | Slint 1.17.x | — |
| **Estabilidad Python pura** | PySide6 6.11.1 | wxPython 4.2.5 |
| **Ligero absoluto (sin wallpaper)** | CustomTkinter 6.0.0 | Tkinter |
| **Máxima libertad visual (CSS)** | NiceGUI 3.14 native | pywebview + HTML |
| **Prototipo rápido descartable** | Flet 0.85.3 | — |

---

## Recomendación final (Jul 2026)

```text
1. Slint 1.17.0b2 (Python)  — si aceptas beta y .slint
2. PySide6 6.11.1           — si QA exige stable Production
3. NiceGUI 3.14 native      — si prefieres CSS/wallpaper sin aprender .slint
```

**Descartar para PDE Desktop visual:**
CustomTkinter, ttkbootstrap, Tk solo, Dear PyGui, Flet (peso), Bootstack/Plushie (alpha).

---

## PoC por opción (2–3 días c/u)

| Opción | Entregable PoC |
|--------|----------------|
| Slint | `app.slint` wallpaper + outline table + Python mock SFTP |
| PySide6 | QSS + QLabel background + QTableView |
| NiceGUI | `ui.image` background + CSS outline + aggrid/table |

Medir: MB empaquetado, ms arranque, FPS scroll 500 filas, WCAG contraste.

---

## ADR sugerido

Documentar elección en `documentacion/ui/adr/` cuando decidas:

- **UI-002a** Slint  
- **UI-002b** PySide6  
- **UI-002c** NiceGUI native  
