# Arquitectura

## Estructura

```
src/
├── config.py
├── api/
│   ├── main.py                ← FastAPI + CORS + /health + exception handler + router
│   ├── routers/
│   │   ├── documents.py       ← endpoints bajo /documents
│   │   └── analysis_networks.py ← build/latest de la red de corpus
│   └── schemas/
│       ├── documents.py       ← DocumentRead, DocumentListResponse, BatchProcess*
│       ├── entities.py        ← EntityOut, ExtractEntitiesResponse
│       └── network.py         ← respuesta tipada de red, cobertura y artefactos
data/
├── codebooks/codebook_en_construccion_en.md ← especificación completa de NER
├── ner/annotations/a251048a.json  ← anotaciones históricas reservadas para evaluación futura
└── prompts/
    └── ner_prompt.md              ← plantilla única: codebook + bloque objetivo del anotador semántico
├── models/
│   ├── database.py                ← engine, SessionLocal, Base, get_db
│   ├── documents.py               ← ORM Document + incubator_number controlado (1..8)
│   ├── documents_repo.py          ← CRUD, filtros y acceso por status/incubadora
│   ├── canonical_entities.py      ← ORM CanonicalEntity
│   ├── canonical_entities_repo.py ← acceso a entidades canónicas
│   ├── canonical_entity_aliases.py ← alias observados por canónico
│   ├── canonical_entity_aliases_repo.py ← consulta y registro idempotente de alias
│   ├── entities.py                ← mención + identidad + trazabilidad de resolución
│   ├── entities_repo.py           ← eliminar_por_documento, reemplazar_entidades
│   ├── sentences.py               ← ORM Sentence (evidencia oración–entidad)
│   ├── sentences_repo.py          ← reemplazo/elimina oraciones por documento
│   └── storage.py                 ← guardar, leer, eliminar, preparar_nombre
 └── services/
      ├── cleaning.py            ← CleaningService: limpieza determinista de Markdown a texto
      ├── documents.py           ← DocumentService + todas las excepciones
      ├── llm_client.py          ← Cliente Anthropic para tareas LLM
      ├── ner.py                 ← Extracción few-shot (Anthropic + ejemplos curados + tool schema)
      ├── fuzzy_matching.py      ← resolución determinista de entidades v2
      ├── network.py             ← orquestación por corpus/incubadora/documento
      └── pdf_converter.py       ← PdfConverter: PyMuPDF fast path + Docling OCR fallback

src/analysis/
├── backbone.py                   ← construcción de backbone analítico y exportación canónica
├── cooccurrence.py               ← incidencia y matrices de coocurrencia por oración
├── entity_resolution_audit.py    ← simulación reversible antes/después
├── graph_export.py               ← exportación mínima GraphML + CSV + metadata JSON
├── graph_paths.py                ← rutas y nombres estables de artefactos en s3/graphs/
├── leiden.py                     ← clustering reproducible con atributos para Gephi
└── network_visualization.py      ← red plana estática, JSON, HTML y GraphML
```

### Metaredes de Agroforestry — flujo acordado el 20 Nov 2026

`scripts/process_metanetworks.py` construye las tres redes acordadas desde una
captura consistente de los documentos Agroforestry en `fuzzyMatching`. Reutiliza
coocurrencia por oración, backbone documental y Leiden; incluye todos los
componentes del backbone. Por decisión de la usuaria se admiten entidades
presentes en un solo documento (`minimum_node_document_count=1`); las entidades
sin aristas quedan registradas como exclusiones. Los resultados se conservan en
`s3/graphs/metanetworks/agroforestry/<ejecucion>/network{1,2,3}/`.

La persistencia de esta etapa es aditiva y está separada de las tablas de la
meta-red histórica. El esquema versionado está en
`scripts/sql/metanetworks_v1.sql`, aplicado dentro de la transacción de publicación;
no modifica la revisión de Alembic ni las tablas del corpus:

- `metanetwork_runs`: UUID, huella de la fuente, documentos, configuración,
  rutas, hashes y resumen de las tres redes.
- `metanetwork_nodes`: UUID global por cluster, ejecución, red, comunidad,
  procedencia y cantidades; nombre canónico, descripción, vector pgvector
  sin dimensión prefijada y versión de metodología vectorial inicialmente NULL.
