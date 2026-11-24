# Contexto actual del proyecto

Este documento resume el estado metodológico y técnico del proyecto de clasificación semántica y construcción de redes. Es el contexto estable de trabajo para la fase actual; las decisiones y resultados puntuales de cada sesión se mantienen en `.agent/sessions/`.

## 1. Propósito y fase actual

El proyecto transforma documentos de los incubadores en una base de entidades canónicas y redes semánticas auditables. La unidad de evidencia es la oración: las relaciones entre entidades se derivan de su coocurrencia dentro de `(document_id, sentence_id)` y deben poder rastrearse hasta el documento, la oración, el contexto y las entidades originales.

La fase actual trabaja con las redes de **59 documentos publicados**. Las
exclusiones y KAS ya están desplegados. El 24 Nov se sincronizaron 11 JSON NER
nuevos y, por instrucción posterior de la usuaria, se procesó fuzzy matching
antes de retomar el vocabulario controlado. Mac y AWS conservan los mismos
UUID y datos resueltos. Los clusters y las metaredes existentes, calculados
sobre los 48 documentos anteriores, quedan en espera y se conservan intactos.
Continúa pendiente diseñar el vocabulario
controlado y aplicar acuerdos al endpoint `fuzzy-matching`. El codebook operativo
está en `data/codebooks/codebook_en_construccion_en.md`. Sus diez categorías,
fichas y reglas de anotación están desarrolladas en el borrador 0.4.
El codebook sirve como especificación
para la extracción y clasificación mediante LLM en la API, con posterior
canonicalización, atributos de nodos y análisis de coocurrencia.

### Exclusión explícita de Agroforestry Systems — 24 Nov 2026

La usuaria señaló en la web que Agroforestry Systems seguía visible y pidió
retirarlo. La política anterior excluía Agroforestry como nombre completo y
los términos que contienen la sigla SAF/SAFs, pero conservaba esta expresión
inglesa; la corrección añade explícitamente **Agroforestry Systems** y
**Agroforestry System** en todas las categorías y con normalización de formato.
No se expande a otros compuestos ingleses no pedidos.

La auditoría identificó el canónico PRAC
`92b8b72d-3858-426e-aa54-dacd78a74eaf` (768 menciones, 44 documentos)
y el canónico soft_INFRA `750153a8-eac8-42cb-ab4e-6af51c00b3c1`
(una mención): 769 menciones adicionales. La política contiene 121 nombres;
total esperado fuera de los cálculos: 7.400 menciones sobre 59 documentos,
888 del lote nuevo de 11, y 118 canónicos completamente excluidos. Las tablas
no cambian y la evidencia original sigue conservada.

Pasaron 64 pruebas y 681 subpruebas del explorador. La publicación del ajuste
usa una imagen mínima, preservación de ocho tablas y archivos fuente,
comprobación de network/compare y sincronización Git con el commit aprobado.
No requiere cambios de frontend ni nueva publicación Vercel. Evidencia y
recibos: `export/exclude_agroforestry_systems_2026_11_24/`; copia remota:
`export/exclude-agroforestry-systems-20261124/`.

### Publicación web y consolidación de código — 24 Nov 2026

Frontend publicado en Vercel desde `b97877d64c1fb1bcc6e85111c561725a804683b5`
(`fix(graph): recuperar la distribución de redes colapsadas`). Se incluyen
dos cambios que estaban pendientes en src/graph: nuevas posiciones iniciales
distribuidas usando solo anclas de la red anterior y recuperación de cachés
colapsadas; descarta coordenadas no finitas. Pasaron **53 pruebas, lint y build**
con Node 24. GitHub check y Vercel terminaron en success, despliegue
`8trhonrDGaE5eT4QPbRVLDJHU65Y`.

Se comprobó en Brave la web pública con los datos actuales: 59 documentos,
400 nodos seleccionados, 3.323 enlaces, 3.580 nodos conectados en el corpus
y 22.106 menciones después de excluir; el mapa se distribuye sin el colapso
vertical anterior. La página sirve `assets/index-CfQ2yqEi.js`, igual al build
local de producción. URL: `https://semantic-network-explorer.vercel.app/`.

Backend validado con la suite completa: **216 pruebas y 711 subpruebas**.
Esta consolidación versiona las exclusiones, resolución road pavement y
documentación de publicación/fuzzy matching de los 11 nuevos. Las cinco
fuentes de runtime ya coinciden byte por byte entre Mac y la API de AWS.
Para asociarlas al commit probado se respalda el árbol manual del EC2 y
se avanza Git por fast-forward, verificando hashes y preservación completa;
no hace falta reinstalar dependencias ni reemplazar DB o archivos. Se pausa
solo el temporizador automático durante esta coordinación y se restablece
al terminar. Estado y recibos de la publicación:
`export/publish_web_2026_11_24/` y, en EC2, `export/publish-web-20261124/`.
El recibo final contiene los SHA y resultados de sincronización.

### Exclusión completa de la familia SAF — 24 Nov 2026

Después de revisar todas las variantes, la usuaria pidió que **todas** salieran
de la red, incluidos sufijos, numeraciones, tipos y actividades/compuestos.
**Aplicado en AWS y en el código local.** La política tiene ahora 119 nombres
normalizados y una regla explícita de familia SAF/SAFs: se reconoce la sigla
completa dentro de nombres canónicos o textos literales, con sufijos y
compuestos; también las formas compactas SAFsA/SAFsF encontradas después.
No se confunden safe/safety/safeguards/SAFTA/SAFA. La expansión de familia se
activa cuando la lista nominal contiene SAF/SAFs; una lista vacía sigue
desactivando la exclusión por nombres. El resto de exclusiones continúa por
nombre completo. Se mantienen todas las decisiones anteriores.

Catálogo y regla en `src/controlled_vocabulary.py`, aplicados mediante
`exclude_entities` antes de coocurrencias y métricas. El inventario inicial
mostraba 246 menciones y luego se detectaron SAFsA y SAFsF (una cada una),
para **248 menciones SAF** en total, **172 del lote nuevo**. Las 75 SAF/SAFs
simples ya estaban fuera; se retiraron **173 adicionales**. Ya no quedan
las 83 SAFs-A/SAFs-F bajo el canónico traducido sistemas agroflorestais: sus
158 menciones completas quedan excluidas. También quedan fuera SAF-dendê,
SAFs-A variant, SAF 1–14, SAF type I–IV y todos los compuestos listados.
La regla de sigla cubre futuros sufijos/compuestos con el token SAF/SAFs.

Total vigente sobre 59 documentos: **6.631 menciones excluidas**, **705 del
lote de 11 nuevos**; **116 canónicos completamente fuera**, sin exclusiones
parciales en este corpus. Red completa de recurrencia 1/sin top-n:
3.616 nodos/14.102 aristas antes y **3.580 nodos/13.846 aristas después**.
Se verificaron las redes completa y de los 11 nuevos, compare y conservación
de road pavement (36 menciones/physical_INFRA). Auditorías Mac/AWS coinciden;
las huellas completas de ocho tablas y todos los archivos NER/english/cleaned
son iguales antes/después. No se borraron ni cambiaron menciones en PostgreSQL,
no se tocaron fuentes y no se recalcularon clusters. Pasaron **97 pruebas y
698 subpruebas**. Sin commit nuevo ni cambios de frontend.

Evidencia: `export/saf_variants_2026_11_24/inventory.json` y
`export/exclude_all_saf_2026_11_24/` (local-audit.json, requested-names.json,
aws-result.json, public-network.json). SSM exitoso:
`de562749-5d2a-4c1f-b97d-9a54351e1240`. Respaldo remoto:
`export/exclude-all-saf-20261124/`; imagen anterior:
`semanticclassification-api:before-exclude-all-saf-20261124`.

### Revisión previa de exclusiones para 59 documentos — 24 Nov 2026

