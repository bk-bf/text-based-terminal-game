"""
Fantasy RPG - Core Game Mechanics

This package contains the core game mechanics including character creation,
equipment, inventory, and other fundamental game systems.
"""

# Import core classes for easy access
from .character import Character, create_character
from .equipment import Equipment
from .inventory import Inventory, InventoryItem, InventoryManager
from .item import Item
from .character_class import CharacterClass, ClassLoader
from .race import Race, RaceLoader
from .backgrounds import Background, BackgroundLoader
from .feats import Feat, FeatLoader
from .skills import SkillSystem, SkillProficiencies
from .character_creation import CharacterCreationFlow

__all__ = [
    'Character', 'create_character', 'Equipment', 'Inventory', 'InventoryItem', 
    'InventoryManager', 'Item', 'CharacterClass', 'ClassLoader', 'Race', 
    'RaceLoader', 'Background', 'BackgroundLoader', 'Feat', 'FeatLoader',
    'SkillSystem', 'SkillProficiencies', 'CharacterCreationFlow'
]