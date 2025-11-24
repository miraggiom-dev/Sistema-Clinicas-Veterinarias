from database.connection import get_db_connection

class ServicioModel:
    """Modelo para operaciones CRUD sobre la tabla `servicios`.

    Métodos:
    - crear(nombre, tipo, precio_base, costo_mano_obra, duracion_estimada)
    - obtener_todos(activos_only=True)
    - obtener_por_id(id_servicio)
    - actualizar(id_servicio, **kwargs)
    - eliminar(id_servicio)  # borrado lógico (activo = 0)
    - reactivar(id_servicio)
    """

    @staticmethod
    def crear(nombre, tipo, precio_base=0.0, costo_mano_obra=0.0, duracion_estimada=30):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO servicios (nombre, tipo, precio_base, costo_mano_obra, duracion_estimada, activo)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (nombre, tipo, precio_base, costo_mano_obra, duracion_estimada),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creando servicio: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def obtener_todos(activos_only=True):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if activos_only:
                cursor.execute("SELECT * FROM servicios WHERE activo = 1 ORDER BY nombre")
            else:
                cursor.execute("SELECT * FROM servicios ORDER BY nombre")
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error obteniendo servicios: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(id_servicio):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM servicios WHERE id_servicio = ?", (id_servicio,))
            row = cursor.fetchone()
            return row
        except Exception as e:
            print(f"Error obteniendo servicio por id: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def actualizar(id_servicio, nombre=None, tipo=None, precio_base=None, costo_mano_obra=None, duracion_estimada=None, activo=None):
        """Actualiza los campos proporcionados para el servicio indicado."""
        fields = []
        params = []
        if nombre is not None:
            fields.append("nombre = ?")
            params.append(nombre)
        if tipo is not None:
            fields.append("tipo = ?")
            params.append(tipo)
        if precio_base is not None:
            fields.append("precio_base = ?")
            params.append(precio_base)
        if costo_mano_obra is not None:
            fields.append("costo_mano_obra = ?")
            params.append(costo_mano_obra)
        if duracion_estimada is not None:
            fields.append("duracion_estimada = ?")
            params.append(duracion_estimada)
        if activo is not None:
            fields.append("activo = ?")
            params.append(1 if bool(activo) else 0)

        if not fields:
            return False

        params.append(id_servicio)
        sql = f"UPDATE servicios SET {', '.join(fields)} WHERE id_servicio = ?"

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, tuple(params))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando servicio: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def eliminar(id_servicio):
        """Borrado lógico: marca `activo = 0` para no perder historial."""
        return ServicioModel.actualizar(id_servicio, activo=0)

    @staticmethod
    def reactivar(id_servicio):
        """Re-activa un servicio previamente desactivado."""
        return ServicioModel.actualizar(id_servicio, activo=1)
