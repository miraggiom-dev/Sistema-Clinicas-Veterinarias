
from models.ingresos_model import IngresosModel

class ReporteController:
    """
    Controlador para reportes administrativos: rentabilidad, auditoría, ingresos, etc.
    """
    def __init__(self):
        self.ingresos_model = IngresosModel()

    def rentabilidad_por_especialidad(self, fecha_inicio=None, fecha_fin=None):
        # Retorna rentabilidad por especialidad (cirugía, consulta, vacunación)
        from database.connection import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
            SELECT s.nombre AS especialidad, COUNT(c.id_cita) AS cantidad, SUM(s.precio_base) AS total
            FROM citas c
            JOIN servicios s ON c.id_servicio = s.id_servicio
            WHERE s.nombre IN ('Cirugía', 'Consulta', 'Vacunación')
        '''
        params = []
        if fecha_inicio and fecha_fin:
            query += " AND date(c.fecha_hora) BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])
        query += " GROUP BY s.nombre"
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    def historial_cambios_diagnostico(self, id_paciente=None):
        # ... (sin cambios)
        return []

    def ingresos_mensuales(self, mes, anio):
        return self.ingresos_model.obtener_ingresos_por_mes(mes, anio)

    def exportar_txt(self, datos, mes, anio):
        return self.ingresos_model.exportar_ingresos_txt(datos, mes, anio)
