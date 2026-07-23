# Plan de migración: PostgreSQL + Docker (Fase 1)

> Estado: **propuesta / planificación**. No se ha ejecutado ningún cambio en la app.
> Alcance acordado: **solo Fase 1** (Postgres + Docker Compose), **manteniendo Flet funcionando igual**,
> **portando el esquema real 1:1** (14 tablas, snake_case) y usando **Docker solo para desarrollo local**
> (el deploy en Render se decide después). FastAPI y Next.js quedan para Fases 2 y 3.

Este plan corrige y aterriza el documento arquitectónico original ("CLIMB REMAKE") contra el
código que existe hoy, para que la migración **no rompa** ninguna funcionalidad.

---

## 0. Diferencias frente al documento original (y por qué)

| Documento original | Ajuste en este plan | Motivo |
|---|---|---|
| `init.sql` con 10 tablas y rediseño (tabla `Agentes`, `idAgente` en todo) | Portar las **14 tablas reales** tal cual | El `init.sql` del doc **omite** `Camino_Elegido`, `Voice_Profile`, `Logros_Personales`, `Mirror_Patrones`, `Password_Resets`. Aplicarlo mata Mirror, Archive, Clarity/voice, elección de camino y recuperación de contraseña. |
| Columnas en `idUsuario` (camelCase) | Mantener `id_usuario` (snake_case) | Postgres baja identificadores sin comillas a minúsculas; `fila["id_usuario"]` (usado en 123 sitios) se rompería. |
| Tabla `Agentes` + `orquestar_interaccion_agente()` | **Diferido a Fase 2** | Es un refactor mayor del Core (6 agentes con firmas y salidas distintas, citación por índice, directiva de idioma). No es parte de una migración segura de persistencia. |
| Backend = uvicorn/FastAPI montando Flet | **Fase 1 = Flet solo** (como hoy) | FastAPI es Fase 2. Para Fase 1 el backend sigue siendo la app Flet web, solo que apunta a Postgres. |
| `CMD ["uvicorn", "main.py", ...]` | `CMD ["python", "main.py"]` con `PORT=8550` | `main.py` ya arranca Flet web en `$PORT`. El `uvicorn main.py` del doc es sintácticamente incorrecto además. |
| `docker-compose` sin secretos | Pasar `ANTHROPIC_API_KEY` y `SMTP_*` vía `env_file` | Sin esas variables los agentes y el correo no funcionan. |
| `JSONB` para los campos JSON | Mantener `TEXT` + `json.dumps/loads` | Cambiar a JSONB obliga a tocar lectura/escritura en todo el data layer. Se puede optimizar a JSONB en una fase posterior. |

---

## 1. Objetivo de la Fase 1

- Reemplazar SQLite por **PostgreSQL 16** para tener **persistencia real** (hoy en Render el disco de SQLite es efímero) y **paridad de entorno** entre Fedora/macOS/Windows con Docker Compose.
- **Cero cambios de comportamiento** para el usuario: mismas vistas, mismos agentes, mismo flujo.
- Todo el trabajo se concentra en **dos archivos** (`data/clsConexionDB.py` y `data/clsInteraccionDB.py`) más los archivos de infraestructura nuevos. Las vistas y el Core no cambian (salvo un puñado de lecturas de columnas camelCase; ver §4.3).

---

## 2. Estructura de repositorio propuesta (Fase 1, mínima)

No hace falta el monorepo `backend/ frontend/` todavía. Se añade lo mínimo:

```
Climb/
├── docker-compose.yml        # NUEVO — orquesta db + backend
├── Dockerfile                # NUEVO — imagen del backend (Flet + psycopg2)
├── requirements.txt          # + psycopg2-binary
├── .env                      # + DATABASE_URL (además de ANTHROPIC/SMTP ya existentes)
├── database/
│   └── init.sql              # NUEVO — esquema Postgres (§3)
├── main.py, clsRouter.py, componentes.py, tema.py
├── core/   data/   views/
```

Cuando llegue la Fase 3 (Next.js), se mueve la app a `backend/` y se agrega `frontend/`.

---

## 3. `database/init.sql` (esquema real portado a PostgreSQL)

14 tablas, snake_case, tipos Postgres. Las columnas camelCase del SQLite actual se normalizan a
snake_case (marcadas con `-- (renombrada)`); ver §4.3 para los ajustes de código que esto implica.

