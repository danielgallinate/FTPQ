# ADR — Cifrado opcional de minibase en templates v2.0

**Estado:** aceptado · **Fecha:** 2026-08-05

## Contexto

Los templates EMR QA v2.0 guardan datos de referencia (MRN, correos, etc.) en `minibase.records` como JSON plano. El operador puede copiar el archivo fuera del entorno local.

## Decisión

1. Cifrado **opcional** de la minibase con **AES-256-GCM**.
2. **Una llave activa** por sesión, almacenada en `emr-qa/config/template_encryption.key` (no commiteada).
3. En disco: `header.encryption.key_id` + `minibase_sealed`; el `header` (columnas, reglas) permanece en claro.
4. Templates plaintext y cifrados conviven en la misma KB.
5. Cifrado inicial solo por acción explícita (**Cifrar minibase**); guardar preserva el estado.
6. Gestión de llave en **Ver → Llave** (generar, cargar, exportar).

## Amenaza cubierta

Copia del JSON sin la llave (USB, backup, repositorio filtrado).

## Límites

- La llave en el mismo proyecto protege contra copia **solo del JSON**, no contra acceso completo a la máquina del operador.
- Nombres de columnas y reglas siguen visibles en `header`.
- No sustituye políticas org de PHI ni canal oficial PDE.

## Alternativas descartadas

- Passphrase / KDF: el operador pidió llave generada automáticamente.
- Cifrar todo el JSON: rompe listados y edición de estructura sin desbloqueo constante.
- Cifrar campo a campo: complejidad sin beneficio para minibases pequeñas.

## Referencias

- [`iteracion-02-template-schema.md`](./iteracion-02-template-schema.md)
- `emr-qa/emrqa/template_crypto.py`, `template_key_store.py`, `validation_storage.py`
