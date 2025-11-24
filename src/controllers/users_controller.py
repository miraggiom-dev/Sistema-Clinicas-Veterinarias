from models.usuario_model import UsuarioModel

class UsersController:
    def __init__(self):
        self.model = UsuarioModel()

    def obtener_usuarios(self):
        return self.model.obtener_todos()

    def crear_usuario(self, nombre, rol, email, password):
        return self.model.crear(nombre, rol, email, password)