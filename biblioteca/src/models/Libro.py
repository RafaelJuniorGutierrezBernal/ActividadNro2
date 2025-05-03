class Libro:
    def __init__(self, titulo, autor, isbn, disponible=True):
        if titulo is None:
            raise ValueError("El título no puede ser nulo.")
        if autor is None:
            raise ValueError("El autor no puede ser nulo.")
        if isbn is None:
            raise ValueError("El ISBN no puede ser nulo.")
            
        if not titulo.strip():
            raise ValueError("El título no puede estar vacío.")
        if not autor.strip():
            raise ValueError("El autor no puede estar vacío.")
        if not isbn.strip():
            raise ValueError("El ISBN no puede estar vacío.")
            
        if len(titulo.strip()) < 2:
            raise ValueError("El título debe tener al menos 2 caracteres.")
        if len(autor.strip()) < 2:
            raise ValueError("El autor debe tener al menos 2 caracteres.")
            
        self.titulo = titulo.strip()
        self.autor = autor.strip()
        self.isbn = isbn.strip()
        self.disponible = disponible
        self.titulo_normalizado = None  
        self.autor_normalizado = None   

    def __str__(self):
        estado = "Sí" if self.disponible else "No"
        return f"Título: {self.titulo}, Autor: {self.autor}, ISBN: {self.isbn}, Disponible: {estado}"

    def __eq__(self, otro):
        """Sobrecarga del operador de igualdad para comparar por ISBN."""
        if isinstance(otro, Libro):
            return self.isbn == otro.isbn
        return False
        
    def __hash__(self):
        """Necesario para usar el libro en conjuntos o como clave en diccionarios."""
        return hash(self.isbn)

    def disponibilidad(self):
        return self.disponible
    
    def to_dict(self):
        return {
            "titulo": self.titulo,
            "autor": self.autor,
            "isbn": self.isbn,
            "disponible": self.disponible,
            "titulo_normalizado": self.titulo_normalizado,
            "autor_normalizado": self.autor_normalizado
        }
        
    @classmethod
    def from_dict(cls, datos):
        """Crear un objeto Libro a partir de un diccionario."""
        if not datos:
            raise ValueError("No se puede crear un libro desde datos nulos o vacíos.")
            
        # Verificar campos obligatorios
        if "titulo" not in datos:
            raise ValueError("Falta el campo 'titulo' en los datos del libro.")
        if "autor" not in datos:
            raise ValueError("Falta el campo 'autor' en los datos del libro.")
        if "isbn" not in datos:
            raise ValueError("Falta el campo 'isbn' en los datos del libro.")
            
        try:
            libro = cls(
                titulo=datos["titulo"],
                autor=datos["autor"],
                isbn=datos["isbn"],
                disponible=datos.get("disponible", True)
            )
            libro.titulo_normalizado = datos.get("titulo_normalizado")
            libro.autor_normalizado = datos.get("autor_normalizado")
            
            return libro
        except ValueError as e:
            print(f"Error al crear libro desde diccionario: {e}")
            raise
