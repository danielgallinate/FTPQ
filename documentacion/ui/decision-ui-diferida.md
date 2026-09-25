# Decisión UI diferida — toolkit vs avance

> Decisión de arquitectura UI — 2026-07-14  
> **Estado:** Aprobado para planificación. Toolkit (Slint / PySide6 / NiceGUI) **sin elegir**.

---

## Veredicto

| Pregunta | Respuesta |
|----------|-----------|
| ¿Cambiar UI después? | **Sí**, si `core/` limpio y `ui/` es capa delgada |
| ¿Avanzar SFTP/pandas antes? | **Sí** — no bloqueados por UI |
| ¿Qué decidir ya? | **Contrato visual** (wallpaper → scrim → outline mono), no la librería |

**Regla:** `ui/` importa `core`; `core/` nunca importa toolkit.

---

## Capas al cambiar toolkit

| Capa | Al cambiar Slint ↔ PySide6 ↔ NiceGUI |
|------|--------------------------------------|
| `core/`, `adapters/`, `mocks/`, tests | **Se reutiliza** |
| Tokens YAML (`ui/theme/tokens/`) | Valores iguales; cambia motor (QSS / `.slint` / CSS) |
| Wireframes U-01–U-06 | Misma funcionalidad, otro renderer |
| Carpeta `ui/` | **Reescritura** (estimado 2–4 semanas si UI delgada) |

```text
  NO se tira ──► core/ + adapters/ + tests/
  SÍ se rehace ─► ui/ (presentación)
```

---

## Anti-patterns (evitar desde el inicio)

| ❌ | Consecuencia |
|----|--------------|
| Lógica SFTP en widgets | Reescribir todo al cambiar UI |
| Tipos paramiko en `core/` | Acoplamiento |
| Tokens hardcodeados sin YAML | Rediseño manual |
| Sin `ThemeEngine` (Protocol) | Pantallas acopladas al toolkit |

---

## Qué avanzar sin elegir toolkit

### Ahora (paralelo)

| # | Entregable | Módulo |
|---|------------|--------|
| 1 | Spec SFTP cerrada | `documentacion/sftp/` |
| 2 | `core/` + mocks + tests SFTP | SFTP |
| 3 | CLI headless (`--sftp-test`, `--list`) | infra |
| 4 | Wireframes U-01–U-06 (sin código) | UI |
| 5 | Tokens mono YAML | UI — borrador en [`../../draft/diseno/`](../../draft/diseno/README.md) |

### Después SFTP core

- Spec pandas + `IFileAnalyzer` + mock — sin UI

### Recién entonces

- PoC 1 pantalla (explorador) en **un** toolkit
- Medir peso, arranque, tabla 500 filas
- ADR UI-002 con ganador

---

## Decisión visual congelada (sin toolkit)

- [x] Modelo 3 capas: wallpaper → scrim → outline
- [x] Mono B/N primero; paletas después
- [x] U-R1: UI no contiene lógica SFTP
- [ ] Wireframes U-01 conexión, U-02 explorador — ver [pantallas.md](./pantallas.md)
- [ ] `ThemeEngine` Protocol en `ui/theme/protocol.py` (sin implementación)

Detalle visual: [`../../draft/diseno/sistema-capas-wallpaper.md`](../../draft/diseno/sistema-capas-wallpaper.md)

---

## Cuándo sí elegir toolkit antes

- Demo visual al cliente en < 1 semana
- Política prohíbe PyPI beta → **PySide6 6.11.1** directo
- Un solo dev — elegir uno y no re-evaluar

Comparativa candidatos: [`../../draft/diseno/tabla-versiones-ui.md`](../../draft/diseno/tabla-versiones-ui.md)

---

## Orden recomendado

```text
Semana 1–2   SFTP core + mocks + CLI headless
Semana 2     Wireframes + tokens (decisión visual)
Semana 3     PoC 1 toolkit
Semana 3+    ADR UI-002 + ui/
```

**Bloquear elección de toolkit** solo antes de implementar masivamente `ui/widgets/` y empaquetado final.

---

## Origen

Promovido desde [`../../draft/diseno/decision-ui-diferida.md`](../../draft/diseno/decision-ui-diferida.md) (2026-07-14).
