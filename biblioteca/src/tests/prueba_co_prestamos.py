import sys
import os

# Agregar el directorio src al path de Python de manera segura
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.Biblioteca import Biblioteca
from models.Libro import Libro
from models.Usuario import Usuario

def main():
    print("🏛️ Iniciando Prueba de Co-préstamos")
    
    # Crear instancia de biblioteca
    biblioteca = Biblioteca()
    
    # Agregar algunos libros
    print("\n📚 Agregando libros...")
    libros = [
        ("978-84-376-0494-7", "Cien años de soledad", "Gabriel García Márquez"),
        ("978-84-376-0495-4", "El amor en los tiempos del cólera", "Gabriel García Márquez"),
        ("978-84-376-0496-1", "Crónica de una muerte anunciada", "Gabriel García Márquez"),
        ("978-84-376-0497-8", "Rayuela", "Julio Cortázar"),
        ("978-84-376-0498-5", "Pedro Páramo", "Juan Rulfo"),
        ("978-84-376-0499-2", "Los detectives salvajes", "Roberto Bolaño"),
        ("978-84-376-0500-5", "2666", "Roberto Bolaño"),
        ("978-84-376-0501-2", "La casa de los espíritus", "Isabel Allende"),
        ("978-84-376-0502-9", "El Aleph", "Jorge Luis Borges"),
        ("978-84-376-0503-6", "Ficciones", "Jorge Luis Borges")
    ]
    
    for isbn, titulo, autor in libros:
        biblioteca.agregar_libro(titulo, autor, isbn)
        print(f"✅ Agregado: {titulo}")
    
    # Agregar algunos usuarios
    print("\n👥 Agregando usuarios...")
    usuarios = [
        ("usuario1@test.com", "Juan Pérez", "1234567890"),
        ("usuario2@test.com", "María García", "2345678901"),
        ("usuario3@test.com", "Carlos López", "3456789012"),
        ("usuario4@test.com", "Ana Martínez", "4567890123"),
        ("usuario5@test.com", "Pedro Sánchez", "5678901234")
    ]
    
    for correo, nombre, telefono in usuarios:
        biblioteca.registrar_usuario(nombre, telefono, correo)
        print(f"✅ Agregado: {nombre}")
    
    # Realizar algunos préstamos para crear co-préstamos
    print("\n📖 Realizando préstamos...")
    prestamos = [
        # Usuario 1: Fan de García Márquez
        ("usuario1@test.com", "978-84-376-0494-7"),  # Cien años de soledad
        ("usuario1@test.com", "978-84-376-0495-4"),  # El amor en los tiempos del cólera
        ("usuario1@test.com", "978-84-376-0496-1"),  # Crónica de una muerte anunciada
        
        # Usuario 2: Fan de Bolaño
        ("usuario2@test.com", "978-84-376-0499-2"),  # Los detectives salvajes
        ("usuario2@test.com", "978-84-376-0500-5"),  # 2666
        ("usuario2@test.com", "978-84-376-0494-7"),  # También lee García Márquez
        
        # Usuario 3: Fan de Borges
        ("usuario3@test.com", "978-84-376-0502-9"),  # El Aleph
        ("usuario3@test.com", "978-84-376-0503-6"),  # Ficciones
        ("usuario3@test.com", "978-84-376-0497-8"),  # También lee Cortázar
        
        # Usuario 4: Variedad de lecturas
        ("usuario4@test.com", "978-84-376-0494-7"),  # Cien años de soledad
        ("usuario4@test.com", "978-84-376-0499-2"),  # Los detectives salvajes
        ("usuario4@test.com", "978-84-376-0502-9"),  # El Aleph
        
        # Usuario 5: Fan de literatura latinoamericana
        ("usuario5@test.com", "978-84-376-0494-7"),  # Cien años de soledad
        ("usuario5@test.com", "978-84-376-0497-8"),  # Rayuela
        ("usuario5@test.com", "978-84-376-0498-5")   # Pedro Páramo
    ]
    
    for correo, isbn in prestamos:
        biblioteca.realizar_prestamo(correo, isbn)
        print(f"✅ Préstamo: {biblioteca.libros[isbn].titulo} a {biblioteca.usuarios[correo].nombre}")
    
    # Construir el grafo de co-préstamos
    print("\n🔄 Construyendo grafo de co-préstamos...")
    biblioteca.gestor_grafo.construir_grafo_co_prestamos(biblioteca.prestamos, biblioteca.libros)
    
    # Visualizar el grafo
    print("\n📊 Visualizando grafo de co-préstamos...")
    biblioteca.gestor_grafo.visualizar_grafo("co-préstamos")
    
    # Obtener recomendaciones para cada usuario
    print("\n📚 Obteniendo recomendaciones para cada usuario...")
    for correo, nombre, _ in usuarios:
        print(f"\nRecomendaciones para {nombre}:")
        recomendaciones = biblioteca.gestor_grafo.obtener_libros_recomendados(correo, biblioteca)
        if recomendaciones:
            for i, rec in enumerate(recomendaciones, 1):
                print(f"{i}. {rec['titulo']} - {rec['autor']} (Score: {rec['score']})")
        else:
            print("No hay recomendaciones disponibles.")
    
    print("\n✨ Prueba completada exitosamente!")

if __name__ == "__main__":
    main() 