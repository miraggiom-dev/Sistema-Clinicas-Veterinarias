import customtkinter as ctk


class FarmaceutaView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        # CORRECCIÓN: Renombrar a 'controller'. En main.py se pasa 
        #             FarmaceutaController, por lo que este nombre es más apropiado.
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
        self.tab_ventas = self.vista_pestanas.add("Registrar Venta")
        self.tab_alertas = self.vista_pestanas.add("Alertas")

        self._configurar_tab_recetas()
        self._configurar_tab_inventario()
        self._configurar_tab_ventas()
        self._configurar_tab_alertas()

    def _configurar_tab_recetas(self):
        ctk.CTkLabel(
            self.tab_recetas,
            text="Recetas Veterinarias Pendientes",
            font=("Roboto", 18),
        ).pack(pady=20)
        btn_cargar = ctk.CTkButton(
            self.tab_recetas,
            text="Cargar Recetas",
            command=self._manejar_cargar_recetas,
        )
        btn_cargar.pack(pady=5)
        self.lbl_estado_recetas = ctk.CTkLabel(
            self.tab_recetas, text="[Listado de recetas pendientes]"
        )
        self.lbl_estado_recetas.pack(pady=10)

    def _manejar_cargar_recetas(self):
        recetas = self.controller.obtener_recetas_pendientes()
        if recetas:
            self.lbl_estado_recetas.configure(
                text=f"Recetas cargadas: {len(recetas)} pendientes."
            )
        else:
            self.lbl_estado_recetas.configure(text="No hay recetas pendientes.")

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
        self.frame_tabla_inventario.pack(pady=10, fill="x")
        # Mostrar la tabla de inventario automáticamente al cargar la pestaña
        self._mostrar_tabla_inventario()

    def _mostrar_tabla_inventario(self):
        # Limpiar el frame de la tabla
        for widget in self.frame_tabla_inventario.winfo_children():
            widget.destroy()
        # Obtener productos
        productos = self.controller.modelo.producto_model.get_all_products()
        headers = ["ID", "Nombre", "Stock", "Stock Mínimo", "Precio Venta", "Costo Unitario", "Vencimiento", "Acción"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.frame_tabla_inventario, text=h, font=("Roboto", 12, "bold")).grid(row=0, column=col, padx=5, pady=2)
        self._inventario_entries = {}
        for i, prod in enumerate(productos, start=1):
            row_entries = {}
            ctk.CTkLabel(self.frame_tabla_inventario, text=str(prod[0])).grid(row=i, column=0, padx=5, pady=2)  # ID
            ctk.CTkLabel(self.frame_tabla_inventario, text=str(prod[1])).grid(row=i, column=1, padx=5, pady=2)  # Nombre
            # Editable fields
            for j, field in zip(range(2, 7), ["stock_actual", "stock_minimo", "precio_venta", "costo_unitario", "fecha_vencimiento"]):
                entry = ctk.CTkEntry(self.frame_tabla_inventario, width=80)
                entry.insert(0, str(prod[j]))
                entry.grid(row=i, column=j, padx=5, pady=2)
                row_entries[field] = entry
            # Botón guardar
            btn = ctk.CTkButton(self.frame_tabla_inventario, text="Guardar", width=70,
                command=lambda pid=prod[0], e=row_entries: self._guardar_edicion_producto(pid, e))
            btn.grid(row=i, column=7, padx=5, pady=2)
            self._inventario_entries[prod[0]] = row_entries

    def _guardar_edicion_producto(self, id_producto, entries):
        # Obtener valores editados
        try:
            stock_actual = int(entries["stock_actual"].get())
            stock_minimo = int(entries["stock_minimo"].get())
            precio_venta = float(entries["precio_venta"].get())
            costo_unitario = float(entries["costo_unitario"].get())
            fecha_vencimiento = entries["fecha_vencimiento"].get()
        except Exception:
            ctk.CTkMessagebox(title="Error", message="Verifica los datos ingresados.", icon="cancel")
            return
        exito = self.controller.modelo.producto_model.actualizar_producto(
            id_producto, stock_actual, stock_minimo, precio_venta, costo_unitario, fecha_vencimiento
        )
        if exito:
            ctk.CTkMessagebox(title="Éxito", message="Producto actualizado.", icon="check")
            self._mostrar_tabla_inventario()
        else:
            ctk.CTkMessagebox(title="Error", message="No se pudo actualizar el producto.", icon="cancel")

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
                self._recargar_combo_productos()
                self._actualizar_alertas()

        ctk.CTkButton(modal, text="Registrar Producto", command=registrar).pack(pady=10)
        ctk.CTkButton(modal, text="Cerrar", command=modal.destroy).pack(pady=5)

    def _configurar_tab_ventas(self):
        ctk.CTkLabel(
            self.tab_ventas, text="Registro de Venta de Productos", font=("Roboto", 18)
        ).pack(pady=20)

        lista_productos_combo, self.mapeo_productos = (
            self.controller.obtener_lista_productos_para_venta()
        )

        frame_inputs = ctk.CTkFrame(self.tab_ventas, fg_color="transparent")
        frame_inputs.pack(pady=10)

        self.lbl_detalle_producto = ctk.CTkLabel(
            self.tab_ventas,
            text="Producto: Seleccione un producto para ver detalle",
            wraplength=400,
            justify="left",
            fg_color="#333333",
            corner_radius=5,
        )
        self.lbl_detalle_producto.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(frame_inputs, text="Producto:").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )

        self.combo_id_prod = ctk.CTkComboBox(
            frame_inputs,
            values=lista_productos_combo,
            width=300,
            command=self._manejar_seleccion_producto,
        )
        self.combo_id_prod.grid(row=0, column=1, padx=10, pady=5)

        if lista_productos_combo:
            self.combo_id_prod.set(lista_productos_combo[0])
            self._manejar_seleccion_producto(lista_productos_combo[0])
        else:
            self.combo_id_prod.set("No hay productos disponibles")

        ctk.CTkLabel(frame_inputs, text="Cantidad:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.entrada_cantidad = ctk.CTkEntry(frame_inputs, width=300)
        self.entrada_cantidad.grid(row=1, column=1, padx=10, pady=5)

        btn_venta = ctk.CTkButton(
            self.tab_ventas,
            text="Registrar Venta",
            command=self._manejar_registro_venta,
        )
        btn_venta.pack(pady=10)
        self.lbl_estado_venta = ctk.CTkLabel(self.tab_ventas, text="", text_color="white")
        self.lbl_estado_venta.pack(pady=5)

    def _obtener_id_seleccionado(self, valor_combo_seleccionado):
        """Usa el mapeo para obtener el ID real del producto."""
        return self.mapeo_productos.get(valor_combo_seleccionado, None)

    def _manejar_seleccion_producto(self, valor_seleccionado):
        """Maneja el evento de selección del ComboBox."""
        self._manejar_busqueda_producto(valor_seleccionado=valor_seleccionado)

    def _manejar_busqueda_producto(self, event=None, valor_seleccionado=None):
        """Busca el producto por ID y actualiza la etiqueta de detalle."""

        if valor_seleccionado is None:
            valor_seleccionado = self.combo_id_prod.get()

        id_producto = self._obtener_id_seleccionado(valor_seleccionado)

        if id_producto is None:
            self.lbl_detalle_producto.configure(
                text="Producto: Seleccione un producto válido", text_color="red"
            )
            return

        datos_producto = self.controller.obtener_datos_producto(id_producto)

        if datos_producto:
            nombre = datos_producto.get("nombre", "N/A")
            stock = datos_producto.get("stock", "N/A")
            vence = datos_producto.get("vence", "N/A")
            precio = datos_producto.get("precio", "N/A")

            detalle_text = (
                f"Nombre: {nombre}\n"
                f"Stock: {stock}\n"
                f"Precio: ${precio:.2f}\n"
                f"Vencimiento: {vence}\n"
            )
            self.lbl_detalle_producto.configure(text=detalle_text, text_color="white")
        else:
            self.lbl_detalle_producto.configure(
                text="Producto: ID no encontrado en inventario", text_color="red"
            )

    def _manejar_registro_venta(self):
        id_producto_combo = self.combo_id_prod.get()
        id_producto = self._obtener_id_seleccionado(id_producto_combo)

        if id_producto is None or id_producto == "" or id_producto == 0:
            self.lbl_estado_venta.configure(
                text="Error: Seleccione un producto válido de la lista.", text_color="red"
            )
            return

        cantidad = self.entrada_cantidad.get()
        if not cantidad.isdigit() or int(cantidad) <= 0:
            self.lbl_estado_venta.configure(
                text="Ingrese una cantidad válida (mayor a 0).", text_color="red"
            )
            return

        exito, mensaje = self.controller.registrar_venta(id_producto, cantidad)

        color = "green" if exito else "red"
        self.lbl_estado_venta.configure(text=mensaje, text_color=color)

        if exito:
            self._recargar_combo_productos()

            self._manejar_busqueda_producto(valor_seleccionado=id_producto_combo)

            self.entrada_cantidad.delete(0, "end")

            self._actualizar_alertas()

    def _recargar_combo_productos(self):
        """Recarga la lista del ComboBox después de una venta para reflejar el nuevo stock."""
        lista_productos_combo, self.mapeo_productos = (
            self.controller.obtener_lista_productos_para_venta()
        )

        valor_anterior = self.combo_id_prod.get()

        self.combo_id_prod.configure(values=lista_productos_combo)

        if valor_anterior in lista_productos_combo:
            self.combo_id_prod.set(valor_anterior)
        elif lista_productos_combo:
            self.combo_id_prod.set(lista_productos_combo[0])
        else:
            self.combo_id_prod.set("No hay productos disponibles")

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