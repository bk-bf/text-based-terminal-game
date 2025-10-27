"""
Fantasy RPG - Text-Based D&D 5e Adventure Game

A comprehensive text-based RPG system implementing D&D 5e mechanics
with world generation, character progression, and interactive gameplay.
"""

# Import main components for easy access
# Remove circular dependencies - don't import from game or ui here
from .core import Character, create_character, Equipment, Inventory, Item
from .world import TerrainGenerator, World
# from .game import main  # REMOVED - causes circular dependency
# from .ui import run_ui  # REMOVED - may cause circular dependency

__version__ = "1.0.0"
__author__ = "Fantasy RPG Development Team"

__all__ = [
    'Character', 'create_character', 'Equipment', 'Inventory', 'Item',
    'TerrainGenerator', 'World'
]