import customtkinter as ctk
from controllers.payment_report_controller import PaymentReportController
import os
import webbrowser
from datetime import datetime

class PaymentReportView(ctk.CTkToplevel):

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Generar Informe de Pagos")
        self.geometry("420x280")
        self.attributes('-topmost', True)
        self.focus_force()
        if master:
            try:
                self.transient(master)
            except Exception:
                pass
        
        try:
            frame_bg = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        except Exception:
            frame_bg = None

        container = ctk.CTkFrame(self, fg_color=frame_bg)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(container, text="Informe Mensual de Pagos", font=("Roboto", 16, "bold")).pack(pady=10)

        frame_date = ctk.CTkFrame(container, fg_color="transparent")
        frame_date.pack(pady=10)

        ctk.CTkLabel(frame_date, text="Mes:").grid(row=0, column=0, padx=5)
        self.var_mes = ctk.StringVar(value=str(datetime.now().month))
        self.opt_mes = ctk.CTkOptionMenu(frame_date, variable=self.var_mes, values=[str(i) for i in range(1, 13)], width=70)
        self.opt_mes.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(frame_date, text="Año:").grid(row=0, column=2, padx=5)
        self.var_anio = ctk.StringVar(value=str(datetime.now().year))
        self.entry_anio = ctk.CTkEntry(frame_date, textvariable=self.var_anio, width=80)
        self.entry_anio.grid(row=0, column=3, padx=5)

        self.lbl_status = ctk.CTkLabel(container, text="", text_color="green", wraplength=380)
        self.lbl_status.pack(pady=10)

        btn_frame = ctk.CTkFrame(container, fg_color=frame_bg)
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="Generar Informe", command=self._generar).pack(side="right", padx=6)
        ctk.CTkButton(btn_frame, text="Abrir carpeta", command=self._abrir_carpeta).pack(side="right")

    def _generar(self):
        mes = self.var_mes.get()
        anio = self.var_anio.get()
        
        try:
            mes_int = int(mes)
            anio_int = int(anio)
        except ValueError:
            self.lbl_status.configure(text="Mes o Año inválidos.", text_color="red")
            return

        ruta = PaymentReportController.generar_informe_mensual(mes_int, anio_int)
        
        if ruta:
            name = os.path.basename(ruta)
            self.lbl_status.configure(text=f"Informe generado: {name}", text_color="green")
            try:
                webbrowser.open('file://' + os.path.abspath(ruta))
            except Exception:
                pass
        else:
            self.lbl_status.configure(text="No se encontraron pagos para este periodo.", text_color="orange")

    def _abrir_carpeta(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        base = os.path.join(project_root, 'informes_pagos')
        try:
            os.makedirs(base, exist_ok=True)
            webbrowser.open('file://' + os.path.abspath(base))
        except Exception:
            pass
