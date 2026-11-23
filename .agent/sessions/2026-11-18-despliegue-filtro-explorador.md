# Despliegue del filtro del explorador — 18 Nov 2026

## Decisiones y ejecución

- La usuaria autorizó el commit, push y despliegue y ejecutó los comandos de
  publicación y operación de AWS desde su Terminal.
- Commit publicado y desplegado: `e56c4b872b34cf5289e748342b1540fce915177f`.
- GitHub Actions quedó bloqueado antes de iniciar pasos por un problema de
  facturación de la cuenta. La usuaria reintentó sin éxito. Se documentó la
  alternativa de soporte al no aparecer importes facturables en sus capturas.
- La suite local completa pasó: 196 pruebas y 591 subpruebas. La comprobación
  específica del explorador pasó: 53 pruebas y 578 subpruebas.
- El servidor seguía en `f900018` con 14 archivos modificados o sin seguimiento.
  La comparación encontró 13 idénticos al nuevo commit y una única línea vacía
  adicional al final de `data/prompts/translation_prompt.md`.
- La usuaria ejecutó `export/deploy_e56c4b8/deploy.py`. El script tomó el lock
  del despliegue automático, respaldó fuentes e imagen y guardó las ediciones
  en Git stash antes de ejecutar el script de despliegue publicado.
- Alembic ya estaba en `f0a1b2c3d4e5`. La actualización no tenía migraciones
  pendientes y no ejecutó procesamiento de documentos.

## Evidencia y recuperación

- Comparación local: `export/deploy_e56c4b8/20261118T142224Z/comparison.json`.
- Registro completo: archivos `deployment-*.log` de `export/deploy_e56c4b8/`.
- Carpeta remota: `/home/ubuntu/semanticClassification/export/manual-e56c4b8-20261118T142712Z/`.
  Contiene `source-before.tar.gz`, `server-before.patch`, `deployment.json`,
  `network-verification.json` y `compare-verification.json`.
- Imagen anterior: `semanticclassification-api:before-e56c4b8-20261118t142712z`.
- Stash de respaldo: `97bd3e02fdd2811b205bb16d4f1c8019be1ae22d`.

## Resultado observado

El registro termina en `VERIFIED_DEPLOY_OK` con el SHA publicado. La API pasó
el health check y las comprobaciones del filtro en `/network` y `/compare`.
Se reportaron como excluidos `agroforestry` PRAC (664 menciones) y
`MADRE DE DIOS` LOC (411 menciones). La red predeterminada sin recorte top-n
devolvió 462 nodos y 3.515 aristas, sin esos nombres ni aristas incidentes a
sus IDs. El envío de `excluded_entity_names: []` se comprobó en un alcance vacío.

El marcador y el historial del temporizador registraron el despliegue manual
exitoso. La comprobación visual del dashboard y el desbloqueo de GitHub Actions
siguen abiertos en `context/tasks.md`.
