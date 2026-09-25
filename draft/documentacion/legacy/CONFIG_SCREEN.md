# Manual — Configuration screen (F4)

Guide for QA and development of the PDE SFTP validator. Explains each editable field in the TUI,
what happens when you change it, and how to obtain the correct value.

---

## 1. Open and save

| Action | Key / control | Effect |
|--------|---------------|--------|
| Open editor | **F4** (from browser) | Modal "CONFIG (section 1 — your settings)" |
| Restore startup backup | **F5** | See **§1.1** (different behavior inside F4 modal vs browser) |
| Save | **Save** button | Writes **section 1** only to `.env`; restarts the TUI |
| Cancel | **Esc** or **Cancel** | Closes without saving |
| Error after save | Red config screen | Missing required value or SSH key does not exist |

**File edited:** `.env` at the project root (path shown on screen).

**Important:** F4 does **not** edit the database password or `SFTP_HOST`. Those live in sections 2 and 3 of `.env` (see §6).

---

## 1.1 F5 Restore — what it does and why it appears on several screens

**F5** is the **rescue** key: return to the configuration from when you **started** `./run_tui.sh` in this session, without hand-editing `.env` or restarting the terminal.

### What gets restored?

Only **section 1** of `.env` (F4 fields):

`CONFIG_NAME`, `CONFIG_ID`, `SFTP_USER`, `SFTP_KEY_PATH`, `DEFAULT_FOLDER`, `LOOKBACK_DAYS`, `FILE_NAME`

Does **not** change section 2 (DB password), `SFTP_HOST`, or export paths.

### What is the “startup backup”?

When you run `./run_tui.sh`, the app saves a copy of section 1 to `.env.tui_session` (local file, not included in the QA zip).

- That snapshot is **F5’s reference point** for the whole session.
- If you save another config with **F4 → Save** and the TUI restarts, **F5 still points to the original** `./run_tui.sh` startup, not the last Save.
- On **F8** exit, `.env.tui_session` is removed; the next `./run_tui.sh` creates a new backup.

**Example:** you start with `config3`, switch to `config5` via F4 Save by mistake → **F5** returns to `config3` and restarts the TUI.

### Two F5 behaviors (important)

| Where you press F5 | What it does |
|--------------------|--------------|
| **Browser** or **config error screen** | Writes startup backup to `.env` and **restarts the TUI** (session-wide “undo”) |
| **Inside F4 modal** (before Save) | Only **resets form fields** to backup; does **not** touch `.env` until Save |

In the F4 modal, F5 cancels edits you were typing. From the browser, F5 is the definitive on-disk undo.

### Why F5 appears on several screens

**Norton Commander** style: **global** actions (F4 Config, **F5 Restore**, F6 Export, F8 Exit) are available on main screens so you are not stuck when something goes wrong:

| Screen | F5 in footer | Reason |
|--------|--------------|--------|
| **Browser** (SFTP listing) | Yes | Return to startup config if you changed config and see the wrong folder |
| **Configuration error** | Yes | If `.env` is invalid, F5 restores backup without manual editing |
| **F2 analysis / F7 summary / scan in progress** | No | Temporary screens; **Esc** returns to browser where F5 is available |
| **Help / quit confirm** | No | Short modals; close with Esc or F8 |

From the normal flow or a config error, you can always **F5 → return to session start state**.

### When to use F5

| Situation | Use F5? |
|-----------|---------|
| You saved wrong config in F4 | Yes (from browser) |
| You are typing wrong values in F4 and have not saved | Yes (in modal; or Esc/Cancel) |
| You want to undo the **last** Save but keep startup | No — F5 goes to **startup**, not previous Save |
| You changed `DB_RO_PASSWORD` manually in `.env` | F5 does **not** restore it (not section 1) |

---

## 2. F4 screen fields

### CONFIG_NAME

| | |
|---|---|
| **What it is** | Logical PDE configuration name in PostgreSQL (`config.config_name`). |
| **Example** | `Daniel_test_config3` |
| **When changed** | App looks up another config in DB; default SFTP user, `config/<name>/…` paths, and browser listings change. |
| **How to obtain** | 1) Ask DEA/PDE for the config name to audit.<br>2) Or query DB (with VPN):<br>`SELECT config_id, config_name FROM config ORDER BY config_name;`<br>3) Usually matches the folder name under `config/` on SFTP. |

---

### SFTP_USER

