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

    def registrar_venta(self, id_producto, cantidad, id_farmaceuta=None):
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
        
        if id_farmaceuta is None:
            return False, "Error: No se pudo identificar al usuario que realiza la venta."

        datos_producto = self.modelo.obtener_producto_por_id(id_producto)
        nombre_producto = datos_producto["nombre"] if datos_producto else "(desconocido)"
        precio_unitario = datos_producto["precio"] if datos_producto else 0
        total_venta = precio_unitario * cantidad

        exito_stock = self.modelo.procesar_venta(id_producto, cantidad)
        if not exito_stock:
            return False, "Error al actualizar el stock del producto."

        fecha_venta = self.modelo.registrar_venta_en_db(id_producto, id_farmaceuta, cantidad, total_venta)
        if fecha_venta:
            return True, f"Venta registrada: {nombre_producto} x{cantidad} el {fecha_venta}. Total: ${total_venta:.2f}. Stock actualizado."
        else:
            return False, "Error: No se pudo guardar la venta en la base de datos."

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
            
            mapeo_id_nombre[formato_combo] = id_producto
            
        return lista_combo, mapeo_id_nombre

    def procesar_despacho(self, id_receta, id_producto, cantidad, id_farmaceuta):
        """
        Procesa el despacho de una receta médica.
        """
        try:
            id_receta = int(id_receta)
            id_producto = int(id_producto)
            cantidad = int(cantidad)
        except ValueError:
            return False, "Error: IDs y cantidad deben ser numéricos."

        # 1. Obtener datos del producto para calcular total
        datos_producto = self.modelo.obtener_producto_por_id(id_producto)
        if not datos_producto:
            return False, "Error: Producto no encontrado."
        
        precio_unitario = datos_producto["precio"]
        total_venta = precio_unitario * cantidad

        # 2. Llamar al modelo para la transacción
        exito, mensaje = self.modelo.despachar_receta_db(
            id_receta, id_producto, cantidad, total_venta, id_farmaceuta
        )
        
        return exito, mensaje