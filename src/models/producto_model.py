from database.connection import get_db_connection
from sqlite3 import Error

class ProductoModel:
    def actualizar_producto(self, id_producto, stock_actual, stock_minimo, precio_venta, costo_unitario, fecha_vencimiento):

        conn = get_db_connection()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE productos
                SET stock_actual = ?, stock_minimo = ?, precio_venta = ?, costo_unitario = ?, fecha_vencimiento = ?
                WHERE id_producto = ?
                """,
                (stock_actual, stock_minimo, precio_venta, costo_unitario, fecha_vencimiento, id_producto),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            return False
        finally:
            conn.close()

    def add_product(self, nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento):

        conn = get_db_connection()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO productos (nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al añadir producto: {e}")
            return False
        finally:
            conn.close()

    def get_all_products(self):

        conn = get_db_connection()
        if conn is None: return []
        
        query = """
        SELECT id_producto, nombre, stock_actual, stock_minimo, 
               precio_venta, costo_unitario, fecha_vencimiento
        FROM productos
        ORDER BY nombre ASC;
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener inventario: {e}")
            return []
        finally:
            conn.close()
            
    def get_product_details(self, id_producto):
        
        conn = get_db_connection()
        if conn is None: return None
        
        query = """
        SELECT id_producto, nombre, stock_actual, precio_venta, fecha_vencimiento
        FROM productos
        WHERE id_producto = ?;
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query, (id_producto,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "nombre": row[1],
                    "stock": row[2],
                    "precio": row[3],
                    "vence": row[4]
                }
            return None
        except Error as e:
            print(f"Error al obtener detalles de producto {id_producto}: {e}")
            return None
        finally:
            conn.close()

    def get_low_stock_alerts(self):

        conn = get_db_connection()
        if conn is None: return []

        query = """
        SELECT id_producto, nombre, stock_actual
        FROM productos
        WHERE stock_actual <= stock_minimo
        ORDER BY stock_actual ASC;
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query)

            return cursor.fetchall() 
        except Error as e:
            print(f"Error al obtener alertas de stock: {e}")
            return []
        finally:
            conn.close()
    
    def get_expiry_alerts(self):

        conn = get_db_connection()
        if conn is None: return []

        query = """
        SELECT id_producto, nombre, fecha_vencimiento
        FROM productos
        WHERE fecha_vencimiento BETWEEN DATE('now') AND DATE('now', '+90 days')
        ORDER BY fecha_vencimiento ASC;
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query)

            return cursor.fetchall() 
        except Error as e:
            print(f"Error al obtener alertas de vencimiento: {e}")
            return []
        finally:
            conn.close()
            
    def get_product_stock(self, id_producto):

        conn = get_db_connection()
        if conn is None: return None
        
        query = "SELECT stock_actual FROM productos WHERE id_producto = ?" 
        try:
            cursor = conn.cursor()
            cursor.execute(query, (id_producto,))
            row = cursor.fetchone()
            return row[0] if row else 0 
        except Error as e:
            print(f"Error al verificar stock de producto {id_producto}: {e}")
            return None
        finally:
            conn.close()
            
    def update_product_stock(self, id_producto, cantidad_vendida):

        conn = get_db_connection()
        if conn is None: return False

        query = """
        UPDATE productos
        SET stock_actual = stock_actual - ?
        WHERE id_producto = ?;
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query, (cantidad_vendida, id_producto))
            conn.commit()
            return cursor.rowcount > 0 
        except Error as e:
            print(f"Error al actualizar stock: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def obtener_todos():

        conn = get_db_connection()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos ORDER BY nombre ASC")
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener productos: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def crear(nombre, precio_venta, costo_unitario, stock_actual, fecha_vencimiento):

        conn = get_db_connection()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO productos (nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento)
                VALUES (?, ?, ?, ?, 5, ?)
                """,
                (nombre, precio_venta, costo_unitario, stock_actual, fecha_vencimiento),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al crear producto: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def descontar_stock(id_producto, cantidad):

        conn = get_db_connection()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto = ?",
                (cantidad, id_producto),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al descontar stock: {e}")
            return False
        finally:
            conn.close()
