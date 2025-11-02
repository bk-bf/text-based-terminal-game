"""
Fantasy RPG - Game Engine

Central coordinator that manages all game systems and provides a unified interface
for game state management, world interaction, and system integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import random
from datetime import datetime
from enum import Enum

# Import existing systems
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import only non-circular dependencies at module level
from world.world_coordinator import WorldCoordinator
from world.weather_core import WeatherState, generate_weather_state

# Import location generator with fallback
try:
    from locations.location_generator import LocationGenerator
except ImportError:
    # Create a stub if location generator not available
    class LocationGenerator:
        def __init__(self):
            pass

# DON'T import Character, PlayerState, TimeSystem here - use late imports


@dataclass
class WorldPosition:
    """Player's position in the world"""
    hex_id: str
    hex_data: Dict[str, Any]
    available_locations: List[Dict[str, Any]] = field(default_factory=list)
    current_location_id: Optional[str] = None
    current_location_data: Optional[Dict[str, Any]] = None
    current_area_id: str = "entrance"  # Current area within location
    coords: Optional[Tuple[int, int]] = None  # Tuple coordinates for movement calculations


@dataclass
class GameTime:
    """Game time tracking"""
    year: int = 1000
    day: int = 1
    hour: int = 8  # Start at 8 AM
    minute: int = 0
    season: str = "spring"
    
    def get_time_string(self) -> str:
        """Get formatted time string"""
        period = "AM" if self.hour < 12 else "PM"
        display_hour = self.hour if self.hour <= 12 else self.hour - 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{self.minute:02d} {period}"
    
    def get_date_string(self) -> str:
        """Get formatted date string"""
        return f"Day {self.day}, Year {self.year} ({self.season.title()})"


@dataclass
class GameState:
    """Complete game state snapshot"""
    character: Any  # Use Any to avoid circular import
    player_state: Any  # Use Any to avoid circular import
    world_position: WorldPosition
    game_time: GameTime
    current_weather: WeatherState
    world_seed: int
    
    # Game session info
    created_at: datetime = field(default_factory=datetime.now)
    last_saved: Optional[datetime] = None
    play_time_minutes: int = 0


