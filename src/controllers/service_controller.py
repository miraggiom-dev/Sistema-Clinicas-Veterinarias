from models.servicio_model import ServicioModel

class ServiceController:
    def __init__(self):
        pass

    def obtener_servicios(self, activos_only=False):
        """Obtiene todos los servicios."""
        return ServicioModel.obtener_todos(activos_only=activos_only)

    def crear_servicio(self, nombre, tipo, precio_base, costo_mano_obra, duracion_estimada):
        """Crea un nuevo servicio."""
        try:
            precio_base = float(precio_base)
        except ValueError:
            precio_base = 0.0
        
        try:
            costo_mano_obra = float(costo_mano_obra)
        except ValueError:
            costo_mano_obra = 0.0
            
        try:
            duracion_estimada = int(duracion_estimada)
        except ValueError:
            duracion_estimada = 30

        return ServicioModel.crear(nombre, tipo, precio_base, costo_mano_obra, duracion_estimada)

    def actualizar_servicio(self, id_servicio, nombre, tipo, precio_base, costo_mano_obra, duracion_estimada, activo=True):
        """Actualiza un servicio existente."""
        try:
            precio_base = float(precio_base)
        except ValueError:
            precio_base = 0.0
        
        try:
            costo_mano_obra = float(costo_mano_obra)
        except ValueError:
            costo_mano_obra = 0.0
            
        try:
            duracion_estimada = int(duracion_estimada)
        except ValueError:
            duracion_estimada = 30

        return ServicioModel.actualizar(
            id_servicio, 
            nombre=nombre, 
            tipo=tipo,
            precio_base=precio_base, 
            costo_mano_obra=costo_mano_obra, 
            duracion_estimada=duracion_estimada,
            activo=activo
        )

    def eliminar_servicio(self, id_servicio):
        """Elimina (desactiva) un servicio."""
        return ServicioModel.eliminar(id_servicio)

    def reactivar_servicio(self, id_servicio):
        """Reactiva un servicio."""
        return ServicioModel.reactivar(id_servicio)