Los totales de esta revisión anterior quedaron sustituidos por la exclusión
completa de la familia SAF descrita arriba.

La usuaria reiteró la lista completa del 23 Nov para que también cubra los 11
documentos nuevos y añadió **the Amazon, Amazonia y peruvian amazon**. Se
mantienen todas las exclusiones posteriores de plot/plots, pilot plots,
plots 5 and 6 y seis nombres road; municipios solo cuando indique nombres
concretos. La política contiene ahora 83 nombres normalizados, siempre por
nombre completo y en cualquier categoría. Incluye variantes de formato,
tildes, puntuación y las equivalencias nominales explícitas ya definidas.
Amazonia cubre Amazônia y Amazonía por normalización. Los tres nombres nuevos
corresponden a 1.206 menciones (the Amazon 903, Peruvian Amazon 207 y Amazônia 96).

La auditoría detectó que el filtro anterior por canónico dejaba pasar 75
menciones literales SAF/SAFs, de ellas 20 de los documentos nuevos, porque
fuzzy matching las había vinculado a `sistemas agroflorestais` (UUID
`78e0aa9e-2c0f-4591-9e36-0bb7d55637ec`). Se corrigió `exclude_entities`
para comprobar además el texto literal completo de cada mención **antes de
coocurrencias y métricas**. Cuando solo la forma literal está excluida se
quitan esas menciones, sin descartar otras formas del mismo canónico. En este
caso permanecen 83 menciones de SAFs-A/SAFs-F, no incluidas en la lista de
nombres simples. Si se excluye el canónico por nombre o UUID se siguen
retirando todas sus menciones. La lista explícita vacía desactiva la exclusión
nominal como antes. La respuesta describe exclusiones parciales con `partial`
y `remaining_mention_count`; el frontend actual es compatible y no se modificó.

**Aplicado y verificado en AWS y en el código local:** 6.458 menciones se
retiran del cálculo sobre 59 documentos; 553 corresponden al lote nuevo de
11. Se excluyen completamente 79 canónicos y parcialmente uno. La red
completa de recurrencia 1/sin top-n pasó de 3.634 nodos/14.570 aristas a
3.616 nodos/14.102 aristas. Se comprobaron tanto la red completa como la
proyección exclusiva de los 11 nuevos y el endpoint compare. Road pavement
conserva 36 menciones/physical_INFRA. Las huellas completas de ocho tablas y
todos los archivos NER/english/cleaned permanecen intactas; auditorías Mac/AWS
coinciden. No se escribieron datos ni se recalcularon clusters históricos.
Pasaron 95 pruebas y 675 subpruebas. Sin commit nuevo.

Evidencia: `export/exclusions_59_2026_11_24/` (local-audit-before.json,
local-audit.json, requested-names.json, aws-result.json y public-network.json).
SSM exitoso: `fbf52f77-ba04-4759-9d3e-86df6d2aedba`.
Respaldo remoto: `export/exclusions-59-20261124/`; imagen anterior:
`semanticclassification-api:before-exclusions-59-20261124`.
Este filtro global cubre futuros documentos aunque sus canónicos tengan UUID
nuevos; no hay que reejecutar NER/fuzzy matching ni borrar filas para aplicarlo.

### Road pavement y exclusiones — 24 Nov 2026

La usuaria pidió agrupar los términos que contienen la palabra road bajo
`road pavement` y luego precisó que **new roads debe excluirse**, sin entrar
en esa unificación. La exclusión adicional de `new roads` ya está aplicada en
Mac y AWS: un canónico physical_INFRA, UUID
`52cba12b-e08f-44cf-9152-56bd34722652`, una mención. La red completa de
59 documentos/recurrencia 1/sin top-n pasó de 3.645 nodos y 14.582 aristas a
3.644 nodos y 14.579 aristas. Todas las huellas de DB, archivos y clusters
siguen iguales. Pasaron 59 pruebas y 647 subpruebas. API saludable, despliegue
mínimo sin modificar dependencias, sin commit nuevo.
Evidencia: `export/exclude_new_roads_2026_11_24/deployment-result.json`.
SSM exitoso: `57c75d36-5f35-45a2-8243-18e61f9c6422`.

**Canonicalización completada en AWS y Mac.** La usuaria corrigió explícitamente
que road pavement siempre debe ser **physical_INFRA**, nunca PRAC. Se mantuvieron
las exclusiones anteriores, incluido new roads. Se reunieron 36 menciones de
11 canónicos en el UUID existente `9631fd97-54b5-47f1-a3af-9832dcb1da21`,
nombre `road pavement`, ahora categoría `physical_INFRA`. Los diez canónicos
anteriores sin menciones activas se conservaron para trazabilidad y referencias
históricas. El destino tenía originalmente una sola mención PRAC y no había
referencias de estos once canónicos fuera del corpus publicado Agroforestry.

Se actualizaron exclusivamente canonical_id, categoría y metadatos de resolución
de esas 36 filas de entities, la categoría del canónico destino y 11 alias nuevos
(sin borrar ni modificar los alias anteriores). El texto, offsets, contexto,
oración, UUID de mención, documento, ambigüedad y fechas permanecen iguales.
Las categorías anteriores eran 26 physical_INFRA, 6 LOC y 4 PRAC: se guardaron
en `entities.resolution_details.source_category`, junto al canónico original y
los metadatos completos de la resolución anterior bajo editorial_canonicalization.
La evidencia de la API expone categoría resuelta physical_INFRA y source_category
original. No se modificaron los JSON NER ni fuentes english/cleaned. Documentos,
oraciones, clusters y todas las filas ajenas al cambio conservan sus huellas.

Regla editorial persistente en `src/controlled_vocabulary.py`; fuzzy matching
pasa a `deterministic-v4-roads`. Los tokens completos road/roads se resuelven
como road pavement/physical_INFRA independientemente de la categoría NER,
exceptuando los seis nombres road ya excluidos para evitar reincorporarlos.
La regla prevalece sobre detección de alias de personas. Roadmap, railroads,
broad y broadcast son palabras distintas y no se agrupan. Las exclusiones
road se comparten con el explorador desde el módulo de vocabulario.

En AWS la red completa pasó de 3.644 nodos/14.579 aristas a
3.634 nodos/14.570 aristas, y la API pública confirma una única entidad
road pavement física con 36 menciones; no aparece en la red PRAC. Mac importó
exactamente el mismo plan y las huellas de cuatro tablas coinciden. Se respaldaron
ambas bases; no se hicieron migraciones ni cambios de frontend. Pasaron 93 pruebas
y 667 subpruebas. Fuentes modificadas sin commit nuevo.
Evidencia: `export/road_pavement_2026_11_24/` (plan.json, aws-result.json,
local-result.json, guard-result.json, public-physical-network.json).
SSM principal `59ff5602-6293-4050-b00e-9be0a6134a8f`; ajuste de prioridad
`d4ecfcb5-aebc-418d-8830-4e524585b163`. Respaldo remoto
`export/road-pavement-20261124/database-before.dump`; local
`export/road_pavement_2026_11_24/local-before.dump`.

### Siete exclusiones seleccionadas — 24 Nov 2026

Desplegados en AWS y aplicados al filtro local: `pilot plots`, `plots 5 and 6`,
`road construction`, `Leticia-Tarapaca road`, `new road`,
`Transamazonica Road Region` y `roads`. Se excluyen por nombre completo, en
cualquier categoría y antes de calcular coocurrencias y métricas. Son siete
canónicos con 87 menciones: 1, 2, 4, 1, 1, 1 y 77 respectivamente. No se añadió
una equivalencia roads→road: `road` y `new roads` siguen permitidos, así como
los demás compuestos no seleccionados. La normalización nominal ya existente
de plots→plot también cubre `pilot plot`.

