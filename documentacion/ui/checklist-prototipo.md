# UI — Checklist prototipo (verificable)

> Cada ítem debe pasar **antes** de dar por cerrada una tarea UI.  
> Comando: `pytest tests/test_ui_smoke.py -q` + revisión visual manual.

## Layout

| ID | Criterio | Cómo verificar |
|----|----------|----------------|
| L-01 | Proporción vertical **2:1:1** (nav+detalle / asistente / consulta) | Redimensionar ventana; 3 franjas visibles |
| L-02 | Proporción horizontal arriba **2:1** (navegador / detalle) | Navegador más ancho que detalle |
| L-03 | **Sin toolbar** suelta (Open/Demo/Who is) | Solo menú superior |
| L-04 | **4 paneles** con un solo borde cada uno (sin caja interior) | Inspección visual |
| L-05 | Separación entre paneles (gap) | Wallpaper visible entre marcos |

## Chrome / tema

| ID | Criterio | Cómo verificar |
|----|----------|----------------|
| C-01 | Botón **Color** visible, alineado **derecha** del menú | Captura / ojo / pytest `test_color_button_visible_and_sized` |
| C-06 | Badge **verde** esquina inferior `0.0.YYMMDD.NNNN` | Captura / pytest `test_version_badge_visible` |
| C-02 | Letras **C-o-l-o-r** multicolor | Inspección visual |
| C-03 | Clic Color **alterna** texto/bordes claro ↔ oscuro | Clic + contraste cambia |
| C-04 | Fondo wallpaper **cover** | `ui/assets/pexels-pixabay-33109.jpg` |
| C-05 | Bordes **1px**, esquinas **redondeadas** | Inspección visual |

## Menú

| ID | Criterio | Cómo verificar |
|----|----------|----------------|
| M-01 | File → Open | Diálogo stub |
| M-02 | Ver → Fondo… | Cambia wallpaper |
| M-03 | Configuración → Llaves/Rutas guardan perfil | Rutas: paths+credenciales · Llaves: listar/elegir/crear |
| M-04 | **Test SFTP + Save** responden y botones se reactivan | pytest `test_keys_save_persists` + `test_keys_test_reenables_buttons` |
| M-05 | Paridad validator: SFTP_HOST §3 + F4 user/llave | Manual: mismo .env → Test OK |
| M-04 | Help → Who is | Diálogo acerca de |
| M-05 | **Color solo alterna tema** (no confundir con Who is) | C-03 |

## Paneles

| ID | Criterio | Cómo verificar |
|----|----------|----------------|
| P-01 | P1 título Navegador + tabla | Visual |
| P-02 | P2 título Detalle/mensajes, contenido **sin** marco interior | Visual |
| P-03 | P3 Asistente **sin** input dentro | Visual |
| P-04 | P4 consulta oculta (fase futura) | No visible «Escriba una consulta…» |

## Automatizado (CI / agente)

```bash
QT_QPA_PLATFORM=offscreen pytest tests/test_ui_smoke.py -q
```

Fallo = no declarar tarea UI completa.

---

## Cómo pedirle al agente que verifique

```text
@ui-qa verificar checklist prototipo
```

O explícito:

```text
Implementa X. Luego:
1. pytest tests/test_ui_smoke.py
2. Marca checklist documentacion/ui/checklist-prototipo.md
3. Lista ítems FAIL si no pudiste abrir GUI
```

**Regla:** el agente no dice "listo" sin salida de pytest + tabla PASS/FAIL del checklist.
