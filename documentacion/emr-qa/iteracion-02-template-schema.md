# Iteración 2 — Schema JSON del template

**Estado:** spec v2.0 · **Fecha:** 2026-07-29  
**Relacionado:** [`iteracion-02-funcionalidades.md`](./iteracion-02-funcionalidades.md)

Un **template** es un único archivo JSON: **header** (composición, llaves, reglas) + **minibase** (registros validados). No comparte schema con iteración 1 (`ScreenTemplate` / tags HTML en `ALPHA/`).

---

## Ubicación en disco

```text
emr-qa/knowledge_bases/<kb_id>/templates/<template_id>.json
```

Ejemplo: [`emr-qa/knowledge_bases/default/templates/tpl_example_patient_encounter.json`](../../emr-qa/knowledge_bases/default/templates/tpl_example_patient_encounter.json)

---

## Vista general

```json
{
  "_meta": { "...": "..." },
  "header": { "...": "composición + llaves + reglas + columnas evaluadas por defecto" },
  "minibase": { "...": "registros + política dedup" }
}
```

| Bloque | Rol |
|--------|-----|
| `_meta` | Identidad, versión de schema, KB, timestamps |
| `header` | Definición estática — editable antes y durante uso |
| `minibase` | Datos acumulados — crece al guardar registros en Tab 3 |

---

## `_meta`

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `schema_version` | string | sí | `"2.0"` |
| `template_id` | string | sí | Id estable, p. ej. `tpl_a1b2c3` |
| `knowledge_base_id` | string | sí | Carpeta KB, p. ej. `default` |
| `created_at` | string ISO UTC | sí | Primera persistencia |
| `updated_at` | string ISO UTC | sí | Última modificación |

---

## `header`

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `name` | string | sí | Nombre visible en Tab 3 |
| `description` | string | no | Notas del operador |
| `file_hints` | object | no | Extensiones / patrones de nombre sugeridos |
| `fields` | array | sí | Celdas lógicas ↔ columnas del grid |
| `keys` | array | sí | Llaves simples o compuestas (referencian `field_id`) |
| `rules` | array | no | Reglas de validación por campo o llave |
| `evaluation` | object | no | Columnas marcadas para evaluación por defecto (Tab 2) |

### `header.file_hints`

```json
{
  "extensions": [".csv", ".tsv", ".psv"],
  "filename_contains": ["encounter", "patient"]
}
```

Informativo — no bloquea Abrir/Probar.

### `header.fields[]` — campo lógico

Un campo = una **celda** del grid identificada por nombre de columna (v1: un archivo tabular).

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `field_id` | string | sí | Id estable, p. ej. `fld_mrn` |
| `label` | string | sí | Etiqueta UI |
| `column` | string | sí | Nombre de columna en el archivo (header pandas) |
| `required` | bool | no | Default `false` — participa en reglas |
| `notes` | string | no | Texto libre |

Relaciones entre campos de la **misma fila física** del archivo son independientes: cada campo tiene sus reglas; una llave compuesta agrupa varios `field_id` solo para identidad/dedup.

### `header.keys[]` — llave simple o compuesta

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `key_id` | string | sí | p. ej. `key_patient_encounter` |
| `label` | string | sí | Nombre visible |
| `field_ids` | string[] | sí | Un elemento → llave simple; varios → **compuesta** |
| `primary` | bool | no | Default `false`; **una** llave debe ser `primary: true` para dedup en minibase |

La llave **primaria** define el fingerprint de deduplicación (ver minibase).

### `header.rules[]` — reglas

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `rule_id` | string | sí | |
| `target_type` | `"field"` \| `"key"` | sí | Sobre qué aplica |
| `target_id` | string | sí | `field_id` o `key_id` |
| `type` | string | sí | Ver tabla abajo |
| `params` | object | no | Parámetros según tipo |
| `message` | string | no | Texto en alertas / comentarios |

**Tipos v2.0:**

| `type` | `params` | Efecto |
|--------|----------|--------|
| `not_empty` | — | Valor no vacío tras trim |
| `regex` | `{ "pattern": "..." }` | Coincide regex Python |
| `in_list` | `{ "values": ["A","B"] }` | Valor en conjunto |
| `unique_in_file` | — | Sin repetir en el archivo abierto (modo Probar) |
| `exists_in_minibase` | — | Llave primaria ya guardada en minibase (match positivo) |
| `not_in_minibase` | — | Llave aún no guardada (útil al crear registro) |

