import customtkinter as ctk
from tkinter import messagebox

class UsersView(ctk.CTkFrame):
    def __init__(self, master, controller, id_mascota=None, active_tab=None, switch_module_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        
        self.switch_module_callback = switch_module_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0) 
        self.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(self.left_panel, text="Gestión de Usuarios", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))

        self.scrollable_list = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.scrollable_list.pack(fill="both", expand=True)

        self.right_panel = ctk.CTkFrame(self, width=300, corner_radius=15, fg_color=("#e0e0e0", "#2b2b2b"))
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.right_panel.grid_propagate(False) 

        self._build_form()
        self.mostrar_usuarios()

    def _build_form(self):
        container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Nuevo Usuario", font=("Roboto", 20, "bold")).pack(pady=(0, 20))

        ctk.CTkLabel(container, text="Nombre Completo:", anchor="w").pack(fill="x", pady=(10, 5))
        self.var_nombre = ctk.StringVar()
        ctk.CTkEntry(container, textvariable=self.var_nombre, height=35).pack(fill="x")

        ctk.CTkLabel(container, text="Rol:", anchor="w").pack(fill="x", pady=(10, 5))
        self.var_rol = ctk.StringVar(value="Recepcionista")
        ctk.CTkOptionMenu(container, variable=self.var_rol,
                          values=["Recepcionista", "Veterinario", "Farmacéutico", "Administrador"],
                          height=35).pack(fill="x")

        ctk.CTkLabel(container, text="Email:", anchor="w").pack(fill="x", pady=(10, 5))
        self.var_email = ctk.StringVar()
        ctk.CTkEntry(container, textvariable=self.var_email, height=35).pack(fill="x")

        ctk.CTkLabel(container, text="Contraseña:", anchor="w").pack(fill="x", pady=(10, 5))
        self.var_password = ctk.StringVar()
        ctk.CTkEntry(container, textvariable=self.var_password, show="*", height=35).pack(fill="x")

        ctk.CTkButton(container, text="Crear Usuario", command=self.crear_usuario,
                      height=40, font=("Roboto", 14, "bold"), fg_color="#1f6aa5", hover_color="#144870").pack(fill="x", pady=(30, 0))

    def mostrar_usuarios(self):
        for widget in self.scrollable_list.winfo_children():
            widget.destroy()

        usuarios = self.controller.obtener_usuarios()

        if not usuarios:
            ctk.CTkLabel(self.scrollable_list, text="No hay usuarios registrados.", text_color="gray").pack(pady=20)
            return

        header_frame = ctk.CTkFrame(self.scrollable_list, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        headers = ["ID", "Nombre", "Rol", "Email", "Estado"]
        weights = [1, 3, 2, 3, 1]

        for h, w in zip(headers, weights):
            lbl = ctk.CTkLabel(header_frame, text=h, font=("Roboto", 12, "bold"), text_color="gray", anchor="w")
            lbl.pack(side="left", expand=True, fill="x", padx=5)

        for user in usuarios:
            card = ctk.CTkFrame(self.scrollable_list, fg_color=("#ffffff", "#3a3a3a"), corner_radius=10)
            card.pack(fill="x", pady=5)

            uid = str(user[0])
            nombre = user[1]
            rol = user[2]
            email = user[3]
            estado = "Activo" if user[4] else "Inactivo"

            values = [uid, nombre, rol, email, estado]

            for val, w in zip(values, weights):
                lbl = ctk.CTkLabel(card, text=val, font=("Roboto", 12), anchor="w")
                lbl.pack(side="left", expand=True, fill="x", padx=10, pady=12)

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
