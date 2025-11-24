# models/farmaceuta_model.py

from models.producto_model import ProductoModel 
from models.receta_model import RecetaModel

class FarmaceutaModel:
    """
    Modelo de datos para la Farmacia. Interactúa con la base de datos a través de ProductoModel y RecetaModel.
    """

    def registrar_venta_en_db(self, id_producto, id_farmaceuta, cantidad, total_venta):
        """Registra la venta en la tabla ventas con la fecha y hora actual explícita y la retorna."""
        from database.connection import get_db_connection
        from datetime import datetime
        conn = get_db_connection()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            fecha_venta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """
                INSERT INTO ventas (id_producto, id_farmaceuta, cantidad, total_venta, fecha_venta)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id_producto, id_farmaceuta, cantidad, total_venta, fecha_venta),
            )
            conn.commit()
            # Confirmar que la venta se guardó correctamente y devolver la fecha
            cursor.execute("SELECT id_venta FROM ventas WHERE id_producto=? AND id_farmaceuta=? AND cantidad=? AND total_venta=? AND fecha_venta=? ORDER BY id_venta DESC LIMIT 1", (id_producto, id_farmaceuta, cantidad, total_venta, fecha_venta))
            row = cursor.fetchone()
            if row:
                return fecha_venta
            else:
                return None
        except Exception as e:
            print(f"Error al registrar venta: {e}")
            return None
        finally:
            conn.close()

    def despachar_receta_db(self, id_receta, id_producto, cantidad, total_venta, id_farmaceuta):
        """
        Registra el despacho de una receta:
        1. Descuenta stock.
        2. Cambia estado de receta a 'Despachada'.
        3. Registra la venta.
        Todo en una sola transacción.
        """
        from database.connection import get_db_connection
        from datetime import datetime
        
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión."

        try:
            cursor = conn.cursor()
            conn.execute("BEGIN TRANSACTION;")

            # 1. Verificar Stock nuevamente dentro de la transacción (opcional pero recomendado)
            cursor.execute("SELECT stock_actual FROM productos WHERE id_producto = ?", (id_producto,))
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                return False, "Producto no encontrado."
            
            stock_actual = row[0]
            if stock_actual < cantidad:
                conn.rollback()
                return False, f"Stock insuficiente. Disponible: {stock_actual}"

            # 2. Descontar Stock
            cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto = ?", (cantidad, id_producto))

            # 3. Actualizar Estado Receta
            cursor.execute("UPDATE recetas SET estado = 'Despachada' WHERE id_receta = ?", (id_receta,))

            # 4. Registrar Venta
            fecha_venta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """
                INSERT INTO ventas (id_producto, id_farmaceuta, cantidad, total_venta, fecha_venta)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id_producto, id_farmaceuta, cantidad, total_venta, fecha_venta)
            )

            conn.commit()
            return True, f"Receta despachada correctamente. Venta registrada el {fecha_venta}."

        except Exception as e:
            conn.rollback()
            print(f"Error en transacción de despacho: {e}")
            return False, f"Error en base de datos: {e}"
        finally:
            conn.close()

    def __init__(self):
        self.producto_model = ProductoModel() 
        self.receta_model = RecetaModel()

    def buscar_recetas_pendientes(self):
        """Obtiene recetas pendientes de despacho desde la BD."""
        return self.receta_model.get_pending_recipes()
    
    def obtener_producto_por_id(self, id_producto):
        """Obtiene detalles completos del producto de la DB."""
        return self.producto_model.get_product_details(id_producto)

    def verificar_stock(self, id_producto):
        """Devuelve la cantidad disponible de un producto de la DB."""
        stock = self.producto_model.get_product_stock(id_producto)
        return stock if stock is not None else 0

    def procesar_venta(self, id_producto, cantidad):
        """Actualiza el stock en la DB después de una venta."""
        return self.producto_model.update_product_stock(id_producto, cantidad)

    def obtener_productos_bajo_stock(self):
        """Retorna productos con stock crítico usando la DB."""
        return self.producto_model.get_low_stock_alerts()

    def obtener_productos_por_vencer(self):
        """Retorna productos que vencerán pronto usando la DB."""
        return self.producto_model.get_expiry_alerts()