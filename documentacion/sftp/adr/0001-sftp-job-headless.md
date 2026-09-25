# ADR-0001 — Job SFTP headless

## Estado
Aceptado (2026-09-17)

## Contexto

EMR QA ya se ejecuta por receta JSON y script (`./scripts/run_emr_qa_job.sh`). SFTP solo existía detrás de la UI PDE. El operador necesita **conectar, comprobar que los extracts existen y descargar una secuencia** desde un script, y después validar formato y calidad con el validador tabular **sobre archivos locales**.

ADR EMR QA ([0001](../../emr-qa/adr/0001-alcance-local-only.md), [0002](../../emr-qa/adr/0002-validador-tabular-compartible.md)): el motor pandas sigue leyendo **disco**. SFTP no es un conector de base de datos.

## Decisión

1. Job propio `kind: sftp_fetch` (no mezclar con `EmrQaJob`).
2. CLI `./scripts/run_sftp_job.sh` — mismo patrón de receta, `--json-out`,
   `--error-out` y exit `0` / `1` / `2`.
3. El browser se crea con `create_sftp_browser()` (mock si `PDE_DESKTOP_MOCK=1`). La UI reutiliza ese factory.
4. El validador EMR QA **no** importa paramiko; encadena `--file` a lo ya descargado.
5. El ejecutor puede suministrar `--sftp-user`, `--private-key` y
   `--local-dir` sin editar la receta. Esos parámetros tienen prioridad sobre
   el perfil/job. La llave no se copia ni aparece en resultados.
6. Con `recursive: true`, se preserva la jerarquía remota y se escribe
   `_download_manifest.json`. `destination_name: "{sftp_user}"` crea una
   carpeta por configuración.

## Consecuencias

- Funcionalidades **S18** (job headless) y **S19** (descarga en secuencia) en el catálogo SFTP.
- Los jobs no recursivos conservan el comportamiento v1. Los recursivos usan
  globs `fnmatch` sobre nombre o ruta relativa.
- `on_collision: fail` rechaza una carpeta de configuración ya existente.
- Composición: script de operador llama SFTP y luego EMR QA.

## Referencias

- Contrato: [`../contrato.md`](../contrato.md)
- Catálogo: [`../funcionalidades.md`](../funcionalidades.md)
- Validador local: [`../../emr-qa/adr/0001-alcance-local-only.md`](../../emr-qa/adr/0001-alcance-local-only.md)
