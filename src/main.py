from views.users_view import UsersView
from controllers.historial_diagnostico_controller import HistorialDiagnosticoController
from views.historial_diagnostico_view import HistorialDiagnosticoView
import customtkinter as ctk
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.schema_setup import create_tables 
from controllers.auth_controller import AuthController 
from controllers.farmaceuta_controller import FarmaceutaController 
from views.farmaceuta_view import FarmaceutaView 
from controllers.reporte_controller import ReporteController
from controllers.gestion_precios_controller import GestionPreciosController
from views.gestion_precios_view import GestionPreciosView
from controllers.service_controller import ServiceController
from views.service_view import ServiceView

from views.login_view import LoginView 
from views.dashboard_view import DashboardView
from views.admission_view import AdmissionView
from views.vet_history_view import VetHistoryView
from views.diagnosis_view import DiagnosisView
from views.treatment_view import TreatmentView
from views.medications_view import MedicationsView
from views.appointment_view import AppointmentView

# --- Vistas de ejemplo ---

from views.reporte_view import ReporteView
        
# --- MAPEO DE VISTAS ---

VIEW_MAP = {
    "AdmissionView": AdmissionView,
    "AppointmentView": AppointmentView,
    "VetHistoryView": VetHistoryView,
    "ReportsView": ReporteView,
    "FarmaceutaView": FarmaceutaView,
    "DiagnosisView": DiagnosisView,
    "TreatmentView": TreatmentView,
    "MedicationsView": MedicationsView,
    "UsersView": UsersView,
    "GestionPreciosView": GestionPreciosView,
    "ServiceView": ServiceView,
}


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")



class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Integrado de Gestión de Clínicas Veterinarias")
        self.geometry("900x600")

        self.auth_controller = AuthController() 
        self.farmaceuta_controller = FarmaceutaController()
        self.reporte_controller = ReporteController()
        self.gestion_precios_controller = GestionPreciosController()
        self.historial_diagnostico_controller = HistorialDiagnosticoController()
        from controllers.users_controller import UsersController
        self.users_controller = UsersController()
        self.service_controller = ServiceController()
        self.dashboard_view = None

        self.mostrar_login()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar_pantalla()
        LoginView(
            self,
            controller=self.auth_controller,
            on_login_success=self.navegar_a_dashboard,
        ).pack(fill="both", expand=True)

    def navegar_a_dashboard(self):
        self.limpiar_pantalla()

        usuario_data = self.auth_controller.usuario_actual
        if not usuario_data:
            return

        self.dashboard_view = DashboardView(
            self,
            usuario=usuario_data.nombre,
            rol=usuario_data.rol,
            on_logout=self.cerrar_sesion,
            switch_module_callback=self.cambiar_modulo_principal,
        )
        self.dashboard_view.pack(fill="both", expand=True)

        initial_module_key = self.determinar_modulo_inicial(usuario_data.rol)
        if initial_module_key:
            self.after(100, lambda: self.cambiar_modulo_principal(initial_module_key))

    def determinar_modulo_inicial(self, rol):
        if rol == "Recepcionista":
            return "AdmissionView"
        elif rol == "Veterinario":
            return "VetHistoryView"
        elif rol == "Administrador":
            return "ReportsView"
        elif rol == "Farmacéutico":
            return "FarmaceutaView"
        return None


    def cambiar_modulo_principal(self, module_key, id_mascota=None, active_tab=None):
        """
        Esta función recibe la clave del módulo y lo carga en el área principal del Dashboard.
        """
        if not self.dashboard_view:
            return

        master_frame = self.dashboard_view.get_main_area()
        ViewClass = VIEW_MAP.get(module_key)

        if not ViewClass:
            print(f"Error: Módulo {module_key} no encontrado en VIEW_MAP.")
            return

        for widget in master_frame.winfo_children():
            widget.destroy()
            



        # Determinar el controlador a usar basado en el módulo
        if module_key == "FarmaceutaView":
            controller_a_usar = self.farmaceuta_controller
        elif module_key == "ReportsView":
            controller_a_usar = self.reporte_controller
        elif module_key == "GestionPreciosView":
            controller_a_usar = self.gestion_precios_controller
        elif module_key == "HistorialDiagnosticoView":
            controller_a_usar = self.historial_diagnostico_controller
        elif module_key == "UsersView":
            controller_a_usar = self.users_controller
        elif module_key == "ServiceView":
            controller_a_usar = self.service_controller
        else:
            controller_a_usar = self.auth_controller

        # Pasar el controlador correcto
        ViewClass(
            master_frame, 
            controller_a_usar,
            id_mascota, 
            active_tab, 
            self.cambiar_modulo_principal
        ).pack(fill="both", expand=True)

    def cerrar_sesion(self):
        self.auth_controller.logout()
        self.mostrar_login()


if __name__ == "__main__":
    
    try:
        from database.schema_setup import create_tables
        create_tables()
    except ImportError:
        print("Advertencia: No se encontró database/schema_setup.py. Continuando sin inicialización de DB.")

    app = MainApp()
    app.mainloop()
