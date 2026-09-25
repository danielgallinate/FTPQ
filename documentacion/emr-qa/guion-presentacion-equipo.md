# Guion — presentar FTPQ al equipo (~12 min)

Uso: leerlo casi tal cual. Entre corchetes: acciones o demos. No vender sello ISO/HIPAA ni “calidad de datos”.

**Audiencia:** BI + QA + quien publica o consume exports (Logi, PDE, CSV de query).  
**Objetivo del talk:** que sepan *qué problema resuelve*, *qué no*, *las tres apps*, *cómo lo usaríamos mañana*.

---

## 0. Apertura (45 s)

Hoy no vengo a mostrar un dashboard. Vengo a mostrar una **herramienta local** para no firmar un export con cinco filas en un sheet.

El problema es este: el report **ya salió**. El entregable es un CSV. Alguien abre Excel, mira la cabeza, dice “se ve bien”. Eso no prueba que **siga siendo el archivo que BI definió** — columnas, títulos, tipos — después de un cambio de Logi, de un filtro, o de un lunes sin filas.

Esta suite se llama **FTPQ**. Corre **en tu máquina**, sobre archivos **ya en disco**. No sube nada a una IA. No es un producto de IT ni un validador regulatorio.

---

## 1. Una frase de producto (30 s)

> Reproducimos el **contrato de entrega** del export: layout y tipos. No certificamos que el **contenido** sea verdad de negocio.

En BI nosotros **ya definimos** cómo debe salir el archivo. Esta herramienta **vuelve a comprobar eso** mañana, con el mismo job, sin rehacer el ritual del Excel.

---

## 2. Qué no es (1 min) — decirlo pronto

No es calidad de datos. Un PASS no dice “estos CPT están bien” ni “este paciente existe en el EMR”.

No es UAT. QA sigue firmando aceptación y casos gold de negocio.

No es HIPAA-in-a-box. La app **no sabe qué es PHI**. Si alguien pone identificadores reales en un catálogo, eso es **política**, no un modo de la herramienta. Se corrige con quién versiona qué, no parcheando el motor.

La **salida del job** — el veredicto que se comparte — son **cabeceras, existencia, conteos**. No un dump de filas. El visor, si lo abrís, es el CSV que **ya tenías**. No te da un dato que no estuviera en disco.

Un catálogo o un gold **no valida un archivo de un giga**. Recrea **casos de prueba**. El giga, si cabe, se recorre para **forma y tipos**, no para “todo el contenido está OK”.

---

## 3. Las tres piezas (2 min)

Tres entradas. Una familia. No son tres productos distintos.

**Uno — `run_ui.sh`**  
Cliente SFTP de escritorio: conectar, listar, bajar. Es **llegada** del archivo. No es el validador. Si el CSV ya está en carpeta, este paso ni hace falta.

**Dos — `run_emr_qa_editor.sh`**  
La UI. Acá **diseñamos** el contrato: schema (columnas de más, de menos, títulos, tipos, nulos). Opcional: catálogos, cruce de **dos** archivos (query vs report, versión A vs B). Se usa sobre **set de pruebas QA en DEV**. Ahí sí se mira el grid: estamos armando la regla.

**Tres — CLI: `run_emr_qa_job.sh`, batch, `run_sftp_job.sh`**  
La misma receta en **ambientes superiores**, sin reabrir Excel. Existencia por fecha (`{date}`), descarga, o solo “¿llegó?”. Exit 0 / 1 / 2. **NO DATA** — extract incremental vacío — **no es FAIL**. FAIL es: no está el archivo, o se rompió el contrato.

[Pantalla: tabla de las tres filas en una slide]

| Script | Para qué |
|--------|----------|
| `run_ui` | Traer el archivo |
| `run_emr_qa_editor` | Diseñar el job en DEV |
| `run_emr_qa_job` / batch / `run_sftp_job` | Ejecutar el contrato |

---

## 4. Tres capas, una es el núcleo (2 min)

**Schema — el núcleo.**  
¿Este CSV es el entregable que publicamos? Columnas presentes, faltantes, sobrantes, tipos. Un upgrade de Logi que cambia un entero por texto ** explota acá**. Eso es lo que el muestreo de cinco filas casi nunca ve.

