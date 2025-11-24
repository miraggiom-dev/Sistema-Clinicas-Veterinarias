import customtkinter as ctk


class LoginView(ctk.CTkFrame):
    def __init__(self, master, controller, on_login_success):
        super().__init__(master)
        self.controller = controller
        self.on_login_success = on_login_success
        self.configure(fg_color="#1a1a1a")
        self.pack(fill="both", expand=True)
        self.center_frame = ctk.CTkFrame(
            self, 
            fg_color="#3a3a3a", 
            corner_radius=15
        )
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.label_titulo = ctk.CTkLabel(
            self.center_frame, 
            text="Clínica Veterinaria", 
            font=("Roboto", 26, "bold"),
            text_color="#4a9eff"
        )
        self.label_titulo.pack(pady=(40, 10), padx=50)
        
        # Subtitle
        ctk.CTkLabel(
            self.center_frame,
            text="Iniciar Sesión",
            font=("Roboto", 14),
            text_color="#aaaaaa"
        ).pack(pady=(0, 30), padx=50)

        # Email field with label
        ctk.CTkLabel(
            self.center_frame,
            text="Correo Electrónico",
            font=("Roboto", 11),
            text_color="#888888",
            anchor="w"
        ).pack(anchor="w", padx=50, pady=(0, 5))
        
        self.entry_email = ctk.CTkEntry(
            self.center_frame, 
            placeholder_text="ejemplo@correo.com", 
            width=320,
            height=38,
            font=("Roboto", 12)
        )
        self.entry_email.pack(pady=(0, 15), padx=50)

        # Password field with label
        ctk.CTkLabel(
            self.center_frame,
            text="Contraseña",
            font=("Roboto", 11),
            text_color="#888888",
            anchor="w"
        ).pack(anchor="w", padx=50, pady=(0, 5))
        
        self.entry_pass = ctk.CTkEntry(
            self.center_frame, 
            placeholder_text="••••••••", 
            show="*", 
            width=320,
            height=38,
            font=("Roboto", 12)
        )
        self.entry_pass.pack(pady=(0, 25), padx=50)
        
        # Bind Enter key
        self.entry_email.bind("<Return>", self.evento_login)
        self.entry_pass.bind("<Return>", self.evento_login)

        self.btn_login = ctk.CTkButton(
            self.center_frame, 
            text="Iniciar Sesión", 
            command=self.evento_login, 
            width=320,
            height=42,
            fg_color="#2a5a8a",
            hover_color="#3a6a9a",
            font=("Roboto", 14, "bold"),
            corner_radius=8
        )
        self.btn_login.pack(pady=(0, 15), padx=50)

        self.lbl_error = ctk.CTkLabel(
            self.center_frame, 
            text="", 
            text_color="#ff4444",
            font=("Roboto", 11)
        )
        self.lbl_error.pack(pady=(0, 35), padx=50)

    def evento_login(self, event=None):
        email = self.entry_email.get()
        password = self.entry_pass.get()

        exito = self.controller.login(email, password)

        if exito:
            self.lbl_error.configure(text="")
            self.on_login_success()
        else:
            self.lbl_error.configure(text="Credenciales incorrectas.")
