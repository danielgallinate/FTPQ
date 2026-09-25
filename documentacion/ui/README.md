# Módulo UI

Interfaz gráfica, pantallas, flujos visuales, presentación de errores.  
**Solo presentación.** Lógica SFTP → [`../sftp/`](../sftp/). Análisis → [`../pandas/`](../pandas/).

---

## Documentos

| Archivo | Contenido |
|---------|-----------|
| [funcionalidades.md](./funcionalidades.md) | Catálogo **U01–Uxx** (capacidades de UI) |
| [restricciones.md](./restricciones.md) | UX, accesibilidad, no mezclar lógica |
| [fuera-de-alcance.md](./fuera-de-alcance.md) | Qué no es UI |
| [checklist-prototipo.md](./checklist-prototipo.md) | **QA verificable** — layout, Color, 4 paneles |
| [menu.md](./menu.md) | **Menú superior** — File, Configuración, Help |
| [layout-principal.md](./layout-principal.md) | Shell T invertida — P1, P2, P3 |
| [vision-producto.md](./vision-producto.md) | **Modelo de uso** — inicio sin red, conectar bajo demanda |
| [asistente-metadata.md](./asistente-metadata.md) | Asistente local — metadata PDE, sin leer contenido |
| [decision-ui-diferida.md](./decision-ui-diferida.md) | Decisión toolkit diferida (oficial) |
| [pantallas.md](./pantallas.md) | Inventario U-01–U-06 |
| [criterios-exito.md](./criterios-exito.md) | Checklist cierre UI |

---

## IDs de referencia

Prefijo **U** = UI.

---

## Implementación en código

| Capa | Carpeta repo |
|------|--------------|
| App | `ui/` |
| Prohibido | Import paramiko/pandas directo — solo contratos `core/` |

---

## Relación con otros módulos

| Módulo SFTP | UI consume |
|-------------|------------|
| S05 test | Botón + estados loading |
| S06 list | Tabla / árbol explorador |
| S08 preview | Panel texto (límite visible) |
| S09 download | File picker + progreso |

Wireframes definen **Uxx**, no reescriben **Sxx**.

---

## Estado

| Área | Estado |
|------|--------|
| Toolkit | **PySide6** en código 1.0.0 (prototipo) — ADR formal sin cerrar en [decision-ui-diferida.md](./decision-ui-diferida.md) |
| Contrato visual (wallpaper + outline) | Congelado en draft — [sistema-capas-wallpaper.md](../../draft/diseno/sistema-capas-wallpaper.md) |
| Wireframes U-00–U-SB | Layout T + pantallas — [layout-principal.md](./layout-principal.md), [pantallas.md](./pantallas.md) |
| QA prototipo | [`@ui-qa`](../../skills/ui/qa/SKILL.md) + [checklist-prototipo.md](./checklist-prototipo.md) |

**Prioridad post-1.0.0:** evolucionar por spec de módulo; SFTP spec ya cerrada en baseline.
