"""
Fantasy RPG - Action Logger

Centralized system for logging action results with consistent formatting.
Handles dice rolls, results, time passage, weather changes, and other effects.
"""

from typing import Dict, List, Optional, Any
import random


class ActionLogger:
    """Centralized logging system for all game actions"""
    
    def __init__(self, game_log_panel=None):
        self.game_log_panel = game_log_panel
        self.last_weather = None
        
    def set_game_log(self, game_log_panel):
        """Set the game log panel for output"""
        self.game_log_panel = game_log_panel
    
    def log_action_result(self, action_type: str, result: Dict[str, Any], 
                         character=None, player_state=None, **kwargs):
        """
        Log a complete action result with all standard components.
        
        Args:
            action_type: Type of action (move, rest, look, eat, drink, sleep, etc.)
            result: Result dictionary from time system or action handler
            character: Character object for dice rolls and stats
            player_state: Player state for weather and time info
            **kwargs: Additional action-specific parameters
        """
        if not self.game_log_panel:
            return
        
        # 1. Log the command that was executed
        self._log_command(action_type, **kwargs)
        
        # 2. Log any dice rolls made
        self._log_dice_rolls(action_type, result, character, **kwargs)
        
        # 3. Log the main action result
        self._log_main_result(action_type, result, **kwargs)
        
        # 4. Log time passage (if any)
        self._log_time_passage(result)
        
        # 5. Log weather changes (if any)
        self._log_weather_changes(player_state)
        
        # 6. Log secondary effects
        self._log_secondary_effects(action_type, result, character, **kwargs)
        
        # 7. Add separator
        self.game_log_panel.add_message("")
    
    def _log_command(self, action_type: str, **kwargs):
        """Log the command that was executed"""
        command_formats = {
            "move": lambda **k: f"move to {k.get('destination', 'unknown location')}",
            "rest": lambda **k: "rest",
            "look": lambda **k: "look",
            "eat": lambda **k: "eat",
            "drink": lambda **k: "drink", 
            "sleep": lambda **k: "sleep",
            "inventory": lambda **k: "inventory",
            "character": lambda **k: "character",
            "map": lambda **k: "map",
            "help": lambda **k: "help",
            "survival": lambda **k: "survival status"
        }
        
        formatter = command_formats.get(action_type, lambda **k: action_type)
        command_text = formatter(**kwargs)
        self.game_log_panel.add_command(command_text)
    
    def _log_dice_rolls(self, action_type: str, result: Dict[str, Any], 
                       character=None, **kwargs):
        """Log any dice rolls made for the action"""
        # Define which actions require dice rolls and what kind
        dice_actions = {
            "move": self._roll_travel_checks,
            "look": self._roll_perception_check,
            "rest": self._roll_rest_check,
            "sleep": self._roll_sleep_check
        }
        
        if action_type in dice_actions and character:
            dice_actions[action_type](character, result, **kwargs)
    
    def _roll_travel_checks(self, character, result: Dict[str, Any], **kwargs):
        """Roll dice for travel actions"""
        if not result.get("success", True):
            return
            
        # Navigation check (Wisdom + Survival or just Wisdom)
        nav_roll = random.randint(1, 20)
        wis_mod = character.ability_modifier('wisdom')
        nav_total = nav_roll + wis_mod
        
        self.game_log_panel.add_message(f"[Navigation: {nav_roll} + {wis_mod} = {nav_total}]")
        
        # Determine navigation result
        if nav_total >= 15:
            self.game_log_panel.add_message("You navigate confidently through the terrain.")
        elif nav_total >= 10:
            self.game_log_panel.add_message("You find your way without difficulty.")
        elif nav_total >= 5:
            self.game_log_panel.add_message("You take a slightly longer route but arrive safely.")
        else:
            self.game_log_panel.add_message("You get briefly turned around but eventually find your way.")
    
    def _roll_perception_check(self, character, result: Dict[str, Any], **kwargs):
        """Roll perception check for looking around"""
        perc_roll = random.randint(1, 20)
        wis_mod = character.ability_modifier('wisdom')
        perc_total = perc_roll + wis_mod
        
        self.game_log_panel.add_message(f"[Perception: {perc_roll} + {wis_mod} = {perc_total}]")
        
        # Add perception-based details
        if perc_total >= 18:
            self.game_log_panel.add_message("You notice fine details in your surroundings.")
        elif perc_total >= 13:
            self.game_log_panel.add_message("You observe your environment carefully.")
        elif perc_total >= 8:
            self.game_log_panel.add_message("You take in the basic features of the area.")
        else:
            self.game_log_panel.add_message("You glance around casually.")
    
    def _roll_rest_check(self, character, result: Dict[str, Any], **kwargs):
        """Roll for rest effectiveness"""
        if not result.get("success", True):
            return
            
        # Constitution check for rest quality
        con_roll = random.randint(1, 20)
        con_mod = character.ability_modifier('constitution')
        con_total = con_roll + con_mod
        
        self.game_log_panel.add_message(f"[Rest Quality: {con_roll} + {con_mod} = {con_total}]")
    
    def _roll_sleep_check(self, character, result: Dict[str, Any], **kwargs):
        """Roll for sleep quality"""
        if not result.get("success", True):
            return
            
        # Constitution check for sleep quality
        con_roll = random.randint(1, 20)
        con_mod = character.ability_modifier('constitution')
        con_total = con_roll + con_mod
        
        self.game_log_panel.add_message(f"[Sleep Quality: {con_roll} + {con_mod} = {con_total}]")
        
        if con_total >= 15:
            self.game_log_panel.add_message("You sleep deeply and peacefully.")
        elif con_total >= 10:
            self.game_log_panel.add_message("You sleep well.")
        elif con_total >= 5:
            self.game_log_panel.add_message("You sleep fitfully but get some rest.")
        else:
            self.game_log_panel.add_message("You toss and turn, getting poor rest.")
    
    def _log_main_result(self, action_type: str, result: Dict[str, Any], **kwargs):
        """Log the main result of the action"""
        # Use the message from the result if available
        if result.get("message"):
            self.game_log_panel.add_message(result["message"])
        
        # Add action-specific additional results
        action_results = {
            "move": self._log_move_result,
            "look": self._log_look_result,
            "inventory": self._log_inventory_result,
            "character": self._log_character_result,
            "map": self._log_map_result,
            "help": self._log_help_result,
            "survival": self._log_survival_result
        }
        
        if action_type in action_results:
            action_results[action_type](result, **kwargs)
    
    def _log_move_result(self, result: Dict[str, Any], **kwargs):
        """Log movement-specific results"""
        destination = kwargs.get('destination')
        hex_id = kwargs.get('hex_id')
        elevation = kwargs.get('elevation')
        nearby_locations = kwargs.get('nearby_locations', [])
        
        if result.get("success", True) and destination:
            self.game_log_panel.add_message(f"[>] You travel to {destination} (Hex {hex_id})")
            if elevation:
                natural_elevation = self._convert_elevation_to_natural(elevation)
                self.game_log_panel.add_message(f"Elevation: {natural_elevation}")
            
            # Show nearby locations
            if nearby_locations:
                self.game_log_panel.add_message("You can see:")
                for loc in nearby_locations:
                    symbol = loc.get('symbol', '[?]')
                    name = loc.get('name', 'Unknown')
                    direction = loc.get('direction', 'somewhere')
                    self.game_log_panel.add_message(f"  {symbol} {name} to the {direction}")
    
    def _log_look_result(self, result: Dict[str, Any], **kwargs):
        """Log look action results"""
        location_info = kwargs.get('location_info')
        weather_desc = kwargs.get('weather_desc')
        
        if location_info:
            self.game_log_panel.add_message(f"You look around {location_info['name']}:")
            self.game_log_panel.add_message(location_info['description'])
            
            if weather_desc:
                self.game_log_panel.add_message("")
                self.game_log_panel.add_message("Current weather:")
                # Use the weather description as-is (should already be natural from panels.py)
                self.game_log_panel.add_message(weather_desc)
    
    def _log_inventory_result(self, result: Dict[str, Any], **kwargs):
        """Log inventory action results"""
        self.game_log_panel.add_message("Opening inventory...")
    
    def _log_character_result(self, result: Dict[str, Any], **kwargs):
        """Log character sheet action results"""
        self.game_log_panel.add_message("Reviewing character details...")
    
    def _log_map_result(self, result: Dict[str, Any], **kwargs):
        """Log map action results"""
        current_location = kwargs.get('current_location')
        nearby_locations = kwargs.get('nearby_locations', [])
        
        self.game_log_panel.add_message("Consulting map...")
        if current_location:
            self.game_log_panel.add_message(f"Current: {current_location['name']} ({current_location.get('hex', 'unknown')})")
            self.game_log_panel.add_message("Nearby locations:")
            for loc in nearby_locations:
                symbol = loc.get('symbol', '[?]')
                name = loc.get('name', 'Unknown')
                direction = loc.get('direction', 'somewhere')
                self.game_log_panel.add_message(f"  {symbol} {name} ({direction})")
    
    def _log_help_result(self, result: Dict[str, Any], **kwargs):
        """Log help action results"""
        # Help content is handled elsewhere, just acknowledge
        pass
    
    def _log_survival_result(self, result: Dict[str, Any], **kwargs):
        """Log survival status results"""
        survival_summary = kwargs.get('survival_summary')
        current_time = kwargs.get('current_time')
        
        if survival_summary:
            self.game_log_panel.add_message("Current survival status:")
            self.game_log_panel.add_message("")
            for line in survival_summary.split('\n'):
                if line.strip():
                    self.game_log_panel.add_message(line)
            self.game_log_panel.add_message("")
            if current_time:
                self.game_log_panel.add_message(f"Current time: {current_time}")
    
    def _log_time_passage(self, result: Dict[str, Any]):
        """Log time passage in natural language"""
        time_desc = result.get("time_passed_description")
        if time_desc and result.get("duration_hours", 0) > 0:
            self.game_log_panel.add_message(f"{time_desc} passes.")
    
    def _log_weather_changes(self, player_state):
        """Log weather changes in natural language"""
        if not player_state or not player_state.current_weather:
            return
        
        current_weather = player_state.current_weather
        
        # Check if weather has changed significantly
        if self.last_weather is None:
            self.last_weather = current_weather
            return
        
        # Compare weather conditions
        temp_change = abs(current_weather.feels_like - self.last_weather.feels_like)
        precip_change = abs(current_weather.precipitation - self.last_weather.precipitation)
        wind_change = abs(current_weather.wind_speed - self.last_weather.wind_speed)
        cloud_change = abs(current_weather.cloud_cover - self.last_weather.cloud_cover)
        
        weather_changes = []
        
        # Temperature changes (only log significant changes)
        if temp_change > 15:  # Increased threshold to reduce spam
            if current_weather.feels_like > self.last_weather.feels_like:
                weather_changes.append("The air grows warmer")
            else:
                weather_changes.append("The air grows cooler")
        
        # Precipitation changes (only log meaningful changes)
        if precip_change > 25:  # Increased threshold
            if current_weather.precipitation > self.last_weather.precipitation:
                if current_weather.precipitation_type == "rain":
                    weather_changes.append("Rain begins to fall")
                elif current_weather.precipitation_type == "snow":
                    weather_changes.append("Snow begins to fall")
            else:
                weather_changes.append("The precipitation lessens")
        
        # Wind changes (only log noticeable changes)
        if wind_change > 15:  # Increased threshold
            if current_weather.wind_speed > self.last_weather.wind_speed:
                weather_changes.append("The wind picks up")
            else:
                weather_changes.append("The wind dies down")
        
        # Cloud changes (only log significant changes)
        if cloud_change > 40:  # Increased threshold
            if current_weather.cloud_cover > self.last_weather.cloud_cover:
                weather_changes.append("Clouds gather overhead")
            else:
                weather_changes.append("The clouds begin to clear")
        
        # Log weather changes
        if weather_changes:
            self.game_log_panel.add_message(f"[~] {', '.join(weather_changes)}.")
        
        # Update last weather
        self.last_weather = current_weather
    
    def _log_secondary_effects(self, action_type: str, result: Dict[str, Any], 
                              character=None, **kwargs):
        """Log secondary effects like status changes, level ups, etc."""
        # Status effects
        if result.get("status_effects"):
            for effect in result["status_effects"]:
                self.game_log_panel.add_message(f"• {effect}")
        
        # Level up notifications
        if result.get("level_up"):
            self.game_log_panel.add_level_up_message(f"{character.name} leveled up to level {character.level}!")
        
        # Health changes
        if result.get("hp_change"):
            hp_change = result["hp_change"]
            if hp_change > 0:
                self.game_log_panel.add_message(f"[+] Recovered {hp_change} HP")
            elif hp_change < 0:
                self.game_log_panel.add_combat_message(f"Lost {abs(hp_change)} HP")
        
        # Survival warnings
        if character and hasattr(character, 'player_state') and character.player_state:
            self._check_survival_warnings(character.player_state)
    
    def _check_survival_warnings(self, player_state):
        """Check and log survival warnings"""
        warnings = []
        
        # Check hunger
        hunger_level = player_state.survival.get_hunger_level()
        if hunger_level.value <= 1:  # BAD or CRITICAL
            if hunger_level.value == 0:
                warnings.append("You are starving!")
            else:
                warnings.append("You are very hungry.")
        
        # Check thirst
        thirst_level = player_state.survival.get_thirst_level()
        if thirst_level.value <= 1:  # BAD or CRITICAL
            if thirst_level.value == 0:
                warnings.append("You are severely dehydrated!")
            else:
                warnings.append("You are very thirsty.")
        
        # Check fatigue
        fatigue_level = player_state.survival.get_fatigue_level()
        if fatigue_level.value <= 1:  # BAD or CRITICAL
            if fatigue_level.value == 0:
                warnings.append("You are exhausted!")
            else:
                warnings.append("You are very tired.")
        
        # Check temperature risks
        if player_state.survival.hypothermia_risk > 60:
            warnings.append("You are getting dangerously cold.")
        elif player_state.survival.hyperthermia_risk > 60:
            warnings.append("You are overheating.")
        
        # Log warnings
        for warning in warnings:
            self.game_log_panel.add_message(f"[!] {warning}")
    
    def _convert_elevation_to_natural(self, elevation_str: str) -> str:
        """Convert elevation to natural language description"""
        try:
            if "ft" in elevation_str:
                elevation_ft = int(elevation_str.replace("ft", "").strip())
            else:
                elevation_ft = 320  # Default
        except:
            elevation_ft = 320  # Default fallback
        
        # Convert to natural language descriptions
        if elevation_ft < 100:
            return "Near sea level"
        elif elevation_ft < 500:
            return "Low hills"
        elif elevation_ft < 1000:
            return "Rolling hills"
        elif elevation_ft < 2000:
            return "High hills"
        elif elevation_ft < 3000:
            return "Low mountains"
        elif elevation_ft < 5000:
            return "Mountains"
        elif elevation_ft < 8000:
            return "High mountains"
        else:
            return "Alpine peaks"


# Global action logger instance
action_logger = ActionLogger()


def get_action_logger():
    """Get the global action logger instance"""
    return action_logger