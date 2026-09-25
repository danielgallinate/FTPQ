# Paso 2 — Funcionalidades deseadas

Checklist funcional acordado. IDs **Fxx** son referencia estable para issues, tests y agentes.

---

## 2.1 SFTP — núcleo obligatorio (Fase 0)

| ID | Funcionalidad | Notas |
|----|---------------|-------|
| F01 | Conector SFTP (llave privada SSH) | paramiko |
| F02 | Configurar host, puerto, usuario | UI + perfil JSON |
| F03 | Selector de llave privada en UI | **Gap del TUI:** tecla K no aplica llave al SFTP |
| F04 | Carpeta de llaves configurable | Default `~/.ssh`; Win: `C:\Users\<user>\.ssh` |
| F05 | Probar conexión (test auth) | Siempre contra Transfer real |
| F06 | Explorador gráfico remoto | Carpetas y archivos |
| F07 | Navegar (entrar, subir, refrescar) | — |
| F08 | Preview texto/CSV | Límite RAM: ~512 KB o 500 líneas |
| F09 | Descargar + elegir destino | File picker nativo OS |
| F10 | Generar par llaves SSH | RSA y/o ECDSA |

---

## 2.2 Pandas — análisis sin BD (Fase 1–2)

| ID | Funcionalidad | Notas |
|----|---------------|-------|
| F11 | Analizar CSV (remoto temp o local) | Descarga a temp si viene de SFTP |
| F12 | Stats básicas | Filas, columnas, tipos, nulos |
| F13 | Duplicados / únicos | Por columna o combinación |
| F14 | Detección claves candidatas | Cardinalidad / unicidad |
| F15 | Validar vs perfil JSON local | Delimitador, columnas, metadatos negocio |
| F16 | Validar carpeta (lote) | Cola **secuencial**; resultados en tabla UI |

---

## 2.3 Configuración y perfiles

| ID | Funcionalidad | Notas |
|----|---------------|-------|
| F17 | Guardar/cargar perfiles conexión SFTP | host, user, port, key, dirs |
| F18 | Reglas pandas por perfil | JSON embebido o referenciado |
| F19 | Múltiples perfiles | ej. `Daniel_test_config10` |

---

## 2.4 Empaquetado y plataforma

| ID | Funcionalidad | Notas |
|----|---------------|-------|
| F20 | Ejecutable portable Win + Mac | Sin Python manual en destino |
| F21 | Scripts paridad | `setup.sh`/`run.sh` + `setup.ps1`/`run.ps1` |
| F22 | Regla cross-platform en Cursor | Cambios probados en ambos OS |

---

## Límites funcionales acordados

| Área | Límite |
|------|--------|
| Preview | Solo texto/CSV; binarios → solo descarga |
| pandas | Aviso si archivo > ~50 MB |
| Lote | Un CSV a la vez en memoria |
| Temp | `downloads/`, `tmp/analysis/`; limpiar por sesión |
| Rutas | `pathlib.Path`, `expanduser`; no concatenar con `/` |
| Reinicio Win | `subprocess`, no `os.execv` solo |

---

## Fases de entrega

### Fase 0 — SFTP gráfico ejecutable
F01–F10, F17–F21, perfiles JSON básicos, zip portable.

### Fase 1 — pandas un archivo
F11–F15, reporte UI, lazy import pandas.

### Fase 2 — Lote + ejecutable final
F16, cola secuencial, `.app` / `.exe` para QA WorkSpace.

### Fase futura (fuera de handoff)
Postgres, Snowflake, validación vs `extract_history`.

---

## Criterios de éxito (prototipo)

- [ ] Conectar SFTP con llave elegida en UI (sin editar `.env` a mano)
- [ ] Navegar `scheduled/` / `requested` y ver archivos
- [ ] Preview de CSV de ejemplo
- [ ] Descargar a carpeta elegida
- [ ] Generar llave nueva en `~/.ssh`
- [ ] Analizar CSV: duplicados, únicos, columnas según perfil JSON
- [ ] Misma funcionalidad en Mac (`./run.sh`) y Windows (`.\run.ps1`)
- [ ] Zip/carpeta portable sin Python instalado en máquina destino

---

## Fuera de alcance explícito

- PostgreSQL / RDS  
- Snowflake  
- Validar vs `extract_history`  
- F4 estilo validator con lookup Postgres  
- TUI / Textual como UI principal  
- WSL / Cygwin / Git Bash como **requisito** en Windows  

**Anterior:** [Paso 1](../paso-01-entender/README.md) · **Siguiente:** [Paso 3 — Infraestructura](../paso-03-infraestructura/README.md)
