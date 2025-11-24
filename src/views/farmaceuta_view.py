import customtkinter as ctk


class FarmaceutaView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        controller, 
        id_mascota=None,
        active_tab=None,
        switch_module_callback=None,
        **kwargs,
    ):

        super().__init__(master, **kwargs)
        
        self.controller = controller

        self.id_mascota = id_mascota
        self.active_tab = active_tab
        self.switch_module_callback = switch_module_callback

        self.mapeo_productos = {} 

        ctk.CTkLabel(self, text="MÓDULO DE FARMACIA", font=("Roboto", 24, "bold")).pack(
            pady=10
        )
        
        self.vista_pestanas = ctk.CTkTabview(self)
        self.vista_pestanas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tab_recetas = self.vista_pestanas.add("Ver Recetas")
        self.tab_inventario = self.vista_pestanas.add("Gestión de Inventario")
        self.tab_alertas = self.vista_pestanas.add("Alertas")

        self._configurar_tab_recetas()
        self._configurar_tab_inventario()
        self._configurar_tab_alertas()

    def _configurar_tab_recetas(self):
        ctk.CTkLabel(
            self.tab_recetas,
            text="Recetas Veterinarias Pendientes",
            font=("Roboto", 18, "bold"),
        ).pack(pady=10)

        btn_cargar = ctk.CTkButton(
            self.tab_recetas,
            text="Actualizar Lista",
            command=self._manejar_cargar_recetas,
        )
        btn_cargar.pack(pady=5)

        self.frame_lista_recetas = ctk.CTkScrollableFrame(self.tab_recetas, width=700, height=400)
        self.frame_lista_recetas.pack(pady=10, fill="both", expand=True)

        self.lbl_estado_recetas = ctk.CTkLabel(
            self.tab_recetas, text=""
        )
        self.lbl_estado_recetas.pack(pady=5)
        
        self._manejar_cargar_recetas()

    def _manejar_cargar_recetas(self):
        for widget in self.frame_lista_recetas.winfo_children():
            widget.destroy()

        recetas = self.controller.obtener_recetas_pendientes()
        
        if not recetas:
            self.lbl_estado_recetas.configure(text="No hay recetas pendientes.", text_color="green")
            return

        self.lbl_estado_recetas.configure(text=f"Recetas pendientes: {len(recetas)}", text_color="white")

        for r in recetas:
            self._crear_tarjeta_receta(r)

    def _crear_tarjeta_receta(self, receta):
        id_receta = receta[0]
        id_producto = receta[1]
        cantidad = receta[2]
        fecha = receta[3]
        mascota = receta[4]
        producto_nombre = receta[5]
        veterinario = receta[6]

        card = ctk.CTkFrame(self.frame_lista_recetas, fg_color="#2b2b2b", corner_radius=10)
        card.pack(pady=5, padx=10, fill="x")

        info_text = (
            f"Mascota: {mascota} | Vet: {veterinario}\n"
            f"Producto: {producto_nombre} (Cant: {cantidad})\n"
            f"Fecha: {fecha}"
        )
        ctk.CTkLabel(card, text=info_text, justify="left", font=("Roboto", 14)).pack(side="left", padx=10, pady=10)

        btn_despachar = ctk.CTkButton(
            card, 
            text="Despachar", 
            fg_color="green", 
            hover_color="darkgreen",
            command=lambda r=id_receta, p=id_producto, c=cantidad: self._manejar_despacho(r, p, c)
        )
        btn_despachar.pack(side="right", padx=10, pady=10)

    def _manejar_despacho(self, id_receta, id_producto, cantidad):
        id_farmaceuta = None
        if hasattr(self.controller, 'auth_controller') and self.controller.auth_controller.usuario_actual:
            id_farmaceuta = self.controller.auth_controller.usuario_actual.id_usuario
        elif hasattr(self.controller, 'usuario_actual'): 
             id_farmaceuta = self.controller.usuario_actual.id_usuario
        
        if id_farmaceuta is None:
             print("Advertencia: No se detectó usuario logueado. Usando ID 1 por defecto para pruebas.")
             id_farmaceuta = 1 

        exito, mensaje = self.controller.procesar_despacho(id_receta, id_producto, cantidad, id_farmaceuta)

        if exito:
            self.lbl_estado_recetas.configure(text=mensaje, text_color="green")
            self._manejar_cargar_recetas() 
            self._mostrar_tabla_inventario()
            self._actualizar_alertas()
        else:
            self.lbl_estado_recetas.configure(text=f"Error: {mensaje}", text_color="red")

    def _configurar_tab_inventario(self):
        ctk.CTkLabel(
            self.tab_inventario, text="Control de Inventario", font=("Roboto", 18)
        ).pack(pady=20)
        ctk.CTkButton(
            self.tab_inventario,
            text="Agregar Nuevo Producto",
            command=self._abrir_modal_agregar_producto
        ).pack(pady=5)
        ctk.CTkButton(
            self.tab_inventario,
            text="Ver/Editar Inventario",
            command=self._mostrar_tabla_inventario
        ).pack(pady=5)

        self.frame_tabla_inventario = ctk.CTkFrame(self.tab_inventario)
        self.frame_tabla_inventario.pack(pady=10, expand=True, anchor="center")
        self.lbl_estado_inventario = ctk.CTkLabel(self.tab_inventario, text="", text_color="green")
        self.lbl_estado_inventario.pack(pady=(0, 5))
        self._mostrar_tabla_inventario()

    def _mostrar_tabla_inventario(self):
        
        for widget in self.frame_tabla_inventario.winfo_children():
            widget.destroy()
            
        productos = self.controller.modelo.producto_model.get_all_products()
        headers = ["ID", "Nombre", "Stock", "Stock Mínimo", "Precio Venta", "Costo Unitario", "Vencimiento", "Acción"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.frame_tabla_inventario, text=h, font=("Roboto", 12, "bold")).grid(row=0, column=col, padx=5, pady=2)
        self._inventario_entries = {}
        for i, prod in enumerate(productos, start=1):
            row_entries = {}
            ctk.CTkLabel(self.frame_tabla_inventario, text=str(prod[0])).grid(row=i, column=0, padx=5, pady=2)  # ID
            ctk.CTkLabel(self.frame_tabla_inventario, text=str(prod[1])).grid(row=i, column=1, padx=5, pady=2)  # Nombre

            for j, field in zip(range(2, 7), ["stock_actual", "stock_minimo", "precio_venta", "costo_unitario", "fecha_vencimiento"]):
                entry = ctk.CTkEntry(self.frame_tabla_inventario, width=80)
                entry.insert(0, str(prod[j]))
                entry.grid(row=i, column=j, padx=5, pady=2)
                row_entries[field] = entry
            
            btn = ctk.CTkButton(self.frame_tabla_inventario, text="Guardar", width=70,
                command=lambda pid=prod[0], e=row_entries: self._guardar_edicion_producto(pid, e))
            btn.grid(row=i, column=7, padx=5, pady=2)
            self._inventario_entries[prod[0]] = row_entries

    def _guardar_edicion_producto(self, id_producto, entries):

        try:
            stock_actual = int(entries["stock_actual"].get())
            stock_minimo = int(entries["stock_minimo"].get())
            precio_venta = float(entries["precio_venta"].get())
            costo_unitario = float(entries["costo_unitario"].get())
            fecha_vencimiento = entries["fecha_vencimiento"].get()
        except Exception:
            self.lbl_estado_inventario.configure(text="Verifica los datos ingresados.", text_color="red")
            return
        exito = self.controller.modelo.producto_model.actualizar_producto(
            id_producto, stock_actual, stock_minimo, precio_venta, costo_unitario, fecha_vencimiento
        )
        if exito:
            self.lbl_estado_inventario.configure(text="Producto actualizado.", text_color="green")
            self._mostrar_tabla_inventario()
            self.after(2000, lambda: self.lbl_estado_inventario.configure(text=""))
        else:
            self.lbl_estado_inventario.configure(text="No se pudo actualizar el producto.", text_color="red")

    def _abrir_modal_agregar_producto(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Registrar Nuevo Producto")
        modal.geometry("400x420")
        modal.grab_set()

        labels = [
            ("Nombre", "nombre"),
            ("Precio de Venta", "precio_venta"),
            ("Costo Unitario", "costo_unitario"),
            ("Stock Inicial", "stock_actual"),
            ("Stock Mínimo", "stock_minimo"),
            ("Fecha de Vencimiento (YYYY-MM-DD)", "fecha_vencimiento"),
        ]
        entradas = {}
        for idx, (label, key) in enumerate(labels):
            ctk.CTkLabel(modal, text=label).pack(pady=(10 if idx == 0 else 5, 0))
            entry = ctk.CTkEntry(modal, width=300)
            entry.pack()
            entradas[key] = entry

        lbl_estado = ctk.CTkLabel(modal, text="")
        lbl_estado.pack(pady=10)

        def registrar():
            datos = {k: entradas[k].get() for _, k in labels}
            exito, mensaje = self.controller.registrar_producto(
                datos["nombre"],
                datos["precio_venta"],
                datos["costo_unitario"],
                datos["stock_actual"],
                datos["stock_minimo"],
                datos["fecha_vencimiento"],
            )
            color = "green" if exito else "red"
            lbl_estado.configure(text=mensaje, text_color=color)
            if exito:
                for entry in entradas.values():
                    entry.delete(0, "end")
                self._actualizar_alertas()

        ctk.CTkButton(modal, text="Registrar Producto", command=registrar).pack(pady=10)
        ctk.CTkButton(modal, text="Cerrar", command=modal.destroy).pack(pady=5)

    def _configurar_tab_alertas(self):
        ctk.CTkLabel(
            self.tab_alertas,
            text="Alertas Críticas de Inventario",
            font=("Roboto", 18, "bold"),
        ).pack(pady=20)

        self.lbl_stock_bajo = ctk.CTkLabel(
            self.tab_alertas,
            text="Productos Agotados/Bajo Stock: Cargando...",
            justify="left",
        )
        self.lbl_stock_bajo.pack(pady=5, padx=10, fill="x")

        self.lbl_por_vencer = ctk.CTkLabel(
            self.tab_alertas, text="Próximos a Vencer: Cargando...", justify="left"
        )
        self.lbl_por_vencer.pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(
            self.tab_alertas,
            text="Actualizar Alertas",
            command=self._actualizar_alertas,
        ).pack(pady=10)

        self._actualizar_alertas()

    def _actualizar_alertas(self):
        alertas = self.controller.obtener_alertas_inventario()

        conteo_stock_bajo = len(alertas.get("stock_bajo", []))
        conteo_por_vencer = len(alertas.get("por_vencer", []))

        if conteo_stock_bajo > 0:
            lista_stock_bajo = "\n".join(
                [
                    f"{p[0]} - {p[1]} ({p[2]} unid.)"
                    for p in alertas.get("stock_bajo", [])
                ]
            )
            self.lbl_stock_bajo.configure(
                text=f"Agotados ({conteo_stock_bajo}):\n{lista_stock_bajo}",
                text_color="red",
            )
        else:
            self.lbl_stock_bajo.configure(
                text="No hay productos con stock crítico.", text_color="green"
            )

        if conteo_por_vencer > 0:
            lista_por_vencer = "\n".join(
                [f"{p[0]} - {p[1]} ({p[2]})" for p in alertas.get("por_vencer", [])]
            )
            self.lbl_por_vencer.configure(
                text=f"Próximos a Vencer ({conteo_por_vencer}):\n{lista_por_vencer}",
                text_color="orange",
            )
        else:
            self.lbl_por_vencer.configure(
                text="No hay productos próximos a vencer.", text_color="green"
            )