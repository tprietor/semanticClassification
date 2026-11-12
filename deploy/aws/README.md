# Despliegue en AWS (us-east-2)

Guía de despliegue y operación. El dashboard (`semantic-network-explorer`) está
publicado en Vercel y consume la API de AWS por HTTPS.

## Estado actual (2026-11-06)

La API, el gateway y PostgreSQL están dentro de Docker **en el EC2**. La base no
está en RDS. `s3/` es una carpeta del disco del EC2, no un bucket de Amazon S3.
Las instrucciones de creación de RDS más abajo son una opción histórica, no la
arquitectura actualmente desplegada.

```
Vercel ──HTTPS──▶ EC2 :443 Caddy ──▶ API ──▶ PostgreSQL en el EC2
Mac ──túnel SSH──▶ EC2 ├── PostgreSQL: pgAdmin en 127.0.0.1:15432
                       └── API completa: Postman en 127.0.0.1:18000
```

Para trabajar con la API y la base de AWS desde la Mac no hace falta Docker local.
Abre `deploy/aws/bin/db-tunnel` en una terminal y déjala abierta. pgAdmin tiene
dos registros separados: «AWS semantic_db (solo lectura)» (`sc_readonly`) y
«AWS semantic_db (escritura)» (`sc_user`). El registro local «semantic_db» sigue
apuntando a Docker Desktop; comprueba siempre el nombre antes de editar.

**Fuente vigente:** Tania confirmó que el último despliegue de AWS es la versión
válida. `DATA_PRIMARY=aws` bloquea `resync-from-mac.sh` para evitar sobrescribirla
con la base local. La copia local y `Docker.raw` permanecen intactos.

**Actualización de API — 2026-11-11:** se desplegó el pipeline `english`
autorizado, validado con ocho pruebas en la imagen de producción. El POST
`/documents/{document_id}/translate` prepara el archivo en `s3/english/` y
avanza a `english`; el GET `/documents/{document_id}/english` lo descarga.
Para documentos con idioma registrado `en`, el POST copia directamente el
`cleaned` sin modificar sus bytes: no llama a Anthropic ni requiere una clave
de API. El comportamiento se corrigió por indicación explícita de la usuaria
después de un fallo inicial de saldo durante una verificación innecesaria.
`70767dc6` ya está en `english`, con `language=en` y su `english_path`
registrado; el POST y la descarga respondieron HTTP 200 y ambas versiones
comparten SHA-256. La migración `f0a1b2c3d4e5` ya estaba aplicada.
Evidencia final y respaldos:
`export/english_passthrough_2026-11-11/deployment_result.json` y
`endpoint_result.json` de la Mac. La corrección solo actualizó
`src/services/documents.py` sobre los siete archivos del despliegue inicial;
se conservaron las otras ediciones locales del servidor.

> **Si eres un agente de IA**, sigue [`AGENT-RUNBOOK.md`](AGENT-RUNBOOK.md): define el
> orden, las confirmaciones obligatorias y las comprobaciones de cada paso.

- **Público**: solo los endpoints de lectura del explorador, a través del gateway.
- **Solo por túnel SSH**: la API completa (subir, procesar, borrar) y PostgreSQL.
- **Nunca público**: la base de datos.

No hay autenticación todavía. Cualquiera que tenga la URL del gateway puede leer los
resultados del explorador, pero no modificarlos.

## Datos del project

| Dato | Valor |
|---|---|
| Experiencia | Nueva experiencia de AWS (*project*, inicio de sesión social) |
| Región | **us-east-2 (Ohio)**. Obligatoria: el project no puede crear recursos en otras regiones |
| Plan | FREE, USD 100 de créditos, vence el 2027-04-26 (consultado el 2026-10-26) |
| Tipos de EC2 permitidos | t3/t4g/t8i micro y small, `c7i-flex.large` (4 GB), `m7i-flex.large` (8 GB) |
| Clases de RDS permitidas | `db.t3.micro`, `db.t4g.micro` |

Comprueba el estado del plan con:

```bash
aws freetier get-account-plan-state --profile <perfil> --region us-east-2
```

## Costo (on-demand, us-east-2, precios del 2026-10-26)

| Recurso | Tipo | USD/hora | USD/mes 24/7 |
|---|---|---|---|
| EC2 | `m7i-flex.large` (2 vCPU, 8 GB) | 0,0958 | 69,9 |
| RDS | `db.t4g.micro` | 0,0160 | 11,7 |
| Discos | EBS 30 GB gp3 + RDS 20 GB | — | ~5 |
| IP pública | Elastic IP | 0,005 | ~3,6 |
| **Total** | | | **~90** |

Con todo encendido las 24 horas, **los USD 100 de créditos alcanzan para un mes**.
Formas de estirarlos:

