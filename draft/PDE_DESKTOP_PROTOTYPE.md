# PDE Desktop — plan por valor (alcance revisado)

## Visión
App de escritorio portable (Windows + Mac), ejecutable:
1. **SFTP** — navegar, preview, descargar, gestión de llaves
2. **Análisis con pandas** — estadísticas y reglas sobre archivos CSV (sin base de datos)

**Fuera de alcance por ahora:** Postgres, Snowflake, validación contra logs en BD.

Reutiliza lógica SFTP de `sftp-lite` / `pde_sftp_validator` y patrones pandas de `validators.py` (solo la parte de archivo local).

---

## Alcance funcional

### Núcleo SFTP (v0)
| Requisito | Notas |
|-----------|-------|
| Conector SFTP | paramiko |
| Elegir llave | dropdown desde carpeta configurable |
| Carpeta de llaves configurable | `ssh_keys_dir` (default `~/.ssh`) |
| Explorador remoto | carpetas y archivos |
| Preview en pantalla | texto/CSV (límite tamaño en RAM) |
| Descargar + elegir destino | file picker nativo |
| Generar llave SSH | RSA / ECDSA |

### Análisis pandas (v1, sin BD)
| Requisito | Notas |
|-----------|-------|
| Estadísticas del archivo | filas, columnas, nulos, tipos |
| Duplicados / únicos | por columna o combinación de claves |
| Detección de claves candidatas | columnas con cardinalidad alta/baja |
| Validación vs reglas locales | perfil JSON: delimitador, columnas esperadas, clínica/datasource como metadatos del perfil (no consulta a Postgres) |
| Validar archivo seleccionado | descarga temp → pandas → reporte en UI |
| Validar carpeta / lote | cola secuencial; temp en disco |

**No incluido (eliminado del plan):**
- Conector Postgres
- Conector Snowflake
- Validar archivo vs `extract_history`
- Validar todos los archivos vs logs en BD
- Sincronización CONFIG_ID / `sftp_credentials` desde BD

---

## Infraestructura recomendada

| Dimensión | Elección |
|-----------|----------|
| Runtime | Python 3.11+ |
| SFTP | paramiko |
| Análisis | pandas (lazy import: solo al abrir pestaña Análisis) |
| UI | Flet (prototipo) o PySide6 (si tablas grandes) |
| Empaquetado | PyInstaller one-folder o flet build |
| Proceso | 1 proceso UI + threads para SFTP y pandas |
| Config | perfiles JSON (SFTP + reglas pandas); sin `.env` de BD |

### Memoria estimada
| Modo | RAM aprox. |
|------|------------|
| Solo SFTP | 80–120 MB empaquetado + 50–80 MB runtime |
| SFTP + pandas activo | +50–150 MB según tamaño CSV |
| CSV grande | usar temp en disco; preview limitado (ej. 512 KB / 500 líneas) |

### Restricciones
- Preview y análisis: límite configurable de MB por archivo
- Scan de carpeta: secuencial, no cargar todos los CSV en RAM a la vez
- Sin VPN no hay SFTP; pandas funciona offline sobre archivos ya descargados

---

## Fases

### Fase 0 — Prototipo SFTP gráfico
SFTP completo + perfiles + ejecutable portable básico.

### Fase 1 — pandas sobre archivo(s)
Pestaña Análisis: un archivo desde SFTP o local; reporte duplicados/únicos/claves; reglas desde perfil JSON.

### Fase 2 — Lote y ejecutable final
Validar todos los archivos de una carpeta remota (descarga temp + cola); empaquetado .app / .exe para QA.

### Fase futura (no planificada)
- Postgres (logs, config PDE)
- Snowflake

---

## Contratos para agentes / mocks

```
ISftpBrowser     — list, download, preview, test_auth
IKeyStore        — discover(dir), generate
IProfileStore    — load/save JSON (SFTP + pandas rules)
IFileAnalyzer    — analyze(path) -> stats report (pandas)
```

Mocks: `MockSftpBrowser`, fixtures CSV, perfiles JSON de ejemplo.

---

## Stack mínimo (requirements)

```
paramiko
pandas
python-dotenv   # opcional, perfiles
flet            # o PySide6
```

Sin: psycopg2, snowflake-connector-python, textual.
