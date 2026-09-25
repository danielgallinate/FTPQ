# ADR-0002: Perfiles JSON para SFTP y reglas pandas

## Estado
Aceptado

## Contexto
El validator usa `.env` multi-sección (BD + SFTP). PDE Desktop necesita múltiples entornos, reglas pandas estructuradas y fixtures versionables.

## Decisión
Usar archivos JSON por perfil (`profiles/<id>.json`) con secciones `sftp` y `pandas_rules`. Opcional: `python-dotenv` solo para overrides dev locales (no commitear).

## Consecuencias
### Positivas
- Un archivo por entorno de prueba
- Mocks y tests deterministas
- UI puede listar/cargar perfiles sin parser .env custom

### Negativas
- Migración mental para QA acostumbrados a F4/.env
- Validar schema JSON (recomendado: jsonschema en Fase 1)

## Alternativas consideradas
- Solo .env → menos estructura para reglas pandas
- .env + JSON → dos fuentes de verdad

## Referencias
- Ejemplo en [paso-04-mocks](../paso-04-mocks/README.md)
- F17–F19
