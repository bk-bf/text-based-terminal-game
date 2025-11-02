"""
Fantasy RPG - Location Systems

JSON-based location generation system using CDDA-style data-driven approach.
Locations are generated from templates with weighted spawn tables.
Uses unified Item class from core.item (GameItem removed).
"""

from .location_generator import LocationGenerator, Location, Area, LocationType, AreaSize, TerrainType
from .location_generator import GameObject, GameEntity

__all__ = [
    'LocationGenerator', 'Location', 'Area', 'LocationType', 'AreaSize', 'TerrainType',
    'GameObject', 'GameEntity'
]