class GameEngine:
    """
    Central game coordinator that manages all systems and provides unified interface.
    
    This class serves as the single source of truth for game state and coordinates
    between all backend systems (character, world, survival, locations, etc.).
    """
    
    def __init__(self, world_size: Tuple[int, int] = (20, 20), skip_world_gen: bool = False):
        """Initialize GameEngine with world parameters"""
        self.world_size = world_size
        self.skip_world_gen = skip_world_gen
        self.world_coordinator = None
        self.location_generator = None
        self.time_system = None
        
        # Game state
        self.game_state: Optional[GameState] = None
        self.is_initialized = False
        
        # UI state change notification system
        self.ui_update_callbacks = []
        
        # GameEngine initialized - no logging needed for internal initialization
    
    def register_ui_update_callback(self, callback):
        """Register a callback function to be called when game state changes"""
        if callback not in self.ui_update_callbacks:
            self.ui_update_callbacks.append(callback)
    
    def unregister_ui_update_callback(self, callback):
        """Unregister a UI update callback"""
        if callback in self.ui_update_callbacks:
            self.ui_update_callbacks.remove(callback)
    
    def _notify_ui_state_change(self, change_type: str = "general"):
        """Notify all registered UI callbacks of state changes"""
        for callback in self.ui_update_callbacks:
            try:
                callback(change_type)
            except Exception as e:
                # Log UI callback errors through centralized logger if available
                try:
                    from actions.action_logger import get_action_logger
                    logger = get_action_logger()
                    logger.log_system_message(f"Error in UI callback: {e}")
                except:
                    pass  # Fallback: don't log if logger not available
    
    def new_game(self, character: Any, world_seed: Optional[int] = None) -> GameState:
        """
        Initialize a new game with the given character.
        
        Args:
            character: Created character to start the game with
            world_seed: Optional seed for world generation (random if None)
        
        Returns:
            GameState: Complete initial game state
        """
        # Late imports to avoid circular dependencies
        from game.player_state import PlayerState
        from game.time_system import TimeSystem
        
        # Generate world seed if not provided
        if world_seed is None:
            world_seed = random.randint(1, 1000000)
        
        # Debug logging for world generation
        try:
            from ..actions.action_logger import get_action_logger
            action_logger = get_action_logger()
            action_logger.log_system_message(f"GameEngine.new_game() called with seed {world_seed}")
        except ImportError:
            print(f"DEBUG: GameEngine.new_game() called with seed {world_seed}")
        
        # Clear any existing cached data to ensure fresh generation
        if hasattr(self, 'world_coordinator'):
            try:
                action_logger.log_system_message("Clearing existing WorldCoordinator")
            except:
                print("DEBUG: Clearing existing WorldCoordinator")
            del self.world_coordinator
        
        # Initialize world systems using WorldCoordinator (proper flow)
        try:
            action_logger.log_system_message("Creating new WorldCoordinator...")
        except:
            print("DEBUG: Creating new WorldCoordinator...")
        
        self.world_coordinator = WorldCoordinator(world_size=self.world_size, seed=world_seed)
        
        try:
            action_logger.log_system_message("WorldCoordinator created successfully")
        except:
            print("DEBUG: WorldCoordinator created successfully")
        
        # Generate the complete world through WorldCoordinator
        # Note: The WorldCoordinator should have a generate_world method that returns a World object
        # For now, we'll work with the existing hex_data system
        
        # Initialize player state and time system using real classes
        player_state = PlayerState(character=character, game_engine=self)
        self.time_system = TimeSystem(player_state)
        
        # Choose starting hex coordinates (center of world)
        starting_coords = (self.world_size[0] // 2, self.world_size[1] // 2)  # (10, 10) for 20x20 world
        starting_hex_id = f"{starting_coords[0]:02d}{starting_coords[1]:02d}"  # Convert to "1010"
        
        # Get hex data from the generated world
        hex_data = self.world_coordinator.get_hex_info(starting_hex_id)
        available_locations = self.world_coordinator.get_hex_locations(starting_hex_id)
        
        # Create world position with both coordinate formats
        world_position = WorldPosition(
            hex_id=starting_hex_id,
            hex_data=hex_data,
            available_locations=available_locations,
            coords=starting_coords
        )
        
        # Initialize game time from player state
        game_time = GameTime(
            year=1000,
            day=player_state.game_day,
            hour=int(player_state.game_hour),
            minute=int((player_state.game_hour % 1) * 60),
            season=player_state.game_season
        )
        
        # Generate initial weather
        climate_info = self.world_coordinator.get_climate_info(starting_hex_id)
        if climate_info:
            base_temp = climate_info.get("base_temperature", 65.0)
            climate_type = climate_info.get("zone_type", "temperate")
        else:
            base_temp = 65.0
            climate_type = "temperate"
        
        current_weather = generate_weather_state(
            base_temp, 
            game_time.season, 
            climate_type
        )
        
        # Update PlayerState weather so survival effects work from the start
        player_state.update_weather(current_weather)
        
        # Update player state location to match world position
        player_state.current_hex = starting_hex_id
        player_state.current_location = hex_data.get("name", "Unknown Location")
        
        # Create complete game state
        self.game_state = GameState(
            character=character,
            player_state=player_state,
            world_position=world_position,
            game_time=game_time,
            current_weather=current_weather,
            world_seed=world_seed
        )
        
        # Clear any persistent location data to ensure fresh generation
        self.game_state.persistent_locations = {}
        
        self.is_initialized = True
        
        return self.game_state
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get complete game status for UI display.
        
        Returns:
            Dictionary containing all current game status information
        """
        if not self.is_initialized or not self.game_state:
            return {"error": "Game not initialized"}
        
        gs = self.game_state
        
        # Get natural language descriptions from survival summary
        survival_summary = gs.player_state.get_survival_summary()
        
        # Extract individual descriptions from the survival levels
        hunger_level = gs.player_state.survival.get_hunger_level()
        thirst_level = gs.player_state.survival.get_thirst_level()
        temp_status = gs.player_state.survival.get_temperature_status()
        
        # Convert to natural language
        hunger_desc = hunger_level.name.replace('_', ' ').title()
        thirst_desc = thirst_level.name.replace('_', ' ').title()
        temp_desc = temp_status.name.replace('_', ' ').title()
        
        # Get weather description
        weather_desc = gs.current_weather.get_description()
        
        # Get active conditions
        try:
            from .conditions import get_conditions_manager
            conditions_manager = get_conditions_manager()
            active_conditions = conditions_manager.evaluate_conditions(gs.player_state)
            # Format conditions for display
            formatted_conditions = [conditions_manager.format_condition_for_display(cond) for cond in active_conditions]
        except Exception as e:
            print(f"Warning: Could not evaluate conditions: {e}")
            active_conditions = []
            formatted_conditions = []
        
        # Get location info
        location_info = "Overworld"
        if gs.world_position.current_location_id:
            location_info = gs.world_position.current_location_data.get("name", "Unknown Location")
        
        return {
            "character": {
                "name": gs.character.name,
                "race": gs.character.race,  # Already a string
                "character_class": gs.character.character_class,  # Already a string
                "level": gs.character.level,
                "hp": f"{gs.character.hp}/{gs.character.max_hp}",
                "ac": gs.character.armor_class
            },
            "survival": {
                "hunger": hunger_desc,
                "thirst": thirst_desc,
                "temperature": temp_desc
            },
            "location": {
                "hex": gs.world_position.hex_data["name"],
                "hex_id": gs.world_position.hex_id,
                "current_location": location_info,
                "available_locations": len(gs.world_position.available_locations)
            },
            "time": {
                "time": gs.game_time.get_time_string(),
                "date": gs.game_time.get_date_string()
            },
            "weather": weather_desc,
            "conditions": {
                "active": active_conditions,
                "formatted": formatted_conditions
            },
            "game_info": {
                "world_seed": gs.world_seed,
                "play_time": f"{gs.play_time_minutes // 60}h {gs.play_time_minutes % 60}m"
            }
        }
    
    def get_hex_description(self) -> str:
        """
        Get natural language description of current hex.
        
        Returns:
            Formatted description of current location and conditions
        """
        if not self.is_initialized or not self.game_state:
            return "Game not initialized."
        
        gs = self.game_state
        hex_data = gs.world_position.hex_data
        weather = gs.current_weather
        
        # Build description
        description_parts = []
        
        # Location name and basic description
        description_parts.append(f"**{hex_data['name']}**")
        description_parts.append(hex_data.get('description', 'An unremarkable area.'))
        
        # Weather conditions
        temp_c = (weather.temperature - 32) * 5/9
        weather_desc = f"The weather is {weather.temperature:.0f}°F ({temp_c:.0f}°C)"
        
        if weather.precipitation > 0:
            if weather.precipitation > 50:
                intensity = "heavy"
            elif weather.precipitation > 20:
                intensity = "moderate"
            else:
                intensity = "light"
            weather_desc += f" with {intensity} {weather.precipitation_type}"
        
        if weather.wind_speed > 15:
            weather_desc += f" and strong winds from the {weather.wind_direction.lower()}"
        elif weather.wind_speed > 5:
            weather_desc += f" with a breeze from the {weather.wind_direction.lower()}"
        
        description_parts.append(weather_desc + ".")
        
        # Available locations (get fresh data from WorldCoordinator)
        current_hex_id = gs.world_position.hex_id
        available_locations = self.world_coordinator.get_hex_locations(current_hex_id)
        
        if available_locations:
            location_count = len(available_locations)
            if location_count == 1:
                location_name = available_locations[0].get("name", "a location")
                description_parts.append(f"You can enter {location_name} here.")
            else:
                location_names = [loc.get("name", "a location") for loc in available_locations[:3]]
                if location_count > 3:
                    description_parts.append(f"You can enter {', '.join(location_names)}, and {location_count - 3} other locations here.")
                else:
                    description_parts.append(f"You can enter {', '.join(location_names)} here.")
        else:
            description_parts.append("There are no specific locations to explore in this hex.")
        
        # Show current location status
        if gs.world_position.current_location_id:
            current_location = gs.world_position.current_location_data
            location_name = current_location.get("name", "Unknown Location") if current_location else "a location"
            description_parts.append(f"\nYou are currently inside {location_name}.")
        
        return "\n\n".join(description_parts)
    
    def move_player(self, direction: str) -> Tuple[bool, str]:
        """
        Handle player movement between hexes.
        
        Args:
            direction: Direction to move ("north", "south", "east", "west", etc.)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
        # Exit current location if in one
        if gs.world_position.current_location_id:
            gs.world_position.current_location_id = None
            gs.world_position.current_location_data = None
            gs.world_position.current_area_id = "entrance"  # Reset to default
        
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
        if not self.world_coordinator.can_travel_to_hex(current_hex_id, target_hex_id):
            return False, f"Cannot travel {direction} - the way is blocked or too far."
        
        # Check if character is capable of movement
        if gs.character.hp <= 0:
            return False, "You are unconscious and cannot move."
        
        # Calculate travel time based on terrain and conditions
        travel_time = self._calculate_travel_time(current_hex_id, target_hex_id)
        
        # Use existing time system to advance time (which handles survival effects)
        if self.time_system:
            time_result = self.time_system.perform_activity("travel", duration_override=travel_time)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Travel failed.")
        else:
            # Fallback: just advance game time
            self._advance_game_time(travel_time)
        
        # Move to new hex
        new_hex_data = self.world_coordinator.get_hex_info(target_hex_id)
        new_locations = self.world_coordinator.get_hex_locations(target_hex_id)
        
        gs.world_position.hex_id = target_hex_id
        gs.world_position.coords = target_coords
        gs.world_position.hex_data = new_hex_data
        gs.world_position.available_locations = new_locations
        
        # Generate new weather for the new location
        climate_info = self.world_coordinator.get_climate_info(target_hex_id)
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
            self._notify_ui_state_change("character_death")
            return False, f"{travel_desc}\n\n💀 You collapsed and died during the journey!"
        
        # Notify UI of location change
        self._notify_ui_state_change("location_change")
        
        return True, travel_desc
    
    def enter_location(self, location_id: str = None) -> Tuple[bool, str]:
        """
        Enter a location within the current hex.
        
        Args:
            location_id: ID of location to enter (if None, enter first available)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
        # Check if already in a location
        if gs.world_position.current_location_id:
            return False, "You are already inside a location. Use 'exit' to leave first."
        
        # Get available locations in current hex (fresh from WorldCoordinator)
        current_hex_id = gs.world_position.hex_id
        available_locations = self.world_coordinator.get_hex_locations(current_hex_id)
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
        if starting_area_id in areas:
            area_data = areas[starting_area_id]
            objects = area_data.get("objects", [])
            if objects:
                object_names = [obj.get("name", "something") for obj in objects[:3]]  # Show first 3
                if len(objects) > 3:
                    entry_message += f"\n\nYou notice {', '.join(object_names)}, and more."
                else:
                    entry_message += f"\n\nYou notice {', '.join(object_names)}."
        
        # Shelter conditions now work automatically like "Lit Fire" - no manual setup needed
        
        # Debug location info
        self._debug_location_info(location_data)
        
        # Notify UI of location entry
        self._notify_ui_state_change("location_entry")
        
        return True, entry_message
    
    def exit_location(self) -> Tuple[bool, str]:
        """
        Exit current location back to hex overworld.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
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
        gs.world_position.current_area_id = "entrance"  # Reset to default
        
        # Get current hex description for context
        hex_name = gs.world_position.hex_data.get("name", "the area")
        
        # Shelter conditions now work automatically like "Lit Fire" - no manual removal needed
        
        # Notify UI of location exit
        self._notify_ui_state_change("location_exit")
        
        return True, f"You exit {location_name} and return to {hex_name}."
    
    def move_between_locations(self, direction: str) -> Tuple[bool, str]:
        """Move between different locations within the same hex"""
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
        # Check if player is inside a location
        if not gs.world_position.current_location_id:
            return False, "You are not inside a location."
        
        # Get all locations in current hex
        hex_id = gs.world_position.hex_id
        available_locations = gs.world_position.available_locations
        
        if not available_locations or len(available_locations) < 2:
            return False, "There are no other locations to travel to from here."
        
        # Find current location in the list
        current_location_id = gs.world_position.current_location_id
        current_location_index = None
        
        for i, loc in enumerate(available_locations):
            if loc.get("id") == current_location_id:
                current_location_index = i
                break
        
        if current_location_index is None:
            return False, "Current location not found in available locations."
        
        # Create a simple location graph - arrange locations in cardinal directions
        location_graph = self._create_location_graph(available_locations, current_location_index)
        
        # Check if movement in requested direction is possible
        if direction not in location_graph:
            available_directions = list(location_graph.keys())
            if available_directions:
                return False, f"You cannot go {direction} from here. Available directions: {', '.join(available_directions)}"
            else:
                return False, "There are no exits from this location. Use 'exit' to return to the overworld."
        
        # Get target location
        target_location = location_graph[direction]
        
        # Check if character is capable of movement
        if gs.character.hp <= 0:
            return False, "You are unconscious and cannot move."
        
        # Calculate travel time for location movement (base 15 minutes = 0.25 hours)
        travel_time = self._calculate_location_travel_time()
        
        # Use existing time system to advance time (which handles survival effects)
        if self.time_system:
            time_result = self.time_system.perform_activity("travel", duration_override=travel_time)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Travel failed.")
        else:
            # Fallback: just advance game time
            self._advance_game_time(travel_time)
        
        # Move to target location
        target_location_data = self._get_or_generate_location_data(target_location)
        
        # Update player position
        gs.world_position.current_location_id = target_location.get("id")
        gs.world_position.current_location_data = target_location_data
        gs.world_position.current_area_id = target_location_data.get("starting_area", "entrance")
        
        # Debug location info for location-to-location movement
        self._debug_location_info(target_location_data)
        
        # Build movement message
        target_name = target_location.get("name", "Unknown Location")
        target_desc = target_location_data.get("description", "An unremarkable area.")
        
        # Add time indication to message
        time_desc = self._get_location_travel_description(travel_time)
        message = f"You travel {direction} to {target_name}.{time_desc}\n\n{target_desc}"
        
        # Check if character died during travel
        if gs.character.hp <= 0:
            self._notify_ui_state_change("character_death")
            return False, f"{message}\n\n💀 You collapsed and died during the journey!"
        
        # Show objects in new location
        areas = target_location_data.get("areas", {})
        starting_area_id = target_location_data.get("starting_area", "entrance")
        if starting_area_id in areas:
            area_data = areas[starting_area_id]
            objects = area_data.get("objects", [])
            if objects:
                object_names = [obj.get("name", "something") for obj in objects[:3]]
                if len(objects) > 3:
                    message += f"\n\nYou notice {', '.join(object_names)}, and more."
                else:
                    message += f"\n\nYou notice {', '.join(object_names)}."
        
        # Notify UI of location movement
        self._notify_ui_state_change("location_movement")
        
        return True, message
    
    def rest_in_location(self) -> Tuple[bool, str]:
        """Handle resting/sleeping in current location with fatigue-based wake-up checks"""
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
        # Check if player is inside a location
        if not gs.world_position.current_location_id:
            return False, "You must be inside a location to rest safely. Use 'enter' to enter a location first."
        
        # Check if character is capable of resting
        if gs.character.hp <= 0:
            return False, "You are unconscious and cannot rest voluntarily."
        
        # Get current fatigue level to determine initial wake-up DC
        current_fatigue = gs.player_state.survival.fatigue
        
        # If not fatigued enough, they won't sleep long
        if current_fatigue > 700:  # Well rested
            return False, "You are not tired enough to sleep. Try resting when you're more fatigued."
        
        # Calculate initial wake-up DC based on fatigue (lower fatigue = higher DC = longer sleep)
        # Fatigue 0-200 (exhausted): DC 18-20 (long sleep)
        # Fatigue 200-400 (tired): DC 15-17 (medium sleep)  
        # Fatigue 400-600 (somewhat tired): DC 12-14 (short sleep)
        # Fatigue 600-700 (slightly tired): DC 8-11 (very short sleep)
        
        if current_fatigue <= 200:
            base_dc = 18
        elif current_fatigue <= 400:
            base_dc = 15
        elif current_fatigue <= 600:
            base_dc = 12
        else:
            base_dc = 8
        
        # Start resting
        location_name = gs.world_position.current_location_data.get("name", "this location")
        rest_messages = [f"You settle down to rest in {location_name}..."]
        
        hours_slept = 0
        current_dc = base_dc
        
        # Rest loop - check each hour for wake up
        import random
        while hours_slept < 12:  # Maximum 12 hours of sleep
            hours_slept += 1
            
            # Use time system to advance 1 hour of rest
            if self.time_system:
                time_result = self.time_system.perform_activity("rest", duration_override=1.0)
                if not time_result.get("success", True):
                    return False, time_result.get("message", "Rest was interrupted.")
            else:
                # Fallback: advance time manually
                self._advance_game_time(1.0)
            
            # Check if character died during rest
            if gs.character.hp <= 0:
                return False, f"💀 You died in your sleep after {hours_slept} hours of rest!"
            
            # Roll wake-up check (d20 + constitution modifier)
            constitution_mod = (gs.character.constitution - 10) // 2
            wake_roll = random.randint(1, 20) + constitution_mod
            
            # DC decreases each hour to ensure eventual wake-up
            effective_dc = max(5, current_dc - (hours_slept - 1))
            
            if wake_roll >= effective_dc:
                # Wake up naturally
                break
        
        # Calculate rest quality and fatigue recovery
        if hours_slept >= 8:
            fatigue_recovery = 400  # Full rest
            quality = "excellent"
        elif hours_slept >= 6:
            fatigue_recovery = 300  # Good rest
            quality = "good"
        elif hours_slept >= 4:
            fatigue_recovery = 200  # Decent rest
            quality = "decent"
        elif hours_slept >= 2:
            fatigue_recovery = 100  # Poor rest
            quality = "poor"
        else:
            fatigue_recovery = 50   # Minimal rest
            quality = "restless"
        
        # Apply fatigue recovery
        old_fatigue = gs.player_state.survival.fatigue
        gs.player_state.survival.fatigue = min(1000, gs.player_state.survival.fatigue + fatigue_recovery)
        
        # Update last sleep time
        gs.player_state.last_sleep_hours = 0
        
        # Build result message
        time_desc = f"{hours_slept} hour{'s' if hours_slept != 1 else ''}"
        fatigue_change = gs.player_state.survival.fatigue - old_fatigue
        
        result_message = f"You slept for {time_desc} and had a {quality} rest.\n"
        result_message += f"Fatigue recovered: +{fatigue_change} ({old_fatigue} → {gs.player_state.survival.fatigue})"
        
        # Add time information
        current_time = gs.game_time.get_time_string()
        result_message += f"\n\nYou wake up at {current_time}."
        
        return True, result_message
    
    def interact_with_object(self, object_name: str, action: str) -> Tuple[bool, str]:
        """
        Interact with an object in current area based on its properties
        
        Args:
            object_name: Name of object to interact with
            action: Type of interaction (forage, search, examine, etc.)
        
        Returns:
            (success, message)
        """
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
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
        """Handle searching containers/objects - COORDINATOR ONLY"""
        if not properties.get("can_search"):
            return False, f"There's nothing to search in the {obj.get('name')}."
        
        # Check if already searched
        if obj.get("searched", False):
            return False, f"You have already searched the {obj.get('name')}."
        
        # Simple success for now - ActionHandler implements the multi-skill system
        obj["searched"] = True
        return True, f"You search the {obj.get('name')} and find some items."
    
    def _handle_examine(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle examining objects closely - COORDINATOR ONLY"""
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
        import random
        roll = random.randint(1, 20)
        skill_bonus = self._get_skill_bonus("sleight_of_hand")
        dc = properties.get("dc_lockpick", 15)
        total = roll + skill_bonus
        
        # Lockpicking takes time
        if self.time_system:
            time_result = self.time_system.perform_activity("lockpick", duration_override=1.0)  # 1 hour
            if not time_result.get("success", True):
                return False, time_result.get("message", "Lockpicking failed.")
        
        if total >= dc:
            # Success
            obj["unlocked"] = True
            return True, f"You successfully pick the lock on the {obj.get('name')}!"
        else:
            return False, f"You fail to pick the lock on the {obj.get('name')}."
    
    def _handle_chop(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle chopping wood from objects - COORDINATOR ONLY"""
        if not properties.get("can_chop_wood"):
            return False, f"You can't chop wood from the {obj.get('name')}."
        
        # Check if already chopped
        if obj.get("chopped", False):
            return False, f"You have already chopped wood from the {obj.get('name')}."
        
        # Simple success for now - ActionHandler implements the multi-skill system
        obj["chopped"] = True
        return True, f"You chop wood from the {obj.get('name')} and gather some firewood."
    
    def _handle_take(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
        """Handle taking wood or other materials from objects - COORDINATOR ONLY"""
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
        if self.time_system:
            time_result = self.time_system.perform_activity("quick", duration_override=0.083)  # 5 minutes
            if not time_result.get("success", True):
                return False, time_result.get("message", "Drinking failed.")
        
        # Apply thirst relief based on water quality
        gs = self.game_state
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
        """Get character's skill bonus (placeholder implementation)"""
        # TODO: Connect to actual character skill system
        # For now, return a basic bonus based on character stats
        gs = self.game_state
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
        if success_margin >= 15:      # Exceptional success (nat 20 + good stats)
            return 2.0
        elif success_margin >= 10:    # Great success
            return 1.5
        elif success_margin >= 5:     # Good success
            return 1.2
        elif success_margin >= 0:     # Bare success
            return 1.0
        elif success_margin >= -3:    # Near miss (shouldn't happen since we only call this on success)
            return 0.8
        else:                         # Poor performance
            return 0.5
    
    def _generate_from_item_drops(self, item_drops: Dict, quality_multiplier: float = 1.0) -> Dict[str, int]:
        """Generate items from item_drops configuration with quality scaling"""
        import random
        
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
            
            # For now, generate generic items based on pools
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
    
    def _create_location_graph(self, locations: List[Dict], current_index: int) -> Dict[str, Dict]:
        """Create a persistent bidirectional graph of locations"""
        gs = self.game_state
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
    
    def _get_or_generate_location_data(self, location_template: Dict[str, Any]) -> Dict[str, Any]:
        """Get persistent location data or generate it if first visit"""
        gs = self.game_state
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
        # The WorldCoordinator has already done the conversion from Location objects to dictionaries
        location_data = location_template.copy()  # Make a copy to avoid modifying the original
        
        # Store for persistence
        gs.persistent_locations[location_key] = location_data
        
        return location_data
    
    def _generate_location_from_template(self, template: Dict[str, Any], coords: Tuple[int, int], biome: str) -> Dict[str, Any]:
        """Generate detailed location data from template"""
        # Use LocationGenerator to create detailed location
        if self.location_generator and hasattr(self.location_generator, '_create_location_from_template'):
            try:
                return self.location_generator._create_location_from_template(template, coords, 0)
            except:
                pass
        
        # Fallback: create basic location data
        return {
            "id": template.get("id"),
            "name": template.get("name", "Unknown Location"),
            "description": template.get("description", "An unremarkable area."),
            "type": template.get("type", "wilderness"),
            "size": template.get("size", "medium"),
            "terrain": template.get("terrain", "open"),
            "objects": self._generate_basic_objects(template, biome),
            "exit_flag": template.get("exit_flag", True)
        }
    
    def _generate_basic_objects(self, template: Dict[str, Any], biome: str) -> List[Dict[str, Any]]:
        """Generate basic objects for a location"""
        objects = []
        
        # Add some basic objects based on biome and location type
        location_type = template.get("type", "wilderness")
        
        if "forest" in biome.lower():
            objects.extend([
                {"name": "Berry Bush", "description": "A bush with ripe berries.", "can_forage": True},
                {"name": "Fallen Log", "description": "A moss-covered fallen tree.", "can_search": True}
            ])
        elif "mountain" in biome.lower():
            objects.extend([
                {"name": "Rock Outcrop", "description": "A jutting rock formation.", "can_search": True},
                {"name": "Cave Entrance", "description": "A dark opening in the rock.", "can_enter": True}
            ])
        elif "grassland" in biome.lower():
            objects.extend([
                {"name": "Wildflower Patch", "description": "Colorful wildflowers.", "can_forage": True},
                {"name": "Old Stone", "description": "A weathered standing stone.", "can_examine": True}
            ])
        
        return objects[:2]  # Limit to 2 objects for simplicity
    
    def dump_location_data(self, filename: str = None) -> Tuple[bool, str]:
        """Dump current location data to JSON file for analysis"""
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
        # Check if player is in a location
        if not gs.world_position.current_location_id:
            return False, "You must be inside a location to dump location data."
        
        location_data = gs.world_position.current_location_data
        if not location_data:
            return False, "No location data available."
        
        # Generate filename if not provided
        if not filename:
            location_name = location_data.get("name", "unknown_location").lower().replace(" ", "_")
            hex_id = gs.world_position.hex_id
            filename = f"debug_location_{location_name}_{hex_id}.json"
        
        try:
            import json
            with open(filename, 'w') as f:
                json.dump(location_data, f, indent=2, default=str)
            
            return True, f"Location data dumped to {filename}"
        except Exception as e:
            return False, f"Failed to dump location data: {str(e)}"
    
    def dump_hex_data(self, filename: str = None) -> Tuple[bool, str]:
        """Dump current hex data including all locations to JSON file for analysis"""
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        hex_id = gs.world_position.hex_id
        
        # Get all locations in current hex
        try:
            hex_locations = self.world_coordinator.get_hex_locations(hex_id)
            hex_data = {
                "hex_id": hex_id,
                "coordinates": gs.world_position.coords,
                "hex_info": gs.world_position.hex_data,
                "weather": {
                    "temperature": gs.current_weather.temperature,
                    "precipitation": gs.current_weather.precipitation,
                    "wind_speed": gs.current_weather.wind_speed,
                    "description": gs.current_weather.get_description()
                },
                "locations": hex_locations,
                "current_location_id": gs.world_position.current_location_id
            }
            
            # Generate filename if not provided
            if not filename:
                filename = f"debug_hex_{hex_id}.json"
            
            import json
            with open(filename, 'w') as f:
                json.dump(hex_data, f, indent=2, default=str)
            
            return True, f"Hex data dumped to {filename}"
        except Exception as e:
            return False, f"Failed to dump hex data: {str(e)}"

    def get_location_contents(self) -> str:
        """Get a description of objects and items in the current location with shortkeys"""
        if not self.is_initialized or not self.game_state:
            return ""
        
        gs = self.game_state
        
        # Check if player is in a location
        if not gs.world_position.current_location_id:
            return ""
        
        location_data = gs.world_position.current_location_data
        if not location_data:
            return ""
        
        # Get objects from the location's starting area
        areas = location_data.get("areas", {})
        starting_area_id = location_data.get("starting_area", "entrance")
        
        if starting_area_id not in areas:
            return ""
        
        area_data = areas[starting_area_id]
        objects = area_data.get("objects", [])
        items = area_data.get("items", [])
        
        content_parts = []
        
        if objects:
            # Format objects with their permanent shortkeys from JSON
            formatted_objects = []
            
            # DEBUG: Write to file for inspection
            with open("shortkey_debug.txt", "w") as f:
                f.write("=== OBJECT DEBUG OUTPUT ===\n\n")
                for obj in objects:
                    obj_name = obj.get("name", "Unknown")
                    shortkey = obj.get("shortkey", "")
                    
                    f.write(f"Object: {obj_name}\n")
                    f.write(f"Shortkey: '{shortkey}'\n")
                    f.write(f"Full dict keys: {list(obj.keys())}\n")
                    f.write(f"Full dict: {obj}\n")
                    f.write("-" * 50 + "\n")
                    
                    if shortkey:
                        formatted_objects.append(f"{obj_name} [{shortkey}]")
                    else:
                        formatted_objects.append(obj_name)
            
            content_parts.append(f"You notice {', '.join(formatted_objects)}.")
        
        if items:
            item_names = [item.get("name", "Unknown") for item in items]
            if len(item_names) <= 3:
                content_parts.append(f"Items on the ground: {', '.join(item_names)}.")
            else:
                shown = item_names[:3]
                remaining = len(item_names) - 3
                content_parts.append(f"Items on the ground: {', '.join(shown)}, and {remaining} more.")
        
        return "\n".join(content_parts) if content_parts else ""

    def get_action_handler(self):
        """Get an ActionHandler connected to this GameEngine"""
        # Late import to avoid circular dependencies
        from actions.action_handler import ActionHandler
        
        if not self.is_initialized or not self.game_state:
            return ActionHandler()  # Return basic handler if not initialized
        
        return ActionHandler(
            character=self.game_state.character,
            player_state=self.game_state.player_state,
            game_engine=self  # Connect to this GameEngine
        )
    
    def _calculate_target_coords(self, current_coords: Tuple[int, int], direction: str) -> Optional[Tuple[int, int]]:
        """Calculate target coordinates based on direction"""
        try:
            col, row = current_coords
            
            direction_map = {
                "north": (0, -1),
                "south": (0, 1),
                "east": (1, 0),
                "west": (-1, 0),
                "northeast": (1, -1),
                "northwest": (-1, -1),
                "southeast": (1, 1),
                "southwest": (-1, 1)
            }
            
            if direction.lower() not in direction_map:
                return None
            
            dc, dr = direction_map[direction.lower()]
            new_col = col + dc
            new_row = row + dr
            
            # Check bounds
            if new_col < 0 or new_col >= self.world_size[0] or new_row < 0 or new_row >= self.world_size[1]:
                return None
            
            return (new_col, new_row)
        except:
            return None
    
    def _calculate_travel_time(self, from_hex: str, to_hex: str) -> float:
        """Calculate travel time in hours based on terrain and conditions"""
        # Base travel time: 1-4 hours per hex as per steering guide
        base_time = 2.0  # 2 hours base
        
        # Get terrain difficulty
        from_data = self.world_coordinator.get_hex_info(from_hex)
        to_data = self.world_coordinator.get_hex_info(to_hex)
        
        # Terrain modifiers
        terrain_modifiers = {
            "forest": 1.2,
            "mountain": 1.8,
            "swamp": 1.6,
            "desert": 1.4,
            "plains": 0.8,
            "road": 0.6
        }
        
        from_modifier = terrain_modifiers.get(from_data.get("type", "plains"), 1.0)
        to_modifier = terrain_modifiers.get(to_data.get("type", "plains"), 1.0)
        terrain_time = base_time * ((from_modifier + to_modifier) / 2)
        
        # Weather effects
        weather = self.game_state.current_weather
        weather_modifier = 1.0
        
        if weather.precipitation > 20:  # Heavy precipitation
            weather_modifier += 0.5
        elif weather.precipitation > 5:  # Light precipitation
            weather_modifier += 0.2
        
        if weather.wind_speed > 15:  # Strong winds
            weather_modifier += 0.3
        
        # Character speed effects
        character = self.game_state.character
        speed_modifier = 1.0
        if hasattr(character, 'get_effective_speed'):
            effective_speed = character.get_effective_speed()
            base_speed = getattr(character, 'base_speed', 30)
            speed_modifier = base_speed / max(5, effective_speed)
        
        final_time = terrain_time * weather_modifier * speed_modifier
        
        # Cap between 1-4 hours as per steering guide
        return max(1.0, min(4.0, final_time))
    
    def _calculate_location_travel_time(self) -> float:
        """Calculate travel time between locations (base 15 minutes = 0.25 hours)"""
        base_time = 0.25  # 15 minutes base
        
        # Character speed effects
        character = self.game_state.character
        speed_modifier = 1.0
        if hasattr(character, 'get_effective_speed'):
            effective_speed = character.get_effective_speed()
            base_speed = getattr(character, 'base_speed', 30)
            if effective_speed > 0:
                speed_modifier = base_speed / max(5, effective_speed)
        
        # Weather effects (lighter than overworld travel)
        weather = self.game_state.current_weather
        weather_modifier = 1.0
        
        if weather.precipitation > 30:  # Heavy precipitation
            weather_modifier += 0.2
        elif weather.precipitation > 10:  # Light precipitation
            weather_modifier += 0.1
        
        if weather.wind_speed > 20:  # Very strong winds
            weather_modifier += 0.1
        
        final_time = base_time * weather_modifier * speed_modifier
        
        # Cap between 5 minutes and 1 hour for location travel
        return max(0.083, min(1.0, final_time))  # 0.083 = 5 minutes
    
    def _get_location_travel_description(self, travel_time: float) -> str:
        """Get natural language description of location travel time"""
        minutes = int(travel_time * 60)
        
        if minutes < 5:
            return " You quickly make your way there."
        elif minutes < 15:
            return f" After a short time of walking, you arrive."
        elif minutes < 30:
            return f" After a good walk, you reach your destination."
        else:
            return f" After a longer time of travel, you arrive."

    def _advance_game_time(self, hours: float):
        """Advance game time and update weather"""
        gs = self.game_state
        
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
    
    def _get_travel_description(self, direction: str, hex_data: Dict[str, Any], travel_time: float) -> str:
        """Generate natural language description of travel"""
        time_desc = "some time" if travel_time < 1.5 else "several hours"
        
        descriptions = [
            f"After {time_desc} of travel {direction}, you arrive at {hex_data['name']}.",
            hex_data.get('description', 'An unremarkable area.')
        ]
        
        # Add weather context
        weather = self.game_state.current_weather
        if weather.precipitation > 20:
            descriptions.append("The heavy precipitation made the journey difficult.")
        elif weather.precipitation > 5:
            descriptions.append("Light precipitation accompanied your travels.")
        
        if weather.wind_speed > 15:
            descriptions.append("Strong winds buffeted you along the way.")
        
        return " ".join(descriptions)
    

    
    def save_game(self, save_name: str = "save") -> Tuple[bool, str]:
        """
        Save current game state to JSON file.
        
        Args:
            save_name: Name for the save file (without extension)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized - cannot save."
        
        try:
            import json
            from datetime import datetime
            
            gs = self.game_state
            
            # Create save data structure
            save_data = {
                "version": "1.0",
                "saved_at": datetime.now().isoformat(),
                "game_info": {
                    "world_seed": gs.world_seed,
                    "created_at": gs.created_at.isoformat(),
                    "play_time_minutes": gs.play_time_minutes
                },
                "character": self._serialize_character(gs.character),
                "player_state": self._serialize_player_state(gs.player_state),
                "world_position": self._serialize_world_position(gs.world_position),
                "game_time": self._serialize_game_time(gs.game_time),
                "weather": self._serialize_weather(gs.current_weather),
                "world_data": self._serialize_world_data()
            }
            
            # Save to JSON file
            filename = f"{save_name}.json"
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            # Update last saved time
            gs.last_saved = datetime.now()
            
            return True, f"Game saved to {filename}"
            
        except Exception as e:
            return False, f"Failed to save game: {str(e)}"
    
    def load_game(self, save_name: str = "save") -> Tuple[bool, str]:
        """
        Load game state from JSON save file.
        
        Args:
            save_name: Name of save file to load (without extension)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            import json
            from datetime import datetime
            
            filename = f"{save_name}.json"
            
            # Check if save file exists
            if not os.path.exists(filename):
                return False, f"Save file {filename} not found."
            
            # Load save data
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            # Validate save file version
            if save_data.get("version") != "1.0":
                return False, f"Incompatible save file version: {save_data.get('version', 'unknown')}"
            
            # Create world coordinator without generating new world
            world_seed = save_data["game_info"]["world_seed"]
            
            # Create WorldCoordinator with skip_generation flag
            self.world_coordinator = WorldCoordinator(
                world_size=self.world_size,
                seed=world_seed,
                skip_generation=True  # Don't generate - we'll restore from save
            )
            
            # Deserialize game state components
            character = self._deserialize_character(save_data["character"])
            player_state = self._deserialize_player_state(save_data["player_state"], character)
            world_position = self._deserialize_world_position(save_data["world_position"])
            game_time = self._deserialize_game_time(save_data["game_time"])
            weather = self._deserialize_weather(save_data["weather"])
            
            # Initialize time system
            from game.time_system import TimeSystem
            self.time_system = TimeSystem(player_state)
            
            # Restore world data from save file
            self._deserialize_world_data(save_data["world_data"])
            
            # Create game state
            self.game_state = GameState(
                character=character,
                player_state=player_state,
                world_position=world_position,
                game_time=game_time,
                current_weather=weather,
                world_seed=world_seed,
                created_at=datetime.fromisoformat(save_data["game_info"]["created_at"]),
                last_saved=datetime.fromisoformat(save_data["saved_at"]),
                play_time_minutes=save_data["game_info"]["play_time_minutes"]
            )
            
            self.is_initialized = True
            
            return True, f"Game loaded from {filename}"
            
        except Exception as e:
            return False, f"Failed to load game: {str(e)}"


    # Serialization helper methods for save/load
    def _serialize_character(self, character) -> dict:
        """Serialize character object to dictionary"""
        # Properly serialize inventory using centralized system
        inventory_data = []
        if hasattr(character, 'inventory') and character.inventory:
            if hasattr(character.inventory, 'items'):
                inventory_data = [item.to_dict() for item in character.inventory.items]
        
        # Properly serialize equipment
        equipment_data = {}
        if hasattr(character, 'equipment') and character.equipment:
            equipment_data = dict(character.equipment) if isinstance(character.equipment, dict) else {}
        
        return {
            "name": character.name,
            "race": character.race,
            "character_class": character.character_class,
            "background": getattr(character, 'background', 'Folk Hero'),
            "level": character.level,
            "experience_points": character.experience_points,
            "hp": character.hp,
            "max_hp": character.max_hp,
            "armor_class": character.armor_class,
            "proficiency_bonus": character.proficiency_bonus,
            "strength": character.strength,
            "dexterity": character.dexterity,
            "constitution": character.constitution,
            "intelligence": character.intelligence,
            "wisdom": character.wisdom,
            "charisma": character.charisma,
            "inventory": inventory_data,
            "equipment": equipment_data
        }
    
    def _deserialize_character(self, data: dict):
        """Deserialize character from dictionary"""
        from core.character import Character
        
        character = Character(
            name=data["name"],
            race=data["race"],
            character_class=data["character_class"],
            background=data.get("background", "Folk Hero"),
            level=data["level"],
            experience_points=data["experience_points"],
            hp=data["hp"],
            max_hp=data["max_hp"],
            armor_class=data["armor_class"],
            proficiency_bonus=data["proficiency_bonus"],
            strength=data["strength"],
            dexterity=data["dexterity"],
            constitution=data["constitution"],
            intelligence=data["intelligence"],
            wisdom=data["wisdom"],
            charisma=data["charisma"]
        )
        
        # Initialize inventory system
        character.initialize_inventory()
        
        # Restore inventory items using centralized system
        if "inventory" in data and data["inventory"]:
            from core.inventory import InventoryItem
            for item_data in data["inventory"]:
                item = InventoryItem.from_dict(item_data)
                character.inventory.items.append(item)
        
        # Restore equipment
        if "equipment" in data:
            character.equipment = data["equipment"]
            
        return character
    
    def _serialize_player_state(self, player_state) -> dict:
        """Serialize player state to dictionary"""
        # Safely get survival attributes with defaults
        survival_data = {}
        survival = player_state.survival
        
        # Core survival needs
        survival_data["hunger"] = getattr(survival, "hunger", 500)
        survival_data["thirst"] = getattr(survival, "thirst", 500)
        survival_data["fatigue"] = getattr(survival, "fatigue", 500)
        
        # Temperature regulation
        survival_data["body_temperature"] = getattr(survival, "body_temperature", 500)
        survival_data["warmth"] = getattr(survival, "warmth", 500)
        
        # Environmental exposure
        survival_data["wetness"] = getattr(survival, "wetness", 0)
        survival_data["wind_chill"] = getattr(survival, "wind_chill", 0)
        
        return {
            "survival": survival_data,
            "game_time": {
                "game_hour": getattr(player_state, "game_hour", 12.0),
                "game_day": getattr(player_state, "game_day", 1),
                "game_season": getattr(player_state, "game_season", "spring")
            },
            "location": {
                "current_hex": player_state.current_hex,
                "current_location": player_state.current_location
            },
            "activity": {
                "last_meal_hours": getattr(player_state, "last_meal_hours", 0),
                "last_drink_hours": getattr(player_state, "last_drink_hours", 0),
                "last_sleep_hours": getattr(player_state, "last_sleep_hours", 0),
                "activity_level": getattr(player_state, "activity_level", "normal")
            },
            "status_effects": getattr(player_state, "status_effects", []),
            "temporary_modifiers": getattr(player_state, "temporary_modifiers", {})
        }
    
    def _deserialize_player_state(self, data: dict, character):
        """Deserialize player state from dictionary"""
        from game.player_state import PlayerState
        
        player_state = PlayerState(character=character, game_engine=self)
        
        # Restore survival stats
        survival_data = data["survival"]
        player_state.survival.hunger = survival_data["hunger"]
        player_state.survival.thirst = survival_data["thirst"]
        player_state.survival.fatigue = survival_data["fatigue"]
        player_state.survival.body_temperature = survival_data["body_temperature"]
        player_state.survival.warmth = survival_data["warmth"]
        player_state.survival.wetness = survival_data["wetness"]
        player_state.survival.wind_chill = survival_data["wind_chill"]
        
        # Restore game time data
        if "game_time" in data:
            time_data = data["game_time"]
            player_state.game_hour = time_data["game_hour"]
            player_state.game_day = time_data["game_day"]
            player_state.game_season = time_data["game_season"]
            # Note: turn_counter removed as this is not a turn-based game
        
        # Restore location data
        if "location" in data:
            location_data = data["location"]
            player_state.current_hex = location_data["current_hex"]
            player_state.current_location = location_data["current_location"]
        
        # Restore activity data
        if "activity" in data:
            activity_data = data["activity"]
            player_state.last_meal_hours = activity_data["last_meal_hours"]
            player_state.last_drink_hours = activity_data["last_drink_hours"]
            player_state.last_sleep_hours = activity_data["last_sleep_hours"]
            player_state.activity_level = activity_data["activity_level"]
        
        # Restore status effects and modifiers
        if "status_effects" in data:
            player_state.status_effects = data["status_effects"]
        if "temporary_modifiers" in data:
            player_state.temporary_modifiers = data["temporary_modifiers"]
        
        return player_state
    
    def _serialize_world_position(self, world_position: WorldPosition) -> dict:
        """Serialize world position to dictionary"""
        return {
            "hex_id": world_position.hex_id,
            "hex_data": world_position.hex_data,
            "available_locations": world_position.available_locations,
            "current_location_id": world_position.current_location_id,
            "current_location_data": world_position.current_location_data,
            "current_area_id": world_position.current_area_id,
            "coords": world_position.coords
        }
    
    def _deserialize_world_position(self, data: dict) -> WorldPosition:
        """Deserialize world position from dictionary"""
        return WorldPosition(
            hex_id=data["hex_id"],
            hex_data=data["hex_data"],
            available_locations=data["available_locations"],
            current_location_id=data.get("current_location_id"),
            current_location_data=data.get("current_location_data"),
            current_area_id=data.get("current_area_id", "entrance"),
            coords=tuple(data["coords"]) if data.get("coords") else None
        )
    
    def _serialize_game_time(self, game_time: GameTime) -> dict:
        """Serialize game time to dictionary"""
        return {
            "year": game_time.year,
            "day": game_time.day,
            "hour": game_time.hour,
            "minute": game_time.minute,
            "season": game_time.season
        }
    
    def _deserialize_game_time(self, data: dict) -> GameTime:
        """Deserialize game time from dictionary"""
        return GameTime(
            year=data["year"],
            day=data["day"],
            hour=data["hour"],
            minute=data["minute"],
            season=data["season"]
        )
    
    def _serialize_weather(self, weather: WeatherState) -> dict:
        """Serialize weather state to dictionary"""
        return {
            "temperature": getattr(weather, "temperature", 70.0),
            "wind_speed": getattr(weather, "wind_speed", 0),
            "wind_direction": getattr(weather, "wind_direction", "N"),
            "precipitation": getattr(weather, "precipitation", 0),
            "precipitation_type": getattr(weather, "precipitation_type", "rain"),
            "cloud_cover": getattr(weather, "cloud_cover", 50),
            "visibility": getattr(weather, "visibility", 10000),
            "feels_like": getattr(weather, "feels_like", 70.0),
            "is_storm": getattr(weather, "is_storm", False),
            "lightning_risk": getattr(weather, "lightning_risk", 0.0)
        }
    
    def _deserialize_weather(self, data: dict) -> WeatherState:
        """Deserialize weather state from dictionary"""
        return WeatherState(
            temperature=data.get("temperature", 70.0),
            wind_speed=data.get("wind_speed", 0),
            wind_direction=data.get("wind_direction", "N"),
            precipitation=data.get("precipitation", 0),
            precipitation_type=data.get("precipitation_type", "rain"),
            cloud_cover=data.get("cloud_cover", 50),
            visibility=data.get("visibility", 10000),
            feels_like=data.get("feels_like", 70.0),
            is_storm=data.get("is_storm", False),
            lightning_risk=data.get("lightning_risk", 0.0)
        )
    
    def _serialize_world_data(self) -> dict:
        """Serialize world coordinator data - save entire world like dump_world does"""
        if not self.world_coordinator:
            return {}
        
        # Get the complete world data (similar to dump_world action)
        world_data = {}
        
        # Get all hex data
        if hasattr(self.world_coordinator, 'hex_data'):
            # Convert tuple keys to strings for JSON compatibility
            for coords, hex_info in self.world_coordinator.hex_data.items():
                if isinstance(coords, tuple):
                    key = f"{coords[0]:02d}{coords[1]:02d}"
                else:
                    key = str(coords)
                world_data[key] = hex_info
        
        # Get persistent location data
        persistent_locations = {}
        if hasattr(self.world_coordinator, 'persistent_locations'):
            persistent_locations = self.world_coordinator.persistent_locations
        
        return {
            "hex_data": world_data,
            "persistent_locations": persistent_locations,
            "world_size": self.world_size,
            "world_seed": self.game_state.world_seed if self.game_state else None
        }
    
    def _deserialize_world_data(self, data: dict):
        """Deserialize world coordinator data"""
        if not self.world_coordinator:
            return
        
        # Restore hex data
        if "hex_data" in data:
            if not hasattr(self.world_coordinator, 'hex_data'):
                self.world_coordinator.hex_data = {}
            
            # Convert string keys back to tuples for internal use
            for hex_id, hex_info in data["hex_data"].items():
                if len(hex_id) == 4:  # Format like "1010"
                    coords = (int(hex_id[:2]), int(hex_id[2:]))
                    self.world_coordinator.hex_data[coords] = hex_info
                    # Also store with string key for compatibility
                    self.world_coordinator.hex_data[hex_id] = hex_info
        
        # Restore persistent location data
        if "persistent_locations" in data:
            if not hasattr(self.world_coordinator, 'persistent_locations'):
                self.world_coordinator.persistent_locations = {}
            self.world_coordinator.persistent_locations.update(data["persistent_locations"])
    
    def _check_and_apply_shelter_conditions(self, location_data: Dict):
        """Check for shelter conditions when entering a location and apply them"""
        if not location_data:
            return
        
        # Get shelter information from location
        shelter_type = location_data.get("shelter_type")
        shelter_quality = location_data.get("shelter_quality")
        
        if not shelter_type or not shelter_quality:
            return
        
        # Map shelter quality to condition names
        quality_to_condition = {
            "minimal": "Natural Shelter",
            "basic": "Natural Shelter", 
            "good": "Good Shelter",
            "excellent": "Excellent Shelter"
        }
        
        condition_name = quality_to_condition.get(shelter_quality)
        if not condition_name:
            return
        
        # Apply the shelter condition by updating the player state
        # The conditions system will automatically detect this when evaluating conditions
        gs = self.game_state
        if hasattr(gs.player_state, 'current_shelter'):
            gs.player_state.current_shelter = {
                "type": shelter_type,
                "quality": shelter_quality,
                "condition": condition_name
            }
        else:
            # Add shelter tracking to player state if it doesn't exist
            gs.player_state.current_shelter = {
                "type": shelter_type,
                "quality": shelter_quality,
                "condition": condition_name
            }
    
    def _remove_shelter_conditions(self):
        """Remove shelter conditions when exiting a location"""
        gs = self.game_state
        if hasattr(gs.player_state, 'current_shelter'):
            gs.player_state.current_shelter = None
    
    def _debug_location_info(self, location_data: Dict):
        """Debug location flags and properties"""
        from .conditions import DEBUG_SHELTER
        if not DEBUG_SHELTER or not location_data:
            return
            
        try:
            from ..actions.action_logger import get_action_logger
            action_logger = get_action_logger()
            
            location_name = location_data.get("name", "Unknown Location")
            
            # Collect ALL flags that start with "provides_"
            all_flags = []
            for key, value in location_data.items():
                if key.startswith("provides_") and value:
                    all_flags.append(key.replace("provides_", ""))
            
            # Also check for other relevant flags
            other_flags = []
            for flag in ["exit_flag", "spawn_weight", "size", "terrain", "type"]:
                if flag in location_data:
                    other_flags.append(f"{flag}:{location_data[flag]}")
            
            debug_msg = f"🏠 {location_name}"
            if all_flags:
                debug_msg += f" | Provides: {', '.join(all_flags)}"
            else:
                debug_msg += " | No provides_ flags"
            
            if other_flags:
                debug_msg += f" | {', '.join(other_flags[:3])}"  # Show first 3 to avoid spam
                
            action_logger.log_message(debug_msg)
                
        except ImportError:
            pass