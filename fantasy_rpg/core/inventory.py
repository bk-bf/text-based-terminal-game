"""
Fantasy RPG - Inventory System

Inventory management with weight tracking, item stacking, and encumbrance limits.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from collections import defaultdict
import json
from pathlib import Path


@dataclass
class InventoryItem:
    """Represents an item in inventory with quantity and metadata"""
    item_id: str
    name: str
    item_type: str
    weight: float
    value: int
    quantity: int = 1
    description: str = ""
    properties: List[str] = field(default_factory=list)
    
    # Equipment-specific attributes (None for non-equipment items)
    equippable: bool = False
    slot: Optional[str] = None
    ac_bonus: int = 0
    armor_type: Optional[str] = None  # 'light', 'medium', 'heavy'
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    
    # Magical properties
    magical: bool = False
    enchantment_bonus: int = 0
    special_properties: List[str] = field(default_factory=list)
    
    # Container properties
    capacity_bonus: float = 0.0  # Additional carrying capacity for containers
    
    def get_total_weight(self) -> float:
        """Get total weight for this stack of items"""
        return self.weight * self.quantity
    
    def get_total_value(self) -> int:
        """Get total value for this stack of items"""
        return self.value * self.quantity
    
    def can_stack_with(self, other: 'InventoryItem') -> bool:
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
    
    def split(self, quantity: int) -> Optional['InventoryItem']:
        """Split this stack, returning a new InventoryItem with the specified quantity"""
        if quantity <= 0 or quantity >= self.quantity:
            return None
        
        # Create new item with split quantity
        split_item = InventoryItem(
            item_id=self.item_id,
            name=self.name,
            item_type=self.item_type,
            weight=self.weight,
            value=self.value,
            quantity=quantity,
            description=self.description,
            properties=self.properties.copy(),
            equippable=self.equippable,
            slot=self.slot,
            ac_bonus=self.ac_bonus,
            armor_type=self.armor_type,
            damage_dice=self.damage_dice,
            damage_type=self.damage_type,
            magical=self.magical,
            enchantment_bonus=self.enchantment_bonus,
            special_properties=self.special_properties.copy(),
            capacity_bonus=self.capacity_bonus
        )
        
        # Reduce this item's quantity
        self.quantity -= quantity
        
        return split_item
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving"""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'type': self.item_type,
            'weight': self.weight,
            'value': self.value,
            'quantity': self.quantity,
            'description': self.description,
            'properties': self.properties,
            'equippable': self.equippable,
            'slot': self.slot,
            'ac_bonus': self.ac_bonus,
            'armor_type': self.armor_type,
            'damage_dice': self.damage_dice,
            'damage_type': self.damage_type,
            'magical': self.magical,
            'enchantment_bonus': self.enchantment_bonus,
            'special_properties': self.special_properties,
            'capacity_bonus': self.capacity_bonus
        }
    
    def to_item(self):
        """Convert InventoryItem to Item object for equipment system"""
        # Import from item.py - now the single source of truth
        try:
            from .item import Item
        except ImportError:
            from item import Item
        
        return Item(
            name=self.name,
            item_type=self.item_type,
            weight=self.weight,
            value=self.value,
            description=self.description,
            properties=self.properties,
            pools=[],  # Not needed for equipped items
            drop_weight=1,
            ac_bonus=self.ac_bonus,
            armor_type=self.armor_type,
            damage_dice=self.damage_dice,
            damage_type=self.damage_type,
            equippable=self.equippable,
            slot=self.slot,
            magical=self.magical,
            enchantment_bonus=self.enchantment_bonus,
            special_properties=self.special_properties,
            capacity_bonus=self.capacity_bonus
        )
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InventoryItem':
        """Create from dictionary data"""
        return cls(
            item_id=data['item_id'],
            name=data['name'],
            item_type=data.get('type', 'misc'),
            weight=data.get('weight', 0.0),
            value=data.get('value', 0),
            quantity=data.get('quantity', 1),
            description=data.get('description', ''),
            properties=data.get('properties', []),
            equippable=data.get('equippable', False),
            slot=data.get('slot'),
            ac_bonus=data.get('ac_bonus', 0),
            armor_type=data.get('armor_type'),
            damage_dice=data.get('damage_dice'),
            damage_type=data.get('damage_type'),
            magical=data.get('magical', False),
            enchantment_bonus=data.get('enchantment_bonus', 0),
            special_properties=data.get('special_properties', []),
            capacity_bonus=data.get('capacity_bonus', 0.0)
        )


