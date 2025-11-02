"""
Fantasy RPG - Object Interaction System

Handles all object interactions within locations including:
- Foraging/harvesting from objects
- Searching containers
- Examining objects
- Unlocking/lockpicking
- Chopping wood
- Taking materials
- Drinking water
- Generic 'use' interactions
"""

from typing import Tuple, Dict, Any
import random


class ObjectInteractionSystem:
    """Manages all object-based interactions in locations"""
    
    def __init__(self, game_engine):
        """
        Initialize ObjectInteractionSystem.
        
        Args:
            game_engine: Reference to main GameEngine for accessing game state
        """
        self.game_engine = game_engine
    
    def interact_with_object(self, object_name: str, action: str) -> Tuple[bool, str]:
        """
        Interact with an object in current area based on its properties.
        
        Args:
            object_name: Name of object to interact with
            action: Type of interaction (forage, search, examine, etc.)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.game_engine.is_initialized or not self.game_engine.game_state:
            return False, "Game not initialized."
        
        gs = self.game_engine.game_state
        
        # Check if player is inside a location
        if not gs.world_position.current_location_id:
            return False, "You must be inside a location to interact with objects."
        
        # Get current area objects
        current_area_id = gs.world_position.current_area_id
        location_data = gs.world_position.current_location_data
        
        if not location_data or "areas" not in location_data:
            return False, "No objects available in this area."
        
        areas = location_data.get("areas", {})
        if current_area_id not in areas:
            return False, "Current area not found."
        
        area_data = areas[current_area_id]
        objects = area_data.get("objects", [])
        
        # Find the target object
        target_object = None
        for obj in objects:
            if obj.get("name", "").lower() == object_name.lower():
                target_object = obj
                break
        
        if not target_object:
            return False, f"You don't see any '{object_name}' here."
        
        # Route to appropriate handler based on action and object properties
        properties = target_object.get("properties", {})
        
        if action in ["forage", "harvest", "gather", "pick"]:
            return self._handle_forage(target_object, properties)
        elif action in ["search", "loot"]:
            return self._handle_search(target_object, properties)
        elif action in ["examine", "inspect", "look"]:
            return self._handle_examine(target_object, properties)
        elif action in ["unlock", "pick_lock"]:
            return self._handle_unlock(target_object, properties)
        elif action in ["chop", "cut"]:
            return self._handle_chop(target_object, properties)
        elif action in ["take", "get"]:
            return self._handle_take(target_object, properties)
        elif action in ["drink", "water"]:
            return self._handle_drink(target_object, properties)
        elif action in ["use"]:
            return self._handle_use(target_object, properties)
        else:
            return False, f"You can't {action} the {target_object.get('name', 'object')}."
    
    def _handle_forage(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle foraging/harvesting from objects"""
        if not properties.get("can_forage"):
            return False, f"You can't forage from the {obj.get('name', 'object')}."
        
        # Check if already depleted
        if obj.get("depleted", False):
            return False, f"The {obj.get('name')} has already been foraged recently."
        
        # Simple success for now - ActionHandler will implement the multi-skill system
        obj["depleted"] = True
        return True, f"You successfully forage from the {obj.get('name')} and find some berries."
    
    def _handle_search(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle searching containers/objects"""
        if not properties.get("can_search"):
            return False, f"There's nothing to search in the {obj.get('name')}."
        
        # Check if already searched
        if obj.get("searched", False):
            return False, f"You have already searched the {obj.get('name')}."
        
        # Simple success for now - ActionHandler implements the multi-skill system
        obj["searched"] = True
        return True, f"You search the {obj.get('name')} and find some items."
    
    def _handle_examine(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle examining objects closely"""
        base_description = obj.get("description", "An unremarkable object.")
        
        # Simple examination - ActionHandler implements the multi-skill system
        examination_text = properties.get("examination_text", "")
        if examination_text:
            return True, f"{base_description}\n\nUpon closer examination: {examination_text}"
        else:
            return True, base_description
    
    def _handle_unlock(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle unlocking/lockpicking objects"""
        if not properties.get("can_unlock"):
            return False, f"The {obj.get('name')} cannot be unlocked."
        
        # Check if already unlocked
        if obj.get("unlocked", False):
            return False, f"The {obj.get('name')} is already unlocked."
        
        # Make lockpicking check
        roll = random.randint(1, 20)
        skill_bonus = self._get_skill_bonus("sleight_of_hand")
        dc = properties.get("dc_lockpick", 15)
        total = roll + skill_bonus
        
        # Lockpicking takes time
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("lockpick", duration_override=1.0)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Lockpicking failed.")
        
        if total >= dc:
            # Success
            obj["unlocked"] = True
            return True, f"You successfully pick the lock on the {obj.get('name')}!"
        else:
            return False, f"You fail to pick the lock on the {obj.get('name')}."
    
    def _handle_chop(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle chopping wood from objects"""
        if not properties.get("can_chop_wood"):
            return False, f"You can't chop wood from the {obj.get('name')}."
        
        # Check if already chopped
        if obj.get("chopped", False):
            return False, f"You have already chopped wood from the {obj.get('name')}."
        
        # Simple success for now - ActionHandler implements the multi-skill system
        obj["chopped"] = True
        return True, f"You chop wood from the {obj.get('name')} and gather some firewood."
    
    def _handle_take(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle taking wood or other materials from objects"""
        if properties.get("can_take_wood"):
            # Check if already taken
            if obj.get("wood_taken", False):
                return False, f"You have already taken wood from the {obj.get('name')}."
            
            # Simple success for now - ActionHandler implements the multi-skill system
            obj["wood_taken"] = True
            return True, f"You take materials from the {obj.get('name')}."
        
        return False, f"You can't take anything from the {obj.get('name')}."
    
    def _handle_drink(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle drinking water from objects"""
        if not properties.get("provides_water"):
            return False, f"You can't drink from the {obj.get('name')}."
        
        water_quality = properties.get("water_quality", "poor")
        
        # Drinking is quick
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("quick", duration_override=0.083)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Drinking failed.")
        
        # Apply thirst relief based on water quality
        gs = self.game_engine.game_state
        if water_quality == "excellent":
            thirst_relief = 200
        elif water_quality == "good":
            thirst_relief = 150
        elif water_quality == "fair":
            thirst_relief = 100
        else:  # poor
            thirst_relief = 50
        
        old_thirst = gs.player_state.survival.thirst
        gs.player_state.survival.thirst = min(1000, gs.player_state.survival.thirst + thirst_relief)
        
        return True, (
            f"You drink from the {obj.get('name')}. The water is {water_quality}.\n"
            f"Thirst relief: +{thirst_relief} ({old_thirst} → {gs.player_state.survival.thirst})"
        )
    
    def _handle_use(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle using objects (generic interaction)"""
        # For now, 'use' defaults to examine behavior
        return self._handle_examine(obj, properties)
    
    def _get_skill_bonus(self, skill_name: str) -> int:
        """Get character's skill bonus"""
        gs = self.game_engine.game_state
        
        if skill_name == "nature":
            return (gs.character.wisdom - 10) // 2
        elif skill_name == "perception":
            return (gs.character.wisdom - 10) // 2
        elif skill_name == "investigation":
            return (gs.character.intelligence - 10) // 2
        elif skill_name == "athletics":
            return (gs.character.strength - 10) // 2
        elif skill_name == "sleight_of_hand":
            return (gs.character.dexterity - 10) // 2
        elif skill_name == "survival":
            return (gs.character.wisdom - 10) // 2
        else:
            return 0
    
    def _calculate_quality_multiplier(self, success_margin: int) -> float:
        """
        Calculate quality multiplier based on how much the skill check exceeded the DC.
        
        Args:
            success_margin: How much the roll exceeded the DC (can be negative)
        
        Returns:
            Multiplier for item quantity (0.5 to 2.0)
        """
        if success_margin >= 15:
            return 2.0
        elif success_margin >= 10:
            return 1.5
        elif success_margin >= 5:
            return 1.2
        elif success_margin >= 0:
            return 1.0
        elif success_margin >= -3:
            return 0.8
        else:
            return 0.5
    
    def _generate_from_item_drops(self, item_drops: Dict, quality_multiplier: float = 1.0) -> Dict[str, int]:
        """Generate items from item_drops configuration with quality scaling"""
        items = {}
        
        # Get drop parameters
        min_drops = item_drops.get("min_drops", 0)
        max_drops = item_drops.get("max_drops", 1)
        base_drop_chance = item_drops.get("drop_chance", 50)
        
        # Scale drop chance with quality (better rolls = higher chance)
        scaled_drop_chance = min(95, int(base_drop_chance * quality_multiplier))
        
        # Check if we get any drops
        if random.randint(1, 100) <= scaled_drop_chance:
            base_num_drops = random.randint(min_drops, max_drops)
            # Scale number of drops with quality
            num_drops = max(1, int(base_num_drops * quality_multiplier))
            
            # Generate items based on pools
            pools = item_drops.get("pools", [])
            
            for _ in range(num_drops):
                if "food" in pools:
                    items["wild_berries"] = items.get("wild_berries", 0) + 1
                elif "treasure" in pools:
                    base_coins = random.randint(1, 10)
                    scaled_coins = max(1, int(base_coins * quality_multiplier))
                    items["gold_coins"] = items.get("gold_coins", 0) + scaled_coins
                elif "materials" in pools or "wood" in pools:
                    items["firewood"] = items.get("firewood", 0) + 1
                else:
                    # Generic material
                    items["bone_fragments"] = items.get("bone_fragments", 0) + 1
        
        return items
