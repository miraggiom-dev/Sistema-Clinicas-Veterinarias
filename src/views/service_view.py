import customtkinter as ctk
from tkinter import messagebox
from functools import partial

class ServiceView(ctk.CTkFrame):
    def __init__(self, master, controller, id_mascota=None, active_tab=None, switch_module_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.switch_module_callback = switch_module_callback

        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(self, text="Gestión de Servicios", font=("Roboto", 24, "bold")).grid(row=0, column=0, pady=20)

        # Content Area (Split into List and Form)
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=2) # List
        self.content_frame.grid_columnconfigure(1, weight=1) # Form

        # --- Service List ---
        self.list_frame = ctk.CTkFrame(self.content_frame)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.list_frame, text="Lista de Servicios", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.scrollable_list = ctk.CTkScrollableFrame(self.list_frame)
        self.scrollable_list.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Form ---
        self.form_frame = ctk.CTkFrame(self.content_frame)
        self.form_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.form_frame, text="Nuevo / Editar Servicio", font=("Roboto", 16, "bold")).pack(pady=10)

        self.var_id = ctk.StringVar() # Hidden ID for editing
        
        ctk.CTkLabel(self.form_frame, text="Nombre:").pack(anchor="w", padx=10)
        self.entry_nombre = ctk.CTkEntry(self.form_frame)
        self.entry_nombre.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(self.form_frame, text="Precio Base:").pack(anchor="w", padx=10)
        self.entry_precio = ctk.CTkEntry(self.form_frame)
        self.entry_precio.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(self.form_frame, text="Costo Mano de Obra:").pack(anchor="w", padx=10)
        self.entry_costo = ctk.CTkEntry(self.form_frame)
        self.entry_costo.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(self.form_frame, text="Duración (min):").pack(anchor="w", padx=10)
        self.entry_duracion = ctk.CTkEntry(self.form_frame)
        self.entry_duracion.pack(fill="x", padx=10, pady=(0, 10))

        self.var_activo = ctk.BooleanVar(value=True)
        self.chk_activo = ctk.CTkCheckBox(self.form_frame, text="Activo", variable=self.var_activo)
        self.chk_activo.pack(anchor="w", padx=10, pady=10)

        self.btn_guardar = ctk.CTkButton(self.form_frame, text="Guardar", command=self.guardar_servicio)
        self.btn_guardar.pack(pady=10, padx=10, fill="x")

        self.btn_limpiar = ctk.CTkButton(self.form_frame, text="Limpiar / Nuevo", command=self.limpiar_formulario, fg_color="gray")
        self.btn_limpiar.pack(pady=5, padx=10, fill="x")

        self.cargar_servicios()

    def cargar_servicios(self):
        # Clear list
        for widget in self.scrollable_list.winfo_children():
            widget.destroy()

        servicios = self.controller.obtener_servicios(activos_only=False)
        
        if not servicios:
            ctk.CTkLabel(self.scrollable_list, text="No hay servicios registrados.").pack(pady=20)
            return

        for s in servicios:
            # s is likely a tuple or dict depending on the model. 
            # Model returns rows from fetchall, usually tuples if not using a dict factory.
            # Looking at servicio_model.py, it returns rows directly from cursor.fetchall().
            # Assuming tuples: (id, nombre, precio, costo, duracion, activo)
            
            s_id = s[0]
            s_nombre = s[1]
            s_precio = s[2]
            s_costo = s[3]
            s_duracion = s[4]
            s_activo = s[5]

            card = ctk.CTkFrame(self.scrollable_list)
            card.pack(fill="x", pady=5, padx=5)

            status_color = "green" if s_activo else "red"
            status_text = "Activo" if s_activo else "Inactivo"

            info_text = f"{s_nombre} | ${s_precio} | {s_duracion} min"
            ctk.CTkLabel(card, text=info_text, font=("Roboto", 12, "bold")).pack(side="left", padx=10)
            
            ctk.CTkLabel(card, text=status_text, text_color=status_color).pack(side="left", padx=10)

            btn_edit = ctk.CTkButton(card, text="Editar", width=60, command=partial(self.cargar_en_formulario, s))
            btn_edit.pack(side="right", padx=5, pady=5)

    def cargar_en_formulario(self, servicio):
        self.var_id.set(servicio[0])
        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, servicio[1])
        
        self.entry_precio.delete(0, "end")
        self.entry_precio.insert(0, str(servicio[2]))
        
        self.entry_costo.delete(0, "end")
        self.entry_costo.insert(0, str(servicio[3]))
        
        self.entry_duracion.delete(0, "end")
        self.entry_duracion.insert(0, str(servicio[4]))
        
        self.var_activo.set(bool(servicio[5]))

    def limpiar_formulario(self):
        self.var_id.set("")
        self.entry_nombre.delete(0, "end")
        self.entry_precio.delete(0, "end")
        self.entry_costo.delete(0, "end")
        self.entry_duracion.delete(0, "end")
        self.var_activo.set(True)

    def guardar_servicio(self):
        nombre = self.entry_nombre.get().strip()
        precio = self.entry_precio.get().strip()
        costo = self.entry_costo.get().strip()
        duracion = self.entry_duracion.get().strip()
        activo = self.var_activo.get()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return

        s_id = self.var_id.get()

        if s_id:
            # Update
            ok = self.controller.actualizar_servicio(s_id, nombre, precio, costo, duracion, activo)
            if ok:
                messagebox.showinfo("Éxito", "Servicio actualizado correctamente.")
                self.limpiar_formulario()
                self.cargar_servicios()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el servicio.")
        else:
            # Create
            new_id = self.controller.crear_servicio(nombre, precio, costo, duracion)
            if new_id:
                messagebox.showinfo("Éxito", "Servicio creado correctamente.")
                self.limpiar_formulario()
                self.cargar_servicios()
            else:
                messagebox.showerror("Error", "No se pudo crear el servicio.")
