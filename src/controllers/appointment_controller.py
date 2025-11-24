from datetime import datetime, timedelta
from models.cita_model import CitaModel
from models.usuario_model import UsuarioModel
from models.servicio_model import ServicioModel

class AppointmentController:
    def obtener_veterinarios(self):
        users = UsuarioModel.obtener_todos()
        vets = []
        if users:
            for u in users:
                rol = ""
                try: rol = u['rol']
                except: rol = getattr(u, 'rol', '')

                if str(rol).strip().lower() == 'veterinario':
                    uid, nombre = None, None
                    try: uid = u['id_usuario']
                    except: uid = getattr(u, 'id_usuario', None)
                    try: nombre = u['nombre_completo']
                    except: nombre = getattr(u, 'nombre_completo', None)
                        
                    if uid and nombre:
                        vets.append((uid, nombre))
        return vets

    def obtener_servicios(self):
        raw = ServicioModel.obtener_todos(True) or []
        servicios = []
        for r in raw:
            s_dict = {}
            try:
                s_dict['id_servicio'] = r['id_servicio']
                s_dict['nombre'] = r['nombre']
                try: s_dict['duracion_estimada'] = r['duracion_estimada']
                except: s_dict['duracion_estimada'] = 30
            except:
                try:
                    s_dict['id_servicio'] = r[0]
                    s_dict['nombre'] = r[1]
                    s_dict['duracion_estimada'] = r[4] if len(r) > 4 else 30
                except: continue
            servicios.append(s_dict)
        return servicios

    def buscar_citas_dia(self, fecha_str):
        if not fecha_str: return []
        citas = CitaModel.obtener_agenda_del_dia(fecha_str)
        return citas if citas else []

    def cambiar_estado_cita(self, id_cita, nuevo_estado):
        if not id_cita: return False
        return CitaModel.actualizar_estado(id_cita, nuevo_estado)

    def agendar_cita(self, id_mascota, id_vet, id_servicio, fecha_base, hora, minuto, duracion_min, motivo):
        if not all([id_mascota, id_vet, id_servicio, fecha_base]):
            return False, "Faltan datos obligatorios."

        try:
            fecha_str = f"{fecha_base} {hora}:{minuto}:00"
            dt_inicio = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
            d_min = int(duracion_min) if duracion_min else 30
            dt_fin = dt_inicio + timedelta(minutes=d_min)
            
            str_inicio = dt_inicio.strftime('%Y-%m-%d %H:%M:%S')
            str_fin = dt_fin.strftime('%Y-%m-%d %H:%M:%S')
            
            resultado = CitaModel.agendar(id_mascota, id_vet, id_servicio, str_inicio, str_fin, motivo)
            
            if isinstance(resultado, tuple): return resultado
            elif isinstance(resultado, bool): return resultado, "Cita agendada." if resultado else "Error en BD."
            else: return False, "Respuesta inesperada."
                
        except ValueError: return False, "Formato de fecha inválido."
        except Exception as e: return False, f"Error: {str(e)}"

    def editar_cita_logica(self, id_cita, id_vet, id_servicio, fecha_base, hora, minuto, duracion_min, motivo):
        try:
            fecha_str = f"{fecha_base} {hora}:{minuto}:00"
            dt_inicio = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
            
            d_min = int(duracion_min) if duracion_min else 30
            dt_fin = dt_inicio + timedelta(minutes=d_min)
            
            str_inicio = dt_inicio.strftime('%Y-%m-%d %H:%M:%S')
            str_fin = dt_fin.strftime('%Y-%m-%d %H:%M:%S')

            try:
                resultado = CitaModel.modificar(id_cita, id_vet, id_servicio, str_inicio, str_fin, motivo)
            except TypeError:
                resultado = CitaModel.modificar(id_cita, id_vet, str_inicio, str_fin, motivo)
            
            if isinstance(resultado, tuple): return resultado
            return bool(resultado), "Cita modificada." if resultado else "Error al modificar."
        except Exception as e:
            return False, f"Error: {str(e)}"