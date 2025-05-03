from datetime import datetime

class Prestamo:
    def __init__(self, usuario, libro, fecha_prestamo=None, fecha_devolucion=None):
        if usuario is None:
            raise ValueError("El usuario no puede ser nulo.")
        if libro is None:
            raise ValueError("El libro no puede ser nulo.")
            
        self.usuario = usuario
        self.libro = libro
        self.fecha_prestamo = fecha_prestamo if fecha_prestamo else datetime.now()  
        self.fecha_devolucion = fecha_devolucion
        self.estado = "Activo" if not fecha_devolucion else "Devuelto"
        self.id = None  # Se establecerá en la clase Biblioteca

    def __str__(self):
        fecha_dev = self.fecha_devolucion.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_devolucion else "No devuelto"
        return (f"Usuario: {self.usuario.nombre}, Libro: {self.libro.titulo}, "
                f"Fecha Préstamo: {self.fecha_prestamo.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"Fecha Devolución: {fecha_dev}, Estado: {self.estado}")
    
    def to_dict(self):
        """Convierte el préstamo a un diccionario para almacenamiento."""
        from models.Usuario import Usuario
        from models.Libro import Libro
        
        return {
            "usuario": self.usuario.to_dict() if isinstance(self.usuario, Usuario) else self.usuario,
            "libro": self.libro.to_dict() if isinstance(self.libro, Libro) else self.libro,
            "fecha_prestamo": self.fecha_prestamo.isoformat() if self.fecha_prestamo else None,
            "fecha_devolucion": self.fecha_devolucion.isoformat() if self.fecha_devolucion else None,
            "estado": self.estado,
            "id": self.id
        }
        
    @classmethod
    def from_dict(cls, datos):
        """Crea un objeto Prestamo desde un diccionario."""
        if not datos:
            raise ValueError("No se puede crear un préstamo desde datos nulos o vacíos.")
            
        from models.Usuario import Usuario
        from models.Libro import Libro
        
        # Verificar campos obligatorios
        if "usuario" not in datos:
            raise ValueError("Falta el campo 'usuario' en los datos del préstamo.")
        if "libro" not in datos:
            raise ValueError("Falta el campo 'libro' en los datos del préstamo.")
        
        # Reconstruir objetos relacionados
        usuario_data = datos["usuario"]
        libro_data = datos["libro"]
        
        if not usuario_data:
            raise ValueError("Los datos del usuario en el préstamo no pueden estar vacíos.")
        if not libro_data:
            raise ValueError("Los datos del libro en el préstamo no pueden estar vacíos.")
        
        try:
            usuario = Usuario.from_dict(usuario_data) if isinstance(usuario_data, dict) else usuario_data
            if usuario is None:
                raise ValueError("No se pudo reconstruir el usuario del préstamo.")
                
            libro = Libro.from_dict(libro_data) if isinstance(libro_data, dict) else libro_data
            if libro is None:
                raise ValueError("No se pudo reconstruir el libro del préstamo.")
                
            # Parsear fechas
            fecha_prestamo_str = datos.get("fecha_prestamo")
            fecha_devolucion_str = datos.get("fecha_devolucion")
            
            fecha_prestamo = None
            fecha_devolucion = None
            
            if fecha_prestamo_str:
                try:
                    fecha_prestamo = datetime.fromisoformat(fecha_prestamo_str)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Formato de fecha de préstamo inválido: {e}")
                    
            if fecha_devolucion_str:
                try:
                    fecha_devolucion = datetime.fromisoformat(fecha_devolucion_str)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Formato de fecha de devolución inválido: {e}")
            
            prestamo = cls(
                usuario=usuario,
                libro=libro,
                fecha_prestamo=fecha_prestamo,
                fecha_devolucion=fecha_devolucion
            )
            
            prestamo.estado = datos.get("estado", "Activo")
            prestamo.id = datos.get("id")
            
            return prestamo
        except Exception as e:
            print(f"Error al crear préstamo desde diccionario: {e}")
            raise