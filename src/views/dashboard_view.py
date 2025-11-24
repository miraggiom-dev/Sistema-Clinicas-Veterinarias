import customtkinter as ctk
from views.comprobante_view import ComprobanteView
from views.payment_report_view import PaymentReportView
from views.service_view import ServiceView
from views.profitability_report_view import ProfitabilityReportView


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, usuario, rol, on_logout, switch_module_callback):
        super().__init__(master)
        self.on_logout = on_logout
        self.switch_module_callback = switch_module_callback
        self.rol = rol
        self.active_button = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Enhanced sidebar with darker background
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Main area with subtle background
        self.main_area = ctk.CTkFrame(self, fg_color="#242424", corner_radius=10)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

        self.crear_sidebar_widgets(usuario, rol)
        self.crear_menu_opciones()

    def crear_sidebar_widgets(self, usuario, rol):
        # Logo section
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="#2a2a2a", corner_radius=10)
        logo_frame.pack(pady=25, padx=15, fill="x")
        
        self.lbl_logo = ctk.CTkLabel(
            logo_frame, 
            text="VET CLINIC", 
            font=("Roboto", 20, "bold"),
            text_color="#4a9eff",
            wraplength=180
        )
        self.lbl_logo.pack(pady=15)

        # User info card
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="#252525", corner_radius=8)
        user_frame.pack(pady=(10, 25), padx=15, fill="x")
        
        self.lbl_user = ctk.CTkLabel(
            user_frame, 
            text=f"{usuario}", 
            font=("Roboto", 14, "bold"),
            text_color="white",
            wraplength=180
        )
        self.lbl_user.pack(pady=(10, 2))
        
        ctk.CTkLabel(
            user_frame, 
            text=f"{rol}", 
            font=("Roboto", 11),
            text_color="#888888",
            wraplength=180
        ).pack(pady=(0, 10))

        # Menu section label
        ctk.CTkLabel(
            self.sidebar,
            text="MENÚ",
            font=("Roboto", 11, "bold"),
            text_color="#666666"
        ).pack(anchor="w", padx=20, pady=(5, 10))

        self.menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.menu_frame.pack(fill="both", expand=True, padx=10)

        # Logout button at bottom
        self.btn_salir = ctk.CTkButton(
            self.sidebar,
            text="Cerrar Sesión",
            command=self.on_logout,
            fg_color="#8b0000",
            hover_color="#a00000",
            height=40,
            corner_radius=8,
            font=("Roboto", 12, "bold")
        )
        self.btn_salir.pack(side="bottom", pady=20, padx=15, fill="x")

    def crear_menu_opciones(self):
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
                #("Medicamentos", "MedicationsView"),
            ]
        elif self.rol == "Administrador":
            opciones = [
                ("Informes de Rentabilidad", "ProfitabilityReportView"),
                ("Gestión de Precios", "GestionPreciosView"),
                ("Usuarios", "UsersView"),
                ("Servicios", "ServiceView"),
                ("Informes de Pagos", "PaymentReportView")
            ]
        elif self.rol == "Farmacéutico":
            opciones = [("Farmacia", "FarmaceutaView")]
        else:
            opciones = [("Admisión", "AdmissionView")]

        for nombre, view_key in opciones:
            if view_key == 'ComprobanteView':
                cmd = lambda n=nombre: ComprobanteView(self)
            elif view_key == 'PaymentReportView':
                cmd = lambda n=nombre: PaymentReportView(self)
            elif view_key == 'ProfitabilityReportView':
                cmd = lambda n=nombre: ProfitabilityReportView(self)
            else:
                cmd = lambda key=view_key, btn_name=nombre: self.switch_module_with_highlight(key, btn_name)
            
            btn = ctk.CTkButton(
                self.menu_frame, 
                text=nombre, 
                fg_color="transparent",
                hover_color="#2a2a2a",
                text_color="#cccccc",
                anchor="center",
                height=42,
                corner_radius=8,
                font=("Roboto", 12),
                command=cmd
            )
            btn.pack(fill="x", pady=3, padx=5)
            btn._view_key = view_key  # Store for later reference

    def switch_module_with_highlight(self, view_key, btn_name):
        """Switch module and highlight the active button"""
        # Reset all buttons
        for widget in self.menu_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(fg_color="transparent", text_color="#cccccc")
        
        # Highlight active button
        for widget in self.menu_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and hasattr(widget, '_view_key') and widget._view_key == view_key:
                widget.configure(fg_color="#2a5a8a", text_color="white")
                break
        
        self.switch_module_callback(view_key)

    def get_main_area(self):
        """Retorna el frame principal donde se cargan los módulos."""
        return self.main_area
