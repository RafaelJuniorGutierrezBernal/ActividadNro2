import re
import unicodedata
from datetime import datetime
from models.ArbolBinario import ArbolBinario
from models.Libro import Libro
from models.Usuario import Usuario
from models.Prestamo import Prestamo
from gestor_grafo_mejorado import GestorGrafoBiblioteca
from models.Autor import Autor
from models.Genero import Genero


class Biblioteca:
    def __init__(self):
        self.libros = {}  # ISBN como clave
        self.usuarios = {}  # Correo como clave
        self.prestamos = {}  # ID generado como clave
        self.autores = {} # ID como clave
        self.generos = {} # ID como clave

        # Índices secundarios para búsquedas
        self.libros_por_titulo = {}  # Título normalizado a lista de ISBNs
        self.libros_por_autor = {}  # Autor normalizado a lista de ISBNs
        self.usuarios_por_nombre = {}  # Nombre normalizado a lista de correos
        self.usuarios_por_telefono = {}  # Teléfono a correo
        
        # Árboles binarios para búsquedas rápidas
        self.arbol_titulos = ArbolBinario()  # Árbol ordenado por título normalizado
        self.arbol_autores = ArbolBinario()  # Árbol ordenado por autor normalizado
        self.arbol_isbn = ArbolBinario()     # Árbol ordenado por ISBN
        self.arbol_nombres_usuarios = ArbolBinario() # Árbol ordenado por nombre normalizado
        self.arbol_correos_usuarios = ArbolBinario() # Árbol ordenado por correo normalizado

        # Inicializar el gestor de grafos
        self.gestor_grafo = GestorGrafoBiblioteca()
        self.grafo_actual_tipo = None # Para saber qué grafo está cargado actualmente

    def normalizar_texto(self, texto):
        """Normaliza texto a minúsculas y sin tildes para búsquedas."""
        if isinstance(texto, str):
            texto = texto.lower()
            texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
        return texto
    
    def agregar_libro(self, titulo, autor, isbn):
        try:
            libro = Libro(titulo, autor, isbn)
            if isbn in self.libros:
                print(f"❌ Error: El libro con ISBN '{isbn}' ya existe.")
                return False

            self.libros[isbn] = libro
            
            # Normalizar y agregar a los índices y árboles
            titulo_normalizado = self.normalizar_texto(titulo)
            autor_normalizado = self.normalizar_texto(autor)
            
            self.libros_por_titulo.setdefault(titulo_normalizado, []).append(isbn)
            self.libros_por_autor.setdefault(autor_normalizado, []).append(isbn)
            
            self.arbol_titulos.insertar(titulo_normalizado, isbn)
            self.arbol_autores.insertar(autor_normalizado, isbn)
            self.arbol_isbn.insertar(isbn, isbn) # El valor es el mismo ISBN para facilitar la búsqueda directa

            print(f"✅ Libro '{titulo}' agregado exitosamente.")
            return True
        except ValueError as e:
            print(f"❌ Error al agregar libro: {e}")
            return False

    def modificar_libro(self, isbn, nuevo_titulo=None, nuevo_autor=None, nueva_disponibilidad=None):
        if isbn not in self.libros:
            print(f"❌ Error: Libro con ISBN '{isbn}' no encontrado.")
            return False
        
        libro = self.libros[isbn]
        actualizado = False

        # Si se va a modificar el título, eliminar del viejo índice y árbol y agregar al nuevo
        if nuevo_titulo and nuevo_titulo != libro.titulo:
            old_titulo_normalizado = self.normalizar_texto(libro.titulo)
            if isbn in self.libros_por_titulo.get(old_titulo_normalizado, []):
                self.libros_por_titulo[old_titulo_normalizado].remove(isbn)
                if not self.libros_por_titulo[old_titulo_normalizado]:
                    del self.libros_por_titulo[old_titulo_normalizado]
            # No se elimina del árbol por clave, se debería reconstruir el árbol si queremos una limpieza perfecta
            # o simplemente dejar el nodo "obsoleto" (no es lo ideal para un AVL, pero simplifica sin persistencia)
            # Para este caso, vamos a asumir que la búsqueda por prefijo manejará las entradas múltiples
            # y que el acceso directo por ISBN es la fuente de verdad.
            
            libro.titulo = nuevo_titulo
            new_titulo_normalizado = self.normalizar_texto(nuevo_titulo)
            self.libros_por_titulo.setdefault(new_titulo_normalizado, []).append(isbn)
            self.arbol_titulos.insertar(new_titulo_normalizado, isbn) # Reinsertar para reflejar cambio
            actualizado = True

        # Si se va a modificar el autor, eliminar del viejo índice y árbol y agregar al nuevo
        if nuevo_autor and nuevo_autor != libro.autor:
            old_autor_normalizado = self.normalizar_texto(libro.autor)
            if isbn in self.libros_por_autor.get(old_autor_normalizado, []):
                self.libros_por_autor[old_autor_normalizado].remove(isbn)
                if not self.libros_por_autor[old_autor_normalizado]:
                    del self.libros_por_autor[old_autor_normalizado]

            libro.autor = nuevo_autor
            new_autor_normalizado = self.normalizar_texto(nuevo_autor)
            self.libros_por_autor.setdefault(new_autor_normalizado, []).append(isbn)
            self.arbol_autores.insertar(new_autor_normalizado, isbn) # Reinsertar para reflejar cambio
            actualizado = True

        if nueva_disponibilidad is not None and isinstance(nueva_disponibilidad, bool):
            libro.disponible = nueva_disponibilidad
            actualizado = True

        if actualizado:
            print(f"✅ Libro con ISBN '{isbn}' modificado exitosamente.")
            return True
        else:
            print("ℹ️ No se realizaron cambios en el libro.")
            return False

    def eliminar_libro(self, isbn):
        if isbn not in self.libros:
            print(f"❌ Error: Libro con ISBN '{isbn}' no encontrado.")
            return False
        
        libro = self.libros[isbn]
        if not libro.disponible: # Si el libro no está disponible (está prestado)
            print(f"❌ Error: El libro '{libro.titulo}' con ISBN '{isbn}' no puede ser eliminado porque está prestado.")
            return False
        
        # Eliminar de los índices secundarios y árboles
        titulo_normalizado = self.normalizar_texto(libro.titulo)
        if isbn in self.libros_por_titulo.get(titulo_normalizado, []):
            self.libros_por_titulo[titulo_normalizado].remove(isbn)
            if not self.libros_por_titulo[titulo_normalizado]:
                del self.libros_por_titulo[titulo_normalizado]
        
        autor_normalizado = self.normalizar_texto(libro.autor)
        if isbn in self.libros_por_autor.get(autor_normalizado, []):
            self.libros_por_autor[autor_normalizado].remove(isbn)
            if not self.libros_por_autor[autor_normalizado]:
                del self.libros_por_autor[autor_normalizado]

      
        self.arbol_isbn.eliminar(isbn)
    

        del self.libros[isbn]
        print(f"✅ Libro con ISBN '{isbn}' eliminado exitosamente.")
        return True

    def buscar_libro(self, tipo_busqueda, valor_busqueda):
        valor_normalizado = self.normalizar_texto(valor_busqueda)
        resultados_isbn = []

        if tipo_busqueda == "isbn":
            # Búsqueda directa en el diccionario
            if valor_busqueda in self.libros:
                resultados_isbn.append(valor_busqueda)
        elif tipo_busqueda == "titulo":
            # Búsqueda por prefijo en el árbol de títulos
            if self.arbol_titulos.raiz:
                claves_encontradas = self.arbol_titulos.buscar_por_prefijo(valor_normalizado)
                for clave_norm, isbns_list in claves_encontradas.items():
                    for isbn in isbns_list:
                        if isbn in self.libros: # Asegurarse de que el libro realmente exista
                            resultados_isbn.append(isbn)
        elif tipo_busqueda == "autor":
            # Búsqueda por prefijo en el árbol de autores
            if self.arbol_autores.raiz:
                claves_encontradas = self.arbol_autores.buscar_por_prefijo(valor_normalizado)
                for clave_norm, isbns_list in claves_encontradas.items():
                    for isbn in isbns_list:
                        if isbn in self.libros: # Asegurarse de que el libro realmente exista
                            resultados_isbn.append(isbn)
        else:
            print("❌ Tipo de búsqueda de libro no válido.")
            return []

        # Eliminar duplicados y retornar objetos Libro
        libros_encontrados = []
        for isbn in sorted(list(set(resultados_isbn))): # Ordenar para resultados consistentes
            libros_encontrados.append(self.libros[isbn])
        
        return libros_encontrados

    def registrar_usuario(self, nombre, numeroTelefono, correoU):
        try:
            usuario = Usuario(nombre, numeroTelefono, correoU)
            if correoU in self.usuarios:
                print(f"❌ Error: El usuario con correo '{correoU}' ya existe.")
                return False

            self.usuarios[correoU] = usuario
            
            # Normalizar y agregar a los índices y árboles
            nombre_normalizado = self.normalizar_texto(nombre)
            
            self.usuarios_por_nombre.setdefault(nombre_normalizado, []).append(correoU)
            self.usuarios_por_telefono[numeroTelefono] = correoU # Teléfono a correo es 1 a 1

            self.arbol_nombres_usuarios.insertar(nombre_normalizado, correoU)
            self.arbol_correos_usuarios.insertar(correoU, correoU) # El valor es el mismo correo para búsqueda directa

            print(f"✅ Usuario '{nombre}' registrado exitosamente.")
            return True
        except ValueError as e:
            print(f"❌ Error al registrar usuario: {e}")
            return False

    def modificar_usuario(self, correoU, nuevo_nombre=None, nuevo_numeroTelefono=None):
        if correoU not in self.usuarios:
            print(f"❌ Error: Usuario con correo '{correoU}' no encontrado.")
            return False
        
        usuario = self.usuarios[correoU]
        actualizado = False

        if nuevo_nombre and nuevo_nombre != usuario.nombre:
            old_nombre_normalizado = self.normalizar_texto(usuario.nombre)
            if correoU in self.usuarios_por_nombre.get(old_nombre_normalizado, []):
                self.usuarios_por_nombre[old_nombre_normalizado].remove(correoU)
                if not self.usuarios_por_nombre[old_nombre_normalizado]:
                    del self.usuarios_por_nombre[old_nombre_normalizado]
            
            usuario.nombre = nuevo_nombre
            new_nombre_normalizado = self.normalizar_texto(nuevo_nombre)
            self.usuarios_por_nombre.setdefault(new_nombre_normalizado, []).append(correoU)
            self.arbol_nombres_usuarios.insertar(new_nombre_normalizado, correoU) # Reinsertar para reflejar cambio
            actualizado = True

        if nuevo_numeroTelefono and nuevo_numeroTelefono != usuario.numeroTelefono:
            # Eliminar la entrada antigua si existe
            if usuario.numeroTelefono in self.usuarios_por_telefono:
                del self.usuarios_por_telefono[usuario.numeroTelefono]
            
            usuario.numeroTelefono = nuevo_numeroTelefono
            self.usuarios_por_telefono[nuevo_numeroTelefono] = correoU
            actualizado = True

        if actualizado:
            print(f"✅ Usuario con correo '{correoU}' modificado exitosamente.")
            return True
        else:
            print("ℹ️ No se realizaron cambios en el usuario.")
            return False

    def eliminar_usuario(self, correoU):
        if correoU not in self.usuarios:
            print(f"❌ Error: Usuario con correo '{correoU}' no encontrado.")
            return False
        
        usuario = self.usuarios[correoU]
        if usuario.libros_prestados: # Si el usuario tiene libros prestados
            print(f"❌ Error: El usuario '{usuario.nombre}' con correo '{correoU}' no puede ser eliminado porque tiene libros prestados.")
            return False
        
        # Eliminar de los índices secundarios y árboles
        nombre_normalizado = self.normalizar_texto(usuario.nombre)
        if correoU in self.usuarios_por_nombre.get(nombre_normalizado, []):
            self.usuarios_por_nombre[nombre_normalizado].remove(correoU)
            if not self.usuarios_por_nombre[nombre_normalizado]:
                del self.usuarios_por_nombre[nombre_normalizado]
        
        if usuario.numeroTelefono in self.usuarios_por_telefono:
            del self.usuarios_por_telefono[usuario.numeroTelefono]

        self.arbol_correos_usuarios.eliminar(correoU)
        # Para el arbol_nombres_usuarios, similar al caso de libros,
        # se asume que las búsquedas por prefijo funcionarán a pesar de entradas obsoletas
        # o se reconstruiría el árbol.

        del self.usuarios[correoU]
        print(f"✅ Usuario con correo '{correoU}' eliminado exitosamente.")
        return True

    def buscar_usuario(self, tipo_busqueda, valor_busqueda):
        valor_normalizado = self.normalizar_texto(valor_busqueda)
        resultados_correo = []

        if tipo_busqueda == "correo":
            # Búsqueda directa en el diccionario
            if valor_busqueda in self.usuarios:
                resultados_correo.append(valor_busqueda)
        elif tipo_busqueda == "nombre":
            # Búsqueda por prefijo en el árbol de nombres
            if self.arbol_nombres_usuarios.raiz:
                claves_encontradas = self.arbol_nombres_usuarios.buscar_por_prefijo(valor_normalizado)
                for clave_norm, correos_list in claves_encontradas.items():
                    for correo in correos_list:
                        if correo in self.usuarios: # Asegurarse de que el usuario realmente exista
                            resultados_correo.append(correo)
        else:
            print("❌ Tipo de búsqueda de usuario no válido.")
            return []

        # Eliminar duplicados y retornar objetos Usuario
        usuarios_encontrados = []
        for correo in sorted(list(set(resultados_correo))): # Ordenar para resultados consistentes
            usuarios_encontrados.append(self.usuarios[correo])
        
        return usuarios_encontrados

    def realizar_prestamo(self, correoU, isbn_libro):
        usuario = self.usuarios.get(correoU)
        libro = self.libros.get(isbn_libro)

        if not usuario:
            print(f"❌ Error: Usuario con correo '{correoU}' no encontrado.")
            return False
        if not libro:
            print(f"❌ Error: Libro con ISBN '{isbn_libro}' no encontrado.")
            return False
        if not libro.disponible:
            print(f"❌ Error: El libro '{libro.titulo}' no está disponible para préstamo.")
            return False
        
        # Verificar si el usuario ya tiene este libro en préstamo activo
        for prestamo in usuario.libros_prestados:
            if prestamo.libro.isbn == isbn_libro and prestamo.estado == "Activo":
                print(f"❌ Error: El usuario '{usuario.nombre}' ya tiene prestado el libro '{libro.titulo}'.")
                return False

        # Generar un ID único para el préstamo (ej. timestamp + hash)
        id_prestamo = f"P-{int(datetime.now().timestamp())}-{len(self.prestamos) + 1}"
        
        prestamo = Prestamo(usuario, libro)
        prestamo.id = id_prestamo
        
        self.prestamos[id_prestamo] = prestamo
        libro.disponible = False
        usuario.libros_prestados.append(prestamo) # Almacenar el objeto Prestamo completo

        print(f"✅ Préstamo de '{libro.titulo}' a '{usuario.nombre}' registrado con éxito. ID: {id_prestamo}")
        return True

    def registrar_devolucion(self, id_prestamo):
        prestamo = self.prestamos.get(id_prestamo)

        if not prestamo:
            print(f"❌ Error: Préstamo con ID '{id_prestamo}' no encontrado.")
            return False
        if prestamo.estado == "Devuelto":
            print(f"❌ Error: El préstamo con ID '{id_prestamo}' ya ha sido devuelto.")
            return False
        
        prestamo.fecha_devolucion = datetime.now()
        prestamo.estado = "Devuelto"
        prestamo.libro.disponible = True
        
        # Eliminar el préstamo de la lista de libros prestados del usuario
        # Se elimina el objeto Prestamo, no solo el libro
        prestamo.usuario.libros_prestados = [p for p in prestamo.usuario.libros_prestados if p.id != id_prestamo]

        print(f"✅ Devolución del libro '{prestamo.libro.titulo}' por '{prestamo.usuario.nombre}' registrada con éxito.")
        return True
    
    def listar_prestamos(self, estado=None):
        prestamos_a_mostrar = []
        if estado:
            for p in self.prestamos.values():
                if p.estado.lower() == estado.lower():
                    prestamos_a_mostrar.append(p)
        else:
            prestamos_a_mostrar = list(self.prestamos.values())
        
        if not prestamos_a_mostrar:
            print(f"ℹ️ No hay préstamos en estado '{estado}'." if estado else "ℹ️ No hay préstamos registrados.")
            return

        print("\n--- Listado de Préstamos ---")
        for i, prestamo in enumerate(prestamos_a_mostrar, 1):
            print(f"{i}. {prestamo}")
            
    def buscar_prestamo(self, tipo_busqueda, valor_busqueda):
        resultados = []
        if tipo_busqueda == "id":
            if valor_busqueda in self.prestamos:
                resultados.append(self.prestamos[valor_busqueda])
        elif tipo_busqueda == "isbn_libro":
            for prestamo in self.prestamos.values():
                if prestamo.libro.isbn == valor_busqueda:
                    resultados.append(prestamo)
        elif tipo_busqueda == "correo_usuario":
            for prestamo in self.prestamos.values():
                if prestamo.usuario.correoU == valor_busqueda:
                    resultados.append(prestamo)
        else:
            print("❌ Tipo de búsqueda de préstamo no válido.")
            return []
        
        return resultados

    def registrar_autor(self, id_autor, nombre):
        try:
            autor = Autor(id_autor, nombre)
            if id_autor in self.autores:
                print(f"❌ Error: El autor con ID '{id_autor}' ya existe.")
                return False
            self.autores[id_autor] = autor
            print(f"✅ Autor '{nombre}' (ID: {id_autor}) registrado exitosamente.")
            return True
        except ValueError as e:
            print(f"❌ Error al registrar autor: {e}")
            return False

    def listar_autores(self):
        if not self.autores:
            print("ℹ️ No hay autores registrados.")
            return
        print("\n--- Listado de Autores ---")
        for autor in self.autores.values():
            print(autor)

    def buscar_autor(self, id_o_nombre):
        id_o_nombre_normalizado = self.normalizar_texto(id_o_nombre)
        resultados = []
        for autor in self.autores.values():
            if self.normalizar_texto(autor.id) == id_o_nombre_normalizado or \
               self.normalizar_texto(autor.nombre).startswith(id_o_nombre_normalizado):
                resultados.append(autor)
        return resultados

    def registrar_genero(self, id_genero, nombre):
        try:
            genero = Genero(id_genero, nombre)
            if id_genero in self.generos:
                print(f"❌ Error: El género con ID '{id_genero}' ya existe.")
                return False
            self.generos[id_genero] = genero
            print(f"✅ Género '{nombre}' (ID: {id_genero}) registrado exitosamente.")
            return True
        except ValueError as e:
            print(f"❌ Error al registrar género: {e}")
            return False

    def listar_generos(self):
        if not self.generos:
            print("ℹ️ No hay géneros registrados.")
            return
        print("\n--- Listado de Géneros ---")
        for genero in self.generos.values():
            print(genero)

    def buscar_genero(self, id_o_nombre):
        id_o_nombre_normalizado = self.normalizar_texto(id_o_nombre)
        resultados = []
        for genero in self.generos.values():
            if self.normalizar_texto(genero.id) == id_o_nombre_normalizado or \
               self.normalizar_texto(genero.nombre).startswith(id_o_nombre_normalizado):
                resultados.append(genero)
        return resultados

    def asignar_autor_a_libro(self, isbn_libro, id_autor):
        libro = self.libros.get(isbn_libro)
        autor = self.autores.get(id_autor)

        if not libro:
            print(f"❌ Error: Libro con ISBN '{isbn_libro}' no encontrado.")
            return False
        if not autor:
            print(f"❌ Error: Autor con ID '{id_autor}' no encontrado.")
            return False

        # Asignar autor al libro (en este modelo simple, el autor del libro es un string)
        # Aquí actualizamos el atributo 'autor' del objeto Libro
        libro.autor = autor.nombre 
        print(f"✅ Autor '{autor.nombre}' asignado al libro '{libro.titulo}'.")
        # También actualizamos el índice por autor y el árbol de autores
        self.modificar_libro(isbn_libro, nuevo_autor=autor.nombre)
        return True

    def asignar_genero_a_libro(self, isbn_libro, id_genero):
        libro = self.libros.get(isbn_libro)
        genero = self.generos.get(id_genero)

        if not libro:
            print(f"❌ Error: Libro con ISBN '{isbn_libro}' no encontrado.")
            return False
        if not genero:
            print(f"❌ Error: Género con ID '{id_genero}' no encontrado.")
            return False
        
        # En este modelo simple, no tenemos un atributo 'genero' directo en Libro.
        # Si quisieras asociar géneros a libros, necesitarías añadir un atributo
        # 'genero' o 'generos' (lista) a la clase Libro.
        # Por ahora, solo simularé la asignación.
        print(f"ℹ️ Funcionalidad de asignación de género a libro no implementada directamente en el modelo Libro.")
        print(f"✅ Se ha simulado la asignación del género '{genero.nombre}' al libro '{libro.titulo}'.")
        return True


    # --- Menús Interactivos ---
    def _menu_gestion_libros(self):
        while True:
            print("\n--- Gestión de Libros ---")
            print("1. Agregar Libro")
            print("2. Modificar Libro")
            print("3. Eliminar Libro")
            print("4. Buscar Libro")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                titulo = input("Ingrese el título del libro: ").strip()
                autor = input("Ingrese el autor del libro: ").strip()
                isbn = input("Ingrese el ISBN del libro: ").strip()
                self.agregar_libro(titulo, autor, isbn)
            elif opcion == "2":
                isbn = input("Ingrese el ISBN del libro a modificar: ").strip()
                libro_existente = self.libros.get(isbn)
                if not libro_existente:
                    print(f"❌ Libro con ISBN '{isbn}' no encontrado.")
                    continue
                print(f"Modificando libro: {libro_existente.titulo} de {libro_existente.autor}")
                nuevo_titulo = input(f"Nuevo título (actual: {libro_existente.titulo}, dejar vacío para no cambiar): ").strip()
                nuevo_autor = input(f"Nuevo autor (actual: {libro_existente.autor}, dejar vacío para no cambiar): ").strip()
                nueva_disponibilidad_str = input(f"¿Disponible? (actual: {'Sí' if libro_existente.disponible else 'No'}, 's' para Sí, 'n' para No, dejar vacío para no cambiar): ").strip().lower()
                
                nueva_disponibilidad = None
                if nueva_disponibilidad_str == 's':
                    nueva_disponibilidad = True
                elif nueva_disponibilidad_str == 'n':
                    nueva_disponibilidad = False

                self.modificar_libro(isbn, nuevo_titulo if nuevo_titulo else None, 
                                     nuevo_autor if nuevo_autor else None, 
                                     nueva_disponibilidad)
            elif opcion == "3":
                isbn = input("Ingrese el ISBN del libro a eliminar: ").strip()
                self.eliminar_libro(isbn)
            elif opcion == "4":
                print("\n--- Buscar Libro ---")
                print("1. Por ISBN")
                print("2. Por Título (por prefijo)")
                print("3. Por Autor (por prefijo)")
                opcion_busqueda = input("Seleccione tipo de búsqueda: ").strip()
                valor_busqueda = input("Ingrese el valor de búsqueda: ").strip()

                tipo_busqueda_map = {"1": "isbn", "2": "titulo", "3": "autor"}
                tipo_busqueda = tipo_busqueda_map.get(opcion_busqueda)

                if tipo_busqueda:
                    resultados = self.buscar_libro(tipo_busqueda, valor_busqueda)
                    if resultados:
                        print("\n--- Libros Encontrados ---")
                        for i, libro in enumerate(resultados, 1):
                            print(f"{i}. {libro}")
                    else:
                        print("❌ No se encontraron libros con ese criterio.")
                else:
                    print("❌ Opción de búsqueda inválida.")
            elif opcion == "0":
                break
            else:
                print("❌ Opción inválida. Por favor, intente de nuevo.")

    def _menu_gestion_usuarios(self):
        while True:
            print("\n--- Gestión de Usuarios ---")
            print("1. Registrar Usuario")
            print("2. Modificar Usuario")
            print("3. Eliminar Usuario")
            print("4. Buscar Usuario")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                nombre = input("Ingrese el nombre del usuario: ").strip()
                telefono = input("Ingrese el número de teléfono del usuario: ").strip()
                correo = input("Ingrese el correo electrónico del usuario: ").strip()
                self.registrar_usuario(nombre, telefono, correo)
            elif opcion == "2":
                correo = input("Ingrese el correo del usuario a modificar: ").strip()
                usuario_existente = self.usuarios.get(correo)
                if not usuario_existente:
                    print(f"❌ Usuario con correo '{correo}' no encontrado.")
                    continue
                print(f"Modificando usuario: {usuario_existente.nombre}")
                nuevo_nombre = input(f"Nuevo nombre (actual: {usuario_existente.nombre}, dejar vacío para no cambiar): ").strip()
                nuevo_telefono = input(f"Nuevo teléfono (actual: {usuario_existente.numeroTelefono}, dejar vacío para no cambiar): ").strip()
                self.modificar_usuario(correo, nuevo_nombre if nuevo_nombre else None, 
                                       nuevo_telefono if nuevo_telefono else None)
            elif opcion == "3":
                correo = input("Ingrese el correo del usuario a eliminar: ").strip()
                self.eliminar_usuario(correo)
            if opcion == "4":
                print("\n--- Buscar Usuario ---")
                print("Seleccione el tipo de búsqueda que desea realizar:")
                print("1. Por Correo: Buscará usuarios por su dirección de correo electrónico.")
                print("2. Por Nombre (por prefijo): Buscará usuarios por un prefijo de su nombre.")
                opcion_busqueda = input("Ingrese el número de la opción deseada: ").strip()
                valor_busqueda = input("Ingrese el valor de búsqueda (correo o nombre): ").strip()

                tipo_busqueda_map = {"1": "correo", "2": "nombre"}
                tipo_busqueda = tipo_busqueda_map.get(opcion_busqueda)

                if tipo_busqueda:
                    resultados = self.buscar_usuario(tipo_busqueda, valor_busqueda)
                    if resultados:
                        print("\n--- Usuarios Encontrados ---")
                        for i, usuario in enumerate(resultados, 1):
                            print(f"{i}. {usuario}")
                    else:
                        print("❌ No se encontraron usuarios con ese criterio.")
                else:
                    print("❌ Opción de búsqueda inválida.")
            elif opcion == "0":
                break
            else:
                print("❌ Opción inválida. Por favor, intente de nuevo.")

    def _menu_gestion_autores_generos(self):
        while True:
            print("\n--- Gestión de Autores y Géneros ---")
            print("1. Gestión de Autores")
            print("2. Gestión de Géneros")
            print("3. Asignar Autor a Libro")
            print("4. Asignar Género a Libro")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                while True:
                    print("\n--- Gestión de Autores ---")
                    print("1. Registrar Autor")
                    print("2. Listar Autores")
                    print("3. Buscar Autor")
                    print("0. Volver al Menú Anterior")
                    opcion_autor = input("Seleccione una opción: ").strip()
                    if opcion_autor == "1":
                        id_autor = input("Ingrese ID del autor: ").strip()
                        nombre_autor = input("Ingrese nombre del autor: ").strip()
                        self.registrar_autor(id_autor, nombre_autor)
                    elif opcion_autor == "2":
                        self.listar_autores()
                    elif opcion_autor == "3":
                        busqueda = input("Ingrese ID o prefijo de nombre del autor: ").strip()
                        autores_encontrados = self.buscar_autor(busqueda)
                        if autores_encontrados:
                            print("\n--- Autores Encontrados ---")
                            for autor in autores_encontrados:
                                print(autor)
                        else:
                            print("❌ No se encontraron autores con ese criterio.")
                    elif opcion_autor == "0":
                        break
                    else:
                        print("❌ Opción inválida.")
            elif opcion == "2":
                while True:
                    print("\n--- Gestión de Géneros ---")
                    print("1. Registrar Género")
                    print("2. Listar Géneros")
                    print("3. Buscar Género")
                    print("0. Volver al Menú Anterior")
                    opcion_genero = input("Seleccione una opción: ").strip()
                    if opcion_genero == "1":
                        id_genero = input("Ingrese ID del género: ").strip()
                        nombre_genero = input("Ingrese nombre del género: ").strip()
                        self.registrar_genero(id_genero, nombre_genero)
                    elif opcion_genero == "2":
                        self.listar_generos()
                    elif opcion_genero == "3":
                        busqueda = input("Ingrese ID o prefijo de nombre del género: ").strip()
                        generos_encontrados = self.buscar_genero(busqueda)
                        if generos_encontrados:
                            print("\n--- Géneros Encontrados ---")
                            for genero in generos_encontrados:
                                print(genero)
                        else:
                            print("❌ No se encontraron géneros con ese criterio.")
                    elif opcion_genero == "0":
                        break
                    else:
                        print("❌ Opción inválida.")
            elif opcion == "3":
                isbn_libro = input("Ingrese el ISBN del libro al que desea asignar un autor: ").strip()
                id_autor = input("Ingrese el ID del autor a asignar: ").strip()
                self.asignar_autor_a_libro(isbn_libro, id_autor)
            elif opcion == "4":
                isbn_libro = input("Ingrese el ISBN del libro al que desea asignar un género: ").strip()
                id_genero = input("Ingrese el ID del género a asignar: ").strip()
                self.asignar_genero_a_libro(isbn_libro, id_genero) # Esta función solo simula la asignación por ahora
            elif opcion == "0":
                break
            else:
                print("❌ Opción inválida. Por favor, intente de nuevo.")

    def _menu_gestion_prestamos(self):
        while True:
            print("\n--- Gestión de Préstamos ---")
            print("1. Realizar Préstamo")
            print("2. Registrar Devolución")
            print("3. Listar Préstamos Activos")
            print("4. Listar Préstamos Devueltos")
            print("5. Listar Todos los Préstamos")
            print("6. Buscar Préstamo")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                correo_usuario = input("Ingrese el correo del usuario: ").strip()
                isbn_libro = input("Ingrese el ISBN del libro: ").strip()
                self.realizar_prestamo(correo_usuario, isbn_libro)
            elif opcion == "2":
                id_prestamo = input("Ingrese el ID del préstamo a devolver: ").strip()
                self.registrar_devolucion(id_prestamo)
            elif opcion == "3":
                self.listar_prestamos(estado="Activo")
            elif opcion == "4":
                self.listar_prestamos(estado="Devuelto")
            elif opcion == "5":
                self.listar_prestamos()
            elif opcion == "6":
                print("\n--- Buscar Préstamo ---")
                print("1. Por ID de Préstamo")
                print("2. Por ISBN de Libro")
                print("3. Por Correo de Usuario")
                opcion_busqueda = input("Seleccione tipo de búsqueda: ").strip()
                valor_busqueda = input("Ingrese el valor de búsqueda: ").strip()

                tipo_busqueda_map = {"1": "id", "2": "isbn_libro", "3": "correo_usuario"}
                tipo_busqueda = tipo_busqueda_map.get(opcion_busqueda)

                if tipo_busqueda:
                    resultados = self.buscar_prestamo(tipo_busqueda, valor_busqueda)
                    if resultados:
                        print("\n--- Préstamos Encontrados ---")
                        for i, prestamo in enumerate(resultados, 1):
                            print(f"{i}. {prestamo}")
                    else:
                        print("❌ No se encontraron préstamos con ese criterio.")
                else:
                    print("❌ Opción de búsqueda inválida.")
            elif opcion == "0":
                break
            else:
                print("❌ Opción inválida. Por favor, intente de nuevo.")

    def _menu_consultas_reportes(self):
        while True:
            print("\n--- Consultas y Reportes ---")
            print("1. Listar todos los libros disponibles")
            print("2. Listar todos los usuarios registrados")
            print("3. Mostrar historial de préstamos de un usuario")
            print("4. Mostrar libros actualmente prestados")
            print("5. Mostrar Estadísticas Generales")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                libros_disponibles = [libro for libro in self.libros.values() if libro.disponible]
                if libros_disponibles:
                    print("\n--- Libros Disponibles ---")
                    for i, libro in enumerate(libros_disponibles, 1):
                        print(f"{i}. {libro.titulo} ({libro.autor}) - ISBN: {libro.isbn}")
                else:
                    print("ℹ️ No hay libros disponibles en este momento.")
            elif opcion == "2":
                if self.usuarios:
                    print("\n--- Usuarios Registrados ---")
                    for i, usuario in enumerate(self.usuarios.values(), 1):
                        print(f"{i}. {usuario.nombre} - Correo: {usuario.correoU}")
                else:
                    print("ℹ️ No hay usuarios registrados.")
            elif opcion == "3":
                correo_usuario = input("Ingrese el correo del usuario para ver su historial: ").strip()
                usuario = self.usuarios.get(correo_usuario)
                if usuario:
                    if usuario.libros_prestados: # Ahora libros_prestados contiene objetos Prestamo
                        print(f"\n--- Historial de Préstamos de {usuario.nombre} ---")
                        for i, prestamo in enumerate(usuario.libros_prestados, 1):
                            fecha_dev = prestamo.fecha_devolucion.strftime("%Y-%m-%d %H:%M:%S") if prestamo.fecha_devolucion else "Pendiente"
                            print(f"{i}. Libro: {prestamo.libro.titulo} (ISBN: {prestamo.libro.isbn}), "
                                  f"Fecha Préstamo: {prestamo.fecha_prestamo.strftime('%Y-%m-%d %H:%M:%S')}, "
                                  f"Fecha Devolución: {fecha_dev}, Estado: {prestamo.estado}")
                    else:
                        print(f"ℹ️ El usuario '{usuario.nombre}' no tiene préstamos registrados.")
                else:
                    print(f"❌ Usuario con correo '{correo_usuario}' no encontrado.")
            elif opcion == "4":
                libros_prestados_actualmente = [
                    prestamo.libro for prestamo in self.prestamos.values() if prestamo.estado == "Activo"
                ]
                if libros_prestados_actualmente:
                    print("\n--- Libros Actualmente Prestados ---")
                    for i, libro in enumerate(libros_prestados_actualmente, 1):
                        print(f"{i}. {libro.titulo} (ISBN: {libro.isbn})")
                else:
                    print("ℹ️ No hay libros actualmente prestados.")
            elif opcion == "5":
                self.mostrar_estadisticas()
            elif opcion == "0":
                break
            else:
                print("❌ Opción inválida. Por favor, intente de nuevo.")

    def mostrar_estadisticas(self):
        total_libros = len(self.libros)
        libros_disponibles = sum(1 for libro in self.libros.values() if libro.disponible)
        libros_prestados = total_libros - libros_disponibles
        
        total_usuarios = len(self.usuarios)
        total_prestamos = len(self.prestamos)
        prestamos_activos = sum(1 for p in self.prestamos.values() if p.estado == "Activo")
        prestamos_devueltos = total_prestamos - prestamos_activos

        print("\n--- Estadísticas de la Biblioteca ---")
        print(f"📚 Total de libros: {total_libros}")
        print(f"  - Libros disponibles: {libros_disponibles}")
        print(f"  - Libros prestados actualmente: {libros_prestados}")
        print(f"👥 Total de usuarios registrados: {total_usuarios}")
        print(f"🔄 Total de préstamos registrados (históricos): {total_prestamos}")
        print(f"  - Préstamos activos: {prestamos_activos}")
        print(f"  - Préstamos devueltos: {prestamos_devueltos}")

    def _menu_herramientas_grafo(self):
        while True:
            print("\n--- Herramientas de Grafo ---")
            print("1. Construir Grafo de Co-préstamos de Libros")
            print("2. Construir Grafo de Similitud de Usuarios")
            print("3. Visualizar Grafo Actual")
            print("4. Obtener Recomendaciones de Libros (Basado en co-préstamos)")
            print("5. Encontrar Usuarios Similares (Basado en similitud de usuarios)")
            print("0. Volver al Menú Principal")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                # Construir grafo de co-préstamos
                self.gestor_grafo.construir_grafo_co_prestamos(self.prestamos, self.libros)
                self.grafo_actual_tipo = "co-préstamos"
                print("✅ Grafo de co-préstamos de libros construido.")
            elif opcion == "2":
                # Construir grafo de similitud de usuarios
                self.gestor_grafo.construir_grafo_similitud_usuarios(self.prestamos, self.usuarios)
                self.grafo_actual_tipo = "similitud de usuarios"
                print("✅ Grafo de similitud de usuarios construido.")
            elif opcion == "3":
                # Visualizar grafo actual
                if self.gestor_grafo.grafo.number_of_nodes() == 0:
                    print("❌ El grafo está vacío. Construya un grafo primero (opción 1 o 2).")
                else:
                    self.gestor_grafo.visualizar_grafo(self.grafo_actual_tipo)
            elif opcion == "4":
                # Obtener recomendaciones de libros
                if self.grafo_actual_tipo != "co-préstamos" or self.gestor_grafo.grafo.number_of_nodes() == 0:
                    print("❌ Debe construir primero el Grafo de Co-préstamos de Libros (opción 1) para obtener recomendaciones.")
                    continue
                correo_usuario = input("Ingrese el correo del usuario para recomendaciones: ").strip()
                if correo_usuario not in self.usuarios:
                    print(f"❌ Usuario con correo '{correo_usuario}' no encontrado.")
                    continue
                
                # Reconstruir el grafo de co-préstamos antes de obtener recomendaciones
                # para asegurar que está actualizado con todos los préstamos actuales.
                # Esto es crucial para la precisión de las recomendaciones.
                self.gestor_grafo.construir_grafo_co_prestamos(self.prestamos, self.libros) 
                
                recomendaciones = self.gestor_grafo.obtener_libros_recomendados(correo_usuario, self, top_n=5)
                if recomendaciones:
                    print(f"\n--- Recomendaciones de libros para '{self.usuarios[correo_usuario].nombre}' ---")
                    for i, rec in enumerate(recomendaciones, 1):
                        print(f"{i}. Título: {rec['titulo']}, Autor: {rec['autor']} (Score: {rec['score']})")
                else:
                    print(f"ℹ️ No se encontraron recomendaciones para '{self.usuarios[correo_usuario].nombre}' en este momento o el usuario no tiene historial de préstamos.")
            elif opcion == "5":
                # Encontrar usuarios similares
                if self.grafo_actual_tipo != "similitud de usuarios" or self.gestor_grafo.grafo.number_of_nodes() == 0:
                    print("❌ Debe construir primero el Grafo de Similitud de Usuarios (opción 2) para encontrar usuarios similares.")
                    continue
                correo_usuario = input("Ingrese el correo del usuario para encontrar similares: ").strip()
                if correo_usuario not in self.usuarios:
                    print(f"❌ Usuario con correo '{correo_usuario}' no encontrado.")
                    continue

                # Reconstruir el grafo de similitud de usuarios antes de obtener similares
                # para asegurar que está actualizado.
                self.gestor_grafo.construir_grafo_similitud_usuarios(self.prestamos, self.usuarios)

                similares = self.gestor_grafo.obtener_usuarios_similares(correo_usuario, self, top_n=5)
                if similares:
                    print(f"\n--- Usuarios similares a '{self.usuarios[correo_usuario].nombre}' ---")
                    for i, sim in enumerate(similares, 1):
                        print(f"{i}. Nombre: {sim['nombre']}, Correo: {sim['correo']} (Libros en común: {sim['libros_en_comun']})")
                else:
                    print(f"ℹ️ No se encontraron usuarios similares a '{self.usuarios[correo_usuario].nombre}' en este momento.")
            elif opcion == "0":
                break
            else:
                print("❌ Opción inválida. Por favor, intente de nuevo.")

    def mostrar_menu(self):
        """
        Muestra el menú principal y delega a los submenús.
        """
        while True:
            print("\n--- Menú Principal de la Biblioteca ---")
            print("1. Gestión de Libros")
            print("2. Gestión de Usuarios")
            print("3. Gestión de Autores y Géneros")
            print("4. Gestión de Préstamos")
            print("5. Consultas y Reportes")
            print("6. Herramientas de Grafo")
            print("0. Salir")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                self._menu_gestion_libros()
            elif opcion == "2":
                self._menu_gestion_usuarios()
            elif opcion == "3":
                self._menu_gestion_autores_generos()
            elif opcion == "4":
                self._menu_gestion_prestamos()
            elif opcion == "5":
                self._menu_consultas_reportes()
            elif opcion == "6":
                self._menu_herramientas_grafo() # Llamar al nuevo menú de grafos
            elif opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Por favor, intente de nuevo.")