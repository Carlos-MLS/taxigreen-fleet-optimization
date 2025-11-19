"""
Funções heurísticas para procura informada.
Implementa diferentes heurísticas para problemas de roteamento.
"""

import math
from typing import Dict, Tuple, Optional


def heuristic_zero(state, goal_state=None, **kwargs) -> float:
    """
    Heurística nula (sempre retorna 0).
    Admissível mas não informativa.
    
    Args:
        state: Estado atual
        goal_state: Estado objetivo (ignorado)
        
    Returns:
        0.0
    """
    return 0.0


def heuristic_euclidean(
    state: str,
    goal_state: str,
    coordinates: Dict[str, Tuple[float, float]]
) -> float:
    """
    Heurística da distância euclidiana.
    
    Calcula a distância em linha reta entre dois pontos.
    Admissível se a velocidade for constante.
    
    Args:
        state: Nó atual
        goal_state: Nó objetivo
        coordinates: Dicionário {node_id: (x, y)}
        
    Returns:
        Distância euclidiana
    """
    if state not in coordinates or goal_state not in coordinates:
        return 0.0
    
    x1, y1 = coordinates[state]
    x2, y2 = coordinates[goal_state]
    
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def heuristic_manhattan(
    state: str,
    goal_state: str,
    coordinates: Dict[str, Tuple[float, float]]
) -> float:
    """
    Heurística da distância Manhattan.
    
    Soma das diferenças absolutas nas coordenadas.
    Útil em grelhas com movimento ortogonal.
    
    Args:
        state: Nó atual
        goal_state: Nó objetivo
        coordinates: Dicionário {node_id: (x, y)}
        
    Returns:
        Distância Manhattan
    """
    if state not in coordinates or goal_state not in coordinates:
        return 0.0
    
    x1, y1 = coordinates[state]
    x2, y2 = coordinates[goal_state]
    
    return abs(x2 - x1) + abs(y2 - y1)


def heuristic_chebyshev(
    state: str,
    goal_state: str,
    coordinates: Dict[str, Tuple[float, float]]
) -> float:
    """
    Heurística da distância Chebyshev.
    
    Máximo das diferenças absolutas nas coordenadas.
    Útil quando movimento diagonal tem mesmo custo.
    
    Args:
        state: Nó atual
        goal_state: Nó objetivo
        coordinates: Dicionário {node_id: (x, y)}
        
    Returns:
        Distância Chebyshev
    """
    if state not in coordinates or goal_state not in coordinates:
        return 0.0
    
    x1, y1 = coordinates[state]
    x2, y2 = coordinates[goal_state]
    
    return max(abs(x2 - x1), abs(y2 - y1))


def heuristic_haversine(
    state: str,
    goal_state: str,
    coordinates: Dict[str, Tuple[float, float]],
    radius: float = 6371.0
) -> float:
    """
    Heurística da distância Haversine (Grande Círculo).
    
    Calcula distância entre dois pontos numa esfera (Terra).
    Coordenadas devem estar em graus (latitude, longitude).
    
    Args:
        state: Nó atual
        goal_state: Nó objetivo
        coordinates: Dicionário {node_id: (lat, lon)} em graus
        radius: Raio da esfera (default: Terra em km)
        
    Returns:
        Distância em km
    """
    if state not in coordinates or goal_state not in coordinates:
        return 0.0
    
    lat1, lon1 = coordinates[state]
    lat2, lon2 = coordinates[goal_state]
    
    # Converter para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Fórmula de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return radius * c