```sql
-- Esquema Climb en PostgreSQL 16. Se ejecuta una vez al crear el contenedor de la BD
-- (montado en /docker-entrypoint-initdb.d/). Portado 1:1 desde el SQLite actual.

-- 1. Usuarios
CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario      SERIAL PRIMARY KEY,
    nombre          TEXT NOT NULL,
    discriminador   TEXT,                    -- legado (login va por username/correo)
    username        TEXT,
    correo          TEXT,
    password_hash   TEXT,
    password_salt   TEXT,
    idioma          TEXT DEFAULT 'en',
    fecha_registro  TIMESTAMPTZ DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_username ON Usuarios (username);
CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_correo   ON Usuarios (correo);

-- 2. Usuario_Perfil (9 respuestas del onboarding)
CREATE TABLE IF NOT EXISTS Usuario_Perfil (
    id_perfil                    SERIAL PRIMARY KEY,
    id_usuario                   INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    apertura_emocional           TEXT,
    contexto_profesional         TEXT,
    logro_principal              TEXT,
    reaccion_presion_visibilidad TEXT,
    intentos_previos             TEXT,
    vision_futuro                TEXT,
    desahogo_libre               TEXT,
    fecha_creacion               TIMESTAMPTZ DEFAULT now()
);

-- 3. Chats
CREATE TABLE IF NOT EXISTS Chats (
    id_chat        SERIAL PRIMARY KEY,
    id_usuario     INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    tipo_agente    TEXT CHECK (tipo_agente IN ('coach_mirror','coach_archive','coach_editor','coach_pacer','clarity_session')),
    fecha_creacion TIMESTAMPTZ DEFAULT now()
);

-- 4. Mensajes_Chat
CREATE TABLE IF NOT EXISTS Mensajes_Chat (
    id_mensaje  SERIAL PRIMARY KEY,
    id_chat     INTEGER NOT NULL REFERENCES Chats(id_chat) ON DELETE CASCADE,
    rol         TEXT CHECK (rol IN ('user','assistant')),
    contenido   TEXT NOT NULL,
    fecha_envio TIMESTAMPTZ DEFAULT now()
);

-- 5. Hallazgos_Perfil
CREATE TABLE IF NOT EXISTS Hallazgos_Perfil (
    id_hallazgo    SERIAL PRIMARY KEY,
    id_usuario     INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    origen         TEXT CHECK (origen IN ('Coach','Mentor','Onboarding')),
    tipo           TEXT CHECK (tipo IN ('Fortaleza','Area_Oportunidad','Bloqueo_Emocional','Meta_Visibilidad')),
    descripcion    TEXT NOT NULL,
    fecha_registro TIMESTAMPTZ DEFAULT now()
);

-- 6. Historico_Resumenes
CREATE TABLE IF NOT EXISTS Historico_Resumenes (
    id_resumen          SERIAL PRIMARY KEY,
    id_usuario          INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    contenido_json      TEXT NOT NULL,
    fecha_actualizacion TIMESTAMPTZ DEFAULT now()
);

-- 7. Camino_Elegido
CREATE TABLE IF NOT EXISTS Camino_Elegido (
    id_camino_elegido         SERIAL PRIMARY KEY,
    id_usuario                INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    nombre_camino             TEXT NOT NULL,
    descripcion_camino        TEXT NOT NULL,
    tradeoff_principal        TEXT,
    riesgo_principal          TEXT,
    tiempo_estimado_semanal   TEXT,
    patron_que_rompe          TEXT,
    caminos_alternativos_json TEXT,
    fecha_eleccion            TIMESTAMPTZ DEFAULT now()
);

-- 8. Textos_Usuario
CREATE TABLE IF NOT EXISTS Textos_Usuario (
    id_texto   SERIAL PRIMARY KEY,          -- (renombrada) idTexto -> id_texto
    id_usuario INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    fuente     TEXT,                        -- 'onboarding' | 'editor' | 'clarity' | 'archive' | 'mirror'
    texto      TEXT NOT NULL,
    fecha      TIMESTAMPTZ DEFAULT now()
);

-- 9. Voice_Profile (1:1 con usuario)
CREATE TABLE IF NOT EXISTS Voice_Profile (
    id_usuario      INTEGER PRIMARY KEY REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    contenido_json  TEXT,
    n_muestras      INTEGER DEFAULT 0,
    ultimo_texto_id INTEGER DEFAULT 0,
    fecha           TIMESTAMPTZ DEFAULT now()
);

-- 10. Logros_Personales (Archive)
CREATE TABLE IF NOT EXISTS Logros_Personales (
    id_registro          SERIAL PRIMARY KEY,   -- (renombrada) idRegistro
    id_usuario           INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE, -- (renombrada) usuarioLogro
    tipo_logro           TEXT,                 -- (renombrada) tipoLogro
    logro                TEXT NOT NULL,
    descripcion_logro    TEXT,                 -- (renombrada) descripcionLogro
    mi_rol               TEXT,
    aprendizaje          TEXT,
    tags_json            TEXT,
    metrics_json         TEXT,
    conversacion_json    TEXT,
    fecha_registro_logro TIMESTAMPTZ DEFAULT now()  -- (renombrada) fechaRegistroLogro
);

-- 11. Mirror_Patrones
CREATE TABLE IF NOT EXISTS Mirror_Patrones (
    id_patron     SERIAL PRIMARY KEY,         -- (renombrada) idPatron
    id_usuario    INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    quote         TEXT NOT NULL,
    source        TEXT,                        -- 'scout' | 'user'
    status        TEXT,                        -- 'pending' | 'observing'
    scout_ref     TEXT,
    reframe_json  TEXT,
    turns_json    TEXT,
    detected_at   TIMESTAMPTZ DEFAULT now(),
    last_observed TIMESTAMPTZ
);

-- 12. Misiones
CREATE TABLE IF NOT EXISTS Misiones (
    id_mision        SERIAL PRIMARY KEY,
    id_usuario       INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    contenido_json   TEXT NOT NULL,
    progreso_json    TEXT,
    estado           TEXT DEFAULT 'activa',
    fecha_creacion   TIMESTAMPTZ DEFAULT now(),
    fecha_completada TIMESTAMPTZ
);

-- 13. Editor_Borradores
CREATE TABLE IF NOT EXISTS Editor_Borradores (
    id_borrador   SERIAL PRIMARY KEY,          -- (renombrada) idBorrador
    id_usuario    INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    formato       TEXT,
    es_correo     INTEGER DEFAULT 0,
    asunto        TEXT,
    borrador      TEXT,
    estado        TEXT DEFAULT 'activo',
    contexto_json TEXT,
    turns_json    TEXT,
    creado        TIMESTAMPTZ DEFAULT now(),
    actualizado   TIMESTAMPTZ DEFAULT now()
);

-- 14. Password_Resets
CREATE TABLE IF NOT EXISTS Password_Resets (
    id_reset       SERIAL PRIMARY KEY,
    id_usuario     INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    code_hash      TEXT NOT NULL,
    expira         TIMESTAMPTZ NOT NULL,
    usado          INTEGER DEFAULT 0,
    fecha_creacion TIMESTAMPTZ NOT NULL
);

-- Índices de rendimiento
CREATE INDEX IF NOT EXISTS idx_chats_usuario     ON Chats (id_usuario);
CREATE INDEX IF NOT EXISTS idx_hallazgos_usuario ON Hallazgos_Perfil (id_usuario);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat     ON Mensajes_Chat (id_chat);
CREATE INDEX IF NOT EXISTS idx_misiones_usuario  ON Misiones (id_usuario);
```

