# main.py

import customtkinter as ctk
import sys
import os

# Asegurar que Python encuentre los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.auth_controller import AuthController
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.admission_view import AdmissionView 

# --- PLACEHOLDERS PARA FUTURAS VISTAS ---
class AppointmentView(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master)
        ctk.CTkLabel(self, text="MÓDULO DE CITAS PENDIENTE", font=("Roboto", 30)).pack(expand=True)
class HistoryView(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master)
        ctk.CTkLabel(self, text="MÓDULO DE HISTORIAL CLÍNICO PENDIENTE", font=("Roboto", 30)).pack(expand=True)
class ReportsView(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master)
        ctk.CTkLabel(self, text="MÓDULO DE REPORTES PENDIENTE", font=("Roboto", 30)).pack(expand=True)
# ----------------------------------------


# Mapeo de Vistas
VIEW_MAP = {
    "AdmissionView": AdmissionView,
    "AppointmentView": AppointmentView, 
    "HistoryView": HistoryView, 
    "ReportsView": ReportsView,
}


# Configuración global
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Integrado de Gestión Veterinaria")
        self.geometry("900x600")
        
        self.auth_controller = AuthController()
        self.dashboard_view = None 

        self.mostrar_login()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar_pantalla()
        LoginView(self, controller=self.auth_controller, on_login_success=self.navegar_a_dashboard).pack(fill="both", expand=True)

    def navegar_a_dashboard(self):
        self.limpiar_pantalla()
        
        usuario_data = self.auth_controller.usuario_actual
        if not usuario_data:
            return

        # 1. Crear el Dashboard y ASIGNARLO INMEDIATAMENTE A self.dashboard_view
        self.dashboard_view = DashboardView(
            self, 
            usuario=usuario_data.nombre, 
            rol=usuario_data.rol, 
            on_logout=self.cerrar_sesion,
            switch_module_callback=self.cambiar_modulo_principal 
        )
        # 2. Empaquetar el dashboard.
        self.dashboard_view.pack(fill="both", expand=True) 
        
        # 3. OBTENER EL MÓDULO INICIAL
        initial_module_key = self.determinar_modulo_inicial(usuario_data.rol)
        
        # 4. PASO CRÍTICO: Usar self.after() para cargar el módulo DESPUÉS de que Tkinter haya terminado de dibujar el Dashboard.
        if initial_module_key:
            # Ejecutar self.cambiar_modulo_principal(initial_module_key) después de 100ms
            self.after(100, lambda: self.cambiar_modulo_principal(initial_module_key)) 
            
    def determinar_modulo_inicial(self, rol):
        if rol == "Recepcionista":
            return "AdmissionView"
        elif rol == "Veterinario":
            return "HistoryView"
        elif rol == "Administrador":
            return "ReportsView" 
        return None


    def cambiar_modulo_principal(self, module_key):
        """
        Esta función recibe la clave del módulo y lo carga en el área principal del Dashboard.
        """
        if not self.dashboard_view:
            return 

        master_frame = self.dashboard_view.get_main_area()
        ViewClass = VIEW_MAP.get(module_key)
        
        if not ViewClass:
            return

        # Eliminar cualquier módulo anterior
        for widget in master_frame.winfo_children():
            widget.destroy()
        
        # Crear y empaquetar la nueva vista
        ViewClass(master_frame, self.auth_controller).pack(fill="both", expand=True)


    def cerrar_sesion(self):
        self.auth_controller.logout()
        self.mostrar_login()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
    
    