from datetime import datetime, timedelta
from models.cita_model import CitaModel
from controllers.admission_controller import AdmissionController

class AlertsController:
    def __init__(self):
        self.admission_controller = AdmissionController()
        self._six_months = timedelta(days=182)

    def obtener_alertas(self):
        """
        Busca todas las mascotas y filtra las que no han venido en 6 meses.
        Retorna una lista de diccionarios lista para usar en la vista.
        """
        alertas = []
        
        clientes = self.admission_controller.buscar_clientes("") or []
        
        for c in clientes:

            try: pid = c['id_propietario']; pnom = c['nombre']
            except: pid = getattr(c, 'id_propietario', None); pnom = getattr(c, 'nombre', 'Cliente')
            
            if not pid: continue

            mascotas = self.admission_controller.obtener_mascotas_cliente(pid) or []
            
            for m in mascotas:
                try: mid = m['id_mascota']; mnom = m['nombre']
                except: mid = getattr(m, 'id_mascota', None); mnom = getattr(m, 'nombre', 'Mascota')
                
                if not mid: continue

                ultima_fecha = self._calcular_ultima_visita(mid)
                
                if not ultima_fecha:
                    continue

                tiempo_sin_venir = datetime.now() - ultima_fecha
                
                if tiempo_sin_venir >= self._six_months:
                    alertas.append({
                        "id_propietario": pid,
                        "propietario": pnom,
                        "id_mascota": mid,
                        "mascota": mnom,
                        "ultima_visita": ultima_fecha.strftime("%Y-%m-%d"),
                        "dias_ausente": tiempo_sin_venir.days
                    })
        
        return alertas

    def _calcular_ultima_visita(self, id_mascota):
        """Obtiene el historial desde el Modelo y devuelve un objeto datetime o None."""
        try:
            rows = CitaModel.obtener_historial_mascota(id_mascota)
            if not rows: return None

            for r in rows:
                try: 
                    estado = r['estado']
                    fecha_raw = r['fecha_hora']
                except: 
                    fecha_raw = r[0]
                    estado = r[1] if len(r) > 1 else 'Realizada'

                if str(estado).strip().lower() == 'realizada':
                    fecha_limpia = str(fecha_raw).split('.')[0].strip()
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                        try: return datetime.strptime(fecha_limpia, fmt)
                        except: continue
            return None
        except Exception as e:
            print(f"Error calculando visita: {e}")
            return None

    def enviar_recordatorio(self, id_prop, id_masc):
        return self.admission_controller.enviar_recordatorio_mascota(id_prop, id_masc)