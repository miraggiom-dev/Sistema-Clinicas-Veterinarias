from database.connection import get_db_connection
from sqlite3 import Error

class ProductoModel:
    
    def get_all_products(self):
        """Obtiene todo el inventario (Query 2)."""
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
        """
        Obtiene nombre, stock, precio y vencimiento de un producto por su ID.
        """
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
        """Obtiene productos con stock bajo (Query 3A). Retorna (id, nombre, stock_actual)."""
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
            # Retorna una lista de tuplas (id, nombre, stock)
            return cursor.fetchall() 
        except Error as e:
            print(f"Error al obtener alertas de stock: {e}")
            return []
        finally:
            conn.close()
    
    def get_expiry_alerts(self):
        """Obtiene productos con vencimiento cercano (Query 3B - 90 días). Retorna (id, nombre, fecha_vencimiento)."""
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
            # Retorna una lista de tuplas (id, nombre, fecha)
            return cursor.fetchall() 
        except Error as e:
            print(f"Error al obtener alertas de vencimiento: {e}")
            return []
        finally:
            conn.close()
            
    def get_product_stock(self, id_producto):
        """Obtiene el stock actual de un producto específico."""
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
        """Actualiza el stock después de una venta."""
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
            
    def add_product(self, nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento):
        """Inserta un nuevo producto al inventario."""
        conn = get_db_connection()
        if conn is None: return False
        
        query = """
        INSERT INTO productos (nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query, (nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento))
            conn.commit()
            return True
        except Error as e:
            print(f"Error al añadir producto: {e}")
            return False
        finally:
            conn.close()