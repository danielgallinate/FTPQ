# Windows guide — PDE SFTP Validator

How to run the validator on **Windows**. Two paths:

| Path | Recommendation | `.sh` scripts |
|------|----------------|---------------|
| **A — WSL2 + Ubuntu** | Preferred for QA | Yes (`./setup.sh`, `./run_tui.sh`) |
| **B — Native Windows** | If you cannot install WSL | No (manual `py` commands) |

Both require: **VPN**, **Python 3.11+**, a complete **`.env`**, and a **private SSH key**.

---

## Path A — WSL2 (recommended)

WSL2 is **not an emulator**: it is **real Linux** inside Windows. The project runs the same as on macOS.

### A.1 Install WSL2 (first time)

1. Open **PowerShell as Administrator** (right-click → Run as administrator).
2. Run:

```powershell
wsl --install
```

3. **Restart** Windows when prompted.
4. On return, **Ubuntu** opens and asks you to create a **Linux user** and **password** (can differ from Windows).

**Verify installation** (PowerShell or CMD):

```powershell
wsl -l -v
```

`Ubuntu` should show **VERSION 2**. If VERSION 1:

```powershell
wsl --set-default-version 2
wsl --update
```

**Install Ubuntu only** (if it did not install automatically):

```powershell
wsl --install -d Ubuntu
```

### A.2 Open the Linux terminal

- Start menu → **Ubuntu**, or
- **Windows Terminal** → new tab → **Ubuntu**

Use **Windows Terminal** (not legacy CMD) for the TUI: **F1–F8** work better.

