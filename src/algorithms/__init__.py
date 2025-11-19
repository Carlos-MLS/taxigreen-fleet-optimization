"""
Módulo de algoritmos de procura.
Contém implementações de algoritmos informados e não-informados.
"""

from .uninformed import (
    breadth_first_search,
    depth_first_search,
    uniform_cost_search
)

from .informed import (
    a_star_search,
    greedy_best_first_search,
    weighted_a_star
)

from .heuristics import (
    heuristic_zero,
    heuristic_euclidean,
    heuristic_manhattan,
    heuristic_chebyshev,
    heuristic_haversine,
    heuristic_time_estimate,
    heuristic_composite,
    heuristic_min_stations,
    HeuristicFactory,
    is_admissible,
    is_consistent
)

__all__ = [
    # Uninformed search
    'breadth_first_search',
    'depth_first_search',
    'uniform_cost_search',
    
    # Informed search
    'a_star_search',
    'greedy_best_first_search',
    'weighted_a_star',
    
    # Heuristics
    'heuristic_zero',
    'heuristic_euclidean',
    'heuristic_manhattan',
    'heuristic_chebyshev',
    'heuristic_haversine',
    'heuristic_time_estimate',
    'heuristic_composite',
    'heuristic_min_stations',
    'HeuristicFactory',
    'is_admissible',
    'is_consistent'
]
