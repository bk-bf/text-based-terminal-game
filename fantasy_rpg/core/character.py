"""
Fantasy RPG - Character System

Character creation and management functionality.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
try:
    from .inventory import Inventory, InventoryItem, InventoryManager
except ImportError:
    # Handle running directly from core directory
    try:
        from inventory import Inventory, InventoryItem, InventoryManager
    except ImportError:
        # Create minimal stubs if inventory system not available
        class Inventory:
            def __init__(self): pass
        class InventoryItem:
            def __init__(self): pass
        class InventoryManager:
            def __init__(self): pass

# D&D 5e Experience Point Thresholds for levels 1-20
# Generated using the official D&D 5e XP progression formula
def _generate_xp_thresholds():
    """Generate XP thresholds for levels 1-20 using D&D 5e formula"""
    thresholds = {1: 0}  # Level 1 starts at 0 XP
    
    # D&D 5e XP progression follows this pattern:
    # Each level requires more XP, with specific jumps at certain levels
    xp_increments = [
        300,   # Level 2
        600,   # Level 3  
        1800,  # Level 4
        3800,  # Level 5
        7500,  # Level 6
        9000,  # Level 7
        11000, # Level 8
        14000, # Level 9
        16000, # Level 10
        21000, # Level 11
        15000, # Level 12
        20000, # Level 13
        20000, # Level 14
        25000, # Level 15
        30000, # Level 16
        30000, # Level 17
        40000, # Level 18
        40000, # Level 19
        50000  # Level 20
    ]
    
    current_xp = 0
    for level in range(2, 21):
        current_xp += xp_increments[level - 2]
        thresholds[level] = current_xp
    
    return thresholds

XP_THRESHOLDS = _generate_xp_thresholds()


@dataclass
class Character:
    """D&D 5e character implementation"""
    # Core D&D stats
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    
    # Derived stats
    level: int
    hp: int
    max_hp: int
    armor_class: int
    proficiency_bonus: int
    
    # Progression
    experience_points: int
    
    # Character identity
    name: str = ""
    race: str = ""
    character_class: str = ""
    background: str = ""
    
    # Equipment system - 9 equipment slots
    equipment: Optional[object] = None  # Will be Equipment instance
    
    # Inventory - carried items not equipped (new Inventory class)
    inventory: Optional[Inventory] = None
    

    
    # Skill proficiencies (will be initialized when needed)
    skill_proficiencies: Optional[object] = None
    
    # Feat support framework
    feats: List[str] = field(default_factory=list)
    
    # Movement speed (in feet, D&D standard)
    base_speed: int = 30  # Standard human speed
    
    def ability_modifier(self, ability: str) -> int:
        """Calculate D&D ability modifier: (score - 10) // 2"""
        base_score = getattr(self, ability)
        base_modifier = (base_score - 10) // 2
        
        # Apply condition effects if available
        condition_modifier = self.get_condition_modifier(ability)
        
        return base_modifier + condition_modifier
    
    def get_condition_modifier(self, ability: str) -> int:
        """Get condition-based modifier for an ability score"""
        if not hasattr(self, 'player_state') or not self.player_state:
            return 0
        
        try:
            from ..game.conditions import get_conditions_manager
            conditions_manager = get_conditions_manager()
            active_conditions = conditions_manager.evaluate_conditions(self.player_state)
            total_effects = conditions_manager.calculate_total_effects(active_conditions)
            
            return total_effects.get("ability_modifiers", {}).get(ability, 0)
        except (ImportError, Exception):
            return 0
    
    def get_effective_speed(self) -> int:
        """Calculate effective movement speed including condition penalties"""
        base_speed = self.base_speed
        
        # Apply condition-based movement penalties
        if not hasattr(self, 'player_state') or not self.player_state:
            return base_speed
        
        try:
            from ..game.conditions import get_conditions_manager
            conditions_manager = get_conditions_manager()
            active_conditions = conditions_manager.evaluate_conditions(self.player_state)
            total_effects = conditions_manager.calculate_total_effects(active_conditions)
            
            movement_penalty = total_effects.get("movement_penalty", 0.0)
            
            # Apply penalty as a fraction (0.5 = half speed, 0.75 = quarter speed lost)
            effective_speed = int(base_speed * (1.0 - movement_penalty))
            
            # Minimum speed of 5 feet (can't go below crawling speed)
            return max(5, effective_speed)
            
        except (ImportError, Exception):
            return base_speed
    
    def calculate_ac(self) -> int:
        """Calculate armor class from dexterity and equipment"""
        # Use new equipment system if available
        if self.equipment:
            return self.equipment.calculate_total_ac_bonus(self)
        
        # Fallback to old inventory system for backward compatibility
        base_ac = 10 + self.ability_modifier('dexterity')
        shield_bonus = 0
        
        # Check for armor and shield in inventory (simplified for now)
        # TODO: Implement proper equipment system for AC calculation
        # For now, just use base AC calculation
        
        return base_ac + shield_bonus
    
    def calculate_hp(self, character_class=None) -> int:
        """Calculate hit points based on level, class, and constitution"""
        if character_class:
            hit_die = character_class.hit_die
        else:
            # Default to d8 if no class provided
            hit_die = 8
        
        con_modifier = self.ability_modifier('constitution')
        
        if self.level == 1:
            # First level gets max hit die + CON modifier
            return hit_die + con_modifier
        else:
            # Subsequent levels: max at 1st + average for remaining levels
            first_level_hp = hit_die + con_modifier
            average_roll = (hit_die + 1) // 2  # Average of hit die
            additional_levels = self.level - 1
            additional_hp = additional_levels * (average_roll + con_modifier)
            return first_level_hp + additional_hp
    
    def calculate_proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on character level"""
        return 2 + ((self.level - 1) // 4)
    
    def recalculate_derived_stats(self, character_class=None):
        """Recalculate all derived stats (AC, HP, proficiency bonus)"""
        # Update proficiency bonus
        self.proficiency_bonus = self.calculate_proficiency_bonus()
        
        # Update HP
        old_max_hp = self.max_hp
        self.max_hp = self.calculate_hp(character_class)
        
        # If max HP increased, add the difference to current HP
        if self.max_hp > old_max_hp:
            hp_increase = self.max_hp - old_max_hp
            self.hp += hp_increase
        # If max HP decreased, ensure current HP doesn't exceed new max
        elif self.hp > self.max_hp:
            self.hp = self.max_hp
        
        # Update AC
        self.armor_class = self.calculate_ac()
        
        print(f"Recalculated derived stats for {self.name}:")
        print(f"  Level {self.level}: Proficiency +{self.proficiency_bonus}")
        print(f"  HP: {self.hp}/{self.max_hp}")
        print(f"  AC: {self.armor_class}")
    
    def get_xp_for_level(self, level: int) -> int:
        """Get the XP threshold for a specific level"""
        return XP_THRESHOLDS.get(level, XP_THRESHOLDS[20])
    
    def get_current_level_xp_threshold(self) -> int:
        """Get the XP threshold for the current level"""
        return self.get_xp_for_level(self.level)
    
    def get_next_level_xp_threshold(self) -> int:
        """Get the XP threshold for the next level"""
        return self.get_xp_for_level(self.level + 1)
    
    def get_xp_to_next_level(self) -> int:
        """Get the XP needed to reach the next level"""
        if self.level >= 20:
            return 0  # Max level reached
        return self.get_next_level_xp_threshold() - self.experience_points
    
    def can_level_up(self) -> bool:
        """Check if the character has enough XP to level up"""
        if self.level >= 20:
            return False  # Max level reached
        return self.experience_points >= self.get_next_level_xp_threshold()
    
    def add_experience(self, xp_amount: int, character_class=None) -> bool:
        """Add experience points and handle automatic leveling"""
        if xp_amount <= 0:
            print(f"Invalid XP amount: {xp_amount}")
            return False
        
        old_xp = self.experience_points
        old_level = self.level
        
        # Add the XP
        self.experience_points += xp_amount
        print(f"{self.name} gains {xp_amount} XP! ({old_xp} -> {self.experience_points})")
        
        # Check for level ups (can level multiple times if enough XP)
        leveled_up = False
        while self.can_level_up():
            self.level_up(character_class)
            leveled_up = True
        
        # Show XP progress if no level up occurred
        if not leveled_up and self.level < 20:
            xp_needed = self.get_xp_to_next_level()
            next_level_threshold = self.get_next_level_xp_threshold()
            print(f"  {xp_needed} XP needed for level {self.level + 1} (threshold: {next_level_threshold})")
        
        return leveled_up
    
    def level_up(self, character_class=None):
        """Handle level advancement"""
        old_level = self.level
        self.level += 1
        
        # Recalculate all derived stats
        self.recalculate_derived_stats(character_class)
        
        print(f"{self.name} leveled up from {old_level} to {self.level}!")
        
        # Show XP progress for next level
        if self.level < 20:
            xp_needed = self.get_xp_to_next_level()
            next_level_threshold = self.get_next_level_xp_threshold()
            print(f"  {xp_needed} XP needed for level {self.level + 1} (threshold: {next_level_threshold})")
    
    def get_xp_progress_info(self) -> dict:
        """Get detailed XP progress information"""
        if self.level >= 20:
            return {
                'current_level': self.level,
                'current_xp': self.experience_points,
                'current_level_threshold': self.get_current_level_xp_threshold(),
                'next_level_threshold': None,
                'xp_to_next_level': 0,
                'progress_percentage': 100.0,
                'max_level_reached': True
            }
        
        current_threshold = self.get_current_level_xp_threshold()
        next_threshold = self.get_next_level_xp_threshold()
        xp_in_current_level = self.experience_points - current_threshold
        xp_needed_for_level = next_threshold - current_threshold
        progress_percentage = (xp_in_current_level / xp_needed_for_level) * 100
        
        return {
            'current_level': self.level,
            'current_xp': self.experience_points,
            'current_level_threshold': current_threshold,
            'next_level_threshold': next_threshold,
            'xp_to_next_level': self.get_xp_to_next_level(),
            'xp_in_current_level': xp_in_current_level,
            'xp_needed_for_level': xp_needed_for_level,
            'progress_percentage': progress_percentage,
            'max_level_reached': False
        }
    
    def make_skill_check(self, skill_name: str, dc: int = 15, advantage: bool = False, disadvantage: bool = False) -> dict:
        """Make a skill check using the skill system"""
        # Import here to avoid circular imports
        try:
            from .skills import SkillSystem
        except ImportError:
            from fantasy_rpg.core.skills import SkillSystem
        return SkillSystem.make_skill_check(self, skill_name, dc, advantage, disadvantage)
    
    def get_skill_modifier(self, skill_name: str) -> int:
        """Get the total modifier for a skill"""
        try:
            from .skills import SkillSystem
        except ImportError:
            from fantasy_rpg.core.skills import SkillSystem
        return SkillSystem.calculate_skill_modifier(self, skill_name)
    
    def calculate_saving_throw_modifier(self, ability: str, character_class=None) -> int:
        """Calculate saving throw modifier for an ability"""
        base_modifier = self.ability_modifier(ability)
        
        # Check if proficient in this saving throw
        if character_class and character_class.is_proficient_in_saving_throw(ability):
            return base_modifier + self.proficiency_bonus
        else:
            return base_modifier
    
    def make_saving_throw(self, ability: str, dc: int = 15, character_class=None, advantage: bool = False, disadvantage: bool = False) -> dict:
        """Make a saving throw"""
        try:
            from ..utils.utils import roll_d20
        except ImportError:
            from fantasy_rpg.utils.utils import roll_d20
        
        # Calculate modifier
        modifier = self.calculate_saving_throw_modifier(ability, character_class)
        
        # Roll d20 with advantage/disadvantage
        roll_result = roll_d20(advantage=advantage, disadvantage=disadvantage)
        total = roll_result + modifier
        
        # Determine success
        success = total >= dc
        
        # Format proficiency status
        is_proficient = character_class and character_class.is_proficient_in_saving_throw(ability) if character_class else False
        proficiency_text = " (proficient)" if is_proficient else ""
        
        # Format advantage/disadvantage
        roll_type = ""
        if advantage:
            roll_type = " with advantage"
        elif disadvantage:
            roll_type = " with disadvantage"
        
        result = {
            'ability': ability.capitalize(),
            'roll': roll_result,
            'modifier': modifier,
            'total': total,
            'dc': dc,
            'success': success,
            'is_proficient': is_proficient,
            'advantage': advantage,
            'disadvantage': disadvantage
        }
        
        # Print result
        print(f"{self.name} makes a {ability.capitalize()} saving throw{roll_type}:")
        print(f"  Rolled: {roll_result} + {modifier}{proficiency_text} = {total}")
        print(f"  DC {dc}: {'SUCCESS' if success else 'FAILURE'}")
        
        return result
    
    def add_skill_proficiency(self, skill_name: str):
        """Add proficiency in a skill"""
        if self.skill_proficiencies is None:
            try:
                from .skills import SkillProficiencies
            except ImportError:
                from .skills import SkillProficiencies
            self.skill_proficiencies = SkillProficiencies()
        self.skill_proficiencies.add_proficiency(skill_name)
    
    def add_skill_expertise(self, skill_name: str):
        """Add expertise in a skill (double proficiency)"""
        if self.skill_proficiencies is None:
            try:
                from .skills import SkillProficiencies
            except ImportError:
                from .skills import SkillProficiencies
            self.skill_proficiencies = SkillProficiencies()
        self.skill_proficiencies.add_expertise(skill_name)
    
    def add_feat(self, feat_name: str):
        """Add a feat to the character"""
        if feat_name not in self.feats:
            self.feats.append(feat_name)
            print(f"{self.name} gained feat: {feat_name}")
        else:
            print(f"{self.name} already has feat: {feat_name}")
    
    def attempt_foraging(self, forageable_object: Dict, season: str = "summer"):
        """Attempt to forage from an object"""
        try:
            from .foraging import ForagingSystem
        except ImportError:
            from foraging import ForagingSystem
        
        foraging_system = ForagingSystem()
        return foraging_system.attempt_foraging(self, forageable_object, season)
    
    def get_foraging_info(self, forageable_object: Dict, season: str = "summer"):
        """Get information about foraging an object"""
        try:
            from .foraging import ForagingSystem
        except ImportError:
            from foraging import ForagingSystem
        
        foraging_system = ForagingSystem()
        return foraging_system.get_foraging_info(forageable_object, self, season)
    
    def detect_shelter(self, location_data: Dict):
        """Detect available shelter at current location"""
        try:
            from .shelter import ShelterSystem
        except ImportError:
            from shelter import ShelterSystem
        
        shelter_system = ShelterSystem()
        return shelter_system.detect_natural_shelter(location_data, self)
    
    def attempt_camping(self, materials_available: List[str] = None, shelter_type: str = "makeshift_lean_to"):
        """Attempt to make camp"""
        try:
            from .shelter import ShelterSystem, ShelterType
        except ImportError:
            from shelter import ShelterSystem, ShelterType
        
        # Convert string to enum
        shelter_enum = ShelterType.MAKESHIFT_LEAN_TO
        if shelter_type == "proper_camp":
            shelter_enum = ShelterType.PROPER_CAMP
        
        shelter_system = ShelterSystem()
        return shelter_system.attempt_camping(self, materials_available, shelter_enum)
    
    def has_feat(self, feat_name: str) -> bool:
        """Check if character has a specific feat"""
        return feat_name in self.feats
    
    def get_feats(self) -> List[str]:
        """Get list of all character feats"""
        return self.feats.copy()
    
    def remove_feat(self, feat_name: str):
        """Remove a feat from the character"""
        if feat_name in self.feats:
            self.feats.remove(feat_name)
            print(f"{self.name} lost feat: {feat_name}")
        else:
            print(f"{self.name} doesn't have feat: {feat_name}")
    
    def equip_item(self, item, slot: str) -> bool:
        """Equip an item to a specific slot with character-specific validation"""
        if not self.equipment:
            try:
                from .equipment import Equipment
            except ImportError:
                from .equipment import Equipment
            self.equipment = Equipment()
        
        success, message = self.equipment.equip_item(item, slot, self)
        if success:
            # Recalculate stats after equipping
            self.recalculate_derived_stats()
        else:
            print(f"Failed to equip {item.name}: {message}")
        
        return success
    
    def unequip_item(self, slot: str):
        """Unequip an item from a specific slot"""
        if not self.equipment:
            print("No equipment system initialized")
            return None
        
        item, message = self.equipment.unequip_item(slot)
        if item:
            # Recalculate stats after unequipping
            self.recalculate_derived_stats()
            return item
        else:
            print(f"Failed to unequip: {message}")
            return None
    
    def get_equipped_item(self, slot: str):
        """Get the item equipped in a specific slot"""
        if not self.equipment:
            return None
        return self.equipment.get_item_in_slot(slot)
    
    def display_equipment(self) -> str:
        """Display character's equipment"""
        if not self.equipment:
            return "No equipment system"
        return self.equipment.display_equipment()
    
    def get_total_equipment_weight(self) -> float:
        """Get total weight of equipped items"""
        if not self.equipment:
            return 0.0
        return self.equipment.get_total_weight()
    
    def get_total_equipment_value(self) -> int:
        """Get total value of equipped items"""
        if not self.equipment:
            return 0
        return self.equipment.get_total_value()
    
    def get_equipment_attack_bonus(self, weapon_slot: str = 'main_hand') -> int:
        """Get attack bonus from equipped weapon"""
        if not self.equipment:
            return 0
        return self.equipment.get_attack_bonus(weapon_slot)
    
    def get_equipment_damage_bonus(self, weapon_slot: str = 'main_hand') -> int:
        """Get damage bonus from equipped weapon"""
        if not self.equipment:
            return 0
        return self.equipment.get_damage_bonus(weapon_slot)
    
    def get_equipment_saving_throw_bonus(self, ability: str = None) -> int:
        """Get saving throw bonuses from equipped items"""
        if not self.equipment:
            return 0
        return self.equipment.get_saving_throw_bonus(ability)
    
    def get_effective_ability_score(self, ability: str) -> int:
        """Get effective ability score including magical item effects"""
        base_score = getattr(self, ability)
        
        if self.equipment:
            # Check for ability score override (e.g., Gauntlets of Ogre Power)
            override = self.equipment.get_ability_score_override(ability)
            if override is not None:
                # Use the higher of base score or override
                base_score = max(base_score, override)
            
            # Add any ability score bonuses
            bonus = self.equipment.get_ability_score_bonus(ability)
            base_score += bonus
        
        return base_score
    
    def get_effective_ability_modifier(self, ability: str) -> int:
        """Get effective ability modifier including magical item effects"""
        effective_score = self.get_effective_ability_score(ability)
        return (effective_score - 10) // 2
    
    def initialize_inventory(self):
        """Initialize the new inventory system"""
        if self.inventory is None:
            self.inventory = Inventory()
            # Set carrying capacity based on Strength
            self.inventory.update_carrying_capacity(self.strength)
            print(f"Initialized inventory with {self.inventory.max_weight} lb capacity (STR {self.strength})")
    

    
    def add_item_to_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Add an item to inventory by ID"""
        if self.inventory is None:
            self.initialize_inventory()
        
        manager = InventoryManager()
        success = manager.add_item_by_id(self.inventory, item_id, quantity)
        
        if not success:
            encumbrance = self.get_encumbrance_level()
            print(f"Cannot add item - Current encumbrance: {encumbrance}")
        
        return success
    
    def remove_item_from_inventory(self, item_id: str, quantity: int = 1) -> Optional[InventoryItem]:
        """Remove an item from inventory"""
        if self.inventory is None:
            print("No inventory initialized")
            return None
        
        return self.inventory.remove_item(item_id, quantity)
    
    def has_item_in_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory contains an item"""
        if self.inventory is None:
            return False
        
        return self.inventory.has_item(item_id, quantity)
    
    def get_inventory_weight(self) -> float:
        """Get total weight of inventory items"""
        if self.inventory is None:
            return 0.0
        
        return self.inventory.get_total_weight()
    
    def get_total_carrying_weight(self) -> float:
        """Get total weight including equipment and inventory"""
        equipment_weight = self.get_total_equipment_weight()
        inventory_weight = self.get_inventory_weight()
        return equipment_weight + inventory_weight
    
    def get_carrying_capacity(self) -> float:
        """Get maximum carrying capacity based on Strength and equipped containers"""
        base_capacity = self.strength * 15.0  # D&D 5e rule: STR × 15 lbs
        
        # Add capacity bonus from equipped containers
        container_bonus = 0.0
        if self.equipment:
            container_bonus = self.equipment.get_capacity_bonus()
        
        return base_capacity + container_bonus
    
    def get_container_info(self) -> Dict[str, any]:
        """Get information about equipped containers"""
        if not self.equipment:
            return {
                'containers': [],
                'total_bonus': 0.0,
                'base_capacity': self.strength * 15.0,
                'total_capacity': self.strength * 15.0
            }
        
        containers = self.equipment.get_equipped_containers()
        total_bonus = self.equipment.get_capacity_bonus()
        base_capacity = self.strength * 15.0
        
        container_details = []
        for container in containers:
            container_details.append({
                'name': container.name,
                'slot': container.slot,
                'capacity_bonus': container.capacity_bonus,
                'weight': container.weight,
                'magical': container.magical
            })
        
        return {
            'containers': container_details,
            'total_bonus': total_bonus,
            'base_capacity': base_capacity,
            'total_capacity': base_capacity + total_bonus
        }
    
    def get_encumbrance_level(self) -> str:
        """Get current encumbrance level"""
        if self.inventory is None:
            # Calculate based on equipment only
            total_weight = self.get_total_equipment_weight()
            capacity = self.get_carrying_capacity()
        else:
            total_weight = self.get_total_carrying_weight()
            capacity = self.get_carrying_capacity()
        
        if total_weight <= capacity * 0.33:
            return "Light"
        elif total_weight <= capacity * 0.66:
            return "Medium"
        elif total_weight <= capacity:
            return "Heavy"
        else:
            return "Overencumbered"
    
    def is_overencumbered(self) -> bool:
        """Check if character is overencumbered"""
        return self.get_encumbrance_level() == "Overencumbered"
    
    def get_encumbrance_penalties(self) -> Dict[str, any]:
        """Get penalties applied due to encumbrance"""
        encumbrance = self.get_encumbrance_level()
        
        penalties = {
            'movement_speed_modifier': 1.0,
            'disadvantage_on_ability_checks': False,
            'disadvantage_on_attack_rolls': False,
            'disadvantage_on_saving_throws': False,
            'description': 'No encumbrance penalties'
        }
        
        if encumbrance == "Heavy":
            penalties.update({
                'movement_speed_modifier': 0.67,  # -10 feet (assuming 30 ft base)
                'description': 'Heavy load: Movement speed reduced by 10 feet'
            })
        elif encumbrance == "Overencumbered":
            penalties.update({
                'movement_speed_modifier': 0.33,  # -20 feet (assuming 30 ft base)
                'disadvantage_on_ability_checks': True,
                'disadvantage_on_attack_rolls': True,
                'disadvantage_on_saving_throws': True,
                'description': 'Overencumbered: Movement speed reduced by 20 feet, disadvantage on ability checks, attack rolls, and saving throws'
            })
        
        return penalties
    
    def update_inventory_capacity(self):
        """Update inventory carrying capacity when Strength changes"""
        if self.inventory is not None:
            self.inventory.update_carrying_capacity(self.strength)
    
    def display_inventory(self, show_details: bool = False) -> str:
        """Display character's inventory"""
        if self.inventory is None:
            return "No inventory initialized. Use initialize_inventory() first."
        
        return self.inventory.display_inventory(show_details)
    
    def get_inventory_summary(self) -> Dict[str, any]:
        """Get summary of inventory status"""
        total_weight = self.get_total_carrying_weight()
        capacity = self.get_carrying_capacity()
        encumbrance = self.get_encumbrance_level()
        penalties = self.get_encumbrance_penalties()
        
        return {
            'total_weight': total_weight,
            'carrying_capacity': capacity,
            'remaining_capacity': max(0, capacity - total_weight),
            'encumbrance_level': encumbrance,
            'is_overencumbered': self.is_overencumbered(),
            'penalties': penalties,
            'equipment_weight': self.get_total_equipment_weight(),
            'inventory_weight': self.get_inventory_weight()
        }