- `metanetwork_node_members`: integrantes canónicos con nombre/categoría de
  origen y evidencia documental y oracional. Las restricciones impiden asignar
  una entidad a varios clusters de una misma red y ejecución o cruzar redes.

No se incluye Estado de revisión ni se crean conexiones entre clusters en esta
etapa. Las futuras aristas serán por similitud de vectores dentro de cada red.
Los nuevos resultados aún requieren endpoints de lectura e integración en la
ventana Dashboard del frontend existente; no utilizan las rutas históricas
de promoción que exigen nodos aceptados.

El procesador tiene tres comandos: `prepare` solo genera una carpeta nueva;
`publish` comprueba hashes y la fuente vigente, instala el esquema e inserta en
una sola transacción; `verify` compara todos los nodos, integrantes y evidencia
persistida con los archivos iniciales, exige los campos diferidos en NULL y
comprueba la conservación de la fuente. Una publicación repetida de la misma
ejecución es idempotente; un UUID con contenido diferente se rechaza.
El validador admite también la configuración histórica de mínimo dos documentos
para verificar esa ejecución inmutable, sin usarla para las nuevas ejecuciones.
`scripts/sql/consultar_metaredes.sql` ofrece consultas de solo lectura para
pgAdmin que seleccionan la ejecución más reciente con el criterio vigente.

Ejemplo de ejecución en el entorno con acceso a PostgreSQL, desde la raíz:

```bash
PYTHONPATH=. python scripts/process_metanetworks.py prepare --output s3/graphs/metanetworks/agroforestry/<ejecucion> --expected-documents 48
PYTHONPATH=. python scripts/process_metanetworks.py publish --output s3/graphs/metanetworks/agroforestry/<ejecucion>
PYTHONPATH=. python scripts/process_metanetworks.py verify --output s3/graphs/metanetworks/agroforestry/<ejecucion>
```

La fuente comprimida, el procesador, el esquema SQL y las huellas de los módulos
analíticos se guardan con cada ejecución. Los JSON incluyen las redes iniciales
y los clusters con `links: []`; GraphML es un artefacto interno del cálculo
existente de Leiden, no un requisito para trabajar en Gephi.

### Implementación histórica de meta-red

La capa de meta-red anterior añade `src/models/semantic_nodes.py`,
`src/services/semantic_nodes.py`, `src/api/schemas/semantic_nodes.py` y
`src/api/routers/semantic_nodes.py`. Su primera entrega registra comunidades
Leiden aceptadas como nodos titulables. Las relaciones entre nodos se construyen
determinísticamente con `src/models/semantic_relationships.py`,
`src/services/semantic_relationships.py` y `src/api/routers/semantic_relationships.py`.

Flujo de nodos semánticos:

```text
GET  /semantic-nodes/leiden-source?language=es&artifact_source=accepted-2026-08-25
  → partición vigente, SHA-256 del GraphML y comunidades disponibles
POST /semantic-nodes/from-leiden
  → registra una comunidad aceptada con fuente, community_id y expected_clustering_sha256
GET  /semantic-nodes
GET  /semantic-nodes/{node_id}
POST /semantic-nodes/{node_id}/generate-description
  → usa el prompt editorial y evidencia interna; genera título/descripcion draft
PATCH /semantic-nodes/{node_id}
  → permite corregir título, descripción o aceptar el nodo
```

Ejemplo de promoción:

```json
{
  "projection_id": "prac-infra-rul-v2",
  "community_id": "C001",
  "artifact_source": "accepted-2026-08-25",
  "incubator_number": "all",
  "language": "es",
  "expected_clustering_sha256": "<SHA-256 recibido en leiden-source>"
}
```

La promoción conserva por incubadora los documentos y miembros que aportan
soporte en el alcance elegido. La generación no modifica nodos `accepted` ni
`retired`; para regenerar uno aceptado, primero se devuelve a `draft`.

## Capas

```
api/routers → services → models/{repo, storage}
   ↓            ↓              ↓
  HTTP       orquesta       DB + archivos
```

## Flujo Objetivo 1: Upload

