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
    
    def __init__(self, world_size: Tuple[int, int] = (20, 20)):
        """Initialize GameEngine with world parameters"""
        self.world_size = world_size
        self.world_coordinator = None
        self.location_generator = None
        self.time_system = None
        
        # Game state
        self.game_state: Optional[GameState] = None
        self.is_initialized = False
        
        print("GameEngine initialized")
    
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
        
        print("Starting new game...")
        
        # Generate world seed if not provided
        if world_seed is None:
            world_seed = random.randint(1, 1000000)
        
        print(f"Initializing world with seed {world_seed}")
        
        # Initialize world systems using WorldCoordinator (proper flow)
        self.world_coordinator = WorldCoordinator(world_size=self.world_size, seed=world_seed)
        
        # Generate the complete world through WorldCoordinator
        print("Generating world through WorldCoordinator...")
        # Note: The WorldCoordinator should have a generate_world method that returns a World object
        # For now, we'll work with the existing hex_data system
        
        # Initialize player state and time system using real classes
        player_state = PlayerState(character=character)
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
        
        # Initialize game time
        game_time = GameTime()
        
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
        
        # Create complete game state
        self.game_state = GameState(
            character=character,
            player_state=player_state,
            world_position=world_position,
            game_time=game_time,
            current_weather=current_weather,
            world_seed=world_seed
        )
        
        self.is_initialized = True
        
        print(f"New game initialized successfully!")
        print(f"Starting location: {hex_data['name']}")
        print(f"Weather: {current_weather.temperature:.0f}°F, {current_weather.precipitation_type}")
        print(f"Time: {game_time.get_time_string()}, {game_time.get_date_string()}")
        
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
        
        # Build natural language response
        travel_desc = self._get_travel_description(direction, new_hex_data, travel_time)
        
        # Check if character died during travel
        if gs.character.hp <= 0:
            return False, f"{travel_desc}\n\n💀 You collapsed and died during the journey!"
        
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
        
        # Get current hex description for context
        hex_name = gs.world_position.hex_data.get("name", "the area")
        
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
        
        # Build movement message
        target_name = target_location.get("name", "Unknown Location")
        target_desc = target_location_data.get("description", "An unremarkable area.")
        
        # Add time indication to message
        time_desc = self._get_location_travel_description(travel_time)
        message = f"You travel {direction} to {target_name}.{time_desc}\n\n{target_desc}"
        
        # Check if character died during travel
        if gs.character.hp <= 0:
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
    
    def examine_object(self, object_name: str) -> Tuple[bool, str]:
        """Examine an object in the current location"""
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
        # Check if player is in a location
        if not gs.world_position.current_location_id:
            return False, "You must be inside a location to examine objects."
        
        # Get current location data
        location_data = gs.world_position.current_location_data
        if not location_data:
            return False, "No location data available."
        
        # Get objects from the location's starting area
        areas = location_data.get("areas", {})
        starting_area_id = location_data.get("starting_area", "entrance")
        
        if starting_area_id not in areas:
            return False, "No objects available to examine."
        
        # Get area data (it's a dictionary now)
        area_data = areas[starting_area_id]
        objects = area_data.get("objects", [])
        
        # Find matching object by name
        target_object = None
        for obj in objects:
            obj_name = obj.get('name', '').lower()
            if object_name.lower() in obj_name or obj_name in object_name.lower():
                target_object = obj
                break
        
        if not target_object:
            # List available objects
            if objects:
                object_names = [obj.get('name', 'Unknown') for obj in objects[:5]]
                return False, f"Cannot find '{object_name}'. Available objects: {', '.join(object_names)}"
            else:
                return False, "There are no objects to examine here."
        
        # Examine the object
        obj_name = target_object.get('name', 'Unknown Object')
        obj_desc = target_object.get('description', 'An unremarkable object.')
        
        # Check for special examination properties
        properties = target_object.get('properties', {})
        examination_text = properties.get('examination_text', '')
        
        result = f"**{obj_name}**\n\n{obj_desc}"
        
        if examination_text:
            result += f"\n\n{examination_text}"
        
        # Show interaction hints based on properties
        hints = []
        if properties.get('can_search'):
            hints.append("You could search this object.")
        if properties.get('can_take_wood'):
            hints.append("You could take wood from this.")
        if properties.get('can_light_fire'):
            hints.append("You could light a fire here.")
        if properties.get('provides_water'):
            hints.append("This provides fresh water.")
        
        if hints:
            result += f"\n\n{' '.join(hints)}"
        
        return True, result
    
    def search_object(self, object_name: str) -> Tuple[bool, str]:
        """Search an object for items"""
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
        # Check if player is in a location
        if not gs.world_position.current_location_id:
            return False, "You must be inside a location to search objects."
        
        # Get current location data and find object
        location_data = gs.world_position.current_location_data
        if not location_data:
            return False, "No location data available."
        
        # Get objects from the location's starting area
        areas = location_data.get("areas", {})
        starting_area_id = location_data.get("starting_area", "entrance")
        
        if starting_area_id not in areas:
            return False, "No objects available to search."
        
        area_data = areas[starting_area_id]
        objects = area_data.get("objects", [])
        
        # Find matching object
        target_object = None
        for obj in objects:
            obj_name = obj.get('name', '').lower()
            if object_name.lower() in obj_name or obj_name in object_name.lower():
                target_object = obj
                break
        
        if not target_object:
            return False, f"Cannot find '{object_name}' to search."
        
        # Check if object can be searched
        properties = target_object.get('properties', {})
        if not properties.get('can_search', False):
            obj_name = target_object.get('name', 'the object')
            return False, f"You cannot search {obj_name}."
        
        # Get items from the object
        item_drops = target_object.get('item_drops', [])
        
        if not item_drops:
            obj_name = target_object.get('name', 'the object')
            return True, f"You search {obj_name} thoroughly but find nothing useful."
        
        # Show available items (for now, just list them)
        obj_name = target_object.get('name', 'the object')
        item_names = [item.get('name', 'Unknown Item') for item in item_drops[:3]]
        
        if len(item_drops) > 3:
            return True, f"You search {obj_name} and find {', '.join(item_names)}, and more items."
        else:
            return True, f"You search {obj_name} and find {', '.join(item_names)}."
    
    def take_item(self, item_name: str) -> Tuple[bool, str]:
        """Take an item and add it to inventory"""
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
        # Check if player is in a location
        if not gs.world_position.current_location_id:
            return False, "You must be inside a location to take items."
        
        # Get current location data
        location_data = gs.world_position.current_location_data
        if not location_data:
            return False, "No location data available."
        
        # Get items from the location's starting area
        areas = location_data.get("areas", {})
        starting_area_id = location_data.get("starting_area", "entrance")
        
        if starting_area_id not in areas:
            return False, "No items available to take."
        
        area_data = areas[starting_area_id]
        items = area_data.get("items", [])
        
        # Also check object item drops
        objects = area_data.get("objects", [])
        all_items = list(items)  # Start with loose items
        
        # Add items from object drops
        for obj in objects:
            item_drops = obj.get("item_drops", [])
            all_items.extend(item_drops)
        
        # Find matching item by name
        target_item = None
        for item in all_items:
            item_name_check = item.get('name', '').lower()
            if item_name.lower() in item_name_check or item_name_check in item_name.lower():
                target_item = item
                break
        
        if not target_item:
            if all_items:
                item_names = [item.get('name', 'Unknown') for item in all_items[:5]]
                return False, f"Cannot find '{item_name}'. Available items: {', '.join(item_names)}"
            else:
                return False, "There are no items to take here."
        
        # Try to add item to character inventory
        item_id = target_item.get('id', item_name.lower().replace(' ', '_'))
        item_display_name = target_item.get('name', item_name)
        
        try:
            success = gs.character.add_item_to_inventory(item_id, 1)
            
            if success:
                # Remove item from location (for now, just mark as taken)
                # TODO: Implement proper item removal from location state
                return True, f"You take the {item_display_name}."
            else:
                return False, f"You cannot carry the {item_display_name} - your inventory is full or too heavy."
                
        except Exception as e:
            return False, f"Failed to take {item_display_name}: {str(e)}"
    
    def use_object(self, object_name: str) -> Tuple[bool, str]:
        """Use an object (context-specific actions)"""
        if not self.is_initialized or not self.game_state:
            return False, "Game not initialized."
        
        gs = self.game_state
        
        # Check if player is in a location
        if not gs.world_position.current_location_id:
            return False, "You must be inside a location to use objects."
        
        # Get current location data
        location_data = gs.world_position.current_location_data
        if not location_data:
            return False, "No location data available."
        
        # Get objects from the location's starting area
        areas = location_data.get("areas", {})
        starting_area_id = location_data.get("starting_area", "entrance")
        
        if starting_area_id not in areas:
            return False, "No objects available to use."
        
        area_data = areas[starting_area_id]
        objects = area_data.get("objects", [])
        
        # Find matching object
        target_object = None
        for obj in objects:
            obj_name = obj.get('name', '').lower()
            if object_name.lower() in obj_name or obj_name in object_name.lower():
                target_object = obj
                break
        
        if not target_object:
            return False, f"Cannot find '{object_name}' to use."
        
        # Check object properties for usage options
        properties = target_object.get('properties', {})
        obj_name = target_object.get('name', 'the object')
        
        # Implement basic usage based on properties
        if properties.get('can_light_fire'):
            if properties.get('fuel_required'):
                return True, f"You would need fuel to light a fire in {obj_name}. Try finding some wood first."
            else:
                return True, f"You light a fire in {obj_name}. Warmth spreads through the area."
        
        elif properties.get('provides_water'):
            return True, f"You drink fresh water from {obj_name}. Your thirst is quenched."
        
        elif properties.get('can_take_wood'):
            # This should probably be handled by 'take' command instead
            return False, f"You should 'take' wood from {obj_name} instead of using it."
        
        elif properties.get('provides_warmth'):
            return True, f"You warm yourself near {obj_name}."
        
        else:
            return False, f"You're not sure how to use {obj_name}."
    
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
        """Get a description of objects and items in the current location"""
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
            object_names = [obj.get("name", "Unknown") for obj in objects]
            content_parts.append(f"Objects: {', '.join(object_names)}")
        
        if items:
            item_names = [item.get("name", "Unknown") for item in items]
            content_parts.append(f"Items: {', '.join(item_names)}")
        
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
            time_system=self.time_system,
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
    

    
    def save_game(self, save_name: str) -> bool:
        """
        Save current game state.
        
        Args:
            save_name: Name for the save file
        
        Returns:
            True if save successful, False otherwise
        """
        if not self.is_initialized or not self.game_state:
            return False
        
        # For now, return a placeholder - this will be implemented in task 6.1
        print(f"Save system not yet implemented. Save name: {save_name}")
        return False
    
    def load_game(self, save_name: str) -> bool:
        """
        Load game state from save file.
        
        Args:
            save_name: Name of save file to load
        
        Returns:
            True if load successful, False otherwise
        """
        # For now, return a placeholder - this will be implemented in task 6.1
        print(f"Load system not yet implemented. Save name: {save_name}")
        return False