Con 59 documentos, recurrencia 1, todas las categorías y sin top-n, la red
conectada pasó de 3.650 nodos/14.670 aristas a 3.645 nodos/14.582 aristas;
no todos los canónicos excluidos estaban conectados en esa proyección.
Las huellas completas de ocho tablas y los archivos NER/english/cleaned
permanecen iguales: no se modificaron datos ni clusters históricos.
Pasaron 59 pruebas y 646 subpruebas. API saludable. Imagen mínima basada en la
API anterior, copiando solo explorer.py, sin reinstalar dependencias.
Sin commit nuevo. Evidencia: `export/exclude_selected_2026_11_24/`,
`selected-inventory.json` y `deployment-result.json`.
SSM exitoso: `c28d3ce3-a224-43ac-bbb1-02ac4bba8467`.
Respaldo remoto: `export/exclude-selected-20261124/`; imagen anterior:
`semanticclassification-api:before-selected-exclusions-20261124`.

### Exclusión de plot — 24 Nov 2026

Por instrucción de la usuaria se excluyeron los nombres completos `plot` y
`plots`, incluyendo mayúsculas y puntuación normalizadas, antes de construir
coocurrencias y calcular métricas del explorador. Son dos canónicos LOC:
`cb3f3725-3fd0-4429-9d80-4a674e59a386` (31 menciones) y
`fc92cf1a-cad4-4ae0-b56c-8d12f8f19fa5` (45 menciones).
La red solo LOC, 59 documentos, recurrencia 1 y sin top-n pasó de 430 nodos y
1.417 aristas a 428 nodos y 1.399 aristas. Se comprobaron las huellas completas
de ocho tablas y todos los archivos NER/english/cleaned antes y después:
PostgreSQL, fuentes y clusters permanecen intactos. Pasaron 59 pruebas y
629 subpruebas. Los 21 nombres compuestos distintos quedan pendientes de
decisión explícita: no hay exclusión por subcadena ni equivalencias nuevas
entre plot, field, farm y chacra.

Código actualizado en Mac y AWS; sin commit nuevo. El primer build remoto
agotó el disco al reinstalar dependencias y su rollback dejó el archivo fuente
vacío; la API anterior siguió saludable. Se restauró el respaldo y se completó
un build mínimo basado en `semanticclassification-api:before-plot-exclusion-20261124`,
copiando únicamente `/app/src/analysis/explorer.py`, sin cambiar dependencias.
No se borraron imágenes, caché ni datos. El disco quedó con aproximadamente
1,2 GB libres antes de esa recuperación: revisar capacidad antes de otro build
completo. SSM exitoso: `13937566-2423-4b02-9f99-4781fa4d56cf`.
Evidencia y candidatos: `export/exclude_plot_2026_11_24/`, especialmente
`deployment-result.json`, `inventory.json` y `compound_candidates.json`.
Respaldo remoto: `export/exclude-plot-20261124/`.

### Fuzzy matching de los 11 NER nuevos — 24 Nov 2026

**Completado en AWS y sincronizado en la Mac.** El corpus Agroforestry queda
en ambas bases con **59 fuzzyMatching, 55 english y 1 cleaned**, sin documentos
de este lote pendientes en ner. Se ejecutó el servicio existente
`DocumentService.preparar_fuzzy_matching`, versión `deterministic-v3`, únicamente
para los 11 UUID del manifiesto de publicación; los 48 anteriores no se reprocesaron.

Resultado persistido: **5.602 menciones, 1.900 oraciones, 996 canónicos nuevos
y 1.030 alias nuevos**. El resto de las menciones se vinculó con canónicos
existentes conforme a las reglas actuales. Todavía no se aplicaron acuerdos
editoriales nuevos ni la equivalencia pendiente de TFFF.

Antes de procesar se comprobó que el servidor ya agrupa ATT/KNOW/SKILL en KAS
para las redes. PostgreSQL conserva exactamente las categorías originales de
cada mención: en este lote hay **296 ATT, 40 KNOW y 19 SKILL**. La API pública
devuelve 59 documentos y un único grupo KAS, con **375 canónicos** en todo el
corpus. Una red de prueba solo KAS de los 11 nuevos, con recurrencia 1 y sin
top-n, devuelve 147 nodos conectados y 149 aristas; el resto de los canónicos
puede quedar fuera de esa proyección por falta de enlaces dentro de KAS.

Se respaldó PostgreSQL remoto y se verificó la lectura completa del dump.
Las llamadas por documento se ejecutaron con savepoints dentro de una única
transacción externa: los once se confirmaron después de validar el conjunto.
Se comprobó que ninguna fila previa de entities, sentences, canonical_entities
o canonical_entity_aliases fue modificada o eliminada. Los nuevos alias pueden
apuntar a canónicos anteriores, conservando intactas sus filas originales.
No cambiaron otros datos de documentos, ningún archivo NER/english/cleaned
ni ninguna de las tres tablas de metaredes.

La copia local importó exclusivamente las filas nuevas de AWS, con los mismos
UUID, fechas y detalles de resolución, después de respaldar PostgreSQL local.
Las huellas completas de las cuatro tablas coinciden con AWS después de la
importación; las huellas de clusters permanecen iguales. El generador local
protege ahora los **59 UUID publicados** en protected_documents.json.

Pasaron 89 pruebas y 618 subpruebas de fuzzy matching y explorador. Evidencia:
`export/fuzzy_11_2026_11_24/aws-result.json`, `local-import-result.json`,
`resolved_snapshot.json.gz`, `public-meta.json` y los scripts de ejecución.
Respaldo remoto: `export/fuzzy-11-20261124/database-before.dump` bajo el repo
del EC2. SSM principal: `1fa582ef-cc65-4cf1-a0d8-533071f00692`.
No se requirieron cambios de aplicación ni un nuevo despliegue Vercel: el
frontend consulta el corpus actualizado de la API.

### Publicación selectiva de NER: etapa previa — 24 Nov 2026

**11 documentos sincronizados en estado `ner`: 10 de idioma original es y 1 pt,
con 5.602 menciones en sus JSON.** Se verificaron contra sus fuentes inglesas
exactas, categorías originales, offsets, contexto de cada mención y ausencia de
duplicados. Los 11 JSON y las tres fuentes corregidas coinciden byte por byte en
Mac y AWS. El registro local de `7503f699` aún estaba en english; se alineó a ner
con su ruta, después de respaldar PostgreSQL local.

Al terminar esta etapa previa había **48 fuzzyMatching, 11 ner, 55 english y
1 cleaned**. La carga actualizó únicamente status/ner_path de estos documentos;
el fuzzy matching posterior se describe arriba. Las categorías
ATT, KNOW y SKILL de los nuevos JSON permanecen conservadas.

Se reemplazaron con respaldo los 11 JSON antiguos que ya existían físicamente
en AWS, aunque sus documentos tenían ner_path NULL. La carpeta remota sigue
conteniendo 195 JSON; la presencia de un archivo no equivale a su estado ni a su
inclusión en el dashboard. No se propagaron borrados locales ni se reemplazó DB.

Fuentes publicadas junto con sus NER:
- `70584b54`: retirada de XXXXXXXXXXX en cleaned y english y separación de
  Desde 1990 en cleaned. Su JSON vigente ya correspondía al inglés corregido.
- `f9cbfc22`: tres separaciones CITE productivo en english. Se ajustaron 23
  offsets, tres superficies por espacios y sus contextos, conservando las 31
  menciones, categorías y sentence_id. La alineación se demostró primero sobre
  el texto anterior exacto de AWS; no hubo reextracción ni cambios semánticos.

Los manifiestos antiguos del generador se conservaron como evidencia histórica;
varios documentos nuevos no tenían manifiesto en ese directorio. El manifiesto
de esta publicación valida directamente los JSON vigentes contra la fuente real.
**No regenerar f9cbfc22 desde sus entradas antiguas de anotación/segmentación sin
alinearlas antes:** la copia NER publicada es la versión ajustada y verificada.

