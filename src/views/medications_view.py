import customtkinter as ctk
from controllers.medications_controller import MedicationsController
from tkinter import messagebox

class MedicationsView(ctk.CTkFrame):
    def __init__(self, master, controller=None, id_mascota=None, active_tab=None, switch_callback=None):
        super().__init__(master)
        self.medications_controller = MedicationsController()
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        

        self.center_frame = ctk.CTkFrame(
            self, 
            fg_color="#2a2a2a",
            corner_radius=15,
            border_width=1,
            border_color="#3a3a3a"
        )
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_titulo = ctk.CTkLabel(
            self.center_frame, 
            text="Registrar Medicamento (Inventario)", 
            font=("Roboto", 24, "bold"),
            text_color="#4a9eff"
        )
        self.lbl_titulo.pack(pady=(30, 20), padx=40)

        self.txt_nombre = ctk.CTkEntry(
            self.center_frame, 
            placeholder_text="Nombre del medicamento", 
            width=450,
            height=35,
            font=("Roboto", 12)
        )
        self.txt_nombre.pack(pady=8, padx=40)
        
        self.txt_precio_venta = ctk.CTkEntry(
            self.center_frame, 
            placeholder_text="Precio de venta", 
            width=450,
            height=35,
            font=("Roboto", 12)
        )
        self.txt_precio_venta.pack(pady=8, padx=40)
        
        self.txt_costo_unitario = ctk.CTkEntry(
            self.center_frame, 
            placeholder_text="Costo unitario", 
            width=450,
            height=35,
            font=("Roboto", 12)
        )
        self.txt_costo_unitario.pack(pady=8, padx=40)
        
        self.txt_stock_actual = ctk.CTkEntry(
            self.center_frame, 
            placeholder_text="Stock actual", 
            width=450,
            height=35,
            font=("Roboto", 12)
        )
        self.txt_stock_actual.pack(pady=8, padx=40)
        
        self.txt_fecha_vencimiento = ctk.CTkEntry(
            self.center_frame, 
            placeholder_text="Fecha de vencimiento (YYYY-MM-DD)", 
            width=450,
            height=35,
            font=("Roboto", 12)
        )
        self.txt_fecha_vencimiento.pack(pady=8, padx=40)

        self.txt_nombre.bind("<Return>", self.registrar_medicamento)
        self.txt_precio_venta.bind("<Return>", self.registrar_medicamento)
        self.txt_costo_unitario.bind("<Return>", self.registrar_medicamento)
        self.txt_stock_actual.bind("<Return>", self.registrar_medicamento)
        self.txt_fecha_vencimiento.bind("<Return>", self.registrar_medicamento)

        self.btn_guardar = ctk.CTkButton(
            self.center_frame, 
            text="Registrar Medicamento", 
            command=self.registrar_medicamento,
            height=40,
            width=450,
            fg_color="#2a5a8a",
            hover_color="#3a6a9a",
            font=("Roboto", 14, "bold")
        )
        self.btn_guardar.pack(pady=(20, 35), padx=40)

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
        import re
        if not re.match(r"^[a-zA-Z0-9\s]+$", nombre):
            messagebox.showerror("Error", "El nombre solo puede contener letras y números.")
            return

        try:
            precio_venta = float(precio_venta)
            if precio_venta < 0:
                messagebox.showerror("Error", "El precio de venta no puede ser negativo.")
                return
            costo_unitario = float(costo_unitario)
            if costo_unitario < 0:
                messagebox.showerror("Error", "El costo unitario no puede ser negativo.")
                return
            stock_actual = int(stock_actual)
            if stock_actual < 0:
                messagebox.showerror("Error", "El stock no puede ser negativo.")
                return
        except ValueError:
            messagebox.showerror("Error", "Precio y costo deben ser números reales, stock entero.")
            return

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_vencimiento):
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")
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
            else:
                messagebox.showerror(
                    "Error", "Ocurrió un error al registrar el medicamento."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error en la base de datos: {e}")
