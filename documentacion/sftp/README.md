# Módulo SFTP

Conexión SSH/SFTP, llaves, exploración remota, preview y descarga.  
**Solo este dominio.** UI: ver [`../ui/`](../ui/). Análisis CSV: ver [`../pandas/`](../pandas/).

---

## Documentos

| Archivo | Contenido |
|---------|-----------|
| [funcionalidades.md](./funcionalidades.md) | Catálogo **S01–S19** |
| [adr/0001-sftp-job-headless.md](./adr/0001-sftp-job-headless.md) | Job CLI headless (S18/S19) |
| [restricciones.md](./restricciones.md) | Reglas **R1–R27** |
| [fuera-de-alcance.md](./fuera-de-alcance.md) | Qué no hace SFTP |
| [contexto-pde.md](./contexto-pde.md) | Rutas AWS Transfer, campos perfil |
| [herencia-validator.md](./herencia-validator.md) | Qué reutilizamos del TUI |
| [flujos.md](./flujos.md) | Flujos de comportamiento (sin wireframes) |
| [errores.md](./errores.md) | Errores técnicos y causas |
| [contrato.md](./contrato.md) | `ISftpBrowser`, `IKeyStore` |
| [criterios-exito.md](./criterios-exito.md) | Checklist cierre módulo |
| [schema-perfil.draft.json](./schema-perfil.draft.json) | JSON schema sección `sftp` |

## Skills (agentes)

| Rol | Carpeta | Contexto |
|-----|---------|----------|
| **Todos** | [`../../skills/sftp/reference.md`](../../skills/sftp/reference.md) | S, R, contrato, PDE |
| Dev | [`../../skills/sftp/dev/`](../../skills/sftp/dev/SKILL.md) | `@sftp-dev` |
| QA | [`../../skills/sftp/qa/`](../../skills/sftp/qa/SKILL.md) | `@sftp-qa` |
| Peer review | [`../../skills/sftp/peer-review/`](../../skills/sftp/peer-review/SKILL.md) | `@sftp-peer-review` |

---

## IDs de referencia

Prefijo **S** = SFTP (issues, tests, mocks).

---

## Implementación en código

| Capa | Carpeta repo |
|------|--------------|
| Contratos | `core/` |
| paramiko | `adapters/` |
| Factory mock/real | `adapters/sftp_browser_factory.py` |
| Job CLI | `sftp_jobs/` · `./scripts/run_sftp_job.sh` |
| Pantallas | `ui/` (consume contratos; no lógica SFTP aquí) |
