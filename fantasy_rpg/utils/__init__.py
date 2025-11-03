"""
Fantasy RPG - Utility Functions

This package contains utility functions and helper classes used throughout the game.
"""

# Import utility functions for easy access
from .utils import *

__all__ = [
    'roll_d20', 'roll_dice', 'format_modifier', 'calculate_distance',
    'Coordinates', 'Dice',
    'HexCoords', 'Direction'  # Type aliases for coordinate representations
]