@dataclass
class Inventory:
    """Character inventory with weight tracking and encumbrance"""
    
    items: List[InventoryItem] = field(default_factory=list)
    max_weight: float = 150.0  # Default carrying capacity in pounds
    
    def __post_init__(self):
        """Initialize inventory"""
        pass
    
    def __len__(self) -> int:
        """Return the number of item stacks in inventory"""
        return len(self.items)
    
    def get_total_weight(self) -> float:
        """Calculate total weight of all items in inventory"""
        return sum(item.get_total_weight() for item in self.items)
    
    def get_total_value(self) -> int:
        """Calculate total value of all items in inventory"""
        return sum(item.get_total_value() for item in self.items)
    
    def get_remaining_capacity(self) -> float:
        """Get remaining weight capacity"""
        return max(0, self.max_weight - self.get_total_weight())
    
    def is_overencumbered(self) -> bool:
        """Check if inventory exceeds weight limit"""
        return self.get_total_weight() > self.max_weight
    
    def get_encumbrance_level(self) -> str:
        """Get encumbrance level description"""
        current_weight = self.get_total_weight()
        capacity = self.max_weight
        
        if current_weight <= capacity * 0.33:
            return "Light"
        elif current_weight <= capacity * 0.66:
            return "Medium"
        elif current_weight <= capacity:
            return "Heavy"
        else:
            return "Overencumbered"
    
    def can_add_item(self, item_id: str, quantity: int = 1, weight_per_item: float = 0.0) -> bool:
        """Check if an item can be added without exceeding weight limit"""
        additional_weight = weight_per_item * quantity
        return (self.get_total_weight() + additional_weight) <= self.max_weight
    
    def add_item(self, item: InventoryItem) -> bool:
        """Add an item to inventory, stacking if possible"""
        # Check weight limit
        if not self.can_add_item(item.item_id, item.quantity, item.weight):
            print(f"Cannot add {item.name}: would exceed weight limit")
            return False
        
        # Try to stack with existing items
        if item.is_stackable():
            for existing_item in self.items:
                if existing_item.can_stack_with(item):
                    existing_item.quantity += item.quantity
                    print(f"Stacked {item.quantity} {item.name} (total: {existing_item.quantity})")
                    return True
            # Debug: Why didn't it stack?
            for existing_item in self.items:
                if existing_item.item_id == item.item_id:
                    print(f"DEBUG: Found matching item_id '{item.item_id}' but couldn't stack:")
                    print(f"  New item stackable: {item.is_stackable()} (type: {item.item_type})")
                    print(f"  Existing item stackable: {existing_item.is_stackable()} (type: {existing_item.item_type})")
                    break
        else:
            print(f"DEBUG: Item '{item.name}' is not stackable (type: {item.item_type})")
        
        # Add as new item
        self.items.append(item)
        print(f"Added {item.quantity} {item.name} to inventory")
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> Optional[InventoryItem]:
        """Remove an item from inventory"""
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                if quantity >= item.quantity:
                    # Remove entire stack
                    removed_item = self.items.pop(i)
                    print(f"Removed {removed_item.quantity} {removed_item.name} from inventory")
                    return removed_item
                else:
                    # Split the stack
                    removed_item = item.split(quantity)
                    if removed_item:
                        print(f"Removed {quantity} {item.name} from inventory ({item.quantity} remaining)")
                        return removed_item
        
        print(f"Item {item_id} not found in inventory")
        return None
    
    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get an item from inventory by ID"""
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory contains at least the specified quantity of an item"""
        item = self.get_item(item_id)
        return item is not None and item.quantity >= quantity
    
    def get_items_by_type(self, item_type: str) -> List[InventoryItem]:
        """Get all items of a specific type"""
        return [item for item in self.items if item.item_type == item_type]
    
    def get_equippable_items(self) -> List[InventoryItem]:
        """Get all equippable items"""
        return [item for item in self.items if item.equippable]
    
    def get_consumable_items(self) -> List[InventoryItem]:
        """Get all consumable items"""
        return self.get_items_by_type('consumable')
    
    def sort_items(self, sort_by: str = 'name'):
        """Sort inventory items"""
        if sort_by == 'name':
            self.items.sort(key=lambda x: x.name.lower())
        elif sort_by == 'type':
            self.items.sort(key=lambda x: (x.item_type, x.name.lower()))
        elif sort_by == 'weight':
            self.items.sort(key=lambda x: x.weight, reverse=True)
        elif sort_by == 'value':
            self.items.sort(key=lambda x: x.value, reverse=True)
        
        print(f"Inventory sorted by {sort_by}")
    
    def display_inventory(self, show_details: bool = False) -> str:
        """Generate a formatted display of inventory contents"""
        if not self.items:
            return "Inventory is empty."
        
        lines = ["=== Inventory ==="]
        
        # Group items by type for better organization
        items_by_type = defaultdict(list)
        for item in self.items:
            items_by_type[item.item_type].append(item)
        
        # Display items by type
        for item_type in sorted(items_by_type.keys()):
            lines.append(f"\n{item_type.title()}:")
            for item in items_by_type[item_type]:
                quantity_str = f" x{item.quantity}" if item.quantity > 1 else ""
                weight_str = f" ({item.get_total_weight():.1f} lbs)" if item.weight > 0 else ""
                value_str = f" [{item.get_total_value()} gp]" if item.value > 0 else ""
                
                line = f"  • {item.name}{quantity_str}{weight_str}{value_str}"
                
                if show_details:
                    if item.description:
                        line += f"\n    {item.description}"
                    if item.special_properties:
                        line += f"\n    Properties: {', '.join(item.special_properties)}"
                
                lines.append(line)
        
        # Add summary
        lines.append("")
        lines.append(f"Total Items: {len(self.items)} stacks ({sum(item.quantity for item in self.items)} individual items)")
        lines.append(f"Total Weight: {self.get_total_weight():.1f} / {self.max_weight:.1f} lbs")
        lines.append(f"Total Value: {self.get_total_value()} gp")
        lines.append(f"Encumbrance: {self.get_encumbrance_level()}")
        
        if self.is_overencumbered():
            lines.append("⚠️  OVERENCUMBERED - Movement speed reduced!")
        
        return "\n".join(lines)
    
    def update_carrying_capacity(self, strength_score: int):
        """Update carrying capacity based on Strength score"""
        # D&D 5e: Carrying capacity = Strength score × 15 pounds
        self.max_weight = strength_score * 15.0
        print(f"Carrying capacity updated to {self.max_weight} lbs (STR {strength_score})")
    
    def to_dict(self) -> Dict:
        """Convert inventory to dictionary for saving"""
        return {
            'items': [item.to_dict() for item in self.items],
            'max_weight': self.max_weight
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Inventory':
        """Create inventory from dictionary data"""
        inventory = cls(max_weight=data.get('max_weight', 150.0))
        
        for item_data in data.get('items', []):
            item = InventoryItem.from_dict(item_data)
            inventory.items.append(item)
        
        return inventory


# Manual testing function
def test_inventory_system():
    """Test the inventory system with weight tracking"""
    print("=== Testing Inventory System ===")
    
    # Create inventory
    inventory = Inventory(max_weight=100.0)  # 100 lb capacity for testing
    
    print(f"Created inventory with {inventory.max_weight} lb capacity")
    print(f"Initial weight: {inventory.get_total_weight()} lbs")
    print(f"Encumbrance level: {inventory.get_encumbrance_level()}")
    
    # Create test items
    print(f"\n--- Creating Test Items ---")
    
    # Heavy item
    sword = InventoryItem(
        item_id="longsword",
        name="Longsword",
        item_type="weapon",
        weight=3.0,
        value=15,
        equippable=True,
        slot="hand",
        damage_dice="1d8",
        damage_type="slashing"
    )
    
    # Stackable items
    arrows = InventoryItem(
        item_id="arrows",
        name="Arrows",
        item_type="ammunition",
        weight=0.05,  # 1 lb per 20 arrows
        value=1,
        quantity=20
    )
    
    potions = InventoryItem(
        item_id="healing_potion",
        name="Potion of Healing",
        item_type="consumable",
        weight=0.5,
        value=50,
        quantity=3
    )
    
    # Heavy armor
    plate_armor = InventoryItem(
        item_id="plate_armor",
        name="Plate Armor",
        item_type="armor",
        weight=65.0,
        value=1500,
        equippable=True,
        slot="body",
        ac_bonus=18
    )
    
    print(f"Created test items:")
    print(f"  • {sword.name}: {sword.weight} lbs")
    print(f"  • {arrows.name}: {arrows.get_total_weight()} lbs ({arrows.quantity} arrows)")
    print(f"  • {potions.name}: {potions.get_total_weight()} lbs ({potions.quantity} potions)")
    print(f"  • {plate_armor.name}: {plate_armor.weight} lbs")
    
    # Test adding items
    print(f"\n--- Testing Item Addition ---")
    
    success1 = inventory.add_item(sword)
    print(f"Add sword result: {success1}")
    
    success2 = inventory.add_item(arrows)
    print(f"Add arrows result: {success2}")
    
    success3 = inventory.add_item(potions)
    print(f"Add potions result: {success3}")
    
    print(f"\nCurrent weight: {inventory.get_total_weight():.1f} lbs")
    print(f"Encumbrance: {inventory.get_encumbrance_level()}")
    
    # Try to add heavy armor (should exceed capacity)
    print(f"\n--- Testing Weight Limit ---")
    success4 = inventory.add_item(plate_armor)
    print(f"Add plate armor result: {success4}")
    
    # Test stacking
    print(f"\n--- Testing Item Stacking ---")
    more_arrows = InventoryItem(
        item_id="arrows",
        name="Arrows",
        item_type="ammunition",
        weight=0.05,
        value=1,
        quantity=10
    )
    
    success5 = inventory.add_item(more_arrows)
    print(f"Add more arrows result: {success5}")
    
    # Display inventory
    print(f"\n--- Inventory Display ---")
    print(inventory.display_inventory())
    
    # Test item removal
    print(f"\n--- Testing Item Removal ---")
    removed = inventory.remove_item("arrows", 5)
    if removed:
        print(f"Removed: {removed.quantity} {removed.name}")
    
    print(f"\nAfter removal:")
    print(f"Current weight: {inventory.get_total_weight():.1f} lbs")
    
    # Test carrying capacity update
    print(f"\n--- Testing Carrying Capacity Update ---")
    inventory.update_carrying_capacity(18)  # Strong character
    print(f"New capacity: {inventory.max_weight} lbs")
    print(f"Encumbrance: {inventory.get_encumbrance_level()}")
    
    # Now try adding the plate armor again
    success6 = inventory.add_item(plate_armor)
    print(f"Add plate armor with higher capacity: {success6}")
    
    print(f"\nFinal inventory:")
    print(inventory.display_inventory())
    
    print("✓ Inventory system tests completed!")
    return inventory


if __name__ == "__main__":
    test_inventory_system()


class InventoryManager:
    """Helper class to manage inventory operations with ItemLoader integration"""
    
    def __init__(self, item_loader=None):
        """Initialize with optional ItemLoader"""
        if item_loader is None:
            try:
                from .equipment import ItemLoader
            except ImportError:
                # Handle direct execution (python inventory.py)
                from equipment import ItemLoader
            self.item_loader = ItemLoader()
        else:
            self.item_loader = item_loader
    
    def create_inventory_item_from_id(self, item_id: str, quantity: int = 1) -> Optional[InventoryItem]:
        """Create an InventoryItem from an item ID using ItemLoader"""
        item = self.item_loader.get_item(item_id)
        if not item:
            print(f"Warning: Item '{item_id}' not found in item database")
            return None
        
        return InventoryItem(
            item_id=item_id,
            name=item.name,
            item_type=item.item_type,
            weight=item.weight,
            value=item.value,
            quantity=quantity,
            description=item.description,
            properties=getattr(item, 'properties', []),
            equippable=item.equippable,
            slot=item.slot,
            ac_bonus=getattr(item, 'ac_bonus', 0) or 0,
            armor_type=getattr(item, 'armor_type', None),
            damage_dice=item.damage_dice,
            damage_type=item.damage_type,
            magical=item.magical,
            enchantment_bonus=item.enchantment_bonus,
            special_properties=item.special_properties or [],
            capacity_bonus=getattr(item, 'capacity_bonus', 0.0)
        )
    
    def add_item_by_id(self, inventory: Inventory, item_id: str, quantity: int = 1) -> bool:
        """Add an item to inventory by ID"""
        inventory_item = self.create_inventory_item_from_id(item_id, quantity)
        if inventory_item:
            return inventory.add_item(inventory_item)
        return False


def create_starting_inventory(character_class_name: str, strength_score: int = 10) -> Inventory:
    """Create a starting inventory for a character class"""
    inventory = Inventory()
    inventory.update_carrying_capacity(strength_score)
    
    manager = InventoryManager()
    
    # Define starting equipment by class
    starting_equipment = {
        'Fighter': [
            ('chain_mail', 1),
            ('shield', 1),
            ('longsword', 1),
            ('dagger', 2),
        ],
        'Rogue': [
            ('leather_armor', 1),
            ('shortsword', 2),
            ('thieves_tools', 1),
            ('dagger', 2),
        ],
        'Cleric': [
            ('scale_mail', 1),
            ('shield', 1),
            ('mace', 1),
            ('holy_symbol', 1),
        ],
        'Wizard': [
            ('dagger', 1),
            ('spellbook', 1),
            ('component_pouch', 1),
        ]
    }
    
    equipment_list = starting_equipment.get(character_class_name, [])
    
    print(f"Creating starting inventory for {character_class_name}:")
    for item_id, quantity in equipment_list:
        success = manager.add_item_by_id(inventory, item_id, quantity)
        if not success:
            print(f"  Warning: Could not add {item_id} x{quantity}")
    
    print(f"Starting inventory created with {inventory.get_total_weight():.1f} lbs")
    return inventory


# Manual test for integration
def test_inventory_integration():
    """Test inventory integration with existing systems"""
    print("=== Testing Inventory Integration ===")
    
    # Test ItemLoader integration
    print("\n1. Testing ItemLoader Integration:")
    manager = InventoryManager()
    
    # Create inventory and add items by ID
    inventory = Inventory(max_weight=200.0)
    
    success1 = manager.add_item_by_id(inventory, 'longsword', 1)
    success2 = manager.add_item_by_id(inventory, 'leather_armor', 1)
    success3 = manager.add_item_by_id(inventory, 'shield', 1)
    
    print(f"Added longsword: {success1}")
    print(f"Added leather armor: {success2}")
    print(f"Added shield: {success3}")
    
    print(f"\nInventory after adding items:")
    print(inventory.display_inventory())
    
    # Test starting inventory creation
    print(f"\n2. Testing Starting Inventory Creation:")
    fighter_inventory = create_starting_inventory('Fighter', strength_score=16)
    print(f"\nFighter starting inventory:")
    print(fighter_inventory.display_inventory())
    
    rogue_inventory = create_starting_inventory('Rogue', strength_score=14)
    print(f"\nRogue starting inventory:")
    print(rogue_inventory.display_inventory())
    
    print("✓ Integration tests completed!")


if __name__ == "__main__":
    test_inventory_system()
    print("\n" + "="*50 + "\n")
    test_inventory_integration()