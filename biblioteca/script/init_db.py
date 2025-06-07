"""
Script para inicializar la base de datos SQLite
"""
import sys
import os

# Añadir el directorio src al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database import Database

def init_database():
    try:
        # Crear instancia de la base de datos
        db = Database()
        
        # Crear las tablas
        db.create_tables()
        
        print("Base de datos inicializada correctamente!")
        print("Ubicación de la base de datos: biblioteca/src/database/biblioteca.db")
        
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    init_database() 