```
POST /documents
  multipart:
    file
    incubator_number (1..8)
    year opcional (1000..9999)
    productive_sector opcional (Agroforestry)
    document_type opcional (vocabulario controlado)
    metadata opcional
    language opcional
  → FastAPI/OpenAPI valida que la incubadora esté entre 1 y 8
  → DocumentService.cargar_documento()
    → Storage.preparar_nombre() → nombre seguro, ext, UUID
    → Storage.guardar()         → s3/archivosCrudos/{uuid}.{ext}
    → DocumentRepo.crear()      → INSERT con status=raw y atributos de ingesta
  ← 201 + DocumentRead (incluye incubadora, idioma, año, sector y tipo documental)

POST /documents/batch
  multipart: files[] + incubadora; año, sector y tipo documental opcionales comunes al lote
  → cada documento conserva sus propios campos en PostgreSQL

PATCH /documents/{document_id}/classification
  multipart form-data: uno o más de year, productive_sector, document_type
  → solo modifica los campos enviados
  → no cambia status ni repite conversión, limpieza o NER

PATCH /documents/{id}/language
  → registra el idioma de un documento ya cargado

POST /documents/set-language-batch
  → registra el idioma para varios documentos a la vez

GET /documents?incubator_number={1..8}&language=es
  → filtra el corpus documental por incubadora y/o idioma
```

## Flujo Objetivo 2: Conversión

```
POST /documents/{id}/process
POST /documents/process-batch

   → DocumentService.convertir()
     → DocumentRepo.leer_uno()          → SELECT
     → PdfConverter().convertir()       → PyMuPDF (PDF nativo) o Docling OCR (fallback) → MD
     → Storage.guardar()                → s3/archivosConvertidos/{id}.md
     → doc.converted_path = path        → guarda ruta en DB
     → DocumentRepo.actualizar_status() → status = 'converted'
  ← 200 OK

convertir_varios: busca todos en status "raw", convierte uno a uno con rollback por documento
```

## Flujo Objetivo 3: Limpieza

```
POST /documents/{id}/clean
POST /documents/clean-batch

   → DocumentService.limpiar()
     → DocumentRepo.leer_uno()          → SELECT
     → Storage.leer(converted_path)     → lee el .md
     → CleaningService.structuralCleaning()
         → ftfy.fix_text()              → repara encoding
         → elimina secciones bibliográficas y editoriales por encabezados Markdown
         → elimina placeholders de imágenes
         → elimina headers/footers repetidos
         → markdown_it.MarkdownIt()     → parsea MD → texto plano con párrafos
         → regex URL/email/teléfono     → elimina datos de contacto
         → elimina metadata de autoria (autores, facilitadores, revisores, directores)
         → elimina direcciones postales, notas legales, copyright y créditos
         → elimina índices/tablas de contenido y headers de anexos; conserva texto de celdas
         → elimina prefijos de numeración de secciones, subsecciones e items
         → elimina números de página y líneas muy cortas
         → deduplica párrafos consecutivos
         → _MULTISPACE + _SPACES + strip → normaliza whitespace (mantiene mayúsculas)
      → Storage.guardar()                → s3/archivosLimpiados/{id}.txt
      → doc.cleaned_path = path          → guarda ruta en DB
      → DocumentRepo.actualizar_status() → status = 'cleaned'
   ← 200 OK

La limpieza vigente es determinista y no llama a Anthropic. Conserva el idioma
original y los párrafos; las citas dentro del cuerpo permanecen para evitar
reescrituras o pérdidas de contenido. La eliminación de referencias depende de
un encabezado Markdown reconocible; los demás formatos requieren revisión.

limpiar_varios: busca todos en status "converted", limpia uno a uno con rollback por documento
```

## Etapa english: traducción previa a NER

`POST /documents/{id}/translate` requiere `cleaned`, conserva el idioma original
en `language`, guarda `s3/english/{id}.txt` y registra `english_path` y el estado
`english`. Si el idioma original es inglés, copia el texto sin proveedor.
`GET /documents/{id}/english` permite consultar la traducción incluso después
de avanzar a NER o fuzzyMatching. El reinicio de una anotación debe conservar
esta etapa y sus archivos.

## Flujo Objetivo 4: Extracción de entidades (NER vía LLM)

