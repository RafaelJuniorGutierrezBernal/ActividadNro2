# Documentación del Sistema de Grafos en la Biblioteca

## 1. Introducción
Este documento describe la implementación y uso del sistema de grafos en el Sistema de Gestión de Biblioteca. Los grafos se utilizan para modelar y optimizar las relaciones entre libros, usuarios, autores y géneros.

## 2. Estructura del Grafo

### 2.1 Nodos
- **Libros**: Representados por su ISBN
  - Atributos: título, autor, peso
- **Usuarios**: Representados por su correo
  - Atributos: nombre, tipo de usuario
- **Autores**: Representados por su ID
  - Atributos: nombre, nacionalidad
- **Géneros**: Representados por su ID
  - Atributos: nombre, descripción

### 2.2 Aristas
- **PRESTAMO**: Usuario → Libro
  - Peso: frecuencia de préstamo
- **ESCRITO_POR**: Libro → Autor
  - Peso: relevancia del autor
- **PERTENECE_A_GENERO**: Libro → Género
  - Peso: relevancia del género

## 3. Funcionalidades Principales

### 3.1 Gestión de Nodos
```python
# Agregar un libro
gestor.agregar_libro("1234567890", "Don Quijote", "Cervantes")

# Agregar un usuario
gestor.agregar_usuario("usuario@email.com", "Juan Pérez")

# Agregar un autor
gestor.agregar_autor("A001", "Miguel de Cervantes")

# Agregar un género
gestor.agregar_genero("G001", "Novela")
```

### 3.2 Gestión de Relaciones
```python
# Vincular libro con usuario
gestor.vincular_libro_con_usuario("1234567890", "usuario@email.com", "PRESTAMO")

# Buscar camino entre nodos
camino = gestor.buscar_camino_entre_nodos("usuario_1", "libro_1")
```

### 3.3 Recomendaciones
```python
# Obtener recomendaciones para un usuario
recomendaciones = gestor.obtener_recomendaciones("usuario@email.com")
```

## 4. Visualización

### 4.1 Gráfico del Grafo
```python
# Visualizar el grafo
gestor.visualizar_grafo("Grafo de la Biblioteca")
```

### 4.2 Análisis de Eficiencia
```python
# Obtener métricas de eficiencia
metricas = gestor.analizar_eficiencia()
```

## 5. Persistencia de Datos

### 5.1 Guardar Estado
```python
# Guardar el estado actual
gestor.guardar_estado()
```

### 5.2 Cargar Estado
```python
# Cargar el último estado guardado
gestor.cargar_estado()
```

## 6. Ejemplos de Uso

### 6.1 Búsqueda de Libros por Autor
```python
# Encontrar todos los libros de un autor
autor_id = "A001"
libros = gestor.obtener_libros_por_autor(autor_id)
```

### 6.2 Análisis de Popularidad
```python
# Analizar la popularidad de los libros
metricas = gestor.analizar_eficiencia()
print(f"Densidad del grafo: {metricas['densidad']}")
print(f"Grado promedio: {metricas['grado_promedio']}")
```

## 7. Consideraciones de Rendimiento

### 7.1 Optimizaciones
- Uso de índices en la base de datos
- Algoritmos eficientes para búsqueda de caminos
- Cálculo de similitud optimizado

### 7.2 Limitaciones
- Tamaño máximo recomendado: 10,000 nodos
- Profundidad máxima de búsqueda: 3 niveles
- Máximo de recomendaciones por usuario: 5

## 8. Mantenimiento

### 8.1 Logs
Los logs se guardan en `grafo_biblioteca.log` y contienen:
- Operaciones realizadas
- Errores encontrados
- Advertencias importantes

### 8.2 Base de Datos
La base de datos se guarda en `biblioteca.db` y contiene:
- Estado actual del grafo
- Historial de actualizaciones
- Métricas de rendimiento 