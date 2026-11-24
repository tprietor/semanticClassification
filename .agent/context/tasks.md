# Tareas

## Exclusiones limitadas a LOC — 24 Nov 2026

- [x] Incluir todos los lugares pedidos, más Madre de Dios River; verificar
  21 canónicos LOC y 442 menciones. Registrar PEM como regla sin coincidencias.
- [x] Aplicar la política por categoría a canónicos y formas literales antes
  de métricas, conservando Amazonian forests en eco_INFRA y términos compuestos.
- [x] Exponer configuración auditable de network/compare y separarla en caché;
  verificar 219 pruebas y 728 subpruebas del backend.
- [x] Publicar en AWS con respaldo y comprobar datos/archivos/clusters intactos;
  preparar sincronización Git con el commit probado. Recibos en export/exclude_loc_2026_11_24.

## Retirar State aislado — 24 Nov 2026

- [x] Auditar 29 términos/165 menciones con state o states y contrastar las
  21 menciones del nodo State con sus categorías originales en los JSON NER.
- [x] Añadir solo state como nombre completo a la exclusión, en cualquier
  categoría, conservando los términos compuestos y sin incluir el plural states.
- [x] Verificar 64 pruebas y 690 subpruebas; preparar publicación respaldada
  y sincronización Git. Recibos en export/exclude_state_2026_11_24.

## Retirar Agroforestry Systems — 24 Nov 2026

- [x] Añadir Agroforestry Systems y Agroforestry System por nombre completo,
  en cualquier categoría, incluyendo sus variantes de formato.
- [x] Auditar 769 menciones adicionales y verificar 64 pruebas/681 subpruebas.
- [x] Preparar publicación con respaldo, comprobación de datos y asociación
  al commit probado; recibos en export/exclude_agroforestry_systems_2026_11_24.

## Publicación web y consolidación — 24 Nov 2026

- [x] Revisar todos los cambios pendientes de backend y frontend y comprobar
  que las cinco fuentes de runtime coinciden con AWS.
- [x] Verificar backend completo: 216 pruebas y 711 subpruebas.
- [x] Verificar frontend: 53 pruebas, lint y build de producción.
- [x] Publicar frontend b97877d en Vercel y verificar GitHub/Vercel en verde;
  observar en Brave la red actualizada y distribuida con 59 documentos.
- [x] Preparar consolidación Git del backend con respaldo de las ediciones
  manuales y comprobación de DB/archivos; recibos en export/publish_web_2026_11_24.

## Excluir toda la familia SAF — 24 Nov 2026

- [x] Registrar todas las variantes y compuestos listados, numeraciones 1–14,
  tipos I–IV, sufijos y las formas compactas adicionales SAFsA/SAFsF.
- [x] Aplicar regla de familia por sigla completa SAF/SAFs antes de coocurrencias;
  cubrir alias con canónico traducido, cualquier categoría y futuros sufijos.
- [x] Verificar 97 pruebas y 698 subpruebas; conservar la opción de lista vacía
  y no confundir SAF con safe/safety/SAFTA/SAFA.
- [x] Verificar despliegue AWS: 248 menciones SAF fuera (173 adicionales),
  total de 6.631 exclusiones y 705 del lote nuevo; sin SAF en los cálculos.
- [x] Verificar conservación de DB, archivos, clusters y road pavement.

## Reaplicar exclusiones a 59 documentos — 24 Nov 2026

- [x] Auditar toda la lista reiterada por la usuaria, más exclusiones posteriores,
  sobre los 59 publicados y distinguir el lote nuevo de 11 documentos.
- [x] Añadir the Amazon, Amazonia (incluye Amazônia por normalización) y
  peruvian amazon, en cualquier categoría y por nombre completo.
- [x] Corregir el filtro para excluir también la forma literal de la mención:
  75 SAF/SAFs habían quedado bajo el canónico sistemas agroflorestais.
  Conservar las 83 menciones de SAFs-A/SAFs-F no pedidas como nombres simples.
- [x] Verificar 95 pruebas y 675 subpruebas de explorador/fuzzy matching.
- [x] Verificar AWS: 6.458 menciones fuera de cálculos, 553 del lote nuevo;
  79 canónicos completamente excluidos y uno parcialmente excluido.
- [x] Comprobar que PostgreSQL, archivos y clusters siguen intactos y que
  road pavement conserva sus 36 menciones como physical_INFRA.

## Road pavement y exclusión adicional — 24 Nov 2026

- [x] Añadir `new roads` al filtro de exclusión, sin convertirlo en road pavement.
- [x] Pasar 59 pruebas y 647 subpruebas del explorador.
- [x] Verificar la exclusión adicional en AWS y la preservación de los datos.
- [x] Unificar 11 canónicos/36 menciones bajo road pavement/physical_INFRA,
  según la corrección explícita de categoría de la usuaria; mantener las
  exclusiones previas, incluido new roads.
- [x] Respaldar y aplicar el mismo plan reversible en PostgreSQL AWS/Mac,
  preservando textos, categorías anteriores en auditoría y clusters.
- [x] Registrar 11 alias nuevos y la regla futura deterministic-v4-roads,
  con prioridad sobre alias de personas incluso si NER etiqueta road como CHAR.
- [x] Verificar API pública: una sola entidad physical_INFRA con 36 menciones;
  pasar 93 pruebas y 667 subpruebas de fuzzy matching/explorador.

## Siete exclusiones seleccionadas — 24 Nov 2026

- [x] Añadir pilot plots, plots 5 and 6, road construction,
  Leticia-Tarapaca road, new road, Transamazonica Road Region y roads
  al filtro por nombre completo; conservar road y new roads.
- [x] Verificar 59 pruebas y 646 subpruebas del explorador.
- [x] Verificar despliegue AWS, siete canónicos/87 menciones excluidos y
  preservación completa de PostgreSQL, archivos y clusters históricos.

## Exclusión de plot — 24 Nov 2026

- [x] Buscar plot/plots y sus formas compuestas en los 59 documentos actuales:
  dos canónicos LOC genéricos, 76 menciones en total.
- [x] Añadir plot por nombre completo y la variante nominal plots al filtro,
  conservando compuestos y actividades hasta decisión explícita de la usuaria.
- [x] Verificar 59 pruebas y 629 subpruebas del explorador.
- [x] Verificar la aplicación en AWS y preservación completa de DB/archivos/clusters:
  LOC pasa de 430 a 428 nodos y de 1.417 a 1.399 aristas, sin cambios de datos.
- [ ] Revisar con la usuaria las formas compuestas y los términos cercanos;
  no inferir equivalencia entre parcela, finca, campo y chacra.

## Fuzzy matching de los 11 NER nuevos — 24 Nov 2026

- [x] Comprobar KAS en las redes antes de procesar y preservar ATT/KNOW/SKILL
  como categorías originales en PostgreSQL y los JSON.
- [x] Respaldar AWS y procesar únicamente los 11 documentos con el servicio
  existente, en una transacción externa con savepoints.
- [x] Validar 5.602 menciones originales, integridad de las filas previas,
  archivos, otros documentos y tablas de clusters.
- [x] Copiar las filas resueltas a la Mac conservando UUID, fechas y detalles;
  verificar las huellas completas y proteger los 59 documentos publicados.
- [x] Verificar la API pública con 59 documentos y KAS; pasar 89 pruebas y
  618 subpruebas de fuzzy matching y explorador.
- [ ] Retomar el vocabulario controlado sobre el corpus actualizado de 59
  documentos; acordar equivalencias editoriales con la usuaria.

## Publicación selectiva de NER — 24 Nov 2026

- [x] Identificar los 11 JSON nuevos (10 es, 1 pt) y validarlos contra sus
  fuentes inglesas actuales, con 5.602 menciones.
- [x] Alinear los offsets/contextos de f9cbfc22 sobre las correcciones de espacios,
  preservando sus 31 menciones y categorías; respaldar su JSON previo.
- [x] Respaldar PostgreSQL y archivos de destino, publicar los 11 NER y las tres
  correcciones de fuente y registrar english → ner únicamente en esos documentos.
- [x] Corregir el estado local de 7503f699 y verificar igualdad de archivos/estados
  Mac/AWS, preservación de los 48 publicados, traducciones y clusters.
- [x] Incorporar estos 11 NER a las redes mediante fuzzy matching por instrucción
  posterior de la usuaria; la revisión editorial del vocabulario sigue pendiente.
- [ ] Antes de regenerar f9cbfc22, alinear también sus entradas históricas de
  segmentación/anotación; conservar como referencia el JSON publicado y su recibo.

## Unificación KAS en las redes actuales — 23 Nov 2026

- [x] Agrupar ATT/KNOW/SKILL en KAS antes de filtrar y calcular la red;
  conservar anotaciones, UUID, fuentes y clusters históricos.
- [x] Actualizar metadata, evidencia, filtros y compatibilidad de clientes antiguos.
- [x] Preparar el frontend con un único control KAS, paleta, leyendas,
  vistas guiadas, URLs y documentación metodológica coherentes.
- [x] Validar la suite completa: 208 pruebas backend y 631 subpruebas; 51 pruebas frontend,
  build y lint correctos con Node 24 temporal.
- [x] Verificar el despliegue de backend y conservación de DB/archivos/clusters.
- [x] Publicar el frontend en Vercel; `5a97c6f`, despliegue exitoso confirmado.
- [x] Sincronizar el código del backend entre Mac, GitHub y AWS, respaldando
  las ediciones manuales y conservando DB, fuentes y clusters.
