
import customtkinter as ctk

class GestionPreciosView(ctk.CTkFrame):
    def __init__(self, master, controller, id_mascota=None, active_tab=None, switch_module_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.switch_module_callback = switch_module_callback
        self.pack_propagate(False)

        ctk.CTkLabel(self, text="Gestión de Precios", font=("Roboto", 28, "bold")).pack(pady=10)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_productos = self.tabview.add("Productos")
        self.tab_servicios = self.tabview.add("Servicios")

        self.crear_tabla_productos()
        self.crear_tabla_servicios()

    def crear_tabla_productos(self):
        productos = self.controller.obtener_productos()
        frame = ctk.CTkFrame(self.tab_productos)
        frame.pack(fill="both", expand=True)
        ctk.CTkLabel(frame, text="Nombre", width=200).grid(row=0, column=0)
        ctk.CTkLabel(frame, text="Precio Actual", width=100).grid(row=0, column=1)
        ctk.CTkLabel(frame, text="Nuevo Precio", width=100).grid(row=0, column=2)
        ctk.CTkLabel(frame, text="Acción", width=100).grid(row=0, column=3)
        self.producto_entries = {}
        for i, prod in enumerate(productos, start=1):
            ctk.CTkLabel(frame, text=prod[1], width=200).grid(row=i, column=0)
            ctk.CTkLabel(frame, text=str(prod[4]), width=100).grid(row=i, column=1)
            entry = ctk.CTkEntry(frame, width=100)
            entry.grid(row=i, column=2)
            btn = ctk.CTkButton(frame, text="Actualizar", width=100, command=lambda pid=prod[0], e=entry, n=prod[1]: self.actualizar_precio_producto(pid, e, n))
            btn.grid(row=i, column=3)
            self.producto_entries[prod[0]] = entry

    def crear_tabla_servicios(self):
        servicios = self.controller.obtener_servicios()
        frame = ctk.CTkFrame(self.tab_servicios)
        frame.pack(fill="both", expand=True)
        ctk.CTkLabel(frame, text="Nombre", width=200).grid(row=0, column=0)
        ctk.CTkLabel(frame, text="Precio Actual", width=100).grid(row=0, column=1)
        ctk.CTkLabel(frame, text="Nuevo Precio", width=100).grid(row=0, column=2)
        ctk.CTkLabel(frame, text="Acción", width=100).grid(row=0, column=3)
        self.servicio_entries = {}
        for i, serv in enumerate(servicios, start=1):
            ctk.CTkLabel(frame, text=serv[1], width=200).grid(row=i, column=0)
            ctk.CTkLabel(frame, text=str(serv[2]), width=100).grid(row=i, column=1)
            entry = ctk.CTkEntry(frame, width=100)
            entry.grid(row=i, column=2)
            btn = ctk.CTkButton(frame, text="Actualizar", width=100, command=lambda sid=serv[0], e=entry, n=serv[1]: self.actualizar_precio_servicio(sid, e, n))
            btn.grid(row=i, column=3)
            self.servicio_entries[serv[0]] = entry

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
        else:
            self.mostrar_error(f"No se pudo actualizar el precio de {nombre}")

    def mostrar_actualizacion_exitosa(self, tipo, nombre):
        ctk.CTkMessageBox(title="Éxito", message=f"Precio de {tipo} '{nombre}' actualizado correctamente.")

    def mostrar_error(self, mensaje):
        ctk.CTkMessageBox(title="Error", message=mensaje)
