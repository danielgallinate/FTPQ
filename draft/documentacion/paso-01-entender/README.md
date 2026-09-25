# Paso 1 — Entender el producto

## Qué estamos construyendo

**PDE Desktop** es una aplicación de escritorio **portable** con **interfaz gráfica** (no terminal/TUI) para:

1. Conectar a **SFTP** (AWS Transfer Family) con llave SSH privada  
2. **Explorar**, previsualizar y **descargar** archivos remotos  
3. **Analizar CSV** con pandas usando **reglas locales** (perfiles JSON)

Plataformas objetivo: **macOS** y **Windows nativo** (PowerShell, sin WSL obligatorio).

## Qué NO es

| No es | Por qué importa |
|-------|-----------------|
| Copia del PDE SFTP Validator TUI | El validator usa Textual, Postgres y validación vs `extract_history` |
| Herramienta con base de datos | Postgres/Snowflake quedan en **fase futura** |
| App que requiere WSL en Windows | QA WorkSpace debe usar `.ps1` nativos |
| Validador oficial contra logs PDE | Las reglas pandas vienen de JSON local, no de `config` en RDS |

## Relación con el proyecto anterior

```text
pde_sftp_validator (TUI)          pde-desktop (nuevo)
─────────────────────────         ────────────────────
Textual / F-keys                  UI gráfica (Flet/PySide6)
.env + Postgres                   Perfiles JSON
F7 SFTP ↔ DB                      Solo SFTP + pandas local
sftp-lite parcial                 Reutilizar lógica paramiko/pandas
WSL recomendado en Win            PowerShell nativo obligatorio
```

**Reutilizar (ideas/código):**

- Lógica SFTP de `sftp-lite` / `pde_sftp_validator`  
- Patrones pandas de `validators.py` **solo** la parte de archivo local  

**No portar en esta fase:**

- Pantalla F4 con lookup Postgres  
- F7 bidireccional SFTP ↔ DB  
- `CONFIG_ID`, `sftp_credentials`, `connection_verified` desde BD  

## Usuarios y escenarios

| Actor | Necesidad |
|-------|-----------|
| QA / analista PDE | Conectar SFTP, ver archivos, descargar, validar CSV sin editar `.env` a mano |
| Desarrollo | Prototipo rápido, mocks sin VPN, empaquetado portable |
| Agente Cursor | Contratos claros (`core/` sin UI), rules que prohíban psycopg2 en fase 0 |

## Restricciones de entorno

- **VPN corporativa** requerida para SFTP real en entornos PDE  
- **Test SFTP siempre real** cuando se prueba conexión (no confiar en flags externos)  
- **IP en whitelist** AWS Transfer Family  
- pandas funciona **offline** sobre archivos ya descargados  

## Glosario mínimo

| Término | Significado en PDE Desktop |
|---------|---------------------------|
| **Perfil** | JSON con host SFTP, usuario, llave, reglas pandas |
| **CONFIG_NAME** (legacy) | En el validator = tenant en Postgres; aquí = nombre lógico del perfil |
| **scheduled / requested** | Carpetas típicas bajo `config/<nombre>/` en SFTP |
| **Perfil pandas** | Delimitador, columnas requeridas, metadatos de negocio en JSON |

## Preguntas que este paso debe responder

- [ ] ¿Entiendo que no hay BD en fase 0–2?  
- [ ] ¿Entiendo la diferencia con el TUI validator?  
- [ ] ¿Sé quién usa la app y qué flujo principal esperan?  

**Siguiente:** [Paso 2 — Funcionalidades](../paso-02-funcionalidades/README.md)
