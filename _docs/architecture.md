# Architecture — Weekly Team Feedback Tool

Companion to [plan.md](plan.md). Describes *how* the MVP is built. No code yet.

Adaptado del stack de referencia usado por [`retroloop`](https://github.com/alexeygrigorev/retroloop),
la implementación de este mismo producto que construyó el curso `ai-dev-tools-zoomcamp`
tras especificar y groomear el backlog.

## Stack

| Concern | Choice | Version |
|---|---|---|
| Language | Python | 3.14 |
| Framework | Django | 6.0 |
| Database | PostgreSQL | 18 |
| DB driver | psycopg | 3.3 |
| App server | gunicorn | 26.0 |
| Templates / interactivity | Django templates + HTMX + Alpine.js | 2.0 / 3.15 |
| Retro board | React island, Vite build, one Django template | 19.2 / 8.1 |
| Styling | Tailwind (CSS-first config, no JS config file) | 4.3 |
| Auth | `django.contrib.auth` — username + password, no email | — |
| Invites | Shareable project join link (rotatable token) | — |
| Background jobs | `django.tasks` + `django-tasks-db` (ORM backend) | 0.12 |
| File storage | None — recordings are deleted after transcription | — |
| Media processing | ffmpeg | 8.1 |
| Transcription | OpenAI transcription API (speaker diarization) | SDK 2.45 |
| Text model (clustering + extraction) | OpenAI, structured outputs (JSON schema) | SDK 2.45 |
| Sessions / cache | Database-backed sessions, local-memory cache | — |
| Tests / lint | pytest, pytest-django, ruff | 9.1 / 4.12 / 0.15 |
| Deploy | Docker Compose — `web`, `worker`, `db` | — |

**Postgres es la única dependencia de infraestructura.** Sin Redis, sin object
store, sin servidor de correo, sin auth de terceros. Un solo SDK `openai` y una
`OPENAI_API_KEY` cubren transcripción y extracción.

Por qué estas decisiones:

- **Django 6.0 trae un framework de Tasks** (`django.tasks`), así que el worker
  en background es una feature del framework, no algo que construimos a mano.
  Core solo incluye backends dummy e inmediato, así que producción necesita el
  paquete separado `django-tasks-db` para la cola respaldada por Postgres.
  Ver [El worker](#el-worker).
- **La transcripción con diarización da etiquetas de hablante.** Saber quién
  dijo qué es lo que hace confiable la extracción del *owner* de cada action
  item — sin eso el modelo adivina la propiedad por contexto de la frase. Es
  la mayor ganancia de precisión disponible en el pipeline.
- **El límite de tamaño de la API de transcripción sigue siendo la restricción
  real** del manejo de media. Bajar el audio a 16 kHz mono Opus con ffmpeg
  mantiene ~3 horas de habla por debajo del límite; grabaciones más largas se
  dividen en chunks.

## Apps de Django

```
config/          settings, urls
accounts/        vistas de signup / login (envoltorio delgado sobre contrib.auth)
projects/        Project, Membership, join links, funciones de permisos
cycles/          FeedbackCycle, Card, CycleParticipation
retro/           Retrospective, Cluster, Vote, Note, Decision, ActionItem
meetings/        MeetingRecord, Transcript, el comando del worker
ai/              servicios de transcripción + clustering + extracción (sin modelos)
board/           el island de React: vista, endpoint de estado, endpoints de mutación
```

`ai/` no tiene modelos ni vistas — expone funciones que reciben objetos de
dominio y devuelven dicts planos. Eso mantiene cada llamada a OpenAI mockeable
en tests y intercambiable por proveedor.

## Modelo de datos

### Identidad y membresía

```
User            django.contrib.auth.models.User — username, display name, password
Project         name, owner -> User, join_token (uuid), created_at
Membership      project, user, role {MEMBER, FACILITATOR}, joined_at
                unique(project, user)
```

**Auth deliberadamente mínima: usuario y contraseña, sin correo en ningún
lado.** `django.contrib.auth.urls` da login/logout; signup es una vista de
formulario. Sin allauth, sin flujo de reset de contraseña, sin verificación,
sin servidor de correo configurado.

**Las invitaciones son un link, no un mensaje.** Cada proyecto lleva un
`join_token`; el facilitador comparte `/join/<token>/`, y cualquier usuario
logueado que lo abra se vuelve `MEMBER`. El token es rotable desde la
configuración del proyecto, lo que revoca todos los links viejos de golpe.

El rol de facilitador es **por ciclo**, no solo por proyecto — el plan permite
asignarlo a otro miembro del equipo. Así que `FeedbackCycle.facilitator -> User`
lleva la autoridad de esa semana; `Membership.role` es el valor por defecto
usado al crear un ciclo.

### Recolección de feedback

```
FeedbackCycle   project, week_start, opens_at, closes_at, facilitator -> User
                status {COLLECTING, CLOSED}
Card            cycle, category {START, STOP, CONTINUE}, text
                author -> User (NULLABLE), is_anonymous, created_at, position
CycleParticipation  cycle, user, card_count, submitted_at
                    unique(cycle, user)
```

### Retrospectiva

```
Retrospective   cycle (1:1), stage, started_at, completed_at, version (int)
                votes_per_member (default 3)
Cluster         retrospective, name, position, is_auto_generated
                status {PENDING, DISCUSSED, SKIPPED, DEFERRED}
Card.cluster    FK -> Cluster, nullable   # tarjetas sin agrupar permitidas
Vote            retrospective, cluster, user, weight (1..3)
                unique(retrospective, cluster, user)
Note            retrospective, cluster (nullable), author, text, created_at
Decision        retrospective, cluster (nullable), text
                source {MANUAL, EXTRACTED}, status {DRAFT, CONFIRMED}
ActionItem      retrospective, cluster (nullable), description
                owner -> User (nullable), due_date (nullable)
                status {OPEN, DONE}, source, review_status {DRAFT, CONFIRMED}
```

`Retrospective.version` es un contador monotónico incrementado dentro de cada
transacción que muta el tablero. Es todo el mecanismo de sincronización del
board (ver abajo).

### Registro de la reunión

```
MeetingRecord   retrospective, uploaded_by, kind {AUDIO, VIDEO, TRANSCRIPT_FILE, PASTED_TEXT}
                temp_path (nullable), original_filename, size_bytes
                status {UPLOADED, TRANSCRIBING, EXTRACTING, READY, FAILED}
                attempts, error_message, created_at, media_deleted_at
Transcript      meeting_record (1:1), text, language, duration_seconds
```

`temp_path` apunta a un archivo temporal en disco y se anula en cuanto la
transcripción tiene éxito. `Transcript.text` en Postgres es el único registro
durable de la reunión.

## El diseño del anonimato — leer antes de la primera migración

El plan promete que los autores anónimos **nunca** se revelan, a nadie. Pero
los contribuyentes deben poder editar sus propias tarjetas antes de la retro,
lo cual requiere saber quién las escribió. Estos dos requisitos no chocan en
principio, chocan en el tiempo — así que se resuelven en el tiempo.

**`Card.author` es nullable, y al revelar se destruye para las tarjetas
anónimas:**

```sql
UPDATE cycles_card SET author_id = NULL
WHERE cycle_id = %s AND is_anonymous = true;
```

Esto corre dentro de la misma transacción que avanza la retrospectiva a
`REVEAL`. Antes de ese momento, `author` existe para que el dueño pueda
editar, y la capa de queries solo devuelve a cada miembro sus propias
tarjetas. Después de ese momento el vínculo no existe en ningún lado — ni
para el facilitador, ni para un admin de la base de datos, ni en un backup de
mañana.

Dos consecuencias a manejar deliberadamente:

- **Las métricas de participación sobreviven vía `CycleParticipation`.**
  Registra *que* un miembro envió feedback y *cuántas* tarjetas, nunca cuáles.
- **El orden filtra identidad.** Revelar tarjetas en orden de `created_at`
  permite correlacionar una tarjeta anónima con quien estaba escribiendo en
  ese momento. Al revelar, asignar `Card.position` en orden mezclado
  (aleatorio) y ordenar por eso en todas partes después.

Esta es la decisión más cara de corregir en todo el sistema si se hace mal —
significaría una migración de datos sobre la tabla más sensible, con datos ya
recolectados bajo una promesa rota. Confirmado por el plan: "el sistema no
revela autores anónimos ni al facilitador ni al equipo".

## Permisos

Toda la autorización vive en `projects/permissions.py` como funciones
predicado planas (`can_reveal(user, retro)`, `can_edit_card(user, card)`, …),
llamadas desde las vistas.

| Acción | Regla |
|---|---|
| Ver la tarjeta de otro miembro | Nunca antes de `REVEAL`; todos después |
| Editar / borrar tarjeta propia | Solo mientras el stage es `COLLECTING` |
| Ver totales de votación | Solo cuando el stage pasó `VOTE`, o `votes_revealed` |
| Avanzar stage, revelar, cerrar votación | Solo el facilitador del ciclo |
| Subir grabación, confirmar extracciones | Solo el facilitador del ciclo |
| Actualizar un action item | Su owner, o el facilitador |

Los totales de votación se **omiten del payload de la API** durante la etapa
de voto — no se ocultan en el cliente. Lo mismo para las tarjetas de otros
miembros antes de revelar. Si llega al navegador, ya se filtró.

## Máquina de estados (stage machine)

```
DRAFT -> REVEAL -> CLUSTER -> VOTE -> DISCUSS -> COMPLETE
```

Solo hacia adelante, dirigida por el facilitador, validada en el servidor en
una única función de servicio `advance_stage()`. Cada transición tiene efectos
secundarios que deben ser transaccionales junto con la escritura del stage:

- `-> REVEAL`: anular autoría anónima, mezclar posiciones, encolar el job de
  auto-clustering.
- `-> VOTE`: congelar la membresía de clusters (mover tarjetas se rechaza
  después).
- `-> DISCUSS`: calcular la agenda priorizada, mostrar los totales de voto.
- `-> COMPLETE`: bloquear el tablero; el resumen se vuelve la superficie de
  lectura.

## Sincronización del tablero — polling sobre un contador de versión

El tablero es la única pantalla con editores concurrentes:

1. Django renderiza `board.html` con el estado inicial serializado en la
   página.
2. Un bundle de React (Vite, ~un árbol de componentes) se monta y toma el
   control.
3. Cada 1.5s hace GET a `/retros/<id>/state?v=<version_conocida>`. Si
   `Retrospective.version` no cambió, la respuesta es mínima; si cambió,
   vuelve el estado completo del tablero y reemplaza el estado del cliente.
4. Cada mutación (`mover tarjeta`, `fusionar clusters`, `renombrar`,
   `emitir voto`, `marcar discutido`) hace POST a su propio endpoint, que
   muta e incrementa `version` en una transacción, y devuelve el nuevo estado
   completo.

Reemplazo de estado completo en vez de diffs, last-write-wins en movimientos
de tarjetas. Para un tablero de 5–8 personas y unas pocas docenas de tarjetas,
el payload es de pocos KB. Sin WebSockets, sin Redis pub/sub, sin CRDT.

Toda otra pantalla (página de proyecto, formulario de feedback, estado de
subida, resumen) es Django templates planos con HTMX para actualizaciones
parciales. Nada de React fuera del board.

## Pipeline de media

**La grabación es transitoria.** Nunca se guarda de forma permanente — cae en
un directorio temporal, se transcribe, y se borra. Solo `Transcript.text`
sobrevive, en Postgres. No hay bucket, no hay `MEDIA_ROOT` que respaldar, y no
hay política de retención que escribir, porque a los pocos minutos no queda
nada que retener.

```
navegador --POST multipart--> Django (streams a /scratch/<uuid>)
                                |
                                +--> MeetingRecord(UPLOADED, temp_path=...)
                                          |
                                encolado vía django.tasks -> worker
                                          |
   +--------------------------------------+
   |  1. ¿video? -> ffmpeg: extraer solo audio
   |  2. ffmpeg: bajar a 16 kHz mono Opus
   |  3. ¿supera el límite? -> dividir en chunks por silencios
   |  4. transcripción con diarización por chunk        [TRANSCRIBING]
   |     -> concatenar -> Transcript (con etiquetas de hablante)
   |     (texto pegado / archivo de transcript se saltan 1-4)
   |  5. BORRAR el archivo temporal, anular temp_path    <-- siempre, incluso en error
   |  6. extracción sobre el transcript                  [EXTRACTING]
   |  7. escribir filas Decision/ActionItem como DRAFT    [READY]
   +--------------------------------------+
```

El paso 5 va en un bloque `finally`. Una transcripción fallida no debe dejar
una grabación abandonada en disco.

## El worker

Sin Celery, sin Redis, sin broker — y, desde Django 6.0, nada hecho a mano
tampoco. Django ahora trae un framework de Tasks, así que un job en background
es una función decorada:

```python
@task
def process_meeting_record(record_id): ...

process_meeting_record.enqueue(record_id=record.pk)
```

Core de Django solo incluye backends dummy e inmediato, ambos para
desarrollo, así que producción configura el backend respaldado por ORM de
`django-tasks-db` en el setting `TASKS`. Los tasks viven en Postgres; el
servicio `worker` de Compose corre el comando worker del paquete. Escalar es
`docker compose up --scale worker=3`, y el row-claiming del backend evita que
dos workers tomen el mismo job.

## Las dos llamadas a OpenAI

Ambas viven en `ai/`, ambas usan structured outputs (JSON schema), ambas
producen **sugerencias que nunca son autoritativas** — coincide con la
decisión del plan de que "las acciones y decisiones generadas por IA siguen
siendo borrador hasta que el facilitador las confirma".

**Clustering** (al revelar): entran todas las tarjetas con
`{id, category, text}`, sale una lista de `{name, card_ids}`. Se escriben como
filas `Cluster` con `is_auto_generated=True`. El equipo edita libremente desde
ahí — la bandera es solo para mostrar ("sugerido"), nunca para permisos.

**Extracción** (después de transcribir): entran el transcript diarizado + la
agenda priorizada + el roster del proyecto; salen decisiones, action items con
nombre de owner, fechas límite, y un resumen. Las etiquetas de hablante hacen
la mayor parte del trabajo aquí. Los nombres de owner se resuelven a filas
`User` por fuzzy match contra el roster; un owner sin match queda `null` en
vez de adivinar — el facilitador elige de un dropdown.

Todo llega como `DRAFT`. El paso de confirmación es una sola pantalla del
facilitador con aceptar/editar/rechazar por ítem. Nada se publica hasta que
actúa.

## Deployment

`docker compose up`, tres servicios:

| Servicio | Comando | Notas |
|---|---|---|
| `db` | postgres:18 | volumen nombrado para los datos |
| `web` | gunicorn | monta el volumen `scratch`; ffmpeg en la imagen |
| `worker` | comando worker de `django-tasks-db` | misma imagen, mismo mount `scratch` |

El volumen scratch se comparte entre `web` y `worker` y no guarda nada de
valor — se puede borrar entre deploys. `db` guarda todo lo que importa, así
que es lo único a respaldar.

Config por variables de entorno: `DATABASE_URL`, `OPENAI_API_KEY`,
`SECRET_KEY`, `ALLOWED_HOSTS`, `DEBUG`. Sin settings de correo, sin
credenciales de storage.

## Preguntas abiertas

La mayoría de las ambigüedades típicas de este diseño ya las resuelve
`plan.md` directamente (edición de tarjetas solo antes de la retro,
irreversibilidad del anonimato, action items como query en vivo por
proyecto). Quedan genuinamente abiertas:

1. **¿Los votos son reasignables mientras dura la etapa de voto?** Asumido:
   sí, libremente, hasta que cierra la votación — ya que los totales están
   ocultos y cambiarlos no filtra nada. Confirmar.
2. **¿Qué cierra un ciclo cuando alguien no envió feedback?** Asumido: el
   facilitador puede cerrar y revelar igual, con los que no enviaron visibles
   como tal. Confirmar.
3. **Una transcripción fallida, ¿implica volver a subir el archivo?** Dado que
   la grabación se borra tras el intento, no hay nada contra qué reintentar.
   Confirmar que ese es el trade-off aceptado, frente a guardar el media 24h
   para permitir reintentos.
