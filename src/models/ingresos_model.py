from database.connection import get_db_connection


class IngresosModel:
    @staticmethod
    def obtener_ingresos_por_mes(mes, anio):
        """
        Retorna una lista de ingresos (servicios y productos) para el mes y año dados.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            SELECT c.id_cita, c.fecha_hora, s.nombre AS servicio, s.precio_base, p.nombre AS propietario
            FROM citas c
            JOIN servicios s ON c.id_servicio = s.id_servicio
            JOIN mascotas m ON c.id_mascota = m.id_mascota
            JOIN propietarios p ON m.id_propietario = p.id_propietario
            WHERE strftime('%m', c.fecha_hora) = ? AND strftime('%Y', c.fecha_hora) = ?
        '''
        cursor.execute(query, (f"{int(mes):02d}", str(anio)))
        servicios = cursor.fetchall()
        # TODO: sumar ventas de productos si aplica
        conn.close()
        return servicios

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
