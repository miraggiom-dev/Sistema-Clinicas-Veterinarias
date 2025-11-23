from database.connection import get_db_connection


class RecetaModel:
    @staticmethod
    def crear(id_diagnostico, id_producto, cantidad, estado="Prescrito"):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO recetas (id_diagnostico, id_producto, cantidad, estado)
                VALUES (?, ?, ?, ?)
                """,
                (id_diagnostico, id_producto, cantidad, estado),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creando receta: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def obtener_por_diagnostico(id_diagnostico):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM recetas WHERE id_diagnostico = ?", (id_diagnostico,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
