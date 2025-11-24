import customtkinter as ctk
from tkinter import messagebox
from functools import partial

class ServiceView(ctk.CTkFrame):
    def __init__(self, master, controller, id_mascota=None, active_tab=None, switch_module_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.switch_module_callback = switch_module_callback

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0) # Fixed width for form
        self.grid_rowconfigure(0, weight=1)

        # --- Left Side: Service List ---
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(self.left_panel, text="Gestión de Servicios", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # Scrollable List
        self.scrollable_list = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.scrollable_list.pack(fill="both", expand=True)

        # --- Right Side: Form ---
        self.right_panel = ctk.CTkFrame(self, width=320, corner_radius=15, fg_color=("#e0e0e0", "#2b2b2b"))
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.right_panel.grid_propagate(False)

        self._build_form()
        self.cargar_servicios()

    def _build_form(self):
        container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Servicio", font=("Roboto", 20, "bold")).pack(pady=(0, 20))

        self.var_id = ctk.StringVar() # Hidden ID

        ctk.CTkLabel(container, text="Nombre:", anchor="w").pack(fill="x", pady=(5, 2))
        self.entry_nombre = ctk.CTkEntry(container, height=35)
        self.entry_nombre.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(container, text="Tipo:", anchor="w").pack(fill="x", pady=(5, 2))
        self.var_tipo = ctk.StringVar(value="Consulta")
        self.opt_tipo = ctk.CTkOptionMenu(container, variable=self.var_tipo, 
                                          values=["Consulta", "Cirugía", "Vacunación", "Otro"],
                                          height=35)
        self.opt_tipo.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(container, text="Precio Base ($):", anchor="w").pack(fill="x", pady=(5, 2))
        self.entry_precio = ctk.CTkEntry(container, height=35)
        self.entry_precio.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(container, text="Costo Mano Obra ($):", anchor="w").pack(fill="x", pady=(5, 2))
        self.entry_costo = ctk.CTkEntry(container, height=35)
        self.entry_costo.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(container, text="Duración (min):", anchor="w").pack(fill="x", pady=(5, 2))
        self.entry_duracion = ctk.CTkEntry(container, height=35)
        self.entry_duracion.pack(fill="x", pady=(0, 10))

        self.var_activo = ctk.BooleanVar(value=True)
        self.chk_activo = ctk.CTkCheckBox(container, text="Activo", variable=self.var_activo)
        self.chk_activo.pack(anchor="w", pady=(10, 20))

        self.btn_guardar = ctk.CTkButton(container, text="Guardar", command=self.guardar_servicio,
                                         height=40, font=("Roboto", 14, "bold"), fg_color="#1f6aa5", hover_color="#144870")
        self.btn_guardar.pack(fill="x", pady=(0, 10))

        self.btn_limpiar = ctk.CTkButton(container, text="Limpiar / Nuevo", command=self.limpiar_formulario,
                                         height=35, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.btn_limpiar.pack(fill="x")

    def cargar_servicios(self):
        for widget in self.scrollable_list.winfo_children():
            widget.destroy()

        servicios = self.controller.obtener_servicios(activos_only=False)
        
        if not servicios:
            ctk.CTkLabel(self.scrollable_list, text="No hay servicios registrados.", text_color="gray").pack(pady=20)
            return

        for s in servicios:
            # Safe access to row data
            try:
                s_id = s['id_servicio']
                s_nombre = s['nombre']
                s_tipo = s['tipo']
                s_precio = s['precio_base']
                s_duracion = s['duracion_estimada']
                s_activo = s['activo']
            except Exception:
                s_id = s[0]
                s_nombre = s[1]
                s_tipo = "N/A"
                s_precio = 0
                s_duracion = 0
                s_activo = 0

            # Card
            card = ctk.CTkFrame(self.scrollable_list, fg_color=("#ffffff", "#3a3a3a"), corner_radius=10)
            card.pack(fill="x", pady=5)

            # Left Info
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            ctk.CTkLabel(info_frame, text=s_nombre, font=("Roboto", 16, "bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info_frame, text=f"{s_tipo} • {s_duracion} min", font=("Roboto", 12), text_color="gray", anchor="w").pack(fill="x")

            # Right Info & Action
            action_frame = ctk.CTkFrame(card, fg_color="transparent")
            action_frame.pack(side="right", padx=15, pady=10)

            price_lbl = ctk.CTkLabel(action_frame, text=f"${s_precio:,.2f}", font=("Roboto", 16, "bold"), text_color="#4a9eff")
            price_lbl.pack(side="top", anchor="e", pady=(0, 5))

            status_color = "#2cc985" if s_activo else "#ff4d4d"
            status_text = "Activo" if s_activo else "Inactivo"
            
            # Status dot
            status_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
            status_frame.pack(side="top", anchor="e")
            
            # Edit Button
            btn_edit = ctk.CTkButton(action_frame, text="Editar", width=80, height=28, 
                                     fg_color="transparent", border_width=1, 
                                     command=partial(self.cargar_en_formulario, s))
            btn_edit.pack(side="top", pady=(5, 0))

    def cargar_en_formulario(self, s):
        try:
            self.var_id.set(s['id_servicio'])
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, s['nombre'])
            
            self.var_tipo.set(s['tipo'])
            
            self.entry_precio.delete(0, "end")
            self.entry_precio.insert(0, str(s['precio_base']))
            
            self.entry_costo.delete(0, "end")
            self.entry_costo.insert(0, str(s['costo_mano_obra']))
            
            self.entry_duracion.delete(0, "end")
            self.entry_duracion.insert(0, str(s['duracion_estimada']))
            
            self.var_activo.set(bool(s['activo']))
            
            self.btn_guardar.configure(text="Actualizar")
        except Exception:
            pass

    def limpiar_formulario(self):
        self.var_id.set("")
        self.entry_nombre.delete(0, "end")
        self.var_tipo.set("Consulta")
        self.entry_precio.delete(0, "end")
        self.entry_costo.delete(0, "end")
        self.entry_duracion.delete(0, "end")
        self.var_activo.set(True)
        self.btn_guardar.configure(text="Guardar")

    def guardar_servicio(self):
        nombre = self.entry_nombre.get().strip()
        tipo = self.var_tipo.get()
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
            ok = self.controller.actualizar_servicio(s_id, nombre, tipo, precio, costo, duracion, activo)
            if ok:
                messagebox.showinfo("Éxito", "Servicio actualizado correctamente.")
                self.limpiar_formulario()
                self.cargar_servicios()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el servicio.")
        else:
            # Create
            new_id = self.controller.crear_servicio(nombre, tipo, precio, costo, duracion)
            if new_id:
                messagebox.showinfo("Éxito", "Servicio creado correctamente.")
                self.limpiar_formulario()
                self.cargar_servicios()
            else:
                messagebox.showerror("Error", "No se pudo crear el servicio.")
