# FARMACEUTA CONTROLLER

from models.farmaceuta_model import FarmaceutaModel


class FarmaceutaController:
    def __init__(self):
        self.modelo = FarmaceutaModel()

    def registrar_producto(self, nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento):
        """
        Registra un nuevo producto en el inventario.
        """
        try:
            precio_venta = float(precio_venta)
            costo_unitario = float(costo_unitario)
            stock_actual = int(stock_actual)
            stock_minimo = int(stock_minimo)
        except ValueError:
            return False, "Error: Verifique los datos numéricos."

        if not nombre or precio_venta < 0 or costo_unitario < 0 or stock_actual < 0 or stock_minimo < 0 or not fecha_vencimiento:
            return False, "Error: Complete todos los campos correctamente."

        exito = self.modelo.producto_model.add_product(
            nombre, precio_venta, costo_unitario, stock_actual, stock_minimo, fecha_vencimiento
        )
        return (exito, "Producto registrado exitosamente." if exito else "Error al registrar el producto.")

    def obtener_recetas_pendientes(self):
        """Obtiene la lista de recetas médicas pendientes."""
        return self.modelo.buscar_recetas_pendientes()
    
    def obtener_datos_producto(self, id_producto):
        """Obtiene los detalles de un producto por su ID (Nombre, Stock, Precio, Vencimiento)."""
        try:
            id_producto = int(id_producto)
        except ValueError:
            return None 

        return self.modelo.obtener_producto_por_id(id_producto)

    def registrar_venta(self, id_producto, cantidad):
        """
        Registra una venta de producto.
        Verifica el stock antes de procesar la venta.
        """
        try:
            id_producto = int(id_producto)
            cantidad = int(cantidad)
        except ValueError:
            return False, "ID de producto y cantidad deben ser números enteros."
        
        if cantidad <= 0:
             return False, "La cantidad debe ser mayor a cero."
             
        stock_disponible = self.modelo.verificar_stock(id_producto)
        
        if stock_disponible == 0:
             return False, "Error: Producto no encontrado o stock inicial es cero."
             
        if stock_disponible < cantidad:
            return False, f"Error: Stock insuficiente. Solo quedan {stock_disponible} unidades."
        
        exito = self.modelo.procesar_venta(id_producto, cantidad)
        
        return exito, "Venta registrada exitosamente y stock actualizado." if exito else "Error interno al registrar la venta."

    def obtener_alertas_inventario(self):
        """Retorna las alertas de bajo stock y productos próximos a vencer."""
        stock_bajo = self.modelo.obtener_productos_bajo_stock()
        por_vencer = self.modelo.obtener_productos_por_vencer()
        return {"stock_bajo": stock_bajo, "por_vencer": por_vencer}
    
    def obtener_lista_productos_para_venta(self):
        """
        Obtiene la lista de todos los productos para llenar el ComboBox.
        Devuelve una lista de strings con formato "ID - Nombre (Stock)".
        También devuelve un mapeo para obtener el ID a partir del nombre.
        """
        productos_db = self.modelo.producto_model.get_all_products()
        lista_combo = []
        mapeo_id_nombre = {}

        for p in productos_db:
            id_producto = p[0]
            nombre = p[1]
            stock = p[2]
            
            formato_combo = f"{id_producto} - {nombre} (Stock: {stock})"
            lista_combo.append(formato_combo)
            
            mapeo_id_nombre[formato_combo] = id_producto
            
        return lista_combo, mapeo_id_nombre