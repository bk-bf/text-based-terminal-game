"""
Fantasy RPG - Save Manager

Handles all game save/load operations including:
- Saving complete game state to JSON
- Loading game state from JSON
- Serializing/deserializing all game components
- World data persistence
"""

from typing import Tuple, Dict, Any
import json
import os
from datetime import datetime


class SaveManager:
    """Manages game save and load operations"""
    
    def __init__(self, game_engine):
        """
        Initialize SaveManager.
        
        Args:
            game_engine: Reference to main GameEngine for accessing game state
        """
        self.game_engine = game_engine
    
    def save_game(self, save_name: str = "save") -> Tuple[bool, str]:
        """
        Save current game state to JSON file.
        
        Args:
            save_name: Name for the save file (without extension)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.game_engine.is_initialized or not self.game_engine.game_state:
            return False, "Game not initialized - cannot save."
        
        try:
            gs = self.game_engine.game_state
            
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
            
            # Import WorldCoordinator
            from world.world_coordinator import WorldCoordinator
            
            # Create WorldCoordinator with skip_generation flag
            self.game_engine.world_coordinator = WorldCoordinator(
                world_size=self.game_engine.world_size,
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
            self.game_engine.time_system = TimeSystem(player_state)
            
            # Restore world data from save file
            self._deserialize_world_data(save_data["world_data"])
            
            # Import GameState
            from game.game_engine import GameState
            
            # Create game state
            self.game_engine.game_state = GameState(
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
            
            self.game_engine.is_initialized = True
            
            return True, f"Game loaded from {filename}"
            
        except Exception as e:
            return False, f"Failed to load game: {str(e)}"
    
    # Serialization helper methods
    
    def _serialize_character(self, character) -> dict:
        """Serialize character object to dictionary"""
        # Properly serialize inventory
        inventory_data = []
        if hasattr(character, 'inventory') and character.inventory and hasattr(character.inventory, 'items'):
            inventory_data = [item.to_dict() for item in character.inventory.items]
        
        # Properly serialize equipment using Equipment.to_dict()
        equipment_data = {}
        if hasattr(character, 'equipment') and character.equipment:
            # Equipment has to_dict() method now
            from core.equipment import Equipment
            if isinstance(character.equipment, Equipment):
                equipment_data = character.equipment.to_dict()
            else:
                # Fallback for unexpected types
                equipment_data = {}
        
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
        
        # Restore inventory items
        if "inventory" in data and data["inventory"]:
            from core.item import Item
            for item_data in data["inventory"]:
                item = Item.from_dict(item_data)
                character.inventory.items.append(item)
        
        # Restore equipment using Equipment.from_dict()
        if "equipment" in data and data["equipment"]:
            from core.equipment import Equipment
            character.equipment = Equipment.from_dict(data["equipment"])
        else:
            # Initialize empty equipment if none saved
            from core.equipment import Equipment
            character.equipment = Equipment()
        
        return character
    
    def _serialize_player_state(self, player_state) -> dict:
        """Serialize player state to dictionary"""
        survival = player_state.survival
        
        survival_data = {
            "hunger": getattr(survival, "hunger", 500),
            "thirst": getattr(survival, "thirst", 500),
            "fatigue": getattr(survival, "fatigue", 500),
            "body_temperature": getattr(survival, "body_temperature", 500),
            "warmth": getattr(survival, "warmth", 500),
            "wetness": getattr(survival, "wetness", 0),
            "wind_chill": getattr(survival, "wind_chill", 0)
        }
        
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
        
        player_state = PlayerState(character=character, game_engine=self.game_engine)
        
        # Restore survival stats
        survival_data = data["survival"]
        player_state.survival.hunger = survival_data["hunger"]
        player_state.survival.thirst = survival_data["thirst"]
        player_state.survival.fatigue = survival_data["fatigue"]
        player_state.survival.body_temperature = survival_data["body_temperature"]
        player_state.survival.warmth = survival_data["warmth"]
        player_state.survival.wetness = survival_data["wetness"]
        player_state.survival.wind_chill = survival_data["wind_chill"]
        
        # Restore game time
        if "game_time" in data:
            time_data = data["game_time"]
            player_state.game_hour = time_data["game_hour"]
            player_state.game_day = time_data["game_day"]
            player_state.game_season = time_data["game_season"]
        
        # Restore location
        if "location" in data:
            location_data = data["location"]
            player_state.current_hex = location_data["current_hex"]
            player_state.current_location = location_data["current_location"]
        
        # Restore activity
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
    
    def _serialize_world_position(self, world_position) -> dict:
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
    
    def _deserialize_world_position(self, data: dict):
        """Deserialize world position from dictionary"""
        from game.game_engine import WorldPosition
        
        return WorldPosition(
            hex_id=data["hex_id"],
            hex_data=data["hex_data"],
            available_locations=data["available_locations"],
            current_location_id=data.get("current_location_id"),
            current_location_data=data.get("current_location_data"),
            current_area_id=data.get("current_area_id", "entrance"),
            coords=tuple(data["coords"]) if data.get("coords") else None
        )
    
    def _serialize_game_time(self, game_time) -> dict:
        """Serialize game time to dictionary"""
        return {
            "year": game_time.year,
            "day": game_time.day,
            "hour": game_time.hour,
            "minute": game_time.minute,
            "season": game_time.season
        }
    
    def _deserialize_game_time(self, data: dict):
        """Deserialize game time from dictionary"""
        from game.game_engine import GameTime
        
        return GameTime(
            year=data["year"],
            day=data["day"],
            hour=data["hour"],
            minute=data["minute"],
            season=data["season"]
        )
    
    def _serialize_weather(self, weather) -> dict:
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
    
    def _deserialize_weather(self, data: dict):
        """Deserialize weather state from dictionary"""
        from world.weather_core import WeatherState
        
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
        """Serialize world coordinator data"""
        if not self.game_engine.world_coordinator:
            return {}
        
        world_data = {}
        
        # Get all hex data
        if hasattr(self.game_engine.world_coordinator, 'hex_data'):
            for coords, hex_info in self.game_engine.world_coordinator.hex_data.items():
                if isinstance(coords, tuple):
                    key = f"{coords[0]:02d}{coords[1]:02d}"
                else:
                    key = str(coords)
                world_data[key] = hex_info
        
        # Get persistent location data
        persistent_locations = {}
        if hasattr(self.game_engine.world_coordinator, 'persistent_locations'):
            persistent_locations = self.game_engine.world_coordinator.persistent_locations
        
        # Serialize mythic events
        mythic_events = []
        if hasattr(self.game_engine.world_coordinator, 'mythic_events'):
            mythic_events = self.game_engine.world_coordinator.mythic_events
        
        # Serialize historical figures
        historical_figures = []
        if hasattr(self.game_engine.world_coordinator, 'historical_figures'):
            from world.historical_figures import HistoricalFigure
            for figure in self.game_engine.world_coordinator.historical_figures:
                if isinstance(figure, HistoricalFigure):
                    historical_figures.append(figure.to_dict())
                else:
                    historical_figures.append(figure)
        
        # Serialize civilizations
        civilizations = []
        if hasattr(self.game_engine.world_coordinator, 'civilizations'):
            from world.civilizations import Civilization
            for civ in self.game_engine.world_coordinator.civilizations:
                if isinstance(civ, Civilization):
                    civilizations.append(civ.to_dict())
                else:
                    civilizations.append(civ)
        
        return {
            "hex_data": world_data,
            "persistent_locations": persistent_locations,
            "world_size": self.game_engine.world_size,
            "world_seed": self.game_engine.game_state.world_seed if self.game_engine.game_state else None,
            "mythic_events": mythic_events,
            "historical_figures": historical_figures,
            "civilizations": civilizations
        }
    
    def _deserialize_world_data(self, data: dict):
        """Deserialize world coordinator data"""
        if not self.game_engine.world_coordinator:
            return
        
        # Restore hex data
        if "hex_data" in data:
            if not hasattr(self.game_engine.world_coordinator, 'hex_data'):
                self.game_engine.world_coordinator.hex_data = {}
            
            # Convert string keys back to tuples for internal use
            for hex_id, hex_info in data["hex_data"].items():
                if len(hex_id) == 4:  # Format like "1010"
                    coords = (int(hex_id[:2]), int(hex_id[2:]))
                    self.game_engine.world_coordinator.hex_data[coords] = hex_info
                    # Also store with string key for compatibility
                    self.game_engine.world_coordinator.hex_data[hex_id] = hex_info
        
        # Restore persistent location data
        if "persistent_locations" in data:
            if not hasattr(self.game_engine.world_coordinator, 'persistent_locations'):
                self.game_engine.world_coordinator.persistent_locations = {}
            self.game_engine.world_coordinator.persistent_locations.update(data["persistent_locations"])
        
        # Restore mythic events
        if "mythic_events" in data:
            self.game_engine.world_coordinator.mythic_events = data["mythic_events"]
        else:
            self.game_engine.world_coordinator.mythic_events = []
        
        # Restore historical figures
        if "historical_figures" in data:
            from world.historical_figures import HistoricalFigure
            self.game_engine.world_coordinator.historical_figures = [
                HistoricalFigure.from_dict(fig_data) for fig_data in data["historical_figures"]
            ]
        else:
            self.game_engine.world_coordinator.historical_figures = []
        
        # Restore civilizations
        if "civilizations" in data:
            from world.civilizations import Civilization
            self.game_engine.world_coordinator.civilizations = [
                Civilization.from_dict(civ_data) for civ_data in data["civilizations"]
            ]
        else:
            self.game_engine.world_coordinator.civilizations = []
