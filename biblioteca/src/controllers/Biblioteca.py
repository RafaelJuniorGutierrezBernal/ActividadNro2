import re
import unicodedata
from datetime import datetime

class Biblioteca:
    def __init__(self):
        self.libros = []
        self.usuarios = []
        self.prestamos = []

    def normalizar_texto(self, texto):
        """Convierte el texto a minúsculas y elimina tildes para búsquedas."""
        texto = texto.lower()
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    def agregar_libro(self, libro):
        if not libro.titulo.strip() or len(libro.titulo) < 2:
            print("❌ Error: El título del libro no puede estar vacío o tener un solo carácter.")
            return False
        if not libro.autor.strip() or len(libro.autor) < 2:
            print("❌ Error: El autor del libro no puede estar vacío o tener un solo carácter.")
            return False
        if not libro.isbn.strip():
            print("❌ Error: El ISBN no puede estar vacío.")
            return False
        
        # Validar formato de ISBN
        if not self.validar_isbn(libro.isbn):
            return False
            
        # Verificar si ya existe un libro con el mismo ISBN
        if any(l.isbn == libro.isbn for l in self.libros):
            print(f"❌ Error: Ya existe un libro con el ISBN {libro.isbn}.")
            return False

        # Guardamos la versión normalizada para búsqueda
        libro.titulo_normalizado = self.normalizar_texto(libro.titulo)
        libro.autor_normalizado = self.normalizar_texto(libro.autor)

        self.libros.append(libro)
        print(f"✅ Libro '{libro.titulo}' agregado correctamente.")
        return True
        
    def validar_isbn(self, isbn):
        """Valida que el ISBN tenga un formato correcto (10 o 13 dígitos)."""
        isbn = isbn.replace("-", "").replace(" ", "")  # Eliminar guiones y espacios
        
        if not isbn.isdigit():
            print("❌ Error: El ISBN debe contener solo dígitos (se permiten guiones y espacios).")
            return False
            
        if len(isbn) != 10 and len(isbn) != 13:
            print("❌ Error: El ISBN debe tener 10 o 13 dígitos.")
            return False
            
        return True

    def registrar_usuario(self, usuario):
        try:
            if not usuario.nombre.strip() or len(usuario.nombre) < 2:
                print("❌ Error: El nombre no puede estar vacío o tener un solo carácter.")
                return False
                
            # Validar teléfono y correo
            if not self.validar_telefono(usuario.telefono):
                return False
                
            if not self.validar_correo(usuario.correoU):
                return False
            
            # Verificación con versión normalizada del correo
            correo_normalizado = usuario.correoU.lower()
            if any(u.correoU.lower() == correo_normalizado for u in self.usuarios):
                print("❌ Error: Este correo ya está registrado.")
                return False

            # Guardamos la versión normalizada para búsquedas futuras
            usuario.nombre_normalizado = self.normalizar_texto(usuario.nombre)

            self.usuarios.append(usuario)
            print(f"✅ Usuario '{usuario.nombre}' registrado correctamente.")
            return True
        except ValueError as e:
            print(f"❌ Error al registrar usuario: {e}")
            return False

    def mostrar_libros_disponibles(self):
        libros_disponibles = [libro for libro in self.libros if libro.disponibilidad()]
        if not libros_disponibles:
            print("📚 No hay libros disponibles en la biblioteca.")
        else:
            print("📚 Libros disponibles:")
            for i, libro in enumerate(libros_disponibles, 1):
                print(f"{i}. {libro}")

    def mostrar_usuarios(self):
        if not self.usuarios:
            print("👤 No hay usuarios registrados.")
        else:
            print("👤 Usuarios registrados:")
            for i, usuario in enumerate(self.usuarios, 1):
                print(f"{i}. {usuario}")
                
    def prestar_libro(self, usuario, libro):
        # Validar que el usuario exista en el sistema
        if usuario not in self.usuarios:
            print("❌ Error: El usuario no está registrado en la biblioteca.")
            return False

        # Validar que el libro exista en el sistema
        if libro not in self.libros:
            print("❌ Error: El libro no está disponible en la biblioteca.")
            return False

        # Validar explícitamente la disponibilidad del libro
        if not libro.disponible:
            print("❌ Error: El libro ya está prestado.")
            return False
            
        # Validar límite de préstamos por usuario (máximo 3 libros)
        if len(usuario.libros_prestados) >= 3:
            print(f"❌ Error: {usuario.nombre} ya tiene el máximo de 3 libros prestados.")
            return False

        from models.Prestamo import Prestamo  # Importación dentro del método para evitar circular imports
        prestamo = Prestamo(usuario, libro)
        
        libro.disponible = False
        usuario.libros_prestados.append(libro)
        self.prestamos.append(prestamo)
        
        print(f"📖 '{libro.titulo}' ha sido prestado a {usuario.nombre}.")
        return True
            
    def devolver_libro(self, usuario, libro):
        # Buscar el préstamo activo
        prestamo = next((p for p in self.prestamos if p.usuario == usuario and p.libro == libro and p.estado == "Prestado"), None)
        
        if not prestamo:
            print("❌ Error: Este libro no está registrado como prestado por este usuario.")
            return False
        
        # Validar que el libro esté en la lista de préstamos del usuario
        if libro not in usuario.libros_prestados:
            print("❌ Error: Inconsistencia en el sistema. Contacte al administrador.")
            return False

        libro.disponible = True
        usuario.libros_prestados.remove(libro)
        
        prestamo.fecha_devolucion = datetime.now()
        prestamo.estado = "Devuelto"
        
        print(f"✅ '{libro.titulo}' ha sido devuelto por {usuario.nombre}.")
        return True
        
    def validar_telefono(self, telefono):
        """Verifica que el número de teléfono solo contenga dígitos y tenga entre 7 y 15 caracteres."""
        # Eliminar espacios y guiones para la validación
        telefono_limpio = telefono.replace(" ", "").replace("-", "")
        
        if telefono_limpio.isdigit() and 7 <= len(telefono_limpio) <= 15:
            return True
        print("❌ Error: El número de teléfono debe contener solo dígitos y tener entre 7 y 15 caracteres.")
        return False

    def validar_correo(self, correo):
        """Verifica que el correo tenga un formato válido."""
        if not correo or not correo.strip():
            print("❌ Error: El correo electrónico no puede estar vacío.")
            return False
            
        patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(patron_correo, correo):
            return True
        print("❌ Error: El correo electrónico no es válido.")
        return False
    
    def buscar_usuario(self, criterio, valor):
        """Busca un usuario por nombre, correo o teléfono."""
        valor_normalizado = self.normalizar_texto(valor) if criterio == "nombre" else valor.lower()
        
        if criterio == "nombre":
            return next((u for u in self.usuarios if self.normalizar_texto(u.nombre).find(valor_normalizado) != -1), None)
        elif criterio == "correo":
            return next((u for u in self.usuarios if u.correoU.lower() == valor_normalizado), None)
        elif criterio == "telefono":
            telefono_limpio = valor.replace(" ", "").replace("-", "")
            return next((u for u in self.usuarios if u.telefono.replace(" ", "").replace("-", "") == telefono_limpio), None)
        return None
        
    def mostrar_menu(self):
        from models.Libro import Libro
        from models.Usuario import Usuario

        while True:
            print("\n╔══════════════════════════╗")
            print("║ 📚  BIBLIOTECA VIRTUAL   ║")
            print("╠══════════════════════════╣")
            print("║ 1️⃣ Registrar usuario    ║")
            print("║ 2️⃣ Agregar libro        ║")
            print("║ 3️⃣ Consultar libros     ║")

            if len(self.usuarios) > 0 and len(self.libros) > 0:
                print("║ 4️⃣ Prestar libro        ║")

            if len(self.prestamos) > 0:
                print("║ 5️⃣ Devolver libro       ║")

            print("║ 6️⃣ Mostrar usuarios     ║")
            print("║ 0️⃣ Salir                ║")
            print("╚══════════════════════════╝")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                nombre = input("Ingrese nombre del usuario: ").strip()
                if not nombre:
                    print("❌ Error: El nombre no puede estar vacío.")
                    continue
                    
                telefono = input("Ingrese número de teléfono: ").strip()
                correo = input("Ingrese correo electrónico: ").strip()

                if self.validar_telefono(telefono) and self.validar_correo(correo):
                    try:
                        usuario = Usuario(nombre, telefono, correo)
                        self.registrar_usuario(usuario)
                    except ValueError as e:
                        print(f"Error: {e}")
                else:
                    print("❌ Registro cancelado debido a datos inválidos.")

            elif opcion == "2":
                titulo = input("Ingrese el título del libro: ").strip()
                if not titulo:
                    print("❌ Error: El título no puede estar vacío.")
                    continue
                    
                autor = input("Ingrese el autor: ").strip()
                isbn = input("Ingrese el ISBN: ").strip()

                libro = Libro(titulo, autor, isbn)
                self.agregar_libro(libro)

            elif opcion == "3":
                self.mostrar_libros_disponibles()

            elif opcion == "4" and len(self.usuarios) > 0 and len(self.libros) > 0:
                print("\n📖 Libros disponibles:")
                for i, libro in enumerate(self.libros, 1):
                    print(f"{i}. {libro}")

                try:
                    libro_idx = int(input("Seleccione el número del libro a prestar: ")) - 1
                    if 0 <= libro_idx < len(self.libros):
                        usuario_correo = input("Ingrese el correo del usuario: ").strip()
                        usuario = self.buscar_usuario("correo", usuario_correo)
                        if usuario:
                            self.prestar_libro(usuario, self.libros[libro_idx])
                        else:
                            print("❌ Usuario no encontrado.")
                    else:
                        print("❌ Número de libro inválido.")
                except ValueError:
                    print("❌ Entrada no válida. Ingrese un número.")

            elif opcion == "5" and len(self.prestamos) > 0:
                print("\n📚 Libros prestados:")
                for i, prestamo in enumerate(self.prestamos, 1):
                    print(f"{i}. {prestamo.libro} (Prestado a: {prestamo.usuario.nombre})")

                try:
                    prestamo_idx = int(input("Seleccione el número del préstamo a devolver: ")) - 1
                    if 0 <= prestamo_idx < len(self.prestamos):
                        prestamo = self.prestamos[prestamo_idx]
                        self.devolver_libro(prestamo.usuario, prestamo.libro)
                    else:
                        print("❌ Número de préstamo inválido.")
                except ValueError:
                    print("❌ Entrada no válida. Ingrese un número.")

            elif opcion == "6":
                self.mostrar_usuarios()

            elif opcion == "0":
                print("👋 ¡Gracias por usar la biblioteca!")
                return  # Usar return en lugar de break si estamos en una función.

            else:
                print("❌ Opción inválida. Intente nuevamente.")