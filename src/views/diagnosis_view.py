import customtkinter as ctk
from controllers.diagnosis_controller import DiagnosisController
from controllers.admission_controller import AdmissionController
from tkinter import messagebox


class DiagnosisView(ctk.CTkFrame):
    def __init__(self, master, controller=None, id_mascota=None, active_tab=None, switch_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.admission_controller = AdmissionController()
        self.diagnosis_controller = DiagnosisController()
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        from models.mascota_model import MascotaModel

        self.lbl_titulo = ctk.CTkLabel(
            self, text="Registro de Diagnóstico", font=("Roboto", 22, "bold")
        )
        self.lbl_titulo.pack(pady=10)

        # Obtener todas las mascotas con propietario
        self.mascotas = MascotaModel.obtener_todas_con_propietario()
        self.mascota_map = {
            f"{m['nombre']} (Dueño: {m['propietario_nombre']})": m
            for m in self.mascotas
        }
        self.cmb_mascota = ctk.CTkComboBox(
            self, values=list(self.mascota_map.keys()), width=300, state="readonly"
        )
        self.cmb_mascota.pack(pady=10)

        self.txt_diagnostico = ctk.CTkEntry(
            self, placeholder_text="Diagnóstico", width=400
        )
        self.txt_diagnostico.pack(pady=5)
        self.txt_tratamiento = ctk.CTkEntry(
            self, placeholder_text="Tratamiento", width=400
        )
        self.txt_tratamiento.pack(pady=5)
        self.txt_observacion = ctk.CTkEntry(
            self, placeholder_text="Observación (opcional)", width=400
        )
        self.txt_observacion.pack(pady=5)

        # Bind Enter key
        self.txt_diagnostico.bind("<Return>", self.registrar_diagnostico)
        self.txt_tratamiento.bind("<Return>", self.registrar_diagnostico)
        self.txt_observacion.bind("<Return>", self.registrar_diagnostico)

        self.btn_guardar = ctk.CTkButton(
            self, text="Registrar Diagnóstico", command=self.registrar_diagnostico
        )
        self.btn_guardar.pack(pady=15)

    def registrar_diagnostico(self, event=None):
        from models.cita_model import CitaModel
        from models.usuario_model import UsuarioModel
        from tkinter import END, simpledialog

        mascota_key = self.cmb_mascota.get()
        if not mascota_key or mascota_key not in self.mascota_map:
            messagebox.showerror("Error", "Seleccione una mascota válida.")
            return
        mascota = self.mascota_map[mascota_key]
        id_mascota = mascota["id_mascota"]
        cita = CitaModel.obtener_ultima_por_mascota(id_mascota)
        if not cita:
            messagebox.showerror(
                "Error",
                "La mascota seleccionada no tiene citas registradas. No se puede asociar diagnóstico.",
            )
            return
        id_cita = cita["id_cita"]
        id_veterinario = cita["id_veterinario"]
        nombre_veterinario = (
            cita["veterinario_nombre"] if "veterinario_nombre" in cita else ""
        )
        email_veterinario = (
            cita["veterinario_email"] if "veterinario_email" in cita else None
        )

        diagnostico = self.txt_diagnostico.get().strip()
        tratamiento = self.txt_tratamiento.get().strip()
        observacion = self.txt_observacion.get().strip()

        if not diagnostico or not tratamiento:
            messagebox.showerror("Error", "Debe ingresar diagnóstico y tratamiento.")
            return

        # Popup de contraseña
        def pedir_contraseña():
            popup = ctk.CTkToplevel(self)
            popup.title("Firmar diagnóstico")
            popup.geometry("350x180")
            popup.grab_set()

            lbl = ctk.CTkLabel(
                popup,
                text="Ingrese su contraseña para firmar el diagnóstico:",
                font=("Roboto", 14),
            )
            lbl.pack(pady=15)
            entry_pass = ctk.CTkEntry(popup, show="*", width=220)
            entry_pass.pack(pady=10)

            def intentar_firma(event=None):
                password = entry_pass.get()
                # Validar contraseña del veterinario en sesión (por email o id)
                # Se asume que el email del veterinario está en cita["veterinario_email"]
                # Si no, se debe obtener por id_veterinario
                from models.usuario_model import UsuarioModel

                # Buscar email del veterinario
                email = email_veterinario
                if not email:
                    # Buscar email por id_veterinario
                    from database.connection import get_db_connection

                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT email, nombre_completo FROM usuarios WHERE id_usuario = ?",
                        (id_veterinario,),
                    )
                    user = cursor.fetchone()
                    conn.close()
                    if user:
                        email = user["email"]
                        nombre = user["nombre_completo"]
                    else:
                        email = None
                        nombre = ""
                else:
                    nombre = nombre_veterinario
                if not email:
                    messagebox.showerror(
                        "Error", "No se pudo obtener el email del veterinario."
                    )
                    popup.destroy()
                    return
                user = UsuarioModel.autenticar(email, password)
                if user:
                    # Firma válida, guardar diagnóstico con firma
                    exito = self.diagnosis_controller.registrar_diagnostico_firmado(
                        id_cita,
                        id_veterinario,
                        diagnostico,
                        tratamiento,
                        observacion,
                        nombre,
                    )
                    if exito:
                        messagebox.showinfo(
                            "Éxito", "Diagnóstico registrado y firmado correctamente."
                        )
                        self.txt_diagnostico.delete(0, END)
                        self.txt_tratamiento.delete(0, END)
                        self.txt_observacion.delete(0, END)
                        popup.destroy()
                    else:
                        messagebox.showerror(
                            "Error", "Ocurrió un error al registrar el diagnóstico."
                        )
                else:
                    messagebox.showerror(
                        "Error",
                        "Contraseña incorrecta. No se puede firmar el diagnóstico.",
                    )
                    entry_pass.delete(0, END)

            btn_firmar = ctk.CTkButton(
                popup, text="Firmar y Registrar", command=intentar_firma
            )
            btn_firmar.pack(pady=10)

            popup.bind("<Return>", intentar_firma)

        pedir_contraseña()
