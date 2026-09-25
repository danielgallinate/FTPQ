# SFTP — Fuera de alcance

Explicitamente **no** es responsabilidad del módulo SFTP.

---

## Operaciones remotas

- Upload (subir archivos al servidor)
- Borrar o renombrar en **remoto**
- Sincronización bidireccional de carpetas
- Sincronización bidireccional de carpetas
- Múltiples conexiones SFTP simultáneas
- Túnel SSH genérico (solo canal SFTP)

*Upload/delete: fase futura con ADR propio en este módulo.*

---

## Otros dominios

| Tema | Módulo responsable |
|------|-------------------|
| Validación vs `extract_history` | Futuro / BD (no ahora) |
| Postgres, CONFIG_ID lookup | Fuera del producto fase 0–2 |
| Análisis CSV, duplicados, reglas | [`../pandas/`](../pandas/) |
| Botones, pantallas, pickers, Lottie | [`../ui/`](../ui/) |
| Empaquetado `.exe` / `.app` | Infra / scripts (doc futura) |

---

## Preview que no es SFTP

Decidir **qué** mostrar en pantalla para binarios es UI.  
SFTP solo reporta: tipo no previewable → usar S09.
