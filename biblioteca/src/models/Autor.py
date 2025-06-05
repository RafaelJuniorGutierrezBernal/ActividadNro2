
class Autor:
    def __init__(self, id_autor, nombre):
        if not id_autor or not nombre:
            raise ValueError("ID y nombre del autor no pueden ser nulos o vacíos.")
        self.id = id_autor.strip()
        self.nombre = nombre.strip()

    def __str__(self):
        return f"Autor(ID: {self.id}, Nombre: '{self.nombre}')"

    def __eq__(self, other):
        if isinstance(other, Autor):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre}

    @classmethod
    def from_dict(cls, datos):
        return cls(datos["id"], datos["nombre"])