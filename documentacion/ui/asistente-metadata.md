# UI — Asistente metadata (sin contenido)

> Alcance acordado — 2026-07-14  
> Complementa [vision-producto.md](./vision-producto.md). Todo **local**; nada a la nube.

---

## Rol del producto

PDE Desktop **no es el sistema que crea los archivos**. Los objetos en SFTP los **provee PDE** (upstream). Esta app:

- Lista y navega (S06–S07)
- Filtra por carpeta, fecha, patrón de **nombre**
- Descarga bajo demanda (S09)
- Opcional: asistente conversacional que traduce intenciones → esos filtros

**No** modifica remoto. **No** es obligatorio leer el interior del CSV en v1 del asistente.

---

## Convención de nombres (compliance)

| Regla | Estado |
|-------|--------|
| Nombres = tipo de documento / extract, no individuos | Convención PDE |
| Sin identificadores de persona en el filename | **Aceptado** por el equipo / compliance |
| Rutas `config/<profile>/scheduled\|requested` | Metadato de entorno, no paciente |

El asistente metadata puede usar **nombres, fechas, tamaños y rutas** en UI, logs locales e intenciones — sin tratar el filename como PHI.

El **contenido** del archivo sigue siendo sensible; por diseño el asistente v1 **no lo parsea**.

---

## Qué hace el asistente (v1 metadata)

| Intención ejemplo | Acción | Lee contenido |
|-------------------|--------|---------------|
| “scheduled última semana” | list + filtro `mtime` / nombre | No |
| “CSV de marzo en requested” | patrón nombre + carpeta | No |
| “Descarga los seleccionados” | S09 | Solo bytes al disco (operador) |
| “¿Cuántos archivos hay?” | conteo metadata | No |

Fuera de alcance v1 asistente: duplicados por columna, conteos de IDs **dentro** del CSV → módulo pandas aparte, consentimiento explícito.

---

## IA comercial vs motor real

| Capa | Descripción |
|------|-------------|
| **Venta** | “Asistente inteligente” — búsqueda y descarga en lenguaje natural |
| **Motor preferido** | Plantillas + reglas locales (whitelist de acciones) |
| **Opcional** | LLM **local** solo para clasificar intención — sin enviar contenido ni nube |
| **Prohibido v1** | LLM cloud con listados o CSV |

---

## Restricciones (U-R11–U-R13)

| ID | Restricción |
|----|-------------|
| **U-R11** | Asistente metadata **no** invoca S08 preview ni pandas sobre CSV clínico |
| **U-R12** | Acciones del asistente = whitelist (listar, filtrar, descargar) |
| **U-R13** | Datos de sesión y consultas: log local auditable; sin upload |

---

## Dependencias

- Explorador U-03 operativo
- Conexión bajo demanda U-02
- Contexto archivos PDE → [`../sftp/contexto-pde.md`](../sftp/contexto-pde.md)

## Fases

```text
v1    Filtros fecha/nombre en explorador (sin chat)
v1.5  Asistente = NL → plantillas metadata
v2    LLM local opcional (intención only)
```

Análisis previo: conversación producto 2026-07-14 (metadata-only, filenames no PHI).
