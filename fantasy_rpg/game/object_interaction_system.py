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

ARCHITECTURE: Returns structured dicts instead of tuples for proper message ordering.
Uses _make_result() helper to create consistent return values.

All methods use Dict[str, Any] pattern with event_type metadata.
"""

from typing import Dict, Any, Optional
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
    
    @staticmethod
    def _make_result(success: bool, message: str = "", **kwargs) -> Dict[str, Any]:
        """Helper to create consistent result dicts
        
        Args:
            success: Whether the action succeeded
            message: Factual message (items found, etc.)
            **kwargs: Additional metadata (event_type, items_found, etc.)
        
        Returns:
            Dict with standardized structure
        """
        result = {'success': success, 'message': message}
        result.update(kwargs)
        return result
    
    def interact_with_object(self, object_name: str, action: str) -> Dict[str, Any]:
        """
        Interact with an object in current area based on its properties.
        
        Args:
            object_name: Name of object to interact with
            action: Type of interaction (forage, search, examine, etc.)
        
        Returns:
            Dict with interaction results:
                {
                    'success': bool,
                    'message': str,  # Factual info (items found, etc.)
                    'event_type': str,  # For NLP: 'search_success', 'forage_depleted', etc.
                    'object_name': str,
                    'items_found': list,  # List of "quantity x Item Name" strings
                    'skill_check': dict,  # Optional: skill check details
                }
        """
        if not self.game_engine.is_initialized or not self.game_engine.game_state:
            return self._make_result(False, "Game not initialized.")
        
        gs = self.game_engine.game_state
        
        # Check if player is inside a location
        if not gs.world_position.current_location_id:
            return self._make_result(False, "You must be inside a location to interact with objects.")
        
        # Get current area objects
        current_area_id = gs.world_position.current_area_id
        location_data = gs.world_position.current_location_data
        
        if not location_data or "areas" not in location_data:
            return self._make_result(False, "No objects available in this area.")
        
        areas = location_data.get("areas", {})
        if current_area_id not in areas:
            return self._make_result(False, "Current area not found.")
        
        area_data = areas[current_area_id]
        objects = area_data.get("objects", [])
        
        # Find the target object
        target_object = None
        for obj in objects:
            if obj.get("name", "").lower() == object_name.lower():
                target_object = obj
                break
        
        if not target_object:
            return self._make_result(False, f"You don't see any '{object_name}' here.")
        
        # Route to appropriate handler based on action and object properties
        properties = target_object.get("properties", {})
        
        if action == "forage":
            return self._handle_forage(target_object, properties)
        elif action == "harvest":
            return self._handle_harvest(target_object, properties)
        elif action == "search":
            return self._handle_search(target_object, properties)
        elif action == "examine":
            return self._handle_examine(target_object, properties)
        elif action == "unlock":
            return self._handle_unlock(target_object, properties)
        elif action == "chop":
            return self._handle_chop(target_object, properties)
        elif action == "drink":
            return self._handle_drink(target_object, properties)
        elif action == "light":
            return self._handle_light(target_object, properties)
        elif action == "use":
            return self._handle_use(target_object, properties)
        elif action == "disarm":
            return self._handle_disarm(target_object, properties)
        else:
            return self._make_result(False, f"You can't {action} the {target_object.get('name', 'object')}.")
    
    def _handle_forage(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle foraging from objects using Survival skill"""
        if not properties.get("can_forage"):
            return self._make_result(False, f"You can't forage from the {obj.get('name', 'object')}.")
        
        # Check if already depleted
        if obj.get("depleted", False):
            return self._make_result(
                False,
                "",
                event_type='forage_depleted',
                object_name=obj.get('name', 'object')
            )
        
        # Simple success for now - ActionHandler will implement the multi-skill system
        obj["depleted"] = True
        
        return self._make_result(
            True,
            "",
            event_type='forage_success',
            object_name=obj.get('name', 'object'),
            items_found=["1x Berries"]
        )
    
    def _handle_harvest(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle harvesting from objects using Nature skill"""
        if not properties.get("can_forage"):
            return self._make_result(False, f"You can't harvest from the {obj.get('name', 'object')}.")
        
        # Check if already depleted
        if obj.get("depleted", False):
            return self._make_result(
                False,
                "",
                event_type='harvest_depleted',
                object_name=obj.get('name', 'object')
            )
        
        # Simple success for now - ActionHandler will implement the multi-skill system
        obj["depleted"] = True
        
        return self._make_result(
            True,
            "",
            event_type='harvest_success',
            object_name=obj.get('name', 'object'),
            items_found=["1x Materials"]
        )
    
    def _handle_search(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle searching containers/objects with full item generation"""
        if not properties.get("can_search"):
            return {'success': False, 'message': f"There's nothing to search in the {obj.get('name')}."}
        
        # Check if already searched
        if obj.get("searched", False):
            return {'success': False, 'message': f"You have already searched the {obj.get('name')}."}
        
        # Make skill check
        roll = random.randint(1, 20)
        primary_skill = "perception"
        secondary_skill = "investigation"
        dc = properties.get("dc_search", 10)
        skill_bonus = self._get_multi_skill_bonus(primary_skill, secondary_skill)
        total = roll + skill_bonus
        
        # Mark as searched regardless of success
        obj["searched"] = True
        
        if total >= dc:
            # Success - generate items based on object's item_drops
            items_generated = self._generate_items_from_object(obj, "search", total, dc)
            
            if items_generated:
                # Add items to inventory
                success_items = []
                failed_items = []
                
                gs = self.game_engine.game_state
                for item_id, quantity in items_generated.items():
                    if gs.character.add_item_to_inventory(item_id, quantity):
                        success_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                    else:
                        failed_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                
                # Build factual message about items found
                result_msg = ""
                if success_items:
                    result_msg += f"You find: {', '.join(success_items)}"
                if failed_items:
                    if result_msg:
                        result_msg += "\n"
                    result_msg += f"Couldn't carry: {', '.join(failed_items)} (inventory full)"
                
                return {
                    'success': True,
                    'message': result_msg,
                    'event_type': 'search_success',
                    'object_name': obj.get('name', 'object'),
                    'items_found': success_items,
                    'skill_check': {
                        'skill': primary_skill,
                        'roll': roll,
                        'modifier': skill_bonus,
                        'total': total,
                        'dc': dc
                    }
                }
            else:
                # Empty container
                return {
                    'success': True,
                    'message': "",
                    'event_type': 'search_empty',
                    'object_name': obj.get('name', 'object'),
                    'items_found': [],
                    'skill_check': {
                        'skill': primary_skill,
                        'roll': roll,
                        'modifier': skill_bonus,
                        'total': total,
                        'dc': dc
                    }
                }
        else:
            # Forgiving failure - still might find something with failed roll
            items_generated = self._generate_items_from_object(obj, "search", total, dc)
            if items_generated:
                success_items = []
                gs = self.game_engine.game_state
                for item_id, quantity in items_generated.items():
                    if gs.character.add_item_to_inventory(item_id, quantity):
                        success_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                
                if success_items:
                    return {
                        'success': True,
                        'message': f"You find: {', '.join(success_items)}",
                        'event_type': 'search_success',
                        'object_name': obj.get('name', 'object'),
                        'items_found': success_items,
                        'skill_check': {
                            'skill': primary_skill,
                            'roll': roll,
                            'modifier': skill_bonus,
                            'total': total,
                            'dc': dc
                        }
                    }
            
            # Failed search - nothing found
            return {
                'success': False,
                'message': "",
                'event_type': 'search_empty',
                'object_name': obj.get('name', 'object'),
                'items_found': [],
                'skill_check': {
                    'skill': primary_skill,
                    'roll': roll,
                    'modifier': skill_bonus,
                    'total': total,
                    'dc': dc
                }
            }
    
    def _handle_examine(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle examining objects closely"""
        base_description = obj.get("description", "An unremarkable object.")
        
        # Simple examination - ActionHandler implements the multi-skill system
        examination_text = properties.get("examination_text", "")
        if examination_text:
            message = f"{base_description}\n\nUpon closer examination: {examination_text}"
        else:
            message = base_description
        
        return self._make_result(True, message)
    
    def _handle_unlock(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle unlocking/lockpicking objects"""
        if not properties.get("can_unlock"):
            return self._make_result(False, f"The {obj.get('name')} cannot be unlocked.")
        
        # Check if already unlocked
        if obj.get("unlocked", False):
            return self._make_result(False, f"The {obj.get('name')} is already unlocked.")
        
        # Make lockpicking check
        roll = random.randint(1, 20)
        skill_bonus = self._get_skill_bonus("sleight_of_hand")
        dc = properties.get("dc_lockpick", 15)
        total = roll + skill_bonus
        
        # Lockpicking takes time
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("lockpick", duration_override=1.0)
            if not time_result.get("success", True):
                return self._make_result(False, time_result.get("message", "Lockpicking failed."))
        
        if total >= dc:
            # Success
            obj["unlocked"] = True
            return self._make_result(
                True,
                "",
                event_type='unlock_success',
                object_name=obj.get('name', 'object')
            )
        else:
            return self._make_result(
                False,
                "",
                event_type='unlock_failure',
                object_name=obj.get('name', 'object')
            )
    
    def _handle_disarm(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle disarming traps"""
        if not properties.get("can_disarm"):
            return self._make_result(False, f"The {obj.get('name')} has no trap to disarm.")
        
        # Check if already disarmed
        if obj.get("disarmed", False):
            return self._make_result(False, f"The trap on the {obj.get('name')} has already been disarmed.")
        
        # Make sleight of hand check for trap disarming
        roll = random.randint(1, 20)
        skill_bonus = self._get_skill_bonus("sleight_of_hand")
        dc = properties.get("dc_disarm", 15)
        total = roll + skill_bonus
        
        # Disarming takes time and concentration
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("general", duration_override=0.5)
            if not time_result.get("success", True):
                return self._make_result(False, time_result.get("message", "Trap disarming failed."))
        
        if total >= dc:
            # Success
            obj["disarmed"] = True
            return self._make_result(
                True,
                "",
                event_type='disarm_success',
                object_name=obj.get('name', 'object')
            )
        else:
            # Failure - trap might trigger
            trigger_damage = properties.get("trap_damage", 0)
            if trigger_damage > 0:
                gs = self.game_engine.game_state
                gs.character.hp = max(0, gs.character.hp - trigger_damage)
                return self._make_result(
                    False,
                    f"You take {trigger_damage} damage.",
                    event_type='disarm_failure',
                    object_name=obj.get('name', 'object'),
                    triggered=True
                )
            else:
                return self._make_result(
                    False,
                    "",
                    event_type='disarm_failure',
                    object_name=obj.get('name', 'object'),
                    triggered=False
                )
    
    def _handle_chop(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle chopping wood from objects"""
        if not properties.get("can_chop_wood"):
            return self._make_result(False, f"You can't chop wood from the {obj.get('name')}.")
        
        # Check if already chopped
        if obj.get("chopped", False):
            return self._make_result(
                False,
                "",
                event_type='chop_depleted',
                object_name=obj.get('name', 'object')
            )
        
        # Simple success for now - ActionHandler implements the multi-skill system
        obj["chopped"] = True
        return self._make_result(
            True,
            "",
            event_type='chop_success',
            object_name=obj.get('name', 'object')
        )
    
    def _handle_drink(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle drinking water from objects - time passage handled by ObjectInteractionHandler"""
        if not properties.get("provides_water"):
            return self._make_result(False, f"You can't drink from the {obj.get('name')}.")
        
        water_quality = properties.get("water_quality", "poor")
        temperature = properties.get("temperature", "cool")
        
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
        
        gs.player_state.survival.thirst = min(1000, gs.player_state.survival.thirst + thirst_relief)
        
        # Quality-specific effects
        if water_quality == "excellent":
            # Small HP bonus for excellent water
            character = gs.character
            character.hp = min(character.max_hp, character.hp + 1)
        
        return self._make_result(
            True,
            "",
            event_type='drink_success',
            object_name=obj.get('name', 'object'),
            water_quality=water_quality,
            temperature=temperature
        )
    
    def _handle_use(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle using objects (generic interaction)"""
        # For now, 'use' defaults to examine behavior
        return self._handle_examine(obj, properties)
    
    def _handle_light(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle lighting fires in fireplaces and similar objects"""
        # Check if already lit FIRST (before checking can_light_fire)
        if obj.get("lit", False):
            return self._make_result(False, f"The {obj.get('name')} is already lit.")
        
        if not properties.get("can_light_fire"):
            return self._make_result(False, f"You can't light a fire in the {obj.get('name')}.")
        
        # Check if fuel is required and available
        fuel_consumed = False
        if properties.get("fuel_required"):
            gs = self.game_engine.game_state
            # Check for firewood in inventory
            has_firewood = False
            for item in gs.character.inventory.items:
                if item.item_id == "firewood" and item.quantity >= 1:
                    has_firewood = True
                    # Consume 1 firewood
                    gs.character.inventory.remove_item("firewood", 1)
                    fuel_consumed = True
                    break
            
            if not has_firewood:
                return self._make_result(False, f"You need firewood to light a fire in the {obj.get('name')}.")
        
        # Make survival check to light fire
        roll = random.randint(1, 20)
        skill_bonus = self._get_skill_bonus("survival")
        dc = 12
        total = roll + skill_bonus
        
        if total >= dc:
            # Success - transform object if it has transforms_to property
            transforms_to = properties.get("transforms_to")
            if transforms_to:
                transform_success = self._transform_object(obj, transforms_to)
                if not transform_success:
                    return self._make_result(False, f"Failed to transform {obj.get('name')} after lighting.")
            else:
                # Just mark as lit if no transformation
                obj["lit"] = True
            
            # Apply warmth benefit
            gs = self.game_engine.game_state
            old_warmth = gs.player_state.survival.warmth
            gs.player_state.survival.warmth = min(1000, gs.player_state.survival.warmth + 100)
            
            # Build factual message about fuel consumption
            fuel_message = ""
            if fuel_consumed:
                fuel_message = "You consume 1 firewood to fuel the flames."
            
            return self._make_result(
                True,
                fuel_message,
                event_type='fire_started',
                object_name=obj.get('name', 'object')
            )
        else:
            return self._make_result(
                False,
                "",
                event_type='fire_failure',
                object_name=obj.get('name', 'object')
            )
    
    def _transform_object(self, target_object: Dict, new_object_id: str) -> bool:
        """Transform an object into a different object type (e.g., fireplace -> lit_fireplace)"""
        try:
            import json
            from pathlib import Path
            
            # Load the new object data from objects.json
            objects_file = Path(__file__).parent.parent / 'data' / 'objects.json'
            with open(objects_file, 'r') as f:
                objects_data = json.load(f)
            
            if new_object_id not in objects_data['objects']:
                print(f"Warning: Object '{new_object_id}' not found in objects.json")
                return False
            
            new_object_data = objects_data['objects'][new_object_id]
            
            # Update the target object with new data
            # Handle name as either string or list of strings
            name_data = new_object_data['name']
            if isinstance(name_data, list):
                # Randomly select one name from the list
                import random
                selected_name = random.choice(name_data)
            else:
                selected_name = name_data
            
            target_object['name'] = selected_name
            target_object['description'] = new_object_data['description']
            target_object['properties'] = new_object_data['properties'].copy()
            target_object['lit'] = True  # Mark as lit
            
            # Copy any item drops if they exist
            if 'item_drops' in new_object_data:
                target_object['item_drops'] = new_object_data['item_drops']
            
            return True
        except Exception as e:
            print(f"Error transforming object: {e}")
            return False
    
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
    
    def _get_multi_skill_bonus(self, primary_skill: str, secondary_skill: str = None) -> int:
        """Get combined skill bonus for multi-skill checks"""
        primary_bonus = self._get_skill_bonus(primary_skill)
        if secondary_skill:
            secondary_bonus = self._get_skill_bonus(secondary_skill)
            # Primary skill gets full weight, secondary gets half weight
            return primary_bonus + (secondary_bonus // 2)
        return primary_bonus
    
    def _generate_items_from_object(self, obj: Dict, interaction_type: str, skill_roll: int = 10, dc: int = 10) -> Dict[str, int]:
        """
        Generate items based on multi-skill risk/reward system.
        Implements the complete item generation logic from the old ActionHandler.
        
        Returns:
            Dictionary mapping item_id -> quantity
        """
        properties = obj.get("properties", {})
        items_to_generate = {}
        
        # Calculate success quality based on how much the roll exceeded DC
        success_margin = skill_roll - dc
        
        # Determine what items to generate based on object type and interaction
        object_name = obj.get("name", "").lower()
        
        # Berry Bush -> Multi-skill approach
        if "berry" in object_name:
            if interaction_type in ["forage", "harvest", "gather", "pick"]:
                # HIGH RISK/HIGH REWARD
                if success_margin >= 0:
                    quantity = 2 + max(0, success_margin // 3)
                    items_to_generate["wild_berries"] = min(5, quantity)
                    
            elif interaction_type in ["search"]:
                # MEDIUM RISK/MEDIUM REWARD
                if success_margin >= 0:
                    quantity = 1 + max(0, success_margin // 5)
                    items_to_generate["wild_berries"] = min(3, quantity)
                else:
                    # Forgiving failure
                    if success_margin >= -3:
                        items_to_generate["wild_berries"] = 1
                        
            elif interaction_type in ["examine"]:
                # LOW RISK/LOW REWARD
                if success_margin >= 0:
                    quantity = 1 + (1 if success_margin >= 8 else 0)
                    items_to_generate["wild_berries"] = quantity
                else:
                    if success_margin >= -5:
                        items_to_generate["wild_berries"] = 1
        
        # Trees/Wood -> Multi-skill approach  
        elif any(wood_type in object_name for wood_type in ["tree", "log", "wood", "pile"]):
            if interaction_type in ["chop", "cut"]:
                # HIGH RISK/HIGH REWARD
                if success_margin >= 0:
                    quantity = 3 + max(0, success_margin // 3)
                    items_to_generate["firewood"] = min(6, quantity)
                else:
                    if success_margin >= -2:
                        items_to_generate["firewood"] = 1
                        
            elif interaction_type in ["search"]:
                # MEDIUM RISK/DIVERSE REWARD
                if success_margin >= 0:
                    firewood_qty = 1 + (1 if success_margin >= 6 else 0)
                    items_to_generate["firewood"] = firewood_qty
                    
                    if success_margin >= 10:
                        items_to_generate["wild_berries"] = 1
                    if success_margin >= 15:
                        items_to_generate["gold_coins"] = random.randint(1, 3)
                else:
                    if success_margin >= -4:
                        items_to_generate["firewood"] = 1
                        
            elif interaction_type in ["take"]:
                # NO RISK/LOW REWARD
                items_to_generate["firewood"] = 1 + (1 if random.randint(1, 100) <= 50 else 0)
        
        # Tables/Containers -> Search-based loot
        elif any(container in object_name for container in ["table", "chest", "crate", "barrel"]):
            if interaction_type in ["search"]:
                if success_margin >= 0:
                    # Base loot
                    items_to_generate["gold_coins"] = random.randint(1, 5)
                    
                    # Bonus items based on success
                    if success_margin >= 8:
                        items_to_generate["firewood"] = 1
                    if success_margin >= 12:
                        items_to_generate["wild_berries"] = random.randint(1, 2)
                else:
                    # Small chance on failure
                    if success_margin >= -3:
                        items_to_generate["gold_coins"] = 1
        
        # Generic fallback
        else:
            # Check for specific item generation in properties
            if properties.get("generates_items"):
                generated_item = properties.get("generated_item_id")
                base_quantity = properties.get("generated_quantity", 1)
                if generated_item:
                    if success_margin >= 0:
                        final_quantity = base_quantity + max(0, success_margin // 5)
                        items_to_generate[generated_item] = final_quantity
                    else:
                        if success_margin >= -3:
                            items_to_generate[generated_item] = max(1, base_quantity // 2)
        
        return items_to_generate
