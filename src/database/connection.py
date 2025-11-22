import sqlite3
from sqlite3 import Row 

def get_db_connection():
    conn = sqlite3.connect('veterinaria.db')
    conn.row_factory = Row 
    return conn
