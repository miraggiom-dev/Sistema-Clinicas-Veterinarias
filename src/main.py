import customtkinter as ctk
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.schema_setup import create_tables 
from controllers.auth_controller import AuthController 

from controllers.farmaceuta_controller import FarmaceutaController 
from views.farmaceuta_view import FarmaceutaView 

from views.login_view import LoginView 
from views.dashboard_view import DashboardView
from views.admission_view import AdmissionView
from views.appointment_view import AppointmentView

class HistoryView(ctk.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):
        super().__init__(master)
        ctk.CTkLabel(self, text="MÓDULO DE HISTORIAL CLÍNICO PENDIENTE", font=("Roboto", 30)).pack(expand=True)

class ReportsView(ctk.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):
        super().__init__(master)
        ctk.CTkLabel(
            self, text="MÓDULO DE REPORTES PENDIENTE", font=("Roboto", 30)
        ).pack(expand=True)

VIEW_MAP = {
    "AdmissionView": AdmissionView,
    "AppointmentView": AppointmentView,
    "HistoryView": HistoryView,
    "ReportsView": ReportsView,
    "FarmaceutaView": FarmaceutaView, 
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
            # Cargar el módulo inicial poco después para asegurar que el dashboard esté listo
            self.after(100, lambda: self.cambiar_modulo_principal(initial_module_key))

    def determinar_modulo_inicial(self, rol):
        if rol == "Recepcionista":
            return "AdmissionView"
        elif rol == "Veterinario":
            return "HistoryView"
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

        # Llamada simple y explícita: pasamos id_mascota y active_tab como parámetros posicionales,
        # y el callback como último argumento.
        ViewClass(master_frame, self.auth_controller, id_mascota, active_tab, self.cambiar_modulo_principal).pack(fill="both", expand=True)


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