**Catálogo — extra.**  
Listas con llave: códigos, clínicas de test, un gold chico. Sirve para *¿sigue existiendo este caso de QA?* No para certificar 900 mil filas.

**Referencia — extra.**  
Dos archivos, orígenes distintos. Mapeo de llaves y columnas a evaluar; los nombres no tienen que ser idénticos. Query exportado vs export del report. Antes vs después del cambio de workbook. **Los dos pueden estar mal igual:** esto mide consistencia, no la verdad absoluta.

[Si hay tiempo: abrir un schema `*_col` y señalar columnas, no celdas.]

---

## 5. Cómo lo usaríamos nosotros (2 min)

**DEV.** Fixture o clínica de test. Abrís la UI, armás el job, lo guardás en Git. El set de pruebas **se puede ver**. Eso es el laboratorio.

**Superiores.** El CSV llega (SFTP o carpeta). Corrés el **mismo** `job.json` por CLI. El veredicto sale en JSON: PASS / FAIL / NO DATA. Eso es lo que entra a un ticket o a un sheet-acta: **una fila por corrida**, no el millón de filas.

**Archivos grandes.** CLI hasta ~1 GiB para **el contrato** (pandas, archivo completo). La UI, si el archivo es enorme, puede abrir **muestra**: eso es inspección, **no** el cierre oficial.

**Nada de esto va a un agente ni a ChatGPT.** El extract se queda en la máquina. Al copiloto, si acaso, le pegamos el **manifiesto** (nombres de columna, conteos), nunca el CSV.

---

## 6. Demo sugerida (3 min) — opcional

1. [Mostrar un CSV de fixture, no prod.] “Esto es DEV.”  
2. [Schema → Validate structure.] “Contrato: columnas y tipos.”  
3. [Terminal] `./scripts/run_emr_qa_job.sh … --file … --short` → `PASS` o `FAIL`.  
4. [Decir] “Este mismo comando es el que correríamos después de un deploy de Logi, sin abrir el archivo.”

Si no hay demo: una captura del `--short` y un manifiesto de cabeceras basta.

---

## 7. Cierre (45 s)

Pedimos tres cosas:

1. Tratar el **CSV como el producto** que validamos, no el dashboard.  
2. Usar FTPQ para **repetir el contrato**, no para reemplazar QA ni para “calidad de datos”.  
3. Jobs en Git; corrida por CLI; el sheet, si existe, es **acta**, no laboratorio.

Preguntas.

---

## Preguntas que van a salir (respuestas cortas)

**¿Esto reemplaza a QA?**  
No. Ellos firman aceptación. Nosotros firmamos “el export sigue siendo el que definimos”.

**¿Sirve para Billing de 700 MB?**  
Para **forma y tipos**, sí, por CLI. Para gold/catálogo, no: el gold es el caso, no el giga.

**¿Y si hoy no hay filas?**  
NO DATA. En incrementales eso puede ser correcto. Ausencia del archivo es otra cosa: FAIL.

**¿Es seguro / HIPAA?**  
La herramienta no clasifica PHI y no manda el archivo a la nube. Quien tiene el CSV **ya lo tenía**. La salida del job no lista valores. Catálogos con datos reales: política del equipo, no un feature.

**¿Windows?**  
App completa: WSL2 + los mismos `.sh`. Hay un CLI estructural nativo más limitado. No es un `.exe` único todavía.

**¿Lo instalo ya?**  
`./scripts/setup.sh` y `./scripts/run_emr_qa_editor.sh`. Handoff en `HANDOFF.md`.

---

## Slide mínima (6 viñetas)

1. Contrato de entrega (columnas/tipos), no calidad de contenido  
2. Local; no sube extracts a IA  
3. UI = diseñar en DEV · CLI = repetir en superiores  
4. Schema núcleo · catálogo/referencia extras  
5. NO DATA ≠ FAIL  
6. El veredicto comparte cabeceras y existencia, no filas  

---

## Lo que no decir

- “Estamos certificados ISO / HIPAA / SOC 2”  
- “Validamos la calidad de los datos”  
- “El agente revisa el extract”  
- “Con el catálogo el archivo entero queda OK”  
- “La UI es el veredicto oficial en archivos grandes”
