# models/farmaceuta_model.py

from models.producto_model import ProductoModel 

class FarmaceutaModel:
    """
    Modelo de datos para la Farmacia. Interactúa con la base de datos a través de ProductoModel.
    """
    def __init__(self):
        self.producto_model = ProductoModel() 
        # Simulación de recetas pendientes
        self.recetas_pendientes = [
            {"id": 101, "id_medicamento": 1, "cantidad": 10, "veterinario": "Dr. Smith"},
            {"id": 102, "id_medicamento": 2, "cantidad": 1, "veterinario": "Dra. Lee"},
        ]

    def buscar_recetas_pendientes(self):
        """Simula la obtención de recetas pendientes de despacho."""
        return self.recetas_pendientes
    
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