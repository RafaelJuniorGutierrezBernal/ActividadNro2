from controllers.Biblioteca import Biblioteca
from models.Libro import Libro
from models.Usuario import Usuario
from models.Prestamo import Prestamo

def main():
    biblioteca = Biblioteca()
    biblioteca.mostrar_menu()

if __name__ == "__main__":
    main()