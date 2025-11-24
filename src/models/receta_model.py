from database.connection import get_db_connection
from sqlite3 import Error


import sqlite3
from sqlite3 import Error


class RecetaModel:

    def get_pending_recipes(self):
        """Obtiene todas las recetas en estado 'Emitida' para despacho (Query 1)."""
        conn = get_db_connection()
        if conn is None:
            return []

        query = """
        SELECT R.id_receta, R.id_producto, R.cantidad,
               C.fecha_hora AS Fecha_Cita, M.nombre AS Mascota, P.nombre AS Producto_Recetado, 
               U.nombre_completo AS Veterinario_Emisor
        FROM recetas AS R
        JOIN productos AS P ON R.id_producto = P.id_producto
        JOIN diagnosticos AS D ON R.id_diagnostico = D.id_diagnostico
        JOIN citas AS C ON D.id_cita = C.id_cita
        JOIN mascotas AS M ON C.id_mascota = M.id_mascota
        JOIN usuarios AS U ON D.id_veterinario = U.id_usuario
        WHERE R.estado = 'Emitida'
        ORDER BY C.fecha_hora ASC;
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener recetas: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def crear(id_diagnostico, id_producto, cantidad):
        """Crea una nueva receta asociada a un diagnóstico."""
        conn = get_db_connection()
        if conn is None:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO recetas (id_diagnostico, id_producto, cantidad, estado)
                   VALUES (?, ?, ?, 'Emitida')""",
                (id_diagnostico, id_producto, cantidad),
            )
            conn.commit()
            return True
        except Error as e:
            print(f"Error al crear receta: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def process_dispatch(self, id_receta, id_producto, cantidad_requerida):
        """
        Maneja la transacción para reducir el stock y actualizar el estado de la receta.
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos."

        try:
            cursor = conn.cursor()

            conn.execute("BEGIN TRANSACTION;")

            cursor.execute(
                "UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto = ?",
                (cantidad_requerida, id_producto),
            )

            cursor.execute(
                "UPDATE recetas SET estado = 'Despachada' WHERE id_receta = ?",
                (id_receta,),
            )

            conn.commit()
            return True, "Receta despachada y stock actualizado correctamente."

        except Error as e:
            conn.rollback()
            print(f"Error en la transacción de despacho: {e}")
            return False, f"Error DB: {e}"
        finally:
            conn.close()

    def get_recetas_detalladas(self, estado_filtro=None, cedula_propietario=None):

        conn = get_db_connection()
        if conn is None:
            return []

        query = """
            SELECT
                R.id_receta, R.cantidad AS cantidad_recetada, R.estado AS estado_receta,
                P.nombre AS nombre_producto, 
                D.id_diagnostico, D.diagnostico, D.tratamiento,
                U.nombre_completo AS nombre_veterinario,
                M.nombre AS nombre_mascota, M.especie, M.raza, M.genero,
                PR.id_propietario, PR.nombre AS nombre_propietario, PR.cedula AS cedula_propietario, PR.telefono AS telefono_propietario
            FROM
                recetas R
            INNER JOIN productos P ON R.id_producto = P.id_producto
            INNER JOIN diagnosticos D ON R.id_diagnostico = D.id_diagnostico
            INNER JOIN citas C ON D.id_cita = C.id_cita
            INNER JOIN mascotas M ON C.id_mascota = M.id_mascota
            INNER JOIN propietarios PR ON M.id_propietario = PR.id_propietario
            INNER JOIN usuarios U ON D.id_veterinario = U.id_usuario
        """

        where_clauses = []
        params = []

        if estado_filtro:
            where_clauses.append("R.estado = ?")
            params.append(estado_filtro)

        if cedula_propietario:
            where_clauses.append("PR.cedula = ?")
            params.append(cedula_propietario)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY R.id_receta DESC;"

        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(query, params)

            return cursor.fetchall()

        except Error as e:
            print(f"Error al obtener recetas detalladas: {e}")
            return []
        finally:
            if conn:
                conn.close()
