# UI — Layout principal (T invertida)

> Shell de trabajo post-inicio — 2026-07-14  
> Pantalla inicio U-00 → transición a este layout. Ver [vision-producto.md](./vision-producto.md).

---

## Vista general

**T invertida** + **menú superior clásico** (desacoplado, U-R14):

```text
┌──────────────────────────────────────────────────────────────┐
│  MENÚ (U-SB) — Archivo · Conexión · Config · Llaves · Ayuda  │
├─────────────────────────────┬────────────────────────────────┤
│  PANEL 1                    │  PANEL 2                         │
│  Navegador                  │  Detalles / mensajes / contenido │
│  (explorador SFTP)          │                                  │
├─────────────────────────────┴────────────────────────────────┤
│  PANEL 3 — Chatbot / asistente (ancho completo)              │
└──────────────────────────────────────────────────────────────┘
```

- **Arriba (fuera del T):** barra de menú horizontal — estilo app de escritorio clásica.
- **Centro:** dos columnas (P1 | P2).
- **Abajo:** chatbot ancho completo bajo P1+P2.
- Menú **desacoplado:** default `top`; alternativas `left` / `right` / `bottom` vía preferencia.

---

## Paneles

| ID | Nombre | Rol | Invoca |
|----|--------|-----|--------|
| **U-P1** | Navegador | Carpetas/archivos, breadcrumb, entrar/`..`/refresh | S06–S07, S10 |
| **U-P2** | Detalle | Item seleccionado, mensajes sistema, preview, errores | S08, U-R10 |
| **U-P3** | Chatbot | Asistente metadata — búsqueda/descarga por lenguaje natural | [asistente-metadata.md](./asistente-metadata.md) |
| **U-SB** | Menú chrome | Barra superior (default): menú, config, conectar, llaves | U-01, U-02, U-04 |

---

## U-P1 — Navegador (arriba izquierda)

Equivalente al **browser** del validator.

**Contenido:**
- Breadcrumb ruta remota (S10)
- Lista: directorios arriba, archivos abajo
- Estado desconectado: lista vacía + texto amigable (U-R9)
- Acciones locales: refrescar, (futuro) filtros fecha/nombre

**Selección:** un click en fila → alimenta **U-P2**.

**Proporción sugerida:** ~45–55 % del ancho del par superior (redimensionable).

---

## U-P2 — Detalle / mensajes / contenido (arriba derecha)

Contexto del ítem activo y feedback de la app.

**Contenido (pestañas o secciones apilables):**

| Sección | Cuándo |
|---------|--------|
| **Detalle** | Archivo/carpeta seleccionado en P1 — nombre, tipo, tamaño, mtime |
| **Mensajes** | Errores conexión, timeouts, avisos — persisten hasta dismiss |
| **Contenido** | Preview texto/CSV truncado (S08) — opcional; asistente v1 puede omitir |

Sin selección: mensaje neutro o último mensaje del sistema.

**Proporción sugerida:** resto del par superior (~45–55 %).

---

## U-P3 — Chatbot (inferior, ancho completo)

Franja inferior tipo **T invertida** — ancho = P1 + P2.

**Contenido:**
- Historial conversación (local)
- Input lenguaje natural
- Respuestas = listados filtrados, confirmación descarga, conteos metadata
- **No** lee contenido CSV (U-R11)

**Interacción con P1:** el asistente puede resaltar o poblar el navegador tras una consulta (“mostrar en explorador”).

**Altura sugerida:** ~20–30 % ventana, redimensionable (splitter).

Ref: [asistente-metadata.md](./asistente-metadata.md)

---

## U-SB — Menú / chrome (posición configurable)

Barra de **menú desacoplada** del layout T: acciones globales, no parte del par P1|P2 ni de P3.

**Default wireframe:** **superior** (`top`) — menú clásico horizontal. Alternativas: `left`, `right`, `bottom` — ver § Menú desacoplado.

| Entrada | Destino |
|---------|---------|
| **File → Open** | U-M01 — llave, user, test, conectar |
| **Configuración → Llaves** | U-M02 / U-04 |
| **Configuración → Rutas** | U-M03 / U-01 paths |
| **Configuración → Otros** | U-M04 — Snowflake/Postgres (futuro) |
| **Help → Who is** | U-M05 / U-00 créditos |

Detalle completo → [menu.md](./menu.md).

