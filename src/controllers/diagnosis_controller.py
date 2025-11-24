from models.diagnostico_model import DiagnosticoModel

class DiagnosisController:
    @staticmethod
    def registrar_diagnostico(
        id_cita, id_veterinario, diagnostico, tratamiento, observacion="", firma=None
    ):
        return DiagnosticoModel.guardar_diagnostico(
            id_cita, id_veterinario, diagnostico, tratamiento, observacion, firma
        )

    @staticmethod
    def registrar_diagnostico_firmado(
        id_cita, id_veterinario, diagnostico, tratamiento, observacion, firma
    ):
        return DiagnosticoModel.guardar_diagnostico(
            id_cita, id_veterinario, diagnostico, tratamiento, observacion, firma
        )

    @staticmethod
    def obtener_historial_diagnostico(id_cita):
        return DiagnosticoModel.obtener_historial_completo(id_cita)
