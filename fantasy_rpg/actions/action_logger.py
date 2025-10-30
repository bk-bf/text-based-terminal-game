"""
Fantasy RPG - Action Logger

Centralized logging system that formats action results for display.
Separates logging logic from UI presentation.
"""

from typing import Dict, List, Optional, Any
import random


class ActionLogger:
    """Centralized logging system for all game messages and actions"""
    
    def __init__(self):
        self.game_log = None
        self.last_weather = None
        self.message_queue = []  # Queue messages when game_log not available
        
    def set_game_log(self, game_log):
        """Set the game log panel for output and flush queued messages"""
        self.game_log = game_log
        
        # Debug: Print connection info
        print(f"ActionLogger: Connected to game_log panel: {game_log}")
        print(f"ActionLogger: Queued messages to flush: {len(self.message_queue)}")
        
        # Flush any queued messages
        if self.message_queue and self.game_log:
            for message_data in self.message_queue:
                message_type = message_data.get('type', 'normal')
                message = message_data.get('message', '')
                
                if message_type == 'command':
                    self.game_log.add_command(message)
                elif message_type == 'system':
                    self.game_log.add_system_message(message)
                elif message_type == 'combat':
                    self.game_log.add_combat_message(message)
                elif message_type == 'level_up':
                    self.game_log.add_level_up_message(message)
                else:
                    self.game_log.add_message(message, message_type)
            
            self.message_queue.clear()
            print(f"ActionLogger: Flushed {len(self.message_queue)} messages")
    
    def log_action_result(self, action_result, character=None, **kwargs):
        """
        Log a complete action result with standardized formatting.
        
        Args:
            action_result: ActionResult object from ActionHandler
            character: Character object for dice rolls and stats
            **kwargs: Additional context (command_text, etc.)
        """
        if not self.game_log:
            return
        
        # 1. Log the command that was executed
        command_text = kwargs.get('command_text', '')
        if command_text:
            self._log_command(command_text)
        
        # 2. Log any dice rolls made
        self._log_dice_rolls(action_result, character)
        
        # 3. Log the main action result
        self._log_main_result(action_result)
        
        # 4. Log time passage (if any)
        self._log_time_passage(action_result)
        
        # 5. Log weather changes (if any)
        player_state = kwargs.get('player_state')
        if player_state:
            self._log_weather_changes(player_state)
        
        # 6. Log secondary effects
        self._log_secondary_effects(action_result, character)
        
        # 7. Add separator for readability
        self.game_log.add_message("")
    
    def _log_command(self, command_text: str):
        """Log the command that was executed"""
        self.game_log.add_command(command_text)
    
    def _log_dice_rolls(self, action_result, character):
        """Log any dice rolls made for the action"""
        if not character:
            return
        
        # Check if action had skill checks
        skill_check = action_result.get('skill_check')
        if skill_check:
            skill_name = skill_check.get('skill', 'Skill')
            roll = skill_check.get('roll', 0)
            modifier = skill_check.get('modifier', 0)
            total = skill_check.get('total', 0)
            dc = skill_check.get('dc', 15)
            
            self.game_log.add_message(f"[{skill_name} Check: {roll} + {modifier} = {total} vs DC {dc}]")
            return
        
        # Determine action type and roll appropriate dice
        movement_type = action_result.get('movement_type')
        if movement_type == 'overworld':
            self._roll_navigation_check(character)
        elif movement_type == 'local':
            # Local movement doesn't need rolls usually
            pass
        
        # Look actions get perception checks
        if action_result.get('location_info'):
            self._roll_perception_check(character)
    
    def _roll_navigation_check(self, character):
        """Roll navigation check for overworld travel"""
        nav_roll = random.randint(1, 20)
        wis_mod = character.ability_modifier('wisdom')
        nav_total = nav_roll + wis_mod
        
        self.game_log.add_message(f"[Navigation: {nav_roll} + {wis_mod} = {nav_total}]")
        
        if nav_total >= 15:
            self.game_log.add_message("You navigate confidently through the terrain.")
        elif nav_total >= 10:
            self.game_log.add_message("You find your way without difficulty.")
        elif nav_total >= 5:
            self.game_log.add_message("You take a slightly longer route but arrive safely.")
        else:
            self.game_log.add_message("You get briefly turned around but eventually find your way.")
    
    def _roll_perception_check(self, character):
        """Roll perception check for looking around"""
        perc_roll = random.randint(1, 20)
        wis_mod = character.ability_modifier('wisdom')
        perc_total = perc_roll + wis_mod
        
        self.game_log.add_message(f"[Perception: {perc_roll} + {wis_mod} = {perc_total}]")
        
        if perc_total >= 18:
            self.game_log.add_message("You notice fine details in your surroundings.")
        elif perc_total >= 13:
            self.game_log.add_message("You observe your environment carefully.")
        elif perc_total >= 8:
            self.game_log.add_message("You take in the basic features of the area.")
        else:
            self.game_log.add_message("You glance around casually.")
    
    def _log_main_result(self, action_result):
        """Log the main result of the action"""
        if action_result.message:
            self.game_log.add_message(action_result.message)
        
        # Handle specific action types
        self._log_movement_result(action_result)
        self._log_location_result(action_result)
        self._log_foraging_result(action_result)
        self._log_shelter_result(action_result)
        self._log_map_result(action_result)
        self._log_status_result(action_result)
    
    def _log_movement_result(self, action_result):
        """Log movement-specific results"""
        movement_type = action_result.get('movement_type')
        if not movement_type:
            return
        
        if movement_type == 'overworld':
            destination = action_result.get('destination', {})
            hex_id = action_result.get('hex_id')
            nearby = action_result.get('nearby_locations', [])
            
            if hex_id:
                self.game_log.add_message(f"[>] You travel to {destination.get('name', 'Unknown')} (Hex {hex_id})")
                
                # Show elevation in natural language
                elevation = destination.get('elevation', '320 ft')
                natural_elevation = self._convert_elevation_to_natural(elevation)
                self.game_log.add_message(f"Elevation: {natural_elevation}")
                
                # Show nearby locations
                if nearby:
                    self.game_log.add_message("You can see:")
                    for loc in nearby:
                        name = loc.get('name', 'Unknown')
                        direction = loc.get('direction', 'somewhere')
                        self.game_log.add_message(f"  {name} to the {direction}")
        
        elif movement_type == 'local':
            destination = action_result.get('destination', {})
            self.game_log.add_message(f"[>] You move to {destination.get('name', 'Unknown Area')}")
    
    def _log_location_result(self, action_result):
        """Log location interaction results"""
        # Handle entering/exiting locations
        if action_result.get('entered_from') == 'overworld':
            location = action_result.get('location', {})
            self.game_log.add_message(f"You are now inside {location.get('name', 'the location')}.")
            
        elif action_result.get('exited_to') == 'overworld':
            hex_info = action_result.get('hex_info', {})
            self.game_log.add_message(f"You are back in {hex_info.get('name', 'the wilderness')}.")
        
        # Handle look results
        location_info = action_result.get('location_info')
        weather_info = action_result.get('weather_info')
        
        if location_info and not action_result.get('entered_from'):
            # This is a look action, not an enter action
            description = location_info.get('description', '')
            if description and description != action_result.message:
                self.game_log.add_message(description)
            
            # Add weather if available
            if weather_info:
                weather_desc = weather_info.get_description()
                if weather_desc:
                    self.game_log.add_message("")
                    self.game_log.add_message("Current weather:")
                    # Show first few lines of weather description
                    weather_lines = weather_desc.split('\n')[:3]
                    for line in weather_lines:
                        if line.strip():
                            self.game_log.add_message(line.strip())
    
    def _log_foraging_result(self, action_result):
        """Log foraging action results"""
        items_found = action_result.get('items_found', [])
        object_name = action_result.get('object_name', 'object')
        experience_gained = action_result.get('experience_gained', 0)
        
        if action_result.success and items_found:
            self.game_log.add_message(f"Items foraged from {object_name}:")
            for item in items_found:
                self.game_log.add_message(f"  • {item}")
            
            if experience_gained > 0:
                self.game_log.add_message(f"[+{experience_gained} XP]")
        elif not action_result.success and object_name:
            self.game_log.add_message(f"No useful items found in {object_name}.")
    
    def _log_shelter_result(self, action_result):
        """Log shelter action results"""
        shelter_created = action_result.get('shelter_created')
        materials_used = action_result.get('materials_used', [])
        shelters_found = action_result.get('shelters_found')
        
        if shelter_created:
            shelter_name = shelter_created.replace('_', ' ').title()
            self.game_log.add_message(f"Camp established: {shelter_name}")
            if materials_used:
                self.game_log.add_message(f"Materials consumed: {', '.join(materials_used)}")
            self.game_log.add_message("You now have shelter from the elements.")
        
        elif shelters_found is not None:
            # This was a shelter detection action
            if shelters_found == 0:
                self.game_log.add_message("No natural shelter is available at this location.")
            else:
                self.game_log.add_message(f"Found {shelters_found} shelter option(s).")
    
    def _log_map_result(self, action_result):
        """Log map action results"""
        current_location = action_result.get('current_location')
        nearby_locations = action_result.get('nearby_locations', [])
        
        if current_location:
            hex_id = current_location.get('hex', 'unknown')
            name = current_location.get('name', 'Unknown')
            self.game_log.add_message(f"Current: {name} ({hex_id})")
            
            if nearby_locations:
                self.game_log.add_message("Nearby locations:")
                for loc in nearby_locations:
                    name = loc.get('name', 'Unknown')
                    direction = loc.get('direction', 'somewhere')
                    self.game_log.add_message(f"  {name} ({direction})")
    
    def _log_status_result(self, action_result):
        """Log survival status results"""
        survival_summary = action_result.get('survival_summary')
        current_time = action_result.get('current_time')
        
        if survival_summary:
            self.game_log.add_message("Current survival status:")
            self.game_log.add_message("")
            for line in survival_summary.split('\n'):
                if line.strip():
                    self.game_log.add_message(line)
            self.game_log.add_message("")
            if current_time:
                self.game_log.add_message(f"Current time: {current_time}")
    
    def _log_time_passage(self, action_result):
        """Log time passage in natural language"""
        time_passed = action_result.time_passed
        if time_passed > 0:
            time_desc = self._format_time_passage(time_passed)
            self.game_log.add_message(f"{time_desc} passes.")
    
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
        if temp_change > 15:
            if current_weather.feels_like > self.last_weather.feels_like:
                weather_changes.append("The air grows warmer")
            else:
                weather_changes.append("The air grows cooler")
        
        # Precipitation changes
        if precip_change > 25:
            if current_weather.precipitation > self.last_weather.precipitation:
                if current_weather.precipitation_type == "rain":
                    weather_changes.append("Rain begins to fall")
                elif current_weather.precipitation_type == "snow":
                    weather_changes.append("Snow begins to fall")
            else:
                weather_changes.append("The precipitation lessens")
        
        # Wind changes
        if wind_change > 15:
            if current_weather.wind_speed > self.last_weather.wind_speed:
                weather_changes.append("The wind picks up")
            else:
                weather_changes.append("The wind dies down")
        
        # Cloud changes
        if cloud_change > 40:
            if current_weather.cloud_cover > self.last_weather.cloud_cover:
                weather_changes.append("Clouds gather overhead")
            else:
                weather_changes.append("The clouds begin to clear")
        
        # Log weather changes
        if weather_changes:
            self.game_log.add_message(f"[~] {', '.join(weather_changes)}.")
        
        # Update last weather
        self.last_weather = current_weather
    
    def _log_secondary_effects(self, action_result, character):
        """Log secondary effects like status changes, level ups, etc."""
        # HP recovery
        hp_recovered = action_result.get('hp_recovered')
        if hp_recovered and hp_recovered > 0:
            self.game_log.add_message(f"[+] Recovered {hp_recovered} HP")
        
        # Experience gained
        experience_gained = action_result.get('experience_gained')
        if experience_gained and experience_gained > 0:
            self.game_log.add_message(f"[+{experience_gained} XP]")
        
        # Check for survival warnings
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
            self.game_log.add_message(f"[!] {warning}")
    
    def log_damage_taken(self, damage_amount: int, damage_type: str, source: str, 
                        old_hp: int, new_hp: int):
        """Log damage taken from various sources"""
        if not self.game_log or damage_amount <= 0:
            return
        
        # Format damage type for display
        damage_type_display = {
            "cold": "cold",
            "heat": "heat", 
            "starvation": "starvation",
            "dehydration": "dehydration",
            "generic": "damage"
        }.get(damage_type, damage_type)
        
        # Format source for display
        source_display = {
            "Icy": "extreme cold",
            "Heat Stroke": "extreme heat",
            "Dying of Hunger": "starvation", 
            "Dying of Thirst": "dehydration"
        }.get(source, source.lower())
        
        # Log the damage with appropriate formatting
        if new_hp <= 0:
            self.game_log.add_combat_message(f"💀 You take {damage_amount} {damage_type_display} damage from {source_display} and collapse! ({old_hp} → {new_hp} HP)")
        elif damage_amount >= 3:
            self.game_log.add_combat_message(f"💥 You take {damage_amount} {damage_type_display} damage from {source_display}! ({old_hp} → {new_hp} HP)")
        else:
            self.game_log.add_combat_message(f"⚡ You take {damage_amount} {damage_type_display} damage from {source_display}. ({old_hp} → {new_hp} HP)")
    
    def log_healing_received(self, heal_amount: int, source: str, old_hp: int, new_hp: int):
        """Log healing received from various sources"""
        if heal_amount <= 0:
            return
        
        # Format source for display
        source_display = {
            "rest": "resting",
            "sleep": "sleeping",
            "food": "eating",
            "potion": "a healing potion"
        }.get(source, source)
        
        message = f"💚 You recover {heal_amount} HP from {source_display}. ({old_hp} → {new_hp} HP)"
        self._log_message(message, "normal")
    
    # Centralized logging methods for all message types
    def log_message(self, message: str, message_type: str = "normal"):
        """Log any message through the centralized system"""
        self._log_message(message, message_type)
    
    def log_command(self, command: str):
        """Log a player command"""
        self._log_message(command, "command")
    
    def log_system_message(self, message: str):
        """Log a system message"""
        self._log_message(message, "system")
    
    def log_combat_message(self, message: str):
        """Log a combat message"""
        self._log_message(message, "combat")
    
    def log_level_up_message(self, message: str):
        """Log a level up message"""
        self._log_message(message, "level_up")
    
    def log_separator(self):
        """Log a separator line"""
        self._log_message("", "normal")
    
    def clear_log(self):
        """Clear the game log"""
        if self.game_log:
            self.game_log.clear_log()
        else:
            self.message_queue.clear()
    
    def _log_message(self, message: str, message_type: str):
        """Internal method to handle message logging with queuing"""
        if self.game_log:
            # Direct logging when game_log is available
            print(f"ActionLogger: Logging '{message}' (type: {message_type}) to game_log")
            if message_type == "command":
                self.game_log.add_command(message)
            elif message_type == "system":
                self.game_log.add_system_message(message)
            elif message_type == "combat":
                self.game_log.add_combat_message(message)
            elif message_type == "level_up":
                self.game_log.add_level_up_message(message)
            else:
                self.game_log.add_message(message, message_type)
            print(f"ActionLogger: Game log now has {len(self.game_log.messages)} messages")
        else:
            # Queue message when game_log not available
            print(f"ActionLogger: Queuing '{message}' (type: {message_type}) - no game_log connected")
            self.message_queue.append({
                'message': message,
                'type': message_type
            })
    
    def _format_time_passage(self, hours: float) -> str:
        """Format time passage in natural language"""
        if hours < 0.1:  # Less than 6 minutes
            return "A few moments"
        elif hours < 0.25:  # Less than 15 minutes
            return "A short while"
        elif hours < 0.5:  # Less than 30 minutes
            return "Some time"
        elif hours < 1.0:  # Less than 1 hour
            return "About half an hour"
        elif hours < 2.0:  # Less than 2 hours
            return "About an hour"
        elif hours < 4.0:  # Less than 4 hours
            return "A couple of hours"
        elif hours < 8.0:  # Less than 8 hours
            return "Several hours"
        else:
            return "Many hours"
    
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
_action_logger = ActionLogger()


def get_action_logger():
    """Get the global action logger instance"""
    return _action_logger