import os
import sys

# Añadir el directorio src al path de Python de forma segura
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gestor_grafo_mejorado import GestorGrafoBiblioteca
import json

DB_PATH = "prueba_biblioteca_libros.db"

def limpiar_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def mostrar_libros_en_db():
    import sqlite3
    if not os.path.exists(DB_PATH):
        print("No existe la base de datos.")
        return
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT datos_grafo FROM grafo_estado ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            print("No hay datos guardados.")
            return
        datos = json.loads(row[0])
        print("\nLibros en la base de datos:")
        for node_id, attrs in datos['nodes'].items():
            if attrs.get('type') == 'libro':
                print(f"- ISBN: {attrs['isbn']}, Título: {attrs['titulo']}, Autor: {attrs['autor_nombre']}")

def main():
    limpiar_db()
    gestor = GestorGrafoBiblioteca(DB_PATH)
    print("Agregando libros...")
    gestor.agregar_libro("111", "Cien Años de Soledad", "Gabriel García Márquez")
    gestor.agregar_libro("222", "Rayuela", "Julio Cortázar")
    gestor.agregar_libro("333", "Pedro Páramo", "Juan Rulfo")
    gestor.guardar_estado()
    print("Libros guardados correctamente.\n")
    mostrar_libros_en_db()

    print("\nActualizando un libro...")
    gestor.agregar_libro("222", "Rayuela (Edición Revisada)", "Julio Cortázar")
    gestor.guardar_estado()
    mostrar_libros_en_db()

    print("\nAgregando usuario y vinculando libro...")
    gestor.agregar_usuario("lector@correo.com", "Lector Prueba")
    gestor.vincular_libro_con_usuario("111", "lector@correo.com", "PRESTAMO")
    gestor.guardar_estado()
    mostrar_libros_en_db()

if __name__ == "__main__":
    main() 