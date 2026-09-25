# PDE SFTP Validator — macOS (legacy)

Flujo del **validator TUI** en macOS/Linux. Para PDE Desktop GUI ver [../plataformas/macos.md](../plataformas/macos.md).

## Setup validator

```bash
chmod +x setup.sh run.sh run_tui.sh scripts/*.sh
./setup.sh
./setup.sh --dev && pytest -q
```

## Uso diario TUI

```bash
./run_tui.sh
# F4 config, F7 scan SFTP↔DB, F8 exit
```

## Check conexiones

```bash
./run.sh --check          # DB + SFTP
./scripts/test-sftp-login.sh
```

Documentación completa: [QA_HANDOFF.md](./QA_HANDOFF.md), [CONFIG_SCREEN.md](./CONFIG_SCREEN.md).
