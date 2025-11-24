import customtkinter as ctk
from controllers.treatment_controller import TreatmentController
from tkinter import messagebox


class TreatmentView(ctk.CTkFrame):
    def __init__(self, master, controller=None, id_mascota=None, active_tab=None, switch_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.treatment_controller = TreatmentController()
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        from models.mascota_model import MascotaModel
        from models.producto_model import ProductoModel

        self.lbl_titulo = ctk.CTkLabel(
            self, text="Registrar Receta (Tratamiento)", font=("Roboto", 22, "bold")
        )
        self.lbl_titulo.pack(pady=10)

        # Mascota
        self.mascotas = MascotaModel.obtener_todas_con_propietario()
        self.mascota_map = {
            f"{m['nombre']} (Dueño: {m['propietario_nombre']})": m
            for m in self.mascotas
        }
        self.cmb_mascota = ctk.CTkComboBox(
            self, values=list(self.mascota_map.keys()), width=300, state="readonly"
        )
        self.cmb_mascota.pack(pady=10)

        # Producto (medicamento)
        self.productos = ProductoModel.obtener_todos()
        self.producto_map = {
            f"{p['nombre']} (Stock: {p['stock_actual']})": p for p in self.productos
        }
        self.cmb_producto = ctk.CTkComboBox(
            self, values=list(self.producto_map.keys()), width=300, state="readonly"
        )
        self.cmb_producto.pack(pady=10)

        # Cantidad
        self.txt_cantidad = ctk.CTkEntry(
            self, placeholder_text="Cantidad a prescribir", width=200
        )
        self.txt_cantidad.pack(pady=5)

        # Bind Enter key
        self.txt_cantidad.bind("<Return>", self.registrar_tratamiento)

        self.btn_guardar = ctk.CTkButton(
            self, text="Registrar Receta", command=self.registrar_tratamiento
        )
        self.btn_guardar.pack(pady=15)

        self.lbl_alerta = ctk.CTkLabel(
            self, text="", text_color="red", font=("Roboto", 14, "bold")
        )
        self.lbl_alerta.pack(pady=5)
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
        # Validar stock
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
                self.mostrar_alerta_stock_bajo()
            else:
                messagebox.showerror(
                    "Error", "Ocurrió un error al registrar la receta."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error en la base de datos: {e}")