Se verificó lectura completa del respaldo PostgreSQL remoto de 23.741.820 bytes
antes de publicar y se guardaron todos los archivos reemplazados. Una transacción
registró los 11 estados; los recibos prueban que no cambiaron otros documentos,
archivos ajenos, entidades, canónicos, alias, oraciones ni las tablas de metaredes.
La API quedó saludable y /meta siguió devolviendo 48 documentos.

Evidencia local: `export/publish_ner_2026_11_24/`, con
`publication_manifest.json`, `publication-result.json`, `ner_alignment.json`,
`local_alignment_result.json`, respaldos y scripts. Respaldo remoto:
`/home/ubuntu/semanticClassification/export/publish-ner-20261124/backup/`.
SSM de publicación: `2ad5a8ed-5f28-4166-b06e-5878593fba70`.
La aplicación de producción no requirió cambios de código ni despliegue Vercel.

### KAS en las redes actuales — 23 Nov 2026

Por instrucción de la usuaria, las redes agrupan `ATT`, `KNOW` y `SKILL` en
una sola categoría `KAS`. Quedan ocho categorías activas del explorador. La
transformación ocurre antes de seleccionar categorías/pares y calcular
coocurrencias y métricas; no es solamente una etiqueta visual. Los UUID y
nombres de las entidades se conservan: agrupar categorías no fusiona términos.

Se aplica como proyección de lectura sobre la anotación original de los 48
Agroforestry publicados. No se reescriben PostgreSQL, JSON NER, fuentes inglesas,
codebook de extracción ni ejecuciones históricas de clusters. `/meta` agrega
los conteos en KAS y `/evidence` conserva la etiqueta original en
`source_category`; filtros antiguos se interpretan como KAS completo.

**Backend desplegado y verificado en AWS.** La auditoría encontró 179 menciones
y 120 canónicos: ATT 152/93, KNOW 17/17 y SKILL 10/10. En la proyección
CHAR+KAS con recurrencia 1 hay 65 nodos KAS conectados; el conteo de 120 incluye
todos los canónicos del corpus, también los que no se conectan en esa proyección.
La comparación antes/después confirmó UUID, métricas, aristas y pesos iguales
para el grupo completo. Se verificaron metadata, network, compare, evidencia,
compatibilidad de filtros y conservación de las 66 exclusiones editoriales.
Las huellas de DB, archivos NER/english y tablas de metaredes quedaron iguales.

Pasaron 72 pruebas backend y 615 subpruebas. El frontend está preparado y pasó
51 pruebas, build y lint: un solo control KAS en ambos idiomas, color compartido,
leyendas, vistas guiadas y migración de URLs. Está en
`export/explorer_kas_2026_11_23/frontend/` (repo `semantic-network-explorer`).
La usuaria autorizó el commit de todos los cambios, push y publicación en
Vercel el 23 Nov. La publicación terminó, sincronizando únicamente código
y conservando los datos de AWS como fuente principal.
La suite completa previa al commit pasó: 208 pruebas y 631 subpruebas.
El frontend quedó publicado en GitHub con `5a97c6f`; Vercel confirmó el despliegue
exitoso `EFVDktezs4MsgyxicVmvRgX4M5VL` y el check del frontend pasó en GitHub.
La revisión visual del dominio público confirmó un único control KAS (120),
sin los controles separados de Knowledge, Attitudes y Skills. El JavaScript
público usa el gateway HTTPS vigente y la API devuelve los 48 documentos.
El commit completo del backend `d69414f` está publicado y aplicado en AWS;
GitHub Actions también terminó correctamente para ese commit. La copia de
código del servidor quedó limpia y la imagen se reconstruyó con el commit.
Las verificaciones posteriores confirmaron DB, NER/english y clusters intactos,
API saludable y las 66 exclusiones. Las cinco ediciones manuales anteriores
se conservaron en stash `46432cbfd92011bff923501734b1cb7cc6893d57` antes de
avanzar la rama. No hubo reemplazo de base, sincronización de datos ni recálculo
de clusters. Recibos en `synchronization-result.json` y
`public-verification.json`, dentro de `export/explorer_kas_2026_11_23/`.
Evidencia en `export/explorer_kas_2026_11_23/deployment-result.json`;
SSM `b2d4dee4-cc81-48f9-9aef-45fb9d1e6efa`, respaldo remoto
`/home/ubuntu/semanticClassification/export/explorer-kas-20261123/rollback/`
e imagen `semanticclassification-api:before-kas-20261123`.

### Exclusiones editoriales del explorador — 23 Nov 2026

La usuaria pidió ampliar la exclusión visual desde los dos nombres anteriores
a la lista explícita de términos genéricos, actores y lugares. La configuración
vigente está en `src/analysis/explorer.py`, en `DEFAULT_EXCLUDED_ENTITY_NAMES`:
71 etiquetas normalizadas, equivalentes a 65 claves de comparación. La lista
original sin repeticiones y el alcance están en
`export/explorer_exclusions_2026_11_23/requested_names.json`.

Se excluyen nombres canónicos **completos en cualquier categoría**, cubriendo
mayúsculas, tildes, espacios, puntuación, guiones, apóstrofos y las variantes
nominales de singular/plural mediante un diccionario explícito. No hay búsqueda
por subcadenas, traducción automática ni fuzzy matching. Así se cubren Perú/Peru,
farmers/farmer, NGO/NGOs, SAF/SAFs, AFS/AFSs y sus variantes tipográficas;
`Agroforestry systems` y nombres más largos no pedidos siguen disponibles.
`río Madre de Dios`, antes conservado, ahora está incluido expresamente.
Amazon y Amazon Region se interpretan como etiquetas separadas; también se
contempla la etiqueta combinada escrita con `/`.

La auditoría fresca de los 48 documentos confirmó 3.023 canónicos en uso y
**66 UUID coincidentes, asociados a 4.562 menciones**: 42 CHAR, 19 LOC y 5 PRAC.
Esas menciones se omiten al construir la red; no se eliminan de PostgreSQL ni
de los JSON. No aparecen como nombres canónicos independientes SAF, SAFs,
río Madre de Dios o Agroforestal; sus reglas quedan configuradas igualmente.
No se añadieron municipios: la usuaria no dio nombres concretos.

El cambio quedó **aplicado en AWS** con respaldo de los dos archivos de código
y de la imagen anterior. Se actualizaron solamente `src/analysis/explorer.py`
y `src/api/schemas/explorer.py`, sin migraciones, reemplazo de la base, nuevas
extracciones ni recálculo de clusters. Las verificaciones de producción en
`/network` y `/compare` confirmaron las exclusiones, la respuesta saludable y
la conservación de la opción explícita `excluded_entity_names: []`.
El frontend omite ese campo y utiliza los valores predeterminados del backend;
no fue necesario modificar ni desplegar el frontend. Para una pestaña ya
abierta, recargar el dashboard permite solicitar los resultados nuevos.

Con el resto de filtros predeterminados y sin top-n, la red pasó de 462 nodos
y 3.515 aristas a **434 nodos y 2.638 aristas**. La cifra de 66 excluidos se
refiere a todos los canónicos coincidentes del corpus: algunos ya estaban
ocultos o no superaban los umbrales de visualización. Las métricas se calculan
después de excluirlos. Las huellas de menciones, oraciones, canónicos y alias,
los conteos globales y las huellas completas de las tres tablas de metaredes
permanecieron idénticos antes y después del cambio.

Pasaron 56 pruebas y 615 subpruebas del explorador, incluidas categorías,
normalización, variantes, ausencia de coincidencias por fragmentos, métricas,
comparación y sobrescritura explícita de la lista. Dependencias de prueba en
`/private/tmp/explorer-exclusions-deps-20261123/`, sin modificar la venv.
Evidencia y scripts en `export/explorer_exclusions_2026_11_23/`, especialmente
`impact.json`, `excluded_nodes.json` y `deployment-result.json`.

