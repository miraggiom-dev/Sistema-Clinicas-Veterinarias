# models/propietario_model.py (CORREGIDO)

from database.connection import get_db_connection

class PropietarioModel:
    def __init__(self, id_prop=None, cedula=None, nombre=None, telefono=None, email=None, direccion=None):
        self.id_propietario = id_prop
        self.cedula = cedula
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion

    @staticmethod
    def existe_cedula(cedula):
        """Verifica si una cédula ya está registrada en la base de datos."""
        conn = get_db_connection()
        cursor = conn.cursor()
        # Excluimos el valor 'N/A' si quieres que existan múltiples clientes antiguos sin cédula
        cursor.execute("SELECT 1 FROM propietarios WHERE cedula = ? AND cedula != 'N/A'", (cedula,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    @staticmethod
    def crear(cedula, nombre, telefono, email, direccion):
        # 1. Validación de Cédula: Evita crear si la cédula ya existe (y no es el valor de relleno 'N/A')
        if cedula != 'N/A' and PropietarioModel.existe_cedula(cedula):
            print(f"Error: La cédula {cedula} ya existe.")
            return None 

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO propietarios (cedula, nombre, telefono, email, direccion) 
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (cedula, nombre, telefono, email, direccion))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            # Esto atrapará errores como el UNIQUE constraint si la DB lo tiene
            print(f"Error creando propietario (DB): {e}") 
            return None
        finally:
            conn.close()

    @staticmethod
    def buscar_por_nombre(busqueda):
        conn = get_db_connection()
        cursor = conn.cursor()
        # Búsqueda flexible por nombre O por cédula
        query = "SELECT * FROM propietarios WHERE nombre LIKE ? OR cedula LIKE ?"
        cursor.execute(query, (f'%{busqueda}%', f'%{busqueda}%'))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def obtener_por_id(id_propietario):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM propietarios WHERE id_propietario = ?", (id_propietario,))
        row = cursor.fetchone()
        conn.close()
        return row
    
