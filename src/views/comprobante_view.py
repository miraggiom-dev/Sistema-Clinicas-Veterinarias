import customtkinter as ctk
from controllers.comprobante_controller import ComprobanteController
from database.connection import get_db_connection
import os
import webbrowser


class ComprobanteView(ctk.CTkToplevel):
    """Ventana simple para generar comprobantes de cita por ID."""
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Generar Comprobante")
        self.geometry("420x220")
        self.attributes('-topmost', True)
        self.focus_force()
        if master:
            try:
                self.transient(master)
            except Exception:
                pass
        try:
            frame_bg = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        except Exception:
            frame_bg = None

        container = ctk.CTkFrame(self, fg_color=frame_bg)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(container, text="Generar comprobante de cita", font=("Roboto", 16, "bold")).pack(pady=6)

        ctk.CTkLabel(container, text="Seleccione la cita:").pack(anchor="w", pady=(8,2))
        self._map_label_to_id = {}
        self._citas_labels = []
        self.opt_citas = ctk.CTkOptionMenu(container, values=self._citas_labels, width=300)
        self.opt_citas.pack(pady=4)
        self._cargar_citas()

        self.lbl_status = ctk.CTkLabel(container, text="", text_color="green")
        self.lbl_status.pack(pady=6)

        btn_frame = ctk.CTkFrame(container, fg_color=frame_bg)
        btn_frame.pack(fill="x", pady=6)

        ctk.CTkButton(btn_frame, text="Generar", command=self._generar).pack(side="right", padx=6)
        ctk.CTkButton(btn_frame, text="Abrir carpeta", command=self._abrir_carpeta).pack(side="right")

    def _generar(self):
        sel = None
        try:
            sel = self.opt_citas.get()
        except Exception:
            sel = None

        if not sel:
            self.lbl_status.configure(text="Seleccione una cita.", text_color="red")
            return

        cid = self._map_label_to_id.get(sel)
        if not cid:
            self.lbl_status.configure(text="Cita inválida seleccionada.", text_color="red")
            return

        ruta = ComprobanteController.generar_comprobante_pdf(cid)
        if ruta:
            name = os.path.basename(ruta)
            if name.lower().endswith('.pdf'):
                msg = f"Comprobante PDF generado: {name}"
            else:
                msg = f"Comprobante generado (texto): {name}"
            self.lbl_status.configure(text=msg, text_color="green")
            try:
                webbrowser.open('file://' + os.path.abspath(ruta))
            except Exception:
                pass
        else:
            self.lbl_status.configure(text="No se pudo generar comprobante.", text_color="red")

    def _cargar_citas(self):
        # Cargar citas que no estén canceladas
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = '''
                SELECT c.id_cita, c.fecha_hora, m.nombre AS mascota, p.nombre AS propietario
                FROM citas c
                LEFT JOIN mascotas m ON c.id_mascota = m.id_mascota
                LEFT JOIN propietarios p ON m.id_propietario = p.id_propietario
                WHERE c.estado != 'Cancelada'
                ORDER BY c.fecha_hora ASC
            '''
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
        except Exception:
            rows = []

        self._map_label_to_id.clear()
        self._citas_labels.clear()
        for r in rows:
            try:
                cid = r['id_cita']
                fh = r['fecha_hora']
                mascota = r['mascota'] or ''
                propietario = r['propietario'] or ''
                label = f"{cid} - {fh} - {mascota} ({propietario})"
            except Exception:
                # tuple fallback
                cid = r[0]
                fh = r[1]
                mascota = r[2] if len(r) > 2 else ''
                propietario = r[3] if len(r) > 3 else ''
                label = f"{cid} - {fh} - {mascota} ({propietario})"
            self._map_label_to_id[label] = cid
            self._citas_labels.append(label)

        if not self._citas_labels:
            self._citas_labels = ["-- No hay citas --"]
            self.opt_citas.configure(values=self._citas_labels)
            self.opt_citas.set(self._citas_labels[0])
        else:
            self.opt_citas.configure(values=self._citas_labels)
            self.opt_citas.set(self._citas_labels[0])

    def _abrir_carpeta(self):
        # Abrir la carpeta de comprobantes dentro de la raíz del proyecto
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        base = os.path.join(project_root, 'comprobantes')
        try:
            os.makedirs(base, exist_ok=True)
            webbrowser.open('file://' + os.path.abspath(base))
        except Exception:
            pass
