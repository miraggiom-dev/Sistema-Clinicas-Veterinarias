
import customtkinter as ctk
from tkinter import filedialog, messagebox
import datetime

class ReporteView(ctk.CTkFrame):
    def __init__(self, master, controller, id_mascota=None, active_tab=None, switch_module_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.switch_module_callback = switch_module_callback
        ctk.CTkLabel(self, text="Reportes Administrativos", font=("Roboto", 28, "bold")).pack(pady=10)


        # Sección de rentabilidad por especialidad
        self.frame_rentabilidad = ctk.CTkFrame(self)
        self.frame_rentabilidad.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.frame_rentabilidad, text="Rentabilidad por Especialidad", font=("Roboto", 18)).grid(row=0, column=0, columnspan=4, pady=5)
        ctk.CTkLabel(self.frame_rentabilidad, text="Desde (YYYY-MM-DD):").grid(row=1, column=0, sticky="e")
        ctk.CTkLabel(self.frame_rentabilidad, text="Hasta (YYYY-MM-DD):").grid(row=2, column=0, sticky="e")
        self.var_inicio = ctk.StringVar()
        self.var_fin = ctk.StringVar()
        self.entry_inicio = ctk.CTkEntry(self.frame_rentabilidad, textvariable=self.var_inicio, width=100)
        self.entry_inicio.grid(row=1, column=1, padx=5, pady=2)
        self.entry_fin = ctk.CTkEntry(self.frame_rentabilidad, textvariable=self.var_fin, width=100)
        self.entry_fin.grid(row=2, column=1, padx=5, pady=2)
        self.btn_rentabilidad = ctk.CTkButton(self.frame_rentabilidad, text="Ver Rentabilidad", command=self.mostrar_rentabilidad)
        self.btn_rentabilidad.grid(row=3, column=0, columnspan=2, pady=8)
        self.tabla_rentabilidad = ctk.CTkFrame(self.frame_rentabilidad)
        self.tabla_rentabilidad.grid(row=4, column=0, columnspan=4, pady=5)

        # Sección de exportación de ingresos
        self.frame_export = ctk.CTkFrame(self)
        self.frame_export.pack(pady=20, padx=20, fill="x")
        ctk.CTkLabel(self.frame_export, text="Exportar Ingresos Mensuales", font=("Roboto", 18)).grid(row=0, column=0, columnspan=2, pady=5)
        ctk.CTkLabel(self.frame_export, text="Mes:").grid(row=1, column=0, sticky="e")
        ctk.CTkLabel(self.frame_export, text="Año:").grid(row=2, column=0, sticky="e")
        self.var_mes = ctk.StringVar(value=str(datetime.datetime.now().month))
        self.var_anio = ctk.StringVar(value=str(datetime.datetime.now().year))
        self.entry_mes = ctk.CTkEntry(self.frame_export, textvariable=self.var_mes, width=60)
        self.entry_mes.grid(row=1, column=1, padx=5, pady=2)
        self.entry_anio = ctk.CTkEntry(self.frame_export, textvariable=self.var_anio, width=60)
        self.entry_anio.grid(row=2, column=1, padx=5, pady=2)
        self.btn_exportar = ctk.CTkButton(self.frame_export, text="Exportar a TXT", command=self.exportar_ingresos_txt)
        self.btn_exportar.grid(row=3, column=0, columnspan=2, pady=10)

    def mostrar_rentabilidad(self):
        for widget in self.tabla_rentabilidad.winfo_children():
            widget.destroy()
        inicio = self.var_inicio.get().strip() or None
        fin = self.var_fin.get().strip() or None
        resultados = self.controller.rentabilidad_por_especialidad(inicio, fin)
        headers = ["Especialidad", "Cantidad", "Total ($)"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.tabla_rentabilidad, text=h, font=("Roboto", 12, "bold")).grid(row=0, column=col, padx=5, pady=2)
        for i, row in enumerate(resultados, start=1):
            for j, val in enumerate(row):
                ctk.CTkLabel(self.tabla_rentabilidad, text=str(val)).grid(row=i, column=j, padx=5, pady=2)

    def exportar_ingresos_txt(self):
        mes = self.var_mes.get()
        anio = self.var_anio.get()
        try:
            mes_int = int(mes)
            anio_int = int(anio)
            if not (1 <= mes_int <= 12):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Mes o año inválido.")
            return
        datos = self.controller.ingresos_mensuales(mes_int, anio_int)
        if not datos:
            messagebox.showinfo("Sin datos", "No hay ingresos registrados para ese mes/año.")
            return
        archivo = self.controller.exportar_txt(datos, mes_int, anio_int)
        messagebox.showinfo("Éxito", f"Informe exportado correctamente en:\n{archivo}")
