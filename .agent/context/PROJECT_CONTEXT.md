# Contexto actual del proyecto

Este documento resume el estado metodológico y técnico del proyecto de clasificación semántica y construcción de redes. Es el contexto estable de trabajo para la fase actual; las decisiones y resultados puntuales de cada sesión se mantienen en `.agent/sessions/`.

## 1. Propósito y fase actual

El proyecto transforma documentos de los incubadores en una base de entidades canónicas y redes semánticas auditables. La unidad de evidencia es la oración: las relaciones entre entidades se derivan de su coocurrencia dentro de `(document_id, sentence_id)` y deben poder rastrearse hasta el documento, la oración, el contexto y las entidades originales.

La fase de trabajo actual con la usuaria es rehacer y auditar el NER de los
documentos Agroforestry, empezando por validar el texto limpio y aplicando el
codebook operativo en `data/codebooks/codebook_en_construccion_en.md`. Sus diez categorías,
fichas y reglas de anotación están desarrolladas en el borrador 0.4.
El codebook sirve como especificación
para la extracción y clasificación mediante LLM en la API, con posterior
canonicalización, atributos de nodos y análisis de coocurrencia.

### Limpieza de la Guía del EUDR — 11 Nov 2026

**Continuidad de traducción:** después de la limpieza, la usuaria pidió completar
directamente los pendientes sin Anthropic. La generación del bloque restante
fue detenida por un filtro de contenido; el intento no creó una traducción
completa ni publicó un archivo inglés. No se llamó a Anthropic ni se modificó
el estado. Registro: `export/eudr_english_2026-11-11/checkpoint.json`, con los
índices pendientes sobre el hash nuevo. No reintentar ni reproducir la generación
bloqueada mediante fragmentación, reformateo, codificación, herramientas,
subagentes o turnos posteriores. Una alternativa permitida es recibir de la
usuaria una traducción completa para comprobar cobertura, cifras y códigos.

La usuaria autorizó limpiar `b4ac3608-c2c2-46ca-8877-564fa4775362`
(*Guia del EUDR -digital.pdf*) antes de preparar su versión inglesa. Se
contrastaron el `cleaned`, el Markdown convertido y las páginas del PDF.
Se retiraron los 26 pies/cabeceras persistentes, portada duplicada,
metadatos de impresión, índice, instrucciones de QR y restos de enlaces.
También se retiraron marcas `~~`, viñetas exportadas como `z`/`|`, llamadas
de nota y numeración flotante dentro de las frases. Se conservaron las
notas normativas y citas con contenido sustantivo.

Se repararon ocho continuaciones entre páginas/columnas y 53 fragmentos
de espaciado/tipografía, estos últimos mediante coincidencia de caracteres
alfanuméricos con bloques nativos del PDF. Se recuperaron cuatro entradas
del glosario, etiquetas de actores, rótulos del diagrama de productos y
encabezados de los seis anexos que la limpieza anterior había perdido.
Los códigos de productos del anexo se verificaron contra los anteriores.
El `cleaned` quedó en 84.795 caracteres y 369 párrafos; su SHA-256 es
`a1aee2da10667f836a518ec44b2eac8bba76f4e724e3858db3a3ffd27407085f`.

Aplicado y verificado en AWS y copia local, con respaldo del texto anterior.
El PDF y el convertido conservan sus hashes. No se modificaron metadatos
de PostgreSQL: sigue `status=cleaned`, `language=es`, `english_path=NULL`,
`ner_path=NULL` y cero menciones persistidas. No se ejecutaron traducción,
NER, fuzzy matching ni despliegues.

Las 360 traducciones originales se conservaron intactas. Se creó un borrador
JSON alineado con los párrafos nuevos, retirando el mismo ruido y señalando
las uniones y recuperaciones que necesitan revisión. De los 43 bloques
originalmente pendientes, seis eran pies de página ya excluidos; quedan
37 bloques originales sin traducir. Al contar también las etiquetas y el
contenido recuperados, el borrador marca 52 párrafos para traducir o completar
y 119 para revisión (los grupos se superponen). No es una versión inglesa
publicable y no debe usarse para cambiar aún el estado a `english`.

Evidencia vigente y borrador: `export/eudr_cleaning_2026-11-11/`, especialmente
`result.json`, `cleanup_report.json`, `paragraph_provenance.json` y
`english_rebased_draft.json`. Los checkpoints del 9 Nov corresponden al
SHA-256 anterior: no se deben interpretar sus índices sobre el nuevo `cleaned`.
Respaldo en AWS:
`data/output/document_cleanup/b4ac3608-c2c2-46ca-8877-564fa4775362/20261111T210245405477Z/`.

### Etapa `english`: copia directa para idioma inglés — 11 Nov 2026

La usuaria autorizó desplegar, reiniciar la API y ejecutar el endpoint para
`70767dc6-c115-46fe-b002-90f8445fd958`. Se desplegó la etapa `english` y,
por su corrección explícita, se retiró la verificación con Anthropic para
documentos cuyo `language` registrado es `en` (incluidas variantes regionales).
En ese caso se copian directamente los bytes del `cleaned`, sin crear un
cliente de Anthropic ni exigir una clave de API. La traducción de otros idiomas
conserva su flujo LLM.

Están disponibles `POST /documents/{document_id}/translate` y
`GET /documents/{document_id}/english`; `DocumentRead` incluye `english_path`.
NER lee esa versión y sus operaciones batch, reversión y eliminación
contemplan la etapa. La migración `f0a1b2c3d4e5` ya estaba aplicada. Pasaron
las ocho pruebas localmente y con las dependencias de producción; la regresión
de copia inglesa usa una clave vacía y comprueba que no se llama al cliente.
Se verificaron `/health`, OpenAPI y el explorador; el temporizador de
despliegue automático quedó restaurado.

El POST real respondió HTTP 200 con `translated=false`. El documento está en
`english`, mantiene `language=en` y tiene
`english_path=s3/english/70767dc6-c115-46fe-b002-90f8445fd958.txt`.
La descarga respondió HTTP 200 y su SHA-256 coincide exactamente con el
`cleaned`: `d8044460c241af402010393b5f0b3c07b8f9b696e2ca804cc959b55082541869`.
Contiene 52.702 caracteres; se guardó también la copia local verificada.
El PDF, convertido, limpio y demás metadatos conservaron sus hashes/valores;
`ner_path` sigue nulo y hay cero menciones. No se ejecutó NER ni fuzzy matching.

El HTTP 502 inicial por saldo insuficiente de Anthropic corresponde a la
implementación anterior, que verificaba innecesariamente el idioma inglés;
ese bloqueo quedó resuelto para esta copia. Evidencia vigente:
`export/english_passthrough_2026-11-11/deployment_result.json` y
`endpoint_result.json`. El respaldo del servidor está en
`export/english-endpoint-20261111T204500156153Z/` y su imagen de reversión es
`semanticclassification-api:before-english-20261111t204500156153z`.

### Limpieza editorial e idioma de `70767dc6` — 11 Nov 2026

Por instrucción de la usuaria se corrigió en AWS el documento
`70767dc6-c115-46fe-b002-90f8445fd958`, *The distribution of cadmium in soil
and cacao beans in Peru*. Su contenido principal es inglés: `language` pasó
de `es` a `en`. Se retiraron del `cleaned` 49 bloques de autores,
afiliaciones, contacto, cabeceras de revista y material editorial final;
se repararon 12 grupos de continuaciones cortadas por páginas, columnas o
figuras. El texto pasó de 56.515 a 52.702 caracteres. Se conservaron todas
las palabras y cifras de los bloques sustantivos retenidos y los ocho pies
de figura. El PDF y el Markdown convertido conservan sus hashes originales.

La corrección se aplicó al archivo de AWS y a la copia local; el SHA-256
resultante es `d8044460c241af402010393b5f0b3c07b8f9b696e2ca804cc959b55082541869`.
Al terminar esa limpieza quedó en `cleaned`, con `english_path` y `ner_path`
nulos y cero menciones persistidas. En esa operación el idioma fue el único
campo de PostgreSQL modificado; el paso posterior a `english` está descrito arriba.
El respaldo, manifiesto previo, resultado y comparación están en
`export/cleaning_70767_2026-11-11/`; en AWS hay otro respaldo bajo
`data/output/document_cleanup/70767dc6-c115-46fe-b002-90f8445fd958/20261111T201015585249Z/`.
La discrepancia de idioma registrada en los checkpoints de traducción del
9 Nov queda resuelta; esos archivos se conservan como antecedentes.

### Reparación de limpieza y reinicio NER — 2 Nov 2026

