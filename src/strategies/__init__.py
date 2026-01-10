"""
Módulo de estratégias de alocação.
"""

from .allocation import (
    AllocationStrategy,
    NearestVehicleStrategy,
    LowestCostStrategy,
    EcoFriendlyStrategy,
    criar_estrategia
)

__all__ = [
    'AllocationStrategy',
    'NearestVehicleStrategy',
    'LowestCostStrategy',
    'EcoFriendlyStrategy',
    'criar_estrategia'
]
