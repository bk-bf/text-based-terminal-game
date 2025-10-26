"""
Fantasy RPG - Equipment System

Equipment management with 9 equipment slots and item definitions.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from pathlib import Path


@dataclass
class Item:
    """Base item class for all equipment and inventory items"""
    name: str
    item_type: str  # 'weapon', 'armor', 'shield', 'accessory', 'consumable', etc.
    description: str = ""
    weight: float = 0.0
    value: int = 0
    
    # Equipment properties
    equippable: bool = False
    slot: Optional[str] = None  # Which slot this item can be equipped to
    
    # Combat properties
    ac_bonus: int = 0
    armor_type: Optional[str] = None  # 'light', 'medium', 'heavy'
    damage_dice: Optional[str] = None  # '1d8', '2d6', etc.
    damage_type: Optional[str] = None  # 'slashing', 'piercing', 'bludgeoning'
    
    # Magical properties
    magical: bool = False
    enchantment_bonus: int = 0
    special_properties: List[str] = field(default_factory=list)
    
    # Container properties
    capacity_bonus: float = 0.0  # Additional carrying capacity for containers
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """Create Item from dictionary data"""
        return cls(
            name=data['name'],
            item_type=data['type'],
            description=data.get('description', ''),
            weight=data.get('weight', 0.0),
            value=data.get('value', 0),
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
    
    def can_equip_to_slot(self, slot: str) -> bool:
        """Check if this item can be equipped to the specified slot"""
        if not self.equippable:
            return False
        
        # Handle special cases
        if self.slot == 'ring' and slot in ['ring_1', 'ring_2']:
            return True
        if self.slot == 'hand' and slot in ['main_hand', 'off_hand']:
            return True
        
        return self.slot == slot
    
    def get_ac_contribution(self, character=None) -> int:
        """Calculate AC contribution from this item"""
        base_ac = 0
        
        if self.item_type == 'armor':
            if self.armor_type == 'light':
                # Light armor: armor AC + full DEX modifier (including magical bonuses)
                dex_mod = character.get_effective_ability_modifier('dexterity') if character else 0
                base_ac = self.ac_bonus + dex_mod
            elif self.armor_type == 'medium':
                # Medium armor: armor AC + DEX modifier (max 2, including magical bonuses)
                dex_mod = min(2, character.get_effective_ability_modifier('dexterity')) if character else 0
                base_ac = self.ac_bonus + dex_mod
            elif self.armor_type == 'heavy':
                # Heavy armor: armor AC only
                base_ac = self.ac_bonus
        elif self.item_type == 'shield':
            # Shield adds to AC
            base_ac = self.ac_bonus
        elif self.item_type == 'accessory':
            # Accessories (rings, amulets) provide AC bonuses from ac_bonus field only
            # enchantment_bonus is used for other bonuses (saves, etc.)
            base_ac = self.ac_bonus
        
        # Add magical enhancement bonus for armor only (weapons handle this differently)
        if self.magical and self.enchantment_bonus > 0 and self.item_type == 'armor':
            base_ac += self.enchantment_bonus
        
        return base_ac


@dataclass
class Equipment:
    """Character equipment system with 11 slots (including containers)"""
    
    # The 11 equipment slots
    head: Optional[Item] = None
    body: Optional[Item] = None
    hands: Optional[Item] = None
    feet: Optional[Item] = None
    main_hand: Optional[Item] = None
    off_hand: Optional[Item] = None
    ring_1: Optional[Item] = None
    ring_2: Optional[Item] = None
    amulet: Optional[Item] = None
    back: Optional[Item] = None  # For backpacks and containers
    waist: Optional[Item] = None  # For belt pouches and satchels
    
    def __post_init__(self):
        """Initialize slot mapping for easy access"""
        self._slots = {
            'head': 'head',
            'body': 'body', 
            'hands': 'hands',
            'feet': 'feet',
            'main_hand': 'main_hand',
            'off_hand': 'off_hand',
            'ring_1': 'ring_1',
            'ring_2': 'ring_2',
            'amulet': 'amulet',
            'back': 'back',
            'waist': 'waist'
        }
    
    def get_slot_names(self) -> List[str]:
        """Get list of all equipment slot names"""
        return list(self._slots.keys())
    
    def get_item_in_slot(self, slot: str) -> Optional[Item]:
        """Get the item equipped in a specific slot"""
        if slot not in self._slots:
            return None
        return getattr(self, slot)
    
    def equip_item(self, item: Item, slot: str, character=None) -> tuple[bool, str]:
        """Equip an item to a specific slot with comprehensive validation"""
        # Basic slot validation
        if slot not in self._slots:
            return False, f"Invalid slot: {slot}"
        
        # Item equippability validation
        if not item.equippable:
            return False, f"{item.name} is not equippable"
        
        if not item.can_equip_to_slot(slot):
            return False, f"Cannot equip {item.name} to {slot} slot (requires {item.slot} slot)"
        
        # Two-handed weapon validation
        if item.item_type == 'weapon' and 'two-handed' in item.special_properties:
            if slot == 'off_hand':
                return False, f"Two-handed weapons cannot be equipped in off-hand slot"
            # For main_hand, we'll auto-unequip off-hand later
        
        # Shield validation - can't use shield with two-handed weapon
        if item.item_type == 'shield' and slot == 'off_hand':
            main_hand = self.get_item_in_slot('main_hand')
            if main_hand and hasattr(main_hand, 'special_properties') and 'two-handed' in main_hand.special_properties:
                return False, f"Cannot equip shield: {main_hand.name} is a two-handed weapon"
        
        # Ring slot flexibility - allow equipping to either ring slot
        if item.slot == 'ring' and slot in ['ring_1', 'ring_2']:
            # Check if the specific slot is free, if not try the other ring slot
            if self.get_item_in_slot(slot):
                other_ring_slot = 'ring_2' if slot == 'ring_1' else 'ring_1'
                if not self.get_item_in_slot(other_ring_slot):
                    slot = other_ring_slot
                    print(f"Ring slot {slot.replace('_', ' ')} occupied, equipping to {other_ring_slot.replace('_', ' ')}")
                else:
                    return False, f"Both ring slots are occupied"
        # Armor type validation (character level requirements could be added here)
        if item.item_type == 'armor' and character:
            # Heavy armor requires strength (could add this validation)
            if item.armor_type == 'heavy':
                str_requirement = 13  # Example requirement
                if character.strength < str_requirement:
                    return False, f"Requires {str_requirement} Strength to wear {item.name}"
        
        # Unequip current item if any
        current_item = self.get_item_in_slot(slot)
        if current_item:
            print(f"Unequipping {current_item.name} from {slot}")
        
        # Handle two-handed weapon equipping - clear off-hand
        if item.item_type == 'weapon' and 'two-handed' in item.special_properties and slot == 'main_hand':
            off_hand_item = self.get_item_in_slot('off_hand')
            if off_hand_item:
                self.unequip_item('off_hand')
                print(f"Automatically unequipped {off_hand_item.name} from off-hand for two-handed weapon")
        
        # Equip new item
        setattr(self, slot, item)
        print(f"Equipped {item.name} to {slot} slot")
        return True, f"Successfully equipped {item.name}"
    
    def unequip_item(self, slot: str) -> tuple[Optional[Item], str]:
        """Unequip item from a specific slot with validation"""
        # Basic slot validation
        if slot not in self._slots:
            return None, f"Invalid slot: {slot}"
        
        item = self.get_item_in_slot(slot)
        if not item:
            return None, f"No item equipped in {slot} slot"
        
        # Unequip the item
        setattr(self, slot, None)
        print(f"Unequipped {item.name} from {slot}")
        return item, f"Successfully unequipped {item.name}"
    
    def can_equip_item(self, item: Item, slot: str, character=None) -> tuple[bool, str]:
        """Check if an item can be equipped without actually equipping it"""
        success, message = self.equip_item(item, slot, character)
        return success, message
    
    def swap_items(self, slot1: str, slot2: str) -> tuple[bool, str]:
        """Swap items between two slots"""
        if slot1 not in self._slots or slot2 not in self._slots:
            return False, "Invalid slot(s)"
        
        item1 = self.get_item_in_slot(slot1)
        item2 = self.get_item_in_slot(slot2)
        
        if not item1 and not item2:
            return False, "Both slots are empty"
        
        # Temporarily store items
        setattr(self, slot1, None)
        setattr(self, slot2, None)
        
        # Swap items
        if item1:
            setattr(self, slot2, item1)
        if item2:
            setattr(self, slot1, item2)
        
        print(f"Swapped items between {slot1} and {slot2}")
        return True, "Items swapped successfully"
    
    def get_equipped_items(self) -> Dict[str, Item]:
        """Get all currently equipped items"""
        equipped = {}
        for slot in self._slots:
            item = self.get_item_in_slot(slot)
            if item:
                equipped[slot] = item
        return equipped
    
    def calculate_total_ac_bonus(self, character=None) -> int:
        """Calculate total AC bonus from all equipped items"""
        total_ac = 0
        base_ac_set = False
        
        for slot, item in self.get_equipped_items().items():
            if item.item_type == 'armor':
                # Armor sets base AC, doesn't add to it
                if not base_ac_set:
                    total_ac = item.get_ac_contribution(character)
                    base_ac_set = True
            else:
                # Other items add to AC
                total_ac += item.get_ac_contribution(character)
        
        # If no armor equipped, use base AC (10 + DEX, including magical bonuses)
        if not base_ac_set and character:
            total_ac = 10 + character.get_effective_ability_modifier('dexterity')
        
        return total_ac
    
    def get_total_weight(self) -> float:
        """Calculate total weight of equipped items"""
        return sum(item.weight for item in self.get_equipped_items().values())
    
    def get_total_value(self) -> int:
        """Calculate total value of equipped items"""
        return sum(item.value for item in self.get_equipped_items().values())
    
    def get_attack_bonus(self, weapon_slot: str = 'main_hand') -> int:
        """Get attack bonus from equipped weapon"""
        weapon = self.get_item_in_slot(weapon_slot)
        if weapon and weapon.item_type == 'weapon':
            bonus = 0
            if weapon.magical and weapon.enchantment_bonus > 0:
                bonus += weapon.enchantment_bonus
            return bonus
        return 0
    
    def get_damage_bonus(self, weapon_slot: str = 'main_hand') -> int:
        """Get damage bonus from equipped weapon"""
        weapon = self.get_item_in_slot(weapon_slot)
        if weapon and weapon.item_type == 'weapon':
            bonus = 0
            if weapon.magical and weapon.enchantment_bonus > 0:
                bonus += weapon.enchantment_bonus
            return bonus
        return 0
    
    def get_saving_throw_bonus(self, ability: str = None) -> int:
        """Get saving throw bonuses from equipped items"""
        bonus = 0
        for item in self.get_equipped_items().values():
            if item.magical and 'protection' in item.special_properties:
                bonus += item.enchantment_bonus
        return bonus
    
    def get_skill_bonus(self, skill: str = None) -> int:
        """Get skill bonuses from equipped items"""
        bonus = 0
        for item in self.get_equipped_items().values():
            # Items could provide skill bonuses (e.g., Thieves' Tools for lockpicking)
            if skill and skill.lower() in [prop.lower() for prop in item.special_properties]:
                bonus += item.enchantment_bonus if item.magical else 1
        return bonus
    
    def get_ability_score_override(self, ability: str) -> Optional[int]:
        """Get ability score override from magical items (e.g., Gauntlets of Ogre Power)"""
        for item in self.get_equipped_items().values():
            if item.magical:
                for prop in item.special_properties:
                    if prop.startswith(f"{ability}_"):
                        try:
                            score = int(prop.split('_')[1])
                            return score
                        except (ValueError, IndexError):
                            continue
        return None
    
    def get_ability_score_bonus(self, ability: str) -> int:
        """Get ability score bonuses from magical items"""
        bonus = 0
        for item in self.get_equipped_items().values():
            if item.magical:
                for prop in item.special_properties:
                    if prop == f"{ability}_bonus" and item.enchantment_bonus > 0:
                        bonus += item.enchantment_bonus
        return bonus
    
    def get_equipped_weapons(self) -> List[Item]:
        """Get all equipped weapons"""
        weapons = []
        for item in self.get_equipped_items().values():
            if item.item_type == 'weapon':
                weapons.append(item)
        return weapons
    
    def has_shield_equipped(self) -> bool:
        """Check if a shield is equipped"""
        off_hand_item = self.get_item_in_slot('off_hand')
        return off_hand_item and off_hand_item.item_type == 'shield'
    
    def has_two_handed_weapon(self) -> bool:
        """Check if a two-handed weapon is equipped"""
        main_hand = self.get_item_in_slot('main_hand')
        return main_hand and 'two-handed' in main_hand.special_properties
    
    def get_capacity_bonus(self) -> float:
        """Get total carrying capacity bonus from equipped containers"""
        total_bonus = 0.0
        
        for item in self.get_equipped_items().values():
            if item.item_type == 'container':
                # Get capacity bonus from the item
                capacity_bonus = getattr(item, 'capacity_bonus', 0.0)
                if capacity_bonus > 0:
                    total_bonus += capacity_bonus
        
        return total_bonus
    
    def get_equipped_containers(self) -> List[Item]:
        """Get all equipped container items"""
        containers = []
        for item in self.get_equipped_items().values():
            if item.item_type == 'container':
                containers.append(item)
        return containers
    
    def display_equipment(self) -> str:
        """Generate a formatted display of equipped items"""
        lines = ["=== Equipment ==="]
        
        for slot in self._slots:
            item = self.get_item_in_slot(slot)
            slot_display = slot.replace('_', ' ').title()
            
            if item:
                lines.append(f"{slot_display:12}: {item.name}")
                if item.magical:
                    lines[-1] += f" +{item.enchantment_bonus}" if item.enchantment_bonus > 0 else ""
                if item.special_properties:
                    lines[-1] += f" ({', '.join(item.special_properties)})"
            else:
                lines.append(f"{slot_display:12}: (empty)")
        
        # Add summary
        equipped_items = self.get_equipped_items()
        if equipped_items:
            lines.append("")
            lines.append(f"Total Weight: {self.get_total_weight():.1f} lbs")
            lines.append(f"Total Value: {self.get_total_value()} gp")
        
        return "\n".join(lines)


class ItemLoader:
    """Loads item data from JSON files"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Try to find the data directory relative to this file
            current_dir = Path(__file__).parent
            if (current_dir / "data").exists():
                self.data_dir = current_dir / "data"
            elif (current_dir.parent / "fantasy_rpg" / "data").exists():
                self.data_dir = current_dir.parent / "fantasy_rpg" / "data"
            else:
                self.data_dir = Path("fantasy_rpg/data")
        else:
            self.data_dir = Path(data_dir)
        self._items_cache: Optional[Dict[str, Item]] = None
    
    def load_items(self) -> Dict[str, Item]:
        """Load all item definitions from items.json"""
        if self._items_cache is not None:
            return self._items_cache
        
        items_file = self.data_dir / "items.json"
        if not items_file.exists():
            print(f"Warning: {items_file} not found, using default items")
            return self._get_default_items()
        
        try:
            with open(items_file, 'r') as f:
                data = json.load(f)
            
            items = {}
            for item_key, item_data in data.get('items', {}).items():
                items[item_key] = Item.from_dict(item_data)
            
            print(f"Loaded {len(items)} items from {items_file}")
            self._items_cache = items
            return items
            
        except Exception as e:
            print(f"Error loading items from {items_file}: {e}")
            return self._get_default_items()
    
    def get_item(self, item_name: str) -> Optional[Item]:
        """Get a specific item by name (case-insensitive)"""
        items = self.load_items()
        item_key = item_name.lower().replace(' ', '_')
        return items.get(item_key)
    
    def _get_default_items(self) -> Dict[str, Item]:
        """Fallback default items if JSON file is missing"""
        leather_armor = Item(
            name="Leather Armor",
            item_type="armor",
            description="Basic leather armor",
            ac_bonus=11,
            armor_type="light",
            weight=10.0,
            value=10,
            equippable=True,
            slot="body"
        )
        
        longsword = Item(
            name="Longsword",
            item_type="weapon",
            description="A versatile sword",
            damage_dice="1d8",
            damage_type="slashing",
            weight=3.0,
            value=15,
            equippable=True,
            slot="main_hand",
            special_properties=["versatile"]
        )
        
        shield = Item(
            name="Shield",
            item_type="shield",
            description="A sturdy wooden shield",
            ac_bonus=2,
            weight=6.0,
            value=10,
            equippable=True,
            slot="off_hand"
        )
        
        return {
            "leather_armor": leather_armor,
            "longsword": longsword,
            "shield": shield
        }