Se utilizó el canal SSM ya disponible porque cambió la IP de la Mac y SSH no
respondía; no se modificaron reglas de red. Comando de despliegue SSM:
`0734483f-d2ba-4cb7-8ec6-62f4fa5a7b0c`. Respaldo remoto de código y registro:
`/home/ubuntu/semanticClassification/export/explorer-exclusions-20261123/`;
imagen `semanticclassification-api:before-exclusions-20261123`.
El cambio de estos dos archivos está aplicado sobre el código del servidor,
conservando el commit base; todavía no se hizo commit ni push de esta entrega.

### Tres metaredes: metodología y metadata acordadas — 20 Nov 2026

**En espera por decisión de la usuaria del 23 Nov.** Se conservan los resultados;
la fase actual modifica solamente las redes de entidades del explorador.

La usuaria confirmó construir tres redes de entidades separadas:

| Red | Categorías |
|---|---|
| Network 1 | CHAR, KNOW, ATT, SKILL |
| Network 2 | CHAR, PRAC, KNOW, RUL |
| Network 3 | CHAR, PRAC, physical_INFRA, soft_INFRA, eco_INFRA |

El flujo acordado es construir cada red, obtener su backbone y calcular sus
clusters con Leiden. Cada cluster se registra como un nuevo nodo global con
UUID propio y vínculos con las entidades integrantes. Después se asignará su
vector mediante una metodología todavía por definir; las aristas se calcularán
por similitud entre esos vectores y se persistirán en PostgreSQL con los UUID
de sus extremos y el valor de la conexión.

La usuaria confirmó que **las aristas de las metaredes corresponden a la
similitud de los vectores de sus nodos**, sustituyendo el criterio anterior
basado en coocurrencias entre las entidades miembro de los clusters.
**Por ahora las tres metaredes permanecen separadas:** solo se calculan y
persisten conexiones entre nodos de la misma red de origen; no se crean aristas
entre Network 1, Network 2 y Network 3. Esta decisión se refiere a las aristas
entre los nuevos nodos de clusters; las reglas y pesos de las redes iniciales
de entidades se concretarán por separado.

La usuaria confirmó mantener **coocurrencias por oración para las tres redes
iniciales de entidades**; sobre ellas se obtiene el backbone y se aplica Leiden.
La similitud de vectores se utilizará después, exclusivamente para las aristas
entre los nuevos nodos que representan clusters dentro de cada metared.

**Frecuencia documental:** la usuaria rechazó explícitamente el mínimo de dos
documentos. Las nuevas ejecuciones admiten entidades presentes en un solo
documento (`minimum_node_document_count=1`); no se exige recurrencia entre
documentos. El backbone existente sigue excluyendo entidades sin aristas
de coocurrencia dentro de la proyección, con el motivo registrado por entidad.

La primera etapa debe guardar los clusters y sus miembros en **PostgreSQL**,
con UUID propio, red de origen, evidencia y procedencia. Los campos **Nombre
canónico representativo**, **Descripción** y **Vector** se guardarán como SQL
`NULL`, no como texto `"null"` ni como vector de ceros, para completarlos después.
La metodología y versión del vector también permanecen sin asignar hasta su
definición. No se calculan todavía aristas entre clusters.

La ruta acordada para los archivos de cada ejecución es:

```text
s3/graphs/metanetworks/agroforestry/<ejecucion>/
  network1/
  network2/
  network3/
```

PostgreSQL será la fuente de consulta para la visualización. La usuaria no
requiere abrir resultados en Gephi: la visualización se integrará en el
dashboard existente, mediante una nueva ventana llamada **Dashboard**.
La construcción y persistencia de clusters preceden a esa integración visual;
no se ha implementado ni desplegado todavía esta nueva ventana.

La metadata confirmada corresponde a **cada nuevo nodo que representa un
cluster**:

| Metadata | Contenido |
|---|---|
| UUID | Identificador propio del nodo, independiente de su nombre. |
| Nombre canónico representativo | Nombre que expresa el cluster dentro de su red. |
| Descripción | Significado y alcance del cluster. |
| Red de origen | Network 1, Network 2 o Network 3. |
| Entidades integrantes y evidencia | Entidades miembro y evidencia documental que sustenta el cluster. |
| Procedencia del cálculo | Versión del corpus, backbone, parámetros de Leiden y cluster original. |
| Vector y versión de su metodología | Valores y método utilizado para obtenerlos; pendientes hasta definir la metodología. |

La usuaria excluyó explícitamente **Estado de revisión**: no se incorpora a
esta metadata la distinción entre propuesto, revisado y aceptado.

Esta decisión metodológica reemplaza para las tres nuevas metaredes el criterio
anterior de agregar pesos de aristas fuente entre clusters y la exigencia de
nodos aceptados. Los endpoints históricos conservan ese enfoque anterior
(sección 11); el nuevo procesador por lotes y sus tablas se describen abajo.
Los pendientes de definición e implementación están en `tasks.md`.

La usuaria pidió conservar en **Mac y AWS** los 48 documentos Agroforestry en
`fuzzyMatching`, sus JSON y los clusters, y proteger la etapa `english` de los
66 documentos traducidos. Se recuperaron los JSON y se copiaron las tablas de
metaredes a la Mac sin modificar datos remotos. El resultado vigente está abajo;
la revisión anterior se conserva como diagnóstico histórico.

### Preservación Mac/AWS y recuperación de english — 20 Nov 2026, 22:31 UTC

**Los 48 JSON ya existen en `s3/archivosNER/` de la Mac**, con hashes idénticos
a los del servidor. Se recuperaron desde la captura auditable local del
18 Nov, probando la serialización hasta obtener exactamente los bytes con
SHA-256 de AWS; la copia fresca confirmó esos mismos hashes y la igualdad
completa con las menciones persistidas. No se recalculó NER ni fuzzy matching
para estos documentos. Sus menciones, oraciones, canónicos y alias de PostgreSQL
permanecen intactos e iguales en ambas bases.

Se copiaron a PostgreSQL local `metanetwork_runs`, `metanetwork_nodes` y
`metanetwork_node_members`: **2 ejecuciones, 353 nodos (327 vigentes y 26
históricos), 4.892 registros de integrantes**. Se conservaron todos los UUID,
fechas de creación, metadata y evidencia originales; no se recalcularon clusters.
Las tres huellas de tablas completas coinciden con AWS. Los artefactos bajo
`s3/graphs/metanetworks/agroforestry/` también están verificados en la Mac.

**Se conservaron los 66 archivos ingleses sin reescribirlos ni traducirlos de
nuevo.** La reanotación continuó durante esta operación: al corregir los estados,
63 documentos seguían en cleaned y 3 ya habían avanzado a ner. Se restableció
english únicamente en los 63 pendientes; los 3 avanzados conservaron ner,
sus JSON y english_path. Estado local verificado al terminar: 48 fuzzyMatching,
63 english, 3 ner y 1 cleaned (Guía EUDR). Son cifras de ese momento, ya que la
reanotación puede continuar. AWS conserva 48 fuzzyMatching, 66 english y 1 cleaned.
Los nuevos NER locales no se publicaron aún en AWS. Se alineó además el idioma
local de `70767dc6` a `en`, conservando la corrección anterior de AWS.

El contrato real del servicio **ya exigía english tanto en el código local como
en el código desplegado en AWS**: NER lee english_path y conserva la traducción
al avanzar a ner. Se comprobó en el servicio de AWS con I/O y proveedor simulados,
sin llamada real al modelo ni cambios de DB. La colección de Postman describía
todavía NER desde cleaned con spaCy/XLM-RoBERTa y no incluía traducción: se
añadieron POST Translate Document, GET English Document y la descripción correcta
de Extract Entities. Se corrigió el flujo de `architecture.md` y se añadió una
regresión que exige 409 para cleaned antes de leer archivos o llamar al proveedor.
Pasaron 14 pruebas y 3 subpruebas de traducción/NER y del lote de metaredes.
No fue necesario modificar ni desplegar el código del endpoint NER.

