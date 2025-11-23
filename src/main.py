import customtkinter as ctk
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.schema_setup import create_tables 
from controllers.auth_controller import AuthController

from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.admission_view import AdmissionView
from views.vet_history_view import VetHistoryView
from views.diagnosis_view import DiagnosisView
from views.treatment_view import TreatmentView
from views.medications_view import MedicationsView


class AppointmentView(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master)
        ctk.CTkLabel(self, text="MÓDULO DE CITAS PENDIENTE", font=("Roboto", 30)).pack(
            expand=True
        )


class ReportsView(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master)
        ctk.CTkLabel(
            self, text="MÓDULO DE REPORTES PENDIENTE", font=("Roboto", 30)
        ).pack(expand=True)


# ----------------------------------------


# Mapeo de Vistas
VIEW_MAP = {
    "AdmissionView": AdmissionView,
    "AppointmentView": AppointmentView,
    "VetHistoryView": VetHistoryView,
    "ReportsView": ReportsView,
    "DiagnosisView": DiagnosisView,
    "TreatmentView": TreatmentView,
    "MedicationsView": MedicationsView,
}


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Integrado de Gestión de Clínicas Veterinarias")
        self.geometry("900x600")

        self.auth_controller = AuthController()
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
            self.after(100, self._iniciar_modulo_diferido, initial_module_key)

    def _iniciar_modulo_diferido(self, initial_module_key):
        self.cambiar_modulo_principal(initial_module_key)

    def determinar_modulo_inicial(self, rol):
        if rol == "Recepcionista":
            return "AdmissionView"
        elif rol == "Veterinario":
            return "VetHistoryView"
        elif rol == "Administrador":
            return "ReportsView"
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
            return

        for widget in master_frame.winfo_children():
            widget.destroy()

        # Llamada simple y explícita: pasamos id_mascota y active_tab como parámetros posicionales,
        # y el callback como último argumento.
        ViewClass(master_frame, self.auth_controller, id_mascota, active_tab, self.cambiar_modulo_principal).pack(fill="both", expand=True)

        usuario_data = self.auth_controller.usuario_actual

        if module_key == "VetHistoryView" and usuario_data:
            ViewClass(master_frame, usuario_data.nombre, usuario_data.rol).pack(
                fill="both", expand=True
            )
        elif module_key in ["DiagnosisView", "TreatmentView", "MedicationsView"]:
            ViewClass(master_frame).pack(fill="both", expand=True)
        else:
            ViewClass(master_frame, self.auth_controller).pack(fill="both", expand=True)

    def cerrar_sesion(self):
        self.auth_controller.logout()
        self.mostrar_login()


if __name__ == "__main__":
    # --- LLAMADO CRÍTICO: Inicialización de la Base de Datos ---
    create_tables()
    # -----------------------------------------------------------

    app = MainApp()
    app.mainloop()
