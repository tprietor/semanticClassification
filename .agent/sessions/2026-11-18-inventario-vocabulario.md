# Inventario auditable del vocabulario — 18 Nov 2026

## Alcance y decisiones

La usuaria pidió preparar un inventario como paso previo al vocabulario controlado
y al ajuste de `fuzzy-matching`, tras compartir un texto de Jessica Talisman sobre
preparación de datos y clustering de OpenRefine.

Se tomó Agroforestry como alcance inicial, con todos los estados y las diez
categorías, conservando también los nombres excluidos del dashboard. Se consultó
AWS en `REPEATABLE READ`, `READ ONLY`; las operaciones de archivos fueron lecturas.
La exportación no ejecutó extracción, resolución, fusiones ni escrituras remotas.

## Evidencia y entrega

- Captura y manifiesto: `export/vocabulary_inventory_2026-11-18/snapshot_aws.json.gz`
  y `snapshot_manifest.json`.
- Scripts de captura, análisis, workbook y validación en esa misma carpeta.
- Excel, TSV, metodología, diccionario y paquete ZIP:
  `outputs/vocabulary_inventory_2026_11_18/`.
- Las propuestas del 3 Nov se conservaron como fuente histórica independiente;
  se recalcularon sus divisiones contra las asignaciones vigentes.
- Se separaron cadenas literales distintas de pares categoría + texto para
  aclarar el denominador usado en la auditoría anterior.
- Los casos reciben IDs reproducibles y un TSV relaciona cada caso con todas
  sus menciones. Las columnas de decisión del workbook se entregaron pendientes.

## Validación

Se conciliaron datos fuente y tablas derivadas, firmas de NER y PostgreSQL,
referencias, categorías, contextos y offsets. Los 32 controles coincidieron.
Se verificaron fórmulas del resumen, la reacción del contador de pendientes
al modificar una decisión y la conservación del estado Investigar como abierto.
Se renderizaron y revisaron las siete hojas. El XLSX guardado conserva tablas,
filtros, validación de decisiones y paneles inmovilizados, sin errores cacheados.
Se comprobaron vínculos de evidencia y hashes del paquete ZIP.

La validación es de integridad y trazabilidad. La cobertura y la interpretación
semántica de las extracciones requieren revisión humana. No se crearon acuerdos
de sinonimia ni definiciones, y no se alteró el endpoint.

Las métricas actuales y los siguientes pasos se mantienen únicamente en
`context/PROJECT_CONTEXT.md` y `context/tasks.md`.

## Ajuste del flujo de edición

La usuaria encontró difícil decidir qué hoja editar y señaló que TFFF no aparecía
en los casos de Revisar. Se generó un archivo de edición de una sola hoja con
todas las formas observadas, en lugar de limitar las decisiones a los casos
automáticos. El inventario original no tenía cambios de la usuaria según sus
hashes y se preservó íntegro.

Se precargaron las dos decisiones explícitas de la conversación y se pusieron
sus filas al comienzo de la hoja para facilitar su identificación. Se verificó
que están todos los IDs originales, que la hoja única conserva sus filtros,
paneles y validación de acción, y que el archivo no contiene errores cacheados.
La revisión visual confirmó que TFFF figura como nombre deseado en ambas formas
y que los cuatro términos observados de Google están marcados para exclusión.

Las decisiones vigentes y el archivo que debe editarse se mantienen en el contexto
principal. La captura de origen y los datos de producción permanecen intactos.
