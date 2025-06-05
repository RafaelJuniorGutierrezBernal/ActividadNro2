import unittest
import os
import sqlite3
import json
from datetime import datetime
from ..gestor_grafo_mejorado import GestorGrafoBiblioteca

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para las pruebas de base de datos."""
        # Crear una base de datos de prueba
        self.db_path = "test_biblioteca.db"
        self.gestor = GestorGrafoBiblioteca(self.db_path)
        
    def tearDown(self):
        """Limpieza después de las pruebas."""
        # Cerrar conexiones
        self.gestor = None
        # Eliminar base de datos de prueba
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_creacion_tabla(self):
        """Prueba la creación correcta de la tabla en la base de datos."""
        # Verificar que la tabla existe
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
        
        # Verificar que se guardó en la base de datos
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM grafo_estado")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)

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
        # Crear dos gestores que acceden a la misma base de datos
        gestor1 = GestorGrafoBiblioteca(self.db_path)
        gestor2 = GestorGrafoBiblioteca(self.db_path)
        
        # Modificar datos desde ambos gestores
        gestor1.agregar_libro("L1", "Libro 1", "Autor 1")
        gestor2.agregar_libro("L2", "Libro 2", "Autor 2")
        
        # Guardar estados
        self.assertTrue(gestor1.guardar_estado())
        self.assertTrue(gestor2.guardar_estado())
        
        # Verificar que ambos estados se guardaron
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM grafo_estado")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 2)

    def test_manejo_errores(self):
        """Prueba el manejo de errores en la base de datos."""
        # Intentar acceder a una base de datos no existente
        gestor_error = GestorGrafoBiblioteca("no_existe.db")
        
        # Verificar que se maneja el error correctamente
        with self.assertRaises(Exception):
            gestor_error.cargar_estado()

if __name__ == '__main__':
    unittest.main() 