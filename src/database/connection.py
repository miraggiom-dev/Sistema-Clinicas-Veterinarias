# database/connection.py

import sqlite3
# Es crucial importar Row
from sqlite3 import Row 

def get_db_connection():
    conn = sqlite3.connect('veterinaria.db')
    # ESTO ES LO QUE HACE QUE SE VEAN LOS DATOS POR NOMBRE DE COLUMNA
    conn.row_factory = Row 
    return conn