- [x] Verificar el dominio público: un único control KAS, 120 canónicos y API
  con los 48 documentos; frontend y backend con checks exitosos en GitHub.

## Exclusiones del explorador: 48 documentos publicados — 23 Nov 2026

- [x] Confirmar el alcance: redes actuales de los 48 documentos; nuevos NER
  sin publicar y clusters/metaredes en espera.
- [x] Registrar la lista explícita y cubrir variantes de formato y singular/plural
  por nombre completo, en cualquier categoría, sin buscar por fragmentos.
- [x] Auditar AWS: 66 canónicos coincidentes y 4.562 menciones asociadas;
  preservar esas menciones y sus JSON.
- [x] Verificar 56 pruebas y 615 subpruebas; comprobar que el frontend usa
  los valores predeterminados del backend.
- [x] Aplicar en AWS solo el filtro del explorador con respaldo, verificar
  network/compare y comprobar que DB y clusters permanecen intactos.
- [ ] Incorporar municipios únicamente cuando la usuaria indique nombres concretos.

## Preservación Mac/AWS y etapa english — 20 Nov 2026

- [x] Respaldar PostgreSQL local antes de recuperar estados y copiar metaredes.
- [x] Verificar que el servicio NER local y desplegado exige english y usa
  english_path, sin ejecutar un proveedor ni una extracción real.
- [x] Restablecer english solo en los documentos locales pendientes, conservando
  los que avanzaron a ner durante la operación y las 66 traducciones.
- [x] Recuperar en la Mac los 48 JSON de fuzzyMatching con bytes idénticos a AWS,
  conservando los NER v2 nuevos y el corpus persistido.
- [x] Copiar los clusters y la evidencia de AWS a PostgreSQL local, conservando
  UUID, fechas y metadata; verificar igualdad de las tablas completas.
- [x] Corregir Postman y documentación del flujo cleaned → english → ner;
  añadir regresión que rechaza cleaned antes de acceder al proveedor.
- [x] Proteger los 48 UUID en el generador GLM y corregir la memoria operativa
  para conservar english y no vaciar la carpeta NER.
- [x] Publicar los 11 NER terminados el 24 Nov de forma selectiva, conservando
  las fuentes inglesas y las versiones de clusters ya calculadas.

## Tres metaredes — 20 Nov 2026 (en espera por decisión del 23 Nov)

- [x] Acordar las tres agrupaciones de categorías y el flujo backbone → Leiden
  → nodo por cluster → vector → aristas por similitud → PostgreSQL.
- [x] Confirmar la metadata de cada nuevo nodo, excluyendo Estado de revisión.
  La especificación vigente está en `PROJECT_CONTEXT.md`.
- [x] Confirmar coocurrencias por oración para las redes iniciales de entidades
  y similitud de vectores para las conexiones posteriores entre clusters.
- [x] Acordar PostgreSQL como fuente de consulta de clusters y miembros, con
  nombre canónico representativo, descripción y vector inicialmente en SQL NULL.
- [x] Acordar la ruta por ejecución y red bajo
  `s3/graphs/metanetworks/agroforestry/<ejecucion>/`.
- [x] Fijar el alcance y los parámetros de la primera ejecución, reutilizando
  el backbone y Leiden existentes; valores y resultados en `PROJECT_CONTEXT.md`.
- [ ] Definir la metodología del vector y su versión, la medida de similitud
  y la regla para crear y ponderar las aristas.
- [x] Confirmar aristas de metaredes por similitud de vectores, sustituyendo
  el criterio de coocurrencias; por ahora solo se conectan nodos de la misma
  red de origen, sin aristas entre las tres redes.
- [x] Implementar un procesador para las tres proyecciones y persistencia
  aditiva en PostgreSQL, sin Estado de revisión ni conexiones por agregación.
- [x] Calcular y guardar los clusters de las tres redes y sus miembros, con
  UUID propio, evidencia y procedencia, dejando nombre, descripción y vector
  en NULL. La ejecución vigente en AWS contiene 327 clusters y 4.104 registros
  de integrantes; la primera ejecución se conserva como referencia histórica.
- [x] Respaldar PostgreSQL antes de publicar; verificar fuente sin cambios,
  integridad completa, restricciones e idempotencia de la publicación.
- [x] Descargar únicamente esta ejecución y verificar su copia local y la
  salud de la API; no se ejecutó sincronización de la base ni de los NER.
- [x] Resolver el umbral documental: la usuaria rechazó el mínimo de 2;
  las nuevas ejecuciones admiten entidades presentes en un solo documento.
- [x] Publicar y verificar una nueva ejecución con mínimo 1 documento,
  conservando la primera ejecución como referencia histórica. Network 1 vuelve
  a incluir KNOW, ATT y SKILL; Network 2 vuelve a incluir KNOW.
- [x] Verificar la copia local completa de la ejecución vigente y ofrecer
  consultas de pgAdmin que seleccionen sus 327 clusters sin mezclar ejecuciones.
- [ ] Añadir endpoints de lectura para las nuevas ejecuciones, clusters,
  integrantes y evidencia; los endpoints históricos no sirven este nuevo esquema.
- [ ] Integrar la visualización en una nueva ventana llamada Dashboard del
  frontend existente, consultando PostgreSQL mediante la API; Gephi no es
  un requisito de la entrega.
- [ ] Calcular y persistir las aristas entre clusters cuando se definan
  vectores, similitud y regla de conexión.
- [x] Retomar la revisión de sincronización Mac → AWS por pedido de la usuaria;
  comparar bases, fuentes y NER sin modificar datos. Diagnóstico y evidencia
  en `PROJECT_CONTEXT.md` y `export/sync_review_2026_11_20/review.json`.
- [x] Conservar los 48 Agroforestry en fuzzyMatching y las dos ejecuciones de
  metaredes de AWS también en la Mac; recuperar english sin retroceder avances.
- [x] Publicar selectivamente los 11 NER nuevos el 24 Nov, sin reemplazar la
  base ni copiar estados locales de reinicio a AWS.
- [ ] Publicar cuando corresponda la corrección de `57ebcb2a` en cleaned/english
  (retirada de `》 `), con respaldo y coincidencia de fuentes para su futuro NER.
- [ ] Continuar la auditoría de los NER v2 vigentes y publicarlos en AWS cuando
  corresponda; la reanotación avanza y los 65 JSON archivados v1 no se suben.

## Inventario auditable y vocabulario controlado — 18 Nov 2026

- [x] Capturar el corpus vigente de AWS con transacción consistente y de solo lectura.
- [x] Inventariar documentos, menciones, formas, canónicos y alias, manteniendo
  la evidencia original y distinguiendo el alcance Agroforestry del legado global.
- [x] Comparar JSON NER con PostgreSQL, verificar offsets y reconciliar conteos.
- [x] Entregar Excel de revisión, TSV para OpenRefine y paquete de evidencia con
  hashes. Estado, métricas y rutas vigentes en `PROJECT_CONTEXT.md`.
- [x] Simplificar la edición en `editar_vocabulario.xlsx`: una sola hoja con todos
  los términos y dos columnas principales para nombre deseado y conservar/excluir.
- [x] Registrar las decisiones explícitas de excluir Google y usar `TFFF` como
  nombre preferido para el nombre completo y la sigla; todavía sin aplicación en DB.
- [ ] Revisar los 81 casos con la usuaria y documentar las decisiones; las propuestas
  previas y las agrupaciones léxicas no implican aprobación de equivalencias.
- [ ] Acordar el alcance y la granularidad del vocabulario a partir del inventario,
  definiendo términos preferidos, definiciones, variantes y distinciones necesarias.
- [ ] Diseñar cómo `fuzzy-matching` consultará esos acuerdos y cómo se revisarán
  nuevos candidatos antes de modificar el endpoint.

## Continuidad del filtro de nodos — 18 Nov 2026

- [x] Implementar y probar la exclusión por nombre en el explorador, con
  `Madre de Dios` y `Agroforestry` como valores predeterminados. El contrato
  vigente, archivos y validación están en `PROJECT_CONTEXT.md`, en el punto
  de continuidad actualizado el 18 Nov.
- [x] Guardar el estado local para apagar el equipo, sin commit, push o despliegue.
- [x] Al retomar el 18 Nov, comprobar `git status` y HEAD antes de editar;
  conservar los cambios locales del filtro y distinguir los nueve commits anteriores.
- [x] Repetir las pruebas del explorador: 53 pruebas y 578 subpruebas exitosas.
- [x] Registrar el filtro y su contexto en el mismo commit, autorizado el 18 Nov.
- [x] Publicar los diez commits pendientes, incluido `e56c4b8`.
- [x] Validar la suite local completa: 196 pruebas y 591 subpruebas exitosas.
- [x] Comparar y respaldar los 14 archivos editados directamente en EC2;
  conservarlos en stash y guardar la imagen anterior antes de actualizar.
- [x] Desplegar manualmente `e56c4b8` en EC2 y verificar `/health`, `/network`,
  `/compare` y la desactivación del filtro por nombre en un alcance vacío.
  Resultado y evidencia vigentes en `PROJECT_CONTEXT.md`.
- [ ] Comprobar visualmente el filtro en el dashboard después de recargarlo.
- [x] Comprobar que GitHub Actions volvió a ejecutar las pruebas: el check
  del backend `d69414f` terminó correctamente el 23 Nov. El bloqueo observado
  el 18 Nov no impidió esta publicación.

## Limpieza y traducción de la Guía del EUDR — 11 Nov 2026

