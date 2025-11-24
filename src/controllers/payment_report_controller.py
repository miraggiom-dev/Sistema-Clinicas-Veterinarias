from database.connection import get_db_connection
import os
from datetime import datetime

class PaymentReportController:

    @staticmethod
    def generar_informe_mensual(mes, anio, salida_dir=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        query_servicios = """
            SELECT 
                c.fecha_hora,
                'Servicio' as tipo,
                s.nombre as descripcion,
                p.nombre as cliente,
                s.precio_base as monto
            FROM citas c
            JOIN servicios s ON c.id_servicio = s.id_servicio
            JOIN mascotas m ON c.id_mascota = m.id_mascota
            JOIN propietarios p ON m.id_propietario = p.id_propietario
            WHERE strftime('%m', c.fecha_hora) = ? AND strftime('%Y', c.fecha_hora) = ?
            AND c.estado != 'Cancelada'
        """
        
        query_ventas = """
            SELECT 
                v.fecha_venta as fecha_hora,
                'Venta' as tipo,
                prod.nombre as descripcion,
                'Venta de Mostrador' as cliente,
                v.total_venta as monto
            FROM ventas v
            JOIN productos prod ON v.id_producto = prod.id_producto
            WHERE strftime('%m', v.fecha_venta) = ? AND strftime('%Y', v.fecha_venta) = ?
        """

        try:
            mes_str = f"{int(mes):02d}"
            anio_str = str(anio)
            
            cursor.execute(query_servicios, (mes_str, anio_str))
            servicios = cursor.fetchall()
            
            cursor.execute(query_ventas, (mes_str, anio_str))
            ventas = cursor.fetchall()
            
        except Exception as e:
            print(f"Error consultando pagos: {e}")
            return None
        finally:
            conn.close()

        todos_pagos = []
        
        for s in servicios:
            todos_pagos.append({
                'fecha': s['fecha_hora'],
                'tipo': s['tipo'],
                'descripcion': s['descripcion'],
                'cliente': s['cliente'],
                'monto': s['monto']
            })
            
        for v in ventas:
            todos_pagos.append({
                'fecha': v['fecha_hora'],
                'tipo': v['tipo'],
                'descripcion': v['descripcion'],
                'cliente': v['cliente'],
                'monto': v['monto']
            })
            
        todos_pagos.sort(key=lambda x: x['fecha'])

        if not todos_pagos:
            return None

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        base_root = salida_dir or os.path.join(project_root, 'informes_pagos')
        base = os.path.join(base_root, anio_str, mes_str)
        
        try:
            os.makedirs(base, exist_ok=True)
        except Exception:
            pass

        filename = f"informe_pagos_{anio_str}_{mes_str}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        ruta = os.path.join(base, filename)

        try:
            total_general = 0.0
            lines = [
                f"INFORME DE PAGOS MENSUAL - {mes_str}/{anio_str}",
                "=" * 60,
                f"{'FECHA':<20} | {'TIPO':<10} | {'DESCRIPCION':<25} | {'MONTO':>10}",
                "-" * 60
            ]
            
            for pago in todos_pagos:
                monto = float(pago['monto'])
                total_general += monto
                lines.append(f"{pago['fecha']:<20} | {pago['tipo']:<10} | {pago['descripcion']:<25} | {monto:>10.2f}")
            
            lines.append("-" * 60)
            lines.append(f"{'TOTAL GENERAL':<58} | {total_general:>10.2f}")
            lines.append("=" * 60)
            lines.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            with open(ruta, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join(lines))
            return ruta
        except Exception as e:
            print(f"Error generando informe de texto: {e}")
            return None
