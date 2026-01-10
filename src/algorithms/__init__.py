"""
Modulo de algoritmos de procura.
Contem implementacoes de algoritmos informados e nao-informados.
"""

from .uninformed import (
    breadth_first_search,
    depth_first_search,
    uniform_cost_search
)

from .informed import (
    a_star_search,
    greedy_best_first_search
)

from .heuristics import (
    heuristic_euclidean,
    heuristic_manhattan,
    heuristic_time_estimate,
    heuristic_composite,
    HeuristicFactory
)

__all__ = [
    # Uninformed search
    'breadth_first_search',
    'depth_first_search',
    'uniform_cost_search',
    
    # Informed search
    'a_star_search',
    'greedy_best_first_search',
    
    # Heuristics
    'heuristic_euclidean',
    'heuristic_manhattan',
    'heuristic_time_estimate',
    'heuristic_composite',
    'HeuristicFactory'
]