La protección operativa del trabajo GLM está en
`data/output/ner_glm/protected_documents.json`, con los 48 UUID protegidos y los
66 documentos con traducción. `generar_artefactos.py` rechaza un UUID protegido
antes de escribir archivos y exige que exista su fuente inglesa. La memoria
`data/output/ner_glm/CONTEXTO_TAREA.md` ahora exige partir de english para NER y
prohíbe vaciar la carpeta NER o perder la traducción en un reinicio. Los 65 JSON
GLM v1 archivados no se restauraron ni se publicaron. La carpeta local contenía
51 JSON al verificar: 48 protegidos y 3 NER v2 en progreso.

Evidencia y scripts reproducibles en `export/preserve_aws_mac_2026_11_20/`:
`english_restoration.json`, `json_recovery.json`, `restoration.json`,
`final_local_verification.json`, `compact_proof.json` y el respaldo previo de
PostgreSQL `local_before.dump` (14 MB). La descarga directa de 10 MB fue lenta;
se reutilizaron artefactos locales solo tras comprobar sus hashes de archivos
y las huellas **completas** de las tres tablas contra la captura fresca de AWS.
La copia completa verificada es `snapshot_materialized.tgz` (10 MB), con
`materialized_receipt.json` que registra la prueba y la huella de origen.
Se detuvieron únicamente las dos descargas redundantes de esta tarea; sus
parciales se conservaron como `.partial`. AWS no se restauró ni se reemplazó.

La diferencia anterior de `57ebcb2a` (retirada local de `》 `) se conservó sin
sobrescribir ninguna de las versiones inglesas. Antes de publicar su futuro
NER deberá verificarse y alinear su fuente exacta. La sincronización futura
continúa siendo selectiva por documento; `DATA_PRIMARY=aws` sigue activo.

### Diagnóstico previo de sincronización — 20 Nov 2026, 21:40 UTC

La usuaria pidió revisar la sincronización. Se inventariaron las dos bases y
los hashes de archivos; **no se modificaron las bases ni archivos de entrada**.
`DATA_PRIMARY=aws` permanece intacto. Evidencia, consultas reproducibles y
diagnóstico en `export/sync_review_2026_11_20/review.json`.

Ambas bases contienen los mismos 193 documentos, 64.280 menciones globales,
61.253 canónicos y 12.129 oraciones. Para los 48 Agroforestry en fuzzyMatching
coinciden las huellas completas de menciones, oraciones, canónicos vinculados
y alias. La eliminación anterior de JSON locales no eliminó esos datos de DB.

| Alcance Agroforestry | Mac | AWS |
|---|---:|---:|
| fuzzyMatching | 48 | 48 |
| english | 0 | 66 |
| ner | 1 | 0 |
| cleaned | 66 | 1 |

Los estados locales se utilizan en el reinicio del trabajo NER v2 y no se deben
copiar literalmente a AWS: 65 documentos locales en cleaned están en english
en AWS. Otra diferencia de metadata es `70767dc6`: Mac aún indica `es`, AWS
conserva la corrección a `en`; no debe sobrescribirse con el dato local antiguo.

Las 66 traducciones ya existen en AWS: 65 son idénticas byte por byte. La única
diferencia afecta a `57ebcb2a-8ba5-463d-a89a-6dffd4b2877d`
(*Modelos-de-negocio-agroforestal-espanol.pdf*): la Mac retiró `》 ` (carácter
residual y espacio; 4 bytes) tanto del texto limpio como del inglés. Los otros
194 de los 195 textos limpios son idénticos. La corrección cambia posiciones
posteriores en el texto: antes de publicar su futuro NER debe alinearse también
la fuente inglesa exacta. Las dos diferencias están guardadas como `.diff`
en el directorio de revisión; no se aplicaron en AWS.

El NER GLM v1 se archivó deliberadamente por cobertura insuficiente, según
`data/output/ner_glm/CONTEXTO_TAREA.md`; sus 65 JSON están en
`data/output/ner_glm_backup_v1/archivosNER_json/` y **no son candidatos de
publicación**. La reanotación v2 tiene actualmente un único JSON vigente:
`32eea2e1-16cd-44f1-ae54-84f48724c85e` (*Income_stacking_and_income_diversification.pdf*),
con 19 menciones. Coinciden los hashes del manifiesto y de la fuente inglesa
de AWS; `_parsear_datos` devolvió las mismas 19 menciones sin issues. Está en
ner en la DB local y english en AWS; su manifiesto aún indica
`ner_generated_pending_human_audit`. No se infiere aprobación semántica de la
validación estructural ni se lo publicó durante esta revisión.

La Mac no tiene tablas `metanetwork_*` en su PostgreSQL. AWS conserva dos
ejecuciones, 353 nodos (327 vigentes y 26 históricos) y 4.892 registros de
integrantes. `resync-from-mac.sh` reemplazaría la base entera y haría perder esas
tablas; sigue bloqueado y no es el mecanismo apropiado. Tampoco se debe ejecutar
una descarga masiva de `s3/` que mezcle los 195 JSON antiguos del servidor con
la carpeta local de reanotación v2, que actualmente contiene un JSON.

La publicación debe ser selectiva por documento: verificar la versión exacta
de la fuente, respaldar cualquier archivo que se reemplace, subir únicamente
artefactos vigentes y actualizar solo ner_path/status del documento terminado
(english → ner). No propagar borrados locales, no restaurar v1, no retroceder
estados de AWS, no ejecutar fuzzy matching ni regenerar metaredes como efecto
de esa publicación. La implementación y publicación del sincronizador siguen
pendientes en `tasks.md`.

### Ejecución vigente sin filtro de recurrencia documental — 20 Nov 2026

La usuaria rechazó el mínimo de dos documentos. Se actualizó el procesador
para construir las tres redes con `minimum_node_document_count=1`, admitiendo
entidades presentes en un solo documento, y se publicó una **nueva ejecución**
en PostgreSQL de AWS. Los demás parámetros del backbone y de Leiden, las
exclusiones exactas de nombres y la separación de las redes se conservaron.

Ejecución vigente: **`6c90bfd6-db31-4a19-8758-09425d4a8214`**.
Ruta: **`s3/graphs/metanetworks/agroforestry/20261120T124610Z/`**.
La fuente sigue siendo exactamente los 48 documentos y sus 23.135 menciones,
con la misma huella `879b831590de6e70d1d3c1f9a9d24381d296905dc5f690d33f795e730d057dc5`.

| Red | Entidades del backbone | Aristas del backbone | Clusters | Categorías presentes |
|---|---:|---:|---:|---|
| Network 1 | 599 | 1.152 | 69 | CHAR, KNOW, ATT, SKILL |
| Network 2 | 1.669 | 4.791 | 126 | CHAR, PRAC, KNOW, RUL |
| Network 3 | 1.836 | 5.284 | 132 | CHAR, PRAC, physical_INFRA, soft_INFRA, eco_INFRA |

Se guardaron **327 nuevos nodos y 4.104 registros de integrantes** (conteo por
red, no entidades globales únicas), con su evidencia completa. Nombre canónico,
descripción, vector y versión de su metodología permanecen en SQL NULL.
No se han creado aristas entre clusters. Se conservan todos los componentes
del backbone; las entidades sin aristas siguen documentadas como exclusiones.

La ejecución inicial de 26 clusters permanece intacta como referencia
histórica. Por ello `metanetwork_nodes` contiene ambas ejecuciones: para leer
el resultado vigente se debe filtrar por el UUID nuevo o usar
`scripts/sql/consultar_metaredes.sql`, que selecciona la ejecución más reciente
con criterio de un documento. No usar el UUID de la primera consulta de pgAdmin
para consultar los nuevos resultados.

