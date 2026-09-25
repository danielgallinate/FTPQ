# Iteración 2 — Funcionalidades

**Estado:** acordado con operador · **Fecha:** 2026-07-29  
**Base:** [`iteracion-02-enfoque-local.md`](./iteracion-02-enfoque-local.md)

---

## Arranque y layout

| Elemento | Comportamiento |
|----------|----------------|
| **Carpeta inicial** | `Downloads` del usuario |
| **Navegador archivos** | Pantalla principal al arrancar (panel derecho del layout idle) |
| **Al Abrir o Probar** | El **navegador desaparece** — el grid ocupa el espacio central |
| **Menú superior** | Se mantiene (estilo PDE) |
| **Capa inferior** | Franja ancho completo bajo el contenido — **comentarios / mensajes** |

Sin SFTP. Solo archivos locales.

### Capa inferior (comentarios)

- Contenido definitivo **pendiente** (operador lo detallará).
- **v1:** canal único para **alertas y mensajes** de la sesión (validación, errores de archivo, avisos de duplicados, etc.).
- Equivalente de rol al panel inferior del layout T de PDE; no bloquea el diseño futuro de comentarios estructurados.

---

## Acciones sobre archivo (doble clic)

| Opción | Comportamiento |
|--------|----------------|
| **Abrir** | Visualizador pandas/grid actual (sidebar Tab 1 sin modo validación). Navegador oculto. |
| **Probar** | Mismo grid + **panel derecho** de validación (3 tabs) + barra de progreso. Navegador oculto. |

Volver al navegador: acción explícita (cerrar viewer / menú Archivo — **detalle UI TBD**).

---

## Modo idle (solo navegador)

```text
┌──────────────────────────────────────────────────────────────┐
│  MENÚ                                                         │
├──────────────────────────────────────────────────────────────┤
│                    NAVEGADOR LOCAL → Downloads                │
├──────────────────────────────────────────────────────────────┤
│  COMENTARIOS / MENSAJES (alertas de sesión)                   │
└──────────────────────────────────────────────────────────────┘
```

---

## Modo Abrir (visualizar)

```text
┌──────────────────────────────────────────────────────────────┐
│  MENÚ                                                         │
├──────────────────────────────────────────────────────────────┤
│  GRID pandas — sidebar vista actual (columnas, stats, etc.)   │
├──────────────────────────────────────────────────────────────┤
│  COMENTARIOS / MENSAJES                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## Modo Probar (validar)

```text
┌──────────────────────────────────────────────────────────────┐
│  MENÚ                                                         │
├──────────────────────────────────────┬───────────────────────┤
│  GRID                                 │  PANEL VALIDACIÓN     │
│  — celdas verdes si llave OK          │  Tab1 │ Tab2 │ Tab3   │
│  — columnas no evaluadas en gris      │                       │
├──────────────────────────────────────┴───────────────────────┤
│  BARRA: % validado · resumen llaves en error                  │
├──────────────────────────────────────────────────────────────┤
│  COMENTARIOS / MENSAJES (alertas detalladas)                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Panel validación — Tab 1 (Vista)

- Paridad con `DataViewerWidget`: columnas visibles, filtro, stats, filas únicas, resaltado fila/columna, contrastes.
- **Interacción con Tab 2:** visibilidad y estilo de columnas siguen flags de evaluación.

---

## Panel validación — Tab 2 (Columnas a evaluar)

| Control | Efecto |
|---------|--------|
| Checkbox por columna | Marca columnas **sujetas a evaluación** |
| Desmarcada | Columna **gris** en grid y en lista |
| Marcada | Estilo normal |
| **Mostrar solo columnas evaluadas** | Oculta las demás en el grid |
| Tab 1 ↔ Tab 2 | Cambios sincronizados |

El **% validado** y las alertas consideran solo columnas marcadas para evaluación.

---

## Panel validación — Tab 3 (Template)

Un **template** es un único artefacto persistente con dos partes en el mismo archivo:

| Sección | Contenido |
|---------|-----------|
| **Header** | Nombre, composición de la fila lógica, **reglas** y definición de **llaves** (simples o **compuestas**, según cómo las guarde el operador) |
| **Minibase** | Registros de filas ya validadas/guardadas — crece **después** de definir header y reglas |

| Regla | Detalle |
|-------|---------|
| Sin template activo | Flujo pide **crear uno** antes de guardar registros |
| Tope del tab | Muestra nombre del template en uso |
| Fila lógica | Reunión de **celdas comunes** de distintas columnas/tablas con relaciones independientes |
| Feedback grid | Celdas participantes → **verde** cuando su llave valida según reglas del template |
| **Duplicados** | **Depurar / rechazar duplicados** en minibase — no justifica guardar el mismo registro dos veces |
| Reutilización | Cargar template existente, editar reglas, aplicar a otros archivos tabulares |

### Modelo de llave (borrador)

- Definida en el **header del template** (no hardcodeada en código).
- Soporta llaves **compuestas** (varias columnas/campos).
- Validación compara filas del archivo abierto contra reglas + minibase del template.

Almacenamiento local JSON (ruta concreta al implementar — p. ej. bajo `emr-qa/knowledge_bases/`).

---

## Barra inferior (modo Probar)

- **Porcentaje** de datos validados (columnas en evaluación × celdas/reglas aplicables).
- **Resumen** de llaves en error.
- Detalle extendido puede replicarse en capa comentarios.

---

## Formatos de archivo

**Objetivo:** todos los formatos **tabulares** que el esfuerzo permita.

| Fase | Formatos |
|------|----------|
| **Reutilización inmediata PDE** | `.csv`, `.tsv`, `.psv` (`core/analysis_types.py`, `pandas_analyzer`) |
| **Ampliación** | Excel (`.xlsx`, `.xls`), otros delimitados — vía pandas + dependencias solo si el coste es razonable |

Criterio: no bloquear iteración 2 por Excel; añadir cuando el pipeline Abrir/Probar esté estable en CSV.

---

## Ciclo de trabajo

1. App → navegador en `Downloads`.
2. Doble clic → **Abrir** (explorar) o **Probar** (validar).
3. **Probar:** Tab 2 elige columnas → Tab 3 crea/carga template → guarda registros en minibase → grid verde + % abajo.
4. Cerrar viewer → vuelve navegador.
5. Otro archivo del mismo tipo → mismo template; ajustar reglas si hace falta.

---

## Decisiones cerradas (2026-07-29)

| # | Pregunta | Respuesta |
|---|----------|-----------|
| 1 | Layout con archivo abierto | Navegador **desaparece** al Abrir o Probar |
| 2 | Capa comentarios | Contenido futuro; **v1 = alertas/mensajes** |
| 3 | Llaves | Simples o **compuestas**, definidas en **template** |
| 4 | Template vs minibase | **Misma entidad** — header (composición + reglas) + minibase (datos) |
| 5 | Unicidad | **Depurar duplicados** — no persistir dobles |
| 6 | Formatos | **Todos tabulares** si esfuerzo razonable; CSV primero |

---

## Pendiente (no bloquea spec)

- UX exacta: volver al navegador, menú Archivo en modo EMR QA.
- Contenido rico de comentarios (post-v1).
- Motor de evaluación de reglas en runtime — `emr-qa/emrqa/validation_engine.py` (`validate_rows`)