- **Apagar el EC2 cuando no se use.** Encendido 10 h en días hábiles cuesta ~USD 21 al
  mes de cómputo. Mientras está detenido solo se pagan los discos y la IP.
- **PostgreSQL dentro del EC2** en lugar de RDS ahorra ~USD 14 al mes, pero se pierden
  los backups automáticos (perfil `local-db` en `docker-compose.prod.yml`).
- `c7i-flex.large` (4 GB) cuesta ~USD 8 menos al mes, con menos margen para docling.

Antes de que se acaben los créditos o venza el plan, hay que pasar al plan pago en
AWS Settings para no perder los recursos.

---

> Los pasos 1–7 siguientes documentan el plan inicial con RDS y acceso directo al
> puerto 8000. **No son instrucciones para operar el despliegue actual.** Para el
> trabajo diario usa «Estado actual», el túnel y «Respaldos y migraciones».

## Paso 1 — Preparar el project (una sola vez)

En la nueva experiencia, la administración se hace en **AWS Settings**
(<https://settings.aws.com>), no en IAM:

1. **Región**: confirma que sea `us-east-2` en *AWS Settings → View all projects →
   Overview → Additional info → Region*.
2. **Límite de gasto**: si el project pasa al plan pago, configura un *spend limit* en
   *AWS Settings → Billing*. Al superarlo, el project se pausa.
3. **Alerta de gastos**: *Billing and Cost Management → Budgets → Create budget* →
   *Monthly cost budget*, por ejemplo USD 50, con aviso por correo.
4. **Colaboradores**: se invitan como *team members* por correo desde AWS Settings.
   No se crean usuarios IAM.
5. En la consola (<https://console.aws.amazon.com>), selecciona arriba a la derecha la
   región **US East (Ohio) us-east-2**.

## Paso 2 — Crear el servidor EC2

**EC2 → Instances → Launch instances**

| Campo | Valor |
|---|---|
| Name | `semantic-api` |
| AMI | Ubuntu Server 24.04 LTS (x86_64) |
| Instance type | `m7i-flex.large` |
| Key pair | *Create new key pair* → `semantic-ec2`, tipo RSA, `.pem`. Guárdala en `~/.ssh/` y ejecuta `chmod 400 ~/.ssh/semantic-ec2.pem` |
| Storage | 30 GiB gp3 |

En *Network settings* → *Edit*, crea el security group `semantic-ec2-sg` con estas
reglas de entrada:

| Tipo | Puerto | Origen | Para qué |
|---|---|---|---|
| SSH | 22 | My IP | Administrar el servidor |
| Custom TCP | 8000 | My IP | API completa para Tania |
| HTTP | 80 | Anywhere (0.0.0.0/0) | Certificado HTTPS (Let's Encrypt) |
| HTTPS | 443 | Anywhere (0.0.0.0/0) | Explorador para Vercel |

*Launch instance*.

**IP fija**: *EC2 → Elastic IPs → Allocate Elastic IP address* → *Actions → Associate*
con la instancia `semantic-api`. Anota la IP, por ejemplo `3.141.20.7`.

El dominio del gateway se forma con esa IP: `3-141-20-7.sslip.io`. Es un servicio
gratuito que resuelve a la IP y permite obtener el certificado HTTPS sin comprar un
dominio. Más adelante se puede cambiar por un dominio propio.

> Si la IP de Tania cambia (pasa en conexiones domésticas), actualiza las reglas
> 22 y 8000 del security group con *My IP*.

## Paso 3 — Crear la base RDS

**RDS → Databases → Create database**

| Campo | Valor |
|---|---|
| Creation method | Standard create |
| Engine | PostgreSQL, versión 16.x |
| Templates | Free tier (o Dev/Test) |
| Deployment | Single-AZ |
| DB instance identifier | `semantic-db` |
| Master username | `sc_admin` |
| Credentials | *Self managed*, con una contraseña larga (guárdala en un gestor) |
| Instance class | `db.t4g.micro` |
| Storage | gp3, 20 GiB, sin autoscaling |
| Connectivity | **Connect to an EC2 compute resource** → `semantic-api` |
| Public access | **No** |
| Additional configuration → Initial database name | `semantic_db` |
| Backup | Automated backups, retención de 7 días |
| Encryption | Activada (viene por defecto) |

Al elegir *Connect to an EC2 compute resource*, AWS crea los security groups para
que solo el EC2 pueda conectarse a la base. Cuando el estado sea *Available*, copia el
**Endpoint** (*Connectivity & security*).

pgvector ya viene disponible en RDS. La restauración crea la extensión automáticamente.

## Paso 4 — Preparar el servidor

Desde la Mac de Tania:

```bash
ssh -i ~/.ssh/semantic-ec2.pem ubuntu@3.141.20.7
```

En el EC2:

```bash
curl -fsSL https://raw.githubusercontent.com/tprieto23/semanticClassification/feat/explorador-entidades/deploy/aws/setup-ec2.sh | bash
exit   # vuelve a entrar para usar docker sin sudo
```

El script instala Docker, crea 4 GB de swap, clona la rama y crea
`~/semanticClassification/.env`. Complétalo con `nano ~/semanticClassification/.env`:

```bash
DATABASE_URL=postgresql://sc_admin:<password>@<endpoint-rds>:5432/semantic_db?sslmode=require
ANTHROPIC_API_KEY=<la clave actual>
GATEWAY_HOST=3-141-20-7.sslip.io
API_WORKERS=2
```

Si la contraseña tiene caracteres como `@`, `:` o `/`, codifícalos en la URL
(por ejemplo, `@` → `%40`).

## Paso 5 — Migrar los datos desde la Mac

En la Mac, desde la raíz de `semanticClassification` y con `docker compose up -d`
corriendo:

```bash
bash deploy/aws/export-from-mac.sh
scp -i ~/.ssh/semantic-ec2.pem export/semantic_db.dump export/s3.tar.gz \
    ubuntu@3.141.20.7:~/semanticClassification/
```

El script muestra cuántos documentos hay por estado y sector, para comparar después.

En el EC2:

```bash
cd ~/semanticClassification
bash deploy/aws/import-on-ec2.sh semantic_db.dump s3.tar.gz
```

El script se niega a restaurar si la base de destino ya tiene tablas, para no pisar
datos por error. Al terminar muestra los mismos conteos: deben coincidir con los de la
Mac.

La Mac conserva su copia: la migración no borra nada en el origen. El archivo
`export/` contiene datos de investigación; no lo subas a Git y bórralo cuando la
migración esté verificada.

## Paso 6 — Levantar los servicios

```bash
cd ~/semanticClassification
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec api alembic upgrade head   # no hace nada si ya está al día
```

La primera construcción tarda entre 10 y 15 minutos (torch y docling). Para verificar:

```bash
curl https://3-141-20-7.sslip.io/health                       # {"status":"ok"}, público
curl https://3-141-20-7.sslip.io/analysis/explorer/v1/meta    # explorador, público
curl https://3-141-20-7.sslip.io/documents                    # 404: no expuesto
curl http://3.141.20.7:8000/docs                              # API completa, solo desde la IP de Tania
```

En Postman, Tania cambia la URL base de `http://localhost:8000` a
`http://3.141.20.7:8000`.

## Paso 7 — Publicar el dashboard en Vercel

1. En Vercel (cuenta de Tania): *Add New → Project* → importar
   `tprieto23/semantic-network-explorer`.
2. Framework: **Vite** (lo detecta solo por `vercel.json`).
3. *Environment Variables*: `VITE_API_BASE_URL` = `https://3-141-20-7.sslip.io`
4. *Deploy*.

`VITE_API_BASE_URL` se fija al construir. Si cambia el gateway, actualiza la variable y
vuelve a desplegar.

## Resincronizar el servidor con la Mac (solo antes del corte de datos)

Mientras la Mac sea la base principal, el servidor es una copia. **Este comando
reemplaza la base de AWS** y solo funciona si `DATA_PRIMARY=mac` figura expresamente
en `deploy/aws/.state.env`. Durante la transición y cuando AWS sea la fuente
principal, queda bloqueado. Desde la raíz del repo:

```bash
bash deploy/aws/resync-from-mac.sh
```

El script pide confirmación, exporta la base y `s3/`, los sube, detiene la API,
reemplaza la base del servidor, actualiza `s3/`, vuelve a levantar la API y compara los
conteos de documentos y entidades. Si no coinciden, termina con error y muestra las
diferencias. El dashboard queda sin datos un par de minutos mientras corre.

`s3/` se actualiza agregando y sobrescribiendo archivos; los que se borren en la Mac no
se borran en el servidor.

## Probar la base y la API de AWS desde la Mac sin Docker local

El túnel SSH deja PostgreSQL accesible solo en la propia Mac y también permite usar
la API completa desde Postman. No hace falta encender Docker Desktop para estas dos
conexiones:

```bash
# Desde la raíz del repositorio.
deploy/aws/bin/db-tunnel
```

Deja esa terminal abierta mientras trabajas. El script comprueba la IP pública de la
Mac y, si cambió, permite SSH solo desde esa IP `/32` en el Security Group existente.
Si AWS CLI indica que la sesión venció, ejecuta `aws login --profile tania-semantic`
y vuelve a abrir el túnel.
`Ctrl+C` cierra ambas conexiones. Si se reinicia el contenedor de PostgreSQL, vuelve
a ejecutar el script para que descubra su nueva IP interna.

| Herramienta | Dirección local | Acceso |
|---|---|---|
| pgAdmin, servidor «AWS semantic_db (solo lectura)» | `127.0.0.1:15432`, base `semantic_db` | Usuario `sc_readonly`; su contraseña local está en `~/.ssh/semantic-db-readonly-password` |
| Postman, URL base de la API | `http://127.0.0.1:18000` | API de producción en EC2 |

El servidor anterior «semantic_db» de pgAdmin apunta al PostgreSQL local y solo
responde con Docker Desktop encendido. Para editar AWS, selecciona expresamente
«AWS semantic_db (escritura)». Su contraseña se solicita al conectar y no se guardó
en pgAdmin. En Postman, selecciona el entorno **«AWS por túnel»**, cuyo `apiUrl` es
`http://127.0.0.1:18000`; `GET Health` respondió `200 OK` el 6 de noviembre. Los
endpoints escriben tanto en la base como en el `s3/` del EC2.

### Respaldos y migraciones

El EC2 ejecuta `~/semantic-backup-db.sh` cada día a las **03:17 UTC**. Hace un
`pg_dump` en formato personalizado, lo lee por completo con `pg_restore` para
verificarlo y conserva siete días en `~/semantic-db-backups/`. El primer respaldo
quedó verificado el 6 de noviembre. Para traer el último a la Mac:

```bash
deploy/aws/bin/pull-db-backup
```

El respaldo de la base no incluye los documentos de `s3/`; esa carpeta aún requiere
una copia fuera del EC2 para proteger documentos nuevos. La copia local contiene los
archivos existentes en AWS: la comparación por contenido del 6 de noviembre encontró
1.386 archivos idénticos entre la Mac y AWS. Para traer los
archivos nuevos o modificados de AWS sin borrar los locales:

```bash
deploy/aws/bin/pull-s3-backup
```

Si reemplaza un archivo local, guarda la versión anterior bajo
`export/s3-previous/`. Ejecuta `pull-db-backup` y `pull-s3-backup` después de procesar
documentos o modificar la base. Para hacer ambos y crear un respaldo nuevo de la base
en un solo paso, ejecuta `deploy/aws/bin/backup-now`. La tarea diaria en EC2 respalda
solo PostgreSQL. Una copia automática de `s3/` fuera del EC2 sigue pendiente. Tampoco existe
restauración automática de RDS, porque se está usando PostgreSQL dentro del EC2.

Las migraciones se aplican **en el contenedor API del EC2**, sin Docker local:

```bash
deploy/aws/bin/ec2-ssh 'cd ~/semanticClassification && docker compose -f docker-compose.prod.yml --profile local-db exec -T api alembic current'
deploy/aws/bin/pull-db-backup
deploy/aws/bin/ec2-ssh 'cd ~/semanticClassification && docker compose -f docker-compose.prod.yml --profile local-db exec -T api alembic upgrade head'
```

Primero despliega el código que contiene la migración; `alembic upgrade head` solo
puede aplicar versiones presentes en la imagen del API. El despliegue automático ya
ejecuta ese comando después de actualizar la imagen.

## Operación diaria

| Tarea | Comando o acción |
|---|---|
| Actualizar a la última versión de la rama | Automático con cada push, si está configurado [`CI-CD.md`](CI-CD.md). A mano, en el EC2: `bash deploy/aws/deploy-on-ec2.sh $(git rev-parse origin/feat/explorador-entidades)` |
| Ver logs | `deploy/aws/bin/ec2-ssh 'cd ~/semanticClassification && docker compose -f docker-compose.prod.yml logs --tail 100 api'` |
| Reiniciar API | `deploy/aws/bin/ec2-ssh 'cd ~/semanticClassification && docker compose -f docker-compose.prod.yml restart api'` |
| Aplicar migraciones | Ejecutar los tres comandos de «Respaldos y migraciones» |
| Apagar el servidor | `aws ec2 stop-instances --instance-ids <id> --profile <perfil> --region us-east-2` |
| Encenderlo | `aws ec2 start-instances --instance-ids <id> --profile <perfil> --region us-east-2` |
| Consultar créditos | `aws freetier get-account-plan-state --profile <perfil> --region us-east-2` |

Los servicios se levantan solos al encender el EC2 (`restart: unless-stopped`). La IP
elástica no cambia al apagar y encender.

La carpeta `s3/` vive en el disco del EC2. Antes de usar el servidor como única fuente
de documentos, hay que programar snapshots del volumen o copiarla a un bucket S3.

## Pendientes conocidos

- Autenticación de la API (planificada).
- Restringir el CORS de la API al dominio de Vercel.
- Dominio propio en lugar de `sslip.io`.
- Pasar al plan pago antes de que se agoten los créditos.
