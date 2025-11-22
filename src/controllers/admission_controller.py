
import models.propietario_model
import models.mascota_model

class AdmissionController:
    
    def registrar_nuevo_cliente(self, cedula, nombre, telefono, email, direccion): # <-- NUEVO PARÁMETRO
        """Registra un cliente y retorna su ID o None si falló"""
        if not cedula or not nombre:
            return None
        # Pasamos la cédula al modelo
        return models.propietario_model.PropietarioModel.crear(cedula, nombre, telefono, email, direccion)

    def registrar_mascota(self, id_propietario, nombre, especie, raza, nacimiento, genero):
        """Agrega una mascota a un cliente existente"""
        if not id_propietario or not nombre or not especie:
            return False
        return models.mascota_model.MascotaModel.crear(id_propietario, nombre, especie, raza, nacimiento, genero)

    def buscar_clientes(self, texto_busqueda):
        """Filtra clientes por nombre o cédula"""
        return models.propietario_model.PropietarioModel.buscar_por_nombre(texto_busqueda)

    def obtener_mascotas_cliente(self, id_propietario):
        return models.mascota_model.MascotaModel.obtener_por_propietario(id_propietario)