def heuristic_time_estimate(
    state: str,
    goal_state: str,
    coordinates: Dict[str, Tuple[float, float]],
    average_speed: float = 40.0
) -> float:
    """
    Heurística de tempo estimado.
    
    Estima o tempo de viagem baseado na distância euclidiana
    e velocidade média.
    
    Args:
        state: Nó atual
        goal_state: Nó objetivo  
        coordinates: Dicionário {node_id: (x, y)}
        average_speed: Velocidade média em km/h
        
    Returns:
        Tempo estimado em minutos
    """
    distance_km = heuristic_euclidean(state, goal_state, coordinates)
    time_hours = distance_km / average_speed
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
    Heurística composta (mais realista).
    
    Combina distância com fator de trânsito para estimar
    tempo mais realista.
    
    Args:
        state: Nó atual
        goal_state: Nó objetivo
        coordinates: Dicionário {node_id: (x, y)}
        traffic_factor: Fator de trânsito (1.0 = livre, 3.0 = congestionado)
        average_speed: Velocidade base em km/h
        
    Returns:
        Tempo estimado ajustado em minutos
    """
    # Calcular tempo base
    base_time = heuristic_time_estimate(state, goal_state, coordinates, average_speed)
    
    # Ajustar por trânsito
    adjusted_time = base_time * traffic_factor
    
    return adjusted_time


def heuristic_min_stations(
    state: str,
    goal_state: str,
    station_locations: Dict[str, str],
    coordinates: Dict[str, Tuple[float, float]],
    vehicle_autonomy: float,
    average_speed: float = 40.0
) -> float:
    """
    Heurística que considera necessidade de recarga.
    
    Estima o tempo incluindo possíveis paragens para recarga
    baseado na autonomia do veículo.
    
    Args:
        state: Nó atual
        goal_state: Nó objetivo
        station_locations: Localizações das estações
        coordinates: Coordenadas dos nós
        vehicle_autonomy: Autonomia restante do veículo (km)
        average_speed: Velocidade média
        
    Returns:
        Tempo estimado incluindo recargas
    """
    # Distância total
    total_distance = heuristic_euclidean(state, goal_state, coordinates)
    
    # Tempo base de viagem
    base_time = (total_distance / average_speed) * 60  # minutos
    
    # Se autonomia é suficiente
    if vehicle_autonomy >= total_distance:
        return base_time
    
    # Calcular número de recargas necessárias
    # Assumindo que cada recarga dá autonomia completa
    num_recharges = math.ceil((total_distance - vehicle_autonomy) / vehicle_autonomy)
    
    # Tempo médio de recarga (assumindo 45 min para elétrico)
    recharge_time = num_recharges * 45.0
    
    return base_time + recharge_time


class HeuristicFactory:
    """
    Factory para criar funções heurísticas configuradas.
    Facilita o uso de heurísticas com parâmetros fixos.
    """
    
    @staticmethod
    def create_euclidean(coordinates: Dict[str, Tuple[float, float]], goal: str):
        """Cria heurística euclidiana para um objetivo específico."""
        def h(state):
            return heuristic_euclidean(state, goal, coordinates)
        return h
    
    @staticmethod
    def create_manhattan(coordinates: Dict[str, Tuple[float, float]], goal: str):
        """Cria heurística Manhattan para um objetivo específico."""
        def h(state):
            return heuristic_manhattan(state, goal, coordinates)
        return h
    
    @staticmethod
    def create_time_estimate(
        coordinates: Dict[str, Tuple[float, float]],
        goal: str,
        average_speed: float = 40.0
    ):
        """Cria heurística de tempo para um objetivo específico."""
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
        """Cria heurística composta para um objetivo específico."""
        def h(state):
            return heuristic_composite(state, goal, coordinates, traffic_factor, average_speed)
        return h


def is_admissible(heuristic_values: Dict[str, float], actual_costs: Dict[str, float]) -> bool:
    """
    Verifica se uma heurística é admissível.
    
    Uma heurística é admissível se nunca sobreestima o custo real.
    h(n) <= h*(n) para todo n
    
    Args:
        heuristic_values: Valores heurísticos {state: h(state)}
        actual_costs: Custos reais {state: custo_real}
        
    Returns:
        True se admissível
    """
    for state in heuristic_values:
        if state in actual_costs:
            if heuristic_values[state] > actual_costs[state]:
                return False
    return True


def is_consistent(
    heuristic_func,
    graph,
    goal_state: str
) -> bool:
    """
    Verifica se uma heurística é consistente (monotónica).
    
    Uma heurística é consistente se:
    h(n) <= c(n, n') + h(n') para todo n, n'
    
    Args:
        heuristic_func: Função heurística
        graph: Grafo (objeto City)
        goal_state: Estado objetivo
        
    Returns:
        True se consistente
    """
    # Verificar para todos os nós e seus vizinhos
    for node in graph.nodes:
        h_n = heuristic_func(node)
        
        for neighbor in graph.obter_vizinhos(node):
            edge = graph.obter_aresta(node, neighbor)
            if edge:
                c_n_n_prime = edge.distancia  # ou tempo_viagem()
                h_n_prime = heuristic_func(neighbor)
                
                # h(n) deve ser <= c(n,n') + h(n')
                if h_n > c_n_n_prime + h_n_prime + 0.001:  # pequena tolerância
                    return False
    
    return True
