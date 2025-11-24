import customtkinter as ctk
from views.comprobante_view import ComprobanteView


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, usuario, rol, on_logout, switch_module_callback):
        super().__init__(master)
        self.on_logout = on_logout
        self.switch_module_callback = switch_module_callback
        self.rol = rol

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.crear_sidebar_widgets(usuario, rol)
        self.crear_menu_opciones()

    def crear_sidebar_widgets(self, usuario, rol):
        self.lbl_logo = ctk.CTkLabel(
            self.sidebar, text="VET SYSTEM", font=("Roboto", 20, "bold")
        )
        self.lbl_logo.pack(pady=20, padx=20)

        self.lbl_user = ctk.CTkLabel(
            self.sidebar, text=f"Hola, {usuario}\n({rol})", font=("Arial", 14)
        )
        self.lbl_user.pack(pady=(10, 30))

        self.menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.menu_frame.pack(fill="x", padx=10)

        self.btn_salir = ctk.CTkButton(
            self.sidebar,
            text="Cerrar Sesión",
            command=self.on_logout,
            fg_color="darkred",
        )
        self.btn_salir.pack(side="bottom", pady=20)

    def crear_menu_opciones(
        self,
    ):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        opciones = []
        if self.rol == "Recepcionista":
            opciones = [("Admisión", "AdmissionView"), ("Citas", "AppointmentView"), ("Comprobante", "ComprobanteView")] 
        elif self.rol == "Veterinario":
            opciones = [
                ("Historial Clínico", "VetHistoryView"),
                ("Citas", "AppointmentView"),
                ("Diagnósticos", "DiagnosisView"),
                ("Tratamientos", "TreatmentView"),
                ("Medicamentos", "MedicationsView"),
            ]
        elif self.rol == "Administrador":
            opciones = [
                ("Reportes", "ReportsView"),
                ("Gestión de Precios", "GestionPreciosView"),
                ("Usuarios", "UsersView"),
                ("Servicios", "ServiceView")
            ]
        elif self.rol == "Farmacéutico":
            opciones = [("Farmacia", "FarmaceutaView")]
        else:
            opciones = [("Admisión", "AdmissionView")]

        for nombre, view_key in opciones:
            if view_key == 'ComprobanteView':
                cmd = lambda n=nombre: ComprobanteView(self)
            else:
                cmd = lambda key=view_key: self.switch_module_callback(key)
            btn = ctk.CTkButton(self.menu_frame, text=nombre, fg_color="transparent", border_width=1,
                                command=cmd)
            btn.pack(fill="x", pady=5, padx=10)

    def get_main_area(self):
        """Retorna el frame principal donde se cargan los módulos."""
        return self.main_area
