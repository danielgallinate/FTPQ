# ADR-0001: Módulo EMR QA local dentro de FTPQ

## Estado
Aceptado (2026-07-22) · **Parcialmente superseded** por [ADR-0002](./0002-validador-tabular-compartible.md) (2026-08-05)

## Contexto

FTPQ agrega una ruta funcional **100 % local**, sin conectores live a Postgres/Snowflake.

La regla `.cursor/rules/scope-no-db.mdc` prohíbe conectores BD y validación estilo validator TUI contra RDS. Este módulo **no viola** esa intención si opera solo con archivos en disco y pandas.

## Decisión (vigente)

1. **Ubicación:** `emr-qa/` + spec en `documentacion/emr-qa/`.
2. **Prohibido (sin nuevo ADR):** `psycopg2`, `asyncpg`, `snowflake-connector-python`, consultas live a RDS.
3. **Permitido:** Python + pandas, plantillas JSON locales, archivos delimitados en disco.
4. **Producto activo:** validador tabular (`emr-qa/shell/app.py`) — ver [README](../README.md).

## Obsoleto en este ADR

Lo siguiente pertenecía a **iteración 1 archivada** (`emr-qa/ALPHA/`) y **no aplica** al flujo activo:

- HTML capturado en browser / consola F12
- `browser_extractor.js` / capturador JS
- Editor de marcado manual sobre snaps de pantalla
- Selenium / Playwright / scraper de pantallas

## Consecuencias

- Dominio separado del SFTP legacy en `core/`
- Validación de fechas/timezone requiere reglas explícitas en plantillas

## Referencias

- Spec activa: [`../README.md`](../README.md)
- ADR alcance compartible: [`./0002-validador-tabular-compartible.md`](./0002-validador-tabular-compartible.md)
- Iteración 1 archivada: [`../iteracion-01-extraccion.md`](../iteracion-01-extraccion.md)
