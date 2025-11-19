"""
Módulo que define a classe City (Cidade).
Representa a cidade como um grafo com nós e arestas dinâmicas.
"""

from typing import Dict, List, Optional, Tuple, Set
import math


class Edge:
    """
    Representa uma aresta (caminho) entre dois nós.
    
    Attributes:
        origem: Nó de origem
        destino: Nó de destino
        distancia: Distância em km
        tempo_base: Tempo de viagem sem trânsito (minutos)
        fator_transito: Multiplicador atual do tempo (1.0 - 3.0)
        estado_aberto: Se a estrada está aberta ou cortada
        duracao_corte: Tempo até reabrir (minutos), se cortada
    """
    
    def __init__(
        self,
        origem: str,
        destino: str,
        distancia: float,
        tempo_base: float
    ):
        """
        Inicializa uma aresta.
        
        Args:
            origem: Nó de origem
            destino: Nó de destino
            distancia: Distância em km
            tempo_base: Tempo base em minutos
        """
        self.origem = origem
        self.destino = destino
        self.distancia = distancia
        self.tempo_base = tempo_base
        self.fator_transito = 1.0  # Normal inicialmente
        self.estado_aberto = True
        self.duracao_corte = 0.0
    
    def tempo_viagem(self) -> float:
        """
        Calcula o tempo de viagem atual considerando trânsito.
        
        Returns:
            Tempo em minutos
        """
        if not self.estado_aberto:
            return float('inf')  # Estrada cortada
        return self.tempo_base * self.fator_transito
    
    def cortar_estrada(self, duracao: float):
        """
        Corta a estrada temporariamente.
        
        Args:
            duracao: Tempo até reabrir (minutos)
        """
        self.estado_aberto = False
        self.duracao_corte = duracao
    
    def reabrir_estrada(self):
        """Reabre a estrada."""
        self.estado_aberto = True
        self.duracao_corte = 0.0
    
    def atualizar_transito(self, fator: float):
        """
        Atualiza o fator de trânsito.
        
        Args:
            fator: Novo fator (1.0 = livre, 3.0 = congestionamento)
        """
        self.fator_transito = max(1.0, min(3.0, fator))


