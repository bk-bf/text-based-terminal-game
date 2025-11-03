"""
Fantasy RPG - Item System

Item base class and related functionality for equipment and inventory management.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
from fantasy_rpg.utils.data_loader import DataLoader


@dataclass
class Item:
    """
    Unified item class for all items in the game.
    
    Handles weight, properties, quantity tracking, and basic item functionality
    for equipment, consumables, and other items. This is the single source of
    truth for all item representations (previously Item, InventoryItem, GameItem).
    """
    name: str
    item_type: str  # 'weapon', 'armor', 'shield', 'consumable', etc.
    weight: float
    value: int = 0
    item_id: str = ""  # Unique identifier (auto-generated from name if empty)
    quantity: int = 1  # Quantity for stacking
    description: str = ""
    properties: Optional[List[str]] = None
    pools: Optional[List[str]] = None  # Pool tags for spawning/drops
    drop_weight: int = 1  # Weight for drop calculations
    
    # Equipment-specific attributes (None for non-equipment items)
    ac_bonus: Optional[int] = None
    armor_type: Optional[str] = None  # 'light', 'medium', 'heavy'
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    equippable: bool = False
    slot: Optional[str] = None
    magical: bool = False
    enchantment_bonus: int = 0
    special_properties: Optional[List[str]] = None
    
    # Container properties
    capacity_bonus: float = 0.0  # Additional carrying capacity for containers
    
    def __post_init__(self):
        """Initialize empty lists if not provided and set item_id."""
        if self.properties is None:
            self.properties = []
        if self.pools is None:
            self.pools = []
        if self.special_properties is None:
            self.special_properties = []
        # Auto-generate item_id from name if not provided
        if not self.item_id:
            self.item_id = self.name.lower().replace(" ", "_")
    
    def get_total_weight(self) -> float:
        """Get total weight for this stack of items"""
        return self.weight * self.quantity
    
    def get_total_value(self) -> int:
        """Get total value for this stack of items"""
        return self.value * self.quantity
    
    def can_stack_with(self, other: 'Item') -> bool:
        """Check if this item can stack with another item"""
        # Items can stack if they have the same ID and are stackable
        return (self.item_id == other.item_id and 
                self.is_stackable() and 
                other.is_stackable())
    
    def is_stackable(self) -> bool:
        """Check if this item type can be stacked"""
        # Consumables, ammunition, tools, and materials can typically stack
        stackable_types = ['consumable', 'ammunition', 'tool', 'component', 'material']
        return self.item_type in stackable_types
    
    def split(self, quantity: int) -> Optional['Item']:
        """Split this stack, returning a new Item with the specified quantity"""
        if quantity <= 0 or quantity >= self.quantity:
            return None
        
        # Create new item with split quantity (copying all attributes)
        split_item = Item(
            item_id=self.item_id,
            name=self.name,
            item_type=self.item_type,
            weight=self.weight,
            value=self.value,
            quantity=quantity,
            description=self.description,
            properties=self.properties.copy() if self.properties else [],
            pools=self.pools.copy() if self.pools else [],
            drop_weight=self.drop_weight,
            equippable=self.equippable,
            slot=self.slot,
            ac_bonus=self.ac_bonus,
            armor_type=self.armor_type,
            damage_dice=self.damage_dice,
            damage_type=self.damage_type,
            magical=self.magical,
            enchantment_bonus=self.enchantment_bonus,
            special_properties=self.special_properties.copy() if self.special_properties else [],
            capacity_bonus=self.capacity_bonus
        )
        
        # Reduce this item's quantity
        self.quantity -= quantity
        
        return split_item
    
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
    
    def can_equip_to_slot(self, slot: str) -> bool:
        """Check if this item can be equipped to the specified slot (alias for equipment.py compatibility)"""
        if not self.equippable:
            return False
        
        # Handle special cases
        if self.slot == 'ring' and slot in ['ring_1', 'ring_2']:
            return True
        if self.slot == 'hand' and slot in ['main_hand', 'off_hand']:
            return True
        if self.slot == 'body' and slot in ['body', 'armor']:
            return True
        
        return self.slot == slot
    
    def get_ac_contribution(self, character=None) -> int:
        """Calculate AC contribution from this item"""
        base_ac = 0
        
        if self.item_type == 'armor':
            if self.armor_type == 'light':
                # Light armor: armor AC + full DEX modifier (including magical bonuses)
                dex_mod = character.get_effective_ability_modifier('dexterity') if character else 0
                base_ac = (self.ac_bonus or 0) + dex_mod
            elif self.armor_type == 'medium':
                # Medium armor: armor AC + DEX modifier (max 2, including magical bonuses)
                dex_mod = min(2, character.get_effective_ability_modifier('dexterity')) if character else 0
                base_ac = (self.ac_bonus or 0) + dex_mod
            elif self.armor_type == 'heavy':
                # Heavy armor: armor AC only
                base_ac = self.ac_bonus or 0
        elif self.item_type == 'shield':
            # Shield adds to AC
            base_ac = self.ac_bonus or 0
        elif self.item_type == 'accessory':
            # Accessories (rings, amulets) provide AC bonuses from ac_bonus field only
            # enchantment_bonus is used for other bonuses (saves, etc.)
            base_ac = self.ac_bonus or 0
        
        # Add magical enhancement bonus for armor only (weapons handle this differently)
        if self.magical and self.enchantment_bonus > 0 and self.item_type == 'armor':
            base_ac += self.enchantment_bonus
        
        return base_ac
    
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
        if self.value > 0:
            desc += f" - ${self.value}"
        if self.ac_bonus:
            desc += f" - AC +{self.ac_bonus}"
        if self.damage_dice:
            desc += f" - {self.damage_dice} {self.damage_type or ''} damage"
        if self.magical:
            desc += f" - Magical"
            if self.enchantment_bonus > 0:
                desc += f" +{self.enchantment_bonus}"
        if self.special_properties:
            desc += f" - Properties: {', '.join(self.special_properties)}"
        return desc
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for saving."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "type": self.item_type,
            "weight": self.weight,
            "value": self.value,
            "quantity": self.quantity,
            "description": self.description,
            "properties": self.properties or [],
            "pools": self.pools or [],
            "drop_weight": self.drop_weight,
            "ac_bonus": self.ac_bonus,
            "armor_type": self.armor_type,
            "damage_dice": self.damage_dice,
            "damage_type": self.damage_type,
            "equippable": self.equippable,
            "slot": self.slot,
            "magical": self.magical,
            "enchantment_bonus": self.enchantment_bonus,
            "special_properties": self.special_properties or [],
            "capacity_bonus": self.capacity_bonus
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create item from dictionary data."""
        return cls(
            item_id=data.get("item_id", ""),
            name=data["name"],
            item_type=data.get("type", "misc"),
            weight=data.get("weight", 0.0),
            value=data.get("value", 0),
            quantity=data.get("quantity", 1),
            description=data.get("description", ""),
            properties=data.get("properties", []),
            pools=data.get("pools", []),
            drop_weight=data.get("drop_weight", 1),
            ac_bonus=data.get("ac_bonus"),
            armor_type=data.get("armor_type"),
            damage_dice=data.get("damage_dice"),
            damage_type=data.get("damage_type"),
            equippable=data.get("equippable", False),
            slot=data.get("slot"),
            magical=data.get("magical", False),
            enchantment_bonus=data.get("enchantment_bonus", 0),
            special_properties=data.get("special_properties", []),
            capacity_bonus=data.get("capacity_bonus", 0.0)
        )


