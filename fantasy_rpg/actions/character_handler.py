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
    
    def handle_equip(self, item_id: str, slot: str = None) -> ActionResult:
        """Handle equipping an item from inventory
        
        CRITICAL: Does NOT log directly! Returns ActionResult with metadata (item_equipped, item_type).
        The UI calls action_logger.log_action_result() which handles NLP message generation.
        This ensures proper message ordering: command appears before the action message.
        
        Args:
            item_id: ID of item to equip
            slot: Optional specific slot to equip to
            
        Returns:
            ActionResult with item_equipped metadata for ActionLogger to process
        """
        if not self.game_engine or not self.game_engine.is_initialized:
            return ActionResult(False, "Game engine not available.")
        
        gs = self.game_engine.game_state
        character = gs.character
        
        # Find item in inventory using next() instead of for-loop
        item = next(
            (inv_item for inv_item in character.inventory.items if inv_item.item_id == item_id),
            None
        )
        
        if not item:
            return ActionResult(False, f"Item '{item_id}' not found in inventory.")
        
        # Determine slot if not provided
        if not slot:
            slot = self._determine_equip_slot(item)
            if not slot:
                return ActionResult(False, f"Cannot determine equipment slot for {item.name}.")
        
        # Attempt to equip - character.equip_item returns bool only
        # We need to call equipment.equip_item directly to get the message
        if not character.equipment:
            from fantasy_rpg.core.equipment import Equipment
            character.equipment = Equipment()
        
        success, message = character.equipment.equip_item(item, slot, character)
        
        if success:
            # Recalculate stats after equipping
            character.recalculate_derived_stats()
            
            # Remove from inventory
            character.inventory.remove_item(item_id, 1)
            
            # Return success with metadata - UI will handle NLP logging
            return ActionResult(
                success=True,
                message="",  # Empty - equipment event handler will create NLP message
                time_passed=0.0,
                item_equipped=item.name,
                item_type=item.item_type,
                slot=slot
            )
        
        return ActionResult(False, message)
    
    def handle_unequip(self, slot: str) -> ActionResult:
        """Handle unequipping an item from a slot
        
        CRITICAL: Does NOT log directly! Returns ActionResult with metadata (item_unequipped, item_type).
        The UI calls action_logger.log_action_result() which handles NLP message generation.
        This ensures proper message ordering: command appears before the action message.
        
        Args:
            slot: The equipment slot to unequip from
        
        Returns:
            ActionResult with item_unequipped metadata for ActionLogger to process
        """
        if not self.game_engine or not self.game_engine.is_initialized:
            return ActionResult(False, "Game engine not available.")
        
        gs = self.game_engine.game_state
        character = gs.character
        
        # Check if equipment exists
        if not character.equipment:
            return ActionResult(False, "No equipment system initialized.")
        
        # Attempt to unequip - call equipment.unequip_item directly to get message
        unequipped_item, message = character.equipment.unequip_item(slot)
        
        if unequipped_item:
            # Recalculate stats after unequipping
            character.recalculate_derived_stats()
            
            # Ensure inventory exists
            if not hasattr(character, 'inventory') or character.inventory is None:
                character.initialize_inventory()
            
            # Add back to inventory
            if hasattr(character, 'inventory') and character.inventory is not None:
                # Ensure item has proper attributes for inventory
                if not unequipped_item.item_id:
                    import uuid
                    unequipped_item.item_id = f"{unequipped_item.name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
                unequipped_item.quantity = 1
                
                added = character.inventory.add_item(unequipped_item)
                
                if added:
                    # Return success with metadata - UI will handle NLP logging
                    return ActionResult(
                        success=True,
                        message="",  # Empty - equipment event handler will create NLP message
                        time_passed=0.0,
                        item_unequipped=unequipped_item.name,
                        item_type=unequipped_item.item_type,
                        slot=slot
                    )
                else:
                    return ActionResult(False, f"Unequipped {unequipped_item.name} but couldn't add to inventory (weight limit?)")
            else:
                return ActionResult(False, f"Unequipped {unequipped_item.name} but no inventory to return to")
        else:
            return ActionResult(False, message)
    
    # Helper methods
    def _determine_equip_slot(self, item) -> str:
        """Determine which slot an item should be equipped to"""
        if not item:
            return None
        
        # Use item's slot property if available
        if hasattr(item, 'slot') and item.slot:
            # Map "hand" to "main_hand", "ring" to "ring_1" for compatibility
            return {'hand': 'main_hand', 'ring': 'ring_1'}.get(item.slot, item.slot)
        
        # Fallback based on item type
        type_to_slot = {
            'weapon': 'main_hand',
            'shield': 'off_hand',
            'armor': 'body'
        }
        return type_to_slot.get(item.item_type)
    
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
        
        # Get objects from current area
        objects = areas[current_area_id].get("objects", [])
        if not objects:
            return None
        
        # Find the first available object with matching name, then check availability
        fallback_obj = None
        for obj in objects:
            if obj.get("name", "").lower() == object_name.lower():
                # Return if available, otherwise save as fallback
                if not (obj.get("depleted", False) or obj.get("searched", False) or
                       obj.get("chopped", False) or obj.get("wood_taken", False)):
                    return obj
                # Save for fallback (non-available but matching name)
                fallback_obj = obj
        
        # Return fallback object (for error messages) if found
        return fallback_obj
    
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
