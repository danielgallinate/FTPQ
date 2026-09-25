# EMR QA — validador tabular local

Abrir y **validar archivos delimitados** (CSV, TSV, PSV) con plantillas JSON, comparación referencia, métricas y export PDF.

Spec: [`../documentacion/emr-qa/README.md`](../documentacion/emr-qa/README.md)

## Arrancar

```bash
./scripts/setup.sh
./scripts/run_emr_qa_editor.sh
```

Requiere Python **3.12+** (Mac nativo o WSL2).

## Flujo

1. Navegador local → archivo en disco
2. **Abrir** (visor pandas) o **Probar** (validación con template)
3. Tab **Referencia** — comparar vs otro CSV
4. Métricas, export PDF/CSV

Fixture: [`fixtures/sample_encounters.csv`](fixtures/sample_encounters.csv)

## Código activo

```text
emr-qa/
  shell/          app PySide6
  emrqa/          validación v2.0
  fixtures/       CSV de prueba
  knowledge_bases/ plantillas v2.0
  config/         llave cifrado (local, no commitear)
```

`ALPHA/` — archivo histórico iteración 1 (captura pantallas); no usar.

Handoff zip: `./scripts/package_handoff.sh` → ver `HANDOFF.md`