class ItemLoader(DataLoader):
    """Loads item definitions from JSON files."""
    
    def load_items(self) -> Dict[str, Item]:
        """Load all item definitions from items.json."""
        cache_key = 'items'
        
        if cache_key not in self._cache:
            try:
                data = self.load_json("items.json")
                
                items = {}
                for item_id, item_data in data.get("items", {}).items():
                    items[item_id] = Item.from_dict(item_data)
                
                self._cache[cache_key] = items
                print(f"Loaded {len(items)} items from {self.data_dir / 'items.json'}")
                
            except FileNotFoundError:
                print(f"Warning: items.json not found in {self.data_dir}, using empty item list")
                self._cache[cache_key] = {}
            except Exception as e:
                print(f"Error loading items from {self.data_dir / 'items.json'}: {e}")
                self._cache[cache_key] = {}
        
        return self._cache[cache_key]
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get a specific item by ID."""
        items = self.load_items()
        return items.get(item_id)
    
    def get_items_by_type(self, item_type: str) -> List[Item]:
        """Get all items of a specific type."""
        items = self.load_items()
        return [item for item in items.values() if item.item_type == item_type]
    
    def get_items_by_pool(self, pool_name: str) -> List[Item]:
        """Get all items that belong to a specific pool."""
        items = self.load_items()
        return [item for item in items.values() if pool_name in (item.pools or [])]
    
    def get_items_by_pools(self, pool_names: List[str]) -> List[Item]:
        """Get all items that belong to any of the specified pools."""
        items = self.load_items()
        result = []
        for item in items.values():
            if item.pools and any(pool in item.pools for pool in pool_names):
                result.append(item)
        return result


# Utility functions for creating common items
def create_item(name: str, item_type: str, weight: float, **kwargs) -> Item:
    """Create a basic item with the given properties."""
    item = Item(
        name=name,
        item_type=item_type,
        weight=weight,
        value=kwargs.get('value', kwargs.get('cost', 0)),  # Support both value and legacy cost
        description=kwargs.get('description', ''),
        properties=kwargs.get('properties', []),
        pools=kwargs.get('pools', []),
        drop_weight=kwargs.get('drop_weight', 1),
        ac_bonus=kwargs.get('ac_bonus'),
        armor_type=kwargs.get('armor_type'),
        damage_dice=kwargs.get('damage_dice', kwargs.get('damage')),  # Support both names
        damage_type=kwargs.get('damage_type'),
        equippable=kwargs.get('equippable', True),
        slot=kwargs.get('slot'),
        magical=kwargs.get('magical', False),
        enchantment_bonus=kwargs.get('enchantment_bonus', 0),
        special_properties=kwargs.get('special_properties', []),
        capacity_bonus=kwargs.get('capacity_bonus', 0.0)
    )
    print(f"Created item: {item.get_description()}")
    return item


def create_weapon(name: str, damage: str, damage_type: str, weight: float, **kwargs) -> Item:
    """Create a weapon item."""
    return create_item(
        name=name,
        item_type="weapon",
        weight=weight,
        damage_dice=damage,
        damage_type=damage_type,
        equippable=True,
        slot="hand",
        **kwargs
    )


def create_armor(name: str, ac_bonus: int, weight: float, **kwargs) -> Item:
    """Create an armor item."""
    return create_item(
        name=name,
        item_type="armor",
        weight=weight,
        ac_bonus=ac_bonus,
        equippable=True,
        slot="body",
        **kwargs
    )


def create_shield(name: str, ac_bonus: int, weight: float, **kwargs) -> Item:
    """Create a shield item."""
    return create_item(
        name=name,
        item_type="shield",
        weight=weight,
        ac_bonus=ac_bonus,
        equippable=True,
        slot="off_hand",
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