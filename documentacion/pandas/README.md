# Módulo Pandas

Análisis de archivos CSV locales o descargados desde SFTP.  
**Solo este dominio.** Conexión remota → [`../sftp/`](../sftp/). Pantallas → [`../ui/`](../ui/).

---

## Documentos

| Archivo | Contenido |
|---------|-----------|
| [funcionalidades.md](./funcionalidades.md) | Catálogo **P01–Pxx** (por definir) |
| [restricciones.md](./restricciones.md) | Límites RAM, lote, etc. |
| [fuera-de-alcance.md](./fuera-de-alcance.md) | Qué no hace pandas |
| [criterios-exito.md](./criterios-exito.md) | Checklist cierre módulo |
| [analisis-librerias-visualizacion.md](./analisis-librerias-visualizacion.md) | Opciones tabla/stats para **Visualizar** |

---

## IDs de referencia

Prefijo **P** = Pandas.

---

## Implementación en código

| Capa | Carpeta repo |
|------|--------------|
| Contrato | `core/file_analyzer.py` |
| pandas | `adapters/pandas_analyzer.py` |

Import **lazy** de pandas (no cargar al arrancar app).

---

## Estado

Pendiente de definición. Borrador en `draft/PDE_DESKTOP_HANDOFF.txt` §2.2 (F11–F16).