- [x] Revisar `b4ac3608-c2c2-46ca-8877-564fa4775362` contra convertido y PDF:
  retirar 26 pies/cabeceras, índice, créditos de impresión, restos de enlaces,
  marcas de formato y viñetas de extracción. Conservar los seis anexos,
  las notas normativas y los códigos de productos.
- [x] Reparar ocho continuaciones y espaciado con respaldo del PDF; recuperar
  glosario, rótulos y encabezados perdidos. Aplicar en AWS y copia local con
  respaldo y SHA-256; 84.795 caracteres, 369 párrafos. Sigue `cleaned/es`.
- [x] Conservar las 360 traducciones guardadas y crear un borrador JSON alineado
  con la limpieza en `export/eudr_cleaning_2026-11-11/english_rebased_draft.json`.
- [ ] Completar/revisar la versión inglesa sobre el hash nuevo del `cleaned`:
  37 bloques originales sin traducir; el borrador marca 52 párrafos para
  traducir/completar contando las recuperaciones y 119 para revisión, con
  solapamiento entre grupos. No publicar un archivo parcial ni cambiar aún
  el estado. Los checkpoints antiguos usan los índices anteriores.
  El intento directo sin Anthropic del 11 Nov fue bloqueado por un filtro
  de contenido y no guardó una traducción completa; consultar
  `export/eudr_english_2026-11-11/checkpoint.json`. No reintentar ni reproducir
  el bloque mediante otros formatos, fragmentación, herramientas o subagentes.
  Queda como alternativa recibir una traducción completa aportada por la usuaria.

## Corrección puntual de `70767dc6` — 11 Nov 2026

- [x] Desplegar los siete archivos de la etapa `english` autorizados y reiniciar
  la API; ocho pruebas exitosas con las dependencias de producción, rutas y
  explorador verificados. Migración `f0a1b2c3d4e5` previamente aplicada.
- [x] Ejecutar `POST /documents/70767dc6-c115-46fe-b002-90f8445fd958/translate`:
  HTTP 502 porque Anthropic rechazó la verificación de idioma por saldo
  insuficiente. Comprobar que sigue `cleaned`, `language=en`, sin `english_path`.
- [x] Corregir el flujo de `language=en` por indicación de la usuaria: copiar
  directamente el `cleaned`, sin Anthropic ni clave de API; ocho pruebas
  exitosas localmente y con las dependencias de producción. Desplegado y API reiniciada.
- [x] Repetir el POST para `70767dc6`: HTTP 200, `status=english`,
  `language=en`, `translated=false`; archivo inglés descargable y copia local
  con el mismo SHA-256 del `cleaned`. El fallo inicial de saldo queda superado
  para este documento; NER y fuzzy matching no se ejecutaron.
- [x] Retirar autores, afiliaciones, cabeceras repetidas y material editorial
  final del `cleaned` de `70767dc6-c115-46fe-b002-90f8445fd958`; reparar los
  cortes de continuidad conservando el contenido sustantivo y los ocho pies
  de figura. Aplicado en AWS y copia local, con respaldos y hashes verificados.
- [x] Corregir `language` de `es` a `en` en PostgreSQL de AWS, manteniendo
  `status=cleaned`, `english_path=NULL`, `ner_path=NULL` y cero menciones.

## Auditoría de limpieza y nuevo NER — 2 Nov 2026

- [x] Sustituir la limpieza lingüística con Anthropic por una limpieza
  determinista que conserve idioma, párrafos y contenido anterior a referencias.
- [x] Regenerar desde el Markdown inglés el texto limpio de
  `660086b9-93ec-4bd6-bd73-b89088ef19f1`, con respaldo del anterior.
- [x] Contrastar y regenerar los otros 16 documentos Agroforestry señalados
  por posible traducción, con respaldos individuales y verificación de copia.
- [ ] Auditar el contenido de cada `cleaned` antes de su nuevo NER; el control
  heurístico de idioma no detecta todas las posibles omisiones o errores.
- [x] Comparar los 62 documentos Agroforestry con `language = es` contra sus
  convertidos; identificar errores de Anthropic y bibliografías persistentes.
- [x] Regenerar los 62 `cleaned` españoles desde `converted`, quitando 57
  secciones bibliográficas y conservando capítulos, anexos y celdas de tablas;
  sin respaldos nuevos del texto anterior.
- [ ] Revisar manualmente los 62 textos regenerados antes de NER, con prioridad
  en los 4 que tenían errores confirmados, los 14 con diferencias relevantes,
  los documentos con OCR y los que dependen de tablas complejas.
- [x] Corregir de `en` a `es` el idioma de cuatro documentos con contenido
  principal en español; el corpus local pasa a 66 `es`.
- [x] Auditar y corregir el `cleaned` de los cuatro documentos recién
  reclasificados; retirar respuestas de Anthropic, bibliografías y resúmenes
  ingleses duplicados, preservando los datos de las fuentes convertidas.
- [x] Corregir el descarte de párrafos largos por la regla de autoría y
  regenerar los 29 documentos españoles anteriores afectados.
- [ ] Decidir si `32eea2e1` debe entrar al NER: su fuente es una conversación
  de búsqueda de literatura, no un estudio primario verificable.
- [x] Completar el NER manual del primer documento inglés sobre el `cleaned`
  reparado: 38 bloques, 360 oraciones, 505 menciones y offsets validados;
  guardar JSON oficial y pasar el documento a `ner` sin Anthropic.
- [x] Auditoría humana de las 505 menciones del primer documento: la usuaria
  confirmó que todo está correcto. El documento permanece en `ner`.
- [x] Reparar el `cleaned` de `c13401cf-aca9-4cbb-846a-803b6b330d3a`:
  retirar dos bibliografías, afiliaciones y material editorial; recuperar el
  resumen y unir pasajes cortados por columnas, sin respaldo nuevo del anterior.
- [x] Completar su NER manual sin Anthropic: 263 oraciones, 318 menciones con
  offsets validados; JSON oficial guardado y estado `ner`.
- [ ] Esperar la auditoría humana de las 318 menciones del segundo documento,
  en particular las 37 marcadas `medium`. No ejecutar fuzzy matching.
- [x] Reparar el `cleaned` de `ce37176e-2970-4ff8-b081-d11ed61386c2`
  desde el `converted` inglés: retirar bibliografía, material editorial y una
  respuesta de Anthropic; conservar resumen, tablas y notas sustantivas.
- [x] Completar su NER manual sin Anthropic: 328 oraciones, 403 menciones con
  offsets validados; JSON oficial guardado y estado local `ner`.
- [ ] Esperar la auditoría humana del tercer documento, con atención a las 52
  menciones marcadas `medium`. No ejecutar fuzzy matching.
- [x] Corregir el `cleaned` inglés de `0ee3a358-0b9a-4899-8def-1471e13b98dc`:
  retirar resumen portugués duplicado, metadatos editoriales y créditos de
  figuras; unir ocho pasajes cortados, sin respaldo nuevo del anterior.
- [x] Completar su NER manual con cobertura determinista de siglas: 359
  oraciones, 631 menciones con offsets validados; JSON oficial y estado `ner`.
- [ ] Esperar la auditoría humana del cuarto documento, incluidas las 107
  menciones marcadas `medium`. No ejecutar fuzzy matching.
- [x] Reparar el `cleaned` de `1e76e99b-cfd5-4f42-846f-44490ba6ff04`
  con cotejo del PDF: quitar material editorial y bibliografía, separar pies de
  figura, unir oraciones cortadas y reconstruir las tablas 1 y 2 legiblemente.
- [x] Completar su NER manual: 325 oraciones, 546 menciones con offsets
  validados; JSON oficial guardado y documento local en `ner` sin Anthropic.
- [ ] Esperar la auditoría humana del quinto documento, incluidas las 102
  menciones `medium`. No ejecutar fuzzy matching.
- [x] Reparar el `cleaned` inglés de `17f2d625-5dda-44e8-9051-af960d4870ec`:
  recuperar el resumen omitido, separar párrafos y reconstruir las tablas 1 y 2
  cotejadas con el PDF, sin guardar respaldo del `cleaned` anterior.
- [x] Completar su NER sin Anthropic: 270 oraciones, 355 menciones literales con
  offsets validados; JSON oficial guardado y estado local `ner`.
- [ ] Esperar la auditoría humana del sexto documento, incluidas las 16
  menciones `medium`. No ejecutar fuzzy matching.
- [x] Reparar el `cleaned` inglés de `6c19caf1-09ef-443f-93d5-12f092eb6711`:
  retirar portada, autores, índice y título duplicado; corregir nombres y OCR
  contra el PDF, y restaurar la atribución a la lista roja de IUCN.
- [x] Completar su NER manual sin Anthropic: 92 oraciones, 117 menciones
  literales con offsets validados; JSON oficial y estado local `ner`.
- [ ] Esperar la auditoría humana del séptimo documento, incluidas las 25
  menciones `medium`. No ejecutar fuzzy matching.
- [x] Reparar el `cleaned` inglés de `089089a9-e93c-493a-8f85-14a1da1b4a67`:
  retirar metadatos y bibliografía; recomponer el orden de lectura, las seis
  tablas y los párrafos cortados cotejando el PDF. Preservar las dos cifras
  contradictorias sobre el área media de concesiones de conservación.
- [x] Completar su NER sin Anthropic: 354 oraciones, 945 menciones literales
  con offsets validados; JSON oficial y estado local `ner`.
