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

## 5. Notas adicionales
- El sistema está diseñado para ser modular y fácilmente extensible.
- Se recomienda mantener las pruebas actualizadas y ampliarlas para cubrir casos límite.
- Si el sistema crece, considerar autenticación y control de acceso.

Ejemplo de Visualización del Grafo de Co-préstamos:
```
```
![alt text](<grafos prueba-1.jpg>)