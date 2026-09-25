# UI — Pantallas (wireframes)

Inventario alineado con [vision-producto.md](./vision-producto.md).

---

## U-00 — Inicio

**Invoca:** —  
**Objetivo:** Pantalla de bienvenida; app usable sin red.

**Componentes:**
- Logo / nombre PDE Desktop
- Versión build
- Créditos / presentación breve
- Accesos: Configuración, Explorador, (futuro: Análisis)

**Estados:** siempre `idle` — no loading de red

**Notas:** No llamar S05 ni S06 aquí. U-R9.

---

## U-01 — Configuración SFTP

**Invoca:** S17, S02–S04  
**Objetivo:** Dónde conectarse, llaves, rutas — sin abrir socket al guardar.

**Componentes:**
- host, port, user
- Selector llave + `ssh_keys_dir`
- `default_remote_path`, `download_dir`
- Guardar / cargar perfil JSON
- Enlace a U-04 (llaves)

**Estados:** idle | saving | saved | validation_error (campos locales)

**Notas:** Guardar perfil ≠ conectar. Conexión solo vía U-02.

---

## U-02 — Conectar / Desconectar

**Invoca:** S05, S01, S06  
**Objetivo:** Único disparador de red SFTP en flujo normal.

**Componentes:**
- Botón Conectar (explorador o barra global)
- Botón Desconectar
- Indicador sesión: desconectado | conectando | conectado | error

**Estados:** disconnected | connecting | connected | error

**Error:** modal/toast legible; al cerrar → app continúa (U-R10)

**Notas:** Tras OK → U-03 lista `default_remote_path`.

---

## U-03 — Explorador remoto (= U-P1)

**Invoca:** S06–S07, S10  
**Objetivo:** Browser validator — panel **arriba izquierda** del [layout T](./layout-principal.md).

**Componentes:**
- Breadcrumb (S10)
- Lista: dirs primero, files después (convención validator)
- Acciones: entrar, `..`, refrescar
- Slots reservados U-09 (acciones extra — futuro)

**Estados:**
- **disconnected:** mensaje “Conecte para explorar” + lista vacía
- **connected:** listado activo
- **loading:** spinner en lista
- **error:** banner en **U-P2** + retry

**Notas:** Selección en P1 → detalle en **U-P2**. Conectar: **File → Open** (U-M01).

---

## U-P2 — Detalle / mensajes / contenido

**Invoca:** S08 (preview opcional), presentación errores  
**Objetivo:** Panel **arriba derecha** — contexto del ítem y feedback.

**Secciones:** detalle metadata | mensajes sistema | preview contenido (futuro / opcional)

---

## U-P3 — Chatbot

**Invoca:** [asistente-metadata.md](./asistente-metadata.md)  
**Objetivo:** Panel **inferior ancho completo** (T invertida).

---

## U-SB — Menú superior (chrome)

**Invoca:** U-M01…U-M05  
**Objetivo:** Barra superior clásica. Spec completa → [menu.md](./menu.md).

```text
File          → Open …
Configuración → Llaves · Rutas · Otros (futuro BD)
Help          → Who is …
```

**Notas:** Conexión solo vía **File → Open** (U-M01). Config guardar rutas ≠ conectar (U-R9).

---

## U-03 legacy note

U-03 = capacidad explorador; **U-P1** = región visual en layout. Misma funcionalidad.

---

## U-M01 — File → Open

**Invoca:** S03, S05, S01, S06, S11–S13  
**Objetivo:** Asistente conexión — elegir llave, user, test, conectar.

Ver [menu.md](./menu.md).

---

## U-04 — Llaves SSH (= Configuración → Llaves)

**Invoca:** S03, S11–S14  
**Objetivo:** Discover, fingerprint, generar par; cambio llave → reconnect (S03).

*(Acceso: **Configuración → Llaves**. Generar y ver llaves; no conectar aquí.)*

---

## U-05 — Preview

**Invoca:** S08  
**Objetivo:** Texto/CSV truncado según R12.

---

## U-06 — Descarga

**Invoca:** S09  
**Objetivo:** File picker local + progreso.

---

## Lista planificada (resumen)

| ID | Pantalla | SFTP | Estado wireframe |
|----|----------|------|------------------|
| U-00 | Inicio | — | ✅ descrito |
| U-01 | Configuración | S02–S04, S17 | ✅ descrito |
| U-02 | Conectar | S05, S06 | ✅ descrito |
| U-03 / U-P1 | Explorador / navegador | S06–S10 | ✅ layout T |
| U-P2 | Detalle / mensajes | S08, errores | ✅ layout T |
| U-P3 | Chatbot | metadata | ✅ layout T |
| U-SB | Menú superior | U-01, U-02 | ✅ layout T |
| U-04 | Llaves | S11–S14 | esqueleto |
| U-05 | Preview | S08 | pendiente |
| U-06 | Descarga | S09 | pendiente |
| U-07 | Análisis CSV | Pxx | futuro |

---

## Plantilla (pantallas nuevas)

```markdown
## U-XXX — Nombre

**Invoca:** Sxx
**Objetivo:**
**Componentes:**
**Estados:** idle | loading | success | error | empty | disconnected
**Notas:**
```
