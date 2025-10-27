"""
Fantasy RPG - Item System

Item base class and related functionality for equipment and inventory management.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
from pathlib import Path


@dataclass
class Item:
    """
    Base class for all items in the game.
    
    Handles weight, properties, and basic item functionality that all
    equipment, consumables, and other items will inherit from.
    """
    name: str
    item_type: str  # 'weapon', 'armor', 'shield', 'consumable', etc.
    weight: float
    cost: int = 0
    description: str = ""
    properties: Optional[List[str]] = None
    
    # Equipment-specific attributes (None for non-equipment items)
    ac_bonus: Optional[int] = None
    damage: Optional[str] = None
    damage_type: Optional[str] = None
    
    def __post_init__(self):
        """Initialize empty properties list if not provided."""
        if self.properties is None:
            self.properties = []
    
    def has_property(self, property_name: str) -> bool:
        """Check if this item has a specific property."""
        return property_name in (self.properties or [])
    
    def add_property(self, property_name: str):
        """Add a property to this item."""
        if self.properties is None:
            self.properties = []
        if property_name not in self.properties:
            self.properties.append(property_name)
    
    def is_weapon(self) -> bool:
        """Check if this item is a weapon."""
        return self.item_type == "weapon"
    
    def is_armor(self) -> bool:
        """Check if this item is armor."""
        return self.item_type == "armor"
    
    def is_shield(self) -> bool:
        """Check if this item is a shield."""
        return self.item_type == "shield"
    
    def is_equipment(self) -> bool:
        """Check if this item can be equipped."""
        return self.item_type in ["weapon", "armor", "shield", "ring", "amulet"]
    
    def can_equip_to(self, slot: str) -> bool:
        """Check if this item can be equipped to a specific slot."""
        slot_mappings = {
            "weapon": ["main_hand", "off_hand"],
            "armor": ["body"],
            "shield": ["off_hand"],
            "ring": ["ring_1", "ring_2"],
            "amulet": ["amulet"],
            "helmet": ["head"],
            "gloves": ["hands"],
            "boots": ["feet"]
        }
        
        valid_slots = slot_mappings.get(self.item_type, [])
        return slot in valid_slots
    
    def get_ac_bonus(self) -> int:
        """Get the AC bonus this item provides (0 if none)."""
        return self.ac_bonus or 0
    
    def get_weight_pounds(self) -> float:
        """Get item weight in pounds."""
        return self.weight
    
    def get_description(self) -> str:
        """Get item description with basic stats."""
        desc = f"{self.name} ({self.item_type})"
        if self.weight > 0:
            desc += f" - {self.weight} lbs"
        if self.ac_bonus:
            desc += f" - AC +{self.ac_bonus}"
        if self.damage:
            desc += f" - {self.damage} {self.damage_type or ''} damage"
        if self.properties:
            desc += f" - Properties: {', '.join(self.properties)}"
        return desc
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for saving."""
        return {
            "name": self.name,
            "type": self.item_type,
            "weight": self.weight,
            "cost": self.cost,
            "description": self.description,
            "properties": self.properties or [],
            "ac_bonus": self.ac_bonus,
            "damage": self.damage,
            "damage_type": self.damage_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create item from dictionary data."""
        return cls(
            name=data["name"],
            item_type=data.get("type", "misc"),
            weight=data.get("weight", 0.0),
            cost=data.get("cost", 0),
            description=data.get("description", ""),
            properties=data.get("properties", []),
            ac_bonus=data.get("ac_bonus"),
            damage=data.get("damage"),
            damage_type=data.get("damage_type")
        )


class ItemLoader:
    """Loads item definitions from JSON files."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize with data directory path."""
        if data_dir is None:
            # Try to find the data directory relative to this file
            current_dir = Path(__file__).parent
            
            # Option 1: data directory in same parent as core (fantasy_rpg/data)
            parent_data_dir = current_dir.parent / "data"
            
            # Option 2: data directory in core (fantasy_rpg/core/data)
            core_data_dir = current_dir / "data"
            
            # Option 3: relative to working directory
            relative_data_dir = Path("fantasy_rpg/data")
            
            if parent_data_dir.exists():
                data_dir = parent_data_dir
            elif core_data_dir.exists():
                data_dir = core_data_dir
            elif relative_data_dir.exists():
                data_dir = relative_data_dir
            else:
                # Fallback - use parent data dir even if it doesn't exist yet
                data_dir = parent_data_dir
        
        self.data_dir = data_dir
        self._cache = {}
    
    def load_items(self) -> Dict[str, Item]:
        """Load all item definitions from items.json."""
        if 'items' not in self._cache:
            items_file = self.data_dir / "items.json"
            
            if not items_file.exists():
                print(f"Warning: {items_file} not found, using empty item list")
                self._cache['items'] = {}
                return self._cache['items']
            
            try:
                with open(items_file, 'r') as f:
                    data = json.load(f)
                
                items = {}
                for item_id, item_data in data.get("items", {}).items():
                    items[item_id] = Item.from_dict(item_data)
                
                self._cache['items'] = items
                print(f"Loaded {len(items)} items from {items_file}")
                
            except Exception as e:
                print(f"Error loading items from {items_file}: {e}")
                self._cache['items'] = {}
        
        return self._cache['items']
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get a specific item by ID."""
        items = self.load_items()
        return items.get(item_id)
    
    def get_items_by_type(self, item_type: str) -> List[Item]:
        """Get all items of a specific type."""
        items = self.load_items()
        return [item for item in items.values() if item.item_type == item_type]


# Utility functions for creating common items
def create_item(name: str, item_type: str, weight: float, **kwargs) -> Item:
    """Create a basic item with the given properties."""
    item = Item(
        name=name,
        item_type=item_type,
        weight=weight,
        cost=kwargs.get('cost', 0),
        description=kwargs.get('description', ''),
        properties=kwargs.get('properties', []),
        ac_bonus=kwargs.get('ac_bonus'),
        damage=kwargs.get('damage'),
        damage_type=kwargs.get('damage_type')
    )
    print(f"Created item: {item.get_description()}")
    return item


def create_weapon(name: str, damage: str, damage_type: str, weight: float, **kwargs) -> Item:
    """Create a weapon item."""
    return create_item(
        name=name,
        item_type="weapon",
        weight=weight,
        damage=damage,
        damage_type=damage_type,
        **kwargs
    )


def create_armor(name: str, ac_bonus: int, weight: float, **kwargs) -> Item:
    """Create an armor item."""
    return create_item(
        name=name,
        item_type="armor",
        weight=weight,
        ac_bonus=ac_bonus,
        **kwargs
    )


def create_shield(name: str, ac_bonus: int, weight: float, **kwargs) -> Item:
    """Create a shield item."""
    return create_item(
        name=name,
        item_type="shield",
        weight=weight,
        ac_bonus=ac_bonus,
        **kwargs
    )


# Manual testing function
def test_item_system():
    """Test item creation and functionality."""
    print("=== Testing Item System ===")
    
    # Test basic item creation
    print("\n1. Testing basic item creation:")
    sword = create_weapon("Test Sword", "1d8", "slashing", 3.0, cost=15, properties=["versatile"])
    print(f"Created: {sword.get_description()}")
    
    armor = create_armor("Test Armor", 6, 55.0, cost=75)
    print(f"Created: {armor.get_description()}")
    
    shield = create_shield("Test Shield", 2, 6.0, cost=10)
    print(f"Created: {shield.get_description()}")
    
    # Test item properties
    print("\n2. Testing item properties:")
    print(f"Sword is weapon: {sword.is_weapon()}")
    print(f"Sword is armor: {sword.is_armor()}")
    print(f"Sword has versatile: {sword.has_property('versatile')}")
    print(f"Armor AC bonus: {armor.get_ac_bonus()}")
    print(f"Shield weight: {shield.get_weight_pounds()} lbs")
    
    # Test equipment slot compatibility
    print("\n3. Testing equipment slots:")
    print(f"Sword can equip to main_hand: {sword.can_equip_to('main_hand')}")
    print(f"Sword can equip to body: {sword.can_equip_to('body')}")
    print(f"Armor can equip to body: {armor.can_equip_to('body')}")
    print(f"Shield can equip to off_hand: {shield.can_equip_to('off_hand')}")
    
    # Test item loader
    print("\n4. Testing item loader:")
    loader = ItemLoader()
    items = loader.load_items()
    print(f"Loaded {len(items)} items from JSON")
    
    if items:
        for item_id, item in items.items():
            print(f"  {item_id}: {item.get_description()}")
    
    # Test specific item loading
    chain_mail = loader.get_item("chain_mail")
    if chain_mail:
        print(f"\nLoaded chain mail: {chain_mail.get_description()}")
        print(f"Chain mail properties: {chain_mail.properties}")
    
    # Test serialization
    print("\n5. Testing serialization:")
    sword_dict = sword.to_dict()
    print(f"Sword as dict: {sword_dict}")
    
    sword_copy = Item.from_dict(sword_dict)
    print(f"Sword copy: {sword_copy.get_description()}")
    
    print("✓ All item tests completed!")
    return items


if __name__ == "__main__":
    test_item_system()