Reglas sobre `target_type: "key"` evalúan el **tuple** de valores de los campos de la llave.

### `header.evaluation`

Preferencias Tab 2 persistidas en el template (sesión puede override temporal).

```json
{
  "columns": ["mrn", "encounter_id", "visit_date"],
  "show_only_evaluated": false
}
```

- `columns`: nombres de columna con checkbox **marcado** por defecto.
- Columnas del archivo no listadas → desmarcadas (gris) hasta que el operador las active.

---

## `minibase`

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `dedup` | object | sí | Política anti-duplicados |
| `records` | array | sí | Registros guardados (puede empezar `[]`) |

### `minibase.dedup`

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `key_id` | string | sí | Debe coincidir con una `header.keys[].key_id` (preferible la `primary`) |
| `strategy` | string | sí | `"composite_key"` en v2.0 |

**Algoritmo `composite_key`:**

1. Tomar valores de los `field_ids` de la llave, en orden.
2. Normalizar cada valor: `str(value).strip()`, vacío → `""`.
3. Concatenar con separador `\x1f`: `val1 \x1f val2 \x1f ...`
4. `key_fingerprint` = SHA-256 hex del UTF-8 resultante.

Al **guardar** registro: si `key_fingerprint` ya existe en `records` → **rechazar** y alertar en capa comentarios.

### `minibase.records[]`

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `record_id` | string | sí | `rec_` + token |
| `key_fingerprint` | string | sí | Dedup |
| `key_id` | string | sí | Llave usada |
| `saved_at` | string ISO UTC | sí | |
| `source` | object | no | Origen del registro (archivo, fila) |
| `values` | object | sí | Mapa `field_id` → valor string |
| `validation` | object | no | Snapshot al guardar |

**`source`:**

```json
{
  "file_name": "encounters_20260729.csv",
  "file_path": "/Users/.../Downloads/encounters_20260729.csv",
  "row_index": 42
}
```

**`validation`:**

```json
{
  "passed": true,
  "failed_rule_ids": [],
  "evaluated_columns": ["mrn", "encounter_id"]
}
```

---

## Flujo modo Probar (referencia)

1. Cargar template → Tab 3 muestra `header.name`.
2. Tab 2 aplica `header.evaluation.columns` (editable).
3. Por cada fila visible del grid (o fila seleccionada — UI TBD):
   - Evaluar reglas solo en columnas evaluadas.
   - Campo OK → celda **verde**.
   - Llave fallida → alerta en barra + comentarios.
4. Guardar registro → construir `values`, calcular fingerprint, dedup, append a `minibase.records`.
5. `% validado` = celdas evaluadas que pasan reglas / total celdas evaluadas (filas visibles o scope TBD).

---

## Cifrado opcional de minibase

Ver ADR [`adr-template-encryption.md`](./adr-template-encryption.md).

Templates pueden guardar la minibase en texto plano (`minibase`) o cifrada (`minibase_sealed`).

### `header.encryption` (solo templates cifrados)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `key_id` | string | Identificador público de la llave (16 hex SHA-256) |
| `alg` | string | `"AES-256-GCM"` |
| `record_count` | int | Cache para listados sin descifrar |

### `minibase_sealed`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nonce_b64` | string | Nonce GCM (12 bytes, base64) |
| `ciphertext_b64` | string | JSON `{dedup, records}` cifrado (base64) |

La llave activa vive en `emr-qa/config/template_encryption.key` (local, no commiteada).

---

## Compatibilidad

| Schema | Uso |
|--------|-----|
| Iteración 1 `ScreenTemplate` | Solo `ALPHA/` — sin `schema_version` 2.0 |
| v2.0 | Modo Probar iteración 2 |

Cargador: si `schema_version == "2.0"` → `ValidationTemplate`; si no → legacy (editor ALPHA).

---

## Implementación

| Artefacto | Ruta |
|-----------|------|
| Modelos Python | `emr-qa/emrqa/validation_models.py` |
| Motor reglas | `emr-qa/emrqa/validation_engine.py` |
| Persistencia | `emr-qa/emrqa/validation_storage.py` |
| Shell UI | `emr-qa/shell/` · `./scripts/run_emr_qa_editor.sh` |
| Ejemplo | `emr-qa/knowledge_bases/default/templates/tpl_example_patient_encounter.json` |
| Tests | `tests/test_emr_qa_validation_template.py` · `tests/test_emr_qa_validation_engine.py` |
