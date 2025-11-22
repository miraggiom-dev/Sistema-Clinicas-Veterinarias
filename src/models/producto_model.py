from database.connection import get_db_connection

class ProductoModel:
    @staticmethod
    def verificar_stock(id_producto, cantidad_solicitada):
        """Retorna True si hay stock"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stock_actual FROM productos WHERE id_producto = ?", (id_producto,))
        prod = cursor.fetchone()
        conn.close()
        
        if prod and prod['stock_actual'] >= cantidad_solicitada:
            return True
        return False

    @staticmethod
    def descontar_stock(id_producto, cantidad):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto = ?", (cantidad, id_producto))
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            conn.close()