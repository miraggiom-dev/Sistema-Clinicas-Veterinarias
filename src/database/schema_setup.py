import sqlite3
import os

DB_NAME = "veterinaria.db"

def create_tables():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            rol TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            estado INTEGER NOT NULL DEFAULT 1
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS propietarios (
            id_propietario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            direccion TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio_venta REAL NOT NULL,
            costo_unitario REAL NOT NULL,
            stock_actual INTEGER NOT NULL DEFAULT 0,
            stock_minimo INTEGER NOT NULL DEFAULT 5,
            fecha_vencimiento TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio_base REAL NOT NULL,
            costo_mano_obra REAL NOT NULL,
            duracion_estimada INTEGER NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        );
        """)

        cursor.execute("""
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
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
            id_mascota INTEGER NOT NULL,
            id_veterinario INTEGER NOT NULL,
            id_servicio INTEGER NOT NULL,
            fecha_hora TEXT NOT NULL,
            fecha_fin TEXT,
            estado TEXT NOT NULL,
            motivo TEXT NOT NULL,
            FOREIGN KEY(id_mascota) REFERENCES mascotas(id_mascota),
            FOREIGN KEY(id_veterinario) REFERENCES usuarios(id_usuario),
            FOREIGN KEY(id_servicio) REFERENCES servicios(id_servicio)
        );
        """)

        cursor.execute("""
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
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recetas (
            id_receta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_diagnostico INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY(id_diagnostico) REFERENCES diagnosticos(id_diagnostico),
            FOREIGN KEY(id_producto) REFERENCES productos(id_producto)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditorias (
            id_log INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            tabla_afectada TEXT NOT NULL,
            id_registro INTEGER NOT NULL,
            accion TEXT NOT NULL,
            datos_antes TEXT NOT NULL,
            datos_despues TEXT NOT NULL,
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
        );
        """)

        # un admin bro
        cursor.execute("""
        INSERT OR IGNORE INTO usuarios (id_usuario, nombre_completo, rol, email, password, estado)
        VALUES (1, 'Administrador', 'Administrador', 'admin@vet.com', 'admin123', 1)
        """)

        conn.commit()
        print("Base de datos y tablas creadas exitosamente.")
        
    except sqlite3.Error as e:
        print(f"Error creando base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_tables()