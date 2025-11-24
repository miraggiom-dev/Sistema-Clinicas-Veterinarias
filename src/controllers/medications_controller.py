from models.producto_model import ProductoModel
from models.receta_model import RecetaModel


class MedicationsController:
    @staticmethod
    def prescribir_medicamento(id_diagnostico, id_producto, cantidad):
        if ProductoModel.verificar_stock(id_producto, cantidad):
            exito = RecetaModel.crear(id_diagnostico, id_producto, cantidad)
            if exito:
                ProductoModel.descontar_stock(id_producto, cantidad)
                return True
        return False

    @staticmethod
    def obtener_recetas_por_diagnostico(id_diagnostico):
        return RecetaModel.obtener_por_diagnostico(id_diagnostico)
