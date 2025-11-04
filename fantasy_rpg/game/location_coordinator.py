"""
Fantasy RPG - Location Coordinator

Handles all location-related operations including:
- Entering and exiting locations
- Moving between locations within a hex
- Area navigation within locations
- Location persistence and generation
"""

from typing import Tuple, Optional, Dict, Any, List
import random


class LocationCoordinator:
    """Manages location entry, exit, and inter-location travel"""
    
    def __init__(self, game_engine):
        """
        Initialize LocationCoordinator.
        
        Args:
            game_engine: Reference to main GameEngine for accessing game state
        """
        self.game_engine = game_engine
    
    def enter_location(self, location_id: str = None) -> Tuple[bool, str]:
        """
        Enter a location within the current hex.
        
        Args:
            location_id: ID of location to enter (if None, enter first available)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.game_engine.is_initialized or not self.game_engine.game_state:
            return False, "Game not initialized."
        
        gs = self.game_engine.game_state
        
        # Check if already in a location
        if gs.world_position.current_location_id:
            return False, "You are already inside a location. Use 'exit' to leave first."
        
        # Get available locations in current hex (fresh from WorldCoordinator)
        current_hex_id = gs.world_position.hex_id
        available_locations = self.game_engine.world_coordinator.get_hex_locations(current_hex_id)
        if not available_locations:
            return False, "There are no locations to enter in this hex."
        
        # Select location to enter
        target_location = None
        if location_id:
            # Find specific location by ID
            for loc in available_locations:
                if loc.get("id") == location_id or loc.get("name", "").lower() == location_id.lower():
                    target_location = loc
                    break
            if not target_location:
                return False, f"Location '{location_id}' not found in this hex."
        else:
            # Enter first available location
            target_location = available_locations[0]
        
        # Generate or load persistent location data
        location_data = self._get_or_generate_location_data(target_location)
        
        # Enter the location
        gs.world_position.current_location_id = target_location.get("id")
        gs.world_position.current_location_data = location_data
        gs.world_position.current_area_id = location_data.get("starting_area", "entrance")
        
        # Build entry message
        location_name = location_data.get("name", "Unknown Location")
        location_desc = location_data.get("description", "An unremarkable area.")
        
        entry_message = f"You enter {location_name}.\n\n{location_desc}"
        
        # Add object information if available
        areas = location_data.get("areas", {})
        starting_area_id = location_data.get("starting_area", "entrance")
        if starting_area_id in areas and (objects := areas[starting_area_id].get("objects", [])):
            object_names = [obj.get("name", "something") for obj in objects[:3]]  # Show first 3
            suffix = ", and more." if len(objects) > 3 else "."
            entry_message += f"\n\nYou notice {', '.join(object_names)}{suffix}"
        
        # Debug location info
        self._debug_location_info(location_data)
        
        # Notify UI of location entry
        self.game_engine._notify_ui_state_change("location_entry")
        
        return True, entry_message
    
    def exit_location(self) -> Tuple[bool, str]:
        """
        Exit current location back to hex overworld.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.game_engine.is_initialized or not self.game_engine.game_state:
            return False, "Game not initialized."
        
        gs = self.game_engine.game_state
        
        # Check if in a location
        if not gs.world_position.current_location_id:
            return False, "You are not inside a location."
        
        # Check if location allows exit
        location_data = gs.world_position.current_location_data
        if location_data and not location_data.get("exit_flag", True):
            return False, "You cannot exit this location directly to the overworld."
        
        # Exit to overworld
        location_name = location_data.get("name", "the location") if location_data else "the location"
        gs.world_position.current_location_id = None
        gs.world_position.current_location_data = None
        gs.world_position.current_area_id = "entrance"
        
        # Get current hex description for context
        hex_name = gs.world_position.hex_data.get("name", "the area")
        
        # Notify UI of location exit
        self.game_engine._notify_ui_state_change("location_exit")
        
        return True, f"You exit {location_name} and return to {hex_name}."
    
    def _find_current_location_index(self, available_locations: List[Dict], current_location_id: str) -> Optional[int]:
        """Find the index of current location in available locations list"""
        return next(
            (i for i, loc in enumerate(available_locations) if loc.get("id") == current_location_id),
            None
        )
    
    def _process_location_travel(self, travel_time: float) -> Tuple[bool, str]:
        """Process time passage and survival effects for location travel"""
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("travel", duration_override=travel_time)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Travel failed.")
        else:
            # Fallback: just advance game time
            self._advance_game_time(travel_time)
        return True, ""
    
    def _build_location_arrival_message(self, target_location: Dict, target_location_data: Dict, 
                                       direction: str, travel_time: float) -> str:
        """Build descriptive message for arriving at a location"""
        target_name = target_location.get("name", "Unknown Location")
        target_desc = target_location_data.get("description", "An unremarkable area.")
        time_desc = self._get_location_travel_description(travel_time)
        
        message = f"You travel {direction} to {target_name}.{time_desc}\n\n{target_desc}"
        
        # Show objects in new location
        areas = target_location_data.get("areas", {})
        starting_area_id = target_location_data.get("starting_area", "entrance")
        if starting_area_id in areas and (objects := areas[starting_area_id].get("objects", [])):
            object_names = [obj.get("name", "something") for obj in objects[:3]]
            suffix = ", and more." if len(objects) > 3 else "."
            message += f"\n\nYou notice {', '.join(object_names)}{suffix}"
        
        return message
    
    def move_between_locations(self, direction: str) -> Tuple[bool, str]:
        """
        Move between different locations within the same hex.
        
        Args:
            direction: Direction to travel
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.game_engine.is_initialized or not self.game_engine.game_state:
            return False, "Game not initialized."
        
        gs = self.game_engine.game_state
        
        # Check if player is inside a location
        if not gs.world_position.current_location_id:
            return False, "You are not inside a location."
        
        # Get all locations in current hex
        available_locations = gs.world_position.available_locations
        
        if not available_locations or len(available_locations) < 2:
            return False, "There are no other locations to travel to from here."
        
        # Find current location in the list
        current_location_index = self._find_current_location_index(
            available_locations, 
            gs.world_position.current_location_id
        )
        
        if current_location_index is None:
            return False, "Current location not found in available locations."
        
        # Create persistent location graph
        location_graph = self._create_location_graph(available_locations, current_location_index)
        
        # Check if movement in requested direction is possible
        if direction not in location_graph:
            available_directions = list(location_graph.keys())
            return False, (
                f"You cannot go {direction} from here. Available directions: {', '.join(available_directions)}"
                if available_directions else
                "There are no exits from this location. Use 'exit' to return to the overworld."
            )
        
        # Get target location
        target_location = location_graph[direction]
        
        # Check if character is capable of movement
        if gs.character.hp <= 0:
            return False, "You are unconscious and cannot move."
        
        # Calculate and process travel time
        travel_time = self._calculate_location_travel_time()
        success, error_msg = self._process_location_travel(travel_time)
        if not success:
            return False, error_msg
        
        # Move to target location
        target_location_data = self._get_or_generate_location_data(target_location)
        
        # Update player position
        gs.world_position.current_location_id = target_location.get("id")
        gs.world_position.current_location_data = target_location_data
        gs.world_position.current_area_id = target_location_data.get("starting_area", "entrance")
        
        # Debug location info for location-to-location movement
        self._debug_location_info(target_location_data)
        
        # Build movement message
        message = self._build_location_arrival_message(
            target_location, target_location_data, direction, travel_time
        )
        
        # Check if character died during travel
        if gs.character.hp <= 0:
            self.game_engine._notify_ui_state_change("character_death")
            return False, f"{message}\n\n💀 You collapsed and died during the journey!"
        
        # Notify UI of location movement
        self.game_engine._notify_ui_state_change("location_movement")
        
        return True, message
    
    def change_area(self, direction: str) -> Tuple[bool, str]:
        """
        Move between areas within a location.
        
        Args:
            direction: Direction to move (n, s, e, w, etc.)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.game_engine.is_initialized or not self.game_engine.game_state:
            return False, "Game not initialized."
        
        gs = self.game_engine.game_state
        
        # Must be in a location
        if not gs.world_position.current_location_id:
            return False, "You are not inside a location."
        
        # Get current area
        location_data = gs.world_position.current_location_data
        if not location_data:
            return False, "Location data not available."
        
        areas = location_data.get("areas", {})
        current_area_id = gs.world_position.current_area_id
        
        if current_area_id not in areas:
            return False, "Current area not found."
        
        current_area = areas[current_area_id]
        exits = current_area.get("exits", {})
        
        # Normalize direction
        direction_map = {
            "north": "n", "south": "s", "east": "e", "west": "w",
            "n": "n", "s": "s", "e": "e", "w": "w"
        }
        
        normalized_direction = direction_map.get(direction.lower())
        if not normalized_direction:
            return False, f"Invalid direction: {direction}"
        
        # Check if exit exists
        if normalized_direction not in exits:
            available = [d for d in ["n", "s", "e", "w"] if d in exits]
            if available:
                return False, f"No exit {direction}. Available: {', '.join(available)}"
            return False, "No exits available from this area."
        
        # Move to new area
        new_area_id = exits[normalized_direction]
        
        if new_area_id not in areas:
            return False, f"Target area '{new_area_id}' not found."
        
        gs.world_position.current_area_id = new_area_id
        new_area = areas[new_area_id]
        
        # Build description
        area_name = new_area.get("name", "an area")
        area_desc = new_area.get("description", "An unremarkable space.")
        
        message = f"You move {direction} to {area_name}.\n\n{area_desc}"
        
        # List objects
        if objects := new_area.get("objects", []):
            object_names = [obj.get("name", "something") for obj in objects[:3]]
            suffix = ", and more." if len(objects) > 3 else "."
            message += f"\n\nYou see {', '.join(object_names)}{suffix}"
        
        return True, message
    
    def _create_location_graph(self, locations: List[Dict], current_index: int) -> Dict[str, Dict]:
        """
        Create a persistent bidirectional graph of locations.
        
        Locations are arranged in a consistent grid pattern based on their IDs,
        ensuring the same locations are always in the same directions.
        
        Args:
            locations: List of available locations
            current_index: Index of current location
        
        Returns:
            Dictionary mapping directions to location objects
        """
        gs = self.game_engine.game_state
        hex_id = gs.world_position.hex_id
        
        # Create unique key for this hex's location graph
        graph_key = f"location_graph_{hex_id}"
        
        # Initialize persistent location graphs if not exists
        if not hasattr(gs, 'persistent_location_graphs'):
            gs.persistent_location_graphs = {}
        
        # If we already have a graph for this hex, use it
        if graph_key in gs.persistent_location_graphs:
            full_graph = gs.persistent_location_graphs[graph_key]
            current_location_id = locations[current_index].get("id")
            return full_graph.get(current_location_id, {})
        
        # Create new persistent bidirectional graph for this hex
        full_graph = {}
        
        # Create a stable arrangement of locations in a grid pattern
        # This ensures consistent directional relationships
        location_positions = {}
        
        # Arrange locations in a simple grid pattern based on their IDs (for consistency)
        sorted_locations = sorted(locations, key=lambda x: x.get("id", ""))
        
        # Calculate grid dimensions
        num_locations = len(sorted_locations)
        grid_size = max(2, int(num_locations ** 0.5) + 1)
        
        # Assign grid positions
        for i, location in enumerate(sorted_locations):
            row = i // grid_size
            col = i % grid_size
            location_positions[location.get("id")] = (row, col)
        
        # Build bidirectional connections based on grid positions
        for location in sorted_locations:
            location_id = location.get("id")
            current_pos = location_positions[location_id]
            connections = {}
            
            # Check all four directions
            directions = {
                "north": (-1, 0),
                "south": (1, 0),
                "east": (0, 1),
                "west": (0, -1)
            }
            
            for direction, (row_offset, col_offset) in directions.items():
                target_pos = (current_pos[0] + row_offset, current_pos[1] + col_offset)
                
                # Find location at target position
                for other_location in sorted_locations:
                    other_id = other_location.get("id")
                    if other_id != location_id and location_positions[other_id] == target_pos:
                        connections[direction] = other_location
                        break
            
            full_graph[location_id] = connections
        
        # Store the persistent graph
        gs.persistent_location_graphs[graph_key] = full_graph
        
        # Return connections for current location
        current_location_id = locations[current_index].get("id")
        return full_graph.get(current_location_id, {})
    
    def _calculate_location_travel_time(self) -> float:
        """
        Calculate travel time between locations (fixed 30 minutes).
        
        Returns:
            Travel time in hours
        """
        return 0.5  # 30 minutes
    
    def _get_location_travel_description(self, travel_time: float) -> str:
        """
        Get natural language description of travel time.
        
        Args:
            travel_time: Time in hours
        
        Returns:
            Formatted time description
        """
        minutes = int(travel_time * 60)
        
        if minutes < 60:
            return f" (about {minutes} minutes)"
        
        hours, remaining_minutes = divmod(minutes, 60)
        if remaining_minutes > 0:
            minute_word = "minute" if remaining_minutes == 1 else "minutes"
            suffix = f" and {remaining_minutes} {minute_word}"
        else:
            suffix = ""
        hour_word = "hour" if hours == 1 else "hours"
        return f" (about {hours} {hour_word}{suffix})"
    
    def _get_or_generate_location_data(self, location_template: Dict[str, Any]) -> Dict[str, Any]:
        """Get persistent location data or generate it if first visit"""
        gs = self.game_engine.game_state
        location_id = location_template.get("id")
        hex_id = gs.world_position.hex_id
        
        # Create unique key for this location in this hex
        location_key = f"{hex_id}_{location_id}"
        
        # Check if we have persistent data for this location
        if not hasattr(gs, 'persistent_locations'):
            gs.persistent_locations = {}
        
        if location_key in gs.persistent_locations:
            # Return existing persistent data
            return gs.persistent_locations[location_key]
        
        # Use the location template directly (it's already a proper dictionary from WorldCoordinator)
        location_data = location_template.copy()  # Make a copy to avoid modifying the original
        
        # Store for persistence
        gs.persistent_locations[location_key] = location_data
        
        return location_data
    
    def _advance_game_time(self, hours: float):
        """Advance game time and update weather"""
        gs = self.game_engine.game_state
        
        # Add hours to game time
        total_minutes = int(hours * 60)
        gs.game_time.minute += total_minutes
        
        # Handle minute overflow
        while gs.game_time.minute >= 60:
            gs.game_time.minute -= 60
            gs.game_time.hour += 1
        
        # Handle hour overflow
        while gs.game_time.hour >= 24:
            gs.game_time.hour -= 24
            gs.game_time.day += 1
        
        # Update season (simplified - every 90 days)
        season_day = (gs.game_time.day - 1) % 360
        if season_day < 90:
            gs.game_time.season = "spring"
        elif season_day < 180:
            gs.game_time.season = "summer"
        elif season_day < 270:
            gs.game_time.season = "autumn"
        else:
            gs.game_time.season = "winter"
        
        # Update play time
        gs.play_time_minutes += total_minutes
    
    def _debug_location_info(self, location_data: Dict):
        """Debug location flags and properties"""
        try:
            from game.conditions import DEBUG_SHELTER
        except ImportError:
            DEBUG_SHELTER = False
            
        if not DEBUG_SHELTER or not location_data:
            return
            
        try:
            from actions.action_logger import get_action_logger
            action_logger = get_action_logger()
            
            debug_msg = self._build_location_debug_message(location_data)
            action_logger.log_message(debug_msg)
                
        except ImportError:
            pass
    
    def _build_location_debug_message(self, location_data: Dict) -> str:
        """Build debug message showing location flags and properties"""
        location_name = location_data.get("name", "Unknown Location")
        
        # Collect ALL flags that start with "provides_"
        all_flags = [
            key.replace("provides_", "")
            for key, value in location_data.items()
            if key.startswith("provides_") and value
        ]
        
        # Also check for other relevant flags
        other_flags = [
            f"{flag}:{location_data[flag]}"
            for flag in ["exit_flag", "spawn_weight", "size", "terrain", "type"]
            if flag in location_data
        ]
        
        debug_msg = f"🏠 {location_name}"
        debug_msg += f" | Provides: {', '.join(all_flags)}" if all_flags else " | No provides_ flags"
        
        if other_flags:
            debug_msg += f" | {', '.join(other_flags[:3])}"  # Show first 3 to avoid spam
        
        return debug_msg
