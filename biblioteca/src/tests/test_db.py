import unittest
import os
import sqlite3
import json
from datetime import datetime
import sys
import time # Agregado para el sleep
import logging # Agregado para el logging en _safe_remove_db
import gc # Agregado para forzar la recolección de basura

# Añadir el directorio src al path de Python de forma segura
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gestor_grafo_mejorado import GestorGrafoBiblioteca

# Configurar logging para el script de prueba
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestDatabase(unittest.TestCase):

    def _safe_remove_db(self, path):
        # Intenta eliminar el archivo de la base de datos de forma segura.
        # Esto es crucial para Windows, donde los bloqueos de archivos son comunes.
        for _ in range(10): # Reintentar hasta 10 veces
            if os.path.exists(path):
                try:
                    os.remove(path)
                    time.sleep(0.05) # Pequeño retraso entre intentos
                    logger.info(f"Base de datos '{path}' eliminada exitosamente.")
                    return True
                except OSError as e:
                    logger.warning(f"Intento de eliminar DB '{path}' falló: {e}. Reintentando...")
                    time.sleep(0.2) # Mayor retraso en caso de error
            else:
                return True # El archivo no existe, ya fue eliminado
        logger.error(f"Fallo persistente al eliminar la DB: {path}")
        return False

    def setUp(self):
        """Configuración inicial para las pruebas de base de datos."""
        self.db_path = "test_biblioteca.db"
        # Asegurar una base de datos limpia para cada test
        self._safe_remove_db(self.db_path) 
        self.gestor = GestorGrafoBiblioteca(self.db_path)
        
    def tearDown(self):
        """Limpieza después de las pruebas."""
        # Asegurar que el gestor y sus conexiones sean descartados antes de eliminar el archivo
        if hasattr(self, 'gestor') and self.gestor is not None:
            del self.gestor
            self.gestor = None
            gc.collect() # Forzar recolección de basura
            time.sleep(0.1) # Dar tiempo para la recolección de basura y liberación de archivos

        self._safe_remove_db(self.db_path) # Usar la función segura para limpiar

    def test_creacion_tabla(self):
        """Prueba la creación correcta de la tabla en la base de datos."""
        # setUp ya inicializa la DB
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='grafo_estado'
            """)
            resultado = cursor.fetchone()
            self.assertIsNotNone(resultado)
            self.assertEqual(resultado[0], 'grafo_estado')

    def test_estructura_tabla(self):
        """Prueba la estructura correcta de la tabla."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(grafo_estado)")
            columnas = cursor.fetchall()
            
            # Verificar columnas
            nombres_columnas = [col[1] for col in columnas]
            self.assertIn('id', nombres_columnas)
            self.assertIn('fecha_actualizacion', nombres_columnas)
            self.assertIn('datos_grafo', nombres_columnas)

    def test_guardar_estado(self):
        """Prueba el guardado de estado en la base de datos."""
        # Agregar datos de prueba
        self.gestor.agregar_libro("123", "Libro Test", "Autor Test")
        self.gestor.agregar_usuario("usuario@test.com", "Usuario Test")
        
        # Guardar estado
        resultado = self.gestor.guardar_estado()
        self.assertTrue(resultado)
        
        # Verificar que se guardó en la base de datos y que solo hay un registro
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM grafo_estado")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1) # Esperamos solo 1 registro si cada test inicia limpio

    def test_cargar_estado(self):
        """Prueba la carga de estado desde la base de datos."""
        # Crear y guardar datos de prueba
        self.gestor.agregar_libro("123", "Libro Test", "Autor Test")
        self.gestor.guardar_estado()
        
        # Crear nuevo gestor y cargar estado
        nuevo_gestor = GestorGrafoBiblioteca(self.db_path)
        resultado = nuevo_gestor.cargar_estado()
        self.assertTrue(resultado)
        
        # Verificar que los datos se cargaron correctamente
        node_id = nuevo_gestor._get_node_id("libro", "123")
        self.assertTrue(nuevo_gestor.grafo.has_node(node_id))
        
        # Limpiar el nuevo gestor
        del nuevo_gestor
        nuevo_gestor = None

    def test_integridad_datos(self):
        """Prueba la integridad de los datos guardados."""
        # Crear datos complejos
        self.gestor.agregar_libro("L1", "Libro 1", "Autor 1")
        self.gestor.agregar_usuario("U1", "Usuario 1")
        self.gestor.vincular_libro_con_usuario("L1", "U1", "PRESTAMO")
        
        # Guardar estado
        self.gestor.guardar_estado()
        
        # Verificar en la base de datos
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT datos_grafo FROM grafo_estado ORDER BY id DESC LIMIT 1")
            datos = json.loads(cursor.fetchone()[0])
            
            # Verificar nodos
            self.assertIn('nodes', datos)
            self.assertIn('edges', datos)
            
            # Verificar que los datos son correctos
            nodos = datos['nodes']
            self.assertTrue(any('libro_L1' in n for n in nodos))
            self.assertTrue(any('usuario_U1' in n for n in nodos))

    def test_concurrencia(self):
        """Prueba el manejo de concurrencia en la base de datos."""
        # Asegurar un inicio limpio para este test específico
        self._safe_remove_db(self.db_path) 

        # Crear dos gestores que acceden a la misma base de datos
        gestor1 = GestorGrafoBiblioteca(self.db_path)
        gestor2 = GestorGrafoBiblioteca(self.db_path)
        
        # Modificar datos desde ambos gestores
        gestor1.agregar_libro("L1", "Libro 1", "Autor 1")
        self.assertTrue(gestor1.guardar_estado()) # Guarda el estado de gestor1

        gestor2.agregar_libro("L2", "Libro 2", "Autor 2")
        self.assertTrue(gestor2.guardar_estado()) # Guarda el estado de gestor2
        
        # Verificar que ambos estados se guardaron (si guardar_estado inserta y no sobrescribe)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM grafo_estado")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 2) # Esperamos 2 registros si ambos guardados insertan
        
        # Limpiar gestores concurrentes
        del gestor1
        del gestor2
        gestor1 = None
        gestor2 = None

    def test_manejo_errores(self):
        """Prueba el manejo de errores en la base de datos."""
        temp_db_path = "no_existe_temp.db"
        self._safe_remove_db(temp_db_path) # Usar la función segura para limpiar

        # Intentar acceder a una base de datos no existente
        gestor_error = GestorGrafoBiblioteca(temp_db_path)
        
        # Verificar que retorna False y no lanza una excepción
        self.assertFalse(gestor_error.cargar_estado())

        # Limpiar la base de datos temporal si se creó
        del gestor_error
        gestor_error = None
        self._safe_remove_db(temp_db_path) # Usar la función segura para limpiar

if __name__ == '__main__':
    unittest.main() 