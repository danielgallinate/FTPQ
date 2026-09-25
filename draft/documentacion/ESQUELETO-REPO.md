# Esqueleto repo — checklist de scaffolding

Usar al crear el repo `pde-desktop` desde este handoff.

## Fase scaffolding (sin features aún)

```text
[ ] Crear repo git vacío pde-desktop
[ ] Copiar documentacion/ + .cursor/ + mocks/fixtures/ + AGENTS.md
[ ] Copiar PDE_DESKTOP_HANDOFF.txt a docs/ o documentacion/
[ ] requirements.txt según librerias/requirements.md
[ ] .gitignore: .venv, downloads/, tmp/, .env, *.pem, dist/
[ ] core/__init__.py + stubs de contratos (Protocol)
[ ] mocks/mock_sftp_browser.py (stub)
[ ] setup.sh / setup.ps1 (venv + pip)
[ ] run.sh / run.ps1 (placeholder UI)
[ ] pytest smoke test imports core
```

## Fase 0 — SFTP

```text
[ ] adapters/paramiko_sftp.py
[ ] ui mínima: perfil + explorer + test conexión
[ ] F03 selector llave funcional
[ ] fixtures SFTP en tests
```

## Fase 1 — pandas

```text
[ ] adapters/pandas_analyzer.py
[ ] UI pestaña análisis
[ ] jsonschema perfiles (opcional)
```

## Fase 2 — entrega QA

```text
[ ] Lote F16
[ ] PyInstaller build Mac + Win
[ ] README QA one-pager
```

## Comandos placeholder (crear en repo)

Los scripts `setup.sh`, `run.sh`, etc. **aún no existen** en este handoff workspace; crearlos al iniciar implementación siguiendo `documentacion/plataformas/`.
