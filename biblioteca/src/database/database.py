"""
Módulo para la gestión de la base de datos SQLite
"""
import sqlite3
import os

class Database:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._initialize_connection()
        return cls._instance

    @classmethod
    def _initialize_connection(cls):
        """Inicializa la conexión a la base de datos"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), 'biblioteca.db')
            cls._connection = sqlite3.connect(db_path)
            cls._connection.row_factory = sqlite3.Row
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise

    def get_connection(self):
        """Obtiene la conexión a la base de datos"""
        if self._connection is None:
            self._initialize_connection()
        return self._connection

    def execute_query(self, query, params=None):
        """Ejecuta una consulta y retorna los resultados"""
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            self._connection.commit()
            return cursor.rowcount
        except Exception as e:
            self._connection.rollback()
            print(f"Error al ejecutar la consulta: {e}")
            raise
        finally:
            cursor.close()

    def create_tables(self):
        """Crea las tablas necesarias en la base de datos"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                genero TEXT,
                isbn TEXT UNIQUE,
                disponible INTEGER DEFAULT 1
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefono TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS prestamos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                libro_id INTEGER,
                usuario_id INTEGER,
                fecha_prestamo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_devolucion TIMESTAMP,
                devuelto INTEGER DEFAULT 0,
                FOREIGN KEY (libro_id) REFERENCES libros (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        ]
        
        for query in queries:
            try:
                self.execute_query(query)
            except Exception as e:
                print(f"Error al crear las tablas: {e}")
                raise

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None 