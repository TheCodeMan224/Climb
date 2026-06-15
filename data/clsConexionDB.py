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
        CREATE TABLE IF NOT EXISTS Misiones (
            id_mision INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            contenido_json TEXT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
        );
        """
    )

    # Migracion de autenticacion: handle (Nombre#numero) + clave hasheada.
    # Las columnas se agregan sobre la tabla Usuarios existente sin perder datos.
    _asegurar_columna(cursor, "Usuarios", "discriminador", "TEXT")
    _asegurar_columna(cursor, "Usuarios", "password_hash", "TEXT")
    _asegurar_columna(cursor, "Usuarios", "password_salt", "TEXT")
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_handle "
        "ON Usuarios(nombre, discriminador)"
    )

    conexion.commit()
    conexion.close()
