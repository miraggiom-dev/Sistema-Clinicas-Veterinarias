import sqlite3

from database.schema_setup import create_tables
from database.connection import get_db_connection
from models.usuario_model import UsuarioModel
from models.diagnostico_model import DiagnosticoModel


def setup_datos_prueba():
    """Inserta datos necesarios pa q agarren las forein kis """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("--- Insertando datos semilla ---")
    

    cursor.execute("INSERT OR IGNORE INTO usuarios (id_usuario, nombre_completo, rol, email, password) VALUES (2, 'Dr. House', 'Veterinario', 'house@vet.com', '123')")
    
    
    cursor.execute("INSERT OR IGNORE INTO propietarios (id_propietario, nombre) VALUES (1, 'Juan Pérez')")
    
    
    cursor.execute("INSERT OR IGNORE INTO mascotas (id_mascota, id_propietario, nombre, especie) VALUES (1, 1, 'Firulais', 'Perro')")
    
    
    cursor.execute("INSERT OR IGNORE INTO servicios (id_servicio, nombre, precio_base, costo_mano_obra, duracion_estimada) VALUES (1, 'Consulta General', 30.0, 10.0, 30)")
    
    
    cursor.execute("""
        INSERT OR IGNORE INTO citas (id_cita, id_mascota, id_veterinario, id_servicio, fecha_hora, estado, motivo) 
        VALUES (1, 1, 2, 1, '2025-10-20 10:00:00', 'Pendiente', 'Vacunación')
    """)
    
    conn.commit()
    conn.close()
    print("Datos semilla listos.\n")

def test_versionado_diagnostico():
    print("--- INICIANDO TEST DE VERSIONADO (Requisito Crítico) ---")
    
    id_cita_prueba = 1
    id_vet_prueba = 2
    
    # PASO 1: Crear el primer diagnóstico
    print("1. Guardando Diagnóstico Versión 1...")
    DiagnosticoModel.guardar_diagnostico(
        id_cita=id_cita_prueba,
        id_veterinario=id_vet_prueba,
        diagnostico_texto="Infección leve de oído.",
        tratamiento="Limpieza y gotas Otix.",
        observacion="Diagnóstico inicial"
    )
    
    # PASO 2: Simular que el veterinario edita el diagnóstico
    print("2. Editando Diagnóstico (Debería crear Versión 2)...")
    DiagnosticoModel.guardar_diagnostico(
        id_cita=id_cita_prueba,
        id_veterinario=id_vet_prueba,
        diagnostico_texto="Infección MODERADA de oído.", # Cambio aquí
        tratamiento="Limpieza, gotas Otix y Antibiótico oral.", # Cambio aquí
        observacion="Se reevalúa severidad, corrección Dr. House"
    )
    

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT version, diagnostico, es_actual FROM diagnosticos WHERE id_cita = ? ORDER BY version ASC", (id_cita_prueba,))
    resultados = cursor.fetchall()
    conn.close()
    
    print("\n--- RESULTADOS EN BASE DE DATOS ---")
    print(f"{'Versión':<10} | {'Estado (Actual)':<15} | {'Diagnóstico'}")
    print("-" * 60)
    
    for row in resultados:
        estado = "VIGENTE (1)" if row['es_actual'] == 1 else "HISTORIAL (0)"
        print(f"{row['version']:<10} | {estado:<15} | {row['diagnostico']}")

    if len(resultados) == 2:
        print("\n[ÉXITO] Se encontraron 2 registros (Historial preservado).")
    else:
        print(f"\n[FALLO] Se esperaban 2 registros, se encontraron {len(resultados)}.")

    if results_ok(resultados):
         print("[ÉXITO] La versión 2 es la vigente y la 1 es historial.")
    else:
         print("[FALLO] Los estados de 'es_actual' no son correctos.")

def results_ok(rows):

    return rows[0]['es_actual'] == 0 and rows[1]['es_actual'] == 1

if __name__ == "__main__":

    create_tables()

    setup_datos_prueba()

    print("--- Test Login ---")
    user = UsuarioModel.autenticar("admin@vet.com", "admin123")
    if user:
        print(f"[ÉXITO] Usuario autenticado: {user.nombre} ({user.rol})\n")
    else:
        print("[FALLO] Login incorrecto\n")

    test_versionado_diagnostico()