```
POST /documents/{id}/extract-entities

   → DocumentService.extraer_entidades_de_documento()
     → DocumentRepo.leer_uno()              → SELECT
     → validar status == 'english'         → cleaned recibe 409
     → Storage.leer(english_path)           → lee el .txt en inglés
     → extraer_entidades(texto, document_id, document_title):
         → _cargar_prompt()                 → lee ner_prompt.md y codebook completo (caché)
           → NER_CODEBOOK_PATH              → data/codebooks/codebook_en_construccion_en.md
         → _partir_por_parrafos()           → chunks de máximo 3 párrafos / 12K caracteres
         → _segmentar_oraciones()           → asigna sentence_id estable y offset absoluto
         → _construir_json_entrada()        → arma JSON con document_id, title y sentences
         → _build_prompt()                  → inserta codebook y JSON objetivo en la plantilla única
         → Anthropic API (claude-sonnet)    → un mensaje de usuario con codebook + fragmento objetivo
         → tool submit_entity_annotations   → salida validada por JSON Schema
         → _parsear_datos()                 → localiza cada span dentro de su sentence_id
         → fallo explícito                  → no persiste resultados truncados o sin tool use
         → _buscar_offset()                 → calcula start/end absolutos buscando text literal
         → _fusionar_entidades()            → conserva apariciones y deduplica solo la misma posición
     → Guardar JSON en s3/archivosNER/{id}.json
     → doc.ner_path = path                   → guarda la ruta del JSON en documents
     → DocumentRepo.actualizar_status()      → status = 'ner'
     → conservar english_path y su archivo  → traducción permanece disponible
   ← 200 + ExtractEntitiesResponse {document_id, entities: [{text, category, start, end, sentence_id, context, ambiguity}]}
```

Este endpoint no escribe, reemplaza ni elimina menciones en la tabla `entities`.
La persistencia y normalización de menciones se delega a un endpoint posterior.

## Flujo de resolución canónica (endpoint histórico Fuzzy Matching)

```
POST /documents/{id}/fuzzy-matching

   → comprueba que el documento exista y tenga status = 'ner'
   → comprueba que ner_path esté registrado
   → lee y valida s3/archivosNER/{id}.json
   → valida primero todas las menciones y analiza el documento completo
   → conserva text/start/end/context; solo normaliza claves de comparación
   → agrupa actores genéricos CHAR mediante singularización controlada
      (mineros → minero; mineras → minera; conserva género y calificadores)
   → detecta familias nominales CHAR por prefijos compatibles dentro del documento
      (Griselda ↔ Griselda Zubizarreta ↔ Griselda Zubizarreta Vargas)
   → rechaza el nombre corto si hay dos familias compatibles en el documento
   → bloquea marcadores institucionales/corporativos en la regla de personas
   → busca candidatos exclusivamente dentro de la misma categoría
   → aplica exacto, alias persistido, nombre personal seguro o fuzzy conservador
   → crea canonical_entity si no existe una coincidencia segura
   → registra los textos observados en canonical_entity_aliases
   → reemplaza las menciones previas del documento en entities
   → persiste method, score, version y details para auditar cada decisión
   → commit único → menciones + canónicos + alias + status
   → status = 'fuzzyMatching'
   ← 200 + menciones con canonical_id y metadatos de la decisión
```

La tabla `canonical_entities` contiene `id`, `canonical_name` y `category`; cada fila
de `entities` referencia una entidad canónica mediante `canonical_id` no nulo. La
versión `deterministic-v2` usa los métodos `exact`, `morphology`, `person_alias`,
`stored_alias`, `person_name`, `fuzzy` y `new`. Los umbrales fuzzy siguen siendo 93
para CHAR/LOC y 96 para INFRA/RUL/PRAC, con margen mínimo de 5 puntos. La forma
minúscula/singular se aplica a actores genéricos controlados; los nombres propios
conservan una etiqueta legible. Los UUID no se transforman.

La categoría activa `RUL` representa reglas, normas e instrumentos
institucionales concretos. La gobernanza puede describirse en el análisis, pero
no se etiqueta por sí sola. Al leer JSON o particiones históricas, el servicio
normaliza `GOV` a `RUL` en memoria; no reescribe esos artefactos. La migración
`b5c6d7e8f9a0` actualiza las categorías persistidas y cambia la proyección activa
de `prac-infra-gov-v1` a `prac-infra-rul-v2`.

