import customtkinter as ctk
from controllers.admission_controller import AdmissionController
from controllers.auth_controller import AuthController
from models.historia_clinica_model import HistoriaClinicaModel
from models.mascota_model import MascotaModel
from models.propietario_model import PropietarioModel


class VetHistoryView(ctk.CTkFrame):
    def __init__(self, master, controller=None, id_mascota=None, active_tab=None, switch_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        # Si el controlador es AuthController, podemos obtener el usuario actual
        self.usuario = None
        self.rol = None
        if controller and hasattr(controller, 'usuario_actual'):
             if controller.usuario_actual:
                self.usuario = controller.usuario_actual.nombre
                self.rol = controller.usuario_actual.rol
        
        self.switch_callback = switch_callback
        self.admission_controller = AdmissionController()
        self.historia_model = HistoriaClinicaModel()
        self.mascota_model = MascotaModel()
        self.mascota_seleccionada = None

        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.crear_interfaz()

    def crear_interfaz(self):
        self.label_titulo = ctk.CTkLabel(
            self, text="Historial Clínico de Mascotas", font=("Roboto", 22, "bold")
        )
        self.label_titulo.pack(pady=10)

        self.frame_lista = ctk.CTkFrame(self)
        self.frame_lista.pack(side="left", fill="y", padx=10, pady=10)

        self.label_lista = ctk.CTkLabel(self.frame_lista, text="Mascotas")
        self.label_lista.pack(pady=5)

        self.listbox_mascotas = ctk.CTkScrollableFrame(
            self.frame_lista, width=250, height=400
        )
        self.listbox_mascotas.pack(fill="y", expand=True)

        self.frame_historial = ctk.CTkFrame(self)
        self.frame_historial.pack(
            side="right", fill="both", expand=True, padx=10, pady=10
        )

        self.label_historial = ctk.CTkLabel(
            self.frame_historial, text="Historial Clínico", font=("Arial", 16, "bold")
        )
        self.label_historial.pack(pady=5)

        self.text_historial = ctk.CTkTextbox(
            self.frame_historial, width=500, height=400
        )
        self.text_historial.pack(fill="both", expand=True)
        self.text_historial.configure(state="disabled")

        self.cargar_mascotas()

    def cargar_mascotas(self):
        mascotas = self.mascota_model.obtener_todas_con_propietario()
        for widget in self.listbox_mascotas.winfo_children():
            widget.destroy()
        for mascota in mascotas:
            nombre_mascota = mascota["nombre"]
            especie = mascota["especie"]
            propietario = mascota["propietario_nombre"]
            btn = ctk.CTkButton(
                self.listbox_mascotas,
                text=f"{nombre_mascota} ({especie}) - Prop: {propietario}",
                width=220,
                command=lambda m=mascota: self.mostrar_historial(m),
            )
            btn.pack(pady=2)

    def mostrar_historial(self, mascota):
        self.mascota_seleccionada = mascota
        historial = self.historia_model.obtener_por_mascota(mascota["id_mascota"])
        self.text_historial.configure(state="normal")
        self.text_historial.delete("1.0", "end")
        if historial:
            for entry in historial:
                self.text_historial.insert(
                    "end",
                    f"Fecha: {entry['fecha']}\nDiagnóstico: {entry['diagnostico']}\nTratamiento: {entry['tratamiento']}\n---\n",
                )
        else:
            self.text_historial.insert(
                "end", "No hay historial clínico para esta mascota."
            )
        self.text_historial.configure(state="disabled")
