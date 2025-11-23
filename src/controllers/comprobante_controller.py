from database.connection import get_db_connection
import os
from datetime import datetime


class ComprobanteController:
    """Controlador para generar comprobantes de citas en formato TXT.

    Método principal:
    - generar_comprobante_txt(id_cita, salida_dir=None) -> ruta_archivo o None
    Nota: se dejó interfaz compatible retornando la ruta del archivo generado.
    """

    @staticmethod
    def generar_comprobante_pdf(id_cita, salida_dir=None):
        """Compatibilidad: genera un TXT y devuelve su ruta (nombre termina en .txt)."""
        # internamente delegamos a la implementación TXT
        return ComprobanteController._generar_comprobante_txt(id_cita, salida_dir)

    @staticmethod
    def _generar_comprobante_txt(id_cita, salida_dir=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                c.id_cita,
                c.fecha_hora,
                c.fecha_fin,
                c.motivo,
                c.estado,
                m.id_mascota,
                m.nombre AS mascota,
                m.especie AS mascota_especie,
                p.id_propietario,
                p.nombre AS propietario,
                p.cedula AS propietario_cedula,
                u.id_usuario AS veterinario_id,
                u.nombre_completo AS veterinario,
                s.id_servicio,
                s.nombre AS servicio
            FROM citas c
            LEFT JOIN mascotas m ON c.id_mascota = m.id_mascota
            LEFT JOIN propietarios p ON m.id_propietario = p.id_propietario
            LEFT JOIN usuarios u ON c.id_veterinario = u.id_usuario
            LEFT JOIN servicios s ON c.id_servicio = s.id_servicio
            WHERE c.id_cita = ?
        """

        try:
            cursor.execute(query, (id_cita,))
            row = cursor.fetchone()
        except Exception as e:
            print(f"Error consultando cita para comprobante: {e}")
            row = None
        finally:
            conn.close()

        if not row:
            return None

        # Helper para sqlite3.Row o tuplas
        def _val(r, key, idx, default=''):
            try:
                return r[key]
            except Exception:
                try:
                    return r[idx]
                except Exception:
                    return default

        fecha_hora = _val(row, 'fecha_hora', 1)
        fecha_fin = _val(row, 'fecha_fin', 2)
        motivo = _val(row, 'motivo', 3)
        estado = _val(row, 'estado', 4)
        mascota = _val(row, 'mascota', 6)
        especie = _val(row, 'mascota_especie', 7)
        propietario = _val(row, 'propietario', 9)
        cedula = _val(row, 'propietario_cedula', 10)
        veterinario = _val(row, 'veterinario', 12)
        servicio = _val(row, 'servicio', 14)

        # preparar directorio de salida: por año/mes dentro de `comprobantes`
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        # Si no se recibe `salida_dir`, guardar dentro de la raíz del proyecto
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        base_root = salida_dir or os.path.join(project_root, 'comprobantes')
        base = os.path.join(base_root, year, month)
        try:
            os.makedirs(base, exist_ok=True)
        except Exception:
            pass

        filename = f"comprobante_cita_{id_cita}_{now.strftime('%Y%m%d%H%M%S')}.txt"
        ruta = os.path.join(base, filename)
        try:
            lines = [
                'COMPROBANTE DE CITA',
                f"Cita ID: {id_cita}",
                f"Propietario: {propietario} (Cédula: {cedula})",
                f"Mascota: {mascota} ({especie})",
                f"Servicio: {servicio}",
                f"Veterinario: {veterinario}",
                f"Fecha inicio: {fecha_hora}",
                f"Fecha fin: {fecha_fin}",
                f"Motivo: {motivo}",
                f"Estado: {estado}",
                '',
                f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            with open(ruta, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join(lines))
            return ruta
        except Exception as e:
            print(f"Error generando comprobante de texto: {e}")
            return None
