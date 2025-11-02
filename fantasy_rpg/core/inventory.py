"""
Fantasy RPG - Inventory System

Inventory management with weight tracking, item stacking, and encumbrance limits.
Uses the unified Item class from core.item.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from collections import defaultdict
import json
from pathlib import Path

# Import unified Item class
from .item import Item


@dataclass
class Inventory:
    """Character inventory with weight tracking and encumbrance"""
    
    items: List[Item] = field(default_factory=list)
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
    
    def add_item(self, item: Item) -> bool:
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
    
    def remove_item(self, item_id: str, quantity: int = 1) -> Optional[Item]:
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
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item from inventory by ID"""
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory contains at least the specified quantity of an item"""
        item = self.get_item(item_id)
        return item is not None and item.quantity >= quantity
    
    def get_items_by_type(self, item_type: str) -> List[Item]:
        """Get all items of a specific type"""
        return [item for item in self.items if item.item_type == item_type]
    
    def get_equippable_items(self) -> List[Item]:
        """Get all equippable items"""
        return [item for item in self.items if item.equippable]
    
    def get_consumable_items(self) -> List[Item]:
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
            item = Item.from_dict(item_data)
            inventory.items.append(item)
        
        return inventory


class InventoryManager:
    """Helper class to manage inventory operations with ItemLoader integration"""
    
    def __init__(self, item_loader=None):
        """Initialize with optional ItemLoader"""
        if item_loader is None:
            try:
                from .item import ItemLoader
            except ImportError:
                # Handle direct execution (python inventory.py)
                from item import ItemLoader
            self.item_loader = ItemLoader()
        else:
            self.item_loader = item_loader
    
    def create_inventory_item_from_id(self, item_id: str, quantity: int = 1) -> Optional[Item]:
        """Create an Item from an item ID using ItemLoader"""
        item = self.item_loader.get_item(item_id)
        if not item:
            print(f"Warning: Item '{item_id}' not found in item database")
            return None
        
        # Create a copy with the specified quantity
        # The item from ItemLoader already has all the fields we need
        item.item_id = item_id
        item.quantity = quantity
        return item
    
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