### A.3 Packages on Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip unzip
python3 --version
```

**Python 3.11 or newer** is required. If `python3 --version` shows 3.10 or lower:

```bash
sudo apt install -y python3.12 python3.12-venv
# Use python3.12 in the following steps if needed
```

### A.4 Copy the project into WSL

**Important:** work in the Linux home (`~/`), not on `C:\` mounted as `/mnt/c/` (slower and permission issues).

```bash
mkdir -p ~/projects && cd ~/projects
```

Copy the zip from Windows:

```bash
cp /mnt/c/Users/YOUR_USER/Downloads/pde-sftp-validator-*.zip .
unzip pde-sftp-validator-*.zip -d pde-validator
cd pde-validator
```

**Alternative:** in Windows Explorer, address bar:

```text
\\wsl$\Ubuntu\home\YOUR_USER\projects
```

paste the zip there, then unzip from Ubuntu.

### A.5 Validator setup (same as Mac/Linux)

```bash
chmod +x setup.sh run.sh run_tui.sh scripts/*.sh
./setup.sh
```

Edit `.env`:

```bash
nano .env
```

Or with VS Code (from the project folder in Ubuntu):

```bash
code .
```

Complete section **1** (`CONFIG_NAME`, `SFTP_USER`, `SFTP_KEY_PATH`) and section **2** (`DB_RO_PASSWORD`).

### A.6 SSH key in WSL

The key must live **inside Linux**, not only on `C:\Users\...`:

```bash
mkdir -p ~/.ssh
cp /mnt/c/Users/YOUR_USER/Downloads/my_key_rsa ~/.ssh/
chmod 600 ~/.ssh/my_key_rsa
```

In `.env`:

```env
SFTP_KEY_PATH=~/.ssh/my_key_rsa
```

### A.7 VPN and run

1. Connect **corporate VPN on Windows** (WSL uses Windows networking).
2. In Ubuntu:

```bash
./run.sh --check
./run_tui.sh
```

### A.8 Common WSL issues

| Symptom | Fix |
|---------|-----|
| `wsl` not recognized | Enable WSL: `wsl --install` and restart |
| Python &lt; 3.11 | Install `python3.12` or upgrade Ubuntu |
| SFTP/DB timeout | VPN on Windows; from WSL `ping` the host from `.env` |
| TUI missing F-keys | Use **Windows Terminal**, not CMD |
| `Permission denied` on key | `chmod 600 ~/.ssh/your_key` |
| Slow or odd behavior | Move project from `/mnt/c/...` to `~/projects/` |

---

## Path B — Native Windows (no WSL)

If you cannot use WSL, use the native **PowerShell scripts** (`.ps1`). They are the exact equivalent of the `.sh` scripts and are the recommended native path. Running Python directly (steps B.4) still works as a fallback.

### B.0 PowerShell scripts (recommended native path)

In **PowerShell**, in the unzipped folder:

```powershell
cd C:\path\to\pde-validator
.\setup.ps1              # create venv + install deps + prepare .env
.\setup.ps1 -Dev         # also install pytest
.\run.ps1 --check        # verify connections
.\run.ps1 --export       # validation + JSON/CSV reports
.\run_tui.ps1            # Norton-style browser
```

If you see "running scripts is disabled on this system", allow them for your user only:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

The scripts auto-detect `py -3`, `python`, or `python3`. Set `$env:PYTHON` to force a specific interpreter.

### B.1 Requirements

- **Python 3.11+** from [python.org](https://www.python.org/downloads/) or Microsoft Store  
  - When installing, check **“Add python.exe to PATH”**.
- **Windows Terminal** (Microsoft Store) for the TUI.
- Corporate **VPN**.
- Optional: **OpenSSL** to decrypt `.env.enc` (or get plain `.env` over a secure channel).

### B.2 Installation

In **PowerShell** or **CMD**, in the unzipped folder:

```powershell
cd C:\path\to\pde-validator
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` with Notepad, VS Code, or `notepad .env`.

### B.3 SSH key on Windows

Store the key at, for example:

```text
C:\Users\YOUR_USER\.ssh\my_key_rsa
```

In `.env` use either:

```env
SFTP_KEY_PATH=C:\Users\YOUR_USER\.ssh\my_key_rsa
```

or:

```env
SFTP_KEY_PATH=~/.ssh/my_key_rsa
```

(Python expands `~` to your user folder.)

There is **no `chmod 600`** on Windows. Restrict file access to your user only (Properties → Security).

### B.4 Run

With venv active (`.\.venv\Scripts\activate`):

```powershell
py validate_extracts.py --check
py browse.py
```

Equivalents to `./run.sh` and `./run_tui.sh`:

```powershell
py validate_extracts.py
py validate_extracts.py --days 7
py validate_extracts.py --export
py validate_extracts.py --dry-run
```

Run the TUI in **Windows Terminal** so F1–F8 work reliably.

### B.5 Encrypted `.env` without bash

If you received `.env.enc` and have no Git Bash/WSL, with OpenSSL installed:

```powershell
openssl enc -aes-256-cbc -pbkdf2 -d -in .env.enc -out .env
```

(Prompts for the password agreed with development.)

### B.6 Native Windows limitations

| Feature | WSL2 | Native Windows |
|---------|------|----------------|
| Setup script | `./setup.sh` | `.\setup.ps1` |
| Run validation | `./run.sh` | `.\run.ps1` |
| TUI browser | `./run_tui.sh` | `.\run_tui.ps1` |
| `scripts/pde-crypto.sh` | Yes | Manual OpenSSL or WSL |
| TUI restart on F4 Save | Yes | Yes (`browse.py` restarts the process) |
| Discover keys in `~/.ssh` | Yes | Yes (`C:\Users\...\.ssh`) |

---

## Quick summary

**WSL2 (recommended):**

```text
PowerShell (admin) → wsl --install → restart → Ubuntu
→ copy zip to ~/projects → ./setup.sh → edit .env
→ VPN → ./run_tui.sh
```

**Native Windows:**

```text
Install Python 3.11+ → venv + pip install
→ copy .env.example .env → edit → VPN
→ py validate_extracts.py --check → py browse.py
```

---

## More documentation

- General QA checklist: `docs/QA_HANDOFF.md`
- Config screen (F4): `docs/CONFIG_SCREEN.md`
- README: `README.md`