- [ ] Esperar la auditoría humana del octavo documento, incluidas las 81
  menciones `medium`. No ejecutar fuzzy matching.
- [x] Reparar el `cleaned` inglés de `5f87adae-ade1-4ff4-b880-7951c20c839b`
  (*Amazon Assessment Report 2025*, 497 páginas): retirar portada, nueve bloques
  extensos de bibliografía, afiliaciones y referencias residuales, y reparar
  ligaduras OCR. Texto final: 626.325 caracteres, sin respaldo nuevo.
- [x] Primera extracción NER asistida por reglas y revisión distribuida por
  capítulos: 3.632 oraciones, 4.305 menciones con offsets literales validados;
  37 apariciones de «agroforestry» cubiertas por PRAC. JSON oficial, estado
  `ner`, cero llamadas a Anthropic.
- [ ] Auditar humanamente el noveno documento completo, con prioridad en las
  1.001 menciones `medium` y las 1.462 oraciones sin anotaciones. Por su tamaño,
  la revisión realizada no fue oración por oración. No ejecutar fuzzy matching.
- [x] Reparar los `cleaned` de cinco documentos recibidos juntos:
  `72d1ae85`, `79a0af26`, `2c2d1176`, `0142af8f` y `13e119a1`. Se retiró
  una respuesta de Anthropic y una sección traducida del primero, se
  restituyeron resúmenes omitidos en el segundo y cuarto, y se recuperaron
  tablas del suplemento. No se guardaron respaldos nuevos.
- [x] Primera extracción NER asistida por reglas y revisión distribuida de
  estos cinco: 701, 503, 587, 559 y 103 menciones respectivamente (2.453 en
  total), offsets y regla Agroforestry/AFSs validados, JSON oficiales y
  auditorías TSV; estados locales `ner`, cero llamadas a Anthropic.
- [ ] Auditoría humana de las cinco extracciones, incluidas 17, 9, 13, 42 y 0
  menciones `medium` respectivamente; el `.docx` es material suplementario
  (cuestionarios y tablas de factores), no un artículo independiente. No
  ejecutar fuzzy matching.
- [x] Reparar el `cleaned` inglés de `1963df4b-4dae-4165-99ea-0f78ceb54844`:
  quitar bibliografía y material editorial, recomponer cortes de dos columnas
  y conservar la tabla de especies; sin respaldo del anterior.
- [x] Primera extracción NER del mismo documento sin Anthropic: 219 oraciones,
  250 menciones literales validadas, 3 apariciones de «agroforestry» en PRAC,
  JSON oficial, auditorías TSV y estado local `ner`.
- [ ] Auditoría humana de ese NER, con prioridad en 5 menciones `medium` y
  oraciones sin anotación. No ejecutar fuzzy matching.
- [x] Reparar los `cleaned` de `52c29204`, `da3b78cd`, `1f2f0bca`,
  `260404f5` y `32377694`: retirar bibliografía/editorial, reparar cortes y
  conservar cuerpo y fichas útiles de la tesis; sin respaldo anterior.
- [x] Primera extracción NER asistida por reglas específicas para esos cinco:
  142, 284, 560, 428 y 142 menciones, respectivamente. Offsets, regla
  Agroforestry/AFSs y unicidad de artefactos validados; JSON oficiales,
  auditorías TSV, estados `ner`, cero llamadas a Anthropic.
- [ ] Auditoría humana de los cinco NER, con 1, 8, 8, 5 y 3 menciones
  `medium` respectivamente. Dar prioridad a la tesis larga y sus oraciones
  sin anotación. No ejecutar fuzzy matching.
- [x] Reparar el `cleaned` de `3facb6fe-5f4e-46a3-b4be-5f304a63b0bd`:
  retirar duplicados editoriales, notas al pie, tablas OCR ilegibles y
  bibliografía; recomponer el cuerpo del informe sin respaldo anterior.
- [x] Primera extracción NER del informe sin Anthropic: 527 oraciones, 721
  menciones con offsets validados, 34 apariciones de «agroforestry» en PRAC,
  JSON oficial, auditorías TSV y estado local `ner`.
- [ ] Auditoría humana del informe: 32 menciones `medium`, 165 oraciones sin
  anotación y revisión editorial de «Law 12.625 / 2012» (el número coincide
  literalmente con el PDF). No ejecutar fuzzy matching.
- [x] Reparar los `cleaned` de `35bfba4d`, `58a33d2c`, `702adc1b`,
  `5ce3cf43`, `600282ba` y `571e5304`: retirar índice/editorial, respuestas
  de Anthropic y referencias; recuperar el cuerpo perdido del artículo de
  puntos de inflexión; unir cortes y corregir OCR repetido sin respaldos.
- [x] Primera pasada NER sin Anthropic de esos seis: 507, 383, 127, 227, 147
  y 199 menciones, respectivamente; offsets y regla PRAC de «agroforestry»
  validados, JSON oficiales y auditorías TSV; estados locales `ner`.
- [ ] Auditoría humana de los seis NER, priorizando las 90, 5, 3, 23, 48 y 12
  menciones `medium` y las 738, 142, 197, 64, 139 y 22 oraciones sin
  anotación. El informe de Tambopata tiene 420 oraciones largas vacías y
  requiere revisión exhaustiva. No ejecutar fuzzy matching.
- [x] Reparar los `cleaned` de `9c6aa0f7`, `7f93c3ee`, `8b3e8649`,
  `7824b517`, `7a5d2888` y `8d9ec319`: normalizar OCR, recuperar resumen y
  capítulo perdidos, quitar referencias, notas y material editorial; sin
  respaldos del texto anterior.
- [x] Primera pasada NER sin Anthropic de esos seis: 84, 288, 50, 755, 197
  y 210 menciones; offsets y regla PRAC de agroforestry/AFSs validados,
  JSON oficiales, auditorías TSV y estados locales `ner`.
- [ ] Auditoría humana de esos seis NER, priorizando el capítulo de
  bioeconomía (`7824b517`): 208 menciones `medium`, 423 oraciones sin
  anotación y OCR residual. Los otros cinco tienen 8, 1, 7, 5 y 12
  menciones `medium`. Revisar posibles omisiones en los dos estudios de agua
  y cacao; no ejecutar fuzzy matching.
- [x] Reparar los `cleaned` de `a14ca4bd`, `a5b24931`, `c46f0d74`,
  `ca251938`, `c2a154e1` y `c60d39ce`: cotejar fuentes, quitar créditos,
  editorial y bibliografías; extraer el texto de las 15 diapositivas y
  conservar cuerpo y anexos sustantivos sin respaldar el cleaned anterior.
- [x] Primera pasada NER de estos seis sin Anthropic: 164, 70, 41, 351, 278
  y 749 menciones, respectivamente; offsets y cobertura PRAC validados,
  JSON oficiales, TSV de auditoría y estados locales `ner`.
- [ ] Auditoría humana de las seis extracciones, con 42, 19, 0, 4, 31 y 13
  menciones `medium` y 78, 146, 8, 340, 119 y 726 oraciones sin anotación.
  Priorizar `c60d39ce` por su longitud y posibles omisiones; revisar también
  tesis, PES y métodos acústicos. No ejecutar fuzzy matching.
- [x] Reparar los `cleaned` de `e5b823c9`, `d4e43ea2`, `e3d7bf1a`,
  `d724a225`, `f9d78335` y `da74aa93`: quitar editorial y listados,
  reconstruir resúmenes y frases cortadas, y retirar índice/formularios de
  la tesis sin respaldar el cleaned anterior.
- [x] Primera pasada NER sin Anthropic para estos seis: 259, 435, 481, 354,
  2.985 y 50 menciones; offsets, cobertura PRAC y unicidad validados;
  JSON oficiales, TSV de auditoría y estados locales `ner`.
- [ ] Auditoría humana de los seis, priorizando la tesis `f9d78335` (102
  menciones `medium`, 1.177 oraciones vacías), el artículo histórico
  `e5b823c9` (71 `medium`) y el estudio fisiológico `da74aa93` (470
  oraciones vacías). Revisar siglas de sistemas en `d4e43ea2`. No ejecutar
  fuzzy matching.
- [x] Reparar los `cleaned` de `d755356e`, `ef62dfe2` y `e8355e39`:
  quitar bibliografía del primero, créditos/editorial del taller y recomponer
  frases partidas por figuras; sin respaldo del cleaned anterior.
- [x] Primera pasada NER de los tres sin Anthropic: 340, 112 y 187
  menciones, JSON oficiales, TSV de auditoría, offsets y PRAC validados;
  estados locales `ner`.
- [ ] Auditoría humana de los tres, con 42, 57 y 114 oraciones sin
  anotación. Revisar la clasificación Agroforestry de `d755356e`, cuyo
  contenido trata minería y no menciona literalmente agroforestry; no
  ejecutar fuzzy matching.

## Explorador interactivo de entidades — 26 Oct 2026

Decisiones: enlazar las diez categorías; importancia = recurrencia documental +
centralidad; evolución por períodos 2021–2023 y 2024–2026; priorizar la red de
entidades. La pausa metodológica de meta-red y clusters se revisó el 20 Nov;
consultar el acuerdo vigente en `PROJECT_CONTEXT.md` y las tareas de las tres
metaredes al inicio de este archivo.

