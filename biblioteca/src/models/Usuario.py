import re

class Usuario:
    def __init__(self, nombre, numeroTelefono, correoU, libros_prestados=None):
        self.nombre = self.validar_nombre(nombre)
        self.numeroTelefono = self.validar_numero(numeroTelefono)
        self.correoU = self.validar_correo(correoU)
        self.libros_prestados = libros_prestados if libros_prestados is not None else []

    def __str__(self):
        return (f"Nombre: {self.nombre}, Correo: {self.correoU}, Teléfono: {self.numeroTelefono}, "
                f"Libros prestados: {len(self.libros_prestados)}")

    @staticmethod
    def validar_nombre(nombre):
        if not nombre or not re.match(r"^[a-zA-Z\s]+$", nombre):
            raise ValueError("El nombre debe contener solo letras y espacios.")
        return nombre.strip()

    @staticmethod
    def validar_numero(numeroTelefono):
        if not numeroTelefono.isdigit() or not (7 <= len(numeroTelefono) <= 15):
            raise ValueError("El número de teléfono debe contener solo números y tener entre 7 y 15 dígitos.")
        return numeroTelefono

    @staticmethod
    def validar_correo(correoU):
        patron_correo = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron_correo, correoU):
            raise ValueError("Correo electrónico no válido.")
        return correoU.strip()

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "numeroTelefono": self.numeroTelefono,
            "correoU": self.correoU,
            "libros_prestados": [libro.to_dict() for libro in self.libros_prestados]
        }