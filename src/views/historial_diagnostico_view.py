import customtkinter as ctk

class HistorialDiagnosticoView(ctk.CTkFrame):
    def __init__(self, master, controller, id_cita=None, active_tab=None, switch_module_callback=None, **kwargs):
        
        super().__init__(master, **kwargs)
        
        self.controller = controller
        self.id_cita = id_cita
        self.switch_module_callback = switch_module_callback
        
        ctk.CTkLabel(self, text="Historial de Cambios en Diagnóstico", font=("Roboto", 24, "bold")).pack(pady=10)
        
        self.tabla = ctk.CTkFrame(self)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)
        
        if id_cita:
            self.mostrar_historial(id_cita)
        else:
            ctk.CTkLabel(self.tabla, text="Seleccione una cita para ver el historial.").pack()

    def mostrar_historial(self, id_cita):
       
        historial = self.controller.obtener_historial_completo(id_cita)
       
        if not historial:
            ctk.CTkLabel(self.tabla, text="No hay historial para esta cita.").pack()
            return
        
        headers = ["Versión", "Diagnóstico", "Tratamiento", "Observación", "Fecha", "Veterinario"]
        
        for col, h in enumerate(headers):
           
            ctk.CTkLabel(self.tabla, text=h, font=("Roboto", 12, "bold")).grid(row=0, column=col, padx=5, pady=2)
        
        for i, diag in enumerate(historial, start=1):
           
            ctk.CTkLabel(self.tabla, text=str(diag['version'])).grid(row=i, column=0)
            ctk.CTkLabel(self.tabla, text=diag['diagnostico']).grid(row=i, column=1)
            ctk.CTkLabel(self.tabla, text=diag['tratamiento']).grid(row=i, column=2)
            ctk.CTkLabel(self.tabla, text=diag['observacion_edicion']).grid(row=i, column=3)
            ctk.CTkLabel(self.tabla, text=diag['fecha_registro']).grid(row=i, column=4)
            ctk.CTkLabel(self.tabla, text=diag['id_veterinario']).grid(row=i, column=5)
