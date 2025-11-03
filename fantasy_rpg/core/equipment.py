"""
Fantasy RPG - Equipment System

Equipment management with 9 equipment slots and item definitions.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# Import Item from item.py - single source of truth
from .item import Item, ItemLoader as BaseItemLoader


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
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize equipment to dictionary for saving"""
        return {
            slot: item.to_dict() if (item := self.get_item_in_slot(slot)) else None
            for slot in self._slots
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Equipment':
        """Deserialize equipment from dictionary when loading"""
        equipment = cls()
        
        if not data:
            return equipment
        
        for slot, item_data in data.items():
            if item_data and slot in equipment._slots:
                # Deserialize the item
                item = Item.from_dict(item_data)
                # Set it in the appropriate slot
                setattr(equipment, slot, item)
        
        return equipment


# ItemLoader is now just an alias to the one from item.py for backwards compatibility
ItemLoader = BaseItemLoader
