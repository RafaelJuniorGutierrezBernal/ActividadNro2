class Libro:
    def __init__(self, titulo, autor, isbn, disponible=True):
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.disponible = disponible

    def __str__(self):
        return f"Título: {self.titulo}, Autor: {self.autor}, ISBN: {self.isbn}, Disponible: {'Sí' if self.disponible else 'No'}"

    def disponibilidad(self):
        return self.disponible
    
    def to_dict(self):
        return {
            "titulo": self.titulo,
            "autor": self.autor,
            "isbn": self.isbn,
            "disponible": self.disponible
        }
