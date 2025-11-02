"""
Fantasy RPG - Movement Handler

Handles all movement and navigation commands by delegating to MovementCoordinator and LocationCoordinator.
This is a thin wrapper that:
1. Parses user input
2. Validates preconditions
3. Delegates to game_engine.movement or game_engine.locations
4. Wraps results in ActionResult

All actual game logic lives in:
- fantasy_rpg/game/movement_coordinator.py (overworld hex movement)
- fantasy_rpg/game/location_coordinator.py (location entry/exit, inter-location travel)
"""

from .base_handler import BaseActionHandler, ActionResult


class MovementHandler(BaseActionHandler):
    """Handler for movement and navigation commands - delegates to coordinators"""
    
    def handle_movement(self, *args) -> ActionResult:
        """Handle movement commands - delegates to MovementCoordinator or LocationCoordinator"""
        if not self.game_engine:
            return ActionResult(False, "Movement system not available.")
        
        # Determine direction from command and args
        parts = [arg for arg in args if arg]
        command = getattr(self, '_current_command', '')
        
        # Map commands to directions
        direction_map = {
            'north': 'north', 'n': 'north',
            'south': 'south', 's': 'south', 
            'east': 'east', 'e': 'east',
            'west': 'west', 'w': 'west',
            'northeast': 'northeast', 'ne': 'northeast',
            'northwest': 'northwest', 'nw': 'northwest',
            'southeast': 'southeast', 'se': 'southeast',
            'southwest': 'southwest', 'sw': 'southwest'
        }
        
        direction = None
        
        # Check if command itself is a direction
        if command in direction_map:
            direction = direction_map[command]
        # Check if first argument is a direction (for "go north")
        elif parts and parts[0] in direction_map:
            direction = direction_map[parts[0]]
        else:
            return ActionResult(False, "Please specify a direction (north, south, east, west, etc.)")
        
        # Check if player is inside a location
        gs = self.game_engine.game_state
        if gs.world_position.current_location_id:
            # Player is inside a location - delegate to LocationCoordinator
            try:
                success, message = self.game_engine.locations.move_between_locations(direction)
                
                if success and self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("travel", duration_override=0.5)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Movement interrupted."))
                
                return ActionResult(
                    success=True,
                    message=message,
                    time_passed=0.5,
                    action_type="location_movement"
                )
            except Exception as e:
                return ActionResult(False, f"Movement failed: {str(e)}")
        
        # Delegate to MovementCoordinator for overworld movement
        try:
            success, message = self.game_engine.movement.move_player(direction)
            
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("travel", duration_override=2.0)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Movement interrupted."))
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=2.0,
                action_type="movement",
                movement_type="overworld",
                direction=direction
            )
                
        except Exception as e:
            return ActionResult(False, f"Movement failed: {str(e)}")

    
    def _update_location_shortcuts(self):
        """Update shortkey manager with current location's objects"""
        if not self.game_engine or not self.game_engine.is_initialized:
            return
        
        gs = self.game_engine.game_state
        
        # Only update if in a location
        if not gs.world_position.current_location_id:
            return
        
        location_data = gs.world_position.current_location_data
        if not location_data:
            return
        
        # Get objects from current area
        areas = location_data.get("areas", {})
        current_area_id = gs.world_position.current_area_id
        
        if current_area_id not in areas:
            return
        
        area_data = areas[current_area_id]
        objects = area_data.get("objects", [])
        
        # Update shortkey manager
        from .shortkey_manager import get_shortkey_manager
        shortkey_manager = get_shortkey_manager()
        shortkey_manager.assign_object_shortcuts_from_data(objects)
    
    def handle_look(self, *args) -> ActionResult:
        """Handle look command through GameEngine"""
        if not self.game_engine:
            return ActionResult(False, "World system not available.")
        
        try:
            gs = self.game_engine.game_state
            
            # Check if player is inside a location
            if gs.world_position.current_location_id:
                # Update shortcuts for current location
                self._update_location_shortcuts()
                
                # Inside a location - show location description and contents
                location_data = gs.world_position.current_location_data
                if location_data:
                    location_name = location_data.get("name", "Unknown Location")
                    location_desc = location_data.get("description", "An unremarkable area.")
                    description = f"**{location_name}**\n\n{location_desc}"
                    
                    # Add location contents
                    contents = self.game_engine.get_location_contents()
                    if contents:
                        description += f"\n\n{contents}"
                else:
                    description = "You are inside a location, but cannot see much."
            else:
                # In overworld - show hex description
                description = self.game_engine.get_hex_description()
            
            return ActionResult(
                success=True,
                message=description,
                time_passed=0.0,  # Looking is instant
                action_type="observation"
            )
        except Exception as e:
            return ActionResult(False, f"Cannot look around: {str(e)}")
    
    def handle_enter_location(self, *args) -> ActionResult:
        """Handle entering a location - delegates to LocationCoordinator"""
        if not self.game_engine:
            return ActionResult(False, "Location system not available.")
        
        try:
            # Delegate to LocationCoordinator
            success, message = self.game_engine.locations.enter_location()
            
            if success:
                # Update shortkey mappings for objects in this location
                self._update_location_shortcuts()
                
                # Use time system
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("look", duration_override=0.25)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Entry interrupted."))
                
                return ActionResult(
                    success=True,
                    message=message,
                    time_passed=0.25,
                    action_type="location_entry"
                )
            else:
                return ActionResult(False, message)
                
        except Exception as e:
            return ActionResult(False, f"Failed to enter location: {str(e)}")
    
    def handle_exit_location(self, *args) -> ActionResult:
        """Handle exiting current location - delegates to LocationCoordinator"""
        if not self.game_engine:
            return ActionResult(False, "Location system not available.")
        
        try:
            # Delegate to LocationCoordinator
            success, message = self.game_engine.locations.exit_location()
            
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("look", duration_override=0.25)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Exit interrupted."))
            
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25,
                action_type="location_exit"
            )
                
        except Exception as e:
            return ActionResult(False, f"Failed to exit location: {str(e)}")
    
    def handle_wait(self, *args) -> ActionResult:
        """Handle waiting/passing time with different duration options"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Wait how long? Options: quick (15min), short (30min), medium (1hr), long (3hr), extended (8hr)")
        
        duration_arg = args[0].lower()
        
        # Map duration arguments to hours (pure time passing, no activity effects)
        duration_map = {
            # Quick wait (15 minutes)
            "quick": 0.25,
            "15min": 0.25,
            "15": 0.25,
            
            # Short wait (30 minutes)
            "short": 0.5,
            "30min": 0.5,
            "30": 0.5,
            
            # Medium wait (1 hour)
            "medium": 1.0,
            "1hr": 1.0,
            "1h": 1.0,
            "1": 1.0,
            "hour": 1.0,
            
            # Long wait (3 hours)
            "long": 3.0,
            "3hr": 3.0,
            "3h": 3.0,
            "3": 3.0,
            
            # Extended wait (8 hours)
            "extended": 8.0,
            "8hr": 8.0,
            "8h": 8.0,
            "8": 8.0,
            "night": 8.0,
        }
        
        if duration_arg not in duration_map:
            available_options = ["quick (15min)", "short (30min)", "medium (1hr)", "long (3hr)", "extended (8hr)"]
            return ActionResult(False, f"Unknown duration '{duration_arg}'. Options: {', '.join(available_options)}")
        
        duration_hours = duration_map[duration_arg]
        
        try:
            # Use time system with "wait" activity (ensures condition effects are applied)
            time_result = None
            if self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("wait", duration_override=duration_hours)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Wait interrupted."))
            
            # Format duration for display
            if duration_hours < 1:
                duration_str = f"{int(duration_hours * 60)} minutes"
            elif duration_hours == 1:
                duration_str = "1 hour"
            else:
                duration_str = f"{duration_hours} hours"
            
            # Create descriptive message based on duration
            if duration_hours <= 0.25:
                activity_desc = "take a brief moment to rest"
            elif duration_hours <= 0.5:
                activity_desc = "rest quietly for a short while"
            elif duration_hours <= 1:
                activity_desc = "rest comfortably for an hour"
            elif duration_hours <= 3:
                activity_desc = "rest deeply for several hours"
            else:
                activity_desc = "rest extensively through an extended period"
            
            message = f"You {activity_desc}, letting {duration_str} pass peacefully."
            
            # Add environmental context
            if self.game_engine.game_state.world_position.current_location_id:
                message += f"\nYou remain in the {self.game_engine.game_state.world_position.current_location_data.get('name', 'location')} during your rest."
            else:
                message += f"\nYou rest in the wilderness of hex {self.game_engine.game_state.world_position.hex_id}."
            
            # Include condition messages and debug output from time system
            return ActionResult.from_time_result(
                time_result,
                success=True,
                message=message,
                action_type="wait"
            )
            
        except Exception as e:
            return ActionResult(False, f"Failed to wait: {str(e)}")
    
    # Store current command for direction detection
    _current_command = ''
