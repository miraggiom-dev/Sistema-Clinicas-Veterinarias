import customtkinter as ctk
from tkinter import messagebox


class TreatmentView(ctk.CTkFrame):
    def __init__(self, master, controller=None, id_mascota=None, active_tab=None, switch_callback=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        from models.mascota_model import MascotaModel
        from models.producto_model import ProductoModel

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
            text="Registrar Receta (Tratamiento)", 
            font=("Roboto", 24, "bold"),
            text_color="#4a9eff"
        )
        self.lbl_titulo.pack(pady=(30, 20), padx=40)

        self.mascotas = MascotaModel.obtener_todas_con_propietario()
        self.mascota_map = {
            f"{m['nombre']} (Dueño: {m['propietario_nombre']})": m
            for m in self.mascotas
        }
        
        ctk.CTkLabel(
            self.center_frame,
            text="Seleccionar Mascota:",
            font=("Roboto", 12),
            text_color="#aaaaaa"
        ).pack(anchor="w", padx=40, pady=(10, 5))
        
        self.cmb_mascota = ctk.CTkComboBox(
            self.center_frame, 
            values=list(self.mascota_map.keys()), 
            width=450, 
            height=35,
            state="readonly",
            font=("Roboto", 12)
        )
        self.cmb_mascota.pack(pady=(0, 15), padx=40)

        self.productos = ProductoModel.obtener_todos()
        self.producto_map = {
            f"{p['nombre']} (Stock: {p['stock_actual']})": p for p in self.productos
        }
        
        ctk.CTkLabel(
            self.center_frame,
            text="Seleccionar Medicamento:",
            font=("Roboto", 12),
            text_color="#aaaaaa"
        ).pack(anchor="w", padx=40, pady=(10, 5))
        
        self.cmb_producto = ctk.CTkComboBox(
            self.center_frame, 
            values=list(self.producto_map.keys()), 
            width=450, 
            height=35,
            state="readonly",
            font=("Roboto", 12)
        )
        self.cmb_producto.pack(pady=(0, 15), padx=40)

        self.txt_cantidad = ctk.CTkEntry(
            self.center_frame, 
            placeholder_text="Cantidad a prescribir", 
            width=450,
            height=35,
            font=("Roboto", 12)
        )
        self.txt_cantidad.pack(pady=8, padx=40)

        self.txt_cantidad.bind("<Return>", self.registrar_tratamiento)

        self.btn_guardar = ctk.CTkButton(
            self.center_frame, 
            text="Registrar Receta", 
            command=self.registrar_tratamiento,
            height=40,
            width=450,
            fg_color="#2a5a8a",
            hover_color="#3a6a9a",
            font=("Roboto", 14, "bold")
        )
        self.btn_guardar.pack(pady=(20, 35), padx=40)

    def registrar_tratamiento(self, event=None):
        from models.cita_model import CitaModel
        from models.diagnostico_model import DiagnosticoModel
        from models.receta_model import RecetaModel
        from models.producto_model import ProductoModel
        from tkinter import END

        mascota_key = self.cmb_mascota.get()
        producto_key = self.cmb_producto.get()
        cantidad = self.txt_cantidad.get().strip()
        if not mascota_key or mascota_key not in self.mascota_map:
            messagebox.showerror("Error", "Seleccione una mascota válida.")
            return
        if not producto_key or producto_key not in self.producto_map:
            messagebox.showerror("Error", "Seleccione un producto válido.")
            return
        if not cantidad:
            messagebox.showerror("Error", "Ingrese la cantidad a prescribir.")
            return
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return
        mascota = self.mascota_map[mascota_key]
        id_mascota = mascota["id_mascota"]
        cita = CitaModel.obtener_ultima_por_mascota(id_mascota)
        if not cita:
            messagebox.showerror(
                "Error", "La mascota seleccionada no tiene citas registradas."
            )
            return
        id_cita = cita["id_cita"]
        diagnostico = DiagnosticoModel.obtener_actual_por_cita(id_cita)
        if not diagnostico:
            messagebox.showerror(
                "Error", "No hay diagnóstico vigente para la última cita de la mascota."
            )
            return
        id_diagnostico = diagnostico["id_diagnostico"]
        producto = self.producto_map[producto_key]
        id_producto = producto["id_producto"]

        if producto["stock_actual"] < cantidad:
            messagebox.showerror(
                "Error", f"Stock insuficiente. Stock actual: {producto['stock_actual']}"
            )
            return
        try:
            exito = RecetaModel.crear(id_diagnostico, id_producto, cantidad)
            if exito:
                ProductoModel.descontar_stock(id_producto, cantidad)
                messagebox.showinfo("Éxito", "Receta registrada correctamente.")
                self.txt_cantidad.delete(0, END)
            else:
                messagebox.showerror(
                    "Error", "Ocurrió un error al registrar la receta."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error en la base de datos: {e}")
