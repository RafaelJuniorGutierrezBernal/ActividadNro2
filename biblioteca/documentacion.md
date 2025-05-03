# Sistema de Gestión de Biblioteca

## 1. Comprensión y Diseño del Modelo

### 1.1 Descripción General

El sistema de gestión de biblioteca es una aplicación que permite administrar libros, usuarios y préstamos en una biblioteca. El sistema se ha diseñado para ser eficiente, escalable y fácil de usar.

### 1.2 Estructuras de Datos Utilizadas

#### Estructuras Lineales
- **Diccionarios (mapas)**: Para almacenamiento principal de libros, usuarios y préstamos, ofreciendo acceso O(1) por clave.
- **Índices secundarios**: Diccionarios adicionales para facilitar búsquedas por diferentes criterios (título, autor, nombre, teléfono).
- **Listas**: Para almacenar préstamos de un usuario y resultados de búsquedas.

#### Estructuras No Lineales (Árboles)
- **Árboles Binarios de Búsqueda AVL**: Para realizar búsquedas eficientes y ordenadas de libros y usuarios.
  - Árbol de títulos
  - Árbol de autores
  - Árbol de ISBN
  - Árbol de nombres de usuarios
  - Árbol de correos electrónicos
  - Árbol de teléfonos

### 1.3 Requerimientos Funcionales

1. **Gestión de Libros**
   - Agregar nuevos libros
   - Buscar libros por diferentes criterios (título, autor, ISBN)
   - Consultar disponibilidad de libros
   - Mostrar catálogo de libros disponibles

2. **Gestión de Usuarios**
   - Registrar nuevos usuarios
   - Buscar usuarios por diferentes criterios (nombre, correo, teléfono)
   - Consultar préstamos de un usuario

3. **Gestión de Préstamos**
   - Prestar libros a usuarios
   - Registrar devoluciones
   - Consultar historial de préstamos

4. **Sistema de Persistencia**
   - Guardar datos en archivos
   - Cargar datos desde archivos
   - Mantener la integridad de los datos entre sesiones

5. **Interfaz de Usuario**
   - Menú interactivo para todas las funcionalidades
   - Búsquedas avanzadas utilizando árboles binarios
   - Visualización de estadísticas

### 1.4 Requerimientos No Funcionales

1. **Eficiencia**
   - Búsquedas rápidas con complejidad O(log n) utilizando árboles binarios balanceados
   - Acceso directo a objetos principales mediante diccionarios (O(1))

2. **Escalabilidad**
   - Estructura que permite manejar grandes volúmenes de datos
   - Árboles autobalanceados para mantener rendimiento con crecimiento de datos

3. **Usabilidad**
   - Interfaz de usuario simple e intuitiva
   - Mensajes de error descriptivos
   - Validación de datos de entrada

4. **Persistencia**
   - Almacenamiento en archivos JSON para mantener datos entre sesiones
   - Carga y guardado eficiente de datos

5. **Mantenibilidad**
   - Código modular y bien estructurado
   - Clases con responsabilidades bien definidas
   - Documentación completa del código

## 2. Elección de Árboles Adecuados

### 2.1 Tipo de Árbol Seleccionado: Árbol Binario de Búsqueda AVL

Para este sistema, se ha seleccionado el **Árbol Binario de Búsqueda AVL** como estructura principal para las operaciones de búsqueda. Esta decisión se basa en las siguientes consideraciones:

#### Ventajas del Árbol AVL para este sistema:

1. **Búsquedas balanceadas O(log n)**: Los árboles AVL garantizan que la altura del árbol se mantenga balanceada (diferencia máxima de 1 entre las alturas de los subárboles izquierdo y derecho), lo que asegura que las búsquedas tengan una complejidad de O(log n), incluso en el peor caso.

2. **Rendimiento consistente**: A diferencia de los árboles binarios de búsqueda tradicionales que pueden degradarse a O(n) en escenarios desfavorables, los árboles AVL mantienen su rendimiento gracias al rebalanceo automático.

3. **Soporte para búsqueda por prefijo**: La estructura jerárquica del árbol permite implementar eficientemente búsquedas por prefijo, una característica valiosa para encontrar títulos, autores o nombres que comiencen con ciertos caracteres.

4. **Operaciones de inserción y eliminación eficientes**: Si bien estas operaciones son más complejas que en un árbol binario normal (debido al rebalanceo), siguen siendo O(log n), lo que es aceptable para nuestra aplicación.

#### Comparación con otras estructuras:

1. **Árboles Binarios de Búsqueda (no balanceados)**:
   - Más simples de implementar
   - Pero pueden degradarse a O(n) en escenarios con datos ordenados
   - No adecuados para nuestra aplicación donde los datos (como títulos de libros) pueden estar parcialmente ordenados

2. **Árboles Rojo-Negro**:
   - Similar rendimiento asintótico que AVL
   - Menos estricto en balanceo, lo que puede resultar en búsquedas ligeramente más lentas
   - Requiere más cambios de color y menos rotaciones que AVL

3. **Árboles B y B+**:
   - Excelentes para almacenamiento en disco y grandes volúmenes de datos
   - Mayor orden de ramificación, lo que reduce la altura del árbol
   - Más complejos de implementar
   - Sería una opción si escalamos a una base de datos

4. **HashMaps/Tablas Hash**:
   - Búsquedas O(1) para claves exactas
   - No soportan directamente búsquedas por rango o prefijo
   - No mantienen un orden natural de los elementos

### 2.2 Justificación por Caso de Uso

1. **Búsqueda de libros por título/autor**:
   - Los usuarios frecuentemente buscan libros conociendo parte del título o autor
   - El árbol AVL permite búsquedas eficientes por prefijo (ej. todos los libros que comienzan con "Harry P...")
   - Mantiene los resultados ordenados, facilitando su presentación

2. **Búsqueda de usuarios por nombre**:
   - Similar a libros, los usuarios pueden ser buscados por fragmentos de nombre
   - El balanceo AVL garantiza tiempos de respuesta consistentes independientemente del patrón de nombres

3. **Búsqueda exacta por ISBN/Correo**:
   - Aunque un HashMap sería ligeramente más eficiente para búsquedas exactas (O(1) vs O(log n))
   - El árbol AVL ofrece una solución unificada que también soporta las búsquedas por prefijo
   - La diferencia de rendimiento es mínima para la escala de datos esperada en una biblioteca

## 3. Implementación de Operaciones con Árboles

### 3.1 Estructura del Árbol AVL

Se ha implementado un árbol AVL completo con las siguientes características:

- Nodos que almacenan clave, valor y factor de balanceo (altura)
- Rotaciones izquierda y derecha para mantener el balanceo
- Factores de balanceo calculados automáticamente

La implementación incluye las siguientes clases:

```python
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
    # Métodos de inserción, búsqueda, eliminación y balanceo
    # ...
```

### 3.2 Operaciones Principales Implementadas

1. **Inserción con Balanceo**
   - Complejidad: O(log n)
   - Incluye reequilibrio mediante rotaciones

2. **Búsqueda Exacta**
   - Complejidad: O(log n)
   - Encuentra un valor asociado a una clave específica

3. **Búsqueda por Prefijo**
   - Complejidad: O(k + m) donde k es la longitud del prefijo y m el número de nodos que coinciden
   - Encuentra todos los valores cuyas claves comienzan con un prefijo dado

4. **Eliminación con Balanceo**
   - Complejidad: O(log n)
   - Mantiene el árbol equilibrado después de eliminar nodos

5. **Recorrido en Orden**
   - Complejidad: O(n)
   - Obtiene elementos ordenados por clave

### 3.3 Integración con el Sistema de Biblioteca

Los árboles se han integrado en la clase `Biblioteca` para mejorar las búsquedas:

```python
class Biblioteca:
    def __init__(self):
        # ...
        # Árboles binarios para búsquedas rápidas
        self.arbol_titulos = ArbolBinario()  # Árbol ordenado por título normalizado
        self.arbol_autores = ArbolBinario()  # Árbol ordenado por autor normalizado
        self.arbol_isbn = ArbolBinario()     # Árbol ordenado por ISBN
        self.arbol_nombres = ArbolBinario()  # Árbol ordenado por nombre normalizado
        self.arbol_correos = ArbolBinario()  # Árbol ordenado por correo
        self.arbol_telefonos = ArbolBinario() # Árbol ordenado por teléfono
        # ...
```

Cada vez que se agrega un libro o usuario, se actualiza el árbol correspondiente:

```python
def _actualizar_indices_libro(self, libro):
    # ...
    # Actualizar árboles binarios para búsqueda rápida
    self.arbol_titulos.insertar(titulo_normalizado, libro.isbn)
    self.arbol_autores.insertar(autor_normalizado, libro.isbn)
    self.arbol_isbn.insertar(libro.isbn, libro)
    # ...
```

Las búsquedas utilizan primero el árbol y, si es necesario, recurren a los índices tradicionales:

```python
def buscar_libro(self, criterio, valor):
    # ...
    if criterio == "titulo":
        # Búsqueda utilizando el árbol binario para la búsqueda por prefijo
        isbn_list = self.arbol_titulos.buscar_por_prefijo(valor_normalizado)
        # ...
```

## 4. Integración y Pruebas

### 4.1 Integración con el Sistema

La integración de los árboles binarios con el resto del sistema se ha realizado de forma modular:

1. **Capa de Modelo**: Clases `Libro`, `Usuario` y `Prestamo` con métodos para conversión a/desde diccionarios
2. **Capa de Controlador**: Clase `Biblioteca` que gestiona todas las operaciones usando tanto estructuras lineales como árboles
3. **Capa de Persistencia**: Clase `Persistencia` que se encarga de guardar/cargar datos en archivos
4. **Capa de Interface**: Menú interactivo en consola que expone todas las funcionalidades

### 4.2 Pruebas Realizadas

#### Pruebas de Funcionalidad Básica
- Agregar libros y verificar que se indexan correctamente en los árboles
- Registrar usuarios y comprobar que se pueden encontrar por diferentes criterios
- Realizar préstamos y devoluciones, verificando la actualización de estado

#### Pruebas de Búsqueda
- Búsqueda exacta por ISBN y verificación de tiempo de respuesta
- Búsqueda por prefijo de título y autor, comprobando que se retornan todos los resultados relevantes
- Comparación de rendimiento entre búsquedas en árboles vs. búsquedas lineales

#### Pruebas de Persistencia
- Guardar datos y verificar que los archivos JSON se crean correctamente
- Cargar datos y comprobar que los objetos, índices y árboles se reconstruyen adecuadamente
- Simular fallos y verificar la gestión de errores

## 5. Optimización y Eficiencia

### 5.1 Análisis de Rendimiento

El uso de árboles AVL ha mejorado significativamente el rendimiento de las búsquedas en comparación con los métodos lineales:

| Operación | Estructura Lineal | Árbol AVL | Mejora |
|-----------|------------------|-----------|--------|
| Búsqueda exacta | O(n) | O(log n) | Significativa para grandes conjuntos |
| Búsqueda por prefijo | O(n) | O(log n + k) | Mejora sustancial |
| Inserción | O(1) | O(log n) | Ligeramente más lenta, pero aceptable |
| Eliminación | O(n) | O(log n) | Mejora significativa |

Donde:
- n es el número total de elementos
- k es el número de resultados que coinciden con el prefijo

### 5.2 Optimizaciones Aplicadas

1. **Índice dual**: Mantener tanto diccionarios como árboles para diferentes tipos de búsquedas
   - Diccionarios para acceso directo por clave principal (O(1))
   - Árboles para búsquedas por prefijo y rangos (O(log n))

2. **Normalización de texto**: Previo a la indexación y búsqueda
   - Convertir a minúsculas
   - Eliminar tildes y caracteres especiales
   - Mejora la precisión de las búsquedas ignorando diferencias triviales

3. **Búsqueda con respaldo**: Si no se encuentra en el árbol, recurrir a métodos alternativos
   - Proporciona resultados incluso en casos edge-case
   - Mantiene compatibilidad con el sistema anterior

4. **Autobalanceo selectivo**: Solo reequilibrar el árbol cuando sea necesario
   - Reduce operaciones de rotación innecesarias
   - Mantiene rendimiento óptimo con menos sobrecarga

### 5.3 Compromiso de Almacenamiento vs. Rendimiento

La implementación actual duplica algunos datos (en diccionarios y árboles) para optimizar diferentes tipos de búsquedas. Este es un compromiso consciente:

- **Ventaja**: Rendimiento óptimo para diferentes patrones de acceso
- **Desventaja**: Mayor uso de memoria

Para una biblioteca típica (miles o decenas de miles de libros), el incremento en el uso de memoria es aceptable considerando la mejora en rendimiento de búsqueda.

## 6. Menú Interactivo

Se ha implementado un menú interactivo completo que permite acceder a todas las funcionalidades del sistema:

```
╔══════════════════════════╗
║ 📚  BIBLIOTECA VIRTUAL   ║
╠══════════════════════════╣
║ 1️⃣ Registrar usuario    ║
║ 2️⃣ Agregar libro        ║
║ 3️⃣ Consultar libros     ║
║ 4️⃣ Prestar libro        ║
║ 5️⃣ Devolver libro       ║
║ 6️⃣ Mostrar usuarios     ║
║ 7️⃣ Buscar               ║
║ 8️⃣ Estadísticas         ║
║ 9️⃣ Guardar datos        ║
║ 0️⃣ Salir                ║
╚══════════════════════════╝
```