> Nota sobre nombres de tabla: Postgres también baja `Usuarios`, `Usuario_Perfil`, etc. a minúsculas,
> pero como el código **nunca** los pone entre comillas, el `FROM Usuarios` funciona igual (se resuelve a `usuarios`).

---

## 4. Cambios en el data layer

Toda la lógica SQL vive en `data/`. El resto de la app (vistas, Core) accede por funciones, así que
**no cambia** (excepto §4.3).

### 4.1 `data/clsConexionDB.py` — conexión psycopg2 + shim de compatibilidad

El truco para no reescribir 41 llamadas `conexion.execute(...)` ni 135 placeholders es un **shim**
que imita la API de `sqlite3.Connection` que usa el código:

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor


def obtener_conexion():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL no está definida")
    return _ConexionCompat(psycopg2.connect(url, cursor_factory=RealDictCursor))


def inicializar_db():
    # El esquema lo crea el contenedor de Postgres vía database/init.sql.
    print("[INFO] Esquema gestionado por PostgreSQL (database/init.sql).")


def _traducir(sql):
    # psycopg2 usa %s en vez de ? para los placeholders.
    return sql.replace("?", "%s")


class _ConexionCompat:
    """Imita sqlite3.Connection para el data layer: .execute() traduce '?'->'%s',
    devuelve un cursor RealDictCursor (fila['columna'] sigue funcionando), y
    expone .cursor(), .commit(), .close()."""

    def __init__(self, conn):
        self._c = conn

    def execute(self, sql, params=()):
        cur = self._c.cursor()
        cur.execute(_traducir(sql), params)
        return cur

    def cursor(self):
        return _CursorCompat(self._c.cursor())

    def commit(self):
        self._c.commit()

    def close(self):
        self._c.close()


