import sqlite3
import os
from pathlib import Path
import dotenv

dotenv.load_dotenv()


DATABASE_PATH_ENV = os.getenv("DATABASE_PATH")
DATABASE_URL_ENV = os.getenv("DATABASE_URL")

def _resolve_db_path():
    if DATABASE_PATH_ENV:
        path = DATABASE_PATH_ENV
    elif DATABASE_URL_ENV:
        if DATABASE_URL_ENV.startswith("sqlite:///"):
            path = DATABASE_URL_ENV.replace("sqlite:///", "", 1)
        elif DATABASE_URL_ENV.startswith("sqlite:////"):
            path = DATABASE_URL_ENV.replace("sqlite:////", "/", 1)
        else:
            path = DATABASE_URL_ENV
    else:
        # Ruta por defecto
        path = os.path.join(os.getcwd(), "veterinaria.db")
        print("la ruta creada es", path)

    p = Path(path).expanduser().resolve()
    
    db_dir = p.parent 
    
    if not db_dir.exists():
        print(f"Creando directorio para la base de datos: {db_dir}")
        os.makedirs(db_dir, exist_ok=True) 
        
    return str(p)

# La variable global que contiene la ruta final de la DB
DB_NAME = _resolve_db_path()

def create_tables():
    """
    Se conecta a la base de datos SQLite (creándola si no existe) y 
    crea todas las tablas con la cláusula IF NOT EXISTS.
    También inserta un usuario administrador por defecto.
    """
    conn = None
    try:
        # Se conecta a la DB. Si el archivo no existe, lo crea.
        conn = sqlite3.connect(DB_NAME)
        # Habilitar el soporte de claves foráneas
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        # 1. Tabla de Usuarios
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            rol TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, 
            estado INTEGER NOT NULL DEFAULT 1
        );
        """
        )

        # 2. Tabla de Propietarios
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS propietarios (
            id_propietario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            cedula TEXT UNIQUE
        );
        """
        )

        # 3. Tabla de Productos (Inventario)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio_venta REAL NOT NULL,
            costo_unitario REAL NOT NULL,
            stock_actual INTEGER NOT NULL DEFAULT 0,
            stock_minimo INTEGER NOT NULL DEFAULT 5,
            fecha_vencimiento TEXT
        );
        """
        )

        # 4. Tabla de Servicios (Costo de procedimientos)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS servicios (
            id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio_base REAL NOT NULL,
            costo_mano_obra REAL NOT NULL,
            duracion_estimada INTEGER NOT NULL, -- en minutos
            activo INTEGER NOT NULL DEFAULT 1
        );
        """
        )

        # 5. Tabla de Mascotas (Referencia a Propietarios)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS mascotas (
            id_mascota INTEGER PRIMARY KEY AUTOINCREMENT,
            id_propietario INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            especie TEXT NOT NULL,
            raza TEXT,
            fecha_nacimiento TEXT,
            genero TEXT,
            FOREIGN KEY(id_propietario) REFERENCES propietarios(id_propietario)
        );
        """
        )

        # 6. Tabla de Citas
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS citas (
            id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
            id_mascota INTEGER NOT NULL,
            id_veterinario INTEGER NOT NULL,
            id_servicio INTEGER NOT NULL,
            fecha_hora TEXT NOT NULL, -- Inicio de la cita
            fecha_fin TEXT,
            estado TEXT NOT NULL, -- Ej: Programada, En Curso, Completada, Cancelada
            motivo TEXT NOT NULL,
            FOREIGN KEY(id_mascota) REFERENCES mascotas(id_mascota),
            FOREIGN KEY(id_veterinario) REFERENCES usuarios(id_usuario),
            FOREIGN KEY(id_servicio) REFERENCES servicios(id_servicio)
        );
        """
        )

        # 7. Tabla de Diagnósticos (Historial Clínico)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS diagnosticos (
            id_diagnostico INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cita INTEGER NOT NULL,
            id_veterinario INTEGER NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            diagnostico TEXT NOT NULL,
            tratamiento TEXT NOT NULL,
            observacion_edicion TEXT,
            fecha_registro TEXT NOT NULL,
            es_actual INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(id_cita) REFERENCES citas(id_cita),
            FOREIGN KEY(id_veterinario) REFERENCES usuarios(id_usuario)
        );
        """
        )

        # 8. Tabla de Recetas (Artículos vendidos/usados)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS recetas (
            id_receta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_diagnostico INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            estado TEXT NOT NULL, -- Ej: Emitida, Despachada
            FOREIGN KEY(id_diagnostico) REFERENCES diagnosticos(id_diagnostico),
            FOREIGN KEY(id_producto) REFERENCES productos(id_producto)
        );
        """
        )
        
        # 9. Tabla de Auditorías/Logs
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS auditorias (
            id_log INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            tabla_afectada TEXT NOT NULL,
            id_registro INTEGER NOT NULL,
            accion TEXT NOT NULL, -- Ej: INSERT, UPDATE, DELETE
            datos_antes TEXT, 
            datos_despues TEXT, 
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
        );
        """
        )

        # Inserta el usuario administrador por defecto
        # Contraseña 'admin123'. Idealmente debería estar hasheada.
        cursor.execute(
            """
        INSERT OR IGNORE INTO usuarios (id_usuario, nombre_completo, rol, email, password, estado)
        VALUES (1, 'Administrador del Sistema', 'Administrador', 'admin@vet.com', 'admin123', 1)
        """
        )

        conn.commit()
        print(f"Base de datos y tablas creadas/verificadas exitosamente en: {DB_NAME}")

    except sqlite3.Error as e:
        print(f"Error creando base de datos: {e}")
    finally:
        if conn:
            conn.close()

# Exportar la función principal y el nombre de la base de datos si es necesario
__all__ = ["create_tables", "DB_NAME"]