Antes de reprocesar un documento puede ejecutarse una auditoría transaccional que
siempre hace rollback y compara también la red G₁/G₃:

```bash
python -m src.analysis.entity_resolution_audit \
  --ner-json s3/archivosNER/{document_id}.json \
  --output-dir data/output/entity_resolution/{document_id}
```

## Flujo Objetivo 5: Red plana de coocurrencia

```
POST /analysis/network
POST /documents/{id}/network

  → solo incluye documentos con status = 'fuzzyMatching'
  → el POST de corpus recibe incubator_number y language en JSON
  → cada filtro admite un valor concreto o "all"; ambos se combinan con AND
  → consulta entities + canonical_entities sin modificar PostgreSQL
  → nodo = canonical_id, con categoría CHAR/LOC/PRAC/INFRA/RUL
  → arista no dirigida = dos canónicos presentes en la misma
    (document_id, sentence_id), incluso CHAR–CHAR y LOC–LOC
  → peso = número de oraciones distintas donde coocurre el par
  → una sola red: no hay layers, macrocapa L2 ni bloques separados
  → el contexto de evidencia se compone a partir de las menciones del par
  → exportación atómica por incubadora + idioma + minimum_weight + include_isolates
  → archivos CSV, Matrix Market, GraphML, JSON, PNG/SVG y HTML interactivo
  → respuesta con cobertura, conteos, 15 pares de categorías, top nodos y URLs

GET /analysis/network/latest
  → recibe incubadora/idioma como query params y lee la combinación exacta
  → no recalcula la red
```

El layout usa fuerzas para componentes pequeños y una disposición determinista
lineal para componentes de más de 500 nodos. Así la configuración predeterminada
del corpus completo sigue siendo operable con miles de nodos.

## Proyección analítica tipada PRAC + INFRA + RUL

La red histórica de cinco categorías continúa disponible. La proyección analítica
principal se registra por separado como `prac-infra-rul-v2`:

```
entities + canonical_entities
  → agrupar todas las menciones por (document_id, sentence_id)
  → conservar todas las entidades de la oración como evidencia contextual
  → proyectar únicamente nodos PRAC, INFRA y RUL
  → permitir los seis category_pair, incluidas relaciones intratipo
  → calcular las nueve vistas como resúmenes en memoria
  → publicar únicamente la vista canónica main-component/all
```

La publicación oficial se organiza primero por formato y luego por alcance:

```
s3/graphs/
├── graphml/<scope>/{main_network,backbone_<projection>,leiden_<projection>}.graphml
├── json/<scope>/{main_network,backbone_<projection>,leiden_<projection>}.json
└── csv/<scope>/
    ├── {main_network,backbone_<projection>}_{nodes,edges}.csv
    └── leiden_<projection>_{communities,members}.csv
```

`<scope>` es `corpus/{language|all}`, `incubators/{number}/{language|all}` o
`documents/{document_id}`. Los nombres son estables y cada ejecución reemplaza
atómicamente los archivos oficiales. Los parámetros exactos quedan en el JSON.

`CHAR` y `LOC` no son nodos de esta proyección, pero siguen disponibles en
PostgreSQL. La tabla `sentences` almacena el texto normalizado de cada oración;
las entidades proyectadas y contextuales se consultan en `entities`. El endpoint
de evidencia combina ambas fuentes bajo demanda para reconstruir la arista, sus
oraciones y entidades contextuales.

### Construcción analítica parametrizada

El POST de la proyección acepta opcionalmente un objeto `construction` discriminado
por `method`. `document-recurrent-core-v1` siempre vuelve a producir la evidencia W1
del scope y después deriva una red analítica sin modificar PostgreSQL:

```
evidencia W1
  → nodo elegible si node.document_count >= minimum_node_document_count
  → arista incluida si ambos extremos son elegibles
  → métricas: sentence_count, document_count, independent_support_count
  → fractional_weight = Σ 1/(N_s - 1)
  → fractional_document_weight = Σ_doc min(1, Σ contribuciones)
  → Weight de GraphML = analysis_weight seleccionado
  → resúmenes de nueve vistas para all-components y main-component
  → GraphML canónico de main-component/all
```

La configuración completa se registra en el JSON, pero no se codifica en carpetas.
La construcción publica únicamente:

