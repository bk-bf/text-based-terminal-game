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
    
    def _delegate_to_system(self, args, action_name: str, activity_type: str = None, 
                           duration: float = 0.1, error_msg: str = None) -> ActionResult:
        """Shared delegation pattern for object interactions
        
        Args:
            args: Command arguments (object name)
            action_name: Action type passed to interact_with_object (search, forage, etc.)
            activity_type: Activity name for time_system.perform_activity() (if different from action_name)
            duration: Time passed in hours (default 0.1 = 6 minutes)
            error_msg: Error message if no arguments provided
            
        Returns:
            ActionResult with metadata for NLP generation
        """
        if error := self._require_location():
            return error
        
        if not args:
            return ActionResult(False, error_msg or f"{action_name.capitalize()} what? Specify an object name.")
        
        object_name = " ".join(args).lower()
        
        try:
            # Delegate to ObjectInteractionSystem
            result = self.game_engine.interact_with_object(object_name, action_name)
            
            success = result.get('success', False)
            
            # Apply time passage with survival effects if activity_type provided
            if success and activity_type and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity(
                    activity_type, duration_override=duration
                )
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", f"{action_name.capitalize()} interrupted."))
            
            # Build ActionResult with all metadata from system
            return ActionResult(
                success=success,
                message=result.get('message', ''),
                time_passed=duration if success else 0.0,
                event_type=result.get('event_type'),
                object_name=result.get('object_name', object_name),
                items_found=result.get('items_found'),
                skill_check=result.get('skill_check'),
                water_quality=result.get('water_quality'),
                temperature=result.get('temperature'),
                triggered=result.get('triggered')
            )
        except Exception as e:
            return ActionResult(False, f"Failed to {action_name}: {str(e)}")
    
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
        """Handle searching objects - delegates to ObjectInteractionSystem"""
        return self._delegate_to_system(
            args, 
            action_name="search",
            duration=0.1,  # 6 minutes
            error_msg="Search what? Specify an object name (e.g., 'search chest')"
        )
    
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
        return self._delegate_to_system(
            args,
            action_name="forage",
            activity_type="forage",
            duration=0.25,  # 15 minutes
            error_msg="Forage what? Specify an object name (e.g., 'forage berry bush')"
        )
    
    def handle_harvest(self, *args) -> ActionResult:
        """Handle harvesting - delegates to ObjectInteractionSystem"""
        return self._delegate_to_system(
            args,
            action_name="harvest",
            activity_type="forage",
            duration=0.25,  # 15 minutes
            error_msg="Harvest what? Specify an object name (e.g., 'harvest berry bush')"
        )
    
    def handle_chop(self, *args) -> ActionResult:
        """Handle chopping wood - delegates to ObjectInteractionSystem"""
        return self._delegate_to_system(
            args,
            action_name="chop",
            activity_type="chop_wood",
            duration=1.0,  # 1 hour
            error_msg="Chop what? Specify an object name (e.g., 'chop tree')"
        )
    
    def handle_drink(self, *args) -> ActionResult:
        """Handle drinking from water sources - delegates to ObjectInteractionSystem"""
        return self._delegate_to_system(
            args,
            action_name="drink",
            activity_type="drink",
            duration=0.1,  # 6 minutes
            error_msg="Drink from what? Specify a water source (e.g., 'drink well')"
        )
    
    def handle_unlock(self, *args) -> ActionResult:
        """Handle unlocking/lockpicking - delegates to ObjectInteractionSystem"""
        return self._delegate_to_system(
            args,
            action_name="unlock",
            activity_type="lockpick",
            duration=0.5,  # 30 minutes
            error_msg="Unlock what? Specify an object name (e.g., 'unlock chest')"
        )
    
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

