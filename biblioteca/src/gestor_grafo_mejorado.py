import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import sqlite3
import json
from typing import List, Dict, Any, Optional
import logging

class GestorGrafoBiblioteca:
    """
    Gestor de Grafos para el Sistema de Biblioteca.
    
    Este gestor implementa un grafo dirigido y ponderado para modelar las relaciones
    entre libros, usuarios, autores y géneros. Las aristas están ponderadas según
    la frecuencia de interacción y el tiempo.
    
    Atributos:
        grafo (nx.DiGraph): Grafo dirigido que representa las relaciones
        db_path (str): Ruta a la base de datos SQLite
    """
    
    def __init__(self, db_path: str = "biblioteca.db"):
        """
        Inicializa el gestor de grafos.
        
        Args:
            db_path (str): Ruta a la base de datos SQLite
        """
        self.grafo = nx.DiGraph()
        self.db_path = db_path
        self._configurar_logging()
        self._inicializar_db()
        
    def _configurar_logging(self):
        """Configura el sistema de logging para el gestor."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='grafo_biblioteca.log'
        )
        self.logger = logging.getLogger('GestorGrafoBiblioteca')
        
    def _inicializar_db(self):
        """Inicializa la base de datos SQLite con las tablas necesarias."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS grafo_estado (
                        id INTEGER PRIMARY KEY,
                        fecha_actualizacion TEXT,
                        datos_grafo TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error al inicializar la base de datos: {e}")
            raise

    def _get_node_id(self, obj_type: str, obj_key: str) -> str:
        """
        Genera un ID de nodo consistente para el grafo.
        
        Args:
            obj_type (str): Tipo de objeto (libro, usuario, autor, genero)
            obj_key (str): Identificador único del objeto
            
        Returns:
            str: ID del nodo formateado
        """
        return f"{obj_type}_{obj_key}"
    
    def agregar_libro(self, libro_isbn: str, titulo: Optional[str] = None, 
                     autor_nombre: Optional[str] = None, peso: float = 1.0) -> bool:
        """
        Agrega un libro como nodo al grafo.
        
        Args:
            libro_isbn (str): ISBN del libro
            titulo (str, optional): Título del libro
            autor_nombre (str, optional): Nombre del autor
            peso (float): Peso inicial del nodo
            
        Returns:
            bool: True si se agregó correctamente, False en caso contrario
        """
        try:
            node_id = self._get_node_id("libro", libro_isbn)
            if not self.grafo.has_node(node_id):
                self.grafo.add_node(
                    node_id, 
                    type="libro",
                    isbn=libro_isbn,
                    titulo=titulo,
                    autor_nombre=autor_nombre,
                    peso=peso,
                    fecha_creacion=datetime.now().isoformat()
                )
                self.logger.info(f"Libro '{titulo}' (ISBN: {libro_isbn}) agregado.")
                return True
            else:
                self.grafo.nodes[node_id].update({
                    'titulo': titulo,
                    'autor_nombre': autor_nombre,
                    'peso': peso
                })
                return True
        except Exception as e:
            self.logger.error(f"Error al agregar libro: {e}")
            return False

    def vincular_libro_con_usuario(self, libro_isbn: str, usuario_correo: str, 
                                 tipo_relacion: str = "PRESTAMO", peso: float = 1.0) -> bool:
        """
        Vincula un libro con un usuario mediante una relación ponderada.
        
        Args:
            libro_isbn (str): ISBN del libro
            usuario_correo (str): Correo del usuario
            tipo_relacion (str): Tipo de relación (PRESTAMO, RESERVA, etc.)
            peso (float): Peso de la relación
            
        Returns:
            bool: True si se vinculó correctamente, False en caso contrario
        """
        try:
            libro_node = self._get_node_id("libro", libro_isbn)
            usuario_node = self._get_node_id("usuario", usuario_correo)
            
            if not self.grafo.has_node(libro_node) or not self.grafo.has_node(usuario_node):
                self.logger.warning(f"No se pudieron encontrar los nodos para vincular")
                return False
                
            self.grafo.add_edge(
                usuario_node,
                libro_node,
                relation=tipo_relacion,
                peso=peso,
                fecha_vinculacion=datetime.now().isoformat()
            )
            self.logger.info(f"Vinculado usuario '{usuario_correo}' con libro '{libro_isbn}'")
            return True
        except Exception as e:
            self.logger.error(f"Error al vincular libro con usuario: {e}")
            return False

    def buscar_camino_entre_nodos(self, nodo_origen: str, nodo_destino: str, 
                                max_profundidad: int = 3) -> List[str]:
        """
        Busca el camino más corto entre dos nodos.
        
        Args:
            nodo_origen (str): ID del nodo origen
            nodo_destino (str): ID del nodo destino
            max_profundidad (int): Profundidad máxima de búsqueda
            
        Returns:
            List[str]: Lista de nodos que forman el camino
        """
        try:
            if not self.grafo.has_node(nodo_origen) or not self.grafo.has_node(nodo_destino):
                return []
                
            camino = nx.shortest_path(
                self.grafo,
                source=nodo_origen,
                target=nodo_destino,
                weight='peso'
            )
            return camino
        except nx.NetworkXNoPath:
            self.logger.warning(f"No se encontró camino entre {nodo_origen} y {nodo_destino}")
            return []
        except Exception as e:
            self.logger.error(f"Error al buscar camino: {e}")
            return []

    def obtener_recomendaciones(self, usuario_correo: str, max_recomendaciones: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene recomendaciones de libros para un usuario basadas en sus interacciones.
        
        Args:
            usuario_correo (str): Correo del usuario
            max_recomendaciones (int): Número máximo de recomendaciones
            
        Returns:
            List[Dict[str, Any]]: Lista de recomendaciones con información detallada
        """
        try:
            usuario_node = self._get_node_id("usuario", usuario_correo)
            if not self.grafo.has_node(usuario_node):
                return []
                
            # Obtener libros que el usuario ha interactuado
            libros_interactuados = set()
            for _, libro_node in self.grafo.edges(usuario_node):
                if self.grafo.nodes[libro_node]['type'] == 'libro':
                    libros_interactuados.add(libro_node)
                    
            # Encontrar usuarios similares
            usuarios_similares = []
            for otro_usuario in self.grafo.nodes():
                if self.grafo.nodes[otro_usuario]['type'] == 'usuario' and otro_usuario != usuario_node:
                    similitud = self._calcular_similitud(usuario_node, otro_usuario)
                    usuarios_similares.append((otro_usuario, similitud))
                    
            # Ordenar por similitud
            usuarios_similares.sort(key=lambda x: x[1], reverse=True)
            
            # Obtener recomendaciones
            recomendaciones = []
            for usuario_similar, _ in usuarios_similares[:max_recomendaciones]:
                for _, libro_node in self.grafo.edges(usuario_similar):
                    if (self.grafo.nodes[libro_node]['type'] == 'libro' and 
                        libro_node not in libros_interactuados):
                        recomendaciones.append({
                            'isbn': self.grafo.nodes[libro_node]['isbn'],
                            'titulo': self.grafo.nodes[libro_node]['titulo'],
                            'autor': self.grafo.nodes[libro_node]['autor_nombre'],
                            'peso': self.grafo.nodes[libro_node]['peso']
                        })
                        
            return recomendaciones[:max_recomendaciones]
        except Exception as e:
            self.logger.error(f"Error al obtener recomendaciones: {e}")
            return []

    def _calcular_similitud(self, usuario1: str, usuario2: str) -> float:
        """
        Calcula la similitud entre dos usuarios basada en sus interacciones.
        
        Args:
            usuario1 (str): ID del primer usuario
            usuario2 (str): ID del segundo usuario
            
        Returns:
            float: Puntuación de similitud entre 0 y 1
        """
        try:
            libros_usuario1 = set(self.grafo[usuario1].keys())
            libros_usuario2 = set(self.grafo[usuario2].keys())
            
            if not libros_usuario1 or not libros_usuario2:
                return 0.0
                
            interseccion = len(libros_usuario1.intersection(libros_usuario2))
            union = len(libros_usuario1.union(libros_usuario2))
            
            return interseccion / union if union > 0 else 0.0
        except Exception as e:
            self.logger.error(f"Error al calcular similitud: {e}")
            return 0.0

    def agregar_usuario(self, correo: str, nombre: Optional[str] = None, peso: float = 1.0) -> bool:
        """
        Agrega un usuario como nodo al grafo.
        
        Args:
            correo (str): Correo electrónico del usuario
            nombre (str, optional): Nombre del usuario
            peso (float): Peso inicial del nodo
            
        Returns:
            bool: True si se agregó correctamente, False en caso contrario
        """
        try:
            node_id = self._get_node_id("usuario", correo)
            if not self.grafo.has_node(node_id):
                self.grafo.add_node(
                    node_id,
                    type="usuario",
                    correo=correo,
                    nombre=nombre,
                    peso=peso,
                    fecha_creacion=datetime.now().isoformat()
                )
                self.logger.info(f"Usuario '{nombre}' (Correo: {correo}) agregado.")
                return True
            else:
                self.grafo.nodes[node_id].update({
                    'nombre': nombre,
                    'peso': peso
                })
                return True
        except Exception as e:
            self.logger.error(f"Error al agregar usuario: {e}")
            return False

    def guardar_estado(self) -> bool:
        """
        Guarda el estado actual del grafo en la base de datos.
        
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            datos_grafo = {
                'nodes': dict(self.grafo.nodes(data=True)),
                'edges': list(self.grafo.edges(data=True))
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO grafo_estado (fecha_actualizacion, datos_grafo)
                    VALUES (?, ?)
                ''', (datetime.now().isoformat(), json.dumps(datos_grafo)))
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error al guardar estado: {e}")
            return False

    def cargar_estado(self) -> bool:
        """
        Carga el último estado guardado del grafo desde la base de datos.
        
        Returns:
            bool: True si se cargó correctamente, False en caso contrario
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT datos_grafo FROM grafo_estado
                    ORDER BY fecha_actualizacion DESC LIMIT 1
                ''')
                resultado = cursor.fetchone()
                
                if resultado:
                    datos_grafo = json.loads(resultado[0])
                    self.grafo = nx.DiGraph()
                    
                    # Restaurar nodos
                    for node, attrs in datos_grafo['nodes'].items():
                        self.grafo.add_node(node, **attrs)
                        
                    # Restaurar aristas
                    for u, v, attrs in datos_grafo['edges']:
                        self.grafo.add_edge(u, v, **attrs)
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error al cargar estado: {e}")
            return False

    def analizar_eficiencia(self) -> Dict[str, Any]:
        """
        Realiza un análisis de eficiencia del grafo.
        
        Returns:
            Dict[str, Any]: Métricas de eficiencia
        """
        try:
            num_nodos = self.grafo.number_of_nodes()
            num_aristas = self.grafo.number_of_edges()

            if num_nodos == 0:
                return {
                    'numero_nodos': 0,
                    'numero_aristas': 0,
                    'densidad': 0.0,
                    'componentes_conexas': 0,
                    'grado_promedio': 0.0,
                    'diametro': float('inf'),
                    'coeficiente_clustering': 0.0
                }

            grado_promedio = sum(dict(self.grafo.degree()).values()) / num_nodos

            is_strongly_connected = nx.is_strongly_connected(self.grafo)
            diametro = nx.diameter(self.grafo) if is_strongly_connected else float('inf')
            coeficiente_clustering = nx.average_clustering(self.grafo.to_undirected())

            return {
                'numero_nodos': num_nodos,
                'numero_aristas': num_aristas,
                'densidad': nx.density(self.grafo),
                'componentes_conexas': nx.number_weakly_connected_components(self.grafo),
                'grado_promedio': grado_promedio,
                'diametro': diametro,
                'coeficiente_clustering': coeficiente_clustering
            }
        except Exception as e:
            self.logger.error(f"Error al analizar eficiencia: {e}", exc_info=True)
            return {}

    def visualizar_grafo(self, tipo_grafo: str = "co-préstamos"):
        """
        Visualiza el grafo actual usando matplotlib.
        
        Args:
            tipo_grafo (str): Tipo de grafo a visualizar ("co-préstamos" o "similitud de usuarios")
        """
        if not self.grafo.number_of_nodes():
            self.logger.warning("El grafo está vacío. No hay nada que visualizar.")
            return
        
        try:
            plt.figure(figsize=(12, 8))
            
            # Configurar el layout
            pos = nx.spring_layout(self.grafo, k=1, iterations=50)
            
            # Dibujar nodos
            node_colors = []
            node_sizes = []
            for node in self.grafo.nodes():
                tipo_nodo = self.grafo.nodes[node].get('tipo', '')
                if tipo_nodo == 'libro':
                    node_colors.append('lightblue')
                    node_sizes.append(100 + len(list(self.grafo.neighbors(node))) * 20)
                else:
                    node_colors.append('lightgreen')
                    node_sizes.append(100)
                    
            nx.draw_networkx_nodes(self.grafo, pos, node_color=node_colors, node_size=node_sizes, alpha=0.7)
            
            # Dibujar aristas
            edge_weights = [self.grafo[u][v]['peso'] for u, v in self.grafo.edges()]
            nx.draw_networkx_edges(self.grafo, pos, width=edge_weights, alpha=0.5, edge_color='gray')
            
            # Dibujar etiquetas
            labels = {node: self.grafo.nodes[node].get('titulo', node) for node in self.grafo.nodes()}
            nx.draw_networkx_labels(self.grafo, pos, labels, font_size=8)
            
            # Agregar título y leyenda
            plt.title(f"Grafo de {tipo_grafo}")
            
            # Agregar leyenda para los pesos de las aristas
            if edge_weights:
                max_weight = max(edge_weights)
                plt.text(0.02, 0.02, 
                        f"Grosor de línea indica frecuencia de co-préstamos\nMáximo: {max_weight} préstamos",
                        transform=plt.gca().transAxes)
            
            plt.axis('off')
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            self.logger.error(f"Error al visualizar grafo: {e}")
            raise

    def construir_grafo_co_prestamos(self, prestamos, libros):
        """
        Construye un grafo de co-préstamos donde los nodos son libros y las aristas
        representan libros que han sido prestados juntos por los mismos usuarios.
        
        Args:
            prestamos (dict): Diccionario de préstamos
            libros (dict): Diccionario de libros
        """
        self.grafo.clear()
        self.logger.info("Construyendo grafo de co-préstamos...")
        
        # Crear nodos para cada libro
        for isbn, libro in libros.items():
            node_id = self._get_node_id("libro", isbn)
            self.grafo.add_node(
                node_id,
                tipo="libro",
                isbn=isbn,
                titulo=libro.titulo,
                autor=libro.autor
            )
        
        # Crear diccionario de libros prestados por usuario
        libros_por_usuario = {}
        for prestamo in prestamos.values():
            if prestamo.estado == "Activo":  # Solo considerar préstamos activos
                usuario = prestamo.usuario.correoU
                if usuario not in libros_por_usuario:
                    libros_por_usuario[usuario] = set()
                libros_por_usuario[usuario].add(prestamo.libro.isbn)
        
        # Crear aristas entre libros prestados por el mismo usuario
        for usuario, libros_prestados in libros_por_usuario.items():
            libros_list = list(libros_prestados)
            for i in range(len(libros_list)):
                for j in range(i + 1, len(libros_list)):
                    libro1 = libros_list[i]
                    libro2 = libros_list[j]
                    
                    node1 = self._get_node_id("libro", libro1)
                    node2 = self._get_node_id("libro", libro2)
                    
                    # Si ya existe una arista, incrementar el peso
                    if self.grafo.has_edge(node1, node2):
                        self.grafo[node1][node2]['peso'] += 1
                    else:
                        self.grafo.add_edge(
                            node1,
                            node2,
                            peso=1,
                            tipo="co-prestamo",
                            usuarios=[usuario]
                        )
        
        self.logger.info(f"Grafo de co-préstamos construido con {self.grafo.number_of_nodes()} nodos y {self.grafo.number_of_edges()} aristas") 

    def obtener_libros_recomendados(self, correo_usuario: str, biblioteca, top_n: int = 5) -> list:
        """
        Obtiene recomendaciones de libros para un usuario basadas en co-préstamos.
        
        Args:
            correo_usuario (str): Correo del usuario
            biblioteca: Instancia de la clase Biblioteca
            top_n (int): Número máximo de recomendaciones a devolver
            
        Returns:
            list: Lista de diccionarios con información de libros recomendados
        """
        if not self.grafo.number_of_nodes():
            self.logger.warning("El grafo está vacío. No se pueden generar recomendaciones.")
            return []
        
        # Obtener libros prestados por el usuario
        usuario = biblioteca.usuarios.get(correo_usuario)
        if not usuario:
            self.logger.warning(f"Usuario {correo_usuario} no encontrado.")
            return []
        
        libros_prestados = set()
        for prestamo in usuario.libros_prestados:
            if prestamo.estado == "Activo":
                libros_prestados.add(prestamo.libro.isbn)
            
        if not libros_prestados:
            self.logger.info(f"El usuario {correo_usuario} no tiene libros prestados actualmente.")
            return []
        
        # Calcular puntuación para cada libro no prestado
        puntuaciones = {}
        for libro_isbn in biblioteca.libros:
            if libro_isbn not in libros_prestados and biblioteca.libros[libro_isbn].disponible:
                puntuacion = 0
                node_id = self._get_node_id("libro", libro_isbn)
                
                # Sumar pesos de aristas con libros prestados por el usuario
                for libro_prestado in libros_prestados:
                    node_prestado = self._get_node_id("libro", libro_prestado)
                    if self.grafo.has_edge(node_prestado, node_id):
                        puntuacion += self.grafo[node_prestado][node_id]['peso']
                    if self.grafo.has_edge(node_id, node_prestado):
                        puntuacion += self.grafo[node_id][node_prestado]['peso']
                    
                if puntuacion > 0:
                    puntuaciones[libro_isbn] = puntuacion
                
        # Ordenar libros por puntuación y devolver los top_n
        libros_recomendados = []
        for isbn, score in sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)[:top_n]:
            libro = biblioteca.libros[isbn]
            libros_recomendados.append({
                'isbn': isbn,
                'titulo': libro.titulo,
                'autor': libro.autor,
                'score': score
            })
        
        return libros_recomendados 