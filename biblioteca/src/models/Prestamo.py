from datetime import datetime

class Prestamo:
    def __init__(self, usuario, libro):
        self.usuario = usuario
        self.libro = libro
        self.fecha_prestamo = datetime.now()  
        self.fecha_devolucion = None
        self.estado = "Activo"

    def __str__(self):
        fecha_dev = self.fecha_devolucion.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_devolucion else "No devuelto"
        return (f"Usuario: {self.usuario.nombre}, Libro: {self.libro.titulo}, "
                f"Fecha Préstamo: {self.fecha_prestamo.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"Fecha Devolución: {fecha_dev}, Estado: {self.estado}")