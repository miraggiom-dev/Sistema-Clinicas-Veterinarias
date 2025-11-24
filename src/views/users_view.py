import customtkinter as ctk
from tkinter import messagebox

class UsersView(ctk.CTkFrame):
    def __init__(self, master, controller, id_mascota=None, active_tab=None, switch_module_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.switch_module_callback = switch_module_callback
        ctk.CTkLabel(self, text="Gestión de Usuarios", font=("Roboto", 28, "bold")).pack(pady=10)

        # Tabla de usuarios
        self.tabla = ctk.CTkFrame(self)
        self.tabla.pack(pady=10, padx=20, fill="x")
        self.mostrar_usuarios()

        # Formulario de alta
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.frame_form, text="Nombre completo:").grid(row=0, column=0, sticky="e")
        ctk.CTkLabel(self.frame_form, text="Rol:").grid(row=1, column=0, sticky="e")
        ctk.CTkLabel(self.frame_form, text="Email:").grid(row=2, column=0, sticky="e")
        ctk.CTkLabel(self.frame_form, text="Contraseña:").grid(row=3, column=0, sticky="e")
        self.var_nombre = ctk.StringVar()
        self.var_rol = ctk.StringVar(value="Recepcionista")
        self.var_email = ctk.StringVar()
        self.var_password = ctk.StringVar()
        ctk.CTkEntry(self.frame_form, textvariable=self.var_nombre, width=180).grid(row=0, column=1, padx=5, pady=2)
        ctk.CTkOptionMenu(self.frame_form, variable=self.var_rol, values=["Recepcionista", "Veterinario", "Farmacéutico", "Administrador"]).grid(row=1, column=1, padx=5, pady=2)
        ctk.CTkEntry(self.frame_form, textvariable=self.var_email, width=180).grid(row=2, column=1, padx=5, pady=2)
        ctk.CTkEntry(self.frame_form, textvariable=self.var_password, show="*", width=180).grid(row=3, column=1, padx=5, pady=2)
        ctk.CTkButton(self.frame_form, text="Crear Usuario", command=self.crear_usuario).grid(row=4, column=0, columnspan=2, pady=8)

    def mostrar_usuarios(self):
        for widget in self.tabla.winfo_children():
            widget.destroy()
        headers = ["ID", "Nombre", "Rol", "Email", "Estado"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.tabla, text=h, font=("Roboto", 12, "bold")).grid(row=0, column=col, padx=5, pady=2)
        usuarios = self.controller.obtener_usuarios()
        for i, user in enumerate(usuarios, start=1):
            for j, val in enumerate(user):
                ctk.CTkLabel(self.tabla, text=str(val)).grid(row=i, column=j, padx=5, pady=2)

    def crear_usuario(self):
        nombre = self.var_nombre.get().strip()
        rol = self.var_rol.get().strip()
        email = self.var_email.get().strip()
        password = self.var_password.get().strip()
        if not (nombre and rol and email and password):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        ok = self.controller.crear_usuario(nombre, rol, email, password)
        if ok:
            messagebox.showinfo("Éxito", "Usuario creado correctamente.")
            self.mostrar_usuarios()
            self.var_nombre.set("")
            self.var_email.set("")
            self.var_password.set("")
        else:
            messagebox.showerror("Error", "No se pudo crear el usuario.")