Antes de publicar se verificó un respaldo remoto de 18 MB en
`/home/ubuntu/semanticClassification/export/metanetwork-before-20261120T124610Z.dump`.
La publicación y `verify` confirmaron la correspondencia completa entre archivos
y PostgreSQL, los valores NULL, la conservación de la fuente y las categorías
previstas de cada red. `/health` sigue respondiendo `{"status":"ok"}`.
Pasaron 11 pruebas locales y 3 subpruebas, incluyendo una regresión explícita
para entidades presentes en un solo documento; el nuevo validador también
permite verificar la ejecución histórica sin cambiar el criterio de las nuevas.
Se descargó y verificó la ejecución completa en la misma ruta local, con
respaldo de transporte de 12 MB en
`export/metanetworks_2026_11_20/execution_min1.tgz`. Los hashes coinciden y
ninguna entidad figura excluida por frecuencia documental. Las consultas
`scripts/sql/consultar_metaredes.sql` se ejecutaron contra AWS y devolvieron
327 clusters en la primera consulta y 89 integrantes para Network 1 / C001.

### Primera ejecución histórica con mínimo dos documentos — 20 Nov 2026

La usuaria autorizó procesar las tres redes. El procesador reproducible está
en `scripts/process_metanetworks.py` y el esquema SQL aditivo en
`scripts/sql/metanetworks_v1.sql`. Se ejecutó en el contenedor API de EC2,
reutilizando los módulos actuales de coocurrencia, backbone y Leiden, sin
reiniciar ni reemplazar la aplicación desplegada.

Fuente: 48 documentos Agroforestry en `fuzzyMatching`, 23.135 menciones, captura
`REPEATABLE READ` de PostgreSQL. Huella del contenido fuente:
`879b831590de6e70d1d3c1f9a9d24381d296905dc5f690d33f795e730d057dc5`.
Los parámetros iniciales adoptan la configuración existente: backbone
`document-recurrent-core-v1`, recurrencia mínima de 2 documentos, peso
`fractional-document`; Leiden `modularity`, resolución 1, semilla 42,
iteraciones hasta convergencia y todos los componentes del backbone.
Se permiten pares de entidades de igual o distinta categoría dentro de cada
red. Se mantienen las exclusiones exactas del explorador `agroforestry` y
`madre de dios`, sin modificar la fuente. Las entidades bajo el umbral o sin
aristas entre entidades elegibles quedan registradas en `excluded.json`.

| Red | Entidades iniciales | Entidades del backbone | Aristas del backbone | Clusters |
|---|---:|---:|---:|---:|
| Network 1 | 823 | 125 | 318 | 11 |
| Network 2 | 2.042 | 311 | 1.563 | 8 |
| Network 3 | 2.232 | 352 | 1.776 | 7 |

Se publicaron **26 nodos con UUID global y 788 registros de integrantes** en
`metanetwork_runs`, `metanetwork_nodes` y `metanetwork_node_members`.
Los integrantes se cuentan por red, no como 788 entidades distintas del corpus.
Nombre canónico representativo (`canonical_name`), descripción (`description`),
vector (`vector`, tipo pgvector sin dimensión prefijada) y versión del método
vectorial (`vector_method_version`) quedaron en SQL NULL. No hay Estado de
revisión ni aristas entre clusters; el nombre de cada entidad integrante sí
se conserva como evidencia de origen.

Ejecución: `b35b368e-1ae3-4f17-9aeb-c609ed3a14ca`.
Archivos en `s3/graphs/metanetworks/agroforestry/20261120T122830Z/`, con las
tres subcarpetas, `manifest.json`, fuente comprimida, procesador y esquema.
Cada red incluye red inicial, backbone, partición Leiden, CSV de comunidades
e integrantes y `clusters.json` con `links: []`. Los hashes permiten comprobar
que la partición y su evidencia no cambiaron.

Antes de publicar se creó y leyó íntegramente el respaldo remoto
`/home/ubuntu/semanticClassification/export/metanetwork-before-20261120T122830Z.dump`
(15 MB). La publicación fue transaccional, con bloqueo de escritura de las
tablas fuente durante la comparación e inserción. Su comprobación íntegra
confirmó la conservación de los 48 documentos y sus menciones; una segunda
publicación de la misma ejecución fue idempotente. La revisión Alembic permanece
`f0a1b2c3d4e5`: estas tablas se gestionan con el esquema SQL versionado del lote.

Verificación: 9 pruebas locales y 3 subpruebas de proyecciones, backbone y Leiden
exitosas; prueba del esquema en PostgreSQL temporal, revertida completamente,
incluyendo nulabilidad, repetición del DDL y rechazo de integrantes duplicados,
categorías inválidas y cruces de red. `verify` comparó todos los nodos,
integrantes y evidencia contra los archivos y volvió a comprobar la fuente.
Scripts de auditoría operativa en `export/metanetworks_2026_11_20/`.
La consulta final confirmó los estados 48 `fuzzyMatching`, 66 `english` y
1 `cleaned`; `/health` respondió `{"status":"ok"}`. Se descargó únicamente
esta ejecución a la misma ruta local y se verificaron todos sus hashes y la
integridad de los 26 nodos contra sus particiones; el archivo de transporte está
en `export/metanetworks_2026_11_20/execution.tgz` (9,4 MB).

**Limitación observada:** con recurrencia mínima de 2 documentos, Network 1
conserva 125 entidades CHAR y ninguna KNOW, ATT o SKILL. Se excluyeron por el
umbral documental las 17 KNOW, 93 ATT y 10 SKILL iniciales; Network 2 también
queda sin KNOW. Es una consecuencia del filtro, no ausencia de esas categorías
en la fuente ni eliminación de sus datos. La usuaria resolvió la decisión
rechazando el mínimo de dos documentos y autorizando la admisión de entidades
presentes en un solo documento. La primera ejecución se conserva íntegra como
referencia histórica; no es el criterio vigente.
Como apoyo a esa decisión se calculó una comparación **solo local, sin
publicación en PostgreSQL**, con umbral de 1 documento y los demás parámetros
iguales: Network 1 conserva 599 entidades y produce 69 clusters (CHAR, KNOW,
ATT y SKILL presentes); Network 2 conserva 1.669 y produce 126 clusters
(CHAR, PRAC, KNOW y RUL presentes); Network 3 conserva 1.836 y produce 132
clusters (sus cinco categorías presentes). Las entidades sin aristas siguen
excluidas por el backbone. Resultados exploratorios en
`export/metanetworks_2026_11_20/threshold1_preview/comparison.json`.
La ventana Dashboard y sus endpoints de lectura aún están pendientes.

### Inventario auditable del vocabulario — 18 Nov 2026

La usuaria pidió preparar el inventario antes de acordar términos, definiciones
y sinónimos, siguiendo el enfoque de preparación de datos compartido de Jessica
Talisman. Se consultó la fuente principal de AWS con una transacción
`REPEATABLE READ`, `READ ONLY`, sin ejecutar NER, fuzzy matching ni fusiones.
La captura terminó a las `2026-11-18T16:53:06.143098+00:00`.

Alcance: los **115 documentos Agroforestry**, todas las categorías y estados,
incluidas las entidades ocultas por defecto en el dashboard. La fuente actual
confirma **48 documentos en fuzzyMatching, 66 en english y uno en cleaned**.
Las **23.135 menciones** de los 48 documentos contienen **3.561 cadenas literales
distintas**, **3.584 pares categoría + forma literal**, **3.023 canónicos en uso**
y **3.286 alias registrados para esos canónicos**. La cifra histórica de 3.584
formas se interpreta aquí explícitamente como pares categoría + texto.