```
graphml/<scope>/backbone_<projection>.graphml
json/<scope>/backbone_<projection>.json
csv/<scope>/backbone_<projection>_nodes.csv
csv/<scope>/backbone_<projection>_edges.csv
```

Sin `construction`, la proyección usa los mismos nombres oficiales y registra el
método `raw-threshold-v1` en sus metadatos. La construcción no ejecuta Leiden.

### Clustering Leiden desacoplado

`POST /analysis/network/projections/{projection_id}/clusterings/leiden` recibe la
misma selección de construcción y una configuración reproducible. La publicación
simplificada acepta la vista canónica `main-component/all`; el cliente nunca envía
rutas de filesystem.

```
GraphML existente
  → hash SHA-256 de la fuente
  → conversión estable a igraph
  → Leiden ponderado (seed + resolution + iterations)
  → IDs estables por tamaño/nombre
  → GraphML derivado + CSV de comunidades/miembros + resumen JSON
```

El artefacto fuente no se modifica. El GraphML derivado conserva `weight` y añade
`modularity_class` entero para la partición de Gephi, además de `community_id`,
`community_size` y `community_color`. Los identificadores son estables únicamente
dentro de la partición exacta; no deben compararse entre filtros o resoluciones.
El JSON registra objetivo, resolución, semilla, iteraciones y atributo de peso. Si
la fuente y la configuración coinciden, el POST devuelve el resultado existente
con `cached=true`; otra configuración reemplaza atómicamente los nombres oficiales.

La configuración `objective_function=modularity` usa la partición generalizada de
modularidad con parámetro de resolución; `cpm` queda disponible para análisis de
sensibilidad. Las comunidades resultantes no se presentan automáticamente como
configuraciones semánticas: la validación de tamaño, evidencia y composición sigue
siendo una fase posterior.

## Explorador de entidades (`entity-explorer-v1`)

Lectura en vivo para el dashboard interactivo (repo de frontend aparte). No
escribe en PostgreSQL ni en `s3/`; reutiliza la coocurrencia por oración y el
núcleo `document-recurrent-core-v1`. Las redes actuales usan ocho categorías:
`CHAR`, `LOC`, `PRAC`, `RUL`, `KAS`, `physical_INFRA`, `soft_INFRA`, `eco_INFRA`;
admite el legado `INFRA` solo si aparece en los datos.
`src/analysis/network_categories.py` transforma `ATT`, `KNOW` y `SKILL` en
`KAS` antes del filtrado de pares y del cálculo de métricas. Mantiene UUID,
nombres y menciones; no cambia la taxonomía de extracción NER ni las fuentes
persistidas. `/meta` agrupa los conteos con CASE y DISTINCT; `/evidence`
devuelve `category=KAS` y conserva `source_category`. Los filtros antiguos
de categorías y pares se normalizan al grupo completo. Las ejecuciones
históricas de clusters no se recalculan ni se reescriben.

```
POST /analysis/explorer/v1/network
  → ExplorerService.network()
    → documentos fuzzyMatching filtrados por período/incubadora/idioma/tipo/document_ids
    → caché de redes (clave: documentos + huella de menciones + filtros estructurales)
      si no está: load_db_mentions(document_ids=...)
                  → build_ranked_network()           (src/analysis/explorer.py)
        1. categorías + link_mode (any | between | within | pairs)
        2. recurrencia documental mínima por nodo
        3. peso analítico mínimo de arista (se eliminan nodos huérfanos)
        4. métricas sobre la red filtrada completa:
           degree, strength, betweenness, closeness, pagerank, document_count
    → select_shown_network()
        5. top_n por ranking_metric (las métricas no cambian con el recorte)
  ← nodos + métricas + rangos, aristas, conteo por etapa y advertencias
```

- Períodos fijos, en orden cronológico: `2000-2020`, `2021-2023` y `2024-2026` (`PERIODS` en
  `src/analysis/explorer.py`). `/compare` usa los tres por defecto.
  Los documentos sin `year` quedan fuera de cualquier período y se contabilizan.
