"""
Módulo de utilitários para algoritmos de procura.
Contém classes Node, Problem e estruturas auxiliares.
"""

from .node import Node, SearchResult
from .problem import Problem, RouteProblem

__all__ = [
    'Node',
    'SearchResult',
    'Problem',
    'RouteProblem'
]
