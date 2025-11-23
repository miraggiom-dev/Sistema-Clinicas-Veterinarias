import customtkinter as ctk
from functools import partial
from models.cita_model import CitaModel
from models.usuario_model import UsuarioModel
from models.mascota_model import MascotaModel
from models.servicio_model import ServicioModel
from controllers.admission_controller import AdmissionController

class AppointmentView(ctk.CTkFrame):
    """Vista para gestionar citas: ver agenda del día, agendar y cancelar."""
    def __init__(self, master, auth_controller, id_mascota=None, active_tab=None, switch_callback=None):
        
        self.prefill_mascota = id_mascota
        self._requested_active_tab = active_tab
        self.switch_callback = switch_callback

        super().__init__(master)
        self.auth_controller = auth_controller

        try:
            default_frame_bg = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            self.configure(fg_color=default_frame_bg)
            self._frame_bg = default_frame_bg
        except Exception:
            self._frame_bg = None

        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.tabview = ctk.CTkTabview(self, width=800)
        self.tabview.pack(fill="both", expand=True)
        self.tabview.add("Agenda")
        self.tabview.add("Agendar")

        self._crear_tab_agenda(self.tabview.tab("Agenda"))
        self._crear_tab_agendar(self.tabview.tab("Agendar"))

        self.admission_controller = AdmissionController()

        try:
            self._cargar_propietarios()
        except Exception:
            pass

        if getattr(self, '_requested_active_tab', None) in ("Agenda", "Agendar"):
            try:
                self.tabview.set(self._requested_active_tab)
            except Exception:
                pass

        self._cargar_veterinarios()

        try:
            self._cargar_servicios()
        except Exception:
            pass

    def _crear_tab_agenda(self, tab):

        frame_bg = getattr(self, '_frame_bg', None)
        container = ctk.CTkFrame(tab, fg_color=frame_bg)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        frame_top = ctk.CTkFrame(container, fg_color=frame_bg)
        frame_top.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_top, text="Fecha (YYYY-MM-DD):").pack(side="left", padx=(10,4))
        self.entry_fecha = ctk.CTkEntry(frame_top, width=150)
        self.entry_fecha.pack(side="left", padx=4)

        btn_cargar = ctk.CTkButton(frame_top, text="Cargar Agenda", command=self.cargar_agenda)
        btn_cargar.pack(side="left", padx=8)

        self.lista_agenda = ctk.CTkScrollableFrame(container, label_text="Agenda del Día", fg_color=frame_bg)
        self.lista_agenda.pack(fill="both", expand=True, padx=10, pady=10)

    def cargar_agenda(self):
        fecha = self.entry_fecha.get().strip()
        frame_bg = getattr(self, '_frame_bg', None)
        for w in self.lista_agenda.winfo_children():
            w.destroy()

        if not fecha:
            ctk.CTkLabel(self.lista_agenda, text="Ingrese una fecha válida.", text_color="orange").pack(pady=10)
            return

        rows = CitaModel.obtener_agenda_del_dia(fecha)
        if not rows:
            ctk.CTkLabel(self.lista_agenda, text="No hay citas para esta fecha.", text_color="gray").pack(pady=10)
            return

        try:
            self._last_loaded_fecha = fecha
        except Exception:
            self._last_loaded_fecha = None

        for r in rows:
            frame = ctk.CTkFrame(self.lista_agenda, fg_color=frame_bg)
            frame.pack(fill="x", pady=5, padx=5)
            texto = f"{r['hora_inicio']} - {r['hora_fin']} | Mascota: {r['mascota']} | Vet: {r['veterinario']} | Servicio: {r['servicio']} | Estado: {r['estado']}"
            ctk.CTkLabel(frame, text=texto, anchor="w").pack(side="left", padx=6)
            btn_edit = ctk.CTkButton(frame, text="Editar", width=90, command=partial(self._abrir_modal_editar, r))
            btn_edit.pack(side="right", padx=6)

            try:
                id_c = r['id_cita']
            except Exception:
                id_c = None
            btn_cancel = ctk.CTkButton(frame, text="Cancelar", width=90, command=partial(self._cancelar_cita, id_c))
            btn_cancel.pack(side="right", padx=6)

    def _cancelar_cita(self, id_cita):
        exito = CitaModel.cancelar(id_cita)
        if exito:
            self.cargar_agenda()

    def _crear_tab_agendar(self, tab):

        frame_bg = getattr(self, '_frame_bg', None)
        container = ctk.CTkFrame(tab, fg_color=frame_bg)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        frame = ctk.CTkFrame(container, fg_color=frame_bg)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Propietario:").grid(row=0, column=0, sticky="w", pady=10, padx=(0,12))
        self.prop_var = ctk.StringVar()
        self.opt_propietarios = ctk.CTkOptionMenu(frame, values=["Cargando..."], variable=self.prop_var)
        self.opt_propietarios.grid(row=0, column=1, pady=10, sticky="w")
        ctk.CTkButton(frame, text="Nuevo Propietario", width=140, command=self._crear_modal_propietario).grid(row=0, column=2, padx=8)

        ctk.CTkLabel(frame, text="Mascota:").grid(row=1, column=0, sticky="w", pady=10)
        self.masc_var = ctk.StringVar()
        self.opt_mascotas = ctk.CTkOptionMenu(frame, values=["Seleccione propietario"], variable=self.masc_var)
        self.opt_mascotas.grid(row=1, column=1, pady=10, sticky="w")
        ctk.CTkButton(frame, text="Nueva Mascota", width=140, command=self._crear_modal_mascota).grid(row=1, column=2, padx=8)

        ctk.CTkLabel(frame, text="Veterinario:").grid(row=2, column=0, sticky="w", pady=10)
        self.vet_var = ctk.StringVar()
        self.opt_veterinarios = ctk.CTkOptionMenu(frame, values=["Cargando..."], variable=self.vet_var)
        self.opt_veterinarios.grid(row=2, column=1, pady=10, sticky="w")

        ctk.CTkLabel(frame, text="Servicio:").grid(row=3, column=0, sticky="w", pady=10)
        self.serv_var = ctk.StringVar()
        self.opt_servicios = ctk.CTkOptionMenu(frame, values=["Cargando..."], variable=self.serv_var)
        self.opt_servicios.grid(row=3, column=1, pady=10, sticky="w")

        ctk.CTkLabel(frame, text="Fecha de la cita (YYYY-MM-DD):").grid(row=4, column=0, sticky="w", pady=6)
        self.date_picker = ctk.CTkEntry(frame, width=120)
        self.date_picker.grid(row=4, column=1, sticky="w", pady=6)

        ctk.CTkLabel(frame, text="Hora inicio:").grid(row=4, column=2, sticky="w", padx=(12,0))
        hours = [f"{h:02d}" for h in range(0,24)]
        minutes = ["00","15","30","45"]
        self.start_hour_var = ctk.StringVar(value=hours[9])
        self.start_min_var = ctk.StringVar(value=minutes[0])
        self.opt_start_hour = ctk.CTkOptionMenu(frame, values=hours, variable=self.start_hour_var, width=70)
        self.opt_start_hour.grid(row=4, column=3, sticky="w")
        self.opt_start_min = ctk.CTkOptionMenu(frame, values=minutes, variable=self.start_min_var, width=70)
        self.opt_start_min.grid(row=4, column=4, sticky="w", padx=(6,0))


        ctk.CTkLabel(frame, text="Motivo:").grid(row=6, column=0, sticky="w", pady=10)
        self.entry_motivo = ctk.CTkEntry(frame, width=220)
        self.entry_motivo.grid(row=6, column=1, pady=10, sticky="ew")

        try:
            frame.grid_columnconfigure(1, weight=1)
        except Exception:
            pass

        self.lbl_status = ctk.CTkLabel(frame, text="", text_color="green")
        self.lbl_status.grid(row=7, column=0, columnspan=3, pady=12)

        btn_agendar = ctk.CTkButton(frame, text="Agendar Cita", command=self.agendar_cita)
        btn_agendar.grid(row=8, column=0, columnspan=3, pady=14)

    def _cargar_veterinarios(self):
        users = UsuarioModel.obtener_todos()

        def _val(item, key):
            try:
                return item[key]
            except Exception:
                try:
                    return getattr(item, key)
                except Exception:
                    return None

        vets = []
        self._vet_map = {}
        if users:
            for u in users:
                rv = _val(u, 'rol')
                if rv is None:
                    continue
                try:
                    if str(rv).strip().lower() == 'veterinario':
                        uid = _val(u, 'id_usuario')
                        nombre = _val(u, 'nombre_completo')
                        if uid is not None and nombre is not None:
                            vets.append((uid, nombre))
                            try:
                                self._vet_map[uid] = nombre
                            except Exception:
                                pass
                except Exception:
                    continue

        valores = [f"{v[0]} - {v[1]}" for v in vets]
        if not valores:
            valores = ["No hay veterinarios"]
        try:
            self.opt_veterinarios.configure(values=valores)
            if valores:
                self.vet_var.set(valores[0])
        except Exception:
            pass

    def _cargar_servicios(self):
        """Carga los servicios activos en el option menu de la pestaña Agendar."""
        try:
            rows = ServicioModel.obtener_todos(True) or []
        except Exception:
            rows = []

        valores = []
        self._serv_map = {}
        for r in rows:
            try:
                sid = r['id_servicio'] if isinstance(r, dict) else r[0]
                nombre = r.get('nombre') if isinstance(r, dict) else r[1]
                dur = r.get('duracion_estimada') if isinstance(r, dict) else (r[4] if len(r) > 4 else None)
                self._serv_map[sid] = {'nombre': nombre, 'duracion': dur}
                valores.append(f"{sid} - {nombre}")
            except Exception:
                continue

        if not valores:
            valores = ["No hay servicios"]

        try:
            self.opt_servicios.configure(values=valores)
            self.serv_var.set(valores[0])
        except Exception:
            pass

    def _crear_modal_servicio(self):
        win = ctk.CTkToplevel(self)
        win.title("Nuevo Servicio")
        win.geometry("420x380")

        ctk.CTkLabel(win, text="Registrar Servicio", font=("Roboto", 16, "bold")).pack(pady=8)

        entry_nombre = ctk.CTkEntry(win, placeholder_text="Nombre del Servicio", width=360)
        entry_nombre.pack(pady=6)
        entry_precio = ctk.CTkEntry(win, placeholder_text="Precio base", width=360)
        entry_precio.pack(pady=6)
        entry_costo = ctk.CTkEntry(win, placeholder_text="Costo mano de obra", width=360)
        entry_costo.pack(pady=6)
        entry_duracion = ctk.CTkEntry(win, placeholder_text="Duración estimada (minutos)", width=360)
        entry_duracion.pack(pady=6)

        lbl_status = ctk.CTkLabel(win, text="")
        lbl_status.pack(pady=6)

        """ def guardar_s():
            nombre = entry_nombre.get().strip()
            try:
                precio = entry_precio.get().strip() or 0.0
            except Exception:
                precio = 0.0
            try:
                costo = entry_costo.get().strip() or 0.0
            except Exception:
                costo = 0.0
            try:
                dur = entry_duracion.get().strip() or 30
            except Exception:
                dur = 30

            if not nombre:
                lbl_status.configure(text="El nombre es obligatorio.", text_color="red")
                return

            nid = ServicioModel.crear(nombre, precio, costo, dur)
            if nid:
                lbl_status.configure(text="Servicio creado.", text_color="green")
                win.after(500, win.destroy)
                try:
                    self._cargar_servicios()
                    formatted = f"{nid} - {nombre}"
                    self.serv_var.set(formatted)
                except Exception:
                    pass
            else:
                lbl_status.configure(text="Error creando servicio.", text_color="red")

        ctk.CTkButton(win, text="Guardar Servicio", command=guardar_s).pack(pady=10) """

    def _cargar_propietarios(self):
        """Carga los propietarios en el option menu de la pestaña Agendar."""
        try:
            rows = self.admission_controller.buscar_clientes("") or []
        except Exception:
            rows = []

        valores = []
        for r in rows:
            try:
                pid = r['id_propietario']
                nombre = r.get('nombre') if isinstance(r, dict) else r['nombre']
                ced = r.get('cedula') if isinstance(r, dict) else r['cedula']
                valores.append(f"{pid} - {nombre} ({ced})")
            except Exception:
                continue

        if not valores:
            valores = ["No hay propietarios"]

        try:
            self.opt_propietarios.configure(values=valores)
            self.prop_var.set(valores[0])
        except Exception:
            pass

        try:
            self.prop_var.trace_add('write', self._on_propietario_selected)
        except Exception:
            try:
                self.prop_var.trace('w', self._on_propietario_selected)
            except Exception:
                pass

    def _on_propietario_selected(self, *args):
        sel = self.prop_var.get() if getattr(self, 'prop_var', None) else None
        if not sel:
            return
        if sel.startswith("No hay"):
            try:
                self.lbl_status.configure(text="No hay propietarios. Use 'Nuevo Propietario' para crear uno.", text_color="orange")
            except Exception:
                pass
            return
        # parse id
        try:
            pid = int(sel.split('-')[0].strip())
        except Exception:
            return
        self._cargar_mascotas(pid)

    def _cargar_mascotas(self, id_propietario):
        """Carga las mascotas de un propietario en el option menu."""
        try:
            rows = self.admission_controller.obtener_mascotas_cliente(id_propietario) or []
        except Exception:
            rows = []

        valores = []
        for m in rows:
            try:
                mid = m['id_mascota']
                nombre = m.get('nombre') if isinstance(m, dict) else m['nombre']
                valores.append(f"{mid} - {nombre}")
            except Exception:
                continue

        if not valores:
            valores = ["No hay mascotas"]

        try:
            self.opt_mascotas.configure(values=valores)
            self.masc_var.set(valores[0])
        except Exception:
            pass

    def _crear_modal_propietario(self):
        win = ctk.CTkToplevel(self)
        win.title("Nuevo Propietario")
        win.geometry("420x380")

        ctk.CTkLabel(win, text="Registrar Cliente", font=("Roboto", 16, "bold")).pack(pady=8)

        entry_cedula = ctk.CTkEntry(win, placeholder_text="Cédula/Documento de Identidad", width=360)
        entry_cedula.pack(pady=6)
        entry_nombre = ctk.CTkEntry(win, placeholder_text="Nombre Completo", width=360)
        entry_nombre.pack(pady=6)
        entry_tel = ctk.CTkEntry(win, placeholder_text="Teléfono", width=360)
        entry_tel.pack(pady=6)
        entry_email = ctk.CTkEntry(win, placeholder_text="Email", width=360)
        entry_email.pack(pady=6)
        entry_dir = ctk.CTkEntry(win, placeholder_text="Dirección", width=360)
        entry_dir.pack(pady=6)

        lbl_status = ctk.CTkLabel(win, text="")
        lbl_status.pack(pady=6)

        def guardar():
            ced = entry_cedula.get().strip() or 'N/A'
            nombre = entry_nombre.get().strip()
            telefono = entry_tel.get().strip()
            email = entry_email.get().strip()
            direccion = entry_dir.get().strip()
            nid = self.admission_controller.registrar_nuevo_cliente(ced, nombre, telefono, email, direccion)
            if nid:
                lbl_status.configure(text="Cliente registrado.", text_color="green")
                win.after(600, win.destroy)
                # recargar y seleccionar
                self._cargar_propietarios()
                try:
                    formatted = f"{nid} - {nombre} ({ced})"
                    self.prop_var.set(formatted)
                except Exception:
                    pass
            else:
                lbl_status.configure(text="Error al registrar cliente.", text_color="red")

        ctk.CTkButton(win, text="Guardar Cliente", command=guardar).pack(pady=10)

    def _crear_modal_mascota(self):
        # necesita propietario seleccionado
        sel = self.prop_var.get() if getattr(self, 'prop_var', None) else None
        if not sel or "-" not in sel:
            self.lbl_status.configure(text="Seleccione primero un propietario.", text_color="red")
            return
        try:
            pid = int(sel.split('-')[0].strip())
        except Exception:
            self.lbl_status.configure(text="Propietario inválido.", text_color="red")
            return

        win = ctk.CTkToplevel(self)
        win.title("Nueva Mascota")
        win.geometry("420x380")

        ctk.CTkLabel(win, text="Registrar Mascota", font=("Roboto", 16, "bold")).pack(pady=8)

        entry_nombre = ctk.CTkEntry(win, placeholder_text="Nombre Mascota", width=360)
        entry_nombre.pack(pady=6)
        entry_especie = ctk.CTkEntry(win, placeholder_text="Especie (Perro, Gato, etc.)", width=360)
        entry_especie.pack(pady=6)
        entry_raza = ctk.CTkEntry(win, placeholder_text="Raza", width=360)
        entry_raza.pack(pady=6)
        entry_nacimiento = ctk.CTkEntry(win, placeholder_text="Fecha Nacimiento (YYYY-MM-DD)", width=360)
        entry_nacimiento.pack(pady=6)
        genero_var = ctk.StringVar(value="Macho")
        ctk.CTkOptionMenu(win, values=["Macho", "Hembra"], variable=genero_var).pack(pady=6)

        lbl_status = ctk.CTkLabel(win, text="")
        lbl_status.pack(pady=6)

        def guardar_m():
            nombre = entry_nombre.get().strip()
            especie = entry_especie.get().strip()
            raza = entry_raza.get().strip()
            nacimiento = entry_nacimiento.get().strip()
            genero = genero_var.get()
            ex = self.admission_controller.registrar_mascota(pid, nombre, especie, raza, nacimiento, genero)
            if ex:
                lbl_status.configure(text="Mascota registrada.", text_color="green")
                win.after(600, win.destroy)
                self._cargar_mascotas(pid)
            else:
                lbl_status.configure(text="Error al registrar mascota.", text_color="red")

        ctk.CTkButton(win, text="Guardar Mascota", command=guardar_m).pack(pady=10)

    def _abrir_modal_editar(self, row):
        """Abre modal para editar una cita existente con selectores de fecha (texto) y hora."""
        def _val(item, key, default=None):
            try:
                return item[key]
            except Exception:
                try:
                    # si es dict-like
                    return item.get(key, default)
                except Exception:
                    try:
                        return getattr(item, key)
                    except Exception:
                        return default

        id_cita = _val(row, 'id_cita')
        if id_cita is None:
            return
        hora_ini = _val(row, 'hora_inicio', '09:00:00')
        hora_fin = _val(row, 'hora_fin', '10:00:00')
        motivo = _val(row, 'motivo', '')

        win = ctk.CTkToplevel(self)
        win.title(f"Editar Cita #{id_cita}")
        win.geometry("420x360")
        try:
            win.transient(self)
            win.grab_set()
        except Exception:
            pass

        frame_bg = getattr(self, '_frame_bg', None)
        container = ctk.CTkFrame(win, fg_color=frame_bg)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(container, text=f"Editar Cita #{id_cita}", font=("Roboto", 16, "bold")).pack(pady=6)

        # Fecha
        ctk.CTkLabel(container, text="Fecha (YYYY-MM-DD):").pack(pady=(8,2), anchor="w")
        dp = ctk.CTkEntry(container, width=300)
        dp.pack(pady=4)
        try:
            if hasattr(self, '_last_loaded_fecha') and getattr(self, '_last_loaded_fecha'):
                dp.insert(0, self._last_loaded_fecha)
        except Exception:
            pass

        # Hora (en una fila)
        row_h = ctk.CTkFrame(container, fg_color=frame_bg)
        row_h.pack(fill="x", pady=6)
        ctk.CTkLabel(row_h, text="Hora inicio:").pack(side="left", padx=(0,8))
        hours = [f"{h:02d}" for h in range(0,24)]
        minutes = ["00","15","30","45"]
        sh, sm, _ = (hora_ini.split(':') + ['00'])[:3]
        start_hour_var = ctk.StringVar(value=sh)
        start_min_var = ctk.StringVar(value=sm)
        ctk.CTkOptionMenu(row_h, values=hours, variable=start_hour_var, width=90).pack(side="left")
        ctk.CTkOptionMenu(row_h, values=minutes, variable=start_min_var, width=90).pack(side="left", padx=(6,0))

        # Veterinario
        ctk.CTkLabel(container, text="Veterinario:").pack(pady=(8,2), anchor="w")
        vet_var = ctk.StringVar()
        vet_values = []
        try:
            vet_values = [f"{k} - {v}" for k, v in getattr(self, '_vet_map', {}).items()]
        except Exception:
            pass
        if not vet_values:
            vet_values = ["No hay veterinarios"]
        opt_v = ctk.CTkOptionMenu(container, values=vet_values, variable=vet_var, width=300)
        opt_v.pack(pady=4)

        try:
            vet_name = None
            try:
                vet_name = row['veterinario']
            except Exception:
                vet_name = None
            if vet_name:
                for v in vet_values:
                    try:
                        if v.split('-',1)[1].strip() == str(vet_name).strip():
                            vet_var.set(v)
                            break
                    except Exception:
                        continue
            if not vet_var.get() and vet_values:
                vet_var.set(vet_values[0])
        except Exception:
            try:
                if vet_values:
                    vet_var.set(vet_values[0])
            except Exception:
                pass

        ctk.CTkLabel(container, text="Motivo:").pack(pady=(8,2), anchor="w")
        entry_m = ctk.CTkEntry(container, width=300)
        entry_m.pack(pady=4)
        entry_m.insert(0, motivo)

        lbl_err = ctk.CTkLabel(container, text="", text_color="red")
        lbl_err.pack(pady=6)

        btn_frame = ctk.CTkFrame(container, fg_color=frame_bg)
        btn_frame.pack(fill="x", pady=(8,4))
        spacer = ctk.CTkLabel(btn_frame, text="")
        spacer.pack(side="left", expand=True)

        def guardar():
            try:
                date_val = dp.get().strip()
            except Exception:
                date_val = ''
            shv = start_hour_var.get()
            smv = start_min_var.get()
            fecha_ini = f"{date_val} {shv}:{smv}:00"
            try:
                from datetime import datetime, timedelta
                d1 = datetime.strptime(fecha_ini, '%Y-%m-%d %H:%M:%S')
                dur_min = 0
                try:
                    svc_id = _val(row, 'id_servicio', None)
                    if svc_id is not None and hasattr(self, '_serv_map'):
                        svc_entry = self._serv_map.get(svc_id)
                        if svc_entry and svc_entry.get('duracion'):
                            dur_min = int(svc_entry.get('duracion') or 0)
                except Exception:
                    pass
                d2 = d1 + timedelta(minutes=dur_min)
                fecha_ini = d1.strftime('%Y-%m-%d %H:%M:%S')
                fecha_fin = d2.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                lbl_err.configure(text='Formato de fecha/hora inválido.')
                return

            sel = vet_var.get()
            if not sel or '-' not in sel:
                lbl_err.configure(text='Seleccione un veterinario.')
                return
            try:
                id_vet = int(sel.split('-')[0].strip())
            except Exception:
                lbl_err.configure(text='Veterinario inválido.')
                return

            mot = entry_m.get().strip()
            ok = CitaModel.modificar(id_cita, id_vet, fecha_ini, fecha_fin, mot)
            try:
                success, message = ok
            except Exception:
                success = bool(ok)
                message = "Cita modificada correctamente." if success else "Error modificando cita."

            if success:
                try:
                    win.grab_release()
                except Exception:
                    pass
                win.destroy()
                self.cargar_agenda()
            else:
                lbl_err.configure(text=message or 'Error al modificar la cita.')

        ctk.CTkButton(btn_frame, text='Guardar cambios', command=guardar).pack(side="right", padx=6)

        def _close_win():
            try:
                win.grab_release()
            except Exception:
                pass
            try:
                win.destroy()
            except Exception:
                pass

        ctk.CTkButton(btn_frame, text='Cancelar', command=_close_win).pack(side="right")

    def agendar_cita(self):
        masc_sel = getattr(self, 'masc_var', None) and self.masc_var.get()
        if not masc_sel or "-" not in masc_sel:
            self.lbl_status.configure(text="Seleccione una mascota válida.", text_color="red")
            return
        try:
            id_mascota = int(masc_sel.split("-")[0].strip())
        except Exception:
            self.lbl_status.configure(text="ID Mascota inválido.", text_color="red")
            return

        vet_sel = self.vet_var.get()
        if not vet_sel or "-" not in vet_sel:
            self.lbl_status.configure(text="Seleccione un veterinario.", text_color="red")
            return
        id_vet = int(vet_sel.split("-")[0].strip())

        serv_sel = getattr(self, 'serv_var', None) and self.serv_var.get()
        id_servicio = None
        if not serv_sel or '-' not in serv_sel:
            if serv_sel and serv_sel.startswith("No hay"):
                self.lbl_status.configure(text="No hay servicios. Cree servicios desde el módulo de administración.", text_color="orange")
                return
            else:
                self.lbl_status.configure(text="Seleccione un servicio válido. Cree servicios desde administración si no hay.", text_color="red")
                return
        else:
            try:
                id_servicio = int(serv_sel.split('-')[0].strip())
            except Exception:
                id_servicio = None
        try:
            date_val = self.date_picker.get()
        except Exception:
            date_val = getattr(self, 'entry_fecha_ini', None)
            if date_val is not None:
                try:
                    date_val = date_val.get().strip().split(' ')[0]
                except Exception:
                    date_val = ''
            else:
                date_val = ''
        sh = getattr(self, 'start_hour_var', None) and self.start_hour_var.get() or '09'
        sm = getattr(self, 'start_min_var', None) and self.start_min_var.get() or '00'
        fecha_ini = f"{date_val} {sh}:{sm}:00"

        try:
            from datetime import datetime, timedelta
            d1 = datetime.strptime(fecha_ini, '%Y-%m-%d %H:%M:%S')

            dur_min = 0
            try:
                if id_servicio is not None and hasattr(self, '_serv_map'):
                    entry = self._serv_map.get(id_servicio)
                    if entry and entry.get('duracion'):
                        dur_min = int(entry.get('duracion') or 0)
            except Exception:
                pass
            d2 = d1 + timedelta(minutes=dur_min)
            fecha_ini = d1.strftime('%Y-%m-%d %H:%M:%S')
            fecha_fin = d2.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            self.lbl_status.configure(text="Fecha/hora inválida.", text_color="red")
            return
        motivo = self.entry_motivo.get().strip()

        exito = CitaModel.agendar(id_mascota, id_vet, id_servicio, fecha_ini, fecha_fin, motivo)
        try:
            success, message = exito
        except Exception:
            success = bool(exito)
            message = "Cita agendada correctamente." if success else "Error al agendar cita."

        if success:
            self.lbl_status.configure(text=message or "Cita agendada correctamente.", text_color="green")
            try:
                self.masc_var.set("")
            except Exception:
                pass
            try:
                if getattr(self, 'serv_var', None):
                    self.serv_var.set("")
            except Exception:
                pass
            try:
                if hasattr(self, 'date_picker'):
                    import datetime
                    today = datetime.date.today().strftime('%Y-%m-%d')
                    try:
                        self.date_picker.delete(0, 'end')
                        self.date_picker.insert(0, today)
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                self.start_hour_var.set('09')
                self.start_min_var.set('00')
            except Exception:
                pass
            try:
                self.entry_motivo.delete(0, 'end')
            except Exception:
                pass
        else:
            # Mostrar el mensaje del modelo si existe
            msg = message or "Error al agendar cita."
            self.lbl_status.configure(text=msg, text_color="red")
