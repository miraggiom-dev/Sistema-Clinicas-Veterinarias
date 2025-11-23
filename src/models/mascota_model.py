from database.connection import get_db_connection


class MascotaModel:
    @staticmethod
    def obtener_todas_con_propietario():
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT m.*, p.nombre as propietario_nombre
            FROM mascotas m
            JOIN propietarios p ON m.id_propietario = p.id_propietario
            ORDER BY p.nombre, m.nombre
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def crear(id_propietario, nombre, especie, raza, nacimiento, genero):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO mascotas (id_propietario, nombre, especie, raza, fecha_nacimiento, genero)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (id_propietario, nombre, especie, raza, nacimiento, genero),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creando mascota: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def obtener_por_propietario(id_propietario):
        """esto lo hizo thomas pa obtener todas las mascotas como las personas en bdd"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM mascotas WHERE id_propietario = ?", (id_propietario,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
