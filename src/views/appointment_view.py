import customtkinter as ctk
from controllers.appointment_controller import AppointmentController
from controllers.admission_controller import AdmissionController

class AppointmentView(ctk.CTkFrame):
    
    def __init__(self, master, auth_controller, id_mascota=None, active_tab=None, switch_callback=None):
        super().__init__(master)
        
        self.switch_callback = switch_callback
        self.controller = AppointmentController()
        self.admission_controller = AdmissionController()
        self._vet_map = {}
        self._serv_map = {} 
        self.prefill_mascota = id_mascota
        
        try:
            self.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        except: pass

        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tabview = ctk.CTkTabview(self, width=800)
        self.tabview.pack(fill="both", expand=True)
        self.tabview.add("Agenda")
        self.tabview.add("Agendar")

        self._init_tab_agenda()
        self._init_tab_agendar()

        self._cargar_veterinarios()
        self._cargar_servicios()
        self._cargar_propietarios()

        if active_tab in ["Agenda", "Agendar"]:
            self.tabview.set(active_tab)

    def _init_tab_agenda(self):
        tab = self.tabview.tab("Agenda")
        
        top_frame = ctk.CTkFrame(tab)
        top_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(top_frame, text="Fecha (YYYY-MM-DD):").pack(side="left", padx=5)
        self.entry_fecha_agenda = ctk.CTkEntry(top_frame, width=150)
        self.entry_fecha_agenda.pack(side="left", padx=5)
        
        from datetime import date
        self.entry_fecha_agenda.insert(0, date.today().strftime("%Y-%m-%d"))

        ctk.CTkButton(top_frame, text="Cargar Agenda", command=self.cargar_agenda).pack(side="left", padx=10)

        self.scroll_agenda = ctk.CTkScrollableFrame(tab, label_text="Agenda del Día")
        self.scroll_agenda.pack(fill="both", expand=True, padx=10, pady=10)

    def cargar_agenda(self):
        for w in self.scroll_agenda.winfo_children(): w.destroy()

        fecha = self.entry_fecha_agenda.get().strip()
        rows = self.controller.buscar_citas_dia(fecha)

        if not rows:
            ctk.CTkLabel(self.scroll_agenda, text="No hay citas para esta fecha.", text_color="gray").pack(pady=10)
            return

        for r in rows:
            self._render_cita_row(r)

    def _render_cita_row(self, r):
        frame = ctk.CTkFrame(self.scroll_agenda)
        frame.pack(fill="x", pady=5, padx=5)
        
        def get_val(item, keys, default='?'):
            if isinstance(item, tuple) and not hasattr(item, 'keys'):
                return default
            for k in keys:
                try: return item[k]
                except: 
                    try: return getattr(item, k)
                    except: pass
            return default

        h_ini_raw = get_val(r, ['hora_inicio'], '00:00:00')
        h_fin_raw = get_val(r, ['hora_fin'], '00:00:00')
        
        try: h_ini = str(h_ini_raw).split(' ')[1][:5]
        except: h_ini = str(h_ini_raw)
        
        try: h_fin = str(h_fin_raw).split(' ')[1][:5]
        except: h_fin = str(h_fin_raw)

        masc = get_val(r, ['mascota', 'nombre_mascota'], 'N/A')
        prop = get_val(r, ['propietario', 'nombre_propietario', 'cliente'], 'N/A')
        vet = get_val(r, ['veterinario', 'nombre_veterinario'], 'N/A')
        serv = get_val(r, ['servicio', 'nombre_servicio'], 'Consulta')
        
        idc = get_val(r, ['id_cita'], None)
        est = get_val(r, ['estado'], 'Pendiente')

        texto = f"{h_ini}-{h_fin} | {prop} - {masc} | {vet} | {serv}"
        
        ctk.CTkLabel(frame, text=texto, anchor="w", font=("Arial", 12)).pack(side="left", padx=10, fill="x", expand=True)

        estados = ['Pendiente', 'Realizada', 'Cancelada', 'Reagendada']
        var_est = ctk.StringVar(value=str(est))
        
        def callback_cambio_estado(nuevo_valor):
            if idc:
                self.controller.cambiar_estado_cita(idc, nuevo_valor)
        
        opt = ctk.CTkOptionMenu(frame, values=estados, variable=var_est, command=callback_cambio_estado, width=110)
        opt.pack(side="right", padx=5)

        def callback_abrir_edicion():
            self._abrir_modal_editar(r)

        ctk.CTkButton(frame, text="Editar", width=70, command=callback_abrir_edicion).pack(side="right", padx=5)

    def _init_tab_agendar(self):
        tab = self.tabview.tab("Agendar")
        
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.columnconfigure(2, weight=0)
        
        ANCHO_INPUT = 300
        
        ctk.CTkLabel(container, text="Propietario:").grid(row=0, column=0, sticky="w", pady=10, padx=(0, 10))
        self.var_prop = ctk.StringVar(value="")
        self.opt_prop = ctk.CTkOptionMenu(container, variable=self.var_prop, values=[], width=ANCHO_INPUT)
        self.opt_prop.grid(row=0, column=1, sticky="ew", pady=10) 
        ctk.CTkButton(container, text="+", width=40, command=self._crear_modal_propietario).grid(row=0, column=2, padx=(10,0), sticky="e")
        
        self.var_prop.trace_add("write", self._on_prop_changed)

        ctk.CTkLabel(container, text="Mascota:").grid(row=1, column=0, sticky="w", pady=10, padx=(0, 10))
        self.var_masc = ctk.StringVar(value="")
        self.opt_masc = ctk.CTkOptionMenu(container, variable=self.var_masc, values=["Seleccione Propietario"], width=ANCHO_INPUT)
        self.opt_masc.grid(row=1, column=1, sticky="ew", pady=10)
        ctk.CTkButton(container, text="+", width=40, command=self._crear_modal_mascota).grid(row=1, column=2, padx=(10,0), sticky="e")

        ctk.CTkLabel(container, text="Veterinario:").grid(row=2, column=0, sticky="w", pady=10, padx=(0, 10))
        self.var_vet = ctk.StringVar(value="")
        self.opt_vet = ctk.CTkOptionMenu(container, variable=self.var_vet, values=[], width=ANCHO_INPUT)
        self.opt_vet.grid(row=2, column=1, sticky="ew", pady=10)

        ctk.CTkLabel(container, text="Servicio:").grid(row=3, column=0, sticky="w", pady=10, padx=(0, 10))
        self.var_serv = ctk.StringVar(value="")
        self.opt_serv = ctk.CTkOptionMenu(container, variable=self.var_serv, values=[], width=ANCHO_INPUT)
        self.opt_serv.grid(row=3, column=1, sticky="ew", pady=10)

        ctk.CTkLabel(container, text="Fecha (YYYY-MM-DD):").grid(row=4, column=0, sticky="w", pady=10, padx=(0, 10))
        
        f_datetime = ctk.CTkFrame(container, fg_color="transparent")
        f_datetime.grid(row=4, column=1, sticky="w", pady=10)
        
        self.entry_date = ctk.CTkEntry(f_datetime, width=140)
        self.entry_date.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(f_datetime, text="Hora:").pack(side="left", padx=(5,5))
        self.var_h = ctk.StringVar(value="09")
        self.var_m = ctk.StringVar(value="00")
        ctk.CTkOptionMenu(f_datetime, values=[f"{x:02d}" for x in range(24)], variable=self.var_h, width=65).pack(side="left")
        ctk.CTkLabel(f_datetime, text=":").pack(side="left")
        ctk.CTkOptionMenu(f_datetime, values=["00","15","30","45"], variable=self.var_m, width=65).pack(side="left")

        ctk.CTkLabel(container, text="Motivo:").grid(row=5, column=0, sticky="w", pady=10, padx=(0, 10))
        self.entry_motivo = ctk.CTkEntry(container, width=ANCHO_INPUT)
        self.entry_motivo.grid(row=5, column=1, sticky="ew", pady=10)

        self.lbl_status = ctk.CTkLabel(container, text="", font=("Arial", 12, "bold"))
        self.lbl_status.grid(row=6, column=0, columnspan=3, pady=10)
        
        ctk.CTkButton(container, text="AGENDAR CITA", command=self.agendar_cita, height=40).grid(row=7, column=1, sticky="ew", pady=10)

    def _cargar_veterinarios(self):
        vets = self.controller.obtener_veterinarios()
        vals = []
        for vid, vname in vets:
            self._vet_map[vid] = vname
            vals.append(f"{vid} - {vname}")
        self.opt_vet.configure(values=vals)
        self.var_vet.set("")

    def _cargar_servicios(self):
        servs = self.controller.obtener_servicios()
        vals = []
        for s in servs:
            try:
                sid = s['id_servicio']
                nom = s['nombre']
            except:
                sid = s.get('id_servicio') if isinstance(s, dict) else s[0]
                nom = s.get('nombre') if isinstance(s, dict) else s[1]
                
            self._serv_map[sid] = s
            vals.append(f"{sid} - {nom}")
        self.opt_serv.configure(values=vals)
        self.var_serv.set("")

    def _cargar_propietarios(self):
        raw = self.admission_controller.buscar_clientes("")
        vals = []
        if raw:
            for c in raw:
                try:
                    cid = c['id_propietario']
                    cnom = c['nombre']
                except (TypeError, IndexError, KeyError):
                    try:
                        cid = c.id_propietario
                        cnom = c.nombre
                    except AttributeError:
                        continue 
                
                vals.append(f"{cid} - {cnom}")
                
        self.opt_prop.configure(values=vals)
        self.var_prop.set("")
        
        if hasattr(self, 'prefill_mascota') and self.prefill_mascota:
            pass

    def _on_prop_changed(self, *args):
        val = self.var_prop.get()
        if not val or "No hay" in val: return
        try:
            pid = int(val.split('-')[0].strip())
            mascotas = self.admission_controller.obtener_mascotas_cliente(pid)
            
            vals = []
            for m in mascotas:
                try:
                    mid = m['id_mascota']
                    mnom = m['nombre']
                except:
                    mid = m.id_mascota
                    mnom = m.nombre
                vals.append(f"{mid} - {mnom}")

            self.opt_masc.configure(values=vals)
            self.var_masc.set("")
        except: pass

    def agendar_cita(self):
        val_masc = self.var_masc.get()
        val_vet = self.var_vet.get()
        val_serv = self.var_serv.get()

        if not val_masc or not val_vet or not val_serv:
             self.lbl_status.configure(text="Error: Complete todos los campos.", text_color="red")
             return

        try:
            id_mascota = int(val_masc.split('-')[0].strip())
            id_vet = int(val_vet.split('-')[0].strip())
            id_serv = int(val_serv.split('-')[0].strip())
        except:
            self.lbl_status.configure(text="Error: Datos inválidos seleccionados.", text_color="red")
            return

        try:
            s_info = self._serv_map.get(id_serv, {})
            dur = s_info['duracion_estimada']
        except:
            dur = 30

        exito, mensaje = self.controller.agendar_cita(
            id_mascota, id_vet, id_serv, 
            self.entry_date.get(), self.var_h.get(), self.var_m.get(),
            dur, self.entry_motivo.get()
        )

        color = "green" if exito else "red"
        self.lbl_status.configure(text=mensaje, text_color=color)

        if exito:
            self.entry_motivo.delete(0, 'end')
            self.var_masc.set("")
            self.var_vet.set("")
            self.var_serv.set("")
            self.var_prop.set("")
            
            if self.entry_date.get() == self.entry_fecha_agenda.get():
                self.cargar_agenda()

    def _crear_modal_propietario(self):
        win = ctk.CTkToplevel(self)
        win.title("Nuevo Cliente")
        win.geometry("400x420")
        
        def crear_input(texto):
            ctk.CTkLabel(win, text=texto).pack(pady=(5,2))
            e = ctk.CTkEntry(win, width=300)
            e.pack(pady=2)
            return e
            
        e_ced = crear_input("Cédula:")
        e_nom = crear_input("Nombre Completo:")
        e_tel = crear_input("Teléfono:")
        e_eml = crear_input("Email:")
        e_dir = crear_input("Dirección:")
        
        lbl_err = ctk.CTkLabel(win, text="", text_color="red")
        lbl_err.pack(pady=5)

        def funcion_guardar():
            nid = self.admission_controller.registrar_nuevo_cliente(
                e_ced.get(), e_nom.get(), e_tel.get(), e_eml.get(), e_dir.get()
            )
            if nid:
                self._cargar_propietarios()
                try: self.var_prop.set(f"{nid} - {e_nom.get()}")
                except: pass
                win.destroy()
            else:
                lbl_err.configure(text="Error al registrar cliente.")

        ctk.CTkButton(win, text="Guardar Cliente", command=funcion_guardar).pack(pady=20)

    def _crear_modal_mascota(self):
        val_p = self.var_prop.get()
        if not val_p or "No hay" in val_p:
            self.lbl_status.configure(text="Seleccione un propietario primero.", text_color="red")
            return
        try: pid = int(val_p.split('-')[0].strip())
        except: return

        win = ctk.CTkToplevel(self)
        win.title("Nueva Mascota")
        win.geometry("400x450")

        def crear_input(texto):
            ctk.CTkLabel(win, text=texto).pack(pady=(5,2))
            e = ctk.CTkEntry(win, width=300)
            e.pack(pady=2)
            return e

        e_nom = crear_input("Nombre:")
        e_esp = crear_input("Especie (Perro, Gato...):")
        e_raz = crear_input("Raza:")
        e_nac = crear_input("Fecha Nacimiento (YYYY-MM-DD):")
        
        ctk.CTkLabel(win, text="Género:").pack(pady=(5,2))
        v_gen = ctk.StringVar(value="Macho")
        ctk.CTkOptionMenu(win, variable=v_gen, values=["Macho", "Hembra"], width=300).pack(pady=2)

        lbl_err = ctk.CTkLabel(win, text="", text_color="red")
        lbl_err.pack(pady=5)

        def funcion_guardar_mascota():
            ok = self.admission_controller.registrar_mascota(
                pid, e_nom.get(), e_esp.get(), e_raz.get(), e_nac.get(), v_gen.get()
            )
            if ok:
                self._on_prop_changed()
                win.destroy()
            else:
                lbl_err.configure(text="Error al crear mascota.")

        ctk.CTkButton(win, text="Guardar Mascota", command=funcion_guardar_mascota).pack(pady=20)

    def _abrir_modal_editar(self, row):
        win = ctk.CTkToplevel(self)
        win.title(f"Editar Cita")
        win.geometry("400x600")
        
        def get_val(item, keys, default='?'):
            for k in keys:
                try: return item[k]
                except: 
                    try: return getattr(item, k)
                    except: pass
            return default

        h_ini = str(get_val(row, ['hora_inicio'], '2025-01-01 09:00:00'))
        id_c = get_val(row, ['id_cita'], 0)
        vet_nom = str(get_val(row, ['veterinario', 'nombre_veterinario'], ''))
        vid = get_val(row, ['id_veterinario'], None)
        
        serv_nom = str(get_val(row, ['servicio', 'nombre_servicio'], ''))
        sid = get_val(row, ['id_servicio'], None)
        
        mot = str(get_val(row, ['motivo'], ''))
        masc = str(get_val(row, ['mascota', 'nombre_mascota'], 'N/A'))
        prop = str(get_val(row, ['propietario', 'nombre_propietario'], 'N/A'))

        ctk.CTkLabel(win, text="Información:", font=("Arial", 12, "bold")).pack(pady=(15, 2))
        ctk.CTkLabel(win, text=f"Paciente: {masc}  |  Dueño: {prop}").pack(pady=2)

        ctk.CTkLabel(win, text="Fecha (YYYY-MM-DD):").pack(pady=(10, 2))
        e_date = ctk.CTkEntry(win, width=200)
        e_date.pack(pady=2)
        try: fecha_orig = h_ini.split(' ')[0]
        except: fecha_orig = h_ini
        e_date.insert(0, fecha_orig)
        
        ctk.CTkLabel(win, text="Hora Inicio:").pack(pady=(10, 2))
        f_h = ctk.CTkFrame(win, fg_color="transparent")
        f_h.pack(pady=2)
        
        try: orig_h, orig_m, _ = h_ini.split(' ')[1].split(':')
        except: orig_h, orig_m = "09", "00"

        v_h = ctk.StringVar(value=orig_h)
        v_m = ctk.StringVar(value=orig_m)
        ctk.CTkOptionMenu(f_h, values=[f"{x:02d}" for x in range(24)], variable=v_h, width=70).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(f_h, text=":").pack(side="left")
        ctk.CTkOptionMenu(f_h, values=["00","15","30","45"], variable=v_m, width=70).pack(side="left", padx=(5, 0))
        
        ctk.CTkLabel(win, text="Veterinario:").pack(pady=(10, 2))
        vets_values = self.opt_vet.cget("values")
        vet_var = ctk.StringVar()
        current_vet_str = "Seleccione"
        if vets_values:
            for v in vets_values:
                if vet_nom and vet_nom in v:
                    current_vet_str = v
                    break
            if current_vet_str == "Seleccione" and vets_values:
                current_vet_str = vets_values[0]

        opt_vet_edit = ctk.CTkOptionMenu(win, values=vets_values, variable=vet_var, width=200)
        opt_vet_edit.pack(pady=2)
        vet_var.set(current_vet_str)

        ctk.CTkLabel(win, text="Servicio:").pack(pady=(10, 2))
        servs_values = self.opt_serv.cget("values")
        serv_var = ctk.StringVar()
        current_serv_str = "Seleccione"
        if servs_values:
            for s in servs_values:
                if serv_nom and serv_nom in s:
                    current_serv_str = s
                    break
            if current_serv_str == "Seleccione" and servs_values:
                current_serv_str = servs_values[0]
        
        opt_serv_edit = ctk.CTkOptionMenu(win, values=servs_values, variable=serv_var, width=200)
        opt_serv_edit.pack(pady=2)
        serv_var.set(current_serv_str)

        ctk.CTkLabel(win, text="Motivo:").pack(pady=(10, 2))
        e_motivo = ctk.CTkEntry(win, width=200)
        e_motivo.pack(pady=2)
        e_motivo.insert(0, mot)

        lbl_err = ctk.CTkLabel(win, text="", text_color="red")
        lbl_err.pack(pady=10)

        def funcion_guardar_cambios():
            sel_vet = vet_var.get()
            try: v_id_final = int(sel_vet.split('-')[0].strip())
            except: v_id_final = vid or 1
            
            sel_serv = serv_var.get()
            try: s_id_final = int(sel_serv.split('-')[0].strip())
            except: s_id_final = sid or 1

            nueva_duracion = 30
            try:
                s_info = self._serv_map.get(s_id_final, {})
                nueva_duracion = s_info.get('duracion_estimada', 30)
            except: pass

            ok, msg = self.controller.editar_cita_logica(
                id_c, v_id_final, s_id_final,
                e_date.get(), v_h.get(), v_m.get(), 
                nueva_duracion, e_motivo.get()
            )
            
            if ok:
                self.cargar_agenda()
                win.destroy()
            else:
                lbl_err.configure(text=msg)

        ctk.CTkButton(win, text="Guardar Cambios", command=funcion_guardar_cambios).pack(pady=20)