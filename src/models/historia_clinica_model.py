from database.connection import get_db_connection


class HistoriaClinicaModel:
    @staticmethod
    def obtener_por_mascota(id_mascota):
        """
        Devuelve una lista de diagnósticos (historial clínico) para una mascota específica.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT d.id_cita, d.id_veterinario, d.fecha_registro as fecha, d.diagnostico, d.tratamiento, d.observacion_edicion, u.nombre_completo as veterinario, d.version, d.es_actual
            FROM diagnosticos d
            JOIN citas c ON d.id_cita = c.id_cita
            JOIN usuarios u ON d.id_veterinario = u.id_usuario
            WHERE c.id_mascota = ?
            ORDER BY d.fecha_registro DESC, d.version DESC
        """
        cursor.execute(query, (id_mascota,))
        rows = cursor.fetchall()
        conn.close()
        return rows
