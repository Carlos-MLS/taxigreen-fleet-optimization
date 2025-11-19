"""
Módulo de simulação.
Contém simulador e coletor de métricas.
"""

from .simulator import TaxiSimulator, EventType, SimulationEvent
from .metrics import MetricsCollector, PedidoMetrica, VeiculoMetrica

__all__ = [
    'TaxiSimulator',
    'EventType',
    'SimulationEvent',
    'MetricsCollector',
    'PedidoMetrica',
    'VeiculoMetrica'
]
