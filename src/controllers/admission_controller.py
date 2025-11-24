import models.propietario_model
import models.mascota_model

class AdmissionController:
    
    def registrar_nuevo_cliente(self, cedula, nombre, telefono, email, direccion): 

        if not cedula or not nombre:
            return None
        return models.propietario_model.PropietarioModel.crear(cedula, nombre, telefono, email, direccion)

    def registrar_mascota(self, id_propietario, nombre, especie, raza, nacimiento, genero):

        if not id_propietario or not nombre or not especie:
            return False
        return models.mascota_model.MascotaModel.crear(id_propietario, nombre, especie, raza, nacimiento, genero)

    def buscar_clientes(self, texto_busqueda):

        return models.propietario_model.PropietarioModel.buscar_por_nombre(texto_busqueda)

    def obtener_mascotas_cliente(self, id_propietario):
        return models.mascota_model.MascotaModel.obtener_por_propietario(id_propietario)

    def actualizar_cliente(self, id_propietario, nombre=None, telefono=None, email=None, direccion=None):
 
        return models.propietario_model.PropietarioModel.actualizar(id_propietario, nombre=nombre, telefono=telefono, email=email, direccion=direccion)

    def enviar_recordatorio_mascota(self, id_propietario, id_mascota):
        
        return True, "Recordatorio enviado correctamente."