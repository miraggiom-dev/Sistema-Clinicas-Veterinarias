from database.connection import get_db_connection


class IngresosModel:
    @staticmethod
    def obtener_ventas_por_mes(mes, anio):
        """
        Retorna una lista de ventas de productos para el mes y año dados.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        query_ventas = '''
            SELECT v.id_venta, v.fecha_venta, pr.nombre AS producto, v.cantidad, v.total_venta, u.nombre_completo AS farmaceuta
            FROM ventas v
            JOIN productos pr ON v.id_producto = pr.id_producto
            JOIN usuarios u ON v.id_farmaceuta = u.id_usuario
            WHERE strftime('%m', v.fecha_venta) = ? AND strftime('%Y', v.fecha_venta) = ?
        '''
        cursor.execute(query_ventas, (f"{int(mes):02d}", str(anio)))
        ventas = cursor.fetchall()
        conn.close()
        return ventas

    @staticmethod
    def exportar_ventas_txt(ventas, mes, anio):
        import os
        carpeta = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'informes_mensuales')
        os.makedirs(carpeta, exist_ok=True)
        nombre_archivo = os.path.join(carpeta, f"ventas_{anio}_{str(mes).zfill(2)}.txt")
        headers = ["ID Venta", "Fecha", "Producto", "Cantidad", "Total Venta ($)", "Farmaceuta"]
        total_mes = sum(float(row[4]) for row in ventas)
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write("\t".join(headers) + "\n")
            for row in ventas:
                f.write("\t".join(str(x) for x in row) + "\n")
            f.write(f"\nTOTAL DEL MES: $ {total_mes:.2f}\n")
        return nombre_archivo
    @staticmethod
    def obtener_ingresos_por_mes(mes, anio):
        """
        Retorna una lista de ingresos (servicios y productos) para el mes y año dados.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        # Servicios
        query_servicios = '''
            SELECT c.id_cita, c.fecha_hora, s.nombre AS servicio, s.precio_base, p.nombre AS propietario
            FROM citas c
            JOIN servicios s ON c.id_servicio = s.id_servicio
            JOIN mascotas m ON c.id_mascota = m.id_mascota
            JOIN propietarios p ON m.id_propietario = p.id_propietario
            WHERE strftime('%m', c.fecha_hora) = ? AND strftime('%Y', c.fecha_hora) = ?
        '''
        cursor.execute(query_servicios, (f"{int(mes):02d}", str(anio)))
        servicios = cursor.fetchall()
        # Ventas de productos
        query_ventas = '''
            SELECT v.id_venta, v.fecha_venta, pr.nombre AS producto, v.total_venta, u.nombre_completo AS farmaceuta
            FROM ventas v
            JOIN productos pr ON v.id_producto = pr.id_producto
            JOIN usuarios u ON v.id_farmaceuta = u.id_usuario
            WHERE strftime('%m', v.fecha_venta) = ? AND strftime('%Y', v.fecha_venta) = ?
        '''
        cursor.execute(query_ventas, (f"{int(mes):02d}", str(anio)))
        ventas = cursor.fetchall()
        conn.close()
        # Unificar ambos tipos de ingresos
        return servicios + ventas

    @staticmethod
    def exportar_ingresos_txt(datos, mes, anio):
        import os
        carpeta = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'informes_mensuales')
        os.makedirs(carpeta, exist_ok=True)
        nombre_archivo = os.path.join(carpeta, f"ingresos_{anio}_{str(mes).zfill(2)}.txt")
        headers = ["ID Cita", "Fecha", "Servicio", "Precio", "Propietario"]
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write("\t".join(headers) + "\n")
            for row in datos:
                f.write("\t".join(str(x) for x in row) + "\n")
        return nombre_archivo
