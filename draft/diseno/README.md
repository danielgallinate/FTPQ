# Draft — Diseño visual PDE Desktop

Borrador de sistema visual. Cuando se apruebe, migrar a `documentacion/ui/`.

| Doc | Tema |
|-----|------|
| [sistema-capas-wallpaper.md](./sistema-capas-wallpaper.md) | Fondo + chrome outline + contraste |
| [infraestructura-ui-stack.md](./infraestructura-ui-stack.md) | Stack y arquitectura repo |
| [comparativa-ui-ligera.md](./comparativa-ui-ligera.md) | Investigación ligera + visual |
| [decision-ui-diferida.md](./decision-ui-diferida.md) | ¿Cambiar UI después? ¿Avanzar sin decidir? |
| [tokens-mono.base.yaml](./tokens-mono.base.yaml) | Tokens B/N (mapear a Slint palette) |

## Principio

```text
Capa 0 — Wallpaper (modificable, imagen)
Capa 1 — Scrim opcional (uniforme, para legibilidad)
Capa 2 — Chrome UI (solo texto + bordes sólidos, sin rellenos)
```

Diseñar primero en **blanco y negro**; paletas de color = override de tokens más adelante.
