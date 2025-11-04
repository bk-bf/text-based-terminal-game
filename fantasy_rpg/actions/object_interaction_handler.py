"""
Fantasy RPG - Object Interaction Handler

Handles all object interaction commands by delegating to ObjectInteractionSystem.
This is a thin wrapper that:
1. Parses user commands
2. Validates preconditions (must be in location)
3. Delegates to game_engine.interact_with_object()
4. Wraps results in ActionResult

All actual game logic lives in fantasy_rpg/game/object_interaction_system.py
"""

from .base_handler import BaseActionHandler, ActionResult


class ObjectInteractionHandler(BaseActionHandler):
    """Handler for object interaction commands - delegates to ObjectInteractionSystem"""
    
    def handle_examine(self, *args) -> ActionResult:
        """Handle examining objects - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Examine what? Specify an object name.")
        
        object_name = " ".join(args).lower()
        
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "examine")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            
            # Examining is very quick - only 6 minutes
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.1 if success else 0.0,
                action_type="object_interaction"
            )
        except Exception as e:
            return ActionResult(False, f"Error: {str(e)}")
    
    def handle_search(self, *args) -> ActionResult:
        """Handle searching objects - delegates to ObjectInteractionSystem
        
        Returns ActionResult with metadata for ActionLogger to generate NLP messages.
        """
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Search what? Specify an object name (e.g., 'search chest')")
        
        object_name = " ".join(args).lower()
        
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "search")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')
            items_found = result.get('items_found', [])
            skill_check = result.get('skill_check')
            
            # Only pass time if the search actually happened
            time_passed = 0.1 if success else 0.0  # 6 minutes for successful search
            
            # Return ActionResult with metadata for NLP generation
            return ActionResult(
                success=success,
                message=message,  # Factual info ("You find: X")
                time_passed=time_passed,
                event_type=event_type,  # For NLP: 'search_success' or 'search_empty'
                object_name=result.get('object_name', object_name),
                items_found=items_found,
                skill_check=skill_check
            )
        except Exception as e:
            return ActionResult(False, f"Error: {str(e)}")
    
    def handle_use(self, *args) -> ActionResult:
        """Handle using objects - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Use what? Specify an object name.")
        
        object_name = " ".join(args).lower()
        
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "use")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25 if success else 0.0,
                action_type="object_interaction"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to use object: {str(e)}")
    
    def handle_forage(self, *args) -> ActionResult:
        """Handle foraging - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Forage what? Specify an object name (e.g., 'forage berry bush')")
        
        object_name = " ".join(args).lower()
        
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "forage")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')
            
            # Use time system to ensure condition effects are applied
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("forage", duration_override=0.25)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Foraging interrupted."))
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25,
                event_type=event_type,
                object_name=result.get('object_name', object_name)
            )
        except Exception as e:
            return ActionResult(False, f"Failed to forage: {str(e)}")
    
    def handle_harvest(self, *args) -> ActionResult:
        """Handle harvesting - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Harvest what? Specify an object name (e.g., 'harvest berry bush')")
        
        object_name = " ".join(args).lower()
        
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "harvest")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')
            
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("forage", duration_override=0.25)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Harvesting interrupted."))
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25,
                event_type=event_type,
                object_name=result.get('object_name', object_name)
            )
        except Exception as e:
            return ActionResult(False, f"Failed to harvest: {str(e)}")
    
    def handle_chop(self, *args) -> ActionResult:
        """Handle chopping wood - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Chop what? Specify an object name (e.g., 'chop tree')")
        
        object_name = " ".join(args).lower()
        
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "chop")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')
            
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("chop_wood", duration_override=1.0)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Chopping interrupted."))
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=1.0,
                event_type=event_type,
                object_name=result.get('object_name', object_name)
            )
        except Exception as e:
            return ActionResult(False, f"Failed to chop: {str(e)}")
    
    def handle_drink(self, *args) -> ActionResult:
        """Handle drinking from water sources - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Drink from what? Specify a water source (e.g., 'drink well')")
        
        object_name = " ".join(args).lower()
        
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "drink")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')
            
            # Use time system
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("drink", duration_override=0.1)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Drinking interrupted."))
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.1,
                action_type="survival",
                event_type=event_type,
                object_name=result.get('object_name', object_name),
                water_quality=result.get('water_quality'),
                temperature=result.get('temperature')
            )
            
        except Exception as e:
            return ActionResult(False, f"Failed to drink: {str(e)}")
    
    def handle_unlock(self, *args) -> ActionResult:
        """Handle unlocking/lockpicking - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Unlock what? Specify an object name (e.g., 'unlock chest')")
        
        object_name = " ".join(args).lower()
        
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "unlock")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')
            
            # Use time system
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("lockpick", duration_override=0.5)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Lockpicking interrupted."))
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.5,
                event_type=event_type,
                object_name=result.get('object_name', object_name)
            )
                
        except Exception as e:
            return ActionResult(False, f"Failed to unlock: {str(e)}")
    
    def handle_light_fire(self, *args) -> ActionResult:
        """Handle lighting fires - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Light what? Specify an object name (e.g., 'light firepit')")
        
        object_name = " ".join(args).lower()
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "light")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25,
                event_type=event_type,
                object_name=result.get('object_name', object_name)
            )
        except Exception as e:
            return ActionResult(False, f"Failed to light fire: {str(e)}")
    
    def handle_disarm_trap(self, *args) -> ActionResult:
        """Handle disarming traps - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, "Disarm trap on what? Specify an object name.")
        
        object_name = " ".join(args).lower()
        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "disarm")
            
            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.5,
                event_type=event_type,
                object_name=result.get('object_name', object_name),
                triggered=result.get('triggered', False)
            )
        except Exception as e:
            return ActionResult(False, f"Failed to disarm trap: {str(e)}")

