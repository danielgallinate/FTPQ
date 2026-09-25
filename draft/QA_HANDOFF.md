# QA handoff — PDE SFTP Validator

One-page checklist to receive, configure, and validate the portable package.

---

## What you receive

| Delivery | Contents | Channel |
|----------|----------|---------|
| **Package A** | `pde-sftp-validator-<version>-qa-<date>.zip` | Email / Drive / CI artifact |
| **Package B** | `DB_RO_PASSWORD`, private SSH key, `CONFIG_NAME` | 1Password / secure channel (never in the zip) |
| **Optional** | `.env.enc` + decryption password | Same secure channel |

The zip does **not** include `.env`, `.venv`, reports, or SSH keys.

---

## Machine requirements

- **macOS, Linux, or Windows** (see `docs/WINDOWS.md`)
- **Python 3.11+** (on Windows: WSL2 recommended, or native Python)
- Corporate **VPN** (RDS + SFTP nonprod)
- Your IP on AWS Transfer Family whitelist (ask infra if SFTP fails)
- **OpenSSL** (only if using `.env.enc`: `scripts/pde-crypto.sh` or OpenSSL on Windows)

### Using Windows?

| Option | Manual |
|--------|--------|
| **WSL2 + Ubuntu** (recommended) | `docs/WINDOWS.md` → Path A |
| **Native Windows** (no WSL) | `docs/WINDOWS.md` → Path B |

---

## Installation (5 minutes)

```bash
unzip pde-sftp-validator-*.zip -d pde-validator
cd pde-validator

chmod +x setup.sh run.sh run_tui.sh scripts/*.sh
./setup.sh
```

If you received `.env.enc`:

```bash
./scripts/pde-crypto.sh decrypt .env.enc
chmod 600 .env
```

Otherwise, edit `.env` manually:

| Section | What to complete |
|---------|------------------|
| **1. YOUR CONFIG** | `CONFIG_NAME`, `SFTP_USER` (same as name), `SFTP_KEY_PATH`, `DEFAULT_FOLDER` |
| **2. DATABASE** | `DB_RO_PASSWORD` (ask the team) |

Place the SSH key in `~/.ssh/` and:

```bash
chmod 600 ~/.ssh/your_key_rsa
```

---

## Verification

```bash
./run.sh --check          # DB + SFTP without downloading CSV
./scripts/test-sftp-login.sh   # SFTP login only
```

If `--check` fails:

| Error | Action |
|-------|--------|
| DB connection | VPN, password, host |
| SFTP auth | Correct key, user = CONFIG_NAME, IP whitelist |
| `Error reading SSH protocol banner` | VPN; IP whitelist on Transfer Family; retry (30s timeout). Do not pause in debugger on `connect()` |
| Key not found | Path in `SFTP_KEY_PATH` and mode 600 |

---

## Validation scope (important)

The tool compares **`extract_path` in the DB log** to the **file on SFTP**. It does **not** apply
business routing rules (scheduled vs requested from filename, hour, or `extract_type`).

| DB field | Role |
|----------|------|
| `extract_path` | **Authoritative** SFTP location (`{folder}/{filename}`) |
| `delivery_folder` | Display only in F2 (not pass/fail) |
| `extract_type` | Display only (`full` / `incremental` — Snowflake pull semantics) |

If log and SFTP agree on path, size, and status → **OK**, even when `delivery_folder` differs from
the folder in `extract_path`.

### F7 statuses

| Status | Meaning |
|--------|---------|
| **OK** | SFTP file matches its log |
| **FAIL** | Log vs SFTP mismatch |
| **ORPHAN** | SFTP file with no matching log |
| **GHOST** | Log in window with no file at `extract_path` on SFTP |

## Daily use

### TUI (recommended)

```bash
./run_tui.sh
```

| Key | Action |
|-----|--------|
| **F4** | Edit config (section 1 of `.env`) — restarts TUI on Save |
| **F5** | Restore section 1 of `.env` to **`./run_tui.sh` startup** and restart TUI (rescue; see `docs/CONFIG_SCREEN.md` §1.1) |
| **F2** | Analyze selected file |
| **F7** | Bidirectional global summary (SFTP ↔ DB): OK / FAIL / ORPHAN / GHOST |
| **F6** | Export analysis to `export/*.txt` |
| **F8** | Exit |

Full manual: `docs/CONFIG_SCREEN.md`

### CLI (batch / manual CI)

```bash
./run.sh                  # validate last 30 days (console)
./run.sh --days 7
./run.sh --export         # JSON + CSV in export/
./run.sh --dry-run        # metadata only, no CSV download
```

---

## Local folders (created automatically)

| Folder | Use |
|--------|-----|
| `downloads/` | F3 downloads in TUI |
| `export/` | `.txt` reports (TUI F6) and `.json`/`.csv` (CLI `--export`) |
| `tmp/validation/` | Temporary CSVs during validation |

---

## Encrypting `.env` (development → QA)

On the development machine:

```bash
./scripts/pde-crypto.sh encrypt .env
# Send .env.enc over secure channel; password via another channel
```

On QA:

```bash
./scripts/pde-crypto.sh decrypt .env.enc
chmod 600 .env
```

---

## Support

- Main README: `README.md`
- **Windows (WSL2 or native):** `docs/WINDOWS.md`
- TUI config (F4): `docs/CONFIG_SCREEN.md`
- Project tests: `./setup.sh --dev && pytest -q`
