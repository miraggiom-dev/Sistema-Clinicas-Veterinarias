from database.connection import get_db_connection
import os
from datetime import datetime

class ProfitabilityReportController:
    """Controlador para generar informes de rentabilidad por tipo de servicio en formato TXT."""

    @staticmethod
    def generar_informe(mes, anio, tipo_servicio):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query para obtener citas del tipo especificado en el mes/año
        query = """
            SELECT 
                c.id_cita,
                c.fecha_hora,
                s.nombre as servicio_nombre,
                s.precio_base,
                p.nombre as propietario,
                m.nombre as mascota
            FROM citas c
            JOIN servicios s ON c.id_servicio = s.id_servicio
            JOIN mascotas m ON c.id_mascota = m.id_mascota
            JOIN propietarios p ON m.id_propietario = p.id_propietario
            WHERE strftime('%m', c.fecha_hora) = ? 
              AND strftime('%Y', c.fecha_hora) = ?
              AND s.tipo = ?
              AND c.estado != 'Cancelada'
            ORDER BY c.fecha_hora ASC
        """

        try:
            mes_str = f"{int(mes):02d}"
            anio_str = str(anio)
            
            cursor.execute(query, (mes_str, anio_str, tipo_servicio))
            rows = cursor.fetchall()
            
        except Exception as e:
            print(f"Error consultando rentabilidad: {e}")
            return None
        finally:
            conn.close()

        if not rows:
            return None

        # Generar archivo TXT
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        base_root = os.path.join(project_root, 'informes_rentabilidad')
        # Estructura: informes_rentabilidad/AÑO/MES/TIPO
        base = os.path.join(base_root, anio_str, mes_str, tipo_servicio)
        
        try:
            os.makedirs(base, exist_ok=True)
        except Exception:
            pass

        filename = f"reporte_{tipo_servicio}_{anio_str}_{mes_str}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        ruta = os.path.join(base, filename)

        try:
            total_ingresos = 0.0
            lines = [
                f"INFORME DE RENTABILIDAD - {tipo_servicio.upper()}",
                f"PERIODO: {mes_str}/{anio_str}",
                "=" * 80,
                f"{'ID':<5} | {'FECHA':<20} | {'SERVICIO':<25} | {'CLIENTE':<20} | {'MONTO':>10}",
                "-" * 80
            ]
            
            for r in rows:
                monto = float(r['precio_base'])
                total_ingresos += monto
                lines.append(f"{r['id_cita']:<5} | {r['fecha_hora']:<20} | {r['servicio_nombre']:<25} | {r['propietario']:<20} | {monto:>10.2f}")
            
            lines.append("-" * 80)
            lines.append(f"{'TOTAL INGRESOS':<73} | {total_ingresos:>10.2f}")
            lines.append(f"{'CANTIDAD DE CITAS':<73} | {len(rows):>10}")
            lines.append("=" * 80)
            lines.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            with open(ruta, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join(lines))
            return ruta
        except Exception as e:
            print(f"Error generando informe de rentabilidad: {e}")
            return None