class _CursorCompat:
    """Cursor que traduce '?'->'%s' en execute(). (lastrowid no existe en
    psycopg2: ver §4.2, se usa RETURNING.)"""

    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=()):
        self._cur.execute(_traducir(sql), params)
        return self

    def __getattr__(self, name):
        return getattr(self._cur, name)
```

Con esto, las **41** `conexion.execute(...)`, las **135** `?` y los `conexion.cursor()`/`fetchone()`/`fetchall()`
siguen funcionando sin tocarse.

### 4.2 Puntos que SÍ hay que tocar en `data/clsInteraccionDB.py`

| Punto | Nº aprox. | Cambio |
|---|---|---|
| `cursor.lastrowid` | 8 | Postgres no lo soporta → añadir `RETURNING <id>` al INSERT y leer `cur.fetchone()["<id>"]`. |
| `except sqlite3.IntegrityError` (en `crear_usuario`) | 1 | Cambiar a `except psycopg2.errors.UniqueViolation` (o `psycopg2.IntegrityError`). |
| Literales `%` en SQL (p. ej. `LIKE '%x%'` en la búsqueda de Archive) | auditar | psycopg2 interpreta `%` para params → duplicar a `%%` en el SQL literal. |
| Fechas | pocos | Postgres devuelve `datetime` (tz-aware), no strings. Ajustar `_parse_fecha`, `_hace`, `_parse_utc` para aceptar `datetime`; en `crear_codigo_reset` pasar objetos `datetime` (psycopg2 los adapta) en vez de `.isoformat()`. |
| `import sqlite3` | 1 | Sustituir por `import psycopg2` (para el tipo de excepción). |

Ejemplo del patrón `RETURNING` (para los 8 `lastrowid`):

```python
# Antes (SQLite):
cursor.execute("INSERT INTO Usuarios (...) VALUES (?, ?)", (a, b))
id_usuario = cursor.lastrowid
# Después (Postgres):
cursor.execute("INSERT INTO Usuarios (...) VALUES (?, ?) RETURNING id_usuario", (a, b))
id_usuario = cursor.fetchone()["id_usuario"]
```

### 4.3 Normalización camelCase → snake_case

El SQLite actual tiene columnas camelCase en 4 tablas. Al pasarlas a snake_case en `init.sql` hay que
actualizar, en `data/clsInteraccionDB.py` (y `core/clsMirror.py`), tanto las **listas de columnas en los
SQL** como las **lecturas `fila["..."]`**:

- `Logros_Personales`: `idRegistro→id_registro`, `usuarioLogro→id_usuario`, `tipoLogro→tipo_logro`, `descripcionLogro→descripcion_logro`, `fechaRegistroLogro→fecha_registro_logro`
- `Textos_Usuario`: `idTexto→id_texto`
- `Mirror_Patrones`: `idPatron→id_patron`
- `Editor_Borradores`: `idBorrador→id_borrador`

Es un conjunto acotado (~8 lecturas de dict + los SELECT/INSERT de esas tablas). Los grep de referencia:
`grep -rn "idRegistro\|usuarioLogro\|tipoLogro\|descripcionLogro\|fechaRegistroLogro\|idTexto\|idPatron\|idBorrador" core/ data/`.

> Alternativa de menor esfuerzo (no recomendada por legibilidad): dejar esas columnas en minúsculas sin
> guion (`idtexto`, `idregistro`, …). Como los identificadores en SQL se auto-minusculan, los `SELECT`/`INSERT`
> **no** cambiarían; solo habría que ajustar las lecturas `fila["idTexto"] → fila["idtexto"]`. Menos ediciones,
> pero nombres feos y divergentes del resto del código.

---

## 5. Infraestructura Docker

### `Dockerfile` (raíz)

```dockerfile
FROM python:3.11-slim

# libpq-dev + build-essential para compilar/enlazar psycopg2.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8550
CMD ["python", "main.py"]   # main.py arranca Flet web en $PORT (WEB_BROWSER)
```

> Se omiten `libmpv-dev`/`mpv` del doc original: son para el modo escritorio de Flet, no para el modo web.
> Si `psycopg2-binary` da problemas, con `libpq-dev` instalado se puede usar `psycopg2` a secas.

### `docker-compose.yml` (raíz)

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: climb_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: climb_dev
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-climb_dev_password}
      POSTGRES_DB: climb_development
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U climb_dev -d climb_development"]
      interval: 5s
      timeout: 3s
      retries: 10

  backend:
    build: .
    container_name: climb_backend
    restart: unless-stopped
    ports:
      - "8550:8550"           # Flet web
    volumes:
      - .:/app                # hot-reload del código en dev
    environment:
      PORT: "8550"
      DATABASE_URL: postgresql://climb_dev:${POSTGRES_PASSWORD:-climb_dev_password}@db:5432/climb_development
    env_file:
      - .env                  # ANTHROPIC_API_KEY, SMTP_USER, SMTP_APP_PASSWORD, SMTP_FROM
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
```

