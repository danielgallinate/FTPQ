# UI — Visión de producto

> Modelo de uso acordado — 2026-07-14  
> Referencia: PDE SFTP Validator (TUI), **más simple** y **sin BD en fase 0**.

---

## Principio central

**La aplicación siempre funciona.** Arranca completa, usable, sin red.  
Ninguna comprobación de conectividad (SFTP, VPN, BD) ocurre hasta que el usuario lo pide.

```text
Arranque ──► Pantalla inicio (logo, presentación, créditos)
                │
                ├──► Configuración (menú aparte)
                ├──► Explorador (vacío / desconectado hasta conectar)
                └──► [Usuario pulsa Conectar] ──► entonces S05, S06…
```

---

## Arranque (U-00)

| Aspecto | Comportamiento |
|---------|----------------|
| Red | **Cero** solicitudes SFTP/HTTP/BD |
| Estado sesión | `disconnected` |
| Pantalla | Inicio amigable: logo, nombre producto, versión, créditos |
| Navegación | Menús accesibles; explorador muestra estado “sin conexión” |
| Perfil | Puede cargarse desde disco (S17) **sin** abrir socket |

Inspiración: app de escritorio normal — no splash que bloquea 30s esperando VPN.

---

## Conexión bajo demanda (U-02)

| Aspecto | Comportamiento |
|---------|----------------|
| Disparador | **File → Open** (U-M01): llave, user, test, conectar |
| Secuencia | Perfil válido → `test_auth` (S05) → si OK → `list_dir` ruta inicial (S06) |
| Hilo | Worker (U-R2, R3) — UI responsive con loading |
| Éxito | Explorador pasa a mostrar carpetas/archivos |
| Fallo | Mensaje claro (timeout, auth, VPN…) → **app sigue**; sesión `error` o `disconnected` |
| Reintento | Usuario puede corregir config y volver a conectar |

**Nunca:** auto-connect al abrir app, al guardar perfil, ni al cambiar de pestaña.

---

## Área de configuración (U-01)

Menú / pantalla dedicada. Para conectar SFTP el usuario define:

| Campo | SFTP | Notas |
|-------|------|-------|
| Dónde conectarse | host, port, user | S02 |
| Llaves | `private_key_path`, `ssh_keys_dir` | S03, S04, S11 |
| Ruta inicial remota | `default_remote_path` | equiv. `DEFAULT_FOLDER` validator |
| Descargas locales | `download_dir` | S09 |
| Perfil | guardar/cargar JSON | S17 |

**Futuro (otros menús, no mezclar con SFTP v1):**

- Credenciales BD / passwords (como sección 2 del `.env` validator)
- Reglas pandas, reglas por entorno
- Cada bloque en su menú — no un formulario gigante

Validator F4 = solo sección 1 SFTP. Desktop: **misma idea**, GUI en lugar de TUI.

---

## Explorador remoto (U-P1 / U-03)

Equivalente al **browser** del validator, en el **panel navegador** del layout T invertida.

Layout completo (menú superior + T invertida) → [layout-principal.md](./layout-principal.md).

```text
┌──────────────────────────────────────────────────────────────┐
│  Menú — File · Configuración · Help                            │
├─────────────────────────────┬────────────────────────────────┤
│ P1 Navegador                │ P2 Detalle / mensajes          │
├─────────────────────────────┴────────────────────────────────┤
│ P3 Chatbot                                                   │
└──────────────────────────────────────────────────────────────┘
```

### Navegación estilo “comandos”, vía GUI

| Acción usuario | Equivalente comando | SFTP |
|----------------|---------------------|------|
| Entrar carpeta | `cd subdir` | S07 → list_dir |
| Subir nivel | `cd ..` | S07 |
| Refrescar | `ls` de nuevo | S07 |
| Ver ruta actual | `pwd` | S10 breadcrumb |

No hay terminal visible; la **metáfora** es la misma que el validator TUI (listado + enter + parent).

### Detalle y acciones

- **Siempre:** nombre, tipo, tamaño, fecha si hay
- **Archivo:** preview (S08), descargar (S09) — cuando existan en spec
- **Carpeta / archivo:** acciones extra — **fuera de alcance v1**; reservar slots en UI

---

## Comparativa Validator TUI → PDE Desktop

| Validator TUI | PDE Desktop |
|---------------|-------------|
| `./run_tui.sh` conecta al abrir | Inicio sin conexión |
| F4 config `.env` sección 1 | U-01 perfil JSON |
| Browser listado | U-03 explorador + detalle |
| F3 descarga | U-05 descarga |
| F7 scan BD↔SFTP | **No** — fuera de alcance |
| `--check` DB+SFTP al inicio | **No** — solo bajo demanda |
| Tecla K llaves (bug L-01) | U-04 llaves + S03 reconnect |
| `.env` secciones 2–3 BD | Menús futuros |

---

## Flujo de pantallas (v1)

```text
U-00 Inicio          logo, créditos, acceso menús
U-01 Configuración   perfil SFTP, llaves, rutas
U-02 Conectar        acción explícita (puede vivir en barra explorador)
U-03 Explorador      listado + detalle + breadcrumb
U-04 Llaves          discover, fingerprint, generar (S11–S14)
U-05 Preview         panel texto/CSV (S08)
U-06 Descarga        picker + progreso (S09)
```

Análisis CSV (pandas) y lote → menús/pestañas posteriores (U-07+).

---

## Errores y continuidad

| Situación | UI |
|-----------|-----|
| Timeout 30s (R4) | Toast/modal: “Tiempo agotado”; botón Cerrar; app usable |
| Auth failed | Mensaje + sugerencia (user/llave); no crash |
| Sin VPN | Mensaje tipo validator banner error |
| Desconectar | Vuelve a lista vacía; inicio/config siguen disponibles |

Ver mapeo técnico → [errores-presentacion.md](./errores-presentacion.md).

---

## Relacionado

- [pantallas.md](./pantallas.md) — wireframes por U-xx
- [funcionalidades.md](./funcionalidades.md) — catálogo U
- [restricciones.md](./restricciones.md) — U-R9 sin auto-conexión
- SFTP flujos → [`../sftp/flujos.md`](../sftp/flujos.md)
- Herencia validator → [`../sftp/herencia-validator.md`](../sftp/herencia-validator.md)