def test_game_engine():
    """Test GameEngine initialization and basic functionality"""
    print("=== Testing GameEngine ===")
    
    # Late imports to avoid circular dependencies
    from core.character import Character
    from core.race import Race
    from core.character_class import CharacterClass, SkillProficiencies, StartingEquipment
    
    # Create basic race and class for testing
    test_race = Race(
        name="Human",
        ability_bonuses={"strength": 1, "constitution": 1},
        size="Medium",
        speed=30,
        languages=["Common"],
        traits=[]
    )
    
    test_class = CharacterClass(
        name="Fighter",
        hit_die=10,
        primary_ability="Strength",
        saving_throw_proficiencies=["Strength", "Constitution"],
        skill_proficiencies=SkillProficiencies(choose=2, from_list=["Acrobatics", "Animal Handling"]),
        starting_equipment=[StartingEquipment(item="Chain Mail", quantity=1)]
    )
    
    test_character = Character(
        # Required stats
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        # Derived stats
        level=1,
        hp=10,
        max_hp=10,
        armor_class=16,
        proficiency_bonus=2,
        experience_points=0,
        # Identity
        name="Aldric",
        race="Human",  # Use string, not object
        character_class="Fighter",  # Use string, not object
        background="Folk Hero"
    )
    
    # Initialize GameEngine
    engine = GameEngine()
    
    # Test new game creation
    game_state = engine.new_game(test_character, world_seed=12345)
    
    print(f"✓ Game state created successfully")
    print(f"✓ Character: {game_state.character.name}")
    print(f"✓ Starting hex: {game_state.world_position.hex_data['name']} ({game_state.world_position.hex_id})")
    print(f"✓ Weather: {game_state.current_weather.temperature:.0f}°F")
    
    # Test status retrieval
    status = engine.get_status()
    print(f"✓ Status retrieved: {status['character']['name']}")
    
    # Test hex description
    description = engine.get_hex_description()
    print(f"✓ Hex description generated ({len(description)} characters)")
    
    print("=== GameEngine test complete ===")
    return engine


