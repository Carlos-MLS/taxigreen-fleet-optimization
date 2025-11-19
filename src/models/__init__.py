"""
Módulo models - Classes base para o sistema TaxiGreen.
Exporta todas as classes principais.
"""

from .vehicle import Vehicle, VehicleType, VehicleState
from .request import Request, Priority, EnvironmentalPreference, RequestStatus
from .station import Station, StationType, StationStatus
from .city import City, Edge

__all__ = [
    'Vehicle',
    'VehicleType',
    'VehicleState',
    'Request',
    'Priority',
    'EnvironmentalPreference',
    'RequestStatus',
    'Station',
    'StationType',
    'StationStatus',
    'City',
    'Edge',
]
