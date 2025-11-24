import customtkinter as ctk
from controllers.admission_controller import AdmissionController
from controllers.auth_controller import AuthController
from models.historia_clinica_model import HistoriaClinicaModel
from models.mascota_model import MascotaModel
from models.propietario_model import PropietarioModel


class VetHistoryView(ctk.CTkFrame):
    def __init__(self, master, controller=None, id_mascota=None, active_tab=None, switch_callback=None):
        super().__init__(master)
        self.controller = controller
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
        
        self.scroll_historial = ctk.CTkScrollableFrame(
            self.frame_historial, width=500, height=400
        )
        self.scroll_historial.pack(fill="both", expand=True)

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
        
        for widget in self.scroll_historial.winfo_children():
            widget.destroy()

        if historial:
            for entry in historial:
                self.crear_tarjeta_historial(entry)
        else:
            lbl = ctk.CTkLabel(
                self.scroll_historial, text="No hay historial clínico para esta mascota."
            )
            lbl.pack(pady=20)

    def crear_tarjeta_historial(self, entry):
        card = ctk.CTkFrame(self.scroll_historial, fg_color="#2b2b2b")
        card.pack(fill="x", pady=5, padx=5)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)
        
        version_text = f"Versión {entry['version']}"
        if entry['es_actual']:
            version_text += " (ACTUAL)"
            color_version = "green"
        else:
            version_text += " (HISTÓRICO)"
            color_version = "gray"

        ctk.CTkLabel(header, text=version_text, font=("Roboto", 12, "bold"), text_color=color_version).pack(side="left", anchor="n")
        
        ctk.CTkLabel(header, text=f"{entry['fecha']}", font=("Roboto", 12)).pack(side="right", anchor="n")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(content, text="Veterinario:", font=("Roboto", 12, "bold")).pack(anchor="w")
        ctk.CTkLabel(content, text=entry['veterinario'], wraplength=400, justify="left").pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(content, text="Diagnóstico:", font=("Roboto", 12, "bold")).pack(anchor="w")
        ctk.CTkLabel(content, text=entry['diagnostico'], wraplength=400, justify="left").pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(content, text="Tratamiento:", font=("Roboto", 12, "bold")).pack(anchor="w")
        ctk.CTkLabel(content, text=entry['tratamiento'], wraplength=400, justify="left").pack(anchor="w", pady=(0, 5))

        if entry['observacion_edicion']:
            ctk.CTkLabel(content, text="Observación:", font=("Roboto", 12, "bold")).pack(anchor="w")
            ctk.CTkLabel(content, text=entry['observacion_edicion'], wraplength=400, justify="left").pack(anchor="w")

        
        if self.rol and self.rol.strip().lower() == "veterinario" and entry['es_actual']:
            btn_edit = ctk.CTkButton(
                card, 
                text="Editar Diagnóstico", 
                height=30,
                fg_color="red", 
                hover_color="darkred",
                text_color="white",
                command=lambda e=entry: self.editar_diagnostico(e)
            )
            btn_edit.pack(pady=10, padx=10, anchor="e")

    def editar_diagnostico(self, entry):
        from datetime import datetime
        from controllers.diagnosis_controller import DiagnosisController
        from models.usuario_model import UsuarioModel
        from tkinter import messagebox

        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Diagnóstico")
        dialog.geometry("500x550")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Editar Diagnóstico", font=("Roboto", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(dialog, text="Diagnóstico:").pack(anchor="w", padx=20)
        txt_diag = ctk.CTkEntry(dialog, width=400)
        txt_diag.pack(pady=5, padx=20)
        txt_diag.insert(0, entry['diagnostico'])

        ctk.CTkLabel(dialog, text="Tratamiento:").pack(anchor="w", padx=20, pady=(10, 0))
        txt_trat = ctk.CTkEntry(dialog, width=400)
        txt_trat.pack(pady=5, padx=20)
        txt_trat.insert(0, entry['tratamiento'])

        ctk.CTkLabel(dialog, text="", height=10).pack()
        ctk.CTkLabel(
            dialog, 
            text="Para confirmar los cambios, ingrese su contraseña:", 
            font=("Roboto", 12, "bold"),
            text_color="#4a9eff"
        ).pack(pady=(10, 5))

        ctk.CTkLabel(dialog, text="Contraseña:").pack(anchor="w", padx=20)
        txt_password = ctk.CTkEntry(dialog, width=400, show="*")
        txt_password.pack(pady=5, padx=20)

        lbl_error = ctk.CTkLabel(dialog, text="", text_color="red")
        lbl_error.pack(pady=5)

        def guardar_cambios():
            nuevo_diag = txt_diag.get().strip()
            nuevo_trat = txt_trat.get().strip()
            password = txt_password.get().strip()
            
            if not nuevo_diag or not nuevo_trat:
                lbl_error.configure(text="Diagnóstico y tratamiento son obligatorios")
                return

            if not password:
                lbl_error.configure(text="Debe ingresar su contraseña para firmar")
                return

            id_veterinario_actual = None
            email_veterinario = None
            
            if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'usuario_actual'):
                if self.controller.usuario_actual:
                    id_veterinario_actual = self.controller.usuario_actual.id_usuario
                    email_veterinario = self.controller.usuario_actual.email

            if not email_veterinario:
                usuarios = UsuarioModel.obtener_todos()
                for user in usuarios:
                    if user['nombre_completo'] == self.usuario:
                        email_veterinario = user['email']
                        id_veterinario_actual = user['id_usuario']
                        break

            if not email_veterinario:
                lbl_error.configure(text="Error: No se pudo verificar el usuario actual")
                return

            usuario_verificado = UsuarioModel.autenticar(email_veterinario, password)
            
            if not usuario_verificado:
                lbl_error.configure(text="Contraseña incorrecta")
                return

            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            observacion = f"Editado por: {self.usuario}, {fecha_actual}"
            
            firma = self.usuario

            exito = DiagnosisController.registrar_diagnostico(
                entry['id_cita'],
                id_veterinario_actual,  
                nuevo_diag,
                nuevo_trat,
                observacion,
                firma=firma  
            )

            if exito:
                messagebox.showinfo("Éxito", "Diagnóstico actualizado y firmado correctamente")
                dialog.destroy()
                self.mostrar_historial(self.mascota_seleccionada)
            else:
                lbl_error.configure(text="Error al guardar el diagnóstico")

        ctk.CTkButton(
            dialog, 
            text="Guardar Cambios", 
            command=guardar_cambios,
            height=35,
            fg_color="#2a5a8a",
            hover_color="#3a6a9a",
            font=("Roboto", 13, "bold")
        ).pack(pady=20)