Los 115 documentos Agroforestry locales estaban en `cleaned` al iniciar el nuevo NER con
auditoría humana y sin llamar al endpoint Anthropic de extracción. El primer
documento, `660086b9-93ec-4bd6-bd73-b89088ef19f1`, tenía el Markdown
convertido en inglés, pero el archivo limpio en español, con pasajes omitidos.
La limpieza lingüística con Anthropic fue retirada del flujo; la limpieza
estructural ahora conserva párrafos y corta referencias y material editorial
final por encabezados antes de perder el formato Markdown. Se respaldó el
texto limpio anterior en `export/ner_audit/<id>/cleaned_anterior_es.txt` y se
regeneró solo ese documento desde el Markdown: 54.594 caracteres en inglés.
Ese fue el estado previo a su nuevo NER manual.

Una revisión heurística de idiomas señaló otros 16 documentos Agroforestry con
conversión aparentemente inglesa y texto limpio aparentemente español. Tras
contrastar sus fuentes y preparar candidatos, se regeneraron desde sus Markdown
con respaldos individuales en `export/cleaning_repair_2026-11-02/`. La misma
heurística ya no marca traducciones inglés→español entre los 115 documentos;
esto no sustituye la revisión de contenido de cada uno antes de NER. El reporte
inicial está en `export/cleaning_audit_2026-11-02.csv`. Los JSON anteriores se
conservan en `Auditoria1` fuera del repositorio.

La auditoría de los 62 documentos Agroforestry con `language = es` comparó cada
Markdown convertido con su `cleaned` anterior. Detectó 4 errores confirmados
(respuestas de Anthropic incrustadas o contenido reformulado), 14 diferencias
relevantes para revisión dirigida y 44 sin alerta material automática. La
limpieza determinista se ajustó para excluir secciones bibliográficas completas,
incluidas variantes de título y anexos bibliográficos, sin cortar los capítulos
o anexos sustantivos que vienen después. También conserva el texto de las celdas
de tablas, antes descartado por completo.

Los 62 archivos `cleaned` españoles se regeneraron desde `converted` y se
sobrescribieron sin guardar copias nuevas del texto anterior. Se eliminaron los
reportes intermedios que contenían fragmentos del `cleaned` antiguo. El registro
actual está en `export/reclean_agroforestry_es_2026-11-02.csv`: 57 secciones
bibliográficas excluidas en 27 documentos. Una verificación posterior encontró 62/62 archivos
iguales a la salida del limpiador vigente, ninguno vacío ni con respuestas
explícitas de Anthropic; todos siguen en estado `cleaned`, sin `ner_path`.
La comprobación automática no sustituye la lectura y auditoría humana de los
textos antes de NER, especialmente en documentos con OCR o tablas complejas.

El primer NER manual completo se hizo sobre
`660086b9-93ec-4bd6-bd73-b89088ef19f1`. Antes de anotar se regeneró su
`cleaned` inglés desde `converted`, quitando portada, resumen duplicado,
metadatos editoriales y 17 encabezados repetidos de la revista; se unieron
cinco oraciones partidas por saltos de página. Se corrigió la segmentación de
citas `et al.` en `src/services/ner.py`. La entrada final contiene 38 bloques y
360 oraciones. Se revisaron todas, incluidas las 150 sin menciones; 505
anotaciones pasaron la validación estricta de literalidad, offsets y
solapamientos. El JSON oficial está en `s3/archivosNER/<id>.json`; el documento
pasó a `ner` sin llamar a Anthropic. El manifiesto con hashes está en
`data/output/ner_manual/<id>/manifest.json`. La usuaria revisó las menciones
y confirmó que todo está correcto. Las 63 menciones marcadas `medium` están en
`export/ner_audit/<id>/menciones_dudosas.tsv` y las 360 oraciones en
`export/ner_audit/<id>/auditoria_ner.tsv`. El documento permanece en `ner`;
la resolución canónica es un paso separado.

El segundo documento procesado es `c13401cf-aca9-4cbb-846a-803b6b330d3a`
(*Critical transitions in the Amazon forest system*). Su `cleaned` contenía
afiliaciones, dos bibliografías y material editorial; se corrigió desde el
`converted`, se recuperó el resumen y se repararon cortes de columnas. El texto
final tiene 47.707 caracteres. Se revisaron 263 oraciones y se guardaron 318
menciones NER con offsets exactos y sin llamadas a Anthropic. El estado local es
`ner`; la auditoría humana está pendiente. Los artefactos siguen el patrón
`data/output/ner_manual/<id>/`, `s3/archivosNER/<id>.json` y
`export/ner_audit/<id>/`. Una sola mención literal contiene “agroforestry” y
quedó clasificada como PRAC. No se ejecutó fuzzy matching.

El tercer documento es `ce37176e-2970-4ff8-b081-d11ed61386c2`
(*Food, monetary, energy, and socio-environmental features of a post-cacao
agroforestry system in the Ecuadorian Amazonia*). Se reconstruyó su `cleaned`
inglés desde el `converted`: se quitaron bibliografía, afiliaciones y una
respuesta de Anthropic, preservando el resumen, las tablas y las notas
sustantivas. Se anotaron manualmente 328 oraciones con 403 menciones; los
fragmentos y offsets pasaron validación estricta. El documento local quedó en
`ner` sin llamadas al proveedor. Artefactos: `data/output/ner_manual/<id>/`,
`s3/archivosNER/<id>.json` y `export/ner_audit/<id>/`. La auditoría humana de
las menciones sigue pendiente; 52 están marcadas `medium`. No se ejecutó fuzzy
matching.

El cuarto documento procesado es `0ee3a358-0b9a-4899-8def-1471e13b98dc`
(*The economy of agroforestry systems in the Amazon*). Su `cleaned` conservaba
un resumen portugués duplicado, metadatos editoriales y créditos de figuras;
se retiraron y se unieron ocho pasajes cortados. El texto inglés final tiene
59.580 caracteres. Se anotaron manualmente 359 oraciones, con una pasada
determinista para cubrir siglas explícitas de los sistemas y campesinados:
631 menciones con offsets validados. El estado local pasó a `ner` sin
Anthropic. Los artefactos están en `data/output/ner_manual/<id>/`,
`s3/archivosNER/<id>.json` y `export/ner_audit/<id>/`. La auditoría humana
sigue pendiente; 107 menciones están marcadas `medium`. No se ejecutó fuzzy
matching.

El quinto documento procesado es `1e76e99b-cfd5-4f42-846f-44490ba6ff04`
(*Panarchy to explore land use: a historical case study from the Peruvian
Amazon*). Su `cleaned` tenía afiliaciones, cabeceras y pies de figura dentro
de oraciones, además de una tabla ilegible y párrafos de dos columnas fuera
de orden. Se contrastó con el PDF y se corrigió sin respaldo nuevo del texto
anterior; las tablas 1 y 2 quedaron en filas legibles. El texto final tiene
51.428 caracteres. Se anotaron manualmente 325 oraciones con 546 menciones;
literalidad y offsets validados. El estado local es `ner` sin Anthropic, con
artefactos en `data/output/ner_manual/<id>/`, `s3/archivosNER/<id>.json` y
`export/ner_audit/<id>/`. La auditoría humana está pendiente, con 102 menciones
`medium`; no se ejecutó fuzzy matching.

El sexto documento procesado es `17f2d625-5dda-44e8-9051-af960d4870ec`
(*Diversity Bears Fruit: Evaluating the Economic Potential of Undervalued Fruits
for an Agroecological Restoration Approach in the Peruvian Amazon*). Su
`cleaned` omitía el resumen y los datos de las tablas 1 y 2, además de tener
párrafos unidos; se reparó contrastando `converted` con el PDF original, sin
respaldo del `cleaned` anterior. El texto final tiene 45.260 caracteres.
Se revisaron 270 oraciones y se guardaron 355 menciones NER con fragmentos y
offsets validados. Las 71 apariciones de «agroforestry» quedaron cubiertas por
PRAC o por una designación completa de otro componente según el codebook.
El documento local está en `ner` sin llamadas a Anthropic. La auditoría humana
sigue pendiente: 16 menciones `medium` en `export/ner_audit/<id>/`; no se ejecutó
fuzzy matching.

El séptimo documento procesado es `6c19caf1-09ef-443f-93d5-12f092eb6711`
(*Assessing Biodiversity within Agroforestry Systems through Ecoacoustic
Monitoring*). Se retiraron del `cleaned` la portada, autores, índice y título
duplicado. Se corrigieron errores OCR de nombres de especies contra el PDF y se
restauró la mención de la lista roja de IUCN que faltaba en tres pasajes. El
texto final tiene 13.180 caracteres. Se revisaron 92 oraciones y se guardaron
117 menciones con fragmentos y offsets validados. Las dos apariciones de
«agroforestry» son PRAC. El documento local está en `ner`, con cero llamadas a
Anthropic. La auditoría humana sigue pendiente: 25 menciones `medium` en
`export/ner_audit/<id>/`; no se ejecutó fuzzy matching.

