"""
Fantasy RPG - Movement Coordinator

Handles all player movement between hexes in the overworld, including:
- Hex-to-hex travel with terrain-based timing
- Exposure and survival effects during travel
- Weather updates on location change
- Travel time calculations
"""

from typing import Tuple, Optional, Dict, Any
import random


class MovementCoordinator:
    """Manages player movement between hexes and travel mechanics"""
    
    def __init__(self, game_engine):
        """
        Initialize MovementCoordinator.
        
        Args:
            game_engine: Reference to main GameEngine for accessing game state
        """
        self.game_engine = game_engine
    
    def move_player(self, direction: str) -> Tuple[bool, str]:
        """
        Handle player movement between hexes.
        
        Args:
            direction: Direction to move ("north", "south", "east", "west", etc.)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.game_engine.is_initialized or not self.game_engine.game_state:
            return False, "Game not initialized."
        
        gs = self.game_engine.game_state
        
        # Exit current location if in one
        if gs.world_position.current_location_id:
            gs.world_position.current_location_id = None
            gs.world_position.current_location_data = None
            gs.world_position.current_area_id = "entrance"
        
        # Get current coordinates and calculate target coordinates
        current_coords = gs.world_position.coords
        if not current_coords:
            return False, "Invalid current position."
        
        target_coords = self._calculate_target_coords(current_coords, direction)
        
        if not target_coords:
            return False, f"Cannot move {direction} from here."
        
        # Convert to hex IDs for WorldCoordinator compatibility
        current_hex_id = f"{current_coords[0]:02d}{current_coords[1]:02d}"
        target_hex_id = f"{target_coords[0]:02d}{target_coords[1]:02d}"
        
        # Validate movement is possible
        if not self.game_engine.world_coordinator.can_travel_to_hex(current_hex_id, target_hex_id):
            return False, f"Cannot travel {direction} - the way is blocked or too far."
        
        # Check if character is capable of movement
        if gs.character.hp <= 0:
            return False, "You are unconscious and cannot move."
        
        # Calculate travel time based on terrain and conditions
        travel_time = self._calculate_travel_time(current_hex_id, target_hex_id)
        
        # Use existing time system to advance time (which handles survival effects)
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("travel", duration_override=travel_time)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Travel failed.")
        else:
            # Fallback: just advance game time
            self._advance_game_time(travel_time)
        
        # Move to new hex
        new_hex_data = self.game_engine.world_coordinator.get_hex_info(target_hex_id)
        new_locations = self.game_engine.world_coordinator.get_hex_locations(target_hex_id)
        
        gs.world_position.hex_id = target_hex_id
        gs.world_position.coords = target_coords
        gs.world_position.hex_data = new_hex_data
        gs.world_position.available_locations = new_locations
        
        # Generate new weather for the new location
        climate_info = self.game_engine.world_coordinator.get_climate_info(target_hex_id)
        if climate_info:
            base_temp = climate_info.get("base_temperature", 65.0)
            climate_type = climate_info.get("zone_type", "temperate")
        else:
            base_temp = 65.0
            climate_type = "temperate"
        
        from world.weather_core import generate_weather_state
        new_weather = generate_weather_state(
            base_temp, 
            gs.game_time.season, 
            climate_type
        )
        gs.current_weather = new_weather
        
        # Update PlayerState weather so survival effects work properly
        gs.player_state.update_weather(new_weather)
        
        # Update player state location to match new world position
        gs.player_state.current_hex = target_hex_id
        gs.player_state.current_location = new_hex_data.get("name", "Unknown Location")
        
        # Synchronize game time with player state time
        gs.game_time.day = gs.player_state.game_day
        gs.game_time.hour = int(gs.player_state.game_hour)
        gs.game_time.minute = int((gs.player_state.game_hour % 1) * 60)
        gs.game_time.season = gs.player_state.game_season
        
        # Build natural language response
        travel_desc = self._get_travel_description(direction, new_hex_data, travel_time)
        
        # Check if character died during travel
        if gs.character.hp <= 0:
            self.game_engine._notify_ui_state_change("character_death")
            return False, f"{travel_desc}\n\n💀 You collapsed and died during the journey!"
        
        # Notify UI of location change
        self.game_engine._notify_ui_state_change("location_change")
        
        return True, travel_desc
    
    def _calculate_target_coords(self, current_coords: Tuple[int, int], direction: str) -> Optional[Tuple[int, int]]:
        """
        Calculate target coordinates based on direction.
        
        Args:
            current_coords: Current (x, y) coordinates
            direction: Direction to move
        
        Returns:
            Target (x, y) coordinates or None if invalid
        """
        x, y = current_coords
        world_size = self.game_engine.world_coordinator.world_size
        
        # Handle world_size as tuple or int
        if isinstance(world_size, tuple):
            max_x, max_y = world_size
        else:
            max_x = max_y = world_size
        
        # Map direction to coordinate changes
        direction_map = {
            "north": (0, -1),
            "south": (0, 1),
            "east": (1, 0),
            "west": (-1, 0),
            "northeast": (1, -1),
            "northwest": (-1, -1),
            "southeast": (1, 1),
            "southwest": (-1, 1),
            # Shortcuts
            "n": (0, -1),
            "s": (0, 1),
            "e": (1, 0),
            "w": (-1, 0),
            "ne": (1, -1),
            "nw": (-1, -1),
            "se": (1, 1),
            "sw": (-1, 1)
        }
        
        if direction.lower() not in direction_map:
            return None
        
        dx, dy = direction_map[direction.lower()]
        new_x = x + dx
        new_y = y + dy
        
        # Validate coordinates are within world bounds
        if 0 <= new_x < max_x and 0 <= new_y < max_y:
            return (new_x, new_y)
        
        return None
    
    def _calculate_travel_time(self, current_hex_id: str, target_hex_id: str) -> float:
        """
        Calculate travel time between hexes based on terrain.
        
        Args:
            current_hex_id: Starting hex ID
            target_hex_id: Destination hex ID
        
        Returns:
            Travel time in hours
        """
        # Get terrain info for both hexes
        target_hex = self.game_engine.world_coordinator.get_hex_info(target_hex_id)
        terrain = target_hex.get("terrain", "plains")
        
        # Base travel times by terrain (in hours)
        terrain_times = {
            "plains": 1.0,
            "forest": 2.0,
            "hills": 2.5,
            "mountains": 4.0,
            "swamp": 3.0,
            "desert": 2.0,
            "tundra": 2.5,
            "water": 0.5,  # Assuming river/lake crossing
            "ocean": 8.0   # Much slower if actually traversable
        }
        
        base_time = terrain_times.get(terrain, 2.0)
        
        # Weather modifiers
        gs = self.game_engine.game_state
        weather = gs.current_weather
        
        weather_modifier = 1.0
        if hasattr(weather, 'precipitation'):
            if weather.precipitation in ["heavy_rain", "storm"]:
                weather_modifier = 1.5
            elif weather.precipitation in ["rain", "snow"]:
                weather_modifier = 1.2
        
        # Wind modifier
        if hasattr(weather, 'wind_speed') and weather.wind_speed > 30:
            weather_modifier *= 1.2
        
        return base_time * weather_modifier
    
    def _get_travel_description(self, direction: str, hex_data: Dict[str, Any], travel_time: float) -> str:
        """
        Generate natural language description of travel.
        
        Args:
            direction: Direction traveled
            hex_data: Data about destination hex
            travel_time: Time taken to travel
        
        Returns:
            Formatted travel description
        """
        terrain = hex_data.get("terrain", "plains")
        biome = hex_data.get("biome", "temperate")
        hex_name = hex_data.get("name", "Unknown Area")
        
        # Convert travel time to readable format
        hours = int(travel_time)
        minutes = int((travel_time - hours) * 60)
        
        if hours > 0 and minutes > 0:
            time_str = f"{hours} hour{'s' if hours != 1 else ''} and {minutes} minutes"
        elif hours > 0:
            time_str = f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            time_str = f"{minutes} minutes"
        
        # Build description
        description = f"You travel {direction} for {time_str}.\n\n"
        description += f"You arrive at {hex_name} - a {biome} {terrain} region."
        
        # Add location count if available
        num_locations = len(hex_data.get("locations", []))
        if num_locations > 0:
            description += f"\n\nYou can see {num_locations} location{'s' if num_locations != 1 else ''} nearby."
        
        return description
    
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