**Altura sugerida (modo `top`):** ~32–40 px + submenús desplegables; compacto en icon+label opcional.

Config **no** dispara conexión al guardar (U-R9).

---

## Menú desacoplado — ¿se puede cambiar de lugar?

**Sí.** El menú (U-SB) debe implementarse como **componente independiente** del shell T, no pegado al wireframe “derecha”.

### Separación recomendada

```text
AppShell                    ← geometry: dónde va cada región
  ├── WorkArea (T invertida)  ← P1, P2, P3 — núcleo de trabajo
  └── MenuChrome (U-SB)       ← menú desacoplado; slot configurable
```

| Capa | Responsabilidad |
|------|-----------------|
| **WorkArea** | T invertida: navegador, detalle, chat |
| **MenuChrome** | Ítems de menú, config, conectar — **sin** lógica SFTP |
| **LayoutStore** | Preferencia usuario: posición menú, tamaños splitters |

La lógica (`core/`) no sabe si el menú está a la derecha o arriba; solo emite eventos (`connect_requested`, `open_config`).

### Posiciones posibles (v1 config o v2 drag)

| Slot | Comportamiento |
|------|----------------|
| `top` | **Barra horizontal clásica (default)** — File, Configuración, Help |
| `left` | Sidebar vertical |
| `right` | Sidebar vertical |
| `bottom` | Barra inferior |
| `hidden` | Hamburger / atajo teclado |

**Dock / arrastrar** (estilo IDE) es posible pero **más costoso** — fase v2; v1 basta con **elegir posición en Config** o JSON de layout.

### Persistencia

Guardar en perfil local o `~/.config/pde-desktop/layout.json`:

```json
{
  "menu": { "edge": "top", "height_px": 36, "collapsed": false },
  "splits": { "p1_pct": 50, "p3_height_pct": 25 }
}
```

### Coste por toolkit (orientativo)

| Toolkit | Menú desacoplado + cambiar edge |
|---------|----------------------------------|
| **PySide6** | Fácil — `QDockWidget`, `QToolBar`, layouts |
| **Slint** | Medio — layouts declarativos; re-root al cambiar edge |
| **NiceGUI** | Fácil — CSS flex/grid; mover columna |

Ninguno impide desacoplar; **no fijar “sidebar derecha” en `core/`**.

### Qué no mover sin re-pensar UX

| Región | Notas |
|--------|--------|
| P3 chatbot abajo | Identidad del T invertida; moverlo arriba cambia el producto |
| P1 \| P2 arriba | Core del explorador; intercambiar P1↔P2 sí es posible |
| Menú U-SB | **Libre** — desacoplado por diseño |

---

## Flujo de datos entre paneles

```text
Menú U-SB File → Open ──► SFTP core (test+connect) ──► P1 listado
P1 selección ──────────► P2 detalle / preview
P3 consulta ───────────► filtros metadata ──► P1 (opcional) + mensaje P2
Error SFTP ────────────► P2 mensajes (+ toast); app sigue (U-R10)
```

---

## U-00 vs layout principal

| Momento | Vista |
|---------|--------|
| Primer arranque / “Inicio” desde menú | U-00 splash (logo, créditos) — **sin red** |
| Trabajo habitual | Layout T invertida (este doc) |

U-00 puede ser pantalla completa que cede al shell, o modal — decisión toolkit.

---

## Capas visuales (draft)

Wallpaper + scrim + outline mono → [`../../draft/diseno/sistema-capas-wallpaper.md`](../../draft/diseno/sistema-capas-wallpaper.md).  
Los cuatro paneles comparten chrome; el T define **regiones funcionales**, no colores.

---

## Criterios layout (checklist)

- [ ] P1 + P2 redimensionables (splitter vertical)
- [ ] P3 redimensionable (splitter horizontal)
- [ ] Menú U-SB colapsable / compacto en ventanas bajas
- [ ] Menú U-SB: default `top`; alternativas `left`/`right` vía preferencia (U-R14)
- [ ] P2 legible con mensaje de error largo (timeout VPN)
- [ ] P3 usable sin ocultar controles críticos de P1
- [ ] Paridad Mac/Windows (U-R5)

---

## Relacionado

- [pantallas.md](./pantallas.md) — U-03/U-P1, U-05 en P2
- [funcionalidades.md](./funcionalidades.md) — IDs U-P1…U-SB
- [decision-ui-diferida.md](./decision-ui-diferida.md) — toolkit pendiente
