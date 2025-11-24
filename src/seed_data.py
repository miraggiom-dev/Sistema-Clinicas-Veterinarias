import sqlite3
import os
from datetime import datetime

# Configuración de ruta de DB (Root del proyecto)
# src/seed_data.py -> parent -> veterinaria.db
DB_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "veterinaria.db")

def seed_data():
    print(f"Conectando a la base de datos en: {DB_NAME}")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # 1. Asegurar Usuarios (Ya creados por schema_setup, pero verificamos IDs)
        # ID 3 = Farmacéutico, ID 4 = Veterinario
        
        # 2. Crear Producto de Prueba
        print("Creando producto de prueba...")
        cursor.execute("""
            INSERT INTO productos (nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento)
            VALUES ('Antibiótico General 500mg', 15.50, 8.00, 100, 10, '2025-12-31')
        """)
        id_producto = cursor.lastrowid

        # 3. Crear Propietario
        print("Creando propietario...")
        cursor.execute("""
            INSERT INTO propietarios (nombre, telefono, email, direccion, cedula)
            VALUES ('Juan Perez', '555-0101', 'juan@example.com', 'Calle Falsa 123', '123456789')
        """)
        id_propietario = cursor.lastrowid

        # 4. Crear Mascota
        print("Creando mascota...")
        cursor.execute("""
            INSERT INTO mascotas (id_propietario, nombre, especie, raza, fecha_nacimiento, genero)
            VALUES (?, 'Firulais', 'Perro', 'Labrador', '2020-01-01', 'Macho')
        """, (id_propietario,))
        id_mascota = cursor.lastrowid

        # 5. Crear Servicio
        print("Creando servicio...")
        cursor.execute("""
            INSERT INTO servicios (nombre, precio_base, costo_mano_obra, duracion_estimada)
            VALUES ('Consulta General', 30.00, 10.00, 30)
        """)
        id_servicio = cursor.lastrowid

        # 6. Crear Cita (Hoy)
        print("Creando cita...")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO citas (id_mascota, id_veterinario, id_servicio, fecha_hora, estado, motivo)
            VALUES (?, 4, ?, ?, 'Completada', 'Chequeo general')
        """, (id_mascota, id_servicio, fecha_hoy))
        id_cita = cursor.lastrowid

        # 7. Crear Diagnóstico
        print("Creando diagnóstico...")
        cursor.execute("""
            INSERT INTO diagnosticos (id_cita, id_veterinario, diagnostico, tratamiento, fecha_registro)
            VALUES (?, 4, 'Infección leve', 'Antibióticos por 7 días', ?)
        """, (id_cita, fecha_hoy))
        id_diagnostico = cursor.lastrowid

        # 8. Crear Receta (Estado 'Emitida')
        print("Creando receta pendiente...")
        cursor.execute("""
            INSERT INTO recetas (id_diagnostico, id_producto, cantidad, estado)
            VALUES (?, ?, 2, 'Emitida')
        """, (id_diagnostico, id_producto))
        
        conn.commit()
        print("¡Datos de prueba insertados correctamente!")
        print(f"Producto ID: {id_producto}, Receta creada para 'Firulais'.")

    except Exception as e:
        print(f"Error insertando datos: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    seed_data()