def create_character(name: str, race: str = "Human", character_class: str = "Fighter") -> Character:
    """Create a new character with standard array stat allocation"""
    # Standard array values: 15, 14, 13, 12, 10, 8
    standard_array = [15, 14, 13, 12, 10, 8]
    
    # Optimal stat allocation based on class
    # This is a simple allocation - for interactive allocation, use CharacterCreationFlow
    class_primary_stats = {
        "Fighter": "strength",
        "Rogue": "dexterity", 
        "Cleric": "wisdom",
        "Wizard": "intelligence"
    }
    
    # Get primary ability for the class (default to strength if unknown)
    primary_ability = class_primary_stats.get(character_class, "strength")
    
    # Create stat allocation dictionary
    abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    available_scores = standard_array.copy()
    stat_allocation = {}
    
    # Assign highest score (15) to primary ability
    stat_allocation[primary_ability] = 15
    available_scores.remove(15)
    
    # Constitution is important for HP, give it second priority if not primary
    if primary_ability != 'constitution':
        stat_allocation['constitution'] = 14
        available_scores.remove(14)
    
    # Dexterity is important for AC, give it third priority if not primary
    if primary_ability != 'dexterity' and 'dexterity' not in stat_allocation:
        if 14 in available_scores:
            stat_allocation['dexterity'] = 14
            available_scores.remove(14)
        else:
            stat_allocation['dexterity'] = 13
            available_scores.remove(13)
    
    # Assign remaining scores to remaining abilities
    remaining_abilities = [ability for ability in abilities if ability not in stat_allocation]
    for ability in remaining_abilities:
        stat_allocation[ability] = available_scores.pop(0)
    
    # Create character with allocated stats
    character = Character(
        name=name,
        race=race,
        character_class=character_class,
        strength=stat_allocation['strength'],
        dexterity=stat_allocation['dexterity'],
        constitution=stat_allocation['constitution'],
        intelligence=stat_allocation['intelligence'],
        wisdom=stat_allocation['wisdom'],
        charisma=stat_allocation['charisma'],
        level=1,
        hp=0,  # Will be calculated
        max_hp=0,  # Will be calculated
        armor_class=0,  # Will be calculated
        proficiency_bonus=2,  # Level 1 proficiency
        experience_points=0,
        skill_proficiencies=None  # Will be initialized when skill system is added
    )
    
    # Try to load class data for proper HP calculation
    try:
        from .character_class import ClassLoader
    except ImportError:
        try:
            from character_class import ClassLoader
        except ImportError:
            print("Warning: ClassLoader not available, using minimal class system")
            class ClassLoader:
                def get_class(self, class_name):
                    return type('MockClass', (), {
                        'name': class_name.title(),
                        'hit_die': 10,
                        'starting_equipment': []
                    })()
    
    try:
        from .equipment import Equipment
    except ImportError:
        try:
            from equipment import Equipment
        except ImportError:
            print("Warning: Equipment system not available, using minimal equipment")
            class Equipment:
                def __init__(self): pass
    
    class_loader = ClassLoader()
    char_class = class_loader.get_class(character_class.lower())
    
    # Initialize equipment system
    character.equipment = Equipment()
    
    # Initialize inventory system
    character.initialize_inventory()
    
    # Calculate derived stats with proper class hit die if available
    character.max_hp = character.calculate_hp(char_class)
    character.hp = character.max_hp
    character.armor_class = character.calculate_ac()
    character.proficiency_bonus = character.calculate_proficiency_bonus()
    
    print(f"Created {name} the {race} {character_class}")
    print(f"  Standard Array allocation (Primary: {primary_ability.capitalize()}):")
    print(f"  STR: {character.strength} ({character.ability_modifier('strength'):+d})")
    print(f"  DEX: {character.dexterity} ({character.ability_modifier('dexterity'):+d})")
    print(f"  CON: {character.constitution} ({character.ability_modifier('constitution'):+d})")
    print(f"  INT: {character.intelligence} ({character.ability_modifier('intelligence'):+d})")
    print(f"  WIS: {character.wisdom} ({character.ability_modifier('wisdom'):+d})")
    print(f"  CHA: {character.charisma} ({character.ability_modifier('charisma'):+d})")
    print(f"  HP: {character.hp}/{character.max_hp}, AC: {character.armor_class}")
    
    return character