import sqlite3
import os
from pathlib import Path
import dotenv

dotenv.load_dotenv()

DATABASE_PATH_ENV = os.getenv("DATABASE_PATH")
DATABASE_URL_ENV = os.getenv("DATABASE_URL")

def _resolve_db_path():
    if DATABASE_PATH_ENV:
        path = DATABASE_PATH_ENV
    elif DATABASE_URL_ENV:
        if DATABASE_URL_ENV.startswith("sqlite:///"):
            path = DATABASE_URL_ENV.replace("sqlite:///", "", 1)
        elif DATABASE_URL_ENV.startswith("sqlite:////"):
            path = DATABASE_URL_ENV.replace("sqlite:////", "/", 1)
        else:
            path = DATABASE_URL_ENV
    else:
        path = os.path.join(os.getcwd(), "veterinaria.db")
    
    return str(Path(path).expanduser().resolve())

DB_NAME = _resolve_db_path()

def migrate_database():
    """Migra la base de datos existente agregando columnas faltantes."""
    print(f"Migrando base de datos: {DB_NAME}")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    migrations = []
    
    # Migración 1: Agregar columna 'firma' a diagnosticos
    try:
        cursor.execute("ALTER TABLE diagnosticos ADD COLUMN firma TEXT")
        migrations.append("[OK] Agregada columna 'firma' a tabla 'diagnosticos'")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            migrations.append("[SKIP] Columna 'firma' ya existe en 'diagnosticos'")
        else:
            migrations.append(f"[ERROR] Error agregando 'firma': {e}")
    
    # Migración 2: Agregar columna 'tipo' a servicios
    try:
        cursor.execute("ALTER TABLE servicios ADD COLUMN tipo TEXT NOT NULL DEFAULT 'Consulta'")
        migrations.append("[OK] Agregada columna 'tipo' a tabla 'servicios'")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            migrations.append("[SKIP] Columna 'tipo' ya existe en 'servicios'")
        else:
            migrations.append(f"[ERROR] Error agregando 'tipo': {e}")
    
    conn.commit()
    conn.close()
    
    print("\nResultados de la migración:")
    for msg in migrations:
        print(f"  {msg}")
    print("\n¡Migración completada!")

if __name__ == "__main__":
    migrate_database()
