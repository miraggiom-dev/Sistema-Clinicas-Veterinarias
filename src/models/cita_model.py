from database.connection import get_db_connection


class CitaModel:
    @staticmethod
    def obtener_por_mascota(id_mascota):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM citas WHERE id_mascota = ? ORDER BY fecha_hora DESC",
            (id_mascota,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def obtener_ultima_por_mascota(id_mascota):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM citas WHERE id_mascota = ? ORDER BY fecha_hora DESC LIMIT 1",
            (id_mascota,),
        )
        row = cursor.fetchone()
        conn.close()
        return row