- Betweenness y closeness usan distancia `1/analysis_weight` y se calculan con
  igraph (C), siempre exactas. Closeness aplica la corrección de Wasserman y Faust
  para redes desconectadas, como `networkx.closeness_centrality`. PageRank sigue en
  networkx. Con networkx puro, una red de 3.000 nodos tardaba más de un minuto; con
  igraph, unos segundos. Además, igraph reconoce como empate los caminos mínimos que
  en coma flotante difieren en el último decimal; networkx no, y su intermediación
  se desviaba hasta 2e-4 (ver `NodeMetricsTests`).
- `POST /compare` construye cada período con los mismos filtros y sin `top_n`, y
  devuelve trayectorias de rango, entradas/salidas del top-k y el nodo líder por
  métrica en cada período.
- `GET /evidence` devuelve las oraciones compartidas por dos entidades dentro del
  mismo alcance; su total coincide con `sentence_count` de la arista.
- Filtros imposibles responden 422 (`ExplorerFiltroInvalido`); un alcance sin
  datos responde 200 con red vacía y advertencias.
- `excluded_entity_ids` quita entidades canónicas antes del paso 1 (por ejemplo, la
  región que da contexto a todo el corpus): las métricas del resto se calculan sin
  ellas. La respuesta trae `excluded_entities` con nombre, categoría y menciones
  quitadas (nombre nulo si la entidad no está en el alcance). Es parte de la clave de
  la caché.
- `excluded_entity_names` excluye nombres canónicos completos en cualquier categoría,
  normalizando mayúsculas, tildes, espacios, puntuación, guiones y apóstrofos.
  `entity_exclusion_key` admite singular/plural de los sustantivos configurados
  mediante un diccionario explícito; no usa stemming general, traducción ni fuzzy
  matching. La lista editorial predeterminada vive en `DEFAULT_EXCLUDED_ENTITY_NAMES`
  en `src/analysis/explorer.py`, ampliada por la usuaria el 23 Nov. Incluye
  Agroforestry, Madre de Dios, río Madre de Dios, Perú, las formas indicadas de
  farmers/cooperatives y las demás etiquetas de ese acuerdo. No se infieren municipios.
  `[]` desactiva esta exclusión y una lista explícita reemplaza los valores.
  No coincide por fragmentos: `Agroforestry systems` se conserva. Se aplica junto
  a los IDs antes de construir
  `/network` y `/compare`, recalcula métricas y forma parte de la clave de caché.
  `excluded_entities` enumera los IDs encontrados y sus menciones retiradas. La
  exclusión no modifica el corpus ni impide consultar su evidencia original.
- `language` y `document_types` (lista, con `document_type_mode`: `only` o `exclude`)
  filtran documentos antes de construir la red, en `/network`, `/compare` y `/evidence`,
  y se combinan entre sí. Excluir tipos conserva los documentos sin tipo. El campo
  anterior `document_type` (un solo tipo) se sigue aceptando y se suma a la lista.
  `/meta` trae `document_types` con su conteo. La caché no necesita nada extra: su clave
  ya es el conjunto de documentos.
- Solo entran documentos con `productive_sector = Agroforestry`, salvo que se envíe
  `productive_sector: "all"`.
- En producción, el gateway Caddy (`deploy/gateway/Caddyfile`) solo expone este prefijo
  y `/health`; ver `deploy/aws/README.md`.

### Despliegue continuo

`.github/workflows/backend.yml` corre `pytest` (job «Tests») en cada push y pull
request. El EC2 sondea GitHub cada 5 minutos con un temporizador de systemd
(`deploy/aws/autodeploy/autodeploy.sh`): si `feat/explorador-entidades` tiene un commit
nuevo y su job «Tests» terminó bien, ejecuta `deploy/aws/deploy-on-ec2.sh <commit>`
(fast-forward, `up -d --build api`, espera `/health`, migraciones). No toca la base de
datos ni `s3/`; los datos se siguen resincronizando desde la Mac.

Se descartó desplegar desde GitHub con OIDC: la SCP administrada de los projects de la
nueva experiencia niega `iam:*Provider*` en los planes Free y pago. Detalle en
`deploy/aws/CI-CD.md`.

### Caché del explorador

`RankedNetworkCache` (`src/services/explorer.py`) guarda la salida de los pasos 1 a 4
(`RankedNetwork`). Cambiar `top_n` o `ranking_metric` reutiliza la red sin recalcular,
y `/compare` comparte resultado con `/network` del mismo período.

