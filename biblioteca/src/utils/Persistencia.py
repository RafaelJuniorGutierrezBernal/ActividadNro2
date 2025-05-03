import json
import os
from models.Libro import Libro
from models.Usuario import Usuario
from models.Prestamo import Prestamo

class Persistencia:
    """
    Clase encargada de la persistencia de datos en archivos de texto.
    Permite guardar y cargar los datos de la biblioteca (libros, usuarios, préstamos).
    """
    
    def __init__(self, directorio_datos="datos"):
        """
        Inicializa el gestor de persistencia con el directorio donde se guardarán los datos.
        
        Args:
            directorio_datos (str): Ruta al directorio donde se guardarán los archivos de datos.
        """
        self.directorio_datos = directorio_datos
        self._crear_directorio_si_no_existe()
        
        # Rutas de archivos
        self.ruta_libros = os.path.join(self.directorio_datos, "libros.json")
        self.ruta_usuarios = os.path.join(self.directorio_datos, "usuarios.json")
        self.ruta_prestamos = os.path.join(self.directorio_datos, "prestamos.json")
        self.ruta_contadores = os.path.join(self.directorio_datos, "contadores.json")
    
    def _crear_directorio_si_no_existe(self):
        """Crea el directorio de datos si no existe."""
        if not os.path.exists(self.directorio_datos):
            os.makedirs(self.directorio_datos)
    
    def guardar_biblioteca(self, biblioteca):
        """
        Guarda todos los datos de la biblioteca en archivos.
        
        Args:
            biblioteca: Objeto Biblioteca con los datos a guardar.
        
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario.
        """
        try:
            # Guardar libros
            self._guardar_libros(biblioteca.libros)
            
            # Guardar usuarios
            self._guardar_usuarios(biblioteca.usuarios)
            
            # Guardar préstamos
            self._guardar_prestamos(biblioteca.prestamos)
            
            # Guardar contadores
            self._guardar_contadores({'id_prestamo': biblioteca.id_prestamo})
            
            return True
        except Exception as e:
            print(f"Error al guardar datos: {e}")
            return False
    
    def cargar_biblioteca(self, biblioteca):
        """
        Carga todos los datos de la biblioteca desde archivos.
        
        Args:
            biblioteca: Objeto Biblioteca donde se cargarán los datos.
        
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario.
        """
        try:
            # Verificar si existen los archivos
            if not self._existen_archivos():
                print("No hay datos guardados previamente.")
                return False
            
            # Cargar libros
            libros = self._cargar_libros()
            biblioteca.libros = libros
            
            # Cargar usuarios
            usuarios = self._cargar_usuarios()
            biblioteca.usuarios = usuarios
            
            # Cargar préstamos
            prestamos = self._cargar_prestamos()
            biblioteca.prestamos = prestamos
            
            # Cargar contadores
            contadores = self._cargar_contadores()
            if contadores and 'id_prestamo' in contadores:
                biblioteca.id_prestamo = contadores['id_prestamo']
            
            # Reconstruir índices y árboles
            self._reconstruir_indices(biblioteca)
            
            return True
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            return False
    
    def _guardar_libros(self, libros):
        """Guarda los libros en un archivo JSON."""
        libros_dict = {isbn: libro.to_dict() for isbn, libro in libros.items()}
        with open(self.ruta_libros, 'w', encoding='utf-8') as archivo:
            json.dump(libros_dict, archivo, ensure_ascii=False, indent=2)
    
    def _guardar_usuarios(self, usuarios):
        """Guarda los usuarios en un archivo JSON."""
        usuarios_dict = {correo: usuario.to_dict() for correo, usuario in usuarios.items()}
        with open(self.ruta_usuarios, 'w', encoding='utf-8') as archivo:
            json.dump(usuarios_dict, archivo, ensure_ascii=False, indent=2)
    
    def _guardar_prestamos(self, prestamos):
        """Guarda los préstamos en un archivo JSON."""
        prestamos_dict = {id_prestamo: prestamo.to_dict() for id_prestamo, prestamo in prestamos.items()}
        with open(self.ruta_prestamos, 'w', encoding='utf-8') as archivo:
            json.dump(prestamos_dict, archivo, ensure_ascii=False, indent=2)
    
    def _guardar_contadores(self, contadores):
        """Guarda los contadores en un archivo JSON."""
        with open(self.ruta_contadores, 'w', encoding='utf-8') as archivo:
            json.dump(contadores, archivo, ensure_ascii=False, indent=2)
    
    def _cargar_libros(self):
        """Carga los libros desde un archivo JSON."""
        if not os.path.exists(self.ruta_libros):
            return {}
        
        with open(self.ruta_libros, 'r', encoding='utf-8') as archivo:
            libros_dict = json.load(archivo)
        
        # Convertir diccionarios a objetos Libro
        libros = {}
        for isbn, libro_dict in libros_dict.items():
            try:
                libros[isbn] = Libro.from_dict(libro_dict)
            except Exception as e:
                print(f"Error al cargar libro {isbn}: {e}")
        
        return libros
    
    def _cargar_usuarios(self):
        """Carga los usuarios desde un archivo JSON."""
        if not os.path.exists(self.ruta_usuarios):
            return {}
        
        with open(self.ruta_usuarios, 'r', encoding='utf-8') as archivo:
            usuarios_dict = json.load(archivo)
        
        # Convertir diccionarios a objetos Usuario
        usuarios = {}
        for correo, usuario_dict in usuarios_dict.items():
            try:
                usuarios[correo] = Usuario.from_dict(usuario_dict)
            except Exception as e:
                print(f"Error al cargar usuario {correo}: {e}")
        
        return usuarios
    
    def _cargar_prestamos(self):
        """Carga los préstamos desde un archivo JSON."""
        if not os.path.exists(self.ruta_prestamos):
            return {}
        
        with open(self.ruta_prestamos, 'r', encoding='utf-8') as archivo:
            prestamos_dict = json.load(archivo)
        
        # Convertir diccionarios a objetos Prestamo
        prestamos = {}
        for id_prestamo, prestamo_dict in prestamos_dict.items():
            try:
                prestamos[id_prestamo] = Prestamo.from_dict(prestamo_dict)
            except Exception as e:
                print(f"Error al cargar préstamo {id_prestamo}: {e}")
        
        return prestamos
    
    def _cargar_contadores(self):
        """Carga los contadores desde un archivo JSON."""
        if not os.path.exists(self.ruta_contadores):
            return {}
        
        with open(self.ruta_contadores, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    
    def _existen_archivos(self):
        """Verifica si existen los archivos de datos."""
        return (os.path.exists(self.ruta_libros) or
                os.path.exists(self.ruta_usuarios) or
                os.path.exists(self.ruta_prestamos))
    
    def _reconstruir_indices(self, biblioteca):
        """Reconstruye los índices secundarios y árboles de la biblioteca."""
        # Limpiar índices y árboles
        biblioteca.libros_por_titulo = {}
        biblioteca.libros_por_autor = {}
        biblioteca.usuarios_por_nombre = {}
        biblioteca.usuarios_por_telefono = {}
        
        biblioteca.arbol_titulos = biblioteca.arbol_titulos.__class__()
        biblioteca.arbol_autores = biblioteca.arbol_autores.__class__()
        biblioteca.arbol_isbn = biblioteca.arbol_isbn.__class__()
        biblioteca.arbol_nombres = biblioteca.arbol_nombres.__class__()
        biblioteca.arbol_correos = biblioteca.arbol_correos.__class__()
        biblioteca.arbol_telefonos = biblioteca.arbol_telefonos.__class__()
        
        # Reconstruir índices y árboles para libros
        for libro in biblioteca.libros.values():
            biblioteca._actualizar_indices_libro(libro)
        
        # Reconstruir índices y árboles para usuarios
        for usuario in biblioteca.usuarios.values():
            biblioteca._actualizar_indices_usuario(usuario)
            
        print("Índices y árboles reconstruidos correctamente.")
        
    def eliminar_todos_datos(self):
        """Elimina todos los archivos de datos."""
        try:
            if os.path.exists(self.ruta_libros):
                os.remove(self.ruta_libros)
            if os.path.exists(self.ruta_usuarios):
                os.remove(self.ruta_usuarios)
            if os.path.exists(self.ruta_prestamos):
                os.remove(self.ruta_prestamos)
            if os.path.exists(self.ruta_contadores):
                os.remove(self.ruta_contadores)
            return True
        except Exception as e:
            print(f"Error al eliminar datos: {e}")
            return False 