-- Solo lectura. Ejecutar en pgAdmin contra AWS semantic_db.
-- Selecciona la ejecución más reciente que admite entidades de un documento.
WITH ejecucion AS (
  SELECT id FROM public.metanetwork_runs
  WHERE productive_sector = 'Agroforestry'
    AND configuration->'backbone'->>'minimum_node_document_count' = '1'
  ORDER BY created_at DESC, id DESC LIMIT 1
)
SELECT n.network_id AS red, n.community_id AS cluster, n.id AS uuid,
       n.member_count AS entidades, n.document_count AS documentos,
       n.canonical_name AS nombre, n.description AS descripcion, n.vector
FROM public.metanetwork_nodes n
WHERE n.run_id = (SELECT id FROM ejecucion)
ORDER BY n.network_id, n.community_id;

-- Integrantes de un cluster: cambiar network1 y C001 para explorar otro.
WITH ejecucion AS (
  SELECT id FROM public.metanetwork_runs
  WHERE productive_sector = 'Agroforestry'
    AND configuration->'backbone'->>'minimum_node_document_count' = '1'
  ORDER BY created_at DESC, id DESC LIMIT 1
)
SELECT n.network_id AS red, n.community_id AS cluster,
       m.category AS categoria, m.canonical_name AS entidad,
       m.canonical_id AS uuid_entidad
FROM public.metanetwork_nodes n
JOIN public.metanetwork_node_members m ON m.node_id = n.id
WHERE n.run_id = (SELECT id FROM ejecucion)
  AND n.network_id = 'network1' AND n.community_id = 'C001'
ORDER BY m.category, m.canonical_name, m.canonical_id;
