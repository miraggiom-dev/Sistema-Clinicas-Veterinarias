from database.connection import get_db_connection


class UsuarioModel:
    @staticmethod
    def crear(nombre, rol, email, password):
        """Crea un nuevo usuario con rol, email y password."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO usuarios (nombre_completo, rol, email, password, estado)
                VALUES (?, ?, ?, ?, 1)
                """,
                (nombre, rol, email, password)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return False
        finally:
            conn.close()

    def __init__(self, id_usuario=None, nombre=None, rol=None, email=None, password=None):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.rol = rol
        self.email = email
        self.password = password

    @staticmethod
    def autenticar(email, password):
        """Verifica credenciales y retorna el usuario si es correcto."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM usuarios WHERE email = ? AND password = ? AND estado = 1"
        cursor.execute(query, (email, password))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return UsuarioModel(
                id_usuario=user_data['id_usuario'],
                nombre=user_data['nombre_completo'],
                rol=user_data['rol'],
                email=user_data['email']
            )
        return None

    @staticmethod
    def obtener_todos():
        """Para uso del Admin: Listar usuarios."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre_completo, rol, email, estado FROM usuarios")
        users = cursor.fetchall()
        conn.close()
        return users