- [x] `src/analysis/explorer.py` — filtros por etapa, métricas, top-n y comparación entre períodos.
- [x] `src/services/explorer.py` y `src/api/routers/explorer.py` — `/analysis/explorer/v1/{meta,network,compare,evidence}`.
- [x] `load_db_mentions(document_ids=...)` — filtro aditivo por documentos.
- [x] `scipy` declarado en `requirements.txt` (lo exige `networkx.pagerank`).
- [x] 20 pruebas en `tests/test_explorer.py`; prueba de punta a punta sobre PostgreSQL temporal con corpus sintético.
- [x] Filtro `productive_sector` (Agroforestry por defecto) en todos los endpoints del explorador.
- [x] Despliegue preparado: `docker-compose.prod.yml`, gateway Caddy, scripts y guía en `deploy/aws/`.
- [x] Desplegar en el project AWS (us-east-2) siguiendo `deploy/aws/AGENT-RUNBOOK.md` desde la Mac de Tania y migrar la base real.
- [ ] Activar el despliegue automático en el EC2: `bash deploy/aws/install-autodeploy.sh` (`deploy/aws/CI-CD.md`).
- [ ] Decidir si `/analysis/network`, las proyecciones y Leiden también filtran por sector.
- [x] Registrar y verificar `language`, `year` y `document_type` de los 116 documentos Agroforestry locales según la tabla de la usuaria (27 Oct 2026).
- [ ] Completar los metadatos del resto del corpus si se incorpora al análisis; sin año los documentos no entran en la evolución.
- [ ] Probar el explorador sobre la DB real después de reprocesar con las diez categorías.
- [x] Red del explorador más rápida: métricas con igraph y caché de redes por alcance y filtros estructurales.

## Trabajo anterior: codebook y piloto NER — 16 Oct 2026

### Revisión y validación actual

- [x] Descartar los ejemplos few-shot, eliminar su archivo y cargador e incorporar el codebook inglés completo al prompt mediante `NER_CODEBOOK_PATH`.
- [x] Limitar el prompt de usuario a las oraciones e identificadores del documento; retirar la inyección independiente de definiciones y conservar los diez códigos del esquema.
- [x] Verificar el flujo sin demostraciones: 108 pruebas exitosas y 2 omitidas; preparar el piloto con huellas del codebook vigente y conservar el formato de párrafos en una sola línea.
- [x] Unificar codebook e instrucciones del bloque en `ner_prompt.md`; retirar `ner_user_prompt.md` y su configuración.
- [ ] Validar un piloto real con la estrategia `codebook-single-prompt`; los resultados anteriores con demostraciones no validan este cambio.

- [x] Revisar y crear los commits pendientes antes de nuevas ediciones:
  `56e2526` (codebook y documentación), `7e6ff24` (definiciones, prompts, ejemplos).
- [x] Leer completa la sección 6, incluidas 6.1–6.3, y contrastarla con las
  categorías, el prompt y el parser.
- [x] Completar delimitación, artículos y nombres, siglas, enumeraciones,
  pronombres, repeticiones, anidación, negación y temporalidad. Conservar
  normalización y relaciones fuera de NER.
- [x] Alinear el prompt y el parser con la anidación estricta LOC dentro de
  CHAR y añadir regresiones para ambos órdenes, repeticiones y rechazos.
- [x] Completar secciones 7–10 y anexo A sobre el contrato existente.
- [x] Hacer una comprobación final de coherencia entre codebook, definiciones,
  prompts, ejemplos y código. Verificar los archivos guardados para evitar
  recuperar accidentalmente versiones anteriores desde el editor.
- [x] Ejecutar el piloto real de biocarbón y contrastar texto, respuestas y
  menciones conservadas: 74/68 y 86/77 en las dos extracciones completas.
  Artefactos: `data/output/ner_pilot/`. No se escribió en la DB.
- [x] Añadir validación estricta de la respuesta NER, hasta dos correcciones
  por bloque inválido y fallo explícito sin guardar una extracción parcial.
- [ ] Cerrar la revisión de CHAR dentro de CHAR: el modelo sigue devolviendo
  «UNAMAD» dentro de «estudiantes de la UNAMAD», prohibido en el borrador 0.2.
  Se presentó a la usuaria la elección entre conservar la denominación completa
  o permitir ambas cuando identifiquen actores distintos. No hay respuesta aún.
- [ ] Revisar las correcciones semánticas del piloto (residuos/prácticas,
  hornos productivos, sedes como ubicaciones, fragmentos amplios y omisiones).
  Adjudicar una referencia y obtener una extracción aceptada antes del corpus.
- [x] Revisar y registrar en Git los diez archivos con cambios del 16 Oct; los commits
  pendientes de la sesión anterior ya quedaron creados.
- [ ] Validar el endpoint con la API iniciada/reiniciada y el prompt vigente;
  Docker estaba detenido. Fuzzy matching y red siguen como pasos posteriores.

### Avances de la revisión

- [x] Sustituir la sección 2.4 por el contexto territorial y temático aprobado,
  retirando de esa sección la descripción del informe de Tambopata.
- [x] Delimitar NER a extracción y clasificación en el codebook y ambos prompts;
  mantener normalización y relaciones como tareas posteriores independientes.
- [x] Registrar el contexto permitido y la evidencia requeridos en la sección 3.
- [x] Retirar del codebook las referencias a «la usuaria», al proceso de
  elaboración y al informe externo. Conservar el antecedente bibliográfico
  en la sesión `../sessions/2026-10-15-codebook-autonomo.md`.
- [x] Completar criterios generales y secciones de ambigüedad, salida y
  procedimiento de validación; queda la revisión del piloto.
- [x] Precisar el tratamiento de afirmaciones generales en KNOW y trasladarlo
  a la definición de categoría incorporada al prompt.
- [x] Completar los criterios básicos de ATT, evidencia, exclusiones, amplitud,
  delimitación y ejemplo; incorporar la delimitación aprobada al prompt.
- [x] Completar los criterios básicos de SKILL, evidencia, exclusiones,
  capacidad operativa, delimitación y ejemplo; incorporarlos al prompt.
- [x] Completar las fichas PRAC, physical_INFRA, soft_INFRA, eco_INFRA, RUL y LOC
  con evidencia, exclusiones, delimitación, fronteras y ejemplos; actualizar
  las definiciones incorporadas al prompt y la demostración de soft_INFRA.

- [x] Acordar el propósito operativo, el marco conceptual y el enfoque temático.
- [x] Acordar las definiciones de las diez categorías en
  `codebook_en_construccion.md`.
- [x] Delimitar funcionalmente las tres categorías de infraestructura.
- [x] Acordar que CHAR incluye actores con nombre propio o denominación
  genérica cuando el contexto establece su participación o papel.
- [x] Acordar que CHAR incluye personas o colectivos afectados, aunque no
  ejecuten una acción, cuando la afectación está respaldada por el texto.
- [x] Acordar la inclusión de planes en RUL cuando el contexto los presenta
  como instrumentos que establecen condiciones, responsabilidades o criterios
  para las prácticas territoriales.
- [x] Acordar LOC dentro de CHAR: «comunidad de San Pedro» como CHAR
  y «San Pedro» como LOC en la misma oración. Registrar el acuerdo en la
  sección 6 sin generalizar a otras combinaciones ni al mismo fragmento.
- [x] Acordar que en «El taller se realizó en la comunidad de San Pedro»
  solo se anota «San Pedro» como LOC: el contexto ubica el evento sin
  identificar al colectivo como actor.
- [x] Registrar «monitoreo comunitario» como PRAC en «Se realizan
  actividades de monitoreo comunitario», por confirmación de la usuaria.
- [x] Acordar que CHAR se extrae de expresiones que nombran al actor;
  excluir pronombres como «Ellos», aunque su referente sea claro.
- [x] Omitir el artículo inicial que introduce la denominación CHAR:
  «productoras de cacao», sin «Las». Ajustar los ejemplos anteriores;
  conservar los artículos integrantes de nombres propios por el acuerdo posterior.
- [x] Conservar la forma literal de los fragmentos extraídos, incluido
  el plural; distinguir las menciones de la normalización posterior.
- [x] Registrar cada aparición de una mención repetida con su ubicación
  y contexto; conservar las evidencias al vincularlas a un nodo canónico.
- [x] Extraer el nombre completo y la sigla explícitos como dos registros
  CHAR independientes: «Asociación de Productores de Cacao» y «APC».
- [x] Vincular posteriormente esas dos menciones al mismo nodo canónico,
  conservando los registros originales, cuando el texto establece su identidad.
- [x] Extraer por separado actores enumerados explícitamente:
  «productoras de cacao» y «recolectores de castaña», sin artículos ni conjunción.
- [x] Anotar «municipalidad» como CHAR cuando su participación está
  negada, conservando la negación en el contexto y sin afirmar participación.
- [x] Conservar íntegros los nombres propios como «La Esperanza», sin
  eliminar su artículo integrante ni anotarlo por separado.
- [x] Acordar «cooperativa La Esperanza» como fragmento CHAR, conservando
  el descriptor y el nombre propio íntegro.
- [x] Reorientar el trabajo a las características de clasificación por
  categoría y reunir los acuerdos de extracción de CHAR en la sección 6.3.
- [x] Revisar el contrato NER, modelos PostgreSQL y persistencia, sin
  ejecutar Claude ni escribir en la DB. Registrar resultados en
  `../sessions/2026-10-12-revision-contrato-ner.md`.
- [x] Registrar como decisión final el conjunto de diez categorías y sus
  códigos exactos; no volver a plantear cinco frente a diez como una elección.
