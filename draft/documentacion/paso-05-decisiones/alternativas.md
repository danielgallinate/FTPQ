# Alternativas evaluadas (no decidir en silencio)

Matrices del handoff original. Al elegir, crear ADR en `adr/`.

---

## UI

| Opción | Pros | Contras |
|--------|------|---------|
| **Flet** | Rápido, Python puro, portable | Tablas muy grandes más flojas |
| **PySide6** | App desktop madura, tablas | Más boilerplate UI |
| Tauri + web UI | Binario pequeño | Dos stacks; SFTP en sidecar |
| Electron | Ecosistema enorme | Muy pesado (~150 MB+) |

**Handoff:** Flet para prototipo Fase 0; reevaluar si tablas de lote F16 son lentas.

---

## Empaquetado

| Opción | Pros | Contras |
|--------|------|---------|
| **PyInstaller** | Predecible con paramiko+pandas | Antivirus a veces alerta |
| flet build | Integrado si UI=Flet | Menos control fino |
| briefcase | Estilo app store | Windows más complejo |

---

## Config / perfiles

| Opción | Pros | Contras |
|--------|------|---------|
| **JSON files** | Simple, versionable, mocks | Sin UI edición avanzada |
| .env + JSON | Compatible hábitos PDE | Dos fuentes de verdad |
| Solo .env | Familiar para QA | Menos estructura reglas |

---

## Análisis CSV

| Opción | Pros | Contras |
|--------|------|---------|
| **pandas** | Ya usado en validator PDE | RAM en archivos grandes |
| polars | Más rápido, menos RAM | Cambio de stack |
| pyarrow | Streaming parcial | Más bajo nivel |

---

## Cómo registrar la decisión

1. Copiar [adr/TEMPLATE.md](./adr/TEMPLATE.md)  
2. Nombrar `NNNN-titulo-corto.md`  
3. Actualizar tabla "Decisiones pendientes" en [README.md](./README.md)
