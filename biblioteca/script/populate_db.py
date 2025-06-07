"""
Script para poblar la base de datos con datos de ejemplo
"""
import sys
import os

# Añadir el directorio src al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database import Database

def populate_database():
    db = Database()
    try:
        # Datos de ejemplo para libros
        libros = [
            ('El Quijote', 'Miguel de Cervantes', 'Novela', '9788497593538', 1),
            ('Cien años de soledad', 'Gabriel García Márquez', 'Realismo mágico', '9788497592203', 1),
            ('1984', 'George Orwell', 'Ciencia ficción', '9788497591879', 1),
            ('El señor de los anillos', 'J.R.R. Tolkien', 'Fantasía', '9788497591886', 1),
            ('Harry Potter y la piedra filosofal', 'J.K. Rowling', 'Fantasía', '9788497591893', 1)
        ]

        # Datos de ejemplo para usuarios
        usuarios = [
            ('Juan Pérez', 'juan@email.com', '123456789'),
            ('María García', 'maria@email.com', '987654321'),
            ('Carlos López', 'carlos@email.com', '456789123'),
            ('Ana Martínez', 'ana@email.com', '789123456'),
            ('Pedro Sánchez', 'pedro@email.com', '321654987')
        ]

        # Insertar libros
        for libro in libros:
            db.execute_query(
                "INSERT INTO libros (titulo, autor, genero, isbn, disponible) VALUES (?, ?, ?, ?, ?)",
                libro
            )
        print("Libros agregados correctamente!")

        # Insertar usuarios
        for usuario in usuarios:
            db.execute_query(
                "INSERT INTO usuarios (nombre, email, telefono) VALUES (?, ?, ?)",
                usuario
            )
        print("Usuarios agregados correctamente!")

        # Crear algunos préstamos de ejemplo
        prestamos = [
            (1, 1, '2024-03-01', '2024-03-15', 0),  # Juan Pérez presta El Quijote
            (2, 3, '2024-03-02', '2024-03-16', 0),  # Carlos López presta Cien años de soledad
            (3, 2, '2024-03-03', '2024-03-17', 0),  # María García presta 1984
        ]

        for prestamo in prestamos:
            db.execute_query(
                "INSERT INTO prestamos (libro_id, usuario_id, fecha_prestamo, fecha_devolucion, devuelto) VALUES (?, ?, ?, ?, ?)",
                prestamo
            )
        print("Préstamos agregados correctamente!")

        print("\nBase de datos poblada exitosamente!")
        print("Se han agregado:")
        print("- 5 libros")
        print("- 5 usuarios")
        print("- 3 préstamos")

    except Exception as e:
        print(f"Error al poblar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_database() 