- [ ] **Foco actual:** cerrar un codebook básico apoyado en la estructura
  del código existente y en el uso eficiente de Claude. Priorizar las diez
  categorías y sus criterios esenciales; aprovechar la salida estructurada
  y el enriquecimiento local ya implementados. Los ejemplos solo deben
  aclarar criterios generales, sin abrir cadenas de casos individuales.
- [x] Establecer las diez categorías finales en el código de extracción,
  validación y canonicalización; adaptar prompt, ejemplos, red completa y
  visualizador. Comprobar localmente sin llamadas a Claude ni DB real.
- [x] Implementar la anidación acordada LOC dentro de CHAR.
- [ ] Resolver en fuzzy matching la unión de nombre completo con sigla cuando
  el texto establece su identidad, conservando las menciones. No hacerlo en NER.
- [x] Inventariar en seco las 23.135 menciones NER de 48 documentos
  Agroforestry y contrastar Wyss/agroforestería con la base fuzzy histórica:
  libro de auditoría actualizado con 3.098 grupos propuestos, las 3.584
  formas literales y 14.981 menciones en grupos de dos o más formas. Mantiene
  las 17 preguntas clave del legado; sin ejecutar el endpoint.
- [ ] Resolver con la usuaria los canónicos propuestos de Wyss Academy,
  WA SAM Hub/WA y agroforestry/AFS/SAF, y revisar categorías erróneas antes
  de habilitar reglas o migraciones. El endpoint actual no corrige NER.
- [x] Ejecutar el endpoint fuzzy matching sobre los 48 Agroforestry en `ner`:
  todos pasaron a `fuzzyMatching`, con 23.135 entidades persistidas y sin
  discrepancias de conteo por documento. Los 67 restantes siguen en `cleaned`.
- [ ] Auditar y resolver los 25 grupos de variantes que el endpoint dejó
  repartidos entre varios canónicos, antes de asumir que el agrupamiento
  propuesto en el Excel se aplicó a PostgreSQL.
- [x] Añadir `GET /documents/{id}/entities` para auditar en Postman las
  menciones resueltas por documento, con paginación y filtros; verificado
  contra la API y PostgreSQL sin construir la red.
- [x] Corregir las categorías confirmadas en el legado: `WA SAM Hub` LOC→CHAR
  (1 mención), `agroforestry systems` LOC→PRAC (4 menciones), retirar
  `Wyss Academy` LOC huérfano y los canónicos incorrectos sin referencias;
  sincronizar JSON de NER, PostgreSQL, prompt, codebook y libro de auditoría.
- [ ] Definir una nueva proyección analítica del esquema de diez categorías
  antes de sustituir la selección histórica `prac-infra-rul-v2`. Reclasificar
  INFRA histórico según su contexto, sin convertirlo automáticamente.
- [x] Completar reglas de delimitación y ejemplos de validación básicos.
- [x] Consolidar reglas mínimas de anotación y contrastarlas con el contrato
  existente; regresiones locales verificadas.
- [ ] Documentar por separado, en las especificaciones de fuzzy matching y red,
  los criterios de canonicalización, atributos adicionales de nodos y ventana
  y conteo de coocurrencia; contrastarlos con la implementación existente.

Contexto vigente: `PROJECT_CONTEXT.md`. Decisiones de esta sesión:
`../sessions/2026-10-12-codebook-char.md`. Antecedente:
`../sessions/2026-10-09-codebook-continuidad.md`.

## Objetivo 1: Ingesta de documentos ✅

- [x] `src/config.py` — settings sin credenciales
- [x] `src/models/database.py` — conexión DB
- [x] `src/models/documents.py` — ORM Document
- [x] `src/models/documents_repo.py` — CRUD + actualizar_status + leer_por_status
- [x] `src/models/storage.py` — guardar, leer, eliminar en s3/archivosCrudos
- [x] `src/services/documents.py` — DocumentService + excepciones
- [x] `src/api/routers/documents.py` — POST, GET, GET/{id}, DELETE, POST /batch
- [x] `src/api/schemas/documents.py` — DocumentRead, DocumentListResponse, BatchProcess*
- [x] `src/api/main.py` — FastAPI + exception handler
- [x] `documents.incubator_number` — dimensión controlada `1..8`, indexada y validada en PostgreSQL
- [x] `POST /documents` y `POST /documents/batch` — incubadora obligatoria y seleccionable en OpenAPI
- [x] `GET /documents?incubator_number=1..8` — filtro de documentos por incubadora
- [x] Migración `c4d5e6f7a8b9` aplicada; el esquema admite temporalmente incubadora `NULL` para legado
- [x] Eliminados 29 documentos de prueba que permanecían en estado `raw` y sus archivos físicos
- [x] Seguimiento: eliminado `1770a776-d813-47c0-8738-b7f23e06f230` tras revertirlo a `raw`
- [x] `61b5cf8e-8109-408c-a571-cdf5b31512ca` asignado a `incubator_number = 1`
- [x] `documents.language` — idioma del documento (`es`, `en`, `pt`, etc.), nullable, indexado
- [x] `PATCH /documents/{id}/language` — registrar idioma después de la carga
- [x] `POST /documents/set-language-batch` — registrar idioma en lote
- [x] `GET /documents?language=...` — filtrar documentos por idioma
- [x] Migración `d5e6f7a8b9c0` aplicada; todos los documentos existentes quedan con `language = NULL`
- [x] Atributos opcionales en cargas nuevas: `year`, `productive_sector` y `document_type`
- [x] `year` validado como entero de cuatro dígitos (`1000..9999`)
- [x] `productive_sector` usa vocabulario controlado; opción vigente: `Agroforestry`
- [x] `document_type` usa las opciones `academic`, `technical_report`, `project_report`,
  `policy_document`, `manual_or_guide`, `institutional_document` y `other`
- [x] Migración `a4b5c6d7e8f9` aplicada; las columnas son nullable únicamente para compatibilidad histórica
- [x] Colección de Postman actualizada para ingesta individual y por lote
- [x] `PATCH /documents/{id}/classification` con `form-data` para completar o corregir parcialmente esos atributos

## Objetivo 2: Conversión a Markdown ✅

- [x] ~~`markitdown[pdf,docx]` en requirements.txt~~ → reemplazado por `docling`
- [x] `s3/archivosConvertidos/` — destino de archivos .md
- [x] `config.py` — STORAGE_CONVERTED
- [x] `models/documents.py` — columna converted_path
- [x] `services/documents.py` — DocumentService.convertir() con Docling + convertir_varios()
- [x] `api/routers/documents.py` — POST /documents/{id}/process + /process-batch
- [x] Dockerfile — `libgl1`, `libglib2.0-0`, `libxcb1` para OpenCV/Docling
- [x] Probado: 200, 404, 409

### Refactors del objetivo 2
- [x] `models/storage.py` — unificado `guardar(content, filename, target_dir)`, eliminado `guardar_convertido`
- [x] `services/documents.py` — absorbido `ConversionService.convertir()` → `DocumentService.convertir()`
- [x] `api/routers/documents.py` — absorbido `conversion.py`, renombrado `ingesta.py` → `documents.py`
- [x] `api/schemas/documents.py` — renombrado de `ingesta.py`
- [x] Eliminados `services/conversion.py`, `api/routers/conversion.py`, `api/routers/ingesta.py`, `api/schemas/ingesta.py`

### Mejora de rendimiento PDF — Jun 12 2026
- [x] `requirements.txt` — agregado `PyMuPDF`
- [x] `Dockerfile` — agregados `libxcb-shm0`, `libxcb-xfixes0`, `libxcb-xinerama0`, `libglx-mesa0`
- [x] `src/services/pdf_converter.py` — **nuevo** convertidor híbrido:
  - Fast path: PyMuPDF para PDFs nativos (~0.1-1s por documento)
  - Fallback: Docling OCR para PDFs escaneados (~60-90s por documento)
- [x] `src/services/documents.py` — `convertir()` reutiliza `PdfConverter` (lazy)
- [x] Batch de 27 PDFs convertidos en **28 segundos** (vs ~2-3 horas con Docling puro)

### Refactor de simplificación — feat/reedireccion2
- [x] `src/services/pdf_converter.py` — API simplificada: `convertir(file_path: str) -> str`
- [x] `src/services/pdf_converter.py` — código muerto eliminado (`_extraer_imagenes_pymupdf`, bloques comentados, imports no usados)
- [x] `src/services/pdf_converter.py` — TODO documentado para extracción futura de texto en imágenes `.png` dentro de PDFs nativos
- [x] `src/services/documents.py` — adaptado a la nueva firma del convertidor
- [ ] Extracción de imágenes como archivos separados — **postergado** (se mantiene la columna `images_path` en DB/schema por si se retoma)

## Objetivo 3: Limpieza de textos 🔧

- [x] `src/services/cleaning.py` — CleaningService.structuralCleaning()
  - [x] ftfy.fix_text() → reparación de encoding
  - [x] markdown_it.MarkdownIt("commonmark") → parseo MD → extracción texto plano
  - [x] regex → eliminación de URLs, emails, teléfonos
  - [x] eliminación de placeholders de imágenes (`<!-- Start/End of picture text -->`)
  - [x] eliminación conservadora de metadata de autoria (autores, facilitadores, revisores, directores, etc.)
  - [x] eliminación de direcciones postales, correos y teléfonos
  - [x] eliminación de notas legales, copyright y créditos de fotografía/diagramación
  - [x] eliminación de índices/tablas de contenido
  - [x] eliminación de tablas Markdown (agenda, anexos tabulados)
  - [x] eliminación de headers de anexos
  - [x] eliminación de prefijos de numeración de secciones y subsecciones
  - [x] eliminación de items/viñetas sueltos
  - [x] eliminación de números de página y líneas muy cortas
  - [x] deduplicación de párrafos consecutivos
  - [x] normalización whitespace (_MULTISPACE + _SPACES) **sin** `.lower()`
