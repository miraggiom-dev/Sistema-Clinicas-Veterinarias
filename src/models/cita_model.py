from database.connection import get_db_connection


class CitaModel:
    @staticmethod
    def obtener_por_mascota(id_mascota):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM citas WHERE id_mascota = ? ORDER BY fecha_hora DESC",
            (id_mascota,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def obtener_ultima_por_mascota(id_mascota):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM citas WHERE id_mascota = ? ORDER BY fecha_hora DESC LIMIT 1",
            (id_mascota,),
        )
        row = cursor.fetchone()
        conn.close()
        return row

    def __init__(self, id_cita=None, id_mascota=None, id_veterinario=None, id_servicio=None, fecha_hora=None, fecha_fin=None, estado=None, motivo=None):
        self.id_cita = id_cita
        self.id_mascota = id_mascota
        self.id_veterinario = id_veterinario
        self.id_servicio = id_servicio
        self.fecha_hora = fecha_hora
        self.fecha_fin = fecha_fin
        self.estado = estado
        self.motivo = motivo

    @staticmethod
    def verificar_disponibilidad(id_veterinario, fecha_inicio, fecha_fin, id_cita_actual=None):
        """
        Verifica si EL VETERINARIO ya está ocupado en ese rango de horas.
        Lógica de solapamiento: (StartA < EndB) AND (EndA > StartB)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 1 FROM citas 
            WHERE id_veterinario = ? 
            AND estado != 'Cancelada'
            AND (fecha_hora < ? AND fecha_fin > ?)
        """
        params = [id_veterinario, fecha_fin, fecha_inicio]

        # Si es modificación, excluir la propia cita para que no choque consigo misma
        if id_cita_actual:
            query += " AND id_cita != ?"
            params.append(id_cita_actual)

        cursor.execute(query, tuple(params))
        result = cursor.fetchone()
        conn.close()
        
        # Retorna True si ESTÁ DISPONIBLE (result es None), False si está ocupado
        return result is None

    @staticmethod
    def agendar(id_mascota, id_veterinario, id_servicio, fecha_hora, fecha_fin, motivo):
        # 1. Verificar disponibilidad del veterinario
        if not CitaModel.verificar_disponibilidad(id_veterinario, fecha_hora, fecha_fin):
            msg = f"El veterinario ya tiene una cita en el horario {fecha_hora} - {fecha_fin}."
            return False, msg

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO citas (id_mascota, id_veterinario, id_servicio, fecha_hora, fecha_fin, motivo, estado)
                VALUES (?, ?, ?, ?, ?, ?, 'Pendiente')
            """, (id_mascota, id_veterinario, id_servicio, fecha_hora, fecha_fin, motivo))
            conn.commit()
            return True, "Cita agendada correctamente."
        except Exception as e:
            msg = f"Error agendando cita: {e}"
            return False, msg
        finally:
            conn.close()

    @staticmethod
    def modificar(id_cita, id_veterinario, fecha_hora, fecha_fin, motivo):
        """
        Permite cambiar horario o veterinario, verificando que el nuevo hueco esté libre.
        """
        if not CitaModel.verificar_disponibilidad(id_veterinario, fecha_hora, fecha_fin, id_cita_actual=id_cita):
            msg = f"El veterinario ya tiene una cita en el horario {fecha_hora} - {fecha_fin}."
            return False, msg

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE citas 
                SET id_veterinario = ?, fecha_hora = ?, fecha_fin = ?, motivo = ?
                WHERE id_cita = ?
            """, (id_veterinario, fecha_hora, fecha_fin, motivo, id_cita))
            conn.commit()
            return True, "Cita modificada correctamente."
        except Exception as e:
            msg = f"Error modificando cita: {e}"
            return False, msg
        finally:
            conn.close()

    @staticmethod
    def cancelar(id_cita):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE citas SET estado = 'Cancelada' WHERE id_cita = ?", (id_cita,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error cancelando cita: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def obtener_agenda_del_dia(fecha_filtro):
        """
        Muestra la agenda completa del día con Nombres reales (JOINs).
        fecha_filtro debe ser string formato 'YYYY-MM-DD'
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Este Query une 4 tablas para que el recepcionista vea todo claro
        # Asumo que la tabla de veterinarios es 'usuarios' como pusiste en el FK
        query = """
            SELECT 
                c.id_cita,
                time(c.fecha_hora) as hora_inicio,
                time(c.fecha_fin) as hora_fin,
                m.nombre AS mascota,
                u.nombre_completo AS veterinario,
                s.nombre AS servicio,
                c.estado,
                c.motivo
            FROM citas c
            JOIN mascotas m ON c.id_mascota = m.id_mascota
            JOIN usuarios u ON c.id_veterinario = u.id_usuario
            JOIN servicios s ON c.id_servicio = s.id_servicio
            WHERE date(c.fecha_hora) = ? 
            AND c.estado != 'Cancelada'
            ORDER BY c.fecha_hora ASC
        """
        cursor.execute(query, (fecha_filtro,))
        rows = cursor.fetchall()
        conn.close()
        return rows