| | |
|---|---|
| **What it is** | AWS Transfer Family username for SSH key authentication. |
| **Example** | `Daniel_test_config3` (usually **same** as `CONFIG_NAME`) |
| **When changed** | Changes SFTP login identity. If it does not match the provisioned user, connection fails (permission denied). |
| **How to obtain** | 1) In most nonprod environments: **same value as `CONFIG_NAME`**.<br>2) Confirm with infra/DEA the Transfer Family user for that config.<br>3) If empty in `.env`, the validator uses `CONFIG_NAME` automatically. |

---

### SFTP_KEY_PATH

| | |
|---|---|
| **What it is** | Local path to the **private** SSH key for SFTP (not the public key). |
| **Example** | `~/.ssh/pde_daniel_test_config_dea8594_rsa` |
| **When changed** | App tries another key. If the file does not exist → error on save or when listing SFTP. |
| **How to obtain** | 1) When the test config is created, DEA/infra generates a key pair and delivers the **private** key (`.pem` or no extension).<br>2) Store it in `~/.ssh/` with a descriptive name.<br>3) Required permissions: `chmod 600 ~/.ssh/your_key_rsa`<br>4) Path supports `~` (user home). |

---

### DEFAULT_FOLDER

| | |
|---|---|
| **What it is** | Initial browser folder under `config/<CONFIG_NAME>/` (`scheduled` or `requested`). |
| **Values** | `scheduled` or `requested` |
| **When changed** | TUI opens the other folder first; **F7 always scans both** `scheduled/` and `requested/`. |
| **How to obtain** | Pick the folder you browse most often. **Pass/fail does not use this field** — validation uses `extract_path` from each log row. |

**Note:** `delivery_folder` in DB may differ from the folder in `extract_path`. The validator
follows **`extract_path` only** (log location vs SFTP file). No business swap detection.

---

### CONFIG_ID

| | |
|---|---|
| **What it is** | Internal UUID/hash of the `config` row in PostgreSQL. Filters `extract_history` queries. |
| **Example** | `44891f3d72d4463ab12a8d8c5` |
| **When changed** | If wrong, logs are missing or data from another config is mixed in. If **empty**, the validator resolves ID from `CONFIG_NAME`. |
| **How to obtain** | 1) **Recommended:** leave empty and use only `CONFIG_NAME`.<br>2) SQL (VPN):<br>`SELECT config_id, config_name FROM config WHERE config_name = 'Daniel_test_config3';`<br>3) Copy `config_id` if you want to pin it explicitly (useful if configs were renamed). |

---

### LOOKBACK_DAYS

| | |
|---|---|
| **What it is** | Time window (days) to list and validate extracts: last N days from today. |
| **Range** | **1–30** (out-of-range values are clamped automatically). |
| **Default** | `30` |
| **When changed** | Fewer days → fewer files in F7 and `./run.sh`; more days → more DB records and longer scan. |
| **How to obtain** | Choose for your audit: `7` for one week, `30` for the usual month. No external data required. |

---

### FILE_NAME (`.env` only, not shown in F4)

| | |
|---|---|
| **What it is** | Optional filter to validate **one** file (name fragment). |
| **Example** | `PDE Clinic` or `Daniel_test_config3_PDE Clinic_20260703_051019.csv` |
| **When set** | **Ignores** `LOOKBACK_DAYS`; F2/F7 and CLI search only that file. |
| **How to obtain** | Exact or partial CSV name on SFTP or in `extract_path` in `extract_history`. |
| **Editing** | Edit `.env` manually in section 1, or leave empty: `FILE_NAME=` |

---

## 3. `.env` sections F4 does not edit

Complete these **once** (or get values from your team):

### Section 2 — Database

| Variable | How to obtain |
|----------|---------------|
| `DB_HOST` | RDS host for the environment (in `.env.example` for dev). |
| `DB_PORT` | Usually `5432`. |
| `DB_NAME` | Database name (`premium_data_extracts_dev`, etc.). |
| `DB_RO_USER` | Read-only user (`premium_data_extracts_ro`). |
| `DB_RO_PASSWORD` | **Secret:** ask the team; not included in the QA zip. |
| `DB_SSLMODE` | `require` on RDS. |

**Requirement:** VPN connected to reach RDS.

### Section 3 — SFTP

| Variable | How to obtain |
|----------|---------------|
| `SFTP_HOST` | AWS Transfer Family endpoint (e.g. `s-….server.transfer.us-west-2.amazonaws.com`). Shared in nonprod; in `.env.example`. |

### Section 4 — Local options

| Variable | Default | Use |
|----------|---------|-----|
| `DOWNLOAD_DIR` | `./downloads` | F3 saves permanent downloads here. |
| `EXPORT_DIR` | `./export` | F6 exports `.txt` reports here. |