# Manual testing function
def test_equipment_system():
    """Test the equipment system"""
    print("=== Testing Equipment System ===")
    
    # Create equipment instance
    equipment = Equipment()
    
    print(f"Equipment slots: {equipment.get_slot_names()}")
    print(f"Initial equipment:")
    print(equipment.display_equipment())
    
    # Load some items
    item_loader = ItemLoader()
    items = item_loader.load_items()
    print(f"\nAvailable items: {list(items.keys())}")
    
    # Test equipping items
    print(f"\n--- Testing Item Equipping ---")
    
    # Get some items to equip
    leather_armor = item_loader.get_item("leather_armor")
    longsword = item_loader.get_item("longsword")
    shield = item_loader.get_item("shield")
    
    if leather_armor:
        success, message = equipment.equip_item(leather_armor, "body")
        print(f"Equip leather armor: {message}")
    
    if longsword:
        success, message = equipment.equip_item(longsword, "main_hand")
        print(f"Equip longsword: {message}")
    
    if shield:
        success, message = equipment.equip_item(shield, "off_hand")
        print(f"Equip shield: {message}")
    
    print(f"\nAfter equipping items:")
    print(equipment.display_equipment())
    
    # Test unequipping
    print(f"\n--- Testing Item Unequipping ---")
    unequipped, message = equipment.unequip_item("off_hand")
    print(f"Unequip result: {message}")
    if unequipped:
        print(f"Unequipped: {unequipped.name}")
    
    print(f"\nAfter unequipping shield:")
    print(equipment.display_equipment())
    
    print("✓ Equipment system tests passed!")
    return equipment


if __name__ == "__main__":
    test_equipment_system()