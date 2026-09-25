# Paso 4 — Mocks y fixtures

Desarrollo y tests **sin VPN** usando contratos + datos grabados.

---

## Por qué mocks primero

| Problema | Solución mock |
|----------|---------------|
| VPN no siempre disponible | `MockSftpBrowser` con JSON fijo |
| SFTP lento en CI | Fixtures de listados pre-grabados |
| QA sin credenciales | Perfil ejemplo + CSV sample |
| Agente Cursor alucina APIs | Contratos en `core/` + implementaciones Mock* |

---

## Contratos (interfaces)

Separar **siempre** core de adapters:

### ISftpBrowser

```python
connect(profile) / disconnect()
test_auth() -> ok | error
list_dir(path) -> entries[]
download(remote, local_path)
preview(remote, max_bytes) -> text
```

### IKeyStore

```python
discover(keys_dir) -> paths[]
generate(path, key_type, bits?) -> (public_path, fingerprint)
fingerprint(path) -> str
```

### IProfileStore

```python
load(profile_id) / save(profile)
list_profiles()
```

### IFileAnalyzer

```python
analyze(csv_path, rules) -> AnalysisReport
analyze_batch(paths[], rules) -> BatchReport
```

**Implementaciones:**

| Prefijo | Uso |
|---------|-----|
| `Real*` | Producción (paramiko, pandas) |
| `Mock*` | Tests unitarios |
| `Fixture*` | JSON/CSV en disco |

---

## Layout de fixtures

```text
mocks/
├── mock_sftp_browser.py
├── mock_key_store.py
├── mock_profile_store.py
└── fixtures/
    ├── sftp/
    │   ├── listing_root.json
    │   ├── listing_scheduled.json
    │   └── listing_requested.json
    ├── csv/
    │   ├── sample_valid.csv
    │   ├── sample_duplicates.csv
    │   └── sample_missing_columns.csv
    └── profiles/
        └── example_profile.json
```

---

## Cómo grabar fixtures desde SFTP real

Cuando tengas VPN (una vez):

1. Conectar con perfil real  
2. Ejecutar script `scripts/record_sftp_listing.py` (por crear) → JSON  
3. Commitear JSON **sin** rutas con secretos ni nombres de cliente sensibles  
4. Anonimizar host/usuario en perfiles de ejemplo  

---

## Perfil de ejemplo (`fixtures/profiles/example_profile.json`)

```json
{
  "profile_id": "example_config",
  "sftp": {
    "host": "s-example.server.transfer.us-west-2.amazonaws.com",
    "port": 22,
    "user": "example_user",
    "private_key_path": "~/.ssh/example_key_rsa",
    "ssh_keys_dir": "~/.ssh",
    "default_remote_path": "config/example_config/scheduled",
    "download_dir": "./downloads"
  },
  "pandas_rules": {
    "delimiter": "\t",
    "required_columns": ["id", "name", "updated_at"],
    "optional_columns": ["notes"],
    "metadata": {
      "clinic_name": "Example Clinic",
      "datasource": "example_ds"
    },
    "preview_max_bytes": 524288,
    "preview_max_lines": 500,
    "warn_file_size_mb": 50
  }
}
```

---

## Listado SFTP de ejemplo (`fixtures/sftp/listing_scheduled.json`)

```json
{
  "path": "config/example_config/scheduled",
  "entries": [
    {"name": "..", "type": "dir", "size": 0},
    {"name": "example_extract_20260701.csv", "type": "file", "size": 1048576},
    {"name": "example_extract_20260702.csv", "type": "file", "size": 2097152}
  ]
}
```

---

## Modo mock en la app

Variable de entorno o flag dev:

```bash
PDE_DESKTOP_MOCK=1 ./run.sh
```

```powershell
$env:PDE_DESKTOP_MOCK=1; .\run.ps1
```

Cuando `PDE_DESKTOP_MOCK=1`:

- Inyectar `MockSftpBrowser` en lugar de `ParamikoSftpBrowser`  
- `test_auth()` siempre OK  
- Listados desde `fixtures/sftp/*.json`  

---

## Tests mínimos con mocks

| Test | Fixture |
|------|---------|
| Listar directorio | `listing_scheduled.json` |
| Preview truncado | CSV sample + límite bytes |
| Reglas pandas columnas faltantes | `sample_missing_columns.csv` |
| Duplicados detectados | `sample_duplicates.csv` |
| Perfil inválido | JSON malformado → error claro |

---

## Checklist paso 4

- [ ] Contratos definidos en `core/` antes de UI  
- [ ] `MockSftpBrowser` pasa mismos tests que contrato documentado  
- [ ] Al menos 1 CSV y 1 perfil en fixtures  
- [ ] Modo mock documentado en README y run scripts  

**Anterior:** [Paso 3](../paso-03-infraestructura/README.md) · **Siguiente:** [Paso 5 — Decisiones](../paso-05-decisiones/README.md)
