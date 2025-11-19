"""
Módulo de estratégias de alocação.
"""

from .allocation import (
    AllocationStrategy,
    NearestVehicleStrategy,
    LowestCostStrategy,
    EcoFriendlyStrategy,
    MinEmissionsStrategy,
    BalancedStrategy,
    PriorityAwareStrategy,
    criar_estrategia
)

__all__ = [
    'AllocationStrategy',
    'NearestVehicleStrategy',
    'LowestCostStrategy',
    'EcoFriendlyStrategy',
    'MinEmissionsStrategy',
    'BalancedStrategy',
    'PriorityAwareStrategy',
    'criar_estrategia'
]
