# Paso 5 — Contextos fuertes y decisiones

ADRs (Architecture Decision Records), alternativas pendientes y lecciones del validator TUI.

---

## Decisiones tomadas (no reabrir sin ADR)

| ID | Decisión | Razón |
|----|----------|-------|
| D-01 | **Sin Postgres/Snowflake** en fase 0–2 | Alcance acordado; prototipo más rápido |
| D-02 | **UI gráfica**, no TUI | Expectativa QA; sftp-lite no cumple |
| D-03 | **Perfiles JSON** vs solo `.env` | Versionable, mocks, reglas pandas estructuradas |
| D-04 | **Test SFTP real** cuando se prueba conexión | Transfer puede desincronizarse de BD |
| D-05 | **Windows nativo** (.ps1) sin WSL obligatorio | WorkSpace QA |
| D-06 | **core/ sin UI** | Agentes y tests aislados |
| D-07 | **Cola secuencial** en lote pandas | Límite RAM |
| D-08 | **Lazy import pandas** | Arranque más liviano |

---

## Decisiones pendientes

| ID | Opciones | Recomendación handoff | Criterio para decidir |
|----|----------|----------------------|------------------------|
| D-UI | Flet vs PySide6 | Flet para Fase 0 | Tablas >10k filas → PySide6 |
| D-PKG | PyInstaller vs flet build | PyInstaller si UI=Flet | Control paramiko + pandas |
| D-CSV | pandas vs polars | pandas | Reuso validator PDE |
| D-ENC | Cifrar perfiles con secretos | No en Fase 0 | Si perfiles van por canal inseguro → cryptography |

Ver matrices completas en [alternativas.md](./alternativas.md).

---

## Lecciones del proyecto anterior (rules obligatorias)

Estas entradas deben vivir en `.cursor/rules/` como contexto duro:

### L-01 — Selector de llave en SFTP
En sftp-lite, tecla **K** lista/genera llaves pero **no aplica** la llave a la conexión SFTP.  
**PDE Desktop:** F03 debe cambiar la llave activa y reconectar.

### L-02 — AWS Transfer vs BD
`config10` autenticó OK con llave de `config3` cuando Transfer estaba bien provisionado.  
`config3` falló por **servidor**, no por llave local.  
**Regla:** nunca marcar conexión OK sin `test_auth()` real.

### L-03 — Paridad Windows
Reinicio de app: usar `subprocess` en Windows, no `os.execv` solo.  
Rutas: `pathlib.Path` + `expanduser`.

### L-04 — Preview y pandas
Documentar límites en perfil y rules: 512 KB / 500 líneas preview; aviso >50 MB.

### L-05 — Validación legacy (referencia)
El validator TUI usa **`extract_path`** como fuente de verdad, no `delivery_folder`.  
PDE Desktop **no implementa** esto en fase 0; solo referencia para fase futura.

---

## ADRs (plantilla)

Nuevas decisiones → archivo en `documentacion/paso-05-decisiones/adr/`:

```text
adr/
├── 0001-sin-base-de-datos.md
├── 0002-perfiles-json.md
└── TEMPLATE.md
```

Formato: contexto → decisión → consecuencias → estado (propuesto | aceptado | obsoleto).

---

## Rules Cursor (esqueleto)

Ubicación: `.cursor/rules/` en repo final. Borradores en [../../.cursor/rules/](../../.cursor/rules/).

| Rule | Propósito |
|------|-----------|
| `scope-no-db.mdc` | Prohibe psycopg2, snowflake, textual |
| `architecture.mdc` | core sin UI; contratos |
| `cross-platform.mdc` | Paridad .sh / .ps1 |
| `sftp-real-test.mdc` | test_auth obligatorio |
| `memory-limits.mdc` | Preview y pandas limits |

---

## Qué copiar al repo nuevo

1. `documentacion/` completa  
2. `.cursor/rules/*.mdc`  
3. `.cursor/skills/` del proyecto  
4. `mocks/fixtures/` mínimos  
5. `PDE_DESKTOP_HANDOFF.txt` como referencia compacta  

**Anterior:** [Paso 4](../paso-04-mocks/README.md) · **Índice:** [README](../README.md)