- [x] `linguisticCleaning()` — ~~regex~~ → **migrado a Anthropic Claude** (Jul 2026):
  - [x] Elimina referencias bibliográficas, citas entre paréntesis y notas al pie
  - [x] Preserva párrafos separados por `\n\n`
  - [x] Chunking por párrafos para textos largos
  - [x] Prompt específico alineado con el dominio territorial amazónico
  - [x] Métodos regex obsoletos eliminados (`_CITA_PARENTESIS`, `_REF_BIB_*`, `_NOTA_PIE`, `_HEADERS_REFERENCIAS`)
- [x] `models/documents.py` — columna cleaned_path
- [x] `models/storage.py` — método leer()
- [x] `services/documents.py` — DocumentService.limpiar() + limpiar_varios() + DocumentoNoConvertido
- [x] `api/routers/documents.py` — POST /documents/{id}/clean + /clean-batch
- [x] `config.py` — DATA_CLEANED = s3/archivosLimpiados (borrado DATA_TXT)
- [x] Probado: 200, 404, 409, 500 (archivo no encontrado)
- [x] `POST /documents/{id}/revert` — revierte al estado anterior (cleaned→converted, converted→raw)

### Refactor de limpieza — Jul 02 2026

- [x] Renombrado `_eliminar_lineas_repetidas` → `_eliminar_headers_footers_y_numeros`:
  - Solo elimina números de página y headers/footers cortos recurrentes.
  - Conserva lemas y frases identitarias repetidas para el futuro conteo de `NARRATIVA`.
- [x] `_es_direccion` separa direcciones postales de topónimos:
  - Nunca elimina ciudades/países aislados (Lima, Perú, Bogotá, Puerto Maldonado).
  - Solo elimina líneas que son predominantemente direcciones postales.
- [x] Nuevo `_es_titulo_estructural` para eliminar headers de sección explícitamente
  (`Introducción`, `Resumen`, `Conclusiones`, `Referencias`, etc.) sin confundir con contenido.
- [x] `_eliminar_citas_parentesis` refinado:
  - Elimina citas académicas `(Apellido, 2020)`.
  - Preserva decretos, leyes, resoluciones y rangos institucionales.
- [x] Nueva `_eliminar_seccion_referencias`:
  - Detecta el header `Referencias` / `Bibliografía` y elimina todo desde ese punto.
- [x] `_URL_PATTERN` mejorado para capturar dominios sin `www`.
- [x] `_PHONE_PATTERN` más conservador:
  - Evita borrar años, fechas, coordenadas y rangos de páginas.
- [x] `_SECCION_PREFIX` corregido:
  - Quita numeración romana de 2+ letras (`II.`, `III.`) pero preserva iniciales (`V.`, `A.`).
- [x] `_NOTA_PIE` corregido para no eliminar listas numeradas legítimas.
- [x] `_REF_BIB_AUTOR` ajustado para no confundir topónimos con autores
  (`Maldonado, Lima` vs `García, A.`).
- [x] Logging de trazabilidad agregado en cada paso de limpieza.
- [x] Verificación manual de que las 9 categorías semánticas se conservan.
- [x] Fix post-refactor: `_es_referencia_bibliografica` ya no usa rangos de años
  (`2001-2018`) como único criterio, evitando que párrafos con datos y
  estadísticas sean eliminados incorrectamente (caso documento
  `e33950f0-0e69-41a8-9f37-50ab93f2a0df`).
- [x] Fix post-refactor: `_eliminar_headers_footers_y_numeros` ahora también
  elimina footers largos en MAYÚSCULAS repetidos, típicos de presentaciones
  tipo PowerPoint convertidas a PDF (caso documento
  `9c6c4d34-34f2-4ecf-a229-71809682cef8`).

## Objetivo 4: Extracción de entidades 🔧

**Enfoque vigente:** Extracción mediante Anthropic Claude con el codebook inglés completo como especificación, diez códigos validados desde `src/categories.py` y salida estructurada mediante tool use.

### Etiquetas finales

| Etiqueta | Descripción |
|----------|-------------|
| CHAR | Actores individuales o colectivos con un rol contextual concreto |
| KNOW | Saberes técnicos, ecológicos o tradicionales |
| ATT | Valores, identidades, percepciones y compromisos |
| SKILL | Destrezas y competencias para realizar tareas |
| PRAC | Prácticas, actividades productivas, cadenas de valor |
| physical_INFRA | Soportes de acceso, movilidad, energía y conectividad tecnológica |
| soft_INFRA | Soportes organizados para producción, aprendizaje, monitoreo e información |
| eco_INFRA | Estructuras que sostienen funciones ecológicas |
| RUL | Reglas, normas e instrumentos institucionales concretos |
| LOC | Lugares geográficos, territorios, regiones, países, ciudades |

Los objetivos, visiones e intenciones no son entidades por sí mismos. Una entidad nominal autónoma contenida en ellos conserva la etiqueta que le corresponda.

### Implementado

- [x] `data/ner/annotations/a251048a.json` — anotaciones históricas retiradas del request; reservadas para trazabilidad
- [x] `data/codebooks/codebook_en_construccion_en.md` — especificación completa cargada directamente en el prompt; se retiró el archivo independiente de demostraciones
- [x] `src/models/entities.py` — ORM Entity (tabla `entities` recreada vía migración)
- [x] `src/services/llm_client.py` — cliente Anthropic compartido (reutilizado por cleaning.py y ner.py)
- [x] `src/services/ner.py` — servicio de extracción con:
  - Plantilla única `data/prompts/ner_prompt.md`: codebook + bloque objetivo
  - Codebook completo incorporado mediante `$codebook` en `data/prompts/ner_prompt.md`
  - Bloque objetivo incorporado mediante `$json_input`, sin demostraciones adicionales
  - Chunking de máximo 3 párrafos o 12K caracteres con offsets absolutos
  - Salida estructurada forzada con `submit_entity_annotations` y JSON Schema
  - Salida semántica: `{"document_id": "...", "annotations": [{label, text, sentence_id, ambiguity}]}`
  - Fallo explícito si Anthropic trunca la respuesta o no usa la herramienta requerida
  - Oraciones con `sentence_id` estable para localizar menciones aunque Claude responda fuera de orden
  - Repeticiones conservadas por aparición, incluso dentro de una misma oración
  - Cálculo backend de `start`/`end` absolutos buscando el span literal en el chunk
  - Campo `context` con el texto de la oración
  - Fusión de resultados de chunks conservando cada aparición por posición
  - Parseo de la entrada estructurada de la herramienta
- [x] `src/services/cleaning.py` — `linguisticCleaning()` migrado a Anthropic (ver Objetivo 3)
- [x] `src/api/schemas/entities.py` — EntityOut con text, category, start, end, context y ambiguity
- [x] `POST /documents/{id}/extract-entities` — endpoint que extrae entidades y guarda el resultado en JSON
- [x] `.env` — variable `ANTHROPIC_API_KEY` (completada por el usuario)
- [x] `requirements.txt` — dependencia `anthropic` (removido spacy/langdetect)
- [x] `src/services/documents.py` — `extraer_entidades_de_documento()` no modifica la tabla `entities`; esa persistencia queda para un endpoint posterior
- [x] `migrations/versions/b8e3f2a1c4d5_recreate_entities_table.py` — recrea tabla entities
- [x] `src/config.py` — `STORAGE_NER = s3/archivosNER`, `NER_PROMPT_PATH = data/prompts/ner_prompt.md`, `NER_CODEBOOK_PATH = data/codebooks/codebook_en_construccion_en.md`
- [x] `src/models/documents.py` — columna `ner_path`
- [x] `migrations/versions/5ea1bb7e236a_add_ner_path_to_documents.py` — migración para `ner_path`
- [x] `src/services/documents.py` — `extraer_entidades_de_documento()` guarda JSON en `s3/archivosNER/{id}.json`, devuelve el array de entidades y actualiza status a `ner`
- [x] `src/api/schemas/documents.py` — `DocumentRead` incluye `ner_path`
- [x] `src/services/documents.py` — `revertir()` soporta revertir desde status `ner` → `cleaned` → `raw`
- [x] `src/services/documents.py` — `eliminar()` borra todos los archivos generados (raw, converted, cleaned, NER)
- [x] `src/services/documents.py` — `extraer_entidades_de_varios()` para batch NER
- [x] `src/api/routers/documents.py` — `POST /documents/extract-entities-batch`
- [x] `POST /documents/{id}/fuzzy-matching` — normaliza, crea/reutiliza canónicos, persiste menciones y avanza a `fuzzyMatching`
- [x] `canonical_entities` — modelo, repositorio y migración inicial
- [x] `entities.canonical_id` — FK obligatoria hacia `canonical_entities`
- [x] Matching conservador por categoría — exact normalizado, fuzzy con umbral y margen, y protección para términos cortos
- [x] Persistencia transaccional — rollback completo ante errores y reemplazo idempotente de menciones por documento

### Rediseño de resolución canónica v2 — Ago 12 2026

