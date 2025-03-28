from datetime import datetime

class Biblioteca:
    def __init__(self):
        self.libros = []
        self.usuarios = []
        self.prestamos = []

    def agregar_libro(self, libro):
        if not libro.titulo.strip() or len(libro.titulo) < 2:
            print("❌ Error: El título del libro no puede estar vacío o tener un solo carácter.")
            return False
        if not libro.autor.strip() or len(libro.autor) < 2:
            print("❌ Error: El autor del libro no puede estar vacío o tener un solo carácter.")
            return False
        if not libro.isbn.strip():
            print("❌ Error: El ISBN del libro no puede estar vacío.")
            return False

        self.libros.append(libro)
        print(f"✅ Libro '{libro.titulo}' agregado correctamente.")
        return True

    def registrar_usuario(self, usuario):
        try:
            for u in self.usuarios:
                if u.correoU == usuario.correoU:
                    print("❌ Error: Este correo ya está registrado.")
                    return False

            self.usuarios.append(usuario)
            print(f"✅ Usuario '{usuario.nombre}' registrado correctamente.")
            return True
        except ValueError as e:
            print(f"❌ Error al registrar usuario: {e}")
            return False

    def mostrar_libros_disponibles(self):
        if not self.libros:
            print("📚 No hay libros disponibles en la biblioteca.")
        else:
            print("📚 Libros disponibles:")
            for libro in self.libros:
                if libro.disponibilidad():
                    print(libro)

    def mostrar_usuarios(self):
        if not self.usuarios:
            print("👤 No hay usuarios registrados.")
        else:
            print("👤 Usuarios registrados:")
            for usuario in self.usuarios:
                print(usuario)
                
    def prestar_libro(self, usuario, libro):
        if usuario not in self.usuarios:
            print("❌ Error: El usuario no está registrado en la biblioteca.")
            return False

        if libro not in self.libros:
            print("❌ Error: El libro no está disponible en la biblioteca.")
            return False

        if not libro.disponibilidad():
            print("❌ Error: El libro ya está prestado.")
            return False

        from models.Prestamo import Prestamo  # Import here to avoid circular import
        prestamo = Prestamo(usuario, libro)
        
        libro.disponible = False
        usuario.libros_prestados.append(libro)
        self.prestamos.append(prestamo)
        
        print(f"📖 '{libro.titulo}' ha sido prestado a {usuario.nombre}.")
        return True
            
    def devolver_libro(self, usuario, libro):
        prestamo = next((p for p in self.prestamos if p.usuario == usuario and p.libro == libro), None)
        
        if not prestamo:
            print("❌ Error: Este libro no está registrado como prestado por este usuario.")
            return False

        libro.disponible = True
        usuario.libros_prestados.remove(libro)
        
        prestamo.fecha_devolucion = datetime.now()
        prestamo.estado = "Devuelto"
        
        print(f"✅ '{libro.titulo}' ha sido devuelto por {usuario.nombre}.")
        return True

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
            
            # Verificación de usuarios y libros usando self
            if len(self.usuarios) > 0 and len(self.libros) > 0:
                print("║ 4️⃣ Prestar libro        ║")
            
            if len(self.prestamos) > 0:
                print("║ 5️⃣ Devolver libro       ║")

            print("║ 6️⃣ Mostrar usuarios     ║")
            print("║ 0️⃣ Salir                ║")
            print("╚══════════════════════════╝")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                nombre = input("Ingrese nombre del usuario: ")
                telefono = input("Ingrese número de teléfono: ")
                correo = input("Ingrese correo electrónico: ")
                try:
                    usuario = Usuario(nombre, telefono, correo)
                    self.registrar_usuario(usuario)
                except ValueError as e:
                    print(f"Error: {e}")

            elif opcion == "2":
                titulo = input("Ingrese el título del libro: ")
                autor = input("Ingrese el autor: ")
                isbn = input("Ingrese el ISBN: ")
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
                        usuario_correo = input("Ingrese el correo del usuario: ")
                        usuario = next((u for u in self.usuarios if u.correoU == usuario_correo), None)
                        if usuario:
                            self.prestar_libro(usuario, self.libros[libro_idx])
                        else:
                            print("❌ Usuario no encontrado.")
                    else:
                        print("❌ Número de libro inválido.")
                except ValueError:
                    print("❌ Entrada no válida. Ingrese un número.")

            elif opcion == "5" and len(self.prestamos) > 0:
                print("\n📜 Libros prestados:")
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
                break

            else:
                print("❌ Opción inválida. Intente nuevamente.")