"""
Fantasy RPG - World Generation and Management

This package contains world generation systems including terrain generation,
climate simulation, and world management.
"""

# Import world classes for easy access
from .terrain_generation import TerrainGenerator, NoiseGenerator
from .world import World

__all__ = ['TerrainGenerator', 'NoiseGenerator', 'World']