def test_movement_system():
    """Test the movement system integration"""
    print("\n=== Testing Movement System ===")
    
    # Create test engine
    engine = test_game_engine()
    
    print(f"\nStarting position: {engine.game_state.world_position.hex_id}")
    print(f"Starting time: {engine.game_state.game_time.get_time_string()}")
    
    # Test movement in each direction
    directions = ["north", "south", "east", "west"]
    
    for direction in directions:
        print(f"\n--- Testing movement {direction} ---")
        success, message = engine.move_player(direction)
        
        if success:
            print(f"✓ Movement {direction} successful")
            print(f"✓ New position: {engine.game_state.world_position.hex_id}")
            print(f"✓ New location: {engine.game_state.world_position.hex_data['name']}")
            print(f"✓ New time: {engine.game_state.game_time.get_time_string()}")
            print(f"✓ Message: {message}")
            break  # Only test one successful movement
        else:
            print(f"✗ Movement {direction} failed: {message}")
    
    # Test invalid movement
    print(f"\n--- Testing invalid movement ---")
    success, message = engine.move_player("invalid_direction")
    if not success:
        print(f"✓ Invalid direction properly rejected: {message}")
    else:
        print(f"✗ Invalid direction should have failed")
    
    print("=== Movement System test complete ===")
    return engine


