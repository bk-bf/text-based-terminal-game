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
        gs.current_weather = generate_weather_state(
            base_temp, 
            gs.game_time.season, 
            climate_type
        )
        
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
        objects = location_data.get("objects", [])
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
            print(f"✓ Message: {message[:100]}...")
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
            print(f"✓ Message: {result.message[:100]}...")
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
    
    # Test location commands
    location_commands = [
        "look",           # Check current area
        "enter",          # Enter first available location
        "look",           # Look around inside location
        "exit",           # Exit back to overworld
        "look",           # Confirm back in overworld
        "debug",          # Test debug command
    ]
    
    for command in location_commands:
        print(f"\n--- Testing location command: '{command}' ---")
        result = action_handler.process_command(command)
        
        if result.success:
            print(f"✓ Command successful")
            print(f"✓ Message: {result.message[:150]}...")
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