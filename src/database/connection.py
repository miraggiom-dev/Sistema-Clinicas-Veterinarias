from database.schema_setup import DB_NAME
import sqlite3
from sqlite3 import Row 

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = Row 
    return conn
