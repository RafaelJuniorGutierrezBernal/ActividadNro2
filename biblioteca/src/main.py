from controllers.Biblioteca import Biblioteca
from models.Libro import Libro
from models.Usuario import Usuario
from models.Prestamo import Prestamo
from models.Autor import Autor
from models.Genero import Genero

def main():
    """
    Función principal que inicia el sistema de biblioteca.
    """
    print("🏛️ Iniciando Sistema de Biblioteca Virtual")
    biblioteca = Biblioteca()
    biblioteca.mostrar_menu()

if __name__ == "__main__":
    main()