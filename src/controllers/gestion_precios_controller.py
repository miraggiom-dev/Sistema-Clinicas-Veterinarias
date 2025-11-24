from models.producto_model import ProductoModel
from models.servicio_model import ServicioModel

class GestionPreciosController:
    def __init__(self):
        self.producto_model = ProductoModel()
        self.servicio_model = ServicioModel()

    def obtener_productos(self):
        return self.producto_model.get_all_products()

    def obtener_servicios(self):
        return self.servicio_model.obtener_todos(activos_only=False)

    def actualizar_precio_producto(self, id_producto, nuevo_precio):
        # Actualiza el precio de un producto
        from database.connection import get_db_connection
        conn = get_db_connection()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE productos SET precio_venta = ? WHERE id_producto = ?",
                (nuevo_precio, id_producto)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error actualizando precio producto: {e}")
            return False
        finally:
            conn.close()

    def actualizar_precio_servicio(self, id_servicio, nuevo_precio):
        # Actualiza el precio base de un servicio
        return self.servicio_model.actualizar(id_servicio, precio_base=nuevo_precio)
