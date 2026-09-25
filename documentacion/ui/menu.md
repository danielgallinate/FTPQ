# UI — Menú superior (U-SB)

> Estructura acordada — 2026-07-14  
> Barra **superior clásica**, desacoplada (U-R14). Layout → [layout-principal.md](./layout-principal.md).

---

## Árbol de menú (v1)

```text
File
  └── Open …                    ← llave, user, test, conectar

Configuración
  ├── Llaves …                  ← generar, ver llaves
  ├── Rutas …                   ← configuraciones generales de paths
  └── Otros …                   ← (futuro) Snowflake, Postgres

Help
  └── Who is …                  ← créditos / quiénes somos
```

---

## File → Open

**ID:** **U-M01**  
**Invoca:** S03, S05, S01, S06, S11–S13, S17 (parcial)

Modal o asistente **único punto de conexión** en flujo normal (U-R9).

| Paso | Acción | Notas |
|------|--------|-------|
| 1 | Seleccionar llave privada | S11 discover + picker; S13 validate |
| 2 | Elegir / confirmar **user** SFTP | S02; suele ligarse a perfil |
| 3 | **Test** conexión | S05 — handshake real |
| 4 | **Conectar** | S01 + list_dir ruta inicial S06 → P1 |

- Cancelar en cualquier paso → sin socket; app sigue.
- Fallo test (timeout, auth) → mensaje en **P2**; no cierra app (U-R10).
- Guardar perfil opcional al final — **guardar ≠ conectar**.

No hay auto-connect al abrir la app; **File → Open** es el disparador explícito.

---

## Configuración → Llaves

**ID:** **U-M02** (= U-04)  
**Invoca:** S11–S14, S03

| Acción | SFTP |
|--------|------|
| **Ver llaves** | discover en `ssh_keys_dir`, fingerprint S12 |
| **Generar llaves** | S14 RSA/ECDSA |

Cambio de llave activa en sesión conectada → S03 reconnect (L-01).

Sin test/conectar aquí — eso es **File → Open**.

---

## Configuración → Rutas

**ID:** **U-M03** (= U-01 rutas)  
**Invoca:** S17, S02 (parcial)

Configuraciones **generales de paths** — persistidas en perfil JSON, **sin abrir SFTP** al guardar.

| Campo | Descripción |
|-------|-------------|
| `ssh_keys_dir` | Carpeta búsqueda llaves (S04) |
| `default_remote_path` | Carpeta remota inicial |
| `download_dir` | Destino local descargas |
| `host`, `port` | Endpoint (opcional editar aquí o en Open) |

Equivalente validator: `DEFAULT_FOLDER`, `DOWNLOAD_DIR`, `SFTP_KEY_PATH` carpeta.

---

## Configuración → Otros

**ID:** **U-M04**  
**Estado:** **placeholder v1** — menú visible, contenido futuro.

| Futuro | Módulo |
|--------|--------|
| Snowflake | Fuera fase 0 — [scope-no-db](../../.cursor/rules/scope-no-db.mdc) |
| Postgres | Fuera fase 0 — mismo |

v1: pantalla “Próximamente” o ítems deshabilitados con tooltip. No implementar conectores hasta ADR explícito.

---

## Help → Who is

**ID:** **U-M05** (= U-00 info)  
**Invoca:** —

Modal o panel:

- Nombre producto PDE Desktop
- Versión
- Créditos / quiénes somos
- Rol: *lectura y asistencia sobre archivos provistos por PDE*

Sin red. Puede reutilizar contenido splash U-00.

---

## Mapa menú → pantallas existentes

| Ítem menú | ID | Pantalla / flujo |
|-----------|-----|------------------|
| File → Open | U-M01 | Conectar bajo demanda (U-02) |
| Configuración → Llaves | U-M02 | U-04 |
| Configuración → Rutas | U-M03 | U-01 (subset rutas) |
| Configuración → Otros | U-M04 | Futuro BD |
| Help → Who is | U-M05 | U-00 créditos |

---

## Etiquetas UI

Menú top-level en **inglés** (`File`, `Help`) y **español** (`Configuración`) — acordado producto. Submenús según tabla arriba.

Paridad Mac/Windows: menú nativo OS donde el toolkit lo permita (U-R5).

---

## Relacionado

- [funcionalidades.md](./funcionalidades.md) — U-M01…U-M05
- [restricciones.md](./restricciones.md) — U-R9, U-R14
- SFTP perfil → [`../sftp/schema-perfil.draft.json`](../sftp/schema-perfil.draft.json)
