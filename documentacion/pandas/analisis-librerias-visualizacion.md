# Análisis — librerías para visualizar datos de archivo

> **Estado:** borrador para decisión — 2026-07-15  
> **Contexto:** acción **Visualizar** en explorador SFTP; hoy muestra texto plano en panel Detalle.  
> **Objetivo:** dar **poder real** a la visualización (tabla, stats, filtros) sin romper arquitectura `core/` / `ui/`.

---

## Decisión de producto (2026-07-15)

**Opción B — aprobada:** **Visualizar = descarga completa**, sin preview remoto parcial (S08 no se usa en este flujo).

| Aspecto | Comportamiento |
|---------|----------------|
| SFTP | `download()` del archivo entero → `tmp/pde-desktop/visualize/` |
| Lectura | `core/file_view.py` lee el archivo local completo |
| Pantalla | Texto plano hoy; tabla pandas en fase 1b |
| Límite pantalla | 500 líneas visibles (truncado solo en UI, archivo local íntegro) |
| Límite memoria | 50 MB para mostrar texto; si excede → error con ruta local del archivo ya descargado |
| S08 `preview()` | Permanece en contrato SFTP para otros usos; **no** expuesto en menú Visualizar |

---

## Situación actual

| Capa | Qué hace hoy |
|------|----------------|
| SFTP | `download()` completo → temp local |
| UI | `DetailPanel` con `QTextEdit` — texto del archivo descargado |
| Pandas | No implementado (`IFileAnalyzer` pendiente) |

**Nota:** el preview remoto S08 (512 KB) queda fuera del flujo Visualizar.

---

## Requisitos derivados

| ID | Requisito |
|----|-----------|
| V-01 | Arranque liviano — **lazy import** (no cargar pandas/QtCharts al boot) |
| V-02 | CSV clínico/operativo: ver **filas × columnas** con scroll, no dump de texto |
| V-03 | Archivos >512 KB preview o >~50 MB análisis: aviso + truncado / descarga |
| V-04 | Mismo contrato en mock y producción (`core/` sin PySide6/pandas) |
| V-05 | Cross-platform Mac + Windows (PySide6 ya elegido en prototipo) |
| V-06 | Worker thread único SFTP; **parse/visualización en hilo aparte** tras bytes en memoria o temp file |
| V-07 | Escalabilidad razonable: 5k–50k filas preview; millones → solo muestra + stats |

---

## Opciones evaluadas

### 1. Solo texto enriquecido (estado actual + mejoras mínimas)

**Stack:** `QTextEdit` / `QPlainTextEdit`, syntax highlight manual opcional.

| Pros | Contras |
|------|---------|
| Cero deps nuevas | CSV ilegible en archivos reales |
| Ya implementado | No sorting, filtros, tipos |
| Seguro para JSON/log | No escala percepción de “producto” |

**Veredicto:** OK para `.log`, `.json` pequeño, `.env`. **Insuficiente** como destino principal de “Visualizar” en CSV.

---

### 2. Tabla nativa Qt — `QTableView` + `QAbstractTableModel` + pandas (recomendado fase 1)

**Stack:**

```text
preview bytes / temp file
    → adapters/pandas_analyzer.py (lazy pandas.read_csv)
    → core/file_view.py → TabularViewModel (filas/columnas/dtypes/stats)
    → ui/widgets/data_table_view.py (QTableView)
```

| Pros | Contras |
|------|---------|
| Encaja con PySide6 prototipo | Hay que implementar model + paginación |
| `QTableView` virtualiza filas (solo pinta visibles) | pandas RAM en CSV grandes |
| Reutiliza stack planificado (F11–F15) | Sort/filter requiere código |
| Sin dep web embebida | |

**Patrón recomendado:**

- Preview remoto ≤512 KB: `StringIO` → pandas con `nrows=500` (alineado R14).
- Visualizar archivo grande: botón “Descargar y abrir completo” → temp → `read_csv` con límite perfil.
- Model expone solo ventana (ej. 500 filas) + metadatos (`truncated`, `total_rows` estimado).

**Veredicto:** **Opción principal** para PDE Desktop — máximo control, mismo toolkit, alineado con `documentacion/pandas/`.

---

### 3. `QTableWidget` directo

Rellenar celdas una a una sin model.

| Pros | Contras |
|------|---------|
| Implementación rápida para demo | O(n) memoria y widgets — **malo** >500 filas |
| | No es patrón Qt idiomático |

**Veredicto:** Solo PoC de un día; **no** producción.

---

### 4. DuckDB / Polars en lugar de pandas (solo parse)

**Stack:** `polars.read_csv` o `duckdb.read_csv` → convertir a model Qt.

