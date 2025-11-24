import customtkinter as ctk
from controllers.alerts_controller import AlertsController 

class AlertsView(ctk.CTkFrame):
    
    def __init__(self, master, controller=None, id_mascota=None, active_tab=None, switch_callback=None, **kwargs):
        super().__init__(master, **(kwargs or {}))
        
        self.controller = AlertsController()
        
        try: self.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        except: pass

        self.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self, text="Alertas de Inactividad", font=("Arial", 16, "bold")).pack(anchor="w", pady=10)
        
        self.lbl_status = ctk.CTkLabel(self, text="Cargando...", text_color="gray")
        self.lbl_status.pack(anchor="w")

        self.scroll = ctk.CTkScrollableFrame(self, label_text="Mascotas")
        self.scroll.pack(fill="both", expand=True, pady=10)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="Refrescar", command=self.cargar_datos).pack(side="left", padx=5)
        
        self.cargar_datos()

    def cargar_datos(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        self.lbl_status.configure(text="Consultando base de datos...", text_color="blue")
        self.update_idletasks()

        lista_alertas = self.controller.obtener_alertas()

        if not lista_alertas:
            self.lbl_status.configure(text="Todo en orden. No hay alertas.", text_color="green")
            return

        self.lbl_status.configure(text=f"Se encontraron {len(lista_alertas)} mascotas inactivas.", text_color="orange")

        for item in lista_alertas:
            self._crear_fila(item)

    def _crear_fila(self, item):
        f = ctk.CTkFrame(self.scroll)
        f.pack(fill="x", pady=5, padx=5)
        
        info = f"{item['mascota']} (Dueño: {item['propietario']}) | Última: {item['ultima_visita']} | Hace {item['dias_ausente']} días"
        
        ctk.CTkLabel(f, text=info, anchor="w").pack(side="left", padx=10, fill="x", expand=True)
        
        def action():
            ok, msg = self.controller.enviar_recordatorio(item['id_propietario'], item['id_mascota'])
            self.lbl_status.configure(text=msg, text_color="green" if ok else "red")

        ctk.CTkButton(f, text="Enviar Aviso", width=100, command=action).pack(side="right", padx=10)