El octavo documento procesado es `089089a9-e93c-493a-8f85-14a1da1b4a67`
(*Understanding the diversity of private conservation in the Peruvian Amazon*).
Su `cleaned` tenía metadatos editoriales, párrafos fuera de orden por columnas,
tablas incompletas y bibliografía en el convertido. Se reconstruyó el texto de
lectura con las seis tablas, sin respaldo del `cleaned` anterior. El PDF fuente
contiene una discrepancia no resuelta: tabla 6 = 6.289 ha de media para
concesiones de conservación; prosa = 1.949 ha. Se conservaron ambos valores y se
documentaron en `cleaning_notes.json`. Se revisaron 354 oraciones y se guardaron
945 menciones con fragmentos y offsets validados. La aparición de «agroforestry»
es PRAC. El estado local es `ner`, sin Anthropic. La auditoría humana de las 81
menciones `medium` está pendiente; no se ejecutó fuzzy matching.

El noveno documento es `5f87adae-ade1-4ff4-b880-7951c20c839b`
(*Amazon Assessment Report 2025*, 497 páginas). El `cleaned` todavía contenía
portada, afiliaciones, referencias dispersas y nueve bloques extensos de
bibliografía. Se reparó en tres pasadas sin respaldo nuevo del anterior; la
versión resultante tiene 626.325 caracteres. Una primera extracción asistida
por reglas literales y revisión de muestras distribuidas por capítulos produjo
4.305 menciones en 3.632 oraciones; 37 apariciones de «agroforestry» están
cubiertas por PRAC. Se validaron offsets, solapamientos y unicidad de archivos;
el documento local está en `ner` sin llamadas a Anthropic. La revisión no fue
oración por oración debido al tamaño del informe. La auditoría humana debe
priorizar las 1.001 menciones `medium` y las oraciones sin anotaciones. Los
artefactos están en `data/output/ner_manual/<id>/`, `s3/archivosNER/<id>.json`
y `export/ner_audit/<id>/`; no se ejecutó fuzzy matching.

En una tanda posterior se procesaron cinco IDs: `72d1ae85-0727-42b3-8a1f-26c6289e3cfe`
(*Farmers and Social Innovations in Rural Development*),
`79a0af26-3664-4c73-a94b-43d5477aa93b` (*Agroforestry Systems for Soil
Health Improvement and Maintenance*), `2c2d1176-2630-465f-8e55-714c18cb2570`
(*Farming systems in the Peruvian amazon*),
`0142af8f-efe8-4818-8479-217b1df90d9b` (*Adoption and Diversity of
Agroforestry Systems in the Amazon Biome*) y
`13e119a1-1e65-4023-84bc-f9135cd60cab` (suplemento `.docx` del tercero).
Sus `cleaned` se reconstruyeron desde `converted` y se cotejaron con la
estructura de las fuentes originales. El primero tenía una sección traducida
al español y una respuesta de Anthropic incrustada; se recuperó el orden
inglés y se eliminó el ruido. El segundo y el cuarto carecían de resumen;
se restauraron. El tercero recuperó su resumen completo y corrigió nombres
de organizaciones en una tabla. El suplemento recuperó tablas de factores y
bloques del cuestionario. No se crearon respaldos nuevos del `cleaned`.

La primera extracción NER asistida por reglas y revisión distribuida produjo,
en el mismo orden, 701, 503, 587, 559 y 103 menciones (2.453 en total), con
offsets literales validados. Las 68, 179, 12 y 225 apariciones de
«agroforestry» o «AFSs» se etiquetaron PRAC, salvo 3 y 2 apariciones dentro
de designaciones completas de actores en los dos primeros documentos. El
suplemento no contiene esos términos. Los cinco documentos quedaron en `ner`
sin Anthropic; sus manifiestos, JSON y auditorías siguen el patrón habitual.
La auditoría humana de las cinco primeras pasadas está pendiente; no se
ejecutó fuzzy matching.

El siguiente documento, `1963df4b-4dae-4165-99ea-0f78ceb54844`
(*Assessment of biodiversity goods for the sustainable development of the
chagra in an indigenous community of the Colombian Amazon*), estaba en
`cleaned` y marcado `language=en`. Se cotejó el convertido y el PDF de 14
páginas: se retiraron bibliografía, licencia y material editorial, se
recompusieron oraciones cortadas por pies de figura y columnas, y se mantuvo
la tabla de 38 especies. El `cleaned` anterior se sustituyó sin respaldo. La
primera pasada NER específica del documento produjo 250 menciones en 219
oraciones, con offsets validados y tres apariciones de «agroforestry» en PRAC.
Se guardaron JSON oficial, manifiesto y TSV de auditoría en el patrón habitual;
la DB local quedó en `ner` y no hubo llamadas a Anthropic. La auditoría humana
está pendiente; incluye cinco menciones `medium` y oraciones sin anotación.
No se ejecutó fuzzy matching.

