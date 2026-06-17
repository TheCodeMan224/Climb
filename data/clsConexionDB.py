"""Conexion y creacion de esquema SQLite para Climb."""

import os
import sqlite3

# Ruta absoluta a climb.db, junto a este archivo de proyecto (raiz Climb/).
_RUTA_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "climb.db")


def obtener_conexion():
    """Devuelve una conexion a climb.db con foreign keys activadas."""
    conexion = sqlite3.connect(_RUTA_DB)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def _asegurar_columna(cursor, tabla, columna, definicion):
    """Agrega una columna a una tabla existente si aun no existe (migracion ligera)."""
    columnas = [fila["name"] for fila in cursor.execute(f"PRAGMA table_info({tabla})").fetchall()]
    if columna not in columnas:
        cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")


def inicializar_db():
    """Crea las 7 tablas con CREATE TABLE IF NOT EXISTS si no existen."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Usuario_Perfil (
            id_perfil INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            apertura_emocional TEXT,
            contexto_profesional TEXT,
            logro_principal TEXT,
            reaccion_presion_visibilidad TEXT,
            intentos_previos TEXT,
            vision_futuro TEXT,
            desahogo_libre TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Chats (
            id_chat INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            tipo_agente TEXT CHECK (tipo_agente IN (
                'coach_mirror', 'coach_archive', 'coach_editor', 'coach_pacer', 'clarity_session'
            )),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Mensajes_Chat (
            id_mensaje INTEGER PRIMARY KEY AUTOINCREMENT,
            id_chat INTEGER NOT NULL,
            rol TEXT CHECK (rol IN ('user', 'assistant')),
            contenido TEXT NOT NULL,
            fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_chat) REFERENCES Chats(id_chat) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Hallazgos_Perfil (
            id_hallazgo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            origen TEXT CHECK (origen IN ('Coach', 'Mentor', 'Onboarding')),
            tipo TEXT CHECK (tipo IN (
                'Fortaleza', 'Area_Oportunidad', 'Bloqueo_Emocional', 'Meta_Visibilidad'
            )),
            descripcion TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Historico_Resumenes (
            id_resumen INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            contenido_json TEXT NOT NULL,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Camino_Elegido (
            id_camino_elegido INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            nombre_camino TEXT NOT NULL,
            descripcion_camino TEXT NOT NULL,
            tradeoff_principal TEXT,
            riesgo_principal TEXT,
            tiempo_estimado_semanal TEXT,
            patron_que_rompe TEXT,
            caminos_alternativos_json TEXT,
            fecha_eleccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Textos_Usuario (
            idTexto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            fuente TEXT,            -- 'onboarding' | 'editor' | 'clarity' | 'archive' | 'mirror'
            texto TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Voice_Profile (
            id_usuario INTEGER PRIMARY KEY,
            contenido_json TEXT,
            n_muestras INTEGER DEFAULT 0,
            ultimo_texto_id INTEGER DEFAULT 0,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Logros_Personales (
            idRegistro INTEGER PRIMARY KEY AUTOINCREMENT,
            usuarioLogro INTEGER NOT NULL,
            tipoLogro TEXT,
            logro TEXT NOT NULL,
            descripcionLogro TEXT,
            fechaRegistroLogro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuarioLogro) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Mirror_Patrones (
            idPatron INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            quote TEXT NOT NULL,
            source TEXT,            -- 'scout' | 'user'
            status TEXT,            -- 'pending' | 'observing'
            scout_ref TEXT,         -- nombre del patron de Scout (dedupe), o NULL
            reframe_json TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_observed TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Misiones (
            id_mision INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            contenido_json TEXT NOT NULL,
            progreso_json TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Editor_Borradores (
            idBorrador INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            formato TEXT,                 -- 'correo' | 'linkedin' | etiqueta libre del usuario
            es_correo INTEGER DEFAULT 0,  -- 1 si se renderiza como correo (asunto + cuerpo)
            asunto TEXT,
            borrador TEXT,
            estado TEXT DEFAULT 'activo', -- 'activo' | 'completado'
            contexto_json TEXT,           -- ficha de logro de Archive, si aplica
            turns_json TEXT,              -- historial del chat para retomar
            creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    # Migracion de autenticacion: handle (Nombre#numero) + clave hasheada.
    # Las columnas se agregan sobre la tabla Usuarios existente sin perder datos.
    _asegurar_columna(cursor, "Usuarios", "discriminador", "TEXT")
    _asegurar_columna(cursor, "Usuarios", "password_hash", "TEXT")
    _asegurar_columna(cursor, "Usuarios", "password_salt", "TEXT")

    # Progreso de misiones (acciones completadas) sobre la tabla existente.
    _asegurar_columna(cursor, "Misiones", "progreso_json", "TEXT")
    # Ciclo de vida de la mision: 'activa' | 'completada' + fecha de cierre.
    _asegurar_columna(cursor, "Misiones", "estado", "TEXT DEFAULT 'activa'")
    _asegurar_columna(cursor, "Misiones", "fecha_completada", "TIMESTAMP")

    # Conversacion en progreso de una sesion de Mirror (para retomarla luego).
    _asegurar_columna(cursor, "Mirror_Patrones", "turns_json", "TEXT")

    # Modelo enriquecido de logros para Archive (sobre la tabla existente).
    _asegurar_columna(cursor, "Logros_Personales", "mi_rol", "TEXT")
    _asegurar_columna(cursor, "Logros_Personales", "aprendizaje", "TEXT")
    _asegurar_columna(cursor, "Logros_Personales", "tags_json", "TEXT")
    _asegurar_columna(cursor, "Logros_Personales", "metrics_json", "TEXT")
    # Conversacion de Archive que origino la ficha (para auditar / rehacer).
    _asegurar_columna(cursor, "Logros_Personales", "conversacion_json", "TEXT")
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_handle "
        "ON Usuarios(nombre, discriminador)"
    )

    conexion.commit()
    conexion.close()