El inventario identifica **81 casos de revisión**: 24 formas en varias categorías,
15 alias vinculados a varios canónicos de la misma categoría, una forma repartida
entre canónicos, 16 agrupaciones por huella léxica y 25 propuestas históricas que
siguen divididas. Estos 25 grupos reúnen 5.717 menciones. Los casos se superponen:
afectan a 6.209 menciones distintas y no equivalen a errores ni uniones aprobadas.
Pasaron los 32 controles de integridad, incluidas la comparación completa de los
JSON NER contra PostgreSQL y la literalidad de los offsets contra `cleaned`.
Esto no valida la exhaustividad o corrección semántica del NER; 2.344 menciones
conservan la marca `medium` de la fuente.

Entrega: `outputs/vocabulary_inventory_2026_11_18/inventario_vocabulario_agroforestry.xlsx`
y `inventario_auditable_agroforestry.zip` en la misma carpeta. El paquete incluye
TSV para OpenRefine, evidencia por mención, relaciones caso–mención, diccionario,
metodología, captura fuente y hashes. La captura y los scripts reproducibles están
en `export/vocabulary_inventory_2026-11-18/`. SHA-256 de la captura comprimida:
`adcbc569eea99b3f02b5d3ca7feb4122b36207bad9fbff29a1e237d50dbc0eb6`.

La tabla canónica actual solo tiene ID, nombre y categoría: no registra definición
ni aprobación terminológica. Como contexto separado, la base global contiene
61.253 canónicos y 42.146 no tienen menciones actuales; no se propone eliminarlos.
Los acuerdos de revisión, el diseño del vocabulario y cualquier cambio del endpoint
siguen pendientes en `tasks.md`. No se modificó el código de producción ni la DB.

**Archivo de edición simplificado:** la usuaria indicó que las siete hojas del
inventario y la ausencia de TFFF en los 81 casos dificultaban la edición. Se creó
`outputs/vocabulary_inventory_2026_11_18/editar_vocabulario.xlsx`, con una única
hoja `Editar` y todos los 3.584 pares categoría + texto. Este es el archivo de
trabajo para sus cambios. D permite indicar el nombre deseado, E permite elegir
`Conservar` o `Excluir`, y G contiene un comentario opcional. Los nombres actuales
precargados conservan el estado de origen; no representan aprobación humana de
todos los términos. Los IDs siguen disponibles para reconciliar cada cambio.

Decisiones explícitas registradas en esta edición: excluir cualquier entidad cuyo
texto o nombre canónico contenga `google`, sin distinguir mayúsculas, en todas las
categorías y documentos actuales/futuros; unificar `TFFF` y
`Tropical Forests Forever Facility` en `soft_INFRA` bajo el nombre preferido
**`TFFF`**. En el alcance observado, la regla Google corresponde a cuatro formas
y cinco menciones, y TFFF a dos formas y siete menciones. Las decisiones están
también en `acuerdos_vocabulario.json`; no se han aplicado a PostgreSQL ni a la API.
El inventario original y su ZIP se conservaron íntegros como evidencia de origen.

### Continuidad del filtro del explorador — 18 Nov 2026

La tarea más reciente es ocultar del explorador los nodos con nombre canónico
exacto `Madre de Dios` o `Agroforestry`, en cualquier categoría. El cambio está
commiteado, publicado y desplegado en EC2 como `e56c4b8`:
`excluded_entity_names` usa ambos nombres por defecto,
ignora mayúsculas y espacios sobrantes y se combina con `excluded_entity_ids`.
Se aplica antes de construir la red y calcular métricas en `/network` y
`/compare`, con exclusiones incluidas en la clave de caché y en la respuesta.
La coincidencia es exacta: `Agroforestry systems` y `río Madre de Dios` siguen
visibles. Una lista explícita reemplaza los valores predeterminados y `[]`
desactiva el filtro por nombre. No se modificó el corpus.

Los cambios del filtro están en `src/analysis/explorer.py`, los schemas y router
de explorer, `src/services/explorer.py`, `tests/test_explorer.py` y la sección
del explorador en `architecture.md`. El 18 Nov se repitieron las **53 pruebas
y 578 subpruebas**, todas exitosas, con dos advertencias de dependencias,
y se verificó `git diff --check`.
Comando usado:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/semantic-commit-deps MPLCONFIGDIR=/private/tmp/semantic-commit-matplotlib .venv/bin/python -m pytest tests/test_explorer.py -q -p no:cacheprovider`.
Las dependencias auxiliares se instalaron en `/private/tmp`; esa carpeta puede
desaparecer al reiniciar. No se alteró el entorno virtual del proyecto.

Rama verificada antes del commit: `feat/explorador-entidades`, HEAD `a1c346e`;
nueve commits locales por delante de `origin/feat/explorador-entidades`.
Esos nueve commits recogen los cambios anteriores del proyecto y
pasaron la suite completa: **193 pruebas y 586 subpruebas**. Inventario:
`export/commit_review_2026-11-11/created_commits.json`.
El 13 Nov se guardó el punto para apagar el equipo sin commit. El 18 Nov se creó
`e56c4b8`, se publicaron los diez commits pendientes y la usuaria ejecutó el
despliegue manual. Antes del despliegue pasó la suite local completa:
**196 pruebas y 591 subpruebas**, con dos advertencias de dependencias.
GitHub Actions no llegó a iniciar las pruebas por un bloqueo de facturación de
la cuenta; el reintento repitió el bloqueo. La pantalla de facturación mostraba
GitHub Free y $0 facturable; la causa concreta queda pendiente de soporte.

Se compararon los 14 archivos modificados directamente en EC2 con el commit:
13 eran idénticos y el prompt de traducción solo tenía una línea vacía adicional.
Se respaldaron los archivos y la imagen anterior, se conservaron los cambios en
un stash y se actualizó el servidor desde `f900018` hasta `e56c4b8`. La revisión
de Alembic ya era `f0a1b2c3d4e5`; no hubo migraciones pendientes.

El registro local confirma `VERIFIED_DEPLOY_OK` para el SHA completo. La API
respondió a `/health`; la red real excluyó `agroforestry` PRAC (664 menciones)
y `MADRE DE DIOS` LOC (411 menciones), con **462 nodos y 3.515 aristas** bajo
los filtros predeterminados y sin recorte top-n. Se verificaron `/network`,
`/compare` y la desactivación mediante `excluded_entity_names: []` en un alcance
vacío. Se actualizó el marcador de despliegue del temporizador al mismo commit.
Evidencia local: `export/deploy_e56c4b8/`; detalles y respaldo remoto en
`../sessions/2026-11-18-despliegue-filtro-explorador.md`. La API que consume el
dashboard ya incorpora el filtro; queda pendiente la comprobación visual del frontend.

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

## 9. Antecedente de próximos pasos técnicos — superado el 20 Nov 2026

La lista siguiente documenta el enfoque anterior. El acuerdo vigente está en
«Tres metaredes: metodología y metadata acordadas»; las tareas vigentes están
en `tasks.md`.

1. Regenerar los artefactos oficiales del backbone y Leiden para
   `prac-infra-rul-v2`, registrar su nuevo SHA-256 y volver a vincular los
   meta-nodes a esa partición exacta.
2. Revisar humanamente los títulos y descripciones generados para los meta-nodes;
   corregirlos y aceptarlos cuando corresponda.
3. Crear el prompt editorial separado para describir conexiones intercluster ya
   calculadas, usando evidencia trazable y sin atribuir causalidad por coocurrencia.
4. Asociar `CHAR` y `LOC` a cada configuración mediante las oraciones que soportan
   sus entidades miembro.

Leiden y la construcción de la meta-red anterior están implementados. La sección
11 describe esa implementación, no el nuevo criterio de similitud de vectores.

## 11. Promoción de comunidades a nodos semánticos

**Implementación anterior:** el acuerdo del 20 Nov sustituye para las tres
nuevas metaredes las conexiones por agregación y el requisito de aceptación
descritos aquí. El código aún conserva este comportamiento anterior.

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
