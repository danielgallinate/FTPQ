# SFTP — Flujos de comportamiento

Secuencias del **módulo SFTP** (sin layout de pantalla). Wireframes → [`../ui/`](../ui/).

**Regla app:** conexión solo bajo demanda del usuario (U-R9). El módulo SFTP no auto-conecta; la UI invoca `connect` / `test_auth` explícitamente.

---

## Arranque de aplicación

```text
1. App inicia → estado sesión: disconnected
2. Cargar perfil desde disco (S17) — opcional, sin socket
3. NO test_auth, NO list_dir, NO ping de red
4. Explorador vacío hasta que usuario dispare conexión (U-02)
```

---

## Conexión (usuario solicita)

```text
1. Usuario pulsa Conectar (U-02)
2. Validar perfil en memoria (S02, S03, S13 local)
3. connect(profile) + test_auth (S05) en worker (R3)
4. Si OK → list_dir(default_remote_path) (S06)
5. Si error (timeout R4, auth, VPN…) → estado error/disconnected;
   propagar SftpError a UI; app sigue (U-R10)
```

---

## Primera conexión (detalle técnico)

```text
1. Perfil (S17) con host, user, key path
2. Opcional: discover llaves (S11) y seleccionar (S03) — en config, antes de conectar
3. test_auth (S05) — solo cuando usuario conecta
4. Si OK → list_dir(default_remote_path) (S06)
5. Si error → propagar SftpError (ver errores.md)
```

---

## Navegación

```text
list_dir(path) → S06
  → entrar subcarpeta: list_dir(child) → S07
  → parent: list_dir("..") → S07
  → refresh: list_dir(current) → S07
```

---

## Archivo seleccionado

```text
preview(path) → S08  (si tipo soportado y bajo límite)
download(path, local) → S09
```

---

## Cambio de llave o perfil

```text
1. disconnect()
2. Actualizar config en memoria
3. connect(nuevo perfil) o test_auth + list_dir
```

**R2:** obligatorio disconnect antes de reconectar.
