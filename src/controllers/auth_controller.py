from models.usuario_model import UsuarioModel

class AuthController:
    def __init__(self):
        self.usuario_actual = None  # Aquí guardaremos quién inició sesión

    def login(self, email, password):

        usuario = UsuarioModel.autenticar(email, password)
        
        if usuario:
            self.usuario_actual = usuario
            print(f"Sesión iniciada: {usuario.nombre} ({usuario.rol})")
            return True
        else:
            self.usuario_actual = None
            print("Fallo de autenticación: Credenciales incorrectas")
            return False

    def logout(self):
        self.usuario_actual = None

    def obtener_rol_actual(self):
        if self.usuario_actual:
            return self.usuario_actual.rol
        return None