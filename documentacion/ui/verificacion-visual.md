# Verificación visual — PDE Desktop UI

## ¿Puede el agente “ver” que está mal?

| Método | Qué detecta | Quién |
|--------|-------------|-------|
| **`pytest tests/test_ui_smoke.py`** | Color existe, tamaño > 0, versión, paneles | Agente (automático) |
| **Screenshot en el chat** | Color invisible, layout, contraste | Agente (visión) + vos |
| **Checklist manual** | Criterios estéticos | Vos |

**No tengo la app en tu pantalla** salvo que:
1. Corras tests (obligatorio del agente), o
2. Adjuntes captura (como hiciste — ahí sí detecté Color ausente).

## Flujo recomendado

```text
1. Pedís cambio UI + “@ui-qa verificar”
2. Agente implementa + pytest
3. Vos: ./scripts/run_ui.sh + screenshot si dudás
4. Comparás versión verde esquina inferior (0.0.YYMMDD.NNNN)
5. Marcás checklist documentacion/ui/checklist-prototipo.md
```

## Cómo pedir revisión con imagen

```text
Revisá esta captura contra checklist-prototipo.md.
Versión en pantalla debería ser 0.0.260715.0001.
Marca FAIL en ítems que no se cumplan.
```

## Versión en pantalla

Formato: **`major.minor.YYMMDD.NNNN`**

| Parte | Ejemplo | Significado |
|-------|---------|-------------|
| major | 0 | Versión producto |
| minor | 0 | Subversión |
| YYMMDD | 260715 | Fecha build (15-jul-2026) |
| NNNN | 0001 | Build del día — **reinicia en 0001 cada día**; incrementar solo entregas del mismo día |

Archivo: `ui/version.py` → `VERSION_DAY` + `BUILD_OF_DAY`

**Día nuevo:** `VERSION_DAY = YYMMDD` de hoy y `BUILD_OF_DAY = 1`.  
**Mismo día:** solo `BUILD_OF_DAY += 1`.

## Script captura (opcional Mac)

```bash
./scripts/run_ui.sh &
sleep 2
screencapture -x /tmp/pde-ui-check.png
```

Adjuntá `/tmp/pde-ui-check.png` al chat.