- Clave: ids de los documentos del alcance, huella de sus menciones (cantidad,
  canónicos distintos y último `created_at`, en `_data_fingerprint`) y
  `ExplorerFilters.structural()`.
- LRU de hasta 16 redes y 300.000 links en total por worker (cerca de 1 KB por
  link: ~14 MB la red por defecto, ~90 MB con recurrencia 1), con vencimiento de
  30 minutos. La red recién calculada se conserva siempre. Es segura entre hilos y, si dos
  peticiones piden la misma clave a la vez, el cálculo se hace una sola vez. Los
  errores no se guardan.
- Límites conocidos:
  - Es por proceso: con `API_WORKERS=2`, cada worker calcula su copia la primera vez.
  - La huella no detecta un cambio de `canonical_name` sin cambio de menciones; el
    vencimiento acota ese caso a 30 minutos. Reiniciar la API vacía la caché, y
    `resync-from-mac.sh` la reinicia.
- Si el corpus o las usuarias crecen: mover la caché a Redis o precalcular la red al
  terminar el fuzzy matching, y sacar el cálculo del request a un trabajo en segundo
  plano.

## Flujo Revertir

```
POST /documents/{id}/revert

  → DocumentService.revertir()
    → DocumentRepo.leer_uno()          → SELECT
    → cleaned  → Storage.eliminar(cleaned_path)  → borra .txt
              → doc.cleaned_path = None
              → status = 'converted'
    → converted → Storage.eliminar(converted_path) → borra .md
               → doc.converted_path = None
               → status = 'raw'
    → raw      → DocumentoNoReversible (409)
  ← 200 OK
```

## Storage

```
s3/
├── archivosCrudos/           ← upload (POST /documents)
├── archivosConvertidos/      ← conversión (POST /documents/{id}/process)
├── archivosLimpiados/        ← limpieza (POST /documents/{id}/clean)
├── archivosNER/              ← extracción NER (POST /documents/{id}/extract-entities)
└── graphs/                   ← GraphML, JSON y CSV oficiales por formato y scope
```

## Endpoints activos

| Método | Ruta | Objetivo |
|---|---|---|
| POST | `/documents` | Subir archivo; clasificación documental opcional |
| POST | `/documents/batch` | Subir múltiples con clasificación opcional común |
| PATCH | `/documents/{id}/classification` | Completar o corregir clasificación mediante form-data |
| GET | `/documents` | Listar + filtros, incluido `incubator_number` |
| GET | `/documents/{id}` | Ver uno |
| DELETE | `/documents/{id}` | Eliminar |
| POST | `/documents/{id}/process` | Convertir a MD |
| POST | `/documents/process-batch` | Convertir todos en raw |
| POST | `/documents/{id}/clean` | Limpiar texto |
| POST | `/documents/clean-batch` | Limpiar todos en converted |
| POST | `/documents/{id}/revert` | Revertir al estado anterior |
| POST | `/documents/{id}/extract-entities` | Extraer entidades NER (Anthropic LLM) |
| POST | `/documents/{id}/fuzzy-matching` | Normalizar y persistir menciones con canonical_id |
| POST | `/documents/{id}/network` | Construir red plana por documento |
| POST | `/analysis/network` | Construir red de corpus/incubadora |
| GET | `/analysis/network/latest` | Leer resumen/URLs sin recalcular |
| POST | `/analysis/network/projections/{projection_id}` | Construir proyección tipada o construcción analítica parametrizada |
| GET | `/analysis/explorer/v1/meta` | Categorías, períodos, incubadoras, idiomas, tipos de documento y documentos listos |
| POST | `/analysis/explorer/v1/network` | Red de entidades filtrada con métricas de centralidad |
| POST | `/analysis/explorer/v1/compare` | Evolución del ranking de centralidad entre períodos |
| GET | `/analysis/explorer/v1/evidence` | Oraciones que respaldan un link entre dos entidades |
| GET | `/files/graphs/{path}` | Servir solo artefactos oficiales de grafos |
| GET | `/health` | Health check |
| POST | `/semantic-network/relationships/build` | Construir relaciones deterministas entre nodos semánticos |
| GET | `/semantic-network/relationships` | Listar relaciones semánticas persistidas |
| POST | `/semantic-network/export/graphml` | Exportar la meta-red persistida a GraphML descargable |
