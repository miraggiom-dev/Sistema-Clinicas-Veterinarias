# views/admission_view.py (CORREGIDO PARA OCULTAR ID DE MASCOTA)

import customtkinter as ctk
from controllers.admission_controller import AdmissionController

class AdmissionView(ctk.CTkFrame):
    def __init__(self, master, auth_controller):
        super().__init__(master)
        self.auth_controller = auth_controller
        self.admission_controller = AdmissionController()
        self.propietario_seleccionado = None
        
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tabview = ctk.CTkTabview(self, width=800)
        self.tabview.pack(fill="both", expand=True)
        
        self.tabview.add("Clientes/Propietarios")
        self.tabview.add("Mascotas")

        self.crear_tab_propietarios(self.tabview.tab("Clientes/Propietarios"))
        self.crear_tab_mascotas(self.tabview.tab("Mascotas"))

        self.actualizar_lista_propietarios()
        
    # ------------------------------------------------------------------
    # --- PESTAÑA 1: CLIENTES/PROPIETARIOS ---
    # ------------------------------------------------------------------
    
    def crear_tab_propietarios(self, tab):
        # Frame superior para búsqueda y registro
        frame_busqueda = ctk.CTkFrame(tab)
        frame_busqueda.pack(fill="x", pady=10)
        
        # Búsqueda ahora puede ser por nombre o cédula
        self.entry_busqueda = ctk.CTkEntry(frame_busqueda, placeholder_text="Buscar por nombre o cédula...", width=250)
        self.entry_busqueda.pack(side="left", padx=10, pady=10)
        
        btn_buscar = ctk.CTkButton(frame_busqueda, text="Buscar", command=self.actualizar_lista_propietarios)
        btn_buscar.pack(side="left", padx=10, pady=10)
        
        # Botón Nuevo Registro
        btn_nuevo = ctk.CTkButton(frame_busqueda, text="Registrar Nuevo Propietario", command=self.mostrar_formulario_propietario)
        btn_nuevo.pack(side="right", padx=10, pady=10)

        # Lista de propietarios 
        self.listbox_propietarios = ctk.CTkScrollableFrame(tab, label_text="Lista de Clientes Encontrados")
        self.listbox_propietarios.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.propietario_widgets = {} 
        
    def actualizar_lista_propietarios(self):
        busqueda = self.entry_busqueda.get()
        propietarios = self.admission_controller.buscar_clientes(busqueda)
        
        # Limpiar lista anterior
        for widget in self.listbox_propietarios.winfo_children():
            widget.destroy()
        self.propietario_widgets = {}
        
        if not propietarios:
            ctk.CTkLabel(self.listbox_propietarios, text="No se encontraron propietarios.", text_color="orange").pack(pady=20)
            return

        for prop in propietarios:
            frame_item = ctk.CTkFrame(self.listbox_propietarios, fg_color="transparent")
            frame_item.pack(fill="x", pady=5)
            
            # Acceso directo a la columna 'cedula'
            cedula_display = prop['cedula'] 
            info_text = f"Cédula: {cedula_display} | Nombre: {prop['nombre']} | Teléfono: {prop['telefono']}"
            ctk.CTkLabel(frame_item, text=info_text, anchor="w").pack(side="left", padx=10)
            
            # Botón para seleccionar y ver mascotas
            btn_seleccionar = ctk.CTkButton(frame_item, text="Seleccionar", width=100,
                                            command=lambda p=prop: self.seleccionar_propietario(p))
            btn_seleccionar.pack(side="right", padx=10)
            self.propietario_widgets[prop['id_propietario']] = btn_seleccionar

    def seleccionar_propietario(self, propietario):
        self.propietario_seleccionado = propietario
        for id_prop, btn in self.propietario_widgets.items():
            if id_prop == propietario['id_propietario']:
                btn.configure(fg_color="green") # Resaltar el seleccionado
            else:
                btn.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

        self.actualizar_tab_mascotas()
        
        self.tabview.set("Mascotas")


    def mostrar_formulario_propietario(self):
        # Formulario simple en una ventana top-level
        win = ctk.CTkToplevel(self)
        win.title("Nuevo Propietario")
        win.geometry("400x400") 

        ctk.CTkLabel(win, text="Registrar Cliente", font=("Roboto", 18, "bold")).pack(pady=10)

        # CAMPO DE CÉDULA
        entry_cedula = ctk.CTkEntry(win, placeholder_text="Cédula/Documento de Identidad", width=300)
        entry_cedula.pack(pady=5)
        
        entry_nombre = ctk.CTkEntry(win, placeholder_text="Nombre Completo", width=300)
        entry_nombre.pack(pady=5)
        
        entry_tel = ctk.CTkEntry(win, placeholder_text="Teléfono", width=300)
        entry_tel.pack(pady=5)
        
        entry_email = ctk.CTkEntry(win, placeholder_text="Email", width=300)
        entry_email.pack(pady=5)
        
        entry_dir = ctk.CTkEntry(win, placeholder_text="Dirección", width=300)
        entry_dir.pack(pady=5)
        
        lbl_status = ctk.CTkLabel(win, text="")
        lbl_status.pack(pady=5)

        def guardar_propietario():
            cedula = entry_cedula.get()
            nombre = entry_nombre.get()
            
            id_prop = self.admission_controller.registrar_nuevo_cliente(
                cedula, # <-- Pasamos la cédula
                nombre, 
                entry_tel.get(), 
                entry_email.get(), 
                entry_dir.get()
            )
            if id_prop:
                lbl_status.configure(text=f"Cliente registrado con Cédula: {cedula}", text_color="green")
                self.actualizar_lista_propietarios()
                win.after(1500, win.destroy)
            else:
                lbl_status.configure(text="Error al registrar cliente. (Verifique que la Cédula no exista)", text_color="red")
        
        ctk.CTkButton(win, text="Guardar Cliente", command=guardar_propietario).pack(pady=10)

    # ------------------------------------------------------------------
    # --- PESTAÑA 2: MASCOTAS ---
    # ------------------------------------------------------------------

    def crear_tab_mascotas(self, tab):
        self.frame_info_propietario = ctk.CTkFrame(tab, fg_color="transparent")
        self.frame_info_propietario.pack(fill="x", pady=5)
        
        self.lbl_info_prop = ctk.CTkLabel(self.frame_info_propietario, text="Seleccione un propietario primero.", text_color="orange")
        self.lbl_info_prop.pack(pady=10)
        
        self.btn_nueva_mascota = ctk.CTkButton(self.frame_info_propietario, text="Registrar Nueva Mascota", state="disabled", command=self.mostrar_formulario_mascota)
        self.btn_nueva_mascota.pack(side="right", padx=10)

        self.listbox_mascotas = ctk.CTkScrollableFrame(tab, label_text="Mascotas del Cliente")
        self.listbox_mascotas.pack(fill="both", expand=True, padx=10, pady=10)

    def actualizar_tab_mascotas(self):
        for widget in self.listbox_mascotas.winfo_children():
            widget.destroy()
            
        if not self.propietario_seleccionado:
            self.lbl_info_prop.configure(text="Seleccione un propietario en la pestaña anterior para ver sus mascotas.", text_color="orange")
            self.btn_nueva_mascota.configure(state="disabled")
            return

        nombre_prop = self.propietario_seleccionado['nombre']
        cedula_prop = self.propietario_seleccionado['cedula'] 
        
        # Muestra la cédula del propietario seleccionado
        self.lbl_info_prop.configure(text=f"Propietario Actual: {nombre_prop} (Cédula: {cedula_prop})", text_color="white")
        self.btn_nueva_mascota.configure(state="normal")

        mascotas = self.admission_controller.obtener_mascotas_cliente(self.propietario_seleccionado['id_propietario'])
        
        if not mascotas:
            ctk.CTkLabel(self.listbox_mascotas, text=f"'{nombre_prop}' no tiene mascotas registradas.", text_color="gray").pack(pady=20)
            return

        for masc in mascotas:
            # Línea modificada: Eliminamos el ID de la mascota
            info_text = f"Nombre: {masc['nombre']} ({masc['especie']} | Raza: {masc['raza']})"
            ctk.CTkLabel(self.listbox_mascotas, text=info_text, anchor="w").pack(fill="x", padx=10, pady=5)

    def mostrar_formulario_mascota(self):
        if not self.propietario_seleccionado:
            return
            
        win = ctk.CTkToplevel(self)
        win.title("Nueva Mascota")
        win.geometry("400x400")

        ctk.CTkLabel(win, text=f"Mascota para: {self.propietario_seleccionado['nombre']}", font=("Roboto", 16, "bold")).pack(pady=10)

        entry_nombre = ctk.CTkEntry(win, placeholder_text="Nombre Mascota", width=300)
        entry_nombre.pack(pady=5)
        
        entry_especie = ctk.CTkEntry(win, placeholder_text="Especie (Perro, Gato, etc.)", width=300)
        entry_especie.pack(pady=5)
        
        entry_raza = ctk.CTkEntry(win, placeholder_text="Raza", width=300)
        entry_raza.pack(pady=5)
        
        entry_nacimiento = ctk.CTkEntry(win, placeholder_text="Fecha Nacimiento (YYYY-MM-DD)", width=300)
        entry_nacimiento.pack(pady=5)
        
        genero_var = ctk.StringVar(value="Macho")
        ctk.CTkOptionMenu(win, values=["Macho", "Hembra"], variable=genero_var).pack(pady=5)
        
        lbl_status = ctk.CTkLabel(win, text="")
        lbl_status.pack(pady=5)
        
        def guardar_mascota():
            id_propietario = self.propietario_seleccionado['id_propietario']
            exito = self.admission_controller.registrar_mascota(
                id_propietario,
                entry_nombre.get(),
                entry_especie.get(),
                entry_raza.get(),
                entry_nacimiento.get(),
                genero_var.get()
            )
            if exito:
                lbl_status.configure(text=f"Mascota '{entry_nombre.get()}' registrada.", text_color="green")
                self.actualizar_tab_mascotas()
                win.after(1500, win.destroy)
            else:
                lbl_status.configure(text="Error al registrar mascota.", text_color="red")
                
        ctk.CTkButton(win, text="Guardar Mascota", command=guardar_mascota).pack(pady=10)