- [x] Planificación por documento antes de comparar menciones aisladas
- [x] Singularización controlada de actores genéricos CHAR, en minúscula y conservando género/calificadores
- [x] Familias de nombres personales por prefijo compatible y ancla más completa
- [x] Protección contra nombres de pila ambiguos y sufijos corporativos (`SA`, `SAC`, `EIRL`, etc.)
- [x] Tabla `canonical_entity_aliases` para conservar formas observadas
- [x] Trazabilidad en `entities`: método, puntaje, versión y evidencia JSON
- [x] Migración `b3c4d5e6f7a8` aplicada y verificada
- [x] Auditoría reversible PostgreSQL + JSON + red antes/después
- [x] Simulación de `Relatos mineros.docx`: 1.111 menciones, DB sin cambios, 13 convergencias y 0 separaciones
- [x] 33 pruebas unitarias/integración local y health check de API
- [ ] Revisar cualitativamente los 48 nuevos canónicos propuestos y las 27 decisiones `person_alias`
- [ ] Reprocesar el documento real solo después de aprobar la auditoría

### Línea base histórica probada

- [x] La versión anterior extrajo 133 entidades en un documento de prueba.
- [x] Persistencia y respuesta HTTP funcionaron con el esquema anterior.
- [ ] Repetir el piloto con el esquema final de diez etiquetas y sin catálogos.

## Objetivos 5–8: Vectores, matrices, grafos, métricas 🔧

### Punto de control de validación Postman — 23 septiembre 2026

- El endpoint `GET /semantic-nodes/leiden-source?language=es&artifact_source=official` fue validado correctamente.
- Clustering validado: `5b0fbd7a7b89c9a00bd6876afce066016195135764ecf66e7f984ef6694ea7f6`.
- Grafo fuente validado: `704bf158c3138a42733a5c466d45055534626d79a5b7521776431955129ac0f7`.
- Se promovió correctamente `C001` a nodo semántico.
- UUID del nodo `C001`: `2e73cadf-6799-46f8-9ba2-ac0a1a5dd40c`.
- El endpoint `GET /semantic-nodes` confirmó `total: 1`.
- El siguiente endpoint en el checklist es el número 4: `GET /semantic-nodes/{node_id}`; su respuesta detallada fue revisada.
- El 24 Sep se verificaron dos credenciales obsoletas cargadas en Docker y se recreó el servicio `api` con la llave vigente.
- `POST /semantic-nodes/{node_id}/generate-description` quedó validado con `HTTP 200`; Anthropic generó y persistió el título y la descripción de `C001` con estado `draft`.
- La generación usa ahora un tool schema forzado en lugar de depender de JSON como texto libre; conserva el fallback de texto para compatibilidad y registra errores del proveedor sin exponer credenciales al cliente HTTP.
- El cliente compartido y Docker Compose admiten además `ANTHROPIC_WORKSPACE_ID` para llaves organizacionales que requieran seleccionar workspace.
- Siguiente paso: revisión humana del título y la descripción generados; después corregir mediante `PATCH /semantic-nodes/{node_id}` o aceptar el nodo con `status: accepted`.
- `POST /semantic-network/relationships/build` validado con 40 nodos registrados: 96 relaciones calculadas a partir de 836 aristas fuente; migración `f3c4d5e6f7a8` aplicada.
- `POST /semantic-network/export/graphml` exporta la meta-red persistida con atributos auditables y aislados a `s3/graphs/graphml/<scope>/semantic_network_<projection>.graphml`.
- Validación real del GraphML: 40 nodos, 96 relaciones, 20 aislados y descarga pública `HTTP 200`.

- [x] Primer experimento de coocurrencia por `(document_id, sentence_id)`
- [x] Nodos definidos por `canonical_id`; menciones repetidas en una oración cuentan una sola presencia
- [x] Matriz de incidencia oración–nodo y adyacencia sparse simétrica
- [x] Red plana única de CHAR, LOC, PRAC, INFRA y RUL; eliminadas capas/bloques L2
- [x] Exportaciones CSV/Matrix Market con observaciones auditables
- [x] Visualización de G₃ (`peso >= 3`) en PNG, HTML interactivo y GraphML
- [x] Matrices regeneradas después de aplicar resolución v2: 523 nodos y 1.216 aristas
- [x] Visualización G₁ completa: peso mínimo 1, 523 nodos, 1.216 aristas y 28 aislados
- [x] Visualizador: aislados preservados, etiquetas bajo demanda en HTML y top 25 en figuras estáticas
- [x] Contexto de cada arista compuesto desde sus menciones, compatible con contextos distintos dentro de una oración
- [x] Relaciones intra-categoría explícitas (incluidas CHAR–CHAR y LOC–LOC)
- [x] `POST /analysis/network` para corpus completo o incubadora
- [x] Body de red con `incubator_number` y `language`, ambos con valor concreto o `"all"`
- [x] Intersección AND de incubadora/idioma y artefactos separados por combinación
- [x] `GET /analysis/network/latest` para lectura sin recálculo
- [x] `POST /documents/{id}/network` para inspección puntual
- [x] Artefactos oficiales por formato y scope; publicación restringida a `/files/graphs`
- [x] Persistencia simplificada a GraphML, JSON de metadatos y CSV canónicos
- [x] Escritura atómica y bloqueo por destino para evitar resultados parciales/concurrentes
- [x] Validación real: 78 documentos, 41.148 menciones, red G₁ de 16.527 nodos y 45.866 aristas
- [x] Suite automatizada: 47 pruebas exitosas
- [x] Proyección versionada `prac-infra-rul-v2` centrada en PRAC, INFRA y RUL
- [x] Seis relaciones: PRAC–PRAC, PRAC–INFRA, PRAC–RUL, INFRA–INFRA, INFRA–RUL y RUL–RUL
- [x] Nueve vistas derivadas sin recalcular la coocurrencia maestra
- [x] Evidencia normalizada oración–entidad con CHAR/LOC contextuales preservados en PostgreSQL
- [x] Endpoint paginado de evidencia por arista consultado bajo demanda en PostgreSQL
- [x] Validación real: 9.518 nodos, 13.196 aristas, 10.310 oraciones y 14.657 observaciones
- [x] Suite automatizada ampliada: 57 pruebas exitosas
- [x] Contrato `construction` discriminado y retrocompatible en la proyección tipada
- [x] Método `document-recurrent-core-v1` por recurrencia documental de nodos
- [x] Pesos `sentence-count`, `document-count`, `fractional` y `fractional-document`
- [x] Auditoría calculada de nodos/aristas excluidos y soporte contextual independiente
- [x] Resúmenes all/main component × nueve vistas; GraphML canónico main-component/all
- [x] Suite automatizada ampliada: 63 pruebas exitosas
- [x] Ejecutar Leiden sobre el GraphML del backbone validado
- [x] Endpoint desacoplado de Leiden con semilla, resolución, pesos y caché
- [x] Exportación GraphML/CSV de comunidades compatible con Gephi

## Objetivo 9: Migración de almacenamiento de grafos a `s3/graphs/` ✅

**Fecha:** 03 Sep 2026

- [x] Nueva tabla `sentences` con `(document_id, sentence_id, text)`
- [x] `src/models/sentences.py` y `src/models/sentences_repo.py`
- [x] Persistir oraciones durante `POST /documents/{id}/fuzzy-matching` y eliminarlas al revertir
- [x] Endpoint de evidencia por arista consulta PostgreSQL en lugar de CSV
- [x] Migración Alembic `d7e8f9a0b1c2_add_sentences_table.py`
- [x] `src/analysis/graph_paths.py` con nombres oficiales estables y parámetros en JSON
- [x] `src/analysis/graph_export.py` para exportación mínima GraphML + CSV + JSON
- [x] `src/analysis/backbone.py` con `export_backbone_to_files`
- [x] `src/analysis/leiden.py` acepta `base_name` y exporta `_communities.csv` y `_members.csv`
- [x] `src/services/network.py` reescrito para `s3/graphs/`, escritura atómica y rutas relativas
- [x] `src/config.py` con `STORAGE_GRAPHS` y alias legado `STORAGE_NETWORK`
- [x] `src/api/main.py` monta `/files/graphs` y conserva `/files/networks` como legado
- [x] `src/api/schemas/network.py` conserva campos adicionales de metadatos
- [x] Suite ampliada a 81 pruebas: 79 pasan y 2 se omiten sin dependencias Leiden

## Objetivo 10: Nodos semánticos para la meta-red 🔧

Antecedente implementado: la aceptación de nodos y las conexiones por agregación
de esta lista corresponden al enfoque anterior. Los pendientes vigentes se
mantienen en «Tres metaredes — 20 Nov 2026» al inicio de este archivo.

- [x] Prompt experto para título y descripción internos: `data/prompts/semantic_node_prompt.md`
- [x] Modelo y migración para nodos, miembros, procedencia y soporte por incubadora
- [x] Consulta de partición Leiden y hash del GraphML exacto
- [x] Promoción explícita e idempotente de una comunidad a nodo semántico
- [x] Consulta, listado, edición y generación LLM de título y descripción
- [x] Aplicar las migraciones y validar los endpoints contra PostgreSQL y Claude en Docker
- [x] Limitar la meta-red a meta-nodes aceptados y registrados; las comunidades no promovidas quedan fuera
- [x] Definir e implementar conexiones intercluster deterministas: basta una arista fuente positiva entre miembros de dos meta-nodes distintos; el peso es la suma de los pesos fuente
- [x] Definición matemática `data/prompts/meta_network_relationships_math.md`
- [x] Instantánea de aristas fuente y agregación SQL de relaciones intercluster
- [x] `POST /semantic-network/relationships/build` y consulta de relaciones
- [x] Exportación GraphML de la meta-red
