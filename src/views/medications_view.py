import customtkinter as ctk
from controllers.medications_controller import MedicationsController
from tkinter import messagebox


class MedicationsView(ctk.CTkFrame):
    def __init__(self, master, controller=None, id_mascota=None, active_tab=None, switch_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.medications_controller = MedicationsController()
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        from models.producto_model import ProductoModel

        self.lbl_titulo = ctk.CTkLabel(
            self, text="Registrar Medicamento (Inventario)", font=("Roboto", 22, "bold")
        )
        self.lbl_titulo.pack(pady=10)

        # Campos para producto
        self.txt_nombre = ctk.CTkEntry(
            self, placeholder_text="Nombre del medicamento", width=400
        )
        self.txt_nombre.pack(pady=5)
        self.txt_precio_venta = ctk.CTkEntry(
            self, placeholder_text="Precio de venta", width=200
        )
        self.txt_precio_venta.pack(pady=5)
        self.txt_costo_unitario = ctk.CTkEntry(
            self, placeholder_text="Costo unitario", width=200
        )
        self.txt_costo_unitario.pack(pady=5)
        self.txt_stock_actual = ctk.CTkEntry(
            self, placeholder_text="Stock actual", width=200
        )
        self.txt_stock_actual.pack(pady=5)
        self.txt_fecha_vencimiento = ctk.CTkEntry(
            self, placeholder_text="Fecha de vencimiento (YYYY-MM-DD)", width=250
        )
        self.txt_fecha_vencimiento.pack(pady=5)

        # Bind Enter key
        self.txt_nombre.bind("<Return>", self.registrar_medicamento)
        self.txt_precio_venta.bind("<Return>", self.registrar_medicamento)
        self.txt_costo_unitario.bind("<Return>", self.registrar_medicamento)
        self.txt_stock_actual.bind("<Return>", self.registrar_medicamento)
        self.txt_fecha_vencimiento.bind("<Return>", self.registrar_medicamento)

        self.btn_guardar = ctk.CTkButton(
            self, text="Registrar Medicamento", command=self.registrar_medicamento
        )
        self.btn_guardar.pack(pady=15)

        self.lbl_alerta = ctk.CTkLabel(
            self, text="", text_color="red", font=("Roboto", 14, "bold")
        )
        self.lbl_alerta.pack(pady=5)

        # Mostrar alerta si algún producto tiene stock bajo
        self.mostrar_alerta_stock_bajo()

    def mostrar_alerta_stock_bajo(self):
        from models.producto_model import ProductoModel

        productos = ProductoModel.obtener_todos()
        bajos = [p["nombre"] for p in productos if p["stock_actual"] < 5]
        if bajos:
            self.lbl_alerta.configure(
                text=f"¡Alerta! Stock bajo en: {', '.join(bajos)}"
            )
        else:
            self.lbl_alerta.configure(text="")

    def registrar_medicamento(self, event=None):
        from models.producto_model import ProductoModel

        nombre = self.txt_nombre.get().strip()
        precio_venta = self.txt_precio_venta.get().strip()
        costo_unitario = self.txt_costo_unitario.get().strip()
        stock_actual = self.txt_stock_actual.get().strip()
        fecha_vencimiento = self.txt_fecha_vencimiento.get().strip()
        if not (
            nombre
            and precio_venta
            and costo_unitario
            and stock_actual
            and fecha_vencimiento
        ):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        try:
            precio_venta = float(precio_venta)
            costo_unitario = float(costo_unitario)
            stock_actual = int(stock_actual)
        except ValueError:
            messagebox.showerror("Error", "Precio, costo y stock deben ser numéricos.")
            return
        try:
            exito = ProductoModel.crear(
                nombre, precio_venta, costo_unitario, stock_actual, fecha_vencimiento
            )
            if exito:
                messagebox.showinfo("Éxito", "Medicamento registrado en inventario.")
                self.txt_nombre.delete(0, "end")
                self.txt_precio_venta.delete(0, "end")
                self.txt_costo_unitario.delete(0, "end")
                self.txt_stock_actual.delete(0, "end")
                self.txt_fecha_vencimiento.delete(0, "end")
                self.mostrar_alerta_stock_bajo()
            else:
                messagebox.showerror(
                    "Error", "Ocurrió un error al registrar el medicamento."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error en la base de datos: {e}")
