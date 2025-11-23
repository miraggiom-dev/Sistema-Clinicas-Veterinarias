from database.connection import get_db_connection
from datetime import datetime

class DiagnosticoModel:
    
    @staticmethod
    def obtener_actual_por_cita(id_cita):
        """Obtiene la versión vigente del diagnóstico de una cita."""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM diagnosticos WHERE id_cita = ? AND es_actual = 1"
        cursor.execute(query, (id_cita,))
        result = cursor.fetchone()
        conn.close()
        return result

    @staticmethod
    def guardar_diagnostico(id_cita, id_veterinario, diagnostico_texto, tratamiento, observacion=""):
        """
        Maneja la lógica de versionado:
        1. Si no existe, crea versión 1.
        2. Si existe, desactiva el anterior y crea versión N+1.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute("SELECT id_diagnostico, version FROM diagnosticos WHERE id_cita = ? AND es_actual = 1", (id_cita,))
            diagnostico_previo = cursor.fetchone()

            nuevo_version = 1

            if diagnostico_previo:

                cursor.execute("UPDATE diagnosticos SET es_actual = 0 WHERE id_diagnostico = ?", (diagnostico_previo['id_diagnostico'],))
                
                nuevo_version = diagnostico_previo['version'] + 1
            
            query_insert = """
                INSERT INTO diagnosticos (id_cita, id_veterinario, version, diagnostico, tratamiento, observacion_edicion, fecha_registro, es_actual)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """
            cursor.execute(query_insert, (id_cita, id_veterinario, nuevo_version, diagnostico_texto, tratamiento, observacion, fecha_hoy))
            
            conn.commit()
            print(f"Diagnóstico guardado. Versión: {nuevo_version}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error guardando diagnóstico: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def obtener_historial_completo(id_cita):
        """Para auditoría: Ver todos los cambios de un diagnóstico."""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM diagnosticos WHERE id_cita = ? ORDER BY version DESC"
        cursor.execute(query, (id_cita,))
        historial = cursor.fetchall()
        conn.close()
        return historial