---

## 4. Recommended first-time flow

```text
1. ./setup.sh                    → creates .venv and .env from .env.example
2. Edit section 2 (DB_RO_PASSWORD) in .env
3. Copy SSH key → ~/.ssh/        → chmod 600
4. F4 in TUI                     → CONFIG_NAME, SFTP_USER, SFTP_KEY_PATH, DEFAULT_FOLDER
5. ./run.sh --check              → test DB + SFTP without downloading CSV
6. ./run_tui.sh                  → browse and validate
```

---

## 5. Protecting and encrypting `.env`

`.env` contains secrets (`DB_RO_PASSWORD`, key paths). **Never** commit it to git (already in `.gitignore`).

### Minimum measures

```bash
chmod 600 .env
chmod 600 ~/.ssh/your_key_rsa
```

### Encrypt `.env` for sharing or archiving

Use the included script (OpenSSL AES-256-CBC + PBKDF2):

```bash
# Encrypt (prompts for password twice)
./scripts/pde-crypto.sh encrypt .env

# Creates: .env.enc — send only that file over a secure channel
```

```bash
# Decrypt before using the tool
./scripts/pde-crypto.sh decrypt .env.enc

# Creates: .env (overwrites if present; back up first)
```

**Password:** agree one with the team (password manager, 1Password, etc.). Without it, `.enc` cannot be recovered.

### Encrypt this manual

```bash
./scripts/pde-crypto.sh encrypt docs/CONFIG_SCREEN.md
# → docs/CONFIG_SCREEN.md.enc
```

```bash
./scripts/pde-crypto.sh decrypt docs/CONFIG_SCREEN.md.enc
```

---

## 6. Quick summary — effect of each change

| Field | If wrong… | If correct… |
|-------|-----------|-------------|
| `CONFIG_NAME` | No data or wrong config | Your PDE tenant listings and validations |
| `SFTP_USER` | SFTP auth error | Connection to correct bucket/folder |
| `SFTP_KEY_PATH` | "Private key not found" | SFTP login with your key |
| `DEFAULT_FOLDER` | Wrong folder on open | Direct entry to scheduled or requested |
| `CONFIG_ID` | Empty or wrong DB queries | (Optional) Explicit filter by ID |
| `LOOKBACK_DAYS` | Too many/few files in scan | Window matching your audit |
| `FILE_NAME` | — | Single-file mode |

---

## 7. Verification after save (F4)

1. The TUI **restarts automatically** (new process with updated config).
2. SFTP browser loads with the new `CONFIG_NAME` in the title bar.
3. If it fails before restart: error screen (`Missing required configuration`, `Private key not found`, etc.).
4. **F5** restores the session-start snapshot if you saved something wrong (also restarts).

**Windows:** on WSL2 use `./run_tui.sh`; on native Windows use `py browse.py` (see `docs/WINDOWS.md`).

---

## 8. Typical contacts for values

| You need | Who / where |
|----------|-------------|
| `CONFIG_NAME`, test scope | DEA team / extract owner |
| SSH key + `SFTP_USER` | Infra / Transfer Family provisioning |
| `DB_RO_PASSWORD` | Backend team or PDE monorepo secret |
| `SFTP_HOST`, `DB_HOST` | `.env.example` or nonprod environment docs |
| VPN | IT / corporate network access |

---

## 9. F7 global scan (bidirectional)

**F7** runs a two-phase scan over `scheduled/` and `requested/` for the current `CONFIG_NAME` and
`LOOKBACK_DAYS` (or `FILE_NAME` filter).

| Phase | Direction | Result statuses |
|-------|-----------|-----------------|
| 1 | SFTP → DB | **OK**, **FAIL**, **ORPHAN** |
| 2 | DB → SFTP | **GHOST** (logs with no file at `extract_path`) |

| Status | Meaning |
|--------|---------|
| **OK** | File on SFTP matches log (`extract_path`, size, generation status) |
| **FAIL** | Mismatch (missing file, wrong path, size, etc.) |
| **ORPHAN** | File on SFTP with no matching `extract_history` row |
| **GHOST** | Log in the time window but no file at `extract_path` on SFTP |

Exported reports (**F6**) include a **Validation scope** footer. The tool does not infer scheduled
vs requested from filenames or `delivery_folder`.

---

*Manual version: 0.6.3 — TUI F4–F8; validation uses `extract_path` only. Windows: `docs/WINDOWS.md`.*