| Pros | Contras |
|------|---------|
| Polars: menos RAM, más rápido en lote | Cambia stack acordado (handoff = pandas) |
| DuckDB: SQL ad hoc sobre CSV | Dep extra; curva para reglas JSON existentes |

**Veredicto:** Evaluar en **fase lote (P06)** si pandas no escala; no para primera visualización.

---

### 5. Visor embebido web — `QWebEngineView` + DataTables / AG Grid / Perspective

| Pros | Contras |
|------|---------|
| UX rica (filtros, column resize) | +80–150 MB binario, Chromium |
| | Complejidad empaquetado Win/Mac |
| | Rompe espíritu “app liviana offline” |

**Veredicto:** Descartado salvo requisito explícito de grid enterprise.

---

### 6. Gráficos — `QtCharts` / `matplotlib` / `plotly`

| Librería | Uso en PDE |
|----------|------------|
| **QtCharts** (PySide6) | Histogramas, conteos por columna — integrado, lazy |
| **matplotlib** | Informes estáticos; pesado; segunda ventana |
| **plotly** | Web; overkill |

**Veredicto:** **QtCharts opcional fase 2** (P02 stats visuales). No sustituye tabla.

---

### 7. Excel-like — `pyqtgraph`, `fastplotlib`, `VisPy`

Orientados a series numéricas / señales, no tablas CSV administrativas.

**Veredicto:** Fuera de alcance.

---

## Arquitectura propuesta (capas)

```text
┌─────────────────────────────────────────────────────────┐
│ ui/panels/detail_panel.py  o  ui/widgets/file_preview/  │
│   · TextPreviewWidget (log/json)                        │
│   · TabularPreviewWidget (QTableView)                   │
└───────────────────────────┬─────────────────────────────┘
                            │ IFilePreview / FileViewState
┌───────────────────────────▼─────────────────────────────┐
│ core/file_preview.py                                    │
│   · detect_kind(path|ext|bytes) → text | tabular        │
│   · PreviewLimits (bytes, rows)                         │
└───────────────────────────┬─────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
  adapters/text      adapters/pandas     mocks/mock_analyzer
  (utf-8 decode)     (read_csv lazy)     (fixture CSV)
```

**Flujo Visualizar (implementado):**

1. UI emite `visualize_requested` en `SftpSessionWorker`.
2. `AppController.visualize_remote_file` → `browser.download()` completo.
3. `read_visualize_file(local_path)` en `core/file_view.py`.
4. UI muestra contenido + ruta local + metadatos.
5. Fase 1b: mismo path local → pandas → `QTableView`.

---

## Matriz decisión resumida

| Opción | Arranque | CSV 10k filas | Deps | Alineación repo | Recomendación |
|--------|----------|---------------|------|-----------------|---------------|
| Texto plano | ★★★★★ | ★ | — | S08 actual | Mantener para no-CSV |
| QTableView + pandas | ★★★★ | ★★★★ | pandas (ya plan) | ★★★★★ | **Fase 1 visualización** |
| QTableWidget | ★★★★★ | ★ | — | ★★ | Solo demo |
| Polars/DuckDB | ★★★ | ★★★★★ | nueva | ★★ | Fase lote |
| QWebEngine + grid JS | ★★ | ★★★★★ | pesada | ★ | No |
| QtCharts | ★★★★ | N/A | incluida PySide6 | ★★★★ | Fase 2 stats |

---

## Plan incremental sugerido

| Fase | Entregable | Librerías |
|------|------------|-----------|
| **0** (hecho) | Preview texto + worker único SFTP | — |
| **1a** | `IFilePreview` + detector extensión | stdlib |
| **1b** | `pandas.read_csv` → `TabularViewModel` → `QTableView` | pandas, PySide6 |
| **1c** | Barra resumen: filas/cols/truncated/nulos top | pandas |
| **2** | Reglas P05 + panel Consulta | pandas, jsonschema |
| **2b** | Mini charts QtCharts (distribución, nulos) | QtCharts |
| **3** | Lote P06, cola, polars si RAM mata | polars (ADR) |

---

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| RAM con CSV 100 MB+ | Límite perfil; preview parcial; no parse completo en S08 |
| pandas lento en UI thread | Worker analítica + spinner en Detalle |
| Tipos mixtos / fechas | `dtype=str` en preview; inferencia opcional en análisis |
| Separador `;` vs `,` | Reglas JSON perfil (P05) |
| Datos sensibles en pantalla | Solo lectura; no logs de contenido (R25) |

---

## Referencias internas

- SFTP S08 / R11–R15: `documentacion/sftp/`
- Pandas P01–P06: `documentacion/pandas/funcionalidades.md`
- UI delgada: `documentacion/ui/decision-ui-diferida.md`
- Handoff F11–F16: `draft/PDE_DESKTOP_HANDOFF.txt`
