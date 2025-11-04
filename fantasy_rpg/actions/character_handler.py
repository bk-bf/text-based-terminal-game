"""
Fantasy RPG - Character Handler

Handles character-related commands:
- Inventory management
- Character sheet viewing
- Rest and sleep
"""

from .base_handler import BaseActionHandler, ActionResult


class CharacterHandler(BaseActionHandler):
    """Handler for character-related commands"""
    
    def handle_inventory(self, *args) -> ActionResult:
        """Handle inventory display"""
        return ActionResult(
            success=True,
            message="Opening inventory...",
            time_passed=0.0,
            action_type="ui_modal",
            modal_type="inventory"
        )
    
    def handle_character(self, *args) -> ActionResult:
        """Handle character sheet display"""
        return ActionResult(
            success=True,
            message="Reviewing character details...",
            time_passed=0.0,
            action_type="ui_modal",
            modal_type="character"
        )
    
    def handle_rest(self, *args) -> ActionResult:
        """Handle resting/sleeping in current location"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        try:
            success, message = self.game_engine.rest_in_location()
            return ActionResult(success, message)
        except Exception as e:
            return ActionResult(False, f"Failed to rest: {str(e)}")
    
    # Helper methods
    def _find_object_in_current_area(self, object_name: str):
        """Find an available object in the current area (GameEngine coordination)"""
        if not self.game_engine or not self.game_engine.is_initialized:
            return None
        
        gs = self.game_engine.game_state
        
        # Check if player is inside a location
        if not gs.world_position.current_location_id:
            return None
        
        # Get current area objects
        current_area_id = gs.world_position.current_area_id
        location_data = gs.world_position.current_location_data
        
        if not location_data or "areas" not in location_data:
            return None
        
        areas = location_data.get("areas", {})
        if current_area_id not in areas:
            return None
        
        # Find the first available object with matching name
        if not (objects := areas[current_area_id].get("objects", [])):
            return None
        
        if available_obj := next(
            (obj for obj in objects 
             if obj.get("name", "").lower() == object_name.lower() and 
             (not obj.get("depleted", False) and not obj.get("searched", False) and 
              not obj.get("chopped", False) and not obj.get("wood_taken", False))),
            None
        ):
            return available_obj
        
        # If no available objects found, return the first match anyway (for error messages)
        return next(
            (obj for obj in objects if obj.get("name", "").lower() == object_name.lower()),
            None
        )
    
    def _apply_rest_benefit(self, rest_bonus: int = 2):
        """Apply rest benefit to character fatigue/health"""
        if self.game_engine and self.game_engine.game_state:
            character = self.game_engine.game_state.character
            player_state = self.game_engine.game_state.player_state
            
            # Heal HP based on rest quality
            heal_amount = rest_bonus
            character.hp = min(character.max_hp, character.hp + heal_amount)
            
            # Reduce fatigue if system exists
            if hasattr(player_state, 'fatigue'):
                player_state.fatigue = max(0, player_state.fatigue - rest_bonus * 10)
