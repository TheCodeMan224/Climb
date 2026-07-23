-- Esquema Climb en PostgreSQL 16. Se ejecuta una vez al crear el contenedor de la BD
-- (montado en /docker-entrypoint-initdb.d/). Portado 1:1 desde el SQLite actual,
-- normalizando identificadores a snake_case.

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

-- 8. Textos_Usuario  (idTexto -> id_texto)
CREATE TABLE IF NOT EXISTS Textos_Usuario (
    id_texto   SERIAL PRIMARY KEY,
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

-- 10. Logros_Personales (Archive)  (camelCase -> snake_case)
CREATE TABLE IF NOT EXISTS Logros_Personales (
    id_registro          SERIAL PRIMARY KEY,
    id_usuario           INTEGER NOT NULL REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    tipo_logro           TEXT,
    logro                TEXT NOT NULL,
    descripcion_logro    TEXT,
    mi_rol               TEXT,
    aprendizaje          TEXT,
    tags_json            TEXT,
    metrics_json         TEXT,
    conversacion_json    TEXT,
    fecha_registro_logro TIMESTAMPTZ DEFAULT now()
);

-- 11. Mirror_Patrones  (idPatron -> id_patron)
CREATE TABLE IF NOT EXISTS Mirror_Patrones (
    id_patron     SERIAL PRIMARY KEY,
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

-- 13. Editor_Borradores  (idBorrador -> id_borrador)
CREATE TABLE IF NOT EXISTS Editor_Borradores (
    id_borrador   SERIAL PRIMARY KEY,
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

-- 15. Agentes (catálogo de configuración dinámica; se siembra desde el código)
CREATE TABLE IF NOT EXISTS Agentes (
    id_agente          SERIAL PRIMARY KEY,
    nombre_agente      VARCHAR(50) UNIQUE NOT NULL,  -- 'scout','pacer','mirror','archive','editor','clarity'
    descripcion_agente TEXT,
    rol_agente         TEXT,   -- identidad / system prompt base
    instruccion_agente TEXT,   -- reglas operacionales base (prompt principal)
    fecha_creacion     TIMESTAMPTZ DEFAULT now()
);

-- Índices de rendimiento
CREATE INDEX IF NOT EXISTS idx_chats_usuario     ON Chats (id_usuario);
CREATE INDEX IF NOT EXISTS idx_hallazgos_usuario ON Hallazgos_Perfil (id_usuario);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat     ON Mensajes_Chat (id_chat);
CREATE INDEX IF NOT EXISTS idx_misiones_usuario  ON Misiones (id_usuario);
