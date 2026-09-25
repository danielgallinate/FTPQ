# Agentes Cursor — PDE Desktop

Roles sugeridos para desarrollo asistido. Copiar/adaptar a `AGENTS.md` en el repo final.

---

## Principios para todos los agentes

1. Leer [paso-01-entender](../paso-01-entender/README.md) antes de codear  
2. Respetar `.cursor/rules/` — especialmente `scope-no-db`  
3. No importar UI en `core/`  
4. Cambios en `.sh` → equivalente `.ps1`  
5. Preferir mocks cuando la tarea no requiera VPN  

---

## Agente: Architect

**Cuándo invocar:** diseño de módulos, nuevos contratos, split core/adapters.

**Contexto obligatorio:**
- `documentacion/paso-03-infraestructura/README.md`
- `documentacion/paso-05-decisiones/README.md`
- `.cursor/rules/architecture.mdc`

**No debe:**
- Añadir Postgres "por si acaso"
- Acoplar pandas a paramiko en core

---

## Agente: SFTP Feature

**Cuándo invocar:** F01–F10, explorador, llaves, download.

**Contexto obligatorio:**
- `paso-02-funcionalidades` § SFTP
- `paso-04-mocks` + `MockSftpBrowser`
- Lección L-01, L-02 en paso-05

**Entregables típicos:**
- Adapter `paramiko_sftp.py`
- Tests con fixtures JSON
- UI: panel explorador + selector llave

---

## Agente: Pandas Feature

**Cuándo invocar:** F11–F16, reglas JSON, lote.

**Contexto obligatorio:**
- Perfil ejemplo en `mocks/fixtures/profiles/`
- Límites memoria en `memory-limits.mdc`
- Lazy import pandas

**Entregables típicos:**
- `pandas_analyzer.py`
- Reporte estructurado `AnalysisReport`
- Tabla resultados lote en UI

---

## Agente: Cross-Platform / Packaging

**Cuándo invocar:** scripts, PyInstaller, QA zip.

**Contexto obligatorio:**
- `plataformas/macos.md`, `plataformas/windows.md`
- `.cursor/rules/cross-platform.mdc`

**Checklist:**
- [ ] `setup.ps1` refleja `setup.sh`
- [ ] Reinicio Win vía subprocess
- [ ] Rutas pathlib en todo el core

---

## Agente: QA Handoff

**Cuándo invocar:** preparar zip para WorkSpace, README QA.

**Contexto obligatorio:**
- Criterios éxito paso-02
- Sin secretos en zip
- Perfil ejemplo sin llaves reales

**Plantilla entrega:**

| Paquete | Contenido |
|---------|-----------|
| Zip portable | `dist/pde-desktop-*` |
| Canal seguro | Llaves SSH, perfiles prod |
| Docs | README + link a macos/windows |

---

## Prompt semilla (copiar al iniciar sesión)

```text
Proyecto: PDE Desktop — app SFTP gráfica + pandas, SIN Postgres.
Lee documentacion/README.md y el paso relevante.
Respeta .cursor/rules/. Usa mocks si no hay VPN.
Paridad Windows: todo .sh tiene .ps1.
```

---

## Subagentes Cursor recomendados

| Tarea | Subagente |
|-------|-----------|
| Explorar repo legacy | `explore` |
| Review pre-PR | `code-reviewer` o skill review-bugbot |
| CI rojo | `ci-investigator` |
| Shell/scripts | `shell` |
