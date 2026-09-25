# UI — Funcionalidades

Capacidades de la **capa de presentación**. No duplicar Sxx/Pxx.

> **Visión de uso:** [vision-producto.md](./vision-producto.md) — inicio sin red, conectar bajo demanda.

| ID | Funcionalidad | Invoca (módulo) |
|----|---------------|-----------------|
| **U00** | Pantalla inicio (logo, créditos, acceso menús) | — (sin SFTP) |
| **U01** | Configuración conexión SFTP | S17, S02–S04 |
| **U02** | Conectar / desconectar (acción explícita) | S05, S01, S06 — vía **U-M01** File→Open |
| **U03** | Explorador remoto + detalle + breadcrumb | S06–S07, S10 |
| **U04** | Gestión llaves (discover, fingerprint, generar) | S03, S11–S14 |
| **U05** | Panel preview archivo | S08 |
| **U06** | Descarga con file picker | S09 |
| **U07** | Pestaña análisis CSV | P01–P06 (futuro) |
| **U08** | Estados loading / error / vacío / desconectado | Todos |
| **U09** | Acciones contextuales por archivo/carpeta | TBD v2 |
| **U-P1** | Panel navegador (layout T) | S06–S07, S10 — ver [layout-principal.md](./layout-principal.md) |
| **U-P2** | Panel detalle / mensajes / contenido | S08, errores UI |
| **U-P3** | Panel chatbot inferior | asistente-metadata |
| **U-SB** | Menú superior (default) — desacoplado | ver [menu.md](./menu.md) |
| **U-M01** | File → Open (llave, user, test, conectar) | S03, S05, S01, S06 |
| **U-M02** | Configuración → Llaves | S11–S14, U-04 |
| **U-M03** | Configuración → Rutas | S17, paths perfil |
| **U-M04** | Configuración → Otros | Snowflake/Postgres futuro |
| **U-M05** | Help → Who is | U-00 créditos |

Detalle por pantalla → [pantallas.md](./pantallas.md).
