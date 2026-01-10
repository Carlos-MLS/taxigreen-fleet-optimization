"""
Funcoes Heuristicas para Procura Informada.

Heuristicas implementadas:
    - Euclidiana: Distancia em linha reta
    - Manhattan: Soma das diferencas absolutas
    - Tempo Estimado: Distancia / velocidade media
    - Composta: Tempo estimado ajustado pelo transito
"""

import math
from typing import Dict, Tuple


def heuristic_euclidean(
    state: str,
    goal_state: str,
    coordinates: Dict[str, Tuple[float, float]]
) -> float:
    """
    Distancia em linha reta entre dois pontos.
    
    Formula: h(n) = sqrt((x2-x1)^2 + (y2-y1)^2)
    
    Args:
        state: Identificador do no atual
        goal_state: Identificador do no objetivo
        coordinates: Mapa {node_id: (x, y)} com as posicoes
        
    Returns:
        Distancia euclidiana em km
    """
    # Verificacao de seguranca: se os nos nao existem, retorna 0
    if state not in coordinates or goal_state not in coordinates:
        return 0.0
    
    # Obter as coordenadas (x, y) de cada ponto
    x1, y1 = coordinates[state]
    x2, y2 = coordinates[goal_state]
    
    # Teorema de Pitagoras: distancia = raiz((dx)^2 + (dy)^2)
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def heuristic_manhattan(
    state: str,
    goal_state: str,
    coordinates: Dict[str, Tuple[float, float]]
) -> float:
    """
    Distancia de Manhattan (soma das diferencas absolutas).
    
    Formula: h(n) = |x2-x1| + |y2-y1|
    
    Args:
        state: Identificador do no atual
        goal_state: Identificador do no objetivo
        coordinates: Mapa {node_id: (x, y)} com as posicoes
        
    Returns:
        Distancia de Manhattan
    """
    if state not in coordinates or goal_state not in coordinates:
        return 0.0
    
    x1, y1 = coordinates[state]
    x2, y2 = coordinates[goal_state]
    
    # Soma das distancias absolutas em cada eixo
    return abs(x2 - x1) + abs(y2 - y1)


def heuristic_time_estimate(
    state: str,
    goal_state: str,
    coordinates: Dict[str, Tuple[float, float]],
    average_speed: float = 40.0
) -> float:
    """
    Tempo estimado de viagem (distancia / velocidade).
    
    Formula: h(n) = distancia_euclidiana / velocidade_media * 60 (minutos)
    
    Args:
        state: Identificador do no atual
        goal_state: Identificador do no objetivo
        coordinates: Mapa com as posicoes dos nos
        average_speed: Velocidade media em km/h (default: 40)
        
    Returns:
        Tempo estimado em minutos
    """
    # Primeiro calculamos a distancia em linha reta
    distance_km = heuristic_euclidean(state, goal_state, coordinates)
    
    # Tempo = Distancia / Velocidade
    time_hours = distance_km / average_speed
    
    # Converter para minutos (mais intuitivo para viagens urbanas)
    time_minutes = time_hours * 60
    
    return time_minutes


def heuristic_composite(
    state: str,
    goal_state: str,
    coordinates: Dict[str, Tuple[float, float]],
    traffic_factor: float = 1.0,
    average_speed: float = 40.0
) -> float:
    """
    Tempo estimado com ajuste pelo fator de transito.
    
    Formula: h(n) = (distancia / velocidade * 60) * fator_transito
    
    Fatores tipicos: 1.0 (livre), 1.5 (moderado), 2.0 (intenso), 3.0 (severo)
    
    Args:
        state: Identificador do no atual
        goal_state: Identificador do no objetivo
        coordinates: Mapa com as posicoes dos nos
        traffic_factor: Multiplicador de tempo (1.0 = transito livre)
        average_speed: Velocidade base em km/h
        
    Returns:
        Tempo estimado ajustado em minutos
    """
    # Calcular o tempo base sem considerar transito
    base_time = heuristic_time_estimate(state, goal_state, coordinates, average_speed)
    
    # Ajustar pelo fator de transito
    # Se fator = 2, a viagem demora o dobro do tempo
    adjusted_time = base_time * traffic_factor
    
    return adjusted_time


class HeuristicFactory:
    """
    Fabrica para criar heuristicas pre-configuradas.
    
    Devolve funcoes h(estado) -> float prontas a usar no A* ou Greedy.
    """
    
    @staticmethod
    def create_euclidean(coordinates: Dict[str, Tuple[float, float]], goal: str):
        """Cria heuristica euclidiana para o objetivo especificado."""
        def h(state):
            return heuristic_euclidean(state, goal, coordinates)
        return h
    
    @staticmethod
    def create_manhattan(coordinates: Dict[str, Tuple[float, float]], goal: str):
        """Cria heuristica Manhattan para o objetivo especificado."""
        def h(state):
            return heuristic_manhattan(state, goal, coordinates)
        return h
    
    @staticmethod
    def create_time_estimate(
        coordinates: Dict[str, Tuple[float, float]],
        goal: str,
        average_speed: float = 40.0
    ):
        """Cria heuristica de tempo para o objetivo especificado."""
        def h(state):
            return heuristic_time_estimate(state, goal, coordinates, average_speed)
        return h
    
    @staticmethod
    def create_composite(
        coordinates: Dict[str, Tuple[float, float]],
        goal: str,
        traffic_factor: float = 1.0,
        average_speed: float = 40.0
    ):
        """Cria heuristica composta para um objetivo especifico."""
        def h(state):
            return heuristic_composite(state, goal, coordinates, traffic_factor, average_speed)
        return h
