from database.connection import get_db_connection
import re

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
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM propietarios WHERE cedula = ? AND cedula != 'N/A'", (cedula,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    @staticmethod
    def crear(cedula, nombre, telefono, email, direccion):

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

            print(f"Error creando propietario (DB): {e}") 
            return None
        finally:
            conn.close()

    @staticmethod
    def buscar_por_nombre(busqueda):
        conn = get_db_connection()
        cursor = conn.cursor()

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

    @staticmethod
    def _is_valid_telefono(telefono):

        if telefono is None:
            return True
        tel = str(telefono).strip()
        if tel == "":
            return True

        return bool(re.fullmatch(r"\d{6,15}", tel))

    @staticmethod
    def _is_valid_email(email):
        if email is None:
            return True
        em = str(email).strip()
        if em == "":
            return True

        return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", em))

    @staticmethod
    def actualizar(id_propietario, nombre=None, telefono=None, email=None, direccion=None):
    
        if nombre is not None:
            if str(nombre).strip() == "":
                return (False, "El nombre no puede quedar vacío.")

        if not PropietarioModel._is_valid_telefono(telefono):
            return (False, "Teléfono inválido. Debe contener sólo dígitos (6-15).")

        if not PropietarioModel._is_valid_email(email):
            return (False, "Email inválido.")

        fields = []
        params = []
        if nombre is not None:
            fields.append("nombre = ?")
            params.append(str(nombre).strip())
        if telefono is not None:
            params.append(str(telefono).strip())
            fields.append("telefono = ?")
        if email is not None:
            fields.append("email = ?")
            params.append(str(email).strip())
        if direccion is not None:
            fields.append("direccion = ?")
            params.append(str(direccion).strip())

        if not fields:

            return (False, "No hay campos para actualizar.")

        params.append(id_propietario)

        query = f"UPDATE propietarios SET {', '.join(fields)} WHERE id_propietario = ?"

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, tuple(params))
            conn.commit()
            return (True, "Datos actualizados correctamente.")
        except Exception as e:
            return (False, f"Error actualizando propietario: {e}")
        finally:
            conn.close()
    