### 6.1 Opciones de Búsqueda

El menú incluye opciones específicas para realizar búsquedas utilizando los árboles binarios:

```
🔍 Opciones de búsqueda:
1. Buscar usuario
2. Buscar libro
3. Búsqueda por prefijo (usando árboles)
```

La opción "Búsqueda por prefijo" permite aprovechar directamente la eficiencia de los árboles AVL para encontrar elementos cuyas claves comienzan con un prefijo dado:

```
🌳 Búsqueda por prefijo (usando árboles binarios):
1. Títulos de libros que comienzan con...
2. Autores que comienzan con...
3. Nombres de usuarios que comienzan con...
```

## 7. Sistema de Persistencia

### 7.1 Almacenamiento en Archivos JSON

Se ha implementado un sistema completo de persistencia que permite guardar y cargar todos los datos de la biblioteca en archivos JSON:

- **libros.json**: Almacena información de todos los libros
- **usuarios.json**: Almacena información de todos los usuarios
- **prestamos.json**: Almacena información de todos los préstamos
- **contadores.json**: Almacena contadores globales (como IDs)

### 7.2 Clases de Serialización

Cada clase del modelo (`Libro`, `Usuario`, `Prestamo`) implementa métodos para convertirse a/desde diccionarios:

```python
# En la clase Libro
def to_dict(self):
    return {
        "titulo": self.titulo,
        "autor": self.autor,
        "isbn": self.isbn,
        "disponible": self.disponible,
        # ...
    }

@classmethod
def from_dict(cls, datos):
    # Crea un objeto Libro a partir de un diccionario
    # ...
```

### 7.3 Gestión de Persistencia

La clase `Persistencia` se encarga de todas las operaciones de guardado/carga:

```python
class Persistencia:
    def __init__(self, directorio_datos="datos"):
        # Inicializar rutas de archivos
        # ...
    
    def guardar_biblioteca(self, biblioteca):
        # Guardar todos los datos en archivos JSON
        # ...
    
    def cargar_biblioteca(self, biblioteca):
        # Cargar datos desde archivos JSON
        # Reconstruir índices y árboles
        # ...
```

### 7.4 Reconstrucción de Estructuras

Al cargar datos, se reconstruyen tanto los índices como los árboles:

```python
def _reconstruir_indices(self, biblioteca):
    # Limpiar índices y árboles existentes
    # ...
    
    # Reconstruir índices y árboles para libros
    for libro in biblioteca.libros.values():
        biblioteca._actualizar_indices_libro(libro)
    
    # Reconstruir índices y árboles para usuarios
    # ...
```

## 8. Conclusiones

### 8.1 Logros del Proyecto

- Implementación exitosa de árboles binarios de búsqueda AVL para mejorar la eficiencia de las búsquedas
- Integración completa con el sistema de gestión de biblioteca existente
- Desarrollo de un sistema de persistencia robusto para mantener los datos entre sesiones
- Creación de una interfaz de usuario mejorada con nuevas opciones de búsqueda

### 8.2 Beneficios de Usar Árboles

- Búsquedas significativamente más rápidas, especialmente para conjuntos grandes de datos
- Soporte para búsquedas por prefijo, mejorando la experiencia del usuario
- Mantenimiento de un rendimiento consistente independientemente del crecimiento de datos

### 8.3 Posibles Mejoras Futuras

- Implementar más tipos de búsquedas avanzadas (por ejemplo, búsqueda por rango de fechas en préstamos)
- Desarrollar una interfaz gráfica para mejorar la usabilidad
- Optimizar el uso de memoria mediante estructuras de datos más compactas
- Implementar estrategias de caché para búsquedas frecuentes

## 9. Referencias Bibliográficas

1. Fritelli, V., Guzman, A., & Tymoschuk, J. (2020). *Algoritmos y estructuras de datos* (2a. ed.). Jorge Sarmiento Editor - Universitas.

2. Joyanes Aguilar, L. (2020). *Fundamentos de programación: algoritmos, estructura de datos y objetos*. McGraw-Hill.

3. Ruiz Rodríguez, R. (2009). *Fundamentos de la programación orientada a objetos: una aplicación a las estructuras de datos en Java*. El Cid Editor.

4. Zohonero Martínez, I., & Joyanes Aguilar, L. (2008). *Estructuras de datos en Java*. McGraw-Hill. 