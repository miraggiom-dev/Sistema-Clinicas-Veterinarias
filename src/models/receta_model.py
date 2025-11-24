# models/receta_model.py
from database.connection import get_db_connection
from sqlite3 import Error

class RecetaModel:
    
    def get_pending_recipes(self):

        conn = get_db_connection()
        if conn is None: return []
        
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

        conn = get_db_connection()
        if conn is None:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO recetas (id_diagnostico, id_producto, cantidad, estado)
                   VALUES (?, ?, ?, 'Emitida')""",
                (id_diagnostico, id_producto, cantidad)
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
        
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos."
            
        try:
            cursor = conn.cursor()
            
            conn.execute("BEGIN TRANSACTION;")
            
            cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto = ?", 
                           (cantidad_requerida, id_producto))
            
            cursor.execute("UPDATE recetas SET estado = 'Despachada' WHERE id_receta = ?", 
                           (id_receta,))
            
            conn.commit()
            return True, "Receta despachada y stock actualizado correctamente."
            
        except Error as e:
            conn.rollback()
            print(f"Error en la transacción de despacho: {e}")
            return False, f"Error DB: {e}"
        finally:
            conn.close()