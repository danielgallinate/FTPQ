# SFTP — Contrato (core)

Interfaces del módulo. Implementación: `adapters/paramiko_*`. Tests: `mocks/mock_*`.

---

## ISftpBrowser

```text
connect(profile: SftpProfile) -> None
disconnect() -> None
test_auth() -> Result[Ok, SftpError]
list_dir(remote_path: str) -> list[RemoteEntry]
download(remote_path: str, local_path: Path) -> None
preview(remote_path: str, max_bytes: int) -> PreviewResult
```

### RemoteEntry

```text
name: str
entry_type: "file" | "dir"
size: int
modified: datetime | None
```

### PreviewResult

```text
content: str
truncated: bool
bytes_read: int
line_count: int
```

---

## IKeyStore

```text
discover(keys_dir: Path) -> list[KeyCandidate]
fingerprint(private_key_path: Path) -> str
generate(path: Path, key_type: str, bits: int | None) -> KeyPairInfo
validate(private_key_path: Path) -> list[KeyWarning]
```

---

## Estados de sesión

```text
disconnected | connecting | connected | error
```

La UI observa estado; no gestiona socket SSH.

---

## Mock

`MockSftpBrowser` + fixtures en `mocks/fixtures/sftp/` cuando `PDE_DESKTOP_MOCK=1`.

Factory: `adapters.sftp_browser_factory.create_sftp_browser()` (UI y CLI).

Job headless: `core.sftp_job.SftpFetchJob` (`kind: sftp_fetch`) ejecutado por `sftp_jobs.runner.run_sftp_job`.