Puntos clave frente al doc original:
- **`env_file: .env`** para que el backend reciba la API key de Anthropic y las credenciales SMTP.
- **`healthcheck` + `depends_on: service_healthy`**: el backend espera a que Postgres esté listo.
- La contraseña sale de `${POSTGRES_PASSWORD}` (definible en `.env`), no hardcodeada.
- `init.sql` montado en `docker-entrypoint-initdb.d/` (se ejecuta **solo** al crear el volumen por primera vez).

### `requirements.txt`

Añadir: `psycopg2-binary`. (Mantener `flet`, `anthropic`, `python-dotenv`.)

### `.env`

Añadir para desarrollo local **fuera** de Docker (dentro de Docker lo inyecta compose):

```
DATABASE_URL=postgresql://climb_dev:climb_dev_password@localhost:5432/climb_development
```

---

## 6. Plan de ejecución (checklist)

1. Crear `database/init.sql` (§3), `Dockerfile` y `docker-compose.yml` (§5). Añadir `psycopg2-binary` a `requirements.txt`.
2. Reescribir `data/clsConexionDB.py` con el conector psycopg2 + shim (§4.1).
3. Ajustar `data/clsInteraccionDB.py`: los 8 `RETURNING`, la excepción de unicidad, los literales `%`, las fechas y la normalización camelCase (§4.2, §4.3). Revisar `core/clsMirror.py` por los `idPatron`.
4. `docker compose up --build`. Verificar que `db` queda *healthy* y que el backend levanta.
5. **Smoke test completo** contra Postgres (§7).
6. `docker compose down && docker compose up` → verificar que **los datos persisten** (volumen `postgres_data`).

## 7. Pruebas (smoke test funcional)

Recorrer cada feature contra Postgres:
- Registro (con idioma), login por correo y por username, **recuperación de contraseña por código**.
- Onboarding de 9 preguntas → diagnóstico de Scout → 3 caminos → elegir camino.
- Pacer: generar misión, completar acciones, cerrar y sugerir siguiente.
- Mirror: sesión (incluida "dejar para después" y retomar), boundary, reframe.
- Archive: chat → ficha → timeline (búsqueda con `%`).
- Editor: borrador nuevo, regenerar, completar, "editado hace…".
- Clarity: espejo → conversación (citas por índice) → puertas.
- Cambio de idioma persistido; salida de IA en el idioma correcto.

## 8. Riesgos y notas

- **Fechas**: es el punto más delicado del port (string ISO → `datetime` tz-aware). Concentrado en `Password_Resets` y en los helpers de fecha; probar expiración/rate-limit del reset explícitamente.
- **`%` en SQL**: auditar la búsqueda de Archive (`LIKE`) antes de correr.
- **Local sin Docker**: `main.py` llama a `obtener_conexion()` que ahora exige `DATABASE_URL`. Para dev en escritorio hay que levantar al menos el contenedor `db` (`docker compose up db`) y apuntar `DATABASE_URL` a `localhost`. (Opcional: mantener un fallback a SQLite si `DATABASE_URL` no está, para no depender de Docker en local — cuesta mantener dos dialectos, no recomendado.)
- **Datos existentes**: como el disco de Render es efímero, no hay datos de producción que migrar. Si en algún punto los hubiera, se haría un export/import puntual SQLite→Postgres.
- **Deploy en Render**: fuera de alcance de Fase 1. Cuando se aborde, se usa un Postgres gestionado + un servicio Docker (el `docker-compose` es para dev local).

## 9. Fuera de alcance (Fases 2 y 3)

- **Fase 2 (API + tabla `Agentes`)**: endpoints FastAPI que resuelven el Core; Flet pasa a consumir HTTP; mover identidad/prompts de los agentes a la BD (`orquestar_interaccion_agente`). Refactor grande y separado.
- **Fase 3 (Frontend)**: Next.js contra los endpoints validados; apagar progresivamente las vistas Flet.
- **Optimizaciones**: pasar los campos JSON a `JSONB`, pool de conexiones, migraciones versionadas (Alembic).
```
