from models.diagnostico_model import DiagnosticoModel

class HistorialDiagnosticoController:
    def __init__(self):
        self.model = DiagnosticoModel()

    def obtener_historial_completo(self, id_cita):
        return self.model.obtener_historial_completo(id_cita)
