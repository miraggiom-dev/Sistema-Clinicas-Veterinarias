from models.diagnostico_model import DiagnosticoModel
from models.mascota_model import MascotaModel
from models.usuario_model import UsuarioModel


class DiagnosisController:
    @staticmethod
    def registrar_diagnostico(
        id_cita, id_veterinario, diagnostico, tratamiento, observacion="", firma=None
    ):
        # Para compatibilidad, sin firma
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
    def obtener_diagnosticos_por_mascota(id_mascota):
        # Devuelve todos los diagnósticos de una mascota
        # Se asume que hay una relación entre mascota -> cita -> diagnostico
        # Aquí deberías obtener todas las citas de la mascota y luego los diagnósticos
        # Por simplicidad, se asume que DiagnosticoModel puede obtener por id_mascota
        # Si no, habría que hacer join con citas
        pass

    @staticmethod
    def obtener_historial_diagnostico(id_cita):
        return DiagnosticoModel.obtener_historial_completo(id_cita)
