# ADR-0001: Sin base de datos en fase 0–2

## Estado
Aceptado

## Contexto
El PDE SFTP Validator depende de Postgres (`extract_history`, `config`) y VPN para validación oficial. El nuevo producto debe entregar valor de SFTP + análisis CSV más rápido, portable y sin credenciales RDS para QA.

## Decisión
No incluir conectores PostgreSQL ni Snowflake hasta una fase futura explícita. Las reglas de validación CSV vienen de perfiles JSON locales.

## Consecuencias
### Positivas
- Menor superficie de secretos en el paquete QA
- Desarrollo offline con mocks
- Empaquetado más simple

### Negativas
- No hay validación vs logs PDE (OK/FAIL/ORPHAN/GHOST)
- CONFIG_ID y sync desde BD fuera de alcance

## Alternativas consideradas
- Portar F7 del validator → rechazado por alcance
- Híbrido .env + JSON con sección DB deshabilitada → rechazado; confunde a QA

## Referencias
- Fase futura en [paso-02-funcionalidades](../paso-02-funcionalidades/README.md)
- Handoff §3 `PDE_DESKTOP_HANDOFF.txt`
