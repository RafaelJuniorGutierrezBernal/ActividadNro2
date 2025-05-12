import re
import unicodedata
from datetime import datetime
from models.ArbolBinario import ArbolBinario
from models.Libro import Libro # Agregado para asegurar que Libro esté disponible para isinstance
from models.Usuario import Usuario # Agregado para asegurar que Usuario esté disponible para isinstance
from models.Prestamo import Prestamo # Agregado para asegurar que Prestamo esté disponible para isinstance


class Biblioteca:
    # Eliminado el parámetro cargar_datos ya que no hay persistencia para cargar
    def __init__(self):
        # Cambio de listas a diccionarios
        self.libros = {}  # ISBN como clave
        self.usuarios = {}  # Correo como clave
        self.prestamos = {}  # ID generado como clave
        # Índices secundarios para búsquedas
        self.libros_por_titulo = {}  # Título normalizado a lista de ISBNs
        self.libros_por_autor = {}  # Autor normalizado a lista de ISBNs
        self.usuarios_por_nombre = {}  # Nombre normalizado a lista de correos
        self.usuarios_por_telefono = {}  # Teléfono a correo
        # Árboles binarios para búsquedas rápidas
        self.arbol_titulos = ArbolBinario()  # Árbol ordenado por título normalizado
        self.arbol_autores = ArbolBinario()  # Árbol ordenado por autor normalizado
        self.arbol_isbn = ArbolBinario()     # Árbol ordenado por ISBN
        self.arbol_nombres = ArbolBinario()  # Árbol ordenado por nombre normalizado
        self.arbol_correos = ArbolBinario()  # Árbol ordenado por correo
        self.arbol_telefonos = ArbolBinario() # Árbol ordenado por teléfono
        self.id_prestamo = 0  # Contador para generar IDs únicos

    def normalizar_texto(self, texto):
        """Convierte el texto a minúsculas y elimina tildes para búsquedas."""
        if texto is None:
            return ""
        texto = texto.lower()
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    def _actualizar_indices_libro(self, libro):
        """Actualiza los índices secundarios para un libro."""
        if libro is None or not hasattr(libro, 'isbn') or not libro.isbn:
            return False
            
        titulo_normalizado = self.normalizar_texto(libro.titulo)
        autor_normalizado = self.normalizar_texto(libro.autor)
        
        # Actualizar índice por título (diccionario)
        if titulo_normalizado not in self.libros_por_titulo:
            self.libros_por_titulo[titulo_normalizado] = []
        if libro.isbn not in self.libros_por_titulo[titulo_normalizado]:
            self.libros_por_titulo[titulo_normalizado].append(libro.isbn)
            
        # Actualizar índice por autor (diccionario)
        if autor_normalizado not in self.libros_por_autor:
            self.libros_por_autor[autor_normalizado] = []
        if libro.isbn not in self.libros_por_autor[autor_normalizado]:
            self.libros_por_autor[autor_normalizado].append(libro.isbn)
            
        # Actualizar árboles binarios para búsqueda rápida
        self.arbol_titulos.insertar(titulo_normalizado, libro.isbn)
        self.arbol_autores.insertar(autor_normalizado, libro.isbn)
        self.arbol_isbn.insertar(libro.isbn, libro)
        
        return True

    def _actualizar_indices_usuario(self, usuario):
        """Actualiza los índices secundarios para un usuario."""
        if usuario is None or not hasattr(usuario, 'correoU') or not usuario.correoU:
            return False
            
        nombre_normalizado = self.normalizar_texto(usuario.nombre)
        telefono_limpio = usuario.numeroTelefono.replace(" ", "").replace("-", "") if usuario.numeroTelefono else ""
        
        # Actualizar índice por nombre (diccionario)
        if nombre_normalizado not in self.usuarios_por_nombre:
            self.usuarios_por_nombre[nombre_normalizado] = []
        if usuario.correoU not in self.usuarios_por_nombre[nombre_normalizado]:
            self.usuarios_por_nombre[nombre_normalizado].append(usuario.correoU)
            
        # Actualizar índice por teléfono (diccionario)
        if telefono_limpio:
            self.usuarios_por_telefono[telefono_limpio] = usuario.correoU
            
        # Actualizar árboles binarios para búsqueda rápida
        self.arbol_nombres.insertar(nombre_normalizado, usuario.correoU)
        self.arbol_correos.insertar(usuario.correoU.lower(), usuario)
        if telefono_limpio:
            self.arbol_telefonos.insertar(telefono_limpio, usuario.correoU)
        
        return True

    def agregar_libro(self, libro):
        if libro is None:
            print("❌ Error: El libro no puede ser nulo.")
            return False
            
        if not libro.titulo or not libro.titulo.strip() or len(libro.titulo) < 2:
            print("❌ Error: El título del libro no puede estar vacío o tener un solo carácter.")
            return False
            
        if not libro.autor or not libro.autor.strip() or len(libro.autor) < 2:
            print("❌ Error: El autor del libro no puede estar vacío o tener un solo carácter.")
            return False
            
        if not libro.isbn or not libro.isbn.strip():
            print("❌ Error: El ISBN no puede estar vacío.")
            return False
        
        # Validar formato de ISBN
        if not self.validar_isbn(libro.isbn):
            return False
            
        # Verificar si ya existe un libro con el mismo ISBN
        if libro.isbn in self.libros:
            print(f"❌ Error: Ya existe un libro con el ISBN {libro.isbn}.")
            return False

        # Guardamos la versión normalizada para búsqueda
        libro.titulo_normalizado = self.normalizar_texto(libro.titulo)
        libro.autor_normalizado = self.normalizar_texto(libro.autor)

        # Guardar libro en diccionario principal
        self.libros[libro.isbn] = libro
        
        # Actualizar índices secundarios
        self._actualizar_indices_libro(libro)
        
        print(f"✅ Libro '{libro.titulo}' agregado correctamente.")
        return True
        
    def validar_isbn(self, isbn):
        """Valida que el ISBN tenga un formato correcto (10 o 13 dígitos)."""
        if isbn is None:
            print("❌ Error: El ISBN no puede ser nulo.")
            return False
            
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
            if usuario is None:
                print("❌ Error: El usuario no puede ser nulo.")
                return False
                
            if not usuario.nombre or not usuario.nombre.strip() or len(usuario.nombre) < 2:
                print("❌ Error: El nombre no puede estar vacío o tener un solo carácter.")
                return False
                
            # Validar teléfono y correo
            if not self.validar_telefono(usuario.numeroTelefono):
                return False
                
            if not self.validar_correo(usuario.correoU):
                return False
            
            # Verificación con versión normalizada del correo
            correo_normalizado = usuario.correoU.lower()
            if correo_normalizado in self.usuarios:
                print("❌ Error: Este correo ya está registrado.")
                return False

            # Guardamos la versión normalizada para búsquedas futuras
            usuario.nombre_normalizado = self.normalizar_texto(usuario.nombre)

            # Guardar usuario en diccionario principal
            self.usuarios[correo_normalizado] = usuario
            
            # Actualizar índices secundarios
            self._actualizar_indices_usuario(usuario)
            
            print(f"✅ Usuario '{usuario.nombre}' registrado correctamente.")
            return True
        except ValueError as e:
            print(f"❌ Error al registrar usuario: {e}")
            return False

    def mostrar_libros_disponibles(self):
        libros_disponibles = [libro for libro in self.libros.values() if libro.disponibilidad()]
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
            for i, usuario in enumerate(self.usuarios.values(), 1):
                print(f"{i}. {usuario}")
                
    def prestar_libro(self, usuario, libro):
        if usuario is None:
            print("❌ Error: El usuario no puede ser nulo.")
            return False
            
        if libro is None:
            print("❌ Error: El libro no puede ser nulo.")
            return False
            
        # Validar que el usuario exista en el sistema
        if usuario.correoU not in self.usuarios:
            print("❌ Error: El usuario no está registrado en la biblioteca.")
            return False

        # Validar que el libro exista en el sistema
        if libro.isbn not in self.libros:
            print("❌ Error: El libro no está disponible en la biblioteca.")
            return False

        # Validar explícitamente la disponibilidad del libro
        if not self.libros[libro.isbn].disponible:
            print("❌ Error: El libro ya está prestado.")
            return False
            
        # Validar límite de préstamos por usuario (máximo 3 libros)
        if len(usuario.libros_prestados) >= 3:
            print(f"❌ Error: {usuario.nombre} ya tiene el máximo de 3 libros prestados.")
            return False

        from models.Prestamo import Prestamo  # Importación dentro del método para evitar circular imports
        prestamo = Prestamo(usuario, libro)
        
        # Generar ID único para el préstamo
        self.id_prestamo += 1
        prestamo_id = f"P{self.id_prestamo}"
        
        # Actualizar estado del libro y usuario
        self.libros[libro.isbn].disponible = False
        usuario.libros_prestados.append(libro)
        
        # Guardar préstamo en el diccionario
        self.prestamos[prestamo_id] = prestamo
        
        print(f"📖 '{libro.titulo}' ha sido prestado a {usuario.nombre}.")
        return True
            
    def devolver_libro(self, usuario, libro):
        if usuario is None or libro is None:
            print("❌ Error: El usuario y el libro no pueden ser nulos.")
            return False
            
        # Buscar el préstamo activo (ahora con búsqueda en diccionario)
        prestamo_encontrado = None
        for prestamo_id, prestamo in self.prestamos.items():
            if (prestamo.usuario.correoU == usuario.correoU and 
                prestamo.libro.isbn == libro.isbn and 
                prestamo.estado == "Activo"):
                prestamo_encontrado = prestamo
                break
        
        if not prestamo_encontrado:
            print("❌ Error: Este libro no está registrado como prestado por este usuario.")
            return False
        
        # Validar que el libro esté en la lista de préstamos del usuario
        if libro not in usuario.libros_prestados:
            print("❌ Error: Inconsistencia en el sistema. Contacte al administrador.")
            return False

        # Actualizar estado del libro y usuario
        self.libros[libro.isbn].disponible = True
        usuario.libros_prestados.remove(libro)
        
        # Actualizar información del préstamo
        prestamo_encontrado.fecha_devolucion = datetime.now()
        prestamo_encontrado.estado = "Devuelto"
        
        print(f"✅ '{libro.titulo}' ha sido devuelto por {usuario.nombre}.")
        return True
        
    def validar_telefono(self, telefono):
        """Verifica que el número de teléfono solo contenga dígitos y tenga entre 7 y 15 caracteres."""
        if telefono is None:
            print("❌ Error: El número de teléfono no puede ser nulo.")
            return False
            
        # Eliminar espacios y guiones para la validación
        telefono_limpio = telefono.replace(" ", "").replace("-", "")
        
        if telefono_limpio.isdigit() and 7 <= len(telefono_limpio) <= 15:
            return True
        print("❌ Error: El número de teléfono debe contener solo dígitos y tener entre 7 y 15 caracteres.")
        return False

    def validar_correo(self, correo):
        """Verifica que el correo tenga un formato válido."""
        if correo is None or not correo or not correo.strip():
            print("❌ Error: El correo electrónico no puede estar vacío o nulo.")
            return False
            
        patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(patron_correo, correo):
            return True
        print("❌ Error: El correo electrónico no es válido.")
        return False
    
    def buscar_usuario(self, criterio, valor):
        """Busca un usuario por nombre, correo o teléfono usando los índices y árboles binarios."""
        if criterio is None or valor is None:
            print("❌ Error: Los criterios de búsqueda no pueden ser nulos.")
            return None
            
        if criterio == "nombre":
            valor_normalizado = self.normalizar_texto(valor)
            
            # Búsqueda utilizando el árbol binario para la búsqueda por prefijos
            correos_list = self.arbol_nombres.buscar_por_prefijo(valor_normalizado)
            
            if correos_list and len(correos_list) > 0:
                # Tomar el primer correo encontrado si hay varios
                correo = correos_list[0] if not isinstance(correos_list[0], list) else correos_list[0][0]
                if correo in self.usuarios:
                    return self.usuarios[correo]
            
            # Si no se encuentra en el árbol, buscar en el diccionario tradicional
            usuarios_encontrados = []
            for nombre_clave in self.usuarios_por_nombre:
                if valor_normalizado in nombre_clave:
                    # Para cada nombre encontrado, obtener sus correos
                    for correo in self.usuarios_por_nombre[nombre_clave]:
                        if correo in self.usuarios:
                            usuarios_encontrados.append(self.usuarios[correo])
            return usuarios_encontrados[0] if usuarios_encontrados else None
            
        elif criterio == "correo":
            correo_normalizado = valor.lower()
            
            # Búsqueda directa en el árbol de correos
            usuario = self.arbol_correos.buscar(correo_normalizado)
            
            # Si no se encuentra en el árbol, buscar en el diccionario
            if usuario is None and correo_normalizado in self.usuarios:
                usuario = self.usuarios[correo_normalizado]
                
            return usuario
            
        elif criterio == "telefono":
            telefono_limpio = valor.replace(" ", "").replace("-", "")
            
            # Búsqueda en el árbol de teléfonos
            correo = self.arbol_telefonos.buscar(telefono_limpio)
            
            # Si no se encuentra en el árbol, buscar en el diccionario
            if correo is None:
                correo = self.usuarios_por_telefono.get(telefono_limpio)
                
            return self.usuarios.get(correo) if correo else None
            
        return None
        
    def buscar_libro(self, criterio, valor):
        """Busca un libro por título, autor o ISBN usando los índices y árboles binarios."""
        if criterio is None or valor is None:
            print("❌ Error: Los criterios de búsqueda no pueden ser nulos.")
            return []
            
        if criterio == "titulo":
            valor_normalizado = self.normalizar_texto(valor)
            
            # Búsqueda utilizando el árbol binario para la búsqueda por prefijos
            isbn_list = self.arbol_titulos.buscar_por_prefijo(valor_normalizado)
            libros_encontrados = []
            
            # Si no se encuentra en el árbol, usar el diccionario tradicional como respaldo
            if not isbn_list:
                # Buscar todos los títulos que contienen la cadena normalizada
                for titulo_clave in self.libros_por_titulo:
                    if valor_normalizado in titulo_clave:
                        # Para cada título encontrado, obtener sus ISBNs
                        for isbn in self.libros_por_titulo[titulo_clave]:
                            if isbn in self.libros:
                                libros_encontrados.append(self.libros[isbn])
            else:
                # Convertir ISBNs en objetos Libro
                for isbn in isbn_list:
                    # Si el ISBN es una lista (múltiples libros con el mismo título)
                    if isinstance(isbn, list):
                        for un_isbn in isbn:
                            if un_isbn in self.libros:
                                libros_encontrados.append(self.libros[un_isbn])
                    elif isbn in self.libros:
                        libros_encontrados.append(self.libros[isbn])
            
            return libros_encontrados
            
        elif criterio == "autor":
            valor_normalizado = self.normalizar_texto(valor)
            
            # Búsqueda utilizando el árbol binario para la búsqueda por prefijos
            isbn_list = self.arbol_autores.buscar_por_prefijo(valor_normalizado)
            libros_encontrados = []
            
            # Si no se encuentra en el árbol, usar el diccionario tradicional como respaldo
            if not isbn_list:
                # Buscar todos los autores que contienen la cadena normalizada
                for autor_clave in self.libros_por_autor:
                    if valor_normalizado in autor_clave:
                        # Para cada autor encontrado, obtener sus ISBNs
                        for isbn in self.libros_por_autor[autor_clave]:
                            if isbn in self.libros:
                                libros_encontrados.append(self.libros[isbn])
            else:
                # Convertir ISBNs en objetos Libro
                for isbn in isbn_list:
                    # Si el ISBN es una lista (múltiples libros con el mismo autor)
                    if isinstance(isbn, list):
                        for un_isbn in isbn:
                            if un_isbn in self.libros:
                                libros_encontrados.append(self.libros[un_isbn])
                    elif isbn in self.libros:
                        libros_encontrados.append(self.libros[isbn])
            
            return libros_encontrados
            
        elif criterio == "isbn":
            isbn_limpio = valor.replace("-", "").replace(" ", "")
            
            # Búsqueda directa en el árbol de ISBN
            libro = self.arbol_isbn.buscar(isbn_limpio)
            
            # Si no se encuentra en el árbol, buscar en el diccionario
            if libro is None and isbn_limpio in self.libros:
                libro = self.libros[isbn_limpio]
                
            return [libro] if libro else []
            
        return []
        
    # ELIMINADO: Este bloque de código estaba fuera de cualquier método y usaba persistencia.
    # """Guarda todos los datos de la biblioteca en archivos."""
    # print("Guardando datos de la biblioteca...")
    # exito = self.persistencia.guardar_biblioteca(self)
    # if exito:
    #     print("✅ Datos guardados correctamente.")
    # else:
    #     print("❌ Error al guardar los datos.")
    # return exito
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas sobre los datos de la biblioteca."""
        total_libros = len(self.libros)
        libros_disponibles = sum(1 for libro in self.libros.values() if libro.disponible)
        libros_prestados = total_libros - libros_disponibles
        
        total_usuarios = len(self.usuarios)
        usuarios_con_prestamos = sum(1 for usuario in self.usuarios.values() if usuario.libros_prestados)
        
        total_prestamos = len(self.prestamos)
        prestamos_activos = sum(1 for prestamo in self.prestamos.values() if prestamo.estado == "Activo")
        prestamos_devueltos = total_prestamos - prestamos_activos
        
        print("\n📊 ESTADÍSTICAS DE LA BIBLIOTECA")
        print(f"Total de libros: {total_libros}")
        print(f"Libros disponibles: {libros_disponibles}")
        print(f"Libros prestados: {libros_prestados}")
        print(f"Total de usuarios: {total_usuarios}")
        print(f"Usuarios con préstamos activos: {usuarios_con_prestamos}")
        print(f"Total de préstamos: {total_prestamos}")
        print(f"Préstamos activos: {prestamos_activos}")
        print(f"Préstamos devueltos: {prestamos_devueltos}")

    def mostrar_menu(self):
        from models.Libro import Libro
        from models.Usuario import Usuario

        while True:
            print("\n╔══════════════════════════╗")
            print("║ 📚 BIBLIOTECA VIRTUAL      ║")
            print("╠══════════════════════════╣")
            print("║1️⃣ Registrar usuario         ║")
            print("║2️⃣ Agregar libro             ║")
            print("║3️⃣ Consultar libros          ║")

            if len(self.usuarios) > 0 and len(self.libros) > 0:
                print("4️⃣ Prestar libro             ║")

            if len(self.prestamos) > 0:
                print("5️⃣ Devolver libro           ║")

            print("║6️⃣ Mostrar usuarios         ║")
            print("║7️⃣ Buscar                   ║")
            print("║8️⃣ Estadísticas             ║")
            print("║0️⃣ Salir                    ║") 
            print("╚══════════════════════════╝")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                nombre = input("Ingrese nombre del usuario: ").strip()
                if not nombre:
                    print("❌ Error: El nombre no puede estar vacío.")
                    continue
                    
                telefono = input("Ingrese número de teléfono: ").strip()
                correo = input("Ingrese correo electrónico: ").strip()

                try:
                    usuario = Usuario(nombre, telefono, correo)
                    exito = self.registrar_usuario(usuario)
                except ValueError as e:
                    print(f"❌ Error: {e}")
                    print("❌ Registro cancelado debido a datos inválidos.")

            elif opcion == "2":
                titulo = input("Ingrese el título del libro: ").strip()
                autor = input("Ingrese el autor: ").strip()
                isbn = input("Ingrese el ISBN: ").strip()

                try:
                    libro = Libro(titulo, autor, isbn)
                    exito = self.agregar_libro(libro)
                except ValueError as e:
                    print(f"❌ Error: {e}")
                    print("❌ Registro de libro cancelado debido a datos inválidos.")

            elif opcion == "3":
                self.mostrar_libros_disponibles()

            elif opcion == "4" and len(self.usuarios) > 0 and len(self.libros) > 0:
                # Mostrar usuarios disponibles
                self.mostrar_usuarios()
                if not self.usuarios:
                    continue
                    
                indice_usuario = input("Seleccione el número de usuario: ")
                try:
                    indice_usuario = int(indice_usuario)
                    if indice_usuario < 1 or indice_usuario > len(self.usuarios):
                        print("❌ Selección inválida.")
                        continue
                    usuario_seleccionado = list(self.usuarios.values())[indice_usuario - 1]
                except (ValueError, IndexError):
                    print("❌ Selección inválida.")
                    continue
                
                # Filtrar y mostrar solo libros disponibles
                libros_disponibles = [libro for libro in self.libros.values() if libro.disponible]
                if not libros_disponibles:
                    print("📚 No hay libros disponibles para préstamo.")
                    continue
                    
                print("\n📖 Libros disponibles:")
                for i, libro in enumerate(libros_disponibles, 1):
                    print(f"{i}. {libro}")
                    
                indice_libro = input("Seleccione el número de libro: ")
                try:
                    indice_libro = int(indice_libro)
                    if indice_libro < 1 or indice_libro > len(libros_disponibles):
                        print("❌ Selección inválida.")
                        continue
                    libro_seleccionado = libros_disponibles[indice_libro - 1]
                except (ValueError, IndexError):
                    print("❌ Selección inválida.")
                    continue
                
                exito = self.prestar_libro(usuario_seleccionado, libro_seleccionado)
                if exito:
                    print("✅ Libro prestado exitosamente.")

            elif opcion == "5" and len(self.prestamos) > 0:
                # Primero seleccionar usuario con préstamos activos
                usuarios_con_prestamos = [usuario for usuario in self.usuarios.values() if usuario.libros_prestados]
                if not usuarios_con_prestamos:
                    print("❌ No hay préstamos activos.")
                    continue
                    
                print("\n👤 Usuarios con préstamos activos:")
                for i, usuario in enumerate(usuarios_con_prestamos, 1):
                    print(f"{i}. {usuario}")
                    
                indice_usuario = input("Seleccione el número de usuario: ")
                try:
                    indice_usuario = int(indice_usuario)
                    if indice_usuario < 1 or indice_usuario > len(usuarios_con_prestamos):
                        print("❌ Selección inválida.")
                        continue
                    usuario_seleccionado = usuarios_con_prestamos[indice_usuario - 1]
                except (ValueError, IndexError):
                    print("❌ Selección inválida.")
                    continue
                
                # Mostrar libros prestados del usuario
                if not usuario_seleccionado.libros_prestados:
                    print(f"❌ {usuario_seleccionado.nombre} no tiene libros prestados.")
                    continue
                    
                print(f"\n📚 Libros prestados a {usuario_seleccionado.nombre}:")
                for i, libro in enumerate(usuario_seleccionado.libros_prestados, 1):
                    print(f"{i}. {libro}")
                    
                indice_libro = input("Seleccione el número de libro a devolver: ")
                try:
                    indice_libro = int(indice_libro)
                    if indice_libro < 1 or indice_libro > len(usuario_seleccionado.libros_prestados):
                        print("❌ Selección inválida.")
                        continue
                    libro_seleccionado = usuario_seleccionado.libros_prestados[indice_libro - 1]
                except (ValueError, IndexError):
                    print("❌ Selección inválida.")
                    continue
                
                exito = self.devolver_libro(usuario_seleccionado, libro_seleccionado)
                if exito:
                    print("✅ Libro devuelto exitosamente.")

            elif opcion == "6":
                self.mostrar_usuarios()
            
            elif opcion == "7":
                print("\n🔍 Opciones de búsqueda:")
                print("1. Buscar usuario")
                print("2. Buscar libro")
                print("3. Búsqueda por prefijo (usando árboles)")
                opcion_busqueda = input("Seleccione una opción: ")
                
                if opcion_busqueda == "1":
                    print("\n👤 Criterios de búsqueda de usuario:")
                    print("1. Por nombre")
                    print("2. Por correo")
                    print("3. Por teléfono")
                    criterio = input("Seleccione un criterio: ")
                    
                    criterio_map = {"1": "nombre", "2": "correo", "3": "telefono"}
                    if criterio not in criterio_map:
                        print("❌ Criterio inválido.")
                        continue
                        
                    valor = input(f"Ingrese el {criterio_map[criterio]} a buscar: ").strip()
                    if not valor:
                        print("❌ El valor de búsqueda no puede estar vacío.")
                        continue
                        
                    usuario = self.buscar_usuario(criterio_map[criterio], valor)
                    if usuario:
                        print(f"\n✅ Usuario encontrado:\n{usuario}")
                    else:
                        print("❌ No se encontró ningún usuario con ese criterio.")
                        
                elif opcion_busqueda == "2":
                    print("\n📚 Criterios de búsqueda de libro:")
                    print("1. Por título")
                    print("2. Por autor")
                    print("3. Por ISBN")
                    criterio = input("Seleccione un criterio: ")
                    
                    criterio_map = {"1": "titulo", "2": "autor", "3": "isbn"}
                    if criterio not in criterio_map:
                        print("❌ Criterio inválido.")
                        continue
                        
                    valor = input(f"Ingrese el {criterio_map[criterio]} a buscar: ").strip()
                    if not valor:
                        print("❌ El valor de búsqueda no puede estar vacío.")
                        continue
                        
                    libros = self.buscar_libro(criterio_map[criterio], valor)
                    if libros:
                        print(f"\n✅ Se encontraron {len(libros)} libro(s):")
                        for i, libro in enumerate(libros, 1):
                            print(f"{i}. {libro}")
                    else:
                        print("❌ No se encontró ningún libro con ese criterio.")
                
                elif opcion_busqueda == "3":
                    print("\n🌳 Búsqueda por prefijo (usando árboles binarios):")
                    print("1. Títulos de libros que comienzan con...")
                    print("2. Autores que comienzan con...")
                    print("3. Nombres de usuarios que comienzan con...")
                    tipo_prefijo = input("Seleccione una opción: ")
                    
                    if tipo_prefijo == "1":
                        prefijo = input("Ingrese el prefijo del título: ").strip().lower()
                        if not prefijo:
                            print("❌ El prefijo no puede estar vacío.")
                            continue
                            
                        # Búsqueda en el árbol de títulos
                        isbn_list = self.arbol_titulos.buscar_por_prefijo(prefijo)
                        if isbn_list:
                            print(f"\n✅ Libros con títulos que comienzan con '{prefijo}':")
                            libros_mostrados = []
                            contador = 1
                            
                            # Procesar los resultados del árbol
                            for isbn_o_lista in isbn_list:
                                if isinstance(isbn_o_lista, list):
                                    for isbn in isbn_o_lista:
                                        if isbn in self.libros and self.libros[isbn] not in libros_mostrados:
                                            libros_mostrados.append(self.libros[isbn])
                                else: # Es un solo ISBN
                                    if isbn_o_lista in self.libros and self.libros[isbn_o_lista] not in libros_mostrados:
                                        libros_mostrados.append(self.libros[isbn_o_lista])
                            
                            for i, libro in enumerate(libros_mostrados, 1):
                                print(f"{i}. {libro}")
                        else:
                            print("❌ No se encontraron libros con ese prefijo de título.")

                    elif tipo_prefijo == "2":
                        prefijo = input("Ingrese el prefijo del autor: ").strip().lower()
                        if not prefijo:
                            print("❌ El prefijo no puede estar vacío.")
                            continue
                            
                        # Búsqueda en el árbol de autores
                        isbn_list = self.arbol_autores.buscar_por_prefijo(prefijo)
                        if isbn_list:
                            print(f"\n✅ Libros de autores que comienzan con '{prefijo}':")
                            libros_mostrados = []
                            for isbn_o_lista in isbn_list:
                                if isinstance(isbn_o_lista, list):
                                    for isbn in isbn_o_lista:
                                        if isbn in self.libros and self.libros[isbn] not in libros_mostrados:
                                            libros_mostrados.append(self.libros[isbn])
                                else: # Es un solo ISBN
                                    if isbn_o_lista in self.libros and self.libros[isbn_o_lista] not in libros_mostrados:
                                        libros_mostrados.append(self.libros[isbn_o_lista])

                            for i, libro in enumerate(libros_mostrados, 1):
                                print(f"{i}. {libro}")
                        else:
                            print("❌ No se encontraron libros de autores con ese prefijo.")

                    elif tipo_prefijo == "3":
                        prefijo = input("Ingrese el prefijo del nombre de usuario: ").strip().lower()
                        if not prefijo:
                            print("❌ El prefijo no puede estar vacío.")
                            continue
                            
                        # Búsqueda en el árbol de nombres de usuarios
                        correos_list = self.arbol_nombres.buscar_por_prefijo(prefijo)
                        if correos_list:
                            print(f"\n✅ Usuarios cuyos nombres comienzan con '{prefijo}':")
                            usuarios_mostrados = []
                            for correo_o_lista in correos_list:
                                if isinstance(correo_o_lista, list):
                                    for correo in correo_o_lista:
                                        if correo in self.usuarios and self.usuarios[correo] not in usuarios_mostrados:
                                            usuarios_mostrados.append(self.usuarios[correo])
                                else: # Es un solo correo
                                    if correo_o_lista in self.usuarios and self.usuarios[correo_o_lista] not in usuarios_mostrados:
                                        usuarios_mostrados.append(self.usuarios[correo_o_lista])
                            
                            for i, usuario in enumerate(usuarios_mostrados, 1):
                                print(f"{i}. {usuario}")
                        else:
                            print("❌ No se encontraron usuarios con ese prefijo de nombre.")
                    else:
                        print("❌ Opción de búsqueda por prefijo inválida.")
                else:
                    print("❌ Opción de búsqueda inválida.")

            elif opcion == "8":
                self.mostrar_estadisticas()

            elif opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Por favor, intente de nuevo.")