import unittest
import os
import sqlite3
import json
from datetime import datetime
from biblioteca.src.gestor_grafo_mejorado import GestorGrafoBiblioteca

class TestLibrosDatabase(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para las pruebas de libros."""
        self.db_path = "test_biblioteca_libros.db"
        self.gestor = GestorGrafoBiblioteca(self.db_path)
        
    def tearDown(self):
        """Limpieza después de las pruebas."""
        self.gestor = None
        import gc
        gc.collect()  # Forzar recolección de basura para cerrar conexiones
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                # Intentar de nuevo tras un pequeño retraso
                import time
                time.sleep(0.1)
                os.remove(self.db_path)

    def test_guardar_libro(self):
        """Prueba el guardado de un libro en la base de datos."""
        # Agregar un libro
        isbn = "1234567890"
        titulo = "Don Quijote"
        autor = "Cervantes"
        
        self.gestor.agregar_libro(isbn, titulo, autor)
        self.gestor.guardar_estado()
        
        # Verificar en la base de datos
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT datos_grafo FROM grafo_estado ORDER BY id DESC LIMIT 1")
            datos = json.loads(cursor.fetchone()[0])
            
            # Verificar que el libro está en los nodos
            node_id = f"libro_{isbn}"
            self.assertIn(node_id, datos['nodes'])
            
            # Verificar los atributos del libro
            libro_data = datos['nodes'][node_id]
            self.assertEqual(libro_data['titulo'], titulo)
            self.assertEqual(libro_data['autor_nombre'], autor)
            self.assertEqual(libro_data['isbn'], isbn)

    def test_guardar_multiples_libros(self):
        """Prueba el guardado de múltiples libros."""
        libros = [
            ("123", "Libro 1", "Autor 1"),
            ("456", "Libro 2", "Autor 2"),
            ("789", "Libro 3", "Autor 3")
        ]
        
        # Agregar varios libros
        for isbn, titulo, autor in libros:
            self.gestor.agregar_libro(isbn, titulo, autor)
        
        self.gestor.guardar_estado()
        
        # Verificar en la base de datos
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT datos_grafo FROM grafo_estado ORDER BY id DESC LIMIT 1")
            datos = json.loads(cursor.fetchone()[0])
            
            # Verificar que todos los libros están en los nodos
            for isbn, titulo, autor in libros:
                node_id = f"libro_{isbn}"
                self.assertIn(node_id, datos['nodes'])
                
                # Verificar los atributos de cada libro
                libro_data = datos['nodes'][node_id]
                self.assertEqual(libro_data['titulo'], titulo)
                self.assertEqual(libro_data['autor_nombre'], autor)
                self.assertEqual(libro_data['isbn'], isbn)

    def test_actualizar_libro(self):
        """Prueba la actualización de un libro existente."""
        # Agregar un libro
        isbn = "123"
        self.gestor.agregar_libro(isbn, "Título Original", "Autor Original")
        self.gestor.guardar_estado()
        
        # Actualizar el libro
        self.gestor.agregar_libro(isbn, "Nuevo Título", "Nuevo Autor")
        self.gestor.guardar_estado()
        
        # Verificar en la base de datos
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT datos_grafo FROM grafo_estado ORDER BY id DESC LIMIT 1")
            datos = json.loads(cursor.fetchone()[0])
            
            # Verificar que el libro se actualizó
            node_id = f"libro_{isbn}"
            libro_data = datos['nodes'][node_id]
            self.assertEqual(libro_data['titulo'], "Nuevo Título")
            self.assertEqual(libro_data['autor_nombre'], "Nuevo Autor")

    def test_libro_con_relaciones(self):
        """Prueba el guardado de un libro con sus relaciones."""
        # Agregar libro y usuario
        self.gestor.agregar_libro("123", "Libro Test", "Autor Test")
        self.gestor.agregar_usuario("usuario@test.com", "Usuario Test")
        
        # Crear relación
        self.gestor.vincular_libro_con_usuario("123", "usuario@test.com", "PRESTAMO")
        self.gestor.guardar_estado()
        
        # Verificar en la base de datos
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT datos_grafo FROM grafo_estado ORDER BY id DESC LIMIT 1")
            datos = json.loads(cursor.fetchone()[0])
            
            # Verificar nodos
            self.assertIn('libro_123', datos['nodes'])
            self.assertIn('usuario_usuario@test.com', datos['nodes'])
            
            # Verificar arista
            aristas = datos['edges']
            self.assertTrue(any(
                u == 'usuario_usuario@test.com' and 
                v == 'libro_123' and 
                d.get('relation') == 'PRESTAMO'
                for u, v, d in aristas
            ))

    def test_cargar_libros(self):
        """Prueba la carga de libros desde la base de datos."""
        # Crear y guardar datos
        self.gestor.agregar_libro("123", "Libro Test", "Autor Test")
        self.gestor.guardar_estado()
        
        # Crear nuevo gestor y cargar
        nuevo_gestor = GestorGrafoBiblioteca(self.db_path)
        nuevo_gestor.cargar_estado()
        
        # Verificar que el libro se cargó correctamente
        node_id = nuevo_gestor._get_node_id("libro", "123")
        self.assertTrue(nuevo_gestor.grafo.has_node(node_id))
        
        # Verificar atributos
        libro_data = nuevo_gestor.grafo.nodes[node_id]
        self.assertEqual(libro_data['titulo'], "Libro Test")
        self.assertEqual(libro_data['autor_nombre'], "Autor Test")
        self.assertEqual(libro_data['isbn'], "123")

if __name__ == '__main__':
    unittest.main() 