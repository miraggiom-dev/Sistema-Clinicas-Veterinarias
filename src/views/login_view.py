import customtkinter as ctk


class LoginView(ctk.CTkFrame):
    def __init__(self, master, controller, on_login_success, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.controller = controller
        self.on_login_success = on_login_success

        self.pack(pady=20, padx=60, fill="both", expand=True)

        self.label_titulo = ctk.CTkLabel(self, text="Clínica Veterinaria", font=("Roboto", 24, "bold"))
        self.label_titulo.pack(pady=(40, 10))

        self.entry_email = ctk.CTkEntry(
            self, placeholder_text="Correo Electrónico", width=300
        )
        self.entry_email.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(
            self, placeholder_text="Contraseña", show="*", width=300
        )
        self.entry_pass.pack(pady=10)
        
        # Bind Enter key
        self.entry_email.bind("<Return>", self.evento_login)
        self.entry_pass.bind("<Return>", self.evento_login)

        self.btn_login = ctk.CTkButton(
            self, text="Iniciar Sesión", command=self.evento_login, width=300
        )
        self.btn_login.pack(pady=20)

        self.lbl_error = ctk.CTkLabel(self, text="", text_color="red")
        self.lbl_error.pack(pady=5)

    def evento_login(self, event=None):
        email = self.entry_email.get()
        password = self.entry_pass.get()

        exito = self.controller.login(email, password)

        if exito:
            self.lbl_error.configure(text="")
            self.on_login_success()
        else:
            self.lbl_error.configure(text="Credenciales incorrectas.")
