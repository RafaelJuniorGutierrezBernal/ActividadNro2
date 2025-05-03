class NodoArbol:
    """Nodo para el árbol binario de búsqueda."""
    def __init__(self, clave, valor=None):
        self.clave = clave      # Clave para ordenar y buscar
        self.valor = valor      # Valor almacenado (puede ser un objeto o una lista)
        self.izquierda = None   # Hijo izquierdo
        self.derecha = None     # Hijo derecho
        self.altura = 1         # Altura del nodo (para balanceo AVL)

class ArbolBinario:
    """Implementación de un árbol binario de búsqueda autobalanceado (AVL)."""
    
    def __init__(self):
        self.raiz = None
        self.cantidad = 0
    
    def insertar(self, clave, valor=None):
        """Inserta un nuevo nodo con la clave y valor dados."""
        if not clave:
            raise ValueError("La clave no puede ser nula o vacía")
            
        self.raiz = self._insertar_recursivo(self.raiz, clave, valor)
        self.cantidad += 1
        return True
    
    def _insertar_recursivo(self, nodo, clave, valor):
        # Si llegamos a un nodo vacío, creamos uno nuevo
        if nodo is None:
            return NodoArbol(clave, valor)
            
        # Si la clave es menor, insertamos en el subárbol izquierdo
        if clave < nodo.clave:
            nodo.izquierda = self._insertar_recursivo(nodo.izquierda, clave, valor)
        # Si la clave es mayor, insertamos en el subárbol derecho
        elif clave > nodo.clave:
            nodo.derecha = self._insertar_recursivo(nodo.derecha, clave, valor)
        # Si la clave existe, actualizamos el valor
        else:
            nodo.valor = valor
            return nodo
        
        # Actualizar la altura del nodo actual
        nodo.altura = 1 + max(self._obtener_altura(nodo.izquierda), 
                             self._obtener_altura(nodo.derecha))
        
        # Obtener el factor de balance
        balance = self._obtener_balance(nodo)
        
        # Casos de desbalance
        
        # Izquierda-Izquierda
        if balance > 1 and clave < nodo.izquierda.clave:
            return self._rotar_derecha(nodo)
            
        # Derecha-Derecha
        if balance < -1 and clave > nodo.derecha.clave:
            return self._rotar_izquierda(nodo)
            
        # Izquierda-Derecha
        if balance > 1 and clave > nodo.izquierda.clave:
            nodo.izquierda = self._rotar_izquierda(nodo.izquierda)
            return self._rotar_derecha(nodo)
            
        # Derecha-Izquierda
        if balance < -1 and clave < nodo.derecha.clave:
            nodo.derecha = self._rotar_derecha(nodo.derecha)
            return self._rotar_izquierda(nodo)
            
        return nodo
    
    def buscar(self, clave):
        """Busca un valor por su clave en el árbol."""
        return self._buscar_recursivo(self.raiz, clave)
    
    def _buscar_recursivo(self, nodo, clave):
        # Si el nodo es nulo o encontramos la clave
        if nodo is None:
            return None
        if nodo.clave == clave:
            return nodo.valor
            
        # Si la clave es menor, buscamos en el subárbol izquierdo
        if clave < nodo.clave:
            return self._buscar_recursivo(nodo.izquierda, clave)
        # Si la clave es mayor, buscamos en el subárbol derecho
        return self._buscar_recursivo(nodo.derecha, clave)
    
    def buscar_por_prefijo(self, prefijo):
        """Busca todos los valores cuyas claves comienzan con el prefijo dado."""
        if not prefijo:
            return []
            
        resultados = []
        self._buscar_prefijo_recursivo(self.raiz, prefijo, resultados)
        return resultados
    
    def _buscar_prefijo_recursivo(self, nodo, prefijo, resultados):
        if nodo is None:
            return
            
        # Verificar si la clave del nodo comienza con el prefijo
        if str(nodo.clave).startswith(prefijo):
            resultados.append(nodo.valor)
            
        # Si el prefijo es menor que la clave, buscar en el subárbol izquierdo
        if prefijo < nodo.clave:
            self._buscar_prefijo_recursivo(nodo.izquierda, prefijo, resultados)
            
        # También buscar en el subárbol derecho si puede contener claves con el prefijo
        if prefijo <= nodo.clave:
            self._buscar_prefijo_recursivo(nodo.derecha, prefijo, resultados)
    
    def eliminar(self, clave):
        """Elimina un nodo con la clave dada."""
        if self.raiz is None:
            return False
            
        resultado = [False]  # Usar lista para pasar por referencia
        self.raiz = self._eliminar_recursivo(self.raiz, clave, resultado)
        
        if resultado[0]:
            self.cantidad -= 1
            
        return resultado[0]
    
    def _eliminar_recursivo(self, nodo, clave, resultado):
        if nodo is None:
            return None
            
        # Buscar el nodo a eliminar
        if clave < nodo.clave:
            nodo.izquierda = self._eliminar_recursivo(nodo.izquierda, clave, resultado)
        elif clave > nodo.clave:
            nodo.derecha = self._eliminar_recursivo(nodo.derecha, clave, resultado)
        else:
            # Nodo encontrado, realizar la eliminación
            resultado[0] = True
            
            # Caso 1: Nodo sin hijos o con un solo hijo
            if nodo.izquierda is None:
                return nodo.derecha
            elif nodo.derecha is None:
                return nodo.izquierda
                
            # Caso 2: Nodo con dos hijos
            # Encontrar el sucesor (nodo más pequeño en el subárbol derecho)
            sucesor = self._encontrar_minimo(nodo.derecha)
            nodo.clave = sucesor.clave
            nodo.valor = sucesor.valor
            
            # Eliminar el sucesor
            nodo.derecha = self._eliminar_recursivo(nodo.derecha, sucesor.clave, [True])
        
        # Si el árbol solo tenía un nodo, retornar
        if nodo is None:
            return nodo
            
        # Actualizar altura
        nodo.altura = 1 + max(self._obtener_altura(nodo.izquierda),
                              self._obtener_altura(nodo.derecha))
                              
        # Verificar balance
        balance = self._obtener_balance(nodo)
        
        # Casos de desbalance
        
        # Izquierda-Izquierda
        if balance > 1 and self._obtener_balance(nodo.izquierda) >= 0:
            return self._rotar_derecha(nodo)
            
        # Izquierda-Derecha
        if balance > 1 and self._obtener_balance(nodo.izquierda) < 0:
            nodo.izquierda = self._rotar_izquierda(nodo.izquierda)
            return self._rotar_derecha(nodo)
            
        # Derecha-Derecha
        if balance < -1 and self._obtener_balance(nodo.derecha) <= 0:
            return self._rotar_izquierda(nodo)
            
        # Derecha-Izquierda
        if balance < -1 and self._obtener_balance(nodo.derecha) > 0:
            nodo.derecha = self._rotar_derecha(nodo.derecha)
            return self._rotar_izquierda(nodo)
            
        return nodo
    
    def _encontrar_minimo(self, nodo):
        """Encuentra el nodo con el valor mínimo en el subárbol."""
        actual = nodo
        while actual.izquierda is not None:
            actual = actual.izquierda
        return actual
    
    def inorden(self):
        """Devuelve una lista con todos los valores en orden ascendente de clave."""
        resultado = []
        self._inorden_recursivo(self.raiz, resultado)
        return resultado
    
    def _inorden_recursivo(self, nodo, resultado):
        if nodo is not None:
            self._inorden_recursivo(nodo.izquierda, resultado)
            resultado.append((nodo.clave, nodo.valor))
            self._inorden_recursivo(nodo.derecha, resultado)
    
    def _obtener_altura(self, nodo):
        """Obtiene la altura de un nodo."""
        if nodo is None:
            return 0
        return nodo.altura
    
    def _obtener_balance(self, nodo):
        """Calcula el factor de balance de un nodo."""
        if nodo is None:
            return 0
        return self._obtener_altura(nodo.izquierda) - self._obtener_altura(nodo.derecha)
    
    def _rotar_izquierda(self, z):
        """Rotación simple a la izquierda."""
        y = z.derecha
        T2 = y.izquierda
        
        # Realizar rotación
        y.izquierda = z
        z.derecha = T2
        
        # Actualizar alturas
        z.altura = 1 + max(self._obtener_altura(z.izquierda),
                          self._obtener_altura(z.derecha))
        y.altura = 1 + max(self._obtener_altura(y.izquierda),
                          self._obtener_altura(y.derecha))
                          
        return y
    
    def _rotar_derecha(self, z):
        """Rotación simple a la derecha."""
        y = z.izquierda
        T3 = y.derecha
        
        # Realizar rotación
        y.derecha = z
        z.izquierda = T3
        
        # Actualizar alturas
        z.altura = 1 + max(self._obtener_altura(z.izquierda),
                          self._obtener_altura(z.derecha))
        y.altura = 1 + max(self._obtener_altura(y.izquierda),
                          self._obtener_altura(y.derecha))
                          
        return y
        
    def __len__(self):
        """Devuelve la cantidad de elementos en el árbol."""
        return self.cantidad
        
    def esta_vacio(self):
        """Indica si el árbol está vacío."""
        return self.raiz is None 