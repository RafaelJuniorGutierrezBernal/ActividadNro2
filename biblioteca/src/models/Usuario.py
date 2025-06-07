import re

class Usuario:
    def __init__(self, nombre, numeroTelefono, correoU, libros_prestados=None):
        if nombre is None:
            raise ValueError("El nombre no puede ser nulo.")
        if numeroTelefono is None:
            raise ValueError("El número de teléfono no puede ser nulo.")
        if correoU is None:
            raise ValueError("El correo electrónico no puede ser nulo.")
            
        self.nombre = self.validar_nombre(nombre)
        self.numeroTelefono = self.validar_numero(numeroTelefono)
        self.correoU = self.validar_correo(correoU)
        self.libros_prestados = libros_prestados if libros_prestados is not None else []
        self.nombre_normalizado = None  # Se establecerá en la clase Biblioteca

    def __str__(self):
        return (f"Nombre: {self.nombre}, Correo: {self.correoU}, Teléfono: {self.numeroTelefono}, "
                f"Libros prestados: {len(self.libros_prestados)}")

    def __eq__(self, otro):
        """Sobrecarga del operador de igualdad para comparar por correo."""
        if isinstance(otro, Usuario):
            return self.correoU.lower() == otro.correoU.lower()
        return False

    def __hash__(self):
        """Necesario para usar el usuario en conjuntos o como clave en diccionarios."""
        return hash(self.correoU.lower())

    @staticmethod
    def validar_nombre(nombre):
        if not nombre or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        # Permitir letras latinas con tildes, diéresis, ñ y espacios (compatible con Python)
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$", nombre):
            raise ValueError("El nombre debe contener solo letras y espacios (incluyendo tildes y ñ).")
        return nombre.strip()

    @staticmethod
    def validar_numero(numeroTelefono):
        if not numeroTelefono or not numeroTelefono.strip():
            raise ValueError("El número de teléfono no puede estar vacío.")
        numeroLimpio = numeroTelefono.replace(" ", "").replace("-", "")
        if not numeroLimpio.isdigit():
            raise ValueError("El número de teléfono debe contener solo dígitos (se permiten espacios y guiones).")
        if not (7 <= len(numeroLimpio) <= 15):
            raise ValueError(f"El número de teléfono debe tener entre 7 y 15 dígitos. Actualmente tiene {len(numeroLimpio)}.")
        return numeroTelefono

    @staticmethod
    def validar_correo(correoU):
        if not correoU or not correoU.strip():
            raise ValueError("El correo electrónico no puede estar vacío.")
        patron_correo = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron_correo, correoU):
            raise ValueError("El formato del correo electrónico no es válido. Debe tener un formato como 'usuario@dominio.com'.")
        return correoU.strip()

    def to_dict(self):
        from models.Libro import Libro  # Importación local para evitar dependencias circulares
        
        return {
            "nombre": self.nombre,
            "numeroTelefono": self.numeroTelefono,
            "correoU": self.correoU,
            "libros_prestados": [libro.to_dict() if isinstance(libro, Libro) else libro for libro in self.libros_prestados],
            "nombre_normalizado": self.nombre_normalizado
        }
        
    @classmethod
    def from_dict(cls, datos):
        """Crear un objeto Usuario a partir de un diccionario."""
        if not datos:
            raise ValueError("No se pueden crear un usuario desde datos nulos o vacíos.")
            
        from models.Libro import Libro  # Importación local para evitar dependencias circulares
        
        # Verificar campos obligatorios
        if "nombre" not in datos:
            raise ValueError("Falta el campo 'nombre' en los datos del usuario.")
        if "numeroTelefono" not in datos:
            raise ValueError("Falta el campo 'numeroTelefono' en los datos del usuario.")
        if "correoU" not in datos:
            raise ValueError("Falta el campo 'correoU' en los datos del usuario.")
        
        # Reconstruir libros prestados
        libros_prestados = []
        for libro_dict in datos.get("libros_prestados", []):
            if isinstance(libro_dict, dict):
                try:
                    libro = Libro.from_dict(libro_dict)
                    if libro:
                        libros_prestados.append(libro)
                except Exception as e:
                    print(f"Error al reconstruir libro prestado: {e}")
            elif isinstance(libro_dict, Libro):
                libros_prestados.append(libro_dict)
                
        try:
            usuario = cls(
                nombre=datos["nombre"],
                numeroTelefono=datos["numeroTelefono"],
                correoU=datos["correoU"],
                libros_prestados=libros_prestados
            )
            usuario.nombre_normalizado = datos.get("nombre_normalizado")
            return usuario
        except ValueError as e:
            print(f"Error al crear usuario desde diccionario: {e}")
            raise