La tanda siguiente de cinco documentos Agroforestry en inglés quedó procesada:
`52c29204-00aa-46c3-bf4a-613dbde8bdb7` (*Restoration through formalization?*),
`da3b78cd-2b7d-476c-8c73-dc3a85b99898` (*Key lessons from Indigenous Peoples
and Local Communities' farming systems*),
`1f2f0bca-2f12-4060-9f63-be48be52c58e` (tesis de Elisabeth Lagneaux),
`260404f5-ad2d-4042-b360-371ee7023d9d` (síntesis sobre cacao) y
`32377694-90d2-4b9c-989f-261ce2c7e222` (propuesta de monitoreo de
biodiversidad). Se corrigieron sus `cleaned` a partir del convertido y la fuente:
material editorial y bibliografía eliminados, cortes de páginas reparados y
anexos OCR ilegibles de la tesis descartados; las fichas de especies se
conservaron. No se guardaron respaldos del `cleaned` anterior. La pasada NER
asistida por reglas específicas produjo respectivamente 142, 284, 560, 428
y 142 menciones (1.556 en total), con fragmentos y offsets validados. Las
apariciones de «agroforestry» y «AFSs» son PRAC salvo cinco designaciones
completas de «agroforestry farmers» (CHAR) en la tesis. Los cinco JSON oficiales,
manifiestos y auditorías TSV están en el patrón habitual. La DB local quedó
en `ner`, sin Anthropic ni fuzzy matching. Auditoría humana pendiente: 1, 8,
8, 5 y 3 menciones `medium`; la tesis requiere especial revisión por sus 405
oraciones sin anotación, que incluyen tablas y metodología.

El siguiente informe del BID, `3facb6fe-5f4e-46a3-b4be-5f304a63b0bd`
(*Amazonian Forest: The Products of Agroecological Systems*), pasó de
`cleaned` a `ner`. Se comparó el convertido con el texto limpio: se retiraron
portadas e índice repetidos, notas al pie incrustadas, tablas OCR ilegibles y
la bibliografía final; se recompusieron oraciones interrumpidas, sin guardar
respaldo del `cleaned` anterior. La primera pasada NER asistida por reglas
específicas dejó 721 menciones en 527 oraciones, con offsets literales y 34
apariciones de «agroforestry» cubiertas por PRAC. El JSON oficial, manifiesto
y TSV de auditoría siguen el patrón `data/output/ner_manual/<id>/`,
`s3/archivosNER/<id>.json` y `export/ner_audit/<id>/`. Estado local `ner`, sin
Anthropic ni fuzzy matching. La auditoría humana está pendiente: 32 menciones
`medium` y 165 oraciones sin anotación; el número de ley transcrito como
«Law 12.625 / 2012» coincide literalmente con el PDF, pero conviene revisar
su exactitud editorial durante la auditoría.

La tanda siguiente de seis documentos Agroforestry en inglés quedó en `ner`:
`35bfba4d-352e-4e55-abfc-292928da3237` (informe NCP de Tambopata),
`58a33d2c-16a9-47aa-a86f-0deddf293290` (cooperativismo en Tomé-Açu),
`702adc1b-1381-4443-8109-61672c4663f5` (sistemas socioecológicos y puntos
de inflexión), `5ce3cf43-99c4-4d5c-a338-5e1c6a3d000f` (chagras de
Monochoa), `600282ba-4314-4fa2-a9c8-fe383c7e56ff` (bancos de semillas)
y `571e5304-5404-4fa6-a82f-a4389652110a` (homegardens de Tomé-Açu).
Se corrigieron los `cleaned`: se eliminó el índice y material editorial del
informe NCP, se unieron pasajes cortados en el artículo cooperativo, se
recuperó desde `converted` el cuerpo perdido del artículo de puntos de
inflexión, se retiró una paráfrasis española de referencias generada por
Anthropic en el artículo de chagras, se normalizaron errores OCR recurrentes
en el estudio de bancos de semillas y se retiró una tabla OCR ilegible del
capítulo de homegardens conservando su prosa adyacente. Se preservaron las
tablas legibles y no se guardaron respaldos del `cleaned` anterior.

La primera pasada NER asistida por reglas produjo respectivamente 507, 383,
127, 227, 147 y 199 menciones (1.590 en total), con offsets validados,
JSON oficiales, manifiestos y TSV de auditoría en el patrón habitual. Todas
las apariciones literales de «agroforestry» restantes están cubiertas por
PRAC; el artículo de puntos de inflexión no contiene esa palabra aunque su
sector registrado sea Agroforestry. No hubo llamadas a Anthropic ni fuzzy
matching. La auditoría humana es prioritaria: los seis tienen 90, 5, 3, 23,
48 y 12 menciones `medium`, y 738, 142, 197, 64, 139 y 22 oraciones sin
anotación. En particular, el informe de Tambopata tiene 420 oraciones
largas sin menciones; es una primera pasada con riesgo de omisiones, no una
extracción revisada exhaustivamente.

La tanda posterior de seis documentos Agroforestry en inglés quedó en `ner`:
`9c6aa0f7-0b55-49ec-a08f-ff4fecf0fcd1` (sequía experimental en cacao),
`7f93c3ee-5816-4250-aced-ce0cca87cc7e` (coproducción de conocimiento
agrícola en Tomé-Açu), `8b3e8649-8fe5-466b-8490-510ec3c33cb6` (uso de
agua en cacao bajo árboles de sombra), `7824b517-d6f6-40ac-869c-af73e98029c8`
(capítulo 30 sobre nueva bioeconomía amazónica),
`7a5d2888-71b1-4805-a042-f01c509990cd` (adopción silvopastoril en el
Amazonas colombiano) y `8d9ec319-2663-42a3-ac22-7e837a2921b9`
(homegardens de la Amazonía oriental). Se repararon los `cleaned` sin respaldo:
se normalizaron signos OCR del estudio de sequía, se quitaron notas/editorial
del estudio de coproducción, se restauró la primera mitad del resumen y se
eliminó la bibliografía del estudio de agua, se recuperó desde `converted`
el capítulo completo de bioeconomía (el anterior perdía la mayor parte y
retenía referencias), y se retiró material editorial de los dos restantes.
La fuente convertida del capítulo de bioeconomía conserva errores OCR
residuales que requieren revisión humana.

La primera pasada NER asistida por reglas produjo respectivamente 84, 288,
50, 755, 197 y 210 menciones (1.584 en total) en 358, 261, 178, 896, 169 y
260 oraciones. Se validaron offsets literales y la cobertura PRAC de todas las
apariciones de «agroforestry»/«AFSs», y se guardaron JSON oficiales,
manifiestos y TSV de auditoría. Los seis estados locales son `ner`, sin
Anthropic ni fuzzy matching. La auditoría humana sigue pendiente, sobre todo
en el capítulo de bioeconomía: 208 menciones `medium` y 423 oraciones sin
anotación. Los otros cinco tienen, respectivamente, 8, 1, 7, 5 y 12
`medium`, y 302, 85, 143, 55 y 128 oraciones sin anotación. En los dos
artículos de agua y cacao abundan oraciones sobre mediciones fisiológicas;
hay que revisar omisiones sin forzar categorías del codebook.

La siguiente tanda de seis documentos ingleses quedó en `ner`:
`a14ca4bd` (sociobioeconomías), `a5b24931` (monitoreo acústico de aves),
`c46f0d74` (presentación de 15 diapositivas), `ca251938` (rentabilidad de
agroforestería), `c2a154e1` (preferencias de productores y PES) y `c60d39ce`
(síntesis técnica de *Theobroma*). Se compararon las fuentes con `converted`
y `cleaned`, se corrigieron los textos limpios sin guardar los anteriores y se
excluyeron créditos, material editorial y listados bibliográficos. En
`c60d39ce` se retiraron los anexos bibliográficos, que explicaban gran parte
de la longitud anterior; en la presentación, mapas y gráficos que solo son
imágenes quedan fuera del NER textual.

La primera pasada asistida por reglas produjo 164, 70, 41, 351, 278 y 749
menciones respectivamente (1.653 en total), con offsets literales y cobertura
PRAC de todas las apariciones de «agroforestry»/«AFSs». Los seis JSON oficiales,
manifiestos y TSV de auditoría están guardados; la base de datos local marca
`ner`. No hubo llamadas a Anthropic ni fuzzy matching. La revisión humana
sigue pendiente: las seis extracciones tienen 42, 19, 0, 4, 31 y 13 menciones
`medium`, y 78, 146, 8, 340, 119 y 726 oraciones sin anotación. Se debe
priorizar la síntesis técnica larga por posibles omisiones, la tesis por sus
tablas y anexos y el artículo acústico por sus términos metodológicos. Este
último no menciona literalmente «agroforestry», aunque su sector registrado
es Agroforestry.

La siguiente tanda de seis documentos Agroforestry ingleses también quedó en
`ner`: `e5b823c9` (historia de sistemas indígenas), `d4e43ea2` (café y
pimienta en Vietnam), `e3d7bf1a` (mito de sostenibilidad del cacao),
`d724a225` (cambio de cobertura en Madre de Dios), `f9d78335` (tesis sobre
propiedad y frontera agrícola) y `da74aa93` (agua en café con sombra). Se
reconciliaron `converted` y `cleaned` sin guardar respaldos: se quitaron
créditos/editorial, se repararon resúmenes y cortes de página, y en la tesis
se retiraron índice, listados de fuentes y formularios de consentimiento;
quedaron el resumen y los capítulos analíticos completos. Las bibliografías
ya estaban fuera de los anteriores `cleaned`.

La pasada NER asistida por reglas produjo 259, 435, 481, 354, 2.985 y 50
menciones respectivamente (4.564 en total). Los JSON oficiales, manifiestos
y TSV de auditoría pasaron validaciones de offsets literales, stopwords,
cobertura PRAC de «agroforestry»/«AFSs» y unicidad de archivos por etapa.
Los seis estados locales son `ner`; no se llamó a Anthropic ni se hizo fuzzy
matching. La auditoría humana sigue pendiente: 71, 0, 4, 4, 102 y 2 menciones
`medium`, con 121, 241, 142, 88, 1.177 y 470 oraciones sin anotación. Hay
que priorizar la tesis larga y el estudio de agua con sombra: en este último
predominan mediciones fisiológicas fuera de las categorías del codebook, pero
la baja cobertura merece revisar posibles omisiones. El estudio de Vietnam
tiene una sola mención literal de «agroforestry» pese a su sector registrado.

La tanda de tres documentos ingleses `d755356e` (deforestación por minería
de oro), `ef62dfe2` (taller TESSA sobre servicios ecosistémicos) y
`e8355e39` (chakras amazónicas ecuatorianas) quedó en `ner`. Se corrigieron
los `cleaned` sin respaldo: se eliminó la bibliografía retenida del artículo
de minería, se quitaron créditos y contenido editorial del taller y se
recompusieron dos frases del artículo sobre chakras interrumpidas por figuras.
Las bibliografías de los otros dos ya estaban fuera del texto limpio.

La primera pasada NER asistida por reglas registró 340, 112 y 187 menciones
respectivamente (639 en total); validó offsets literales, cobertura PRAC de
«agroforestry»/«AFSs» y unicidad de archivos por etapa. Los tres JSON
oficiales, manifiestos y TSV de auditoría están guardados y la base de datos
local marca `ner`, sin Anthropic ni fuzzy matching. La revisión humana sigue
pendiente: los tres tienen 0, 0 y 3 menciones `medium`, y 42, 57 y 114
oraciones sin anotación. El artículo de minería no menciona literalmente
«agroforestry» a pesar del sector Agroforestry registrado; conviene revisar
la pertinencia de ese metadato.

Después se corrigió `language` de `en` a `es` en cuatro documentos que tienen
contenido principal en español: `32eea2e1-16cd-44f1-ae54-84f48724c85e`,
`6352ebd0-0859-4e5b-8eef-19957451abc3`,
`c7cdf424-28ff-458b-84fa-cfc1714dc85e` y
`e6607e5e-b6d7-4a1e-84db-8eb8aedc2be3`. El corpus local Agroforestry queda
con 66 `es`, 48 `en` y 1 `pt`. Estos cuatro siguen en `cleaned`, pero no formaron
parte de la regeneración inicial de 62. Se auditaron y corrigieron después:
`6352ebd0` y `e6607e5e` tenían respuestas de Anthropic incrustadas; el resumen
anterior de `6352ebd0` decía 60 productores aunque la fuente reporta 183
entrevistas. `c7cdf424` y los demás recuperaron texto sustantivo desde
`converted`; se retiraron bibliografías, resúmenes ingleses duplicados y
material editorial. `32eea2e1` es una conversación de búsqueda de literatura,
no un estudio primario: se dejó su síntesis textual sin el diálogo ni las tablas
de fuentes, pero su validez como evidencia para NER requiere decisión humana.

La auditoría encontró además que la regla de autoría descartaba párrafos largos
que mencionaban varias palabras institucionales. Se limitó esa regla a líneas
cortas y se regeneraron 29 de los 62 documentos españoles previos para recuperar
párrafos omitidos. El registro de los 33 archivos actualizados está en
`export/auditoria_y_correccion_es_2026-11-02.csv`. Los 66 documentos españoles
siguen en `cleaned` y sin `ner_path`; no se guardaron copias nuevas del texto
anterior.

### Metadatos del corpus local — 27 Oct 2026

Se registraron y verificaron `language`, `year` y `document_type` para los
116 documentos que entonces tenían `productive_sector = Agroforestry` en
PostgreSQL local, usando la tabla suministrada por la usuaria. Idiomas: 62 `es`,
53 `en` y 1 `pt`; años entre 2001 y 2026. `document_type` conserva literalmente
los valores de la tabla, incluidos `Other`, `WA SAM Hub` y nombres de autores o
revistas. La última columna `Other` fue descartada por indicación de la usuaria;
no se escribió metadata. Se comprobaron los tres campos después del commit y
que el resto de los campos y documentos permanecieran intactos.

Se corrigieron dos UUID transcritos incorrectamente por el asistente en la
lista original, comprobando el nombre del documento en la DB:
`1f2f0bca-2f12-4060-9f63-be48be52c58e` (tesis de Elisabeth Lagneaux) y
`8d9ec319-2663-42a3-ac22-7e837a2921b9` (Plant Composition and Species Use).
Tabla recibida, CSV validado, respaldo previo, importador y reporte de la carga
están en `export/metadata_2026-10-27/`, excluido de Git. La migración local es
`e9f0a1b2c3d4`: `year` admite 1990–2030 y `document_type` es texto libre de hasta
50 caracteres. Esta carga solo actualizó la base local; no sincronizó AWS.

### Explorador de entidades — 26 Oct 2026

En paralelo al codebook, la rama `feat/explorador-entidades` añade la API de
lectura `/analysis/explorer/v1/*` para un dashboard interactivo en un repositorio
de frontend aparte. Enlaza las diez categorías, filtra por recurrencia documental,
peso y centralidad, y compara rankings entre 2021–2023 y 2024–2026. La meta-red
queda en espera. Ver `../sessions/2026-10-26-explorador-entidades.md`.

### Punto de reanudación — 16 Oct 2026

La usuaria descartó el mecanismo few-shot porque el codebook ya define la tarea completa. El servicio carga directamente `data/codebooks/codebook_en_construccion_en.md`, configurado mediante `NER_CODEBOOK_PATH`, y lo inserta en `$codebook` de la plantilla única `data/prompts/ner_prompt.md`. La misma plantilla incluye `$json_input` con las oraciones del bloque; `ner.py` envía el resultado como un mensaje de usuario, sin prompt de sistema separado. Se retiraron `ner_user_prompt.md` y `NER_USER_PROMPT_PATH`. Se eliminaron el archivo de demostraciones, su cargador y `NER_FEW_SHOT_PATH`; ya no se inyectan las definiciones de `src/categories.py` en el prompt. La taxonomía conserva los diez códigos para el esquema y la validación local. Los ejemplos internos del codebook permanecen como parte de sus reglas. La versión española de la raíz se conserva como antecedente; la fuente operativa es la inglesa en `data/codebooks/`.

Los resultados del piloto anterior corresponden al flujo con demostraciones y no validan esta nueva estrategia. El script de validación registra `prompt_strategy: codebook-single-prompt` y exige coincidencia de esa estrategia y del codebook para reanudar respuestas guardadas. Al iniciar/reiniciar la API se recarga el prompt con el codebook; las ediciones no sustituyen automáticamente su caché en memoria.

Comprobación local del cambio: 110 pruebas ejecutadas, 108 exitosas y 2 omitidas por dependencias opcionales de Leiden. Se verificaron la carga del codebook completo, la ausencia de demostraciones externas, el fallo previo a contactar al proveedor si falta el codebook o está vacío, y el formato sin saltos internos de párrafo. Se preparó inicialmente el piloto sin demostraciones y después se unificó la plantilla; no se ejecutó una nueva extracción real ni se reinició la API.

### Antecedente — reglas y piloto del 16 Oct 2026

Se revisaron los cambios guardados antes de nuevas ediciones y se crearon
los commits `56e2526` (codebook y documentación) y `7e6ff24` (definiciones,
prompts y ejemplos) de la sesión anterior. Se leyó completa la sección 6,
incluidas 6.1–6.3, y se contrastó con fichas, prompt y parser.
El borrador 0.2 completa las reglas generales y las secciones 7–10 y anexo A:
fragmentos mínimos literales, siglas separadas, enumeraciones sin reconstrucción,
una categoría por aparición, negación en contexto y niveles de ambigüedad.
La única anidación admitida es LOC estrictamente dentro de CHAR; el parser
ya la conserva en ambos órdenes, también con repeticiones. No se implementó
resolución de siglas ni relaciones dentro de NER.

La validación real se ejecutó mediante `scripts/validate_ner_document.py`,
con respuestas reales de Anthropic y artefactos separados en
`data/output/ner_pilot/`. El script no abre conexiones ni escribe en la DB.
Docker está detenido; no se comprobó el endpoint de la API en ejecución.
NER tiene cachés de prompt en memoria: iniciar/reiniciar la API al validar
su endpoint con las nuevas instrucciones.

Piloto real: informe de biocarbón `6f98dc30-3b28-42aa-b519-497cec4c8627`,
5.267 caracteres, 42 oraciones y 13 bloques. Las dos extracciones completas
produjeron 74/68 y 86/77 anotaciones recibidas/conservadas, respectivamente,
con descartes por solapamiento. Se incorporó validación estricta al servicio,
con hasta dos correcciones por bloque y fallo explícito si persisten errores.
Las ejecuciones con ese control se detuvieron en el bloque que comienza
en 2113: el modelo insiste en añadir CHAR «UNAMAD» dentro de CHAR
«estudiantes de la UNAMAD». Los resultados completos previos son evidencia
de desarrollo, no extracciones aceptadas. El corpus no se ha procesado.
Hay también errores semánticos para revisar: «podas» usadas como residuos,
hornos productivos clasificados como infraestructura física, sedes usadas
como actores y fragmentos explicativos demasiado amplios.

Regresiones: 108 pruebas ejecutadas, 106 exitosas y 2 omitidas por las
dependencias opcionales de Leiden. Los cambios del 16 Oct se registran en
Git por solicitud de la usuaria. La agenda vigente está en `tasks.md`; la evidencia se resume
en `../sessions/2026-10-16-revision-seccion-6-y-piloto.md`.

### Antecedentes de la revisión — 15 Oct 2026

La usuaria está realizando una última revisión del codebook, ahora junto con
el prompt. Confirmó que NER debe dedicarse exclusivamente a extraer y
clasificar menciones. Fuzzy matching y construcción de relaciones son tareas
posteriores mediante endpoints independientes y consecutivos. Se precisó ese
alcance en las secciones 1 y 3 y en ambos prompts NER, conservando el contrato
de cuatro campos. El código ya exige `ner` antes de fuzzy matching y
`fuzzyMatching` antes de construir la red del documento.

La sección 2.4 contiene los dos párrafos aprobados sobre contexto territorial
y temático del corpus. El informe de Tambopata fue un insumo para comprender
ese contexto; la usuaria pidió que las instrucciones sean autónomas y que no
describan ni dependan de ese informe. Se retiraron también las referencias al
informe de la sección 2.5 y el anexo bibliográfico se conservó en la sesión
`../sessions/2026-10-15-codebook-autonomo.md`. La limpieza editorial elimina
referencias a «la usuaria» y al proceso de elaboración, sin cambiar las diez
definiciones ni aprobar propuestas pendientes. Ambos prompts usan instrucciones
autónomas; el de sistema explicita que no se consulten documentos externos.
En la sección 3, la usuaria ya escribió definición de mención, unidad de
anotación, contexto permitido y evidencia. La sección 4 incluye la regla de
omitir expresiones fuera de las categorías y conservar la grafía de los códigos.
En KNOW se confirmó reservar la etiqueta para contenidos que el texto
identifique como saberes o mediante atribución de conocimiento. Una afirmación
informativa o descripción territorial no basta por sí sola. Se admite el saber
sin portador identificado. La regla está en la ficha 5.2 y en `src/categories.py`,
cuya definición se incorpora al prompt. La ficha recoge también los criterios
de exclusión, frontera con ATT y extracción del contenido del saber; el
pendiente general fue sustituido por esas reglas durante la revisión.
La delimitación de ATT fue aprobada y aplicada en la ficha 5.3 y la definición
que se incorpora al prompt: evidencia explícita y atribución a un actor,
exclusión de descripciones factuales, saberes o actividades por sí solos,
actitudes favorables/desfavorables/ambivalentes y extracción de la actitud con
su objeto. El ejemplo productoras/compromiso ya está en las demostraciones.
Se retiró el pendiente general de ATT; esto no completa las demás fichas.
La delimitación de SKILL también fue aprobada y aplicada en la ficha 5.4 y
`src/categories.py`: competencia atribuida a un actor; conocer, querer o actuar
no basta por sí solo; permiso, recursos u oportunidad tampoco demuestran
habilidad. La palabra «puede» requiere evidencia contextual de competencia.
Se extrae la habilidad con su tarea, conservando la atribución en contexto.
Se retiró el pendiente general de SKILL; el ejemplo ya está en las demostraciones.
Por petición de la usuaria, se completaron las fichas 5.5–5.10: PRAC,
physical_INFRA, soft_INFRA, eco_INFRA, RUL y LOC. Incluyen evidencia, exclusiones,
delimitación literal, fronteras y ejemplos, sin pendientes dentro de esas fichas.
PRAC conserva actividades propuestas, futuras o negadas sin afirmar ejecución;
infraestructura se clasifica por función; eco_INFRA exige respaldo textual de
su función ecológica; RUL incluye reglas formales o informales con función
reguladora y conserva la negación en prescripciones; LOC admite denominaciones
genéricas con referente espacial reconocible y mantiene los ejemplos San Pedro.
Las síntesis están en `src/categories.py`, incorporadas al prompt. Se precisó
la función de la plataforma digital en la demostración soft_INFRA, conservando
diez ejemplos. Siguen pendientes las reglas generales y la validación del
codebook; la anidación LOC/CHAR continúa requiriendo adaptación del parser.
Continuar paso a paso, con respuestas breves, revisando codebook y prompt juntos.

### Acuerdos y comprobaciones anteriores — 12 Oct 2026

El foco acordado con la usuaria es definir las características específicas
que deben identificar las menciones para clasificarse en cada categoría:
rasgos esenciales, inclusión, exclusión, evidencia textual y fronteras.
La usuaria pidió frenar la sucesión de casos de delimitación y nombres
individuales. No seguir abriendo casos de artículos, siglas, enumeraciones
o normalización mientras se revisan los criterios de clasificación.

El conjunto de diez categorías es una decisión final de la usuaria:
CHAR, KNOW, ATT, SKILL, PRAC, physical_INFRA, soft_INFRA, eco_INFRA, RUL y LOC.
El código de extracción ya establece esas diez categorías en
`src/categories.py`; esquema estructurado, parser, prompt y validación de
canonicalización usan la misma fuente. INFRA se admite solo al procesar legado,
sin reclasificar automáticamente registros antiguos.
Las definiciones de las diez categorías ya están acordadas. CHAR reúne
ahora una síntesis de sus criterios aprobados en la sección 5.1. No se
presupone que las demás fichas ni todas las fronteras estén completas.
Los ejemplos se usan únicamente cuando aclaran un criterio general.

Se conservan los acuerdos de extracción, anidación LOC dentro de CHAR,
registro de cada aparición y vinculación posterior de nombre completo
y sigla al mismo nodo canónico. Las reglas de extracción de CHAR están
reunidas en la sección 6.3. El último fragmento confirmado es
«cooperativa La Esperanza», con el nombre propio íntegro.

También se mantiene el criterio aprobado para planes en RUL: el contexto
debe presentarlos como instrumentos que establecen condiciones,
responsabilidades o criterios para las prácticas territoriales.

La usuaria precisó después que necesita un codebook más básico, considerando
el uso eficiente de Claude, y pidió revisar primero el código para aprovechar
la estructura de persistencia existente. La revisión identificó el contrato
NER de cuatro campos por mención (`label`, `text`, `sentence_id`, `ambiguity`),
el enriquecimiento local y la persistencia posterior a la canonicalización.
Los modelos y las comprobaciones locales se documentan en
`../sessions/2026-10-12-revision-contrato-ner.md`; no se inspeccionó la DB
en ejecución ni se hicieron llamadas a Claude.

El codebook puede apoyarse en ese contrato y centrarse en las diez categorías
y sus criterios esenciales. La adaptación local del 12 Oct actualizó código,
prompt y demostraciones: diez ejemplos ilustrativos sustituyen los 25 del
esquema anterior. La red completa y su visualizador admiten las diez categorías;
los artefactos históricos pueden conservar INFRA. La proyección versionada
`prac-infra-rul-v2` conserva su selección histórica PRAC/INFRA/RUL y no representa
el nuevo conjunto completo. No se cambiaron datos, migraciones ni servicios
en ejecución. Pruebas locales: 101 ejecutadas, 99 exitosas y 2 omitidas por
dependencias opcionales de Leiden; proveedor y DB simulados.

El parser aún descarta anidaciones y el nombre completo con sigla no se unifica
automáticamente sin alias previo en el caso comprobado. Estas reglas no se
implementaron en la adaptación de categorías. La limpieza mantiene llamadas
propias a Claude. Consultar `tasks.md` y
`../sessions/2026-10-12-implementacion-diez-categorias.md`. Mantener respuestas breves.

Como antecedente técnico, la promoción de comunidades Leiden aceptadas a nodos
semánticos y la construcción determinista de conexiones intercluster están
implementadas. Sus verificaciones y pendientes anteriores se conservan más
abajo, pero no son el punto de continuidad del trabajo del codebook.

### Antecedente operativo — 28 Sep 2026

La sesión más reciente volvió temporalmente al Objetivo 1 para preparar una
nueva ingesta en Postman. La API y PostgreSQL están activos en Docker y la
migración vigente es `c6d7e8f9a0b1 (head)`. Ya se puede iniciar la carga de
documentos. El siguiente paso de la usuaria es ejecutar una carga real con
`POST /documents`, revisar la respuesta `201` y conservar el `document_id`.

En esa carga solo son obligatorios el archivo y `incubator_number`. `language`,
`year`, `productive_sector`, `document_type` y `metadata` pueden omitirse. Los
tres atributos de clasificación pueden completarse posteriormente con el PATCH
descrito en la sección de arquitectura. No se debe añadir `incubator_number` a
la URL ni fijar manualmente `Content-Type`; los datos se envían por `form-data`.

## 2. Arquitectura general

La aplicación es un servicio FastAPI ejecutado con Uvicorn, PostgreSQL 16 con pgvector, SQLAlchemy 2 y Alembic. Docker Compose coordina los servicios. El almacenamiento local de artefactos usa `s3/`.

La ingesta exige `incubator_number`; `year`, `productive_sector`,
`document_type`, `language` y `metadata` son opcionales. Los tres atributos de
clasificación pueden completarse después mediante
`PATCH /documents/{document_id}/classification` con cuerpo `form-data`, sin
reprocesar el documento. `year` admite cuatro dígitos, el sector controlado
vigente es `Agroforestry` y el tipo documental se elige entre `academic`,
`technical_report`, `project_report`, `policy_document`, `manual_or_guide`,
`institutional_document` y `other`. Las columnas nuevas permiten `NULL` solo
para conservar los registros sin clasificación disponible.

El flujo principal es:

```text
documentos
  -> conversión y extracción de texto
  -> limpieza
  -> NER estructurado (Claude few-shot)
  -> fuzzy matching y canonicalización
  -> menciones persistidas con oración y contexto
  -> evidencia entidad–oración
  -> proyecciones de coocurrencia
  -> backbone/configuración
  -> proyección PRAC/INFRA/RUL y Leiden
  -> nodos semánticos y conexiones intercluster
  -> asociación de CHAR/LOC y descripción editorial de conexiones (pendiente)
```

Las categorías NER actuales son `CHAR`, `KNOW`, `ATT`, `SKILL`, `PRAC`,
`physical_INFRA`, `soft_INFRA`, `eco_INFRA`, `RUL` y `LOC`.
`RUL` identifica reglas, normas e instrumentos institucionales concretos, tanto
formales como informales: leyes, reglamentos, políticas, planes, acuerdos,
contratos, permisos, estándares y reglas comunitarias. La gobernanza permanece
como concepto de análisis, pero no como categoría NER. `GOV` es una etiqueta
histórica sustituida por `RUL`; solo se conserva en migraciones, procedencia y
lectura compatible de artefactos anteriores. `INFRA` también queda reservado
al legado: dividir sus menciones requiere revisar el contexto. La proyección
registrada `prac-infra-rul-v2` conserva su definición histórica.

## 3. Evidencia y modelo de coocurrencia

- La coocurrencia se agrupa por `(document_id, sentence_id)`.
- Una oración con `N` entidades proyectadas genera la clique completa de pares no dirigidos.
- `sentence_entities` conserva todas las entidades de la oración, incluidas `CHAR` y `LOC` aunque no pertenezcan a la topología PRAC–INFRA–RUL.
- `edge_observations` conserva la evidencia de cada pareja: documento, oración, contexto, pareja de entidades, texto y ambigüedad.
- Las aristas agregadas conservan `sentence_count`, `document_count`, métricas fraccionales, `category_pair` y niveles de confianza; por tanto, la arista puede remontarse a sus observaciones sin depender únicamente de `weight`.

La base de datos persiste las menciones canonicalizadas con `document_id`, `sentence_id`, `canonical_id`, categoría, texto/contexto, ambigüedad y offsets. La información de oración no se reconstruye únicamente durante `/analysis/network`.

## 4. Auditorías de canonicalización

- `SM T1.docx` fue retirado completamente del conjunto de trabajo.
- Se unificaron únicamente los alias solicitados de Wyss bajo `Wyss Academy for Nature`: `The Wyss Academy for Nature`, `Wyss Academy for Nature`, `Wyss Academy`, `WYSS Academy`, `Wyss`, `WYSS`, `Wyss Academy for Nature WYSS`, `Wyss Academy (WA)` y `Wyss Academy Hub SAM`.
- No se fusionaron entidades del tipo `socios ...` ni otros nombres no incluidos explícitamente.
- Las redes históricas no se destruyen; las nuevas construcciones se escriben en rutas versionadas.

El 3 Nov 2026 se inició una auditoría supervisada del endpoint antes de pasar
los 48 documentos Agroforestry en `ner` a `fuzzyMatching`. El inventario
conserva 23.135 menciones y 3.584 formas literales; se contrastó con las
entidades y alias de 78 documentos históricos ya canonicalizados. El archivo
`outputs/fuzzy_matching_2026_11_03/revision_canonicos_agroforestry.xlsx`
contiene 17 grupos propuestos, 207 filas de variantes, 35 colisiones de
categoría y el inventario completo en su primera versión. El endpoint no se
ejecutó sobre los 48 documentos nuevos; las correcciones confirmadas se
aplicaron directamente a los registros históricos afectados.

El endpoint `deterministic-v3` busca candidatos solo en la categoría recibida
del NER; no corrige etiquetas erróneas. En el inventario inicial, el legado
contenía `WA SAM Hub` como CHAR y LOC, y `agroforestry systems` como PRAC y LOC.
`WA` aparece
vinculado a más de un canónico CHAR. La forma sugerida por la usuaria
`systems agrofostry` no está observada literalmente y puntúa 94,74 frente a
`Agroforestry Systems`, por debajo del umbral PRAC 96. Las decisiones sobre
el hub regional frente a la institución principal, siglas cortas y
agroforestería general frente a sus subtipos quedan pendientes de revisión
con la usuaria antes de crear reglas de alias adicionales.

En la misma auditoría, la usuaria confirmó que `Wyss Academy` y `WA SAM Hub`
no son LOC, y que `agroforestry systems` tampoco es LOC. Se corrigió una
mención histórica de `WA SAM Hub` a CHAR y cuatro de `agroforestry systems`
a PRAC, tanto en PostgreSQL como en sus JSON de NER; se reutilizaron los
canónicos CHAR y PRAC ya existentes. Se eliminaron los canónicos LOC que
quedaron sin referencias, incluido `Wyss Academy` LOC (que ya estaba huérfano),
y dos canónicos huérfanos adicionales de `agroforestry systems` en CHAR y
eco_INFRA. El fuzzy matching ahora rechaza las formas institucionales
inequívocas con categoría distinta de CHAR y la forma exacta
`agroforestry systems` con categoría distinta de PRAC. El codebook y prompt
incluyen estos ejemplos. La versión intermedia del libro tenía 200 variantes
seleccionadas y 33 colisiones; las uniones de alias/canónicos y otros
conflictos siguen pendientes.

La actualización integral del mismo libro amplió el análisis a **todas** las
23.135 menciones NER de los 48 documentos Agroforestry en `ner`: 3.584 formas
literales, 3.098 grupos canónicos propuestos y 14.981 menciones (64,8 %) en
grupos con dos o más formas. De ellas, 6.299 (27,2 % del total) participan en
uniones entre grafías normalizadas distintas mediante familias controladas;
las demás uniones se basan principalmente en mayúsculas, tildes y espacios.
Se separaron explícitamente general/subtipo, AFSs-A/AFSs-F, chagra/chakra y
Amazon/Amazon Basin/Amazon region. El libro contiene hojas `Resumen`,
`Canónicos`, `Variantes`, `Conflictos` y `Legado clave`; esta última conserva
las 17 preguntas y 121 variantes históricas/ejemplos de la revisión inicial.
La base histórica se consultó solo como evidencia: 18 grupos tienen varios
canónicos coincidentes; 48 grupos contienen formas presentes en más de una
categoría NER. Ninguna propuesta equivale a aprobación; al preparar el libro
todavía no se había ejecutado el endpoint.

Después, por instrucción explícita de la usuaria, se ejecutó
`POST /documents/{id}/fuzzy-matching` en los 48 Agroforestry que estaban en
`ner`. Quedaron 48 en `fuzzyMatching` y 67 en `cleaned`. PostgreSQL contiene
23.135 entidades de ese lote, idénticas en número a los JSON fuente para
cada documento; hay cero diferencias entre categoría de mención y categoría
canónica. Distribución de métodos: 16.958 exact, 4.888 new, 780 stored_alias,
376 fuzzy, 66 controlled_alias, 66 morphology y 1 person_name. El endpoint
no aplicó las propuestas del Excel: en la comparación posterior, 25 grupos
de variantes propuestos quedaron divididos entre varios canónicos (5.717
menciones); por ejemplo `farmers`, `Amazon` y `Agroforestry systems`. El
registro está en `data/output/fuzzy_audit_2026_11_03/endpoint_batch_2026_11_03.jsonl`
y la comparación en `postrun_comparison.json` de la misma carpeta.

Para la auditoría documento por documento se añadió
`GET /documents/{id}/entities`: consulta directamente las menciones
persistidas y devuelve texto literal, contexto, categoría, canónico,
método/puntaje y detalles de resolución, junto con nombre original del
archivo, estado y total. Admite `skip`, `limit` (máximo 1000), `category`,
`match_type`, `canonical_id` y `q` (búsqueda textual en mención o canónico).
Es de solo lectura y no requiere construir la red. Se verificó en Docker
con un documento real de 505 menciones, paginación, filtros, 404 y 422.
Al revisar el GET en Postman se añadieron al resumen `productive_sector`,
`document_total`, `category_counts`, `match_type_counts` y `applied_filters`
para distinguir un documento sin entidades de un filtro combinado sin
coincidencias. En `c13401cf-aca9-4cbb-846a-803b6b330d3a`, la combinación
`category=PRAC&match_type=fuzzy&q=Agroforestry` da `total=0`, aunque el
documento tiene 318 entidades (59 PRAC y 6 fuzzy por separado).

## 5. Decisiones metodológicas de la red tipada

La proyección `prac-infra-rul-v2` incluye los seis pares no dirigidos:

`PRAC--PRAC`, `PRAC--INFRA`, `PRAC--RUL`, `INFRA--INFRA`, `INFRA--RUL` y `RUL--RUL`.

Se permiten relaciones intratipo y entre tipos. Las vistas disponibles son `all`, `cross`, `intra` y las seis vistas de pares individuales. `CHAR` y `LOC` quedan fuera de la topología inicial para evitar ruido, pero permanecen en la evidencia y se asociarán después a los clusters mediante sus oraciones de soporte.

No se adopta `weight >= 3` como definición universal del backbone. En la red española, ese corte elimina gran parte de la estructura y sesga el resultado hacia `PRAC--PRAC`. La construcción aprobada usa recurrencia documental de nodos:

```text
un nodo es elegible si document_count >= mínimo configurado
una arista se conserva si ambos extremos son elegibles
```

El valor `edge.document_count >= 2` se conserva como señal de confianza (`transversal`), no como requisito universal de inclusión. Se mantiene el conteo crudo de oraciones y se elige una métrica analítica explícita para el peso.

## 6. Contrato de construcción parametrizable

El endpoint heredado `POST /analysis/network` sigue construyendo la red raw con sus parámetros históricos (`minimum_weight`, `include_isolates`).

La proyección tipada usa `POST /analysis/network/projections/{projection_id}`. El contrato aprobado para el backbone documental es:

```json
{
  "incubator_number": "all",
  "language": "es",
  "construction": {
    "method": "document-recurrent-core-v1",
    "minimum_node_document_count": 2,
    "edge_weighting": "fractional-document",
    "include_minor_components": true
  }
}
```

También se mantiene la construcción compatible `raw-threshold-v1`. La construcción documental implementada incluye:

- elegibilidad de nodos por número de documentos;
- inducción de aristas entre nodos elegibles;
- `fractional_weight`, ponderado por oración como `1/(N_s-1)`;
- `fractional_document_weight`, limitado a una contribución máxima por documento;
- `independent_support_count`, basado en soportes contextuales independientes;
- niveles `transversal`, `recurrent-local` y `exploratory`;
- selección de `analysis_weight` para el atributo GraphML estándar `weight`.

Las métricas de todas las vistas continúan en la respuesta, pero la publicación
oficial usa una única vista canónica: `main-component/all`.

## 7. Almacenamiento oficial de grafos

La raíz vigente es `s3/graphs/`, dividida en `graphml/`, `json/` y `csv/`.
Cada formato repite la misma jerarquía de alcance:

```text
corpus/{es|en|all}/
incubators/{number}/{es|en|all}/
documents/{document_id}/
```

Los nombres oficiales son `main_network`, `backbone_<projection_id>` y
`leiden_<projection_id>`. Los parámetros viven en el JSON de metadatos. Los CSV
de red usan los sufijos `_nodes` y `_edges`; los de Leiden, `_communities` y
`_members`.

Cada ejecución reemplaza atómicamente el nombre estable. Ya no se publican PNG,
SVG, HTML, Matrix Market, JSON completos del grafo, manifiestos duplicados,
vistas materializadas ni CSV de evidencia. La evidencia se consulta directamente
en PostgreSQL.

`s3/archivosRed/` conserva los artefactos históricos y no se elimina hasta
validar las nuevas ejecuciones; no es la ubicación usada por el código vigente.

## 8. Estado de implementación y calidad

Implementado en código:

- `src/analysis/backbone.py` — construcción de backbones analíticos;
- `src/analysis/graph_export.py` — exportación mínima GraphML + CSV + JSON;
- `src/analysis/graph_paths.py` — rutas y nombres estables de `s3/graphs/`;
- `src/analysis/leiden.py` — clustering reproducible con atributos para Gephi;
- esquemas de red en `src/api/schemas/network.py`;
- integración de servicio en `src/services/network.py`;
- rutas en `src/api/routers/analysis_networks.py`;
- tabla `sentences` en `src/models/sentences.py` y `src/models/sentences_repo.py`;
- persistencia de oraciones durante fuzzy matching en `src/services/documents.py`;
- migración `d7e8f9a0b1c2_add_sentences_table.py`;
- pruebas en `tests/test_backbone.py`, `tests/test_leiden.py`,
  `tests/test_network_service.py`, `tests/test_graph_paths.py`,
  `tests/test_sentences_repo.py` y `tests/test_network_visualization.py`;
- ejemplo del contrato en `postman_collection.json`.

La suite contiene 98 pruebas: 96 pasan y 2 se omiten porque este entorno no tiene
instalados `igraph` y `leidenalg` (ambos están en `requirements.txt`).
La generación bajo `s3/graphs/` está implementada y validada por tests; la
ejecución real sobre el corpus completo queda pendiente antes de retirar el
almacenamiento histórico.

## 9. Próximos pasos técnicos

1. Regenerar los artefactos oficiales del backbone y Leiden para
   `prac-infra-rul-v2`, registrar su nuevo SHA-256 y volver a vincular los
   meta-nodes a esa partición exacta.
2. Revisar humanamente los títulos y descripciones generados para los meta-nodes;
   corregirlos y aceptarlos cuando corresponda.
3. Crear el prompt editorial separado para describir conexiones intercluster ya
   calculadas, usando evidencia trazable y sin atribuir causalidad por coocurrencia.
4. Asociar `CHAR` y `LOC` a cada configuración mediante las oraciones que soportan
   sus entidades miembro.

Leiden y la construcción de la meta-red están implementados. La metodología
aprobada para las conexiones intercluster se describe en la sección 11.

## 11. Promoción de comunidades a nodos semánticos

El prompt editorial está en `data/prompts/semantic_node_prompt.md`. Describe las
relaciones internas respaldadas por entidades, aristas y oraciones; no clasifica
pathways ni evalúa el carácter transformador.

La implementación actual añade `semantic_nodes` y `semantic_node_members` mediante
la migración `f2b3c4d5e6f7`. Los endpoints especializados bajo `/semantic-nodes`
permiten consultar la partición Leiden publicada y su SHA-256, promover una
comunidad explícita, listar/leer/editar nodos y generar su título y descripción
con Claude. La promoción conserva miembros, alcance, configuración, huellas de
procedencia y soporte documental por incubadora. El texto generado queda en
`draft` hasta su aceptación humana. La construcción determinista de relaciones
entre nodos usa la fórmula `meta-network-relationship-v1`, importa la instantánea
del GraphML exacto a `semantic_network_source_edges` y agrega en PostgreSQL hacia
`semantic_node_relationships`. Claude no participa en la existencia ni el peso de
estas relaciones.

Una conexión no dirigida entre dos meta-nodes registrados existe si al menos una
arista fuente que supera `minimum_source_edge_weight` conecta entidades miembro de
ambos meta-nodes. El umbral predeterminado es `0`, por lo que cualquier arista
fuente positiva basta. El peso de la conexión es la suma de los atributos `weight`
de sus aristas fuente. `source_edge_count` cuenta aristas entre pares de entidades;
`sentence_support_sum` y `document_support_sum` son sumas de los soportes de esas
aristas, no cantidades únicas de oraciones o documentos. La conexión es una
agregación estructural de coocurrencias entre entidades miembro: no afirma una
relación causal, funcional ni una coocurrencia literal entre los meta-nodes.

La configuración metodológica aprobada exige `require_accepted_nodes=true`:
participan solo meta-nodes registrados y aceptados. Las comunidades no promovidas
quedan fuera de esta meta-red; su ausencia no significa que carezcan de aristas en
el grafo fuente. La validación del corpus español registró 40 meta-nodes, 96
conexiones y 836 aristas fuente contraídas sobre la partición histórica GOV v1.

La migración `b5c6d7e8f9a0` cambia las categorías persistidas y la proyección
semántica a `prac-infra-rul-v2`; `c6d7e8f9a0b1` normaliza también los pares de
categoría en la instantánea de aristas. No se modificaron los artefactos de
`s3/`: allí sigue el GraphML oficial español `prac-infra-gov-v1` de 66
comunidades. Por eso `GET /semantic-nodes/leiden-source` con `artifact_source=official`
responde 404 hasta regenerar los artefactos oficiales RUL v2.

Las filas existentes de nodos y relaciones conservan los hashes de sus GraphML
GOV v1 aunque su `projection_id` se haya migrado. No constituyen una partición
RUL v2 regenerada. La fuente histórica `accepted-2026-08-25` sigue disponible y
el servicio normaliza `GOV` a `RUL` en memoria al leerla; contiene 21 comunidades.

## 10. Referencias de trabajo

- Arquitectura: `.agent/context/architecture.md`
- Tareas: `.agent/context/tasks.md`
- Deuda técnica: `.agent/tech-debt.md`
- Sesiones: `.agent/sessions/`
- Artefactos oficiales de grafos: `s3/graphs/`
- Código de servicios: `src/services/network.py`
- Router: `src/api/routers/analysis_networks.py`
- Esquemas: `src/api/schemas/network.py`
- Construcción backbone: `src/analysis/backbone.py`
