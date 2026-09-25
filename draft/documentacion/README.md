# PDE Desktop — Handoff de documentación

> **Objetivo:** armar el proyecto `pde-desktop` con contexto duro para agentes, QA y desarrollo.  
> **Alcance actual:** SFTP gráfico + análisis pandas **sin** Postgres ni Snowflake.  
> **Fecha handoff:** 2026-07-14

---

## Mapa de la documentación

| Paso | Carpeta | Contenido |
|------|---------|-----------|
| **1** | [paso-01-entender](./paso-01-entender/README.md) | Qué es el producto, qué NO es, relación con validator anterior |
| **2** | [paso-02-funcionalidades](./paso-02-funcionalidades/README.md) | F01–F22, fases, criterios de éxito |
| **3** | [paso-03-infraestructura](./paso-03-infraestructura/README.md) | Arquitectura, stack, repo, empaquetado, memoria |
| **4** | [paso-04-mocks](./paso-04-mocks/README.md) | Fixtures, contratos, mocks para desarrollo sin VPN |
| **5** | [paso-05-decisiones](./paso-05-decisiones/README.md) | ADRs, alternativas, lecciones del validator TUI |

### Referencias transversales

| Tema | Ubicación |
|------|-----------|
| macOS | [plataformas/macos.md](./plataformas/macos.md) |
| Windows (nativo, sin WSL) | [plataformas/windows.md](./plataformas/windows.md) |
| Dependencias Python | [librerias/requirements.md](./librerias/requirements.md) |
| Agentes Cursor | [agentes/README.md](./agentes/README.md) |
| Skills del proyecto | [skills/README.md](./skills/README.md) |
| Proyecto anterior (TUI + BD) | [legacy/](./legacy/) |

---

## Estructura de repo objetivo

```text
pde-desktop/
├── .cursor/
│   ├── rules/              # contextos duros (ver paso-05)
│   └── skills/             # skills de proyecto (ver skills/)
├── documentacion/          # este handoff (o docs/ en repo final)
├── core/                   # lógica sin UI
├── adapters/               # paramiko, pandas
├── ui/                     # Flet o PySide6
├── mocks/fixtures/         # datos grabados
├── tests/
├── setup.sh / run.sh       # macOS / Linux
├── setup.ps1 / run.ps1     # Windows nativo
└── requirements.txt
```

---

## Orden de lectura recomendado

1. **Paso 1** — entender visión y límites  
2. **Paso 2** — checklist funcional por fase  
3. **Paso 5** — decisiones ya tomadas y pendientes  
4. **Paso 3** — cómo construir (arquitectura + plataformas)  
5. **Paso 4** — mocks antes de pedir VPN en cada iteración  
6. **Agentes + Skills** — al abrir Cursor en el repo nuevo  

---

## Documento fuente

El handoff original vive en [`../PDE_DESKTOP_HANDOFF.txt`](../PDE_DESKTOP_HANDOFF.txt).  
Esta carpeta lo expande en guías accionables por paso.

---

## Estado del handoff

| Ítem | Estado |
|------|--------|
| Alcance funcional F01–F22 | ✅ Documentado |
| Fuera de alcance (BD) | ✅ Documentado |
| Contratos ISftpBrowser, etc. | ✅ Documentado |
| UI (Flet vs PySide6) | ⏳ Pendiente decisión |
| Empaquetado (PyInstaller vs flet build) | ⏳ Pendiente decisión |
| Código fuente | ❌ Repo nuevo por crear |
