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
            return {
                'numero_nodos': self.grafo.number_of_nodes(),
                'numero_aristas': self.grafo.number_of_edges(),
                'densidad': nx.density(self.grafo),
                'componentes_conexas': nx.number_weakly_connected_components(self.grafo),
                'grado_promedio': sum(dict(self.grafo.degree()).values()) / self.grafo.number_of_nodes(),
                'diametro': nx.diameter(self.grafo) if nx.is_connected(self.grafo.to_undirected()) else float('inf'),
                'coeficiente_clustering': nx.average_clustering(self.grafo.to_undirected())
            }
        except Exception as e:
            self.logger.error(f"Error al analizar eficiencia: {e}")
            return {}

    def visualizar_grafo(self, title: str = "Grafo de la Biblioteca"):
        """
        Visualiza el grafo usando Matplotlib con mejoras en la presentación.
        
        Args:
            title (str): Título del gráfico
        """
        try:
            if self.grafo.number_of_nodes() == 0:
                self.logger.warning("El grafo está vacío, no se puede visualizar.")
                return

            plt.figure(figsize=(15, 12))
            pos = nx.spring_layout(self.grafo, seed=42, k=1)

            # Configuración de nodos
            node_colors = []
            node_sizes = []
            node_labels = {}
            
            for node_id, attrs in self.grafo.nodes(data=True):
                node_type = attrs.get('type', 'desconocido')
                peso = attrs.get('peso', 1.0)
                
                # Asignar colores según tipo
                if node_type == 'libro':
                    node_colors.append('skyblue')
                    node_labels[node_id] = attrs.get('titulo', node_id)[:20] + "..."
                elif node_type == 'usuario':
                    node_colors.append('lightgreen')
                    node_labels[node_id] = attrs.get('nombre', node_id)[:20]
                elif node_type == 'autor':
                    node_colors.append('lightcoral')
                    node_labels[node_id] = attrs.get('nombre', node_id)[:20]
                elif node_type == 'genero':
                    node_colors.append('lightyellow')
                    node_labels[node_id] = attrs.get('nombre', node_id)[:20]
                else:
                    node_colors.append('gray')
                    node_labels[node_id] = node_id.split('_')[0]
                
                # Tamaño del nodo basado en su peso
                node_sizes.append(1000 + (peso * 500))

            # Dibujar nodos
            nx.draw_networkx_nodes(
                self.grafo, pos,
                node_color=node_colors,
                node_size=node_sizes,
                alpha=0.9,
                linewidths=1,
                edgecolors='black'
            )

            # Dibujar aristas con pesos
            edge_weights = [self.grafo[u][v].get('peso', 1.0) for u, v in self.grafo.edges()]
            nx.draw_networkx_edges(
                self.grafo, pos,
                edge_color='darkgray',
                arrows=True,
                arrowsize=20,
                alpha=0.6,
                width=edge_weights
            )

            # Etiquetas de nodos
            nx.draw_networkx_labels(
                self.grafo, pos,
                labels=node_labels,
                font_size=8,
                font_weight='bold'
            )

            # Etiquetas de aristas
            edge_labels = {
                (u, v): f"{data.get('relation', '')}\n({data.get('peso', 1.0):.1f})"
                for u, v, data in self.grafo.edges(data=True)
            }
            nx.draw_networkx_edge_labels(
                self.grafo, pos,
                edge_labels=edge_labels,
                font_color='blue',
                font_size=7
            )

            plt.title(title, size=15)
            plt.axis('off')
            
            # Agregar leyenda
            tipos = ['Libro', 'Usuario', 'Autor', 'Género']
            colores = ['skyblue', 'lightgreen', 'lightcoral', 'lightyellow']
            patches = [plt.Line2D([0], [0], marker='o', color='w', 
                                markerfacecolor=color, markersize=10, label=tipo)
                      for color, tipo in zip(colores, tipos)]
            plt.legend(handles=patches, loc='upper right', bbox_to_anchor=(1.1, 1))
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            self.logger.error(f"Error al visualizar grafo: {e}")
            raise 