def test_action_handler_integration():
    """Test ActionHandler integration with GameEngine"""
    print("\n=== Testing Action Handler Integration ===")
    
    # Create test engine
    engine = test_game_engine()
    
    # Get connected action handler
    action_handler = engine.get_action_handler()
    
    print(f"\nStarting position: {engine.game_state.world_position.hex_id}")
    
    # Test movement commands through action handler
    test_commands = [
        "north",
        "go south", 
        "move east",
        "w",
        "look",
        "invalid_command",
        "help"
    ]
    
    for command in test_commands:
        print(f"\n--- Testing command: '{command}' ---")
        result = action_handler.process_command(command)
        
        if result.success:
            print(f"✓ Command successful")
            print(f"✓ Message: {result.message}")
            if result.time_passed > 0:
                print(f"✓ Time passed: {result.time_passed} hours")
            if hasattr(result, 'data') and result.data.get('direction'):
                print(f"✓ Direction: {result.data['direction']}")
                print(f"✓ New position: {engine.game_state.world_position.hex_id}")
        else:
            print(f"✗ Command failed: {result.message}")
    
    print("=== Action Handler Integration test complete ===")
    return engine


def test_location_system():
    """Test location entry/exit system integration"""
    print("\n=== Testing Location System ===")
    
    # Create test engine
    engine = test_game_engine()
    
    # Get connected action handler
    action_handler = engine.get_action_handler()
    
    print(f"\nStarting position: {engine.game_state.world_position.hex_id}")
    print(f"Available locations: {len(engine.game_state.world_position.available_locations)}")
    
    # Configuration for debug dumps
    ENABLE_DEBUG_DUMPS = False  # Set to True to enable location data dumps
    
    # Test location commands
    location_commands = [
        "look",           # Check current area
        "enter",          # Enter first available location
        "look",           # Look around inside location
    ]
    
    # Add debug dump if enabled
    if ENABLE_DEBUG_DUMPS:
        location_commands.append("dump_location")  # Dump location data for analysis
    
    # Continue with regular test commands
    location_commands.extend([
        "examine fireplace", # Test object examination
        "search old furniture", # Test object searching
        "take firewood",     # Test item taking
        "use fireplace",     # Test object usage
        "exit",           # Exit back to overworld
        "look",           # Confirm back in overworld
        "debug",          # Test debug command
    ])
    
    for command in location_commands:
        print(f"\n--- Testing location command: '{command}' ---")
        result = action_handler.process_command(command)
        
        if result.success:
            print(f"✓ Command successful")
            print(f"✓ Message: {result.message}")
            if result.time_passed > 0:
                print(f"✓ Time passed: {result.time_passed} hours")
            
            # Show current location status
            current_loc = engine.game_state.world_position.current_location_id
            if current_loc:
                print(f"✓ Currently in location: {current_loc}")
            else:
                print(f"✓ Currently in overworld")
        else:
            print(f"✗ Command failed: {result.message}")
    
    # Test persistence - enter location, exit, re-enter
    print(f"\n--- Testing location persistence ---")
    
    # Enter location
    result1 = action_handler.process_command("enter")
    if result1.success:
        print("✓ Entered location")
        
        # Exit location
        result2 = action_handler.process_command("exit")
        if result2.success:
            print("✓ Exited location")
            
            # Re-enter same location
            result3 = action_handler.process_command("enter")
            if result3.success:
                print("✓ Re-entered location - testing persistence")
                print(f"✓ Location data should be persistent")
            else:
                print(f"✗ Failed to re-enter: {result3.message}")
        else:
            print(f"✗ Failed to exit: {result2.message}")
    else:
        print(f"✗ Failed to enter: {result1.message}")
    
    print("=== Location System test complete ===")
    return engine


if __name__ == "__main__":
    test_location_system()