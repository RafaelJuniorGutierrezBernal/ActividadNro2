# Sistema de Gestión de Biblioteca

## 1. Guía de Instalación y Ejecución

### 1.1 Requisitos del Sistema
- Python 3.6 o superior
- Dependencias: `networkx`, `matplotlib`, `pandas`, `numpy`
- Instalación: `pip install networkx matplotlib pandas numpy`

### 1.2 Instrucciones de Instalación
1. Descomprimir el archivo en cualquier ubicación.
2. Verificar la estructura de directorios:
   ```
   biblioteca/
   ├── src/
   │   ├── controllers/
   │   │   └── Biblioteca.py
   │   ├── models/
   │   │   ├── ArbolBinario.py
   │   │   ├── Libro.py
   │   │   ├── Prestamo.py
   │   │   ├── Usuario.py
   │   │   ├── Autor.py
   │   │   └── Genero.py
   │   ├── gestor_grafo_mejorado.py
   │   └── main.py
   └── documentacion.md
   ```

### 1.3 Ejecución del Programa
- Navegar al directorio del proyecto: `cd ruta/a/biblioteca`
- Ejecutar: `python src/main.py`

## 2. Estructura del Proyecto

### 2.1 Módulos Principales
- **controllers/Biblioteca.py**: Controlador principal que gestiona libros, usuarios, préstamos, autores y géneros.
- **models/**: Contiene las clases de datos (Libro, Usuario, Prestamo, Autor, Genero) y el árbol binario para búsquedas rápidas.
- **gestor_grafo_mejorado.py**: Implementa un grafo dirigido y ponderado para modelar relaciones entre libros, usuarios, autores y géneros.
- **main.py**: Punto de entrada del sistema.

### 2.2 Funcionalidades
- **Gestión de Libros**: Agregar, modificar, eliminar y buscar libros.
- **Gestión de Usuarios**: Registrar, modificar, eliminar y buscar usuarios.
- **Gestión de Préstamos**: Realizar préstamos, registrar devoluciones y listar préstamos activos o devueltos.
- **Gestión de Autores y Géneros**: Registrar autores y géneros, y asignarlos a libros.
- **Grafo y Recomendaciones**: Modelar relaciones entre libros y usuarios, y generar recomendaciones.

## 3. Pruebas

### 3.1 Pruebas Unitarias
- **test_libros_db.py**: Prueba el guardado y carga de libros en la base de datos.
- **test_gestor_grafo.py**: Prueba la funcionalidad del grafo (agregar nodos, vincular, buscar caminos, etc.).
- **test_db.py**: Prueba la creación y estructura de la base de datos.

### 3.2 Ejecución de Pruebas
- Ejecutar todas las pruebas: `python -m unittest discover biblioteca/src/tests`
- Ejecutar pruebas específicas: `python -m unittest biblioteca/src/tests/test_libros_db.py`

## 4. Recomendaciones y Mejoras

### 4.1 Arquitectura
- **Separación de responsabilidades**: Los controladores no acceden directamente a la base de datos, sino a través de servicios o gestores.
- **Documentación**: Cada clase y método público debe estar documentado.

### 4.2 Gestión de errores
- **Validaciones**: Validar entradas del usuario y manejar errores inesperados.
- **Logs**: Centralizar logs y configurar niveles de detalle.

### 4.3 Interfaz de usuario
- **Menús y mensajes**: Claros y amigables. Considerar una interfaz gráfica o web en el futuro.

### 4.4 Grafo y recomendaciones
- **Persistencia**: Optimizar la serialización/deserialización del grafo.
- **Algoritmos**: Mejorar el sistema de recomendaciones con algoritmos avanzados.

### 4.5 Código y estilo
- **PEP8**: Seguir el estándar PEP8 para nombres de variables, indentación, etc.
- **Imports**: Usar imports absolutos para evitar problemas en producción.

### 4.6 Dependencias y entorno
- **requirements.txt**: Incluir todas las dependencias necesarias.
- **README**: Explicar instalación, ejecución y pruebas.

## 5. Análisis de Requerimientos y Selección de Grafos

### 5.1 Análisis de Requerimientos
El análisis de los requerimientos del sistema bibliotecario de entregas anteriores reveló la necesidad de mejorar la eficiencia en las interacciones entre usuarios y libros. Los grafos se identificaron como una solución óptima para modelar estas relaciones debido a:

1. **Requerimientos Adicionales con Grafos**:
   - Modelado de relaciones de co-préstamos entre libros
   - Identificación de patrones de lectura entre usuarios
   - Generación de recomendaciones basadas en préstamos históricos
   - Análisis de popularidad y tendencias de lectura
   - Optimización de la ubicación física de libros en la biblioteca

2. **Beneficios de la Implementación con Grafos**:
   - Mejor visualización de relaciones complejas
   - Análisis eficiente de patrones de uso
   - Capacidad de realizar búsquedas y recomendaciones más precisas
   - Optimización del tiempo de respuesta en consultas complejas
   - Facilidad para escalar el sistema con nuevas funcionalidades

### 5.2 Selección de Tipo de Grafo

#### 5.2.1 Tipo de Grafo Seleccionado: Grafo No Dirigido Ponderado

Se optó por implementar un grafo no dirigido ponderado por las siguientes razones:

1. **Justificación de Grafo No Dirigido**:
   - Las relaciones entre libros y usuarios son bidireccionales
   - Un usuario puede prestar múltiples libros
   - Un libro puede ser prestado por múltiples usuarios
   - No existe una jerarquía natural en las relaciones
   - Facilita el análisis de comunidades y patrones

2. **Justificación de Grafo Ponderado**:
   - Los pesos representan la frecuencia de co-préstamos
   - Permite medir la intensidad de las relaciones
   - Facilita la generación de recomendaciones más precisas
   - Ayuda a identificar patrones de uso más relevantes
   - Permite priorizar relaciones más significativas

3. **Ventajas de la Implementación**:
   - Mejor representación de la realidad del sistema
   - Mayor flexibilidad en el análisis de datos
   - Capacidad de realizar análisis estadísticos
   - Facilidad para implementar algoritmos de recomendación
   - Optimización del rendimiento en consultas complejas

## 6. Conclusiones Generales

El proyecto ha logrado establecer un sistema de gestión de biblioteca funcional, capaz de manejar libros, usuarios, préstamos y devoluciones. Se ha implementado un robusto gestor de grafos para analizar relaciones entre libros y usuarios, permitiendo la generación de recomendaciones basadas en co-préstamos. La estructura modular y el enfoque en la separación de responsabilidades facilitan la mantenibilidad y la futura expansión del sistema.

Se han abordado y resuelto diversos desafíos, como la persistencia de datos, la validación de entradas, la corrección de errores en expresiones regulares y la optimización de las pruebas unitarias. La depuración de los tests, en particular, aseguró la estabilidad y fiabilidad del código, garantizando que el sistema se comporte como se espera bajo diferentes escenarios.

A pesar de las mejoras significativas, siempre hay áreas para futuras optimizaciones. Se recomienda continuar refinando los algoritmos de recomendación, explorando opciones para una interfaz de usuario más interactiva y escalando la arquitectura para manejar un mayor volumen de datos y usuarios.

Ejemplo de Visualización del Grafo de Co-préstamos:

```
```
![alt text](<grafos prueba-1.jpg>)

## Referencias bibliográficas

* Fritelli, V. Guzman, A. Tymoschuk, J. (2020). Algoritmos y estructuras de datos (2a. ed.). Jorge Sarmiento Editor - Universitas. (Págs. 355 - 359).

* Zohonero Martínez, I. Joyanes Aguilar, L. (2008). Estructuras de datos en Java.. McGraw-Hill, España. (Págs. 456 - 485).

* Flórez Rueda, R. (2005). Algoritmos con estructura de datos y programación orientada a objetos. Banco de la República, Luis Ángel Arango.

* Sánchez Juárez, J. (2013). Libro digital Estructuras de Datos. Libre Edición.