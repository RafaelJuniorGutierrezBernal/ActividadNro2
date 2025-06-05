import unittest
import os
import tempfile
from datetime import datetime
from ..gestor_grafo_mejorado import GestorGrafoBiblioteca

class TestGestorGrafoBiblioteca(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para cada prueba."""
        # Crear una base de datos temporal para las pruebas
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.gestor = GestorGrafoBiblioteca(self.temp_db.name)

    def tearDown(self):
        """Limpieza después de cada prueba."""
        self.gestor = None
        os.unlink(self.temp_db.name)

    def test_agregar_libro(self):
        """Prueba la adición de un libro al grafo."""
        # Agregar un libro
        resultado = self.gestor.agregar_libro(
            "1234567890",
            "Don Quijote",
            "Cervantes"
        )
        self.assertTrue(resultado)
        
        # Verificar que el libro se agregó correctamente
        node_id = self.gestor._get_node_id("libro", "1234567890")
        self.assertTrue(self.gestor.grafo.has_node(node_id))
        self.assertEqual(
            self.gestor.grafo.nodes[node_id]['titulo'],
            "Don Quijote"
        )

    def test_agregar_usuario(self):
        """Prueba la adición de un usuario al grafo."""
        # Agregar un usuario
        self.gestor.agregar_usuario(
            "usuario@test.com",
            "Usuario Test"
        )
        
        # Verificar que el usuario se agregó correctamente
        node_id = self.gestor._get_node_id("usuario", "usuario@test.com")
        self.assertTrue(self.gestor.grafo.has_node(node_id))
        self.assertEqual(
            self.gestor.grafo.nodes[node_id]['nombre'],
            "Usuario Test"
        )

    def test_vincular_libro_usuario(self):
        """Prueba la vinculación entre un libro y un usuario."""
        # Agregar libro y usuario
        self.gestor.agregar_libro("123", "Libro Test", "Autor Test")
        self.gestor.agregar_usuario("usuario@test.com", "Usuario Test")
        
        # Vincular
        resultado = self.gestor.vincular_libro_con_usuario(
            "123",
            "usuario@test.com",
            "PRESTAMO"
        )
        self.assertTrue(resultado)
        
        # Verificar la vinculación
        libro_node = self.gestor._get_node_id("libro", "123")
        usuario_node = self.gestor._get_node_id("usuario", "usuario@test.com")
        self.assertTrue(
            self.gestor.grafo.has_edge(usuario_node, libro_node)
        )

    def test_buscar_camino(self):
        """Prueba la búsqueda de caminos entre nodos."""
        # Crear una estructura de prueba
        self.gestor.agregar_libro("L1", "Libro 1", "Autor 1")
        self.gestor.agregar_libro("L2", "Libro 2", "Autor 2")
        self.gestor.agregar_usuario("U1", "Usuario 1")
        
        # Vincular
        self.gestor.vincular_libro_con_usuario("L1", "U1", "PRESTAMO")
        self.gestor.vincular_libro_con_usuario("L2", "U1", "PRESTAMO")
        
        # Buscar camino
        camino = self.gestor.buscar_camino_entre_nodos(
            self.gestor._get_node_id("usuario", "U1"),
            self.gestor._get_node_id("libro", "L2")
        )
        self.assertIsNotNone(camino)
        self.assertTrue(len(camino) > 0)

    def test_recomendaciones(self):
        """Prueba el sistema de recomendaciones."""
        # Crear datos de prueba
        self.gestor.agregar_usuario("U1", "Usuario 1")
        self.gestor.agregar_usuario("U2", "Usuario 2")
        self.gestor.agregar_libro("L1", "Libro 1", "Autor 1")
        self.gestor.agregar_libro("L2", "Libro 2", "Autor 2")
        
        # Vincular
        self.gestor.vincular_libro_con_usuario("L1", "U1", "PRESTAMO")
        self.gestor.vincular_libro_con_usuario("L1", "U2", "PRESTAMO")
        self.gestor.vincular_libro_con_usuario("L2", "U2", "PRESTAMO")
        
        # Obtener recomendaciones
        recomendaciones = self.gestor.obtener_recomendaciones("U1")
        self.assertIsInstance(recomendaciones, list)
        self.assertTrue(len(recomendaciones) > 0)

    def test_persistencia(self):
        """Prueba la persistencia de datos."""
        # Agregar datos de prueba
        self.gestor.agregar_libro("123", "Libro Test", "Autor Test")
        self.gestor.agregar_usuario("usuario@test.com", "Usuario Test")
        
        # Guardar estado
        self.assertTrue(self.gestor.guardar_estado())
        
        # Crear nuevo gestor y cargar estado
        nuevo_gestor = GestorGrafoBiblioteca(self.temp_db.name)
        self.assertTrue(nuevo_gestor.cargar_estado())
        
        # Verificar que los datos se cargaron correctamente
        node_id = nuevo_gestor._get_node_id("libro", "123")
        self.assertTrue(nuevo_gestor.grafo.has_node(node_id))

    def test_analisis_eficiencia(self):
        """Prueba el análisis de eficiencia."""
        # Agregar datos de prueba
        self.gestor.agregar_libro("L1", "Libro 1", "Autor 1")
        self.gestor.agregar_usuario("U1", "Usuario 1")
        self.gestor.vincular_libro_con_usuario("L1", "U1", "PRESTAMO")
        
        # Obtener métricas
        metricas = self.gestor.analizar_eficiencia()
        self.assertIsInstance(metricas, dict)
        self.assertIn('numero_nodos', metricas)
        self.assertIn('numero_aristas', metricas)
        self.assertIn('densidad', metricas)

if __name__ == '__main__':
    unittest.main() 