class City:
    """
    Representa a cidade como um grafo.
    
    Attributes:
        nodes: Conjunto de nós (localizações)
        edges: Dicionário de arestas {(origem, destino): Edge}
        adjacencias: Dicionário de adjacências para busca rápida
    """
    
    def __init__(self):
        """Inicializa uma cidade vazia."""
        self.nodes: Set[str] = set()
        self.edges: Dict[Tuple[str, str], Edge] = {}
        self.adjacencias: Dict[str, List[str]] = {}
    
    def adicionar_no(self, node_id: str):
        """
        Adiciona um nó à cidade.
        
        Args:
            node_id: Identificador do nó
        """
        self.nodes.add(node_id)
        if node_id not in self.adjacencias:
            self.adjacencias[node_id] = []
    
    def adicionar_aresta(
        self,
        origem: str,
        destino: str,
        distancia: float,
        tempo_base: Optional[float] = None,
        bidirecional: bool = True
    ):
        """
        Adiciona uma aresta entre dois nós.
        
        Args:
            origem: Nó de origem
            destino: Nó de destino
            distancia: Distância em km
            tempo_base: Tempo base (se None, calcula assumindo ~40km/h)
            bidirecional: Se True, cria aresta nos dois sentidos
        """
        # Garantir que os nós existem
        self.adicionar_no(origem)
        self.adicionar_no(destino)
        
        # Calcular tempo base se não fornecido
        if tempo_base is None:
            velocidade_media = 40  # km/h
            tempo_base = (distancia / velocidade_media) * 60  # minutos
        
        # Criar aresta
        edge = Edge(origem, destino, distancia, tempo_base)
        self.edges[(origem, destino)] = edge
        
        # Atualizar adjacências
        if destino not in self.adjacencias[origem]:
            self.adjacencias[origem].append(destino)
        
        # Se bidirecional, criar aresta inversa
        if bidirecional:
            edge_inv = Edge(destino, origem, distancia, tempo_base)
            self.edges[(destino, origem)] = edge_inv
            if origem not in self.adjacencias[destino]:
                self.adjacencias[destino].append(origem)
    
    def obter_aresta(self, origem: str, destino: str) -> Optional[Edge]:
        """
        Obtém uma aresta entre dois nós.
        
        Args:
            origem: Nó de origem
            destino: Nó de destino
            
        Returns:
            Edge ou None se não existir
        """
        return self.edges.get((origem, destino))
    
    def obter_vizinhos(self, node_id: str) -> List[str]:
        """
        Obtém os vizinhos de um nó.
        
        Args:
            node_id: Identificador do nó
            
        Returns:
            Lista de nós vizinhos
        """
        return self.adjacencias.get(node_id, [])
    
    def existe_caminho(self, origem: str, destino: str) -> bool:
        """
        Verifica se existe caminho direto entre dois nós.
        
        Args:
            origem: Nó de origem
            destino: Nó de destino
            
        Returns:
            True se existe aresta direta
        """
        edge = self.obter_aresta(origem, destino)
        return edge is not None and edge.estado_aberto
    
    def distancia_euclidiana(self, no1: str, no2: str, coordenadas: Dict[str, Tuple[float, float]]) -> float:
        """
        Calcula a distância euclidiana entre dois nós.
        
        Args:
            no1: Primeiro nó
            no2: Segundo nó
            coordenadas: Dicionário {node_id: (x, y)}
            
        Returns:
            Distância euclidiana
        """
        if no1 not in coordenadas or no2 not in coordenadas:
            return float('inf')
        
        x1, y1 = coordenadas[no1]
        x2, y2 = coordenadas[no2]
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def atualizar_transito_global(self, fator: float):
        """
        Atualiza o trânsito em todas as arestas.
        
        Args:
            fator: Fator de trânsito global
        """
        for edge in self.edges.values():
            edge.atualizar_transito(fator)
    
    def atualizar_transito_zona(self, nodes: List[str], fator: float):
        """
        Atualiza o trânsito em uma zona específica.
        
        Args:
            nodes: Lista de nós da zona
            fator: Fator de trânsito
        """
        for (origem, destino), edge in self.edges.items():
            if origem in nodes or destino in nodes:
                edge.atualizar_transito(fator)
    
    def cortar_estrada(self, origem: str, destino: str, duracao: float):
        """
        Corta uma estrada temporariamente.
        
        Args:
            origem: Nó de origem
            destino: Nó de destino
            duracao: Duração do corte (minutos)
        """
        edge = self.obter_aresta(origem, destino)
        if edge:
            edge.cortar_estrada(duracao)
    
    def num_nodes(self) -> int:
        """Retorna o número de nós."""
        return len(self.nodes)
    
    def num_edges(self) -> int:
        """Retorna o número de arestas."""
        return len(self.edges)
    
    def __str__(self) -> str:
        """Representação string da cidade."""
        return f"City: {self.num_nodes()} nós, {self.num_edges()} arestas"
    
    def to_dict(self) -> dict:
        """
        Converte a cidade para dicionário.
        
        Returns:
            Dicionário com estrutura do grafo
        """
        return {
            'num_nodes': self.num_nodes(),
            'num_edges': self.num_edges(),
            'nodes': list(self.nodes),
            'edges': [
                {
                    'origem': origem,
                    'destino': destino,
                    'distancia': edge.distancia,
                    'tempo_base': edge.tempo_base,
                    'fator_transito': edge.fator_transito,
                    'estado_aberto': edge.estado_aberto
                }
                for (origem, destino), edge in self.edges.items()
            ]
        }
