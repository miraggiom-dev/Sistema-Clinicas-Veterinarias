import customtkinter as ctk
from tkinter import messagebox

class GestionPreciosView(ctk.CTkFrame):
    def __init__(self, master, controller, id_mascota=None, active_tab=None, switch_module_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.switch_module_callback = switch_module_callback
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(header, text="Gestión de Precios", font=("Roboto", 24, "bold")).pack(side="left")

        # Tabs
        self.tabview = ctk.CTkTabview(self, width=800)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.tab_productos = self.tabview.add("Productos")
        self.tab_servicios = self.tabview.add("Servicios")

        # Configure tabs layout
        self.tab_productos.grid_columnconfigure(0, weight=1)
        self.tab_productos.grid_rowconfigure(0, weight=1)
        self.tab_servicios.grid_columnconfigure(0, weight=1)
        self.tab_servicios.grid_rowconfigure(0, weight=1)

        self.crear_tabla_productos()
        self.crear_tabla_servicios()

    def crear_tabla_productos(self):
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self.tab_productos, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        productos = self.controller.obtener_productos()
        
        if not productos:
             ctk.CTkLabel(scroll, text="No hay productos.", text_color="gray").pack(pady=20)
             return

        # Headers
        headers_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(headers_frame, text="Producto", font=("Roboto", 12, "bold"), width=300, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(headers_frame, text="Precio Actual", font=("Roboto", 12, "bold"), width=100).pack(side="left", padx=10)
        ctk.CTkLabel(headers_frame, text="Nuevo Precio", font=("Roboto", 12, "bold"), width=120).pack(side="left", padx=10)

        for prod in productos:
            # Safe named access
            try:
                pid = prod['id_producto']
                nombre = prod['nombre']
                precio = prod['precio_venta']
            except Exception:
                # Fallback
                pid = prod[0]
                nombre = prod[1]
                precio = prod[2]

            card = ctk.CTkFrame(scroll, fg_color=("#ffffff", "#3a3a3a"), corner_radius=8)
            card.pack(fill="x", pady=5)

            ctk.CTkLabel(card, text=nombre, font=("Roboto", 14), anchor="w", width=300).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(card, text=f"${precio}", font=("Roboto", 14, "bold"), width=100).pack(side="left", padx=10)
            
            entry = ctk.CTkEntry(card, width=100, placeholder_text="0.00")
            entry.pack(side="left", padx=10)
            
            btn = ctk.CTkButton(card, text="Actualizar", width=100, 
                                command=lambda p=pid, e=entry, n=nombre: self.actualizar_precio_producto(p, e, n))
            btn.pack(side="right", padx=15)

    def crear_tabla_servicios(self):
        scroll = ctk.CTkScrollableFrame(self.tab_servicios, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        servicios = self.controller.obtener_servicios()
        
        if not servicios:
             ctk.CTkLabel(scroll, text="No hay servicios.", text_color="gray").pack(pady=20)
             return

        # Headers
        headers_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(headers_frame, text="Servicio", font=("Roboto", 12, "bold"), width=300, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(headers_frame, text="Precio Actual", font=("Roboto", 12, "bold"), width=100).pack(side="left", padx=10)
        ctk.CTkLabel(headers_frame, text="Nuevo Precio", font=("Roboto", 12, "bold"), width=120).pack(side="left", padx=10)

        for serv in servicios:
            try:
                sid = serv['id_servicio']
                nombre = serv['nombre']
                precio = serv['precio_base']
            except Exception:
                sid = serv[0]
                nombre = serv[1]
                precio = serv[3] # Index 3 is usually precio_base if 2 is tipo

            card = ctk.CTkFrame(scroll, fg_color=("#ffffff", "#3a3a3a"), corner_radius=8)
            card.pack(fill="x", pady=5)

            ctk.CTkLabel(card, text=nombre, font=("Roboto", 14), anchor="w", width=300).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(card, text=f"${precio}", font=("Roboto", 14, "bold"), width=100).pack(side="left", padx=10)
            
            entry = ctk.CTkEntry(card, width=100, placeholder_text="0.00")
            entry.pack(side="left", padx=10)
            
            btn = ctk.CTkButton(card, text="Actualizar", width=100, 
                                command=lambda s=sid, e=entry, n=nombre: self.actualizar_precio_servicio(s, e, n))
            btn.pack(side="right", padx=15)

    def actualizar_precio_producto(self, id_producto, entry_widget, nombre):
        nuevo_precio = entry_widget.get()
        try:
            nuevo_precio = float(nuevo_precio)
        except ValueError:
            self.mostrar_error(f"Precio inválido para {nombre}")
            return
        ok = self.controller.actualizar_precio_producto(id_producto, nuevo_precio)
        if ok:
            self.mostrar_actualizacion_exitosa("producto", nombre)
            # Refresh view ideally, but for now just clear entry
            entry_widget.delete(0, "end")
        else:
            self.mostrar_error(f"No se pudo actualizar el precio de {nombre}")

    def actualizar_precio_servicio(self, id_servicio, entry_widget, nombre):
        nuevo_precio = entry_widget.get()
        try:
            nuevo_precio = float(nuevo_precio)
        except ValueError:
            self.mostrar_error(f"Precio inválido para {nombre}")
            return
        ok = self.controller.actualizar_precio_servicio(id_servicio, nuevo_precio)
        if ok:
            self.mostrar_actualizacion_exitosa("servicio", nombre)
            entry_widget.delete(0, "end")
        else:
            self.mostrar_error(f"No se pudo actualizar el precio de {nombre}")

    def mostrar_actualizacion_exitosa(self, tipo, nombre):
        messagebox.showinfo("Éxito", f"Precio de {tipo} '{nombre}' actualizado correctamente.")

    def mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)
