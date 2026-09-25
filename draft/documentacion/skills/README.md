# Skills del proyecto

Skills locales en `.cursor/skills/` (copiar al repo `pde-desktop`).  
Complementan las rules con workflows ejecutables.

---

## Índice de skills

| Skill | Carpeta | Cuándo usar |
|-------|---------|-------------|
| pde-handoff | `.cursor/skills/pde-handoff/` | Inicio de sesión; orientación pasos 1–5 |
| pde-sftp-feature | `.cursor/skills/pde-sftp-feature/` | Implementar F01–F10 |
| pde-pandas-feature | `.cursor/skills/pde-pandas-feature/` | Implementar F11–F16 |
| pde-cross-platform | `.cursor/skills/pde-cross-platform/` | Scripts .sh/.ps1, build |
| pde-mock-mode | `.cursor/skills/pde-mock-mode/` | Fixtures y MockSftpBrowser |

Los borradores están en [../../.cursor/skills/](../../.cursor/skills/).

---

## Instalación

Al crear el repo:

```bash
cp -R .cursor/skills pde-desktop/.cursor/
cp -R .cursor/rules pde-desktop/.cursor/
```

---

## Convención SKILL.md

```yaml
---
name: pde-xxx
description: Use when ... (tercer persona, triggers claros)
---
```

Skills de proyecto **no** van en `~/.cursor/skills-cursor/` (reservado Cursor).

---

## Relación skills ↔ rules

| Tipo | Rol |
|------|-----|
| **Rules** (.mdc) | Restricciones duras siempre activas |
| **Skills** | Procedimientos paso a paso bajo demanda |

Ejemplo: rule prohíbe psycopg2; skill `pde-sftp-feature` describe cómo implementar F05 test_auth.
