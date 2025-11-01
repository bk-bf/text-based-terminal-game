"""
Fantasy RPG - UI Panels

Visual display components for the main game interface.
"""

try:
    from textual.app import ComposeResult
    from textual.containers import ScrollableContainer
    from textual.widgets import Static
    from textual import events
except ImportError:
    import sys
    print("Error: Textual library not found!")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()
    print("Try one of these solutions:")
    print("1. Use the same Python version that has textual installed:")
    print("   /opt/homebrew/bin/python3.11 fantasy_rpg/ui.py")
    print()
    print("2. Install textual for your current Python:")
    print("   pip3 install textual>=0.40.0 rich>=13.0.0")
    print()
    print("3. Or install using the specific pip for your Python:")
    print(f"   {sys.executable} -m pip install textual>=0.40.0 rich>=13.0.0")
    exit(1)

# Import custom colors
try:
    from .colors import format_survival_text, format_temperature_text, format_wetness_text
except ImportError:
    from colors import format_survival_text, format_temperature_text, format_wetness_text


class CharacterPanel(Static):
    """Left panel showing character stats and current status"""
    
    def __init__(self, character=None):
        super().__init__()
        self.character = character
        self.world_data = {
            "weather": "Clear, 68°F",
            "hex": "0847", 
            "location": "Forest",
            "elevation": "320 ft"
        }
        
        # Create a sample character if none provided
        if self.character is None:
            self.character = self._create_sample_character()
    
    def _create_sample_character(self):
        """Create a sample character for demonstration"""
        try:
            try:
                from ..core.character_creation import create_character_quick
            except ImportError:
                from fantasy_rpg.core.character_creation import create_character_quick
            character, _, _ = create_character_quick("Aldric", "Human", "Fighter")
            # Modify some stats for demo
            character.hp = 32
            character.max_hp = 45
            character.level = 3
            character.experience_points = 900
            
            # Ensure inventory is properly initialized
            if not hasattr(character, 'inventory') or character.inventory is None:
                character.initialize_inventory()
            
            return character
        except ImportError:
            # Fallback to mock data if character system not available
            class MockCharacter:
                def __init__(self):
                    self.name = "Aldric"
                    self.level = 3
                    self.hp = 32
                    self.max_hp = 45
                    self.armor_class = 18
                    self.experience_points = 900
                    self.strength = 16
                    self.dexterity = 14
                    self.constitution = 15
                    self.intelligence = 12
                    self.wisdom = 13
                    self.charisma = 10
                    self.race = "Human"
                    self.character_class = "Fighter"
                    self.base_speed = 30
                
                def ability_modifier(self, ability):
                    score = getattr(self, ability)
                    return (score - 10) // 2
                
                def get_xp_to_next_level(self):
                    return 1900 - self.experience_points
                
                def get_encumbrance_level(self):
                    return "Light"
                
                def initialize_inventory(self):
                    pass
                
                def get_inventory_weight(self):
                    return 0.0
                
                def get_carrying_capacity(self):
                    return 150.0
                
                def get_total_equipment_weight(self):
                    return 0.0
                
                def get_total_equipment_value(self):
                    return 0
                
                def get_equipped_item(self, slot):
                    return None
                
                def get_condition_modifier(self, ability):
                    return 0
                
                def get_effective_speed(self):
                    return self.base_speed
            
            mock_char = MockCharacter()
            # Add empty inventory for UI compatibility
            mock_char.inventory = None
            mock_char._legacy_inventory = []
            return mock_char
    
    def compose(self) -> ComposeResult:
        yield Static(self._render_character_info(), id="character-info", markup=True)
    
    def update_character(self, character):
        """Update the character data and refresh display"""
        self.character = character
        self.refresh_display()
    
    def update_world_data(self, weather=None, hex_id=None, location=None, elevation=None):
        """Update world/location data and refresh display"""
        if weather is not None:
            self.world_data["weather"] = weather
        if hex_id is not None:
            self.world_data["hex"] = hex_id
        if location is not None:
            self.world_data["location"] = location
        if elevation is not None:
            self.world_data["elevation"] = elevation
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the character panel display"""
        try:
            info_widget = self.query_one("#character-info")
            info_widget.update(self._render_character_info())
        except:
            # Widget not mounted yet, ignore
            pass
    
    def _render_character_info(self) -> str:
        """Render character information as text"""
        char = self.character
        world = self.world_data
        
        # Create HP bar
        hp_bar = self._create_bar(char.hp, char.max_hp, 10)
        
        # Calculate XP progress
        try:
            xp_to_next = char.get_xp_to_next_level()
            xp_info = f"XP: {char.experience_points} ({xp_to_next} to next)"
        except:
            xp_info = f"XP: {char.experience_points}"
        
        # Get encumbrance info
        try:
            encumbrance = char.get_encumbrance_level()
            encumbrance_info = f"Load: {encumbrance}"
        except:
            encumbrance_info = "Load: Light"
        
        # Get speed info
        try:
            speed = char.get_effective_speed()
            speed_info = f"Speed: {speed}ft"
        except:
            speed_info = "Speed: 30ft"
        
        # Format ability scores with modifiers (now includes condition effects)
        abilities_text = f"""STR: {char.strength} ({char.ability_modifier('strength'):+d})
DEX: {char.dexterity} ({char.ability_modifier('dexterity'):+d})
CON: {char.constitution} ({char.ability_modifier('constitution'):+d})
INT: {char.intelligence} ({char.ability_modifier('intelligence'):+d})
WIS: {char.wisdom} ({char.ability_modifier('wisdom'):+d})
CHA: {char.charisma} ({char.ability_modifier('charisma'):+d})"""
        
        # Add survival status if available
        survival_text = ""
        if hasattr(char, 'player_state') and char.player_state:
            player_state = char.player_state
            bars = player_state.get_survival_bars()
            
            # Get sophisticated status descriptions
            hunger_desc = self._get_hunger_description(player_state.survival.get_hunger_level())
            thirst_desc = self._get_thirst_description(player_state.survival.get_thirst_level())
            fatigue_desc = self._get_fatigue_description(player_state.survival.get_fatigue_level())
            warmth_desc = self._get_warmth_description(player_state.survival.get_temperature_status())
            wetness_desc = self._get_wetness_description(player_state.survival.get_wetness_level())
            
            # Add color coding to survival descriptions
            hunger_colored = self._add_survival_color(hunger_desc, player_state.survival.get_hunger_level())
            thirst_colored = self._add_survival_color(thirst_desc, player_state.survival.get_thirst_level())
            fatigue_colored = self._add_survival_color(fatigue_desc, player_state.survival.get_fatigue_level())
            warmth_colored = self._add_temperature_color(warmth_desc, player_state.survival.get_temperature_status())
            wetness_colored = self._add_wetness_color(wetness_desc, player_state.survival.get_wetness_level())
            
            survival_text = f"""
----------------------------
survival:
Hunger: {hunger_colored} 
Thirst: {thirst_colored} 
Fatigue: {fatigue_colored}
Warmth: {warmth_colored} 
Dryness: {wetness_colored}
----------------------------
condition:"""
            
            # Use conditions system to get active conditions
            try:
                # Try different import paths
                try:
                    from ..game.conditions import get_conditions_manager
                except ImportError:
                    from game.conditions import get_conditions_manager
                
                conditions_manager = get_conditions_manager()
                active_conditions = conditions_manager.evaluate_conditions(player_state)
                
                if active_conditions:
                    # Format conditions with severity colors (show ALL conditions)
                    formatted_conditions = []
                    for condition in active_conditions:
                        # Use the conditions manager to format with colors
                        color = conditions_manager.get_condition_severity_color(condition)
                        formatted_conditions.append(f"[{color}]{condition}[/]")
                    
                    condition_list = ", ".join(formatted_conditions)
                    survival_text += f"\n{condition_list}"
                    
            except (ImportError, Exception) as e:
                # Fallback to old system if conditions system not available
                print(f"Conditions system not available: {e}")
                if hasattr(player_state, 'status_effects') and player_state.status_effects:
                    # Remove duplicates and show all unique effects
                    unique_effects = list(dict.fromkeys(player_state.status_effects))
                    formatted_conditions = [f"[{effect}]" for effect in unique_effects if effect and effect.strip()]
                    
                    if formatted_conditions:
                        condition_list = ", ".join(formatted_conditions)
                        survival_text += f"\n{condition_list}"
        
        # Get realistic environment description
        environment_text = self._get_environment_description(char)
        
        return f"""{char.name}
Lv {char.level} {char.race} {char.character_class}

HP: {char.hp}/{char.max_hp} {hp_bar}
AC: {char.armor_class}
{xp_info}
{encumbrance_info}
{speed_info}

----------------------------
abilities:
{abilities_text}{survival_text}

----------------------------
environment:
{environment_text}
"""
    
    def _create_bar(self, current: int, maximum: int, width: int) -> str:
        """Create a simple text-based progress bar"""
        if maximum <= 0:
            return "▓" * width
        
        filled = int((current / maximum) * width)
        empty = width - filled
        
        # Ensure we don't exceed the width
        filled = min(filled, width)
        empty = max(0, width - filled)
        
        return "█" * filled + "▓" * empty
    
    def _get_hunger_description(self, level) -> str:
        """Get sophisticated hunger description"""
        descriptions = {
            "EXCELLENT": "Satiated",
            "GOOD": "Well-fed", 
            "NORMAL": "Content",
            "POOR": "Peckish",
            "BAD": "Famished",
            "CRITICAL": "Starving"
        }
        return descriptions.get(level.name, "Content")
    
    def _get_thirst_description(self, level) -> str:
        """Get sophisticated thirst description"""
        descriptions = {
            "EXCELLENT": "Hydrated",
            "GOOD": "Refreshed",
            "NORMAL": "Quenched", 
            "POOR": "Parched",
            "BAD": "Dehydrated",
            "CRITICAL": "Desiccated"
        }
        return descriptions.get(level.name, "Quenched")
    
    def _get_fatigue_description(self, level) -> str:
        """Get sophisticated fatigue description"""
        descriptions = {
            "EXCELLENT": "Invigorated",
            "GOOD": "Energetic",
            "NORMAL": "Rested",
            "POOR": "Weary", 
            "BAD": "Exhausted",
            "CRITICAL": "Depleted"
        }
        return descriptions.get(level.name, "Rested")
    
    def _get_warmth_description(self, status) -> str:
        """Get sophisticated warmth description"""
        descriptions = {
            "FREEZING": "Freezing",
            "VERY_COLD": "Chilled", 
            "COLD": "Cool",
            "COOL": "Fresh",
            "COMFORTABLE": "Pleasant",
            "WARM": "Cozy",
            "HOT": "Heated",
            "VERY_HOT": "Sweltering", 
            "OVERHEATING": "Scorching"
        }
        return descriptions.get(status.name, "Pleasant")
    
    def _get_wetness_description(self, level) -> str:
        """Get sophisticated wetness description"""
        descriptions = {
            "DRY": "Dry",
            "DAMP": "Moist",
            "WET": "Damp", 
            "SOAKED": "Sodden",
            "DRENCHED": "Soaked"
        }
        return descriptions.get(level.name, "Dry")
    
    def _add_survival_color(self, description: str, level) -> str:
        """Add color coding to survival descriptions based on level"""
        return format_survival_text(description, level.name)
    
    def _add_temperature_color(self, description: str, status) -> str:
        """Add color coding to temperature descriptions"""
        return format_temperature_text(description, status.name)
    
    def _add_wetness_color(self, description: str, level) -> str:
        """Add color coding to wetness descriptions"""
        return format_wetness_text(description, level.name)
    
    def _get_elevation_description(self) -> str:
        """Get natural language elevation description"""
        elevation_str = self.world_data.get("elevation", "320 ft")
        
        # Extract numeric value from elevation string
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
    
    def _get_environment_description(self, char) -> str:
        """Get realistic environment description without modern measurements"""
        if hasattr(char, 'player_state') and char.player_state and char.player_state.current_weather:
            weather = char.player_state.current_weather
            
            # Temperature description based on character sensation
            temp_desc = self._get_ambient_temperature_description(weather.feels_like)
            
            # Sky conditions (cloud cover only)
            if weather.cloud_cover > 90:
                sky_desc = "Overcast"
            elif weather.cloud_cover > 60:
                sky_desc = "Cloudy"
            elif weather.cloud_cover > 30:
                sky_desc = "Partly cloudy"
            elif weather.cloud_cover < 10:
                sky_desc = "Clear"
            else:
                sky_desc = "Fair"
            
            # Weather conditions (precipitation, sun, storms)
            weather_conditions = []
            
            # Check for precipitation first
            if weather.precipitation > 0:
                if weather.precipitation_type == "rain":
                    if weather.precipitation > 70:
                        weather_conditions.append("Heavy rain")
                    elif weather.precipitation > 40:
                        weather_conditions.append("Steady rain")
                    else:
                        weather_conditions.append("Light rain")
                elif weather.precipitation_type == "snow":
                    if weather.precipitation > 70:
                        weather_conditions.append("Heavy snowfall")
                    elif weather.precipitation > 40:
                        weather_conditions.append("Steady snow")
                    else:
                        weather_conditions.append("Light snow")
                elif weather.precipitation_type == "sleet":
                    weather_conditions.append("Sleet")
                elif weather.precipitation_type == "hail":
                    weather_conditions.append("Hailstorm")
            else:
                # No precipitation - check for sunny conditions
                if weather.cloud_cover < 30:
                    weather_conditions.append("Sunny")
                elif weather.cloud_cover < 60:
                    weather_conditions.append("Partly sunny")
                else:
                    weather_conditions.append("Dry")
            
            # Storm conditions (can occur with or without precipitation)
            if weather.is_storm:
                if not any("rain" in cond.lower() or "snow" in cond.lower() for cond in weather_conditions):
                    weather_conditions.append("Dry storm")
            
            # Visibility conditions
            if weather.visibility < 500:
                weather_conditions.append("Poor visibility")
            elif weather.visibility < 1000:
                weather_conditions.append("Hazy")
            
            weather_desc = ", ".join(weather_conditions) if weather_conditions else "Fair"
            
            # Humidity (estimated from precipitation and cloud cover)
            humidity = self._estimate_humidity(weather)
            
            return f"""Temperature: {temp_desc}
Wind: {self._get_wind_description(weather.wind_speed)}
Sky: {sky_desc}
Weather: {weather_desc}
Humidity: {humidity}
Elevation: {self._get_elevation_description()}"""
        else:
            return f"""Temperature: Mild
Wind: Light breeze
Sky: Clear
Weather: Sunny
Humidity: Moderate
Elevation: {self._get_elevation_description()}"""
    
    def _get_ambient_temperature_description(self, temp_f: float) -> str:
        """Get ambient temperature description without numbers"""
        if temp_f < 20:
            return "Bitter cold"
        elif temp_f < 32:
            return "Freezing"
        elif temp_f < 45:
            return "Cold"
        elif temp_f < 55:
            return "Cool"
        elif temp_f < 70:
            return "Mild"
        elif temp_f < 80:
            return "Warm"
        elif temp_f < 90:
            return "Hot"
        elif temp_f < 100:
            return "Very hot"
        else:
            return "Scorching"
    
    def _get_wind_description(self, wind_speed: float) -> str:
        """Get wind condition description"""
        if wind_speed < 1:
            return "Still air"
        elif wind_speed < 4:
            return "Light air"
        elif wind_speed < 8:
            return "Light breeze"
        elif wind_speed < 13:
            return "Gentle breeze"
        elif wind_speed < 19:
            return "Moderate breeze"
        elif wind_speed < 25:
            return "Fresh breeze"
        elif wind_speed < 32:
            return "Strong breeze"
        elif wind_speed < 39:
            return "Near gale"
        elif wind_speed < 47:
            return "Gale"
        elif wind_speed < 55:
            return "Strong gale"
        elif wind_speed < 64:
            return "Storm"
        else:
            return "Hurricane"
    
    def _estimate_humidity(self, weather) -> str:
        """Estimate humidity from weather conditions"""
        humidity_score = 0
        
        # Base humidity from precipitation
        if weather.precipitation > 50:
            humidity_score += 3
        elif weather.precipitation > 20:
            humidity_score += 2
        elif weather.precipitation > 0:
            humidity_score += 1
        
        # Cloud cover affects humidity
        if weather.cloud_cover > 80:
            humidity_score += 2
        elif weather.cloud_cover > 50:
            humidity_score += 1
        
        # Temperature affects perceived humidity
        if weather.temperature > 80:
            humidity_score += 1
        elif weather.temperature < 40:
            humidity_score -= 1
        
        # Wind reduces perceived humidity
        if weather.wind_speed > 20:
            humidity_score -= 1
        
        if humidity_score >= 5:
            return "Oppressive"
        elif humidity_score >= 3:
            return "Humid"
        elif humidity_score >= 1:
            return "Moderate"
        elif humidity_score >= -1:
            return "Dry"
        else:
            return "Arid"


class GameLogPanel(ScrollableContainer):
    """Center panel showing game events and messages with scrolling"""
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.max_messages = 1000  # Keep last 1000 messages
        self.player_state = None  # Will be set by app
        
        # Add some initial messages
        self._add_initial_messages()
    
    def compose(self) -> ComposeResult:
        yield Static(self._render_log(), id="game-log", markup=False)
    
    def _add_initial_messages(self):
        """Add initial messages - now handled by GameEngine initialization"""
        # Initial messages are now added by the GameEngine initialization process
        pass
    
    def add_message(self, message: str, message_type: str = "normal"):
        """Add a new message to the log"""
        # Format message based on type
        if message_type == "combat":
            formatted_message = f"[!] {message}"
        elif message_type == "level_up":
            formatted_message = f"[^] {message}"
        else:
            formatted_message = message
        
        self.messages.append(formatted_message)
        
        # Keep only the last max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        # Refresh the display
        self.refresh_log()
        
        # Auto-scroll to bottom to show new message
        self.scroll_end()
    
    def add_command(self, command: str):
        """Add a player command to the log"""
        self.add_message(f"> {command}", "command")
    
    def add_system_message(self, message: str):
        """Add a system message"""
        self.add_message(message, "system")
    
    def add_combat_message(self, message: str):
        """Add a combat message with special formatting"""
        self.add_message(f"[!] {message}", "combat")
    
    def add_level_up_message(self, message: str):
        """Add a level up message with special formatting"""
        self.add_message(f"[^] {message}", "level_up")
    
    def add_separator(self):
        """Add a visual separator line"""
        self.add_message("")
    
    def clear_log(self):
        """Clear all messages from the log"""
        self.messages = []
        self.refresh_log()
    
    def refresh_log(self):
        """Refresh the log display"""
        try:
            log_widget = self.query_one("#game-log")
            log_widget.update(self._render_log())
        except:
            # Widget not mounted yet, ignore
            pass
    
    def _render_log(self) -> str:
        """Render game log messages"""
        if not self.messages:
            return "No messages yet..."
        
        # Get current time from player state if available
        if self.player_state:
            time_str = self._get_natural_time_description()
            header = f"{time_str}\n\n"
        else:
            header = ""  # No header when no player state
        
        # Join all messages
        content = "\n".join(self.messages)
        
        # Add subtle scroll indicator at the bottom
        footer = "\n\n~"
        
        return header + content + footer
    
    def get_message_count(self) -> int:
        """Get the current number of messages"""
        return len(self.messages)
    
    def get_recent_messages(self, count: int = 10) -> list:
        """Get the most recent messages"""
        return self.messages[-count:] if self.messages else []
    
    def advance_turn(self):
        """Advance the turn counter (legacy method, no longer used)"""
        # This method is kept for compatibility but no longer tracks turns
        pass
    
    def save_log_to_file(self, filename: str = "game_log.txt"):
        """Save the current log to a file"""
        import os
        from datetime import datetime
        
        try:
            # Generate filename with timestamp if default is used
            if filename == "game_log.txt":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"adventure_log_{timestamp}.txt"
            
            # Save directly in the game directory (no subdirectory)
            
            # Write the log file
            with open(filename, 'w', encoding='utf-8') as f:
                # Header with game info
                f.write("=" * 60 + "\n")
                f.write("FANTASY RPG - ADVENTURE LOG\n")
                f.write("=" * 60 + "\n\n")
                
                # Time and character info
                if self.player_state:
                    time_desc = self._get_natural_time_description()
                    f.write(f"Session Time: {time_desc}\n")
                    
                    # Add character info if available
                    if hasattr(self.player_state, 'character') and self.player_state.character:
                        char = self.player_state.character
                        f.write(f"Character: {char.name} (Level {char.level} {char.race} {char.character_class})\n")
                        f.write(f"HP: {char.hp}/{char.max_hp}, AC: {char.armor_class}\n")
                else:
                    f.write(f"Log saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                f.write(f"Total messages: {len(self.messages)}\n")
                f.write("\n" + "=" * 60 + "\n\n")
                
                # Write all messages
                for i, message in enumerate(self.messages, 1):
                    # Clean up message formatting for file output
                    clean_message = message.replace("[!]", "⚠️").replace("[^]", "⬆️").replace("[*]", "✦")
                    f.write(f"{clean_message}\n")
                
                # Footer
                f.write("\n" + "=" * 60 + "\n")
                f.write("End of Adventure Log\n")
                f.write("=" * 60 + "\n")
            
            # Get file size for confirmation
            file_size = os.path.getsize(filename)
            size_kb = file_size / 1024
            
            self.add_system_message(f"📝 Adventure log saved to {filename}")
            self.add_system_message(f"   File size: {size_kb:.1f} KB ({len(self.messages)} messages)")
            
        except Exception as e:
            self.add_system_message(f"❌ Failed to save log: {str(e)}")
            # Try fallback save to current directory
            try:
                fallback_filename = f"adventure_log_backup_{datetime.now().strftime('%H%M%S')}.txt"
                with open(fallback_filename, 'w', encoding='utf-8') as f:
                    f.write("Fantasy RPG Adventure Log (Emergency Backup)\n")
                    f.write("=" * 50 + "\n\n")
                    for message in self.messages:
                        f.write(message + "\n")
                self.add_system_message(f"📝 Backup log saved to {fallback_filename}")
            except Exception as backup_error:
                self.add_system_message(f"❌ Backup save also failed: {str(backup_error)}")
    
    def search_messages(self, search_term: str) -> list:
        """Search for messages containing a specific term"""
        matching_messages = []
        for i, message in enumerate(self.messages):
            if search_term.lower() in message.lower():
                matching_messages.append((i, message))
        return matching_messages
    
    def _get_natural_time_description(self) -> str:
        """Get natural language time description without precise measurements"""
        if not self.player_state:
            return "The adventure begins..."
        
        # Get approximate time of day based on game hour
        hour = int(self.player_state.game_hour)  # Convert to int to avoid float precision issues
        day = self.player_state.game_day
        
        # Time of day descriptions
        if 5 <= hour < 7:
            time_desc = "Early dawn"
        elif 7 <= hour < 9:
            time_desc = "Morning"
        elif 9 <= hour < 12:
            time_desc = "Late morning"
        elif 12 <= hour < 14:
            time_desc = "Midday"
        elif 14 <= hour < 17:
            time_desc = "Afternoon"
        elif 17 <= hour < 19:
            time_desc = "Late afternoon"
        elif 19 <= hour < 21:
            time_desc = "Evening"
        elif 21 <= hour < 23:
            time_desc = "Late evening"
        elif 23 <= hour or hour < 2:
            time_desc = "Deep night"
        elif 2 <= hour < 5:
            time_desc = "Before dawn"
        else:
            time_desc = "Night"
        
        # Day descriptions
        if day == 1:
            day_desc = "the first day"
        elif day == 2:
            day_desc = "the second day"
        elif day == 3:
            day_desc = "the third day"
        elif day <= 7:
            day_desc = f"day {day}"
        elif day <= 14:
            day_desc = f"the {day}th day of your journey"
        else:
            weeks = day // 7
            remaining_days = day % 7
            if weeks == 1:
                if remaining_days == 0:
                    day_desc = "after a week of travel"
                else:
                    day_desc = f"over a week into your journey"
            else:
                day_desc = f"after {weeks} weeks of adventure"
        
        return f"{time_desc} of {day_desc}"


class POIPanel(Static):
    """Right panel showing points of interest and commands"""
    
    def __init__(self):
        super().__init__()
        self.current_hex = "0847"
        self.current_location = "Forest Clearing"
        
        # Define a world map with locations and their connections
        self.world_map = {
            "0847": {
                "name": "Forest Clearing",
                "type": "forest",
                "description": "A peaceful clearing surrounded by ancient oaks",
                "connections": {
                    "north": "0746",
                    "south": "0948", 
                    "east": "0848",
                    "west": "0746"
                }
            },
            "0746": {
                "name": "Ancient Ruins",
                "type": "ruins",
                "description": "Crumbling stone structures from a forgotten age",
                "connections": {
                    "south": "0847",
                    "east": "0747"
                }
            },
            "0848": {
                "name": "Mountain Pass",
                "type": "mountain",
                "description": "A narrow path through rocky peaks",
                "connections": {
                    "west": "0847",
                    "north": "0747",
                    "south": "0949"
                }
            },
            "0948": {
                "name": "Trading Village",
                "type": "settlement",
                "description": "A bustling village with merchants and travelers",
                "connections": {
                    "north": "0847",
                    "east": "0949"
                }
            },
            "0949": {
                "name": "Crystal Cave",
                "type": "cave",
                "description": "A mysterious cave filled with glowing crystals",
                "connections": {
                    "west": "0948",
                    "north": "0848"
                }
            },
            "0747": {
                "name": "Wizard's Tower",
                "type": "tower",
                "description": "A tall spire crackling with magical energy",
                "connections": {
                    "west": "0746",
                    "south": "0848"
                }
            }
        }
        
        # Available commands
        self.commands = [
            {"key": "i", "name": "Inventory", "description": "View carried items"},
            {"key": "c", "name": "Character", "description": "Character sheet"},
            {"key": "m", "name": "Map", "description": "World map"},
            {"key": "r", "name": "Rest", "description": "Rest and recover"},
            {"key": "l", "name": "Look", "description": "Look around"}
        ]
    
    def compose(self) -> ComposeResult:
        yield Static(self._render_poi_info(), id="poi-info", markup=False)
    
    def update_location(self, hex_id: str, location_name: str):
        """Update current location and refresh nearby POIs"""
        self.current_hex = hex_id
        self.current_location = location_name
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the POI panel display"""
        info_widget = self.query_one("#poi-info")
        info_widget.update(self._render_poi_info())
    
    def update_with_game_engine(self, game_engine):
        """Update POI panel with real GameEngine world data"""
        if not game_engine or not game_engine.is_initialized:
            return
            
        gs = game_engine.game_state
        self.current_hex = gs.world_position.hex_id
        
        # Get current location name
        if gs.world_position.current_location_id:
            location_data = gs.world_position.current_location_data
            if location_data:
                self.current_location = f"{location_data.get('name', 'Unknown Location')} ({gs.world_position.hex_data['name']})"
            else:
                self.current_location = f"Inside Location ({gs.world_position.hex_data['name']})"
        else:
            self.current_location = gs.world_position.hex_data['name']
        
        # Get available locations in current hex
        self.available_locations = []
        self.current_location_id = gs.world_position.current_location_id
        self.location_connections = {}
        
        try:
            hex_locations = game_engine.world_coordinator.get_hex_locations(self.current_hex)
            for loc in hex_locations:
                self.available_locations.append(loc.get('name', 'Unknown Location'))
            
            # If player is inside a location, get connections from GameEngine
            if self.current_location_id and len(hex_locations) > 1:
                current_index = None
                for i, loc in enumerate(hex_locations):
                    if loc.get("id") == self.current_location_id:
                        current_index = i
                        break
                
                if current_index is not None:
                    # Use GameEngine's location graph logic for consistency
                    location_graph = game_engine._create_location_graph(hex_locations, current_index)
                    
                    # Convert to display format
                    for direction, location_data in location_graph.items():
                        self.location_connections[direction] = location_data.get('name', 'Unknown Location')
        except:
            self.available_locations = []
        
        # Get adjacent hex information
        self.adjacent_hexes = {}
        try:
            coords = gs.world_position.coords
            x, y = coords
            
            # Get adjacent coordinates
            adjacent_coords = {
                'North': (x, y-1),
                'South': (x, y+1), 
                'East': (x+1, y),
                'West': (x-1, y)
            }
            
            # Get hex data for each direction
            for direction, (adj_x, adj_y) in adjacent_coords.items():
                try:
                    # Check if coordinates are valid
                    if 0 <= adj_x < 20 and 0 <= adj_y < 20:  # Assuming 20x20 world
                        adj_hex_id = f"{adj_x:02d}{adj_y:02d}"
                        adj_hex_data = game_engine.world_coordinator.get_hex_info(adj_hex_id)
                        if adj_hex_data:
                            self.adjacent_hexes[direction] = {
                                'name': adj_hex_data.get('name', f'Hex {adj_hex_id}'),
                                'biome': adj_hex_data.get('type', 'unknown'),
                                'hex_id': adj_hex_id
                            }
                        else:
                            self.adjacent_hexes[direction] = {'name': 'Unknown', 'biome': 'unknown', 'hex_id': adj_hex_id}
                    else:
                        self.adjacent_hexes[direction] = {'name': 'Edge of World', 'biome': 'void', 'hex_id': 'N/A'}
                except:
                    self.adjacent_hexes[direction] = {'name': 'Unknown', 'biome': 'unknown', 'hex_id': 'N/A'}
        except:
            self.adjacent_hexes = {}
        
        self.refresh_display()
    
    def get_nearby_locations(self):
        """Get locations connected to current hex"""
        current_location = self.world_map.get(self.current_hex, {})
        connections = current_location.get("connections", {})
        
        nearby = []
        for direction, hex_id in connections.items():
            if hex_id in self.world_map:
                location = self.world_map[hex_id]
                distance = self._calculate_distance(self.current_hex, hex_id)
                nearby.append({
                    "direction": direction,
                    "hex": hex_id,
                    "name": location["name"],
                    "type": location["type"],
                    "description": location["description"],
                    "distance": distance
                })
        
        return nearby
    
    def get_current_location_info(self):
        """Get detailed info about current location"""
        return self.world_map.get(self.current_hex, {
            "name": self.current_location,
            "type": "unknown",
            "description": "An unexplored area"
        })
    
    def _calculate_distance(self, hex1: str, hex2: str):
        """Calculate distance between two hexes (simplified)"""
        # For now, adjacent hexes are 1 hex away
        return "1 hex"
    
    def _get_location_symbol(self, location_type: str) -> str:
        """Get ASCII symbol for location type"""
        symbols = {
            "forest": "[T]",
            "ruins": "[R]", 
            "mountain": "[^]",
            "settlement": "[H]",
            "cave": "[C]",
            "tower": "[|]",
            "unknown": "[?]"
        }
        return symbols.get(location_type, "[?]")
    
    def _render_poi_info(self) -> str:
        """Render POI and command information"""
        poi_text = f"""current location:
[#] {self.current_location}
Hex: {self.current_hex}

locations in this hex:"""
        
        # Show available locations in current hex
        if hasattr(self, 'available_locations') and self.available_locations:
            if hasattr(self, 'current_location_id') and self.current_location_id:
                # Player is inside a location - show connections to other locations
                poi_text += f"\nConnected locations:"
                if hasattr(self, 'location_connections') and self.location_connections:
                    for direction, location_name in self.location_connections.items():
                        poi_text += f"\n  {direction.title()}: {location_name}"
                else:
                    poi_text += "\n  No connections from here"
            else:
                # Player is in overworld - show locations to enter
                poi_text += f"\nYou can enter: {', '.join(self.available_locations)}"
        else:
            poi_text += "\nNo locations to enter here"
        
        poi_text += "\n\nadjacent hexes:"
        
        # Show adjacent hexes with real world data
        if hasattr(self, 'adjacent_hexes') and self.adjacent_hexes:
            for direction, hex_info in self.adjacent_hexes.items():
                biome_symbol = self._get_biome_symbol(hex_info.get('biome', 'unknown'))
                poi_text += f"\n{biome_symbol} {direction}: {hex_info['name']}"
        else:
            poi_text += "\nNorth: Unknown"
            poi_text += "\nSouth: Unknown" 
            poi_text += "\nEast: Unknown"
            poi_text += "\nWest: Unknown"
        
        poi_text += "\n\navailable commands:"
        poi_text += "\n[i] inventory"
        poi_text += "\n[c] character"
        poi_text += "\n[look] examine area"
        poi_text += "\n[enter] enter location"
        poi_text += "\n[exit] exit to overworld"
        poi_text += "\n[help] show all commands"
        
        poi_text += "\n\nmovement:"
        poi_text += "\nType: n/s/e/w or north/south/east/west"
        
        return poi_text
    
    def _get_biome_symbol(self, biome: str) -> str:
        """Get symbol for biome type"""
        symbols = {
            'forest': '[T]',
            'plains': '[~]', 
            'mountain': '[^]',
            'desert': '[.]',
            'swamp': '[S]',
            'tundra': '[*]',
            'coast': '[~]',
            'unknown': '[?]',
            'void': '[ ]'
        }
        return symbols.get(biome, '[?]')
    
    def get_travel_options(self):
        """Get available travel destinations"""
        nearby = self.get_nearby_locations()
        options = []
        
        for location in nearby:
            options.append({
                "key": location["direction"][0].lower(),  # n, s, e, w
                "direction": location["direction"],
                "hex": location["hex"],
                "name": location["name"],
                "type": location["type"]
            })
        
        return options
    
    def can_travel_to(self, direction: str) -> bool:
        """Check if travel in direction is possible"""
        current_location = self.world_map.get(self.current_hex, {})
        connections = current_location.get("connections", {})
        return direction.lower() in connections
    
    def get_destination_hex(self, direction: str) -> str:
        """Get hex ID for travel direction"""
        current_location = self.world_map.get(self.current_hex, {})
        connections = current_location.get("connections", {})
        return connections.get(direction.lower(), self.current_hex)
    
    def get_location_by_hex(self, hex_id: str):
        """Get location info by hex ID"""
        return self.world_map.get(hex_id, {
            "name": f"Unknown Location {hex_id}",
            "type": "unknown",
            "description": "An unexplored area"
        })
    
    def discover_new_location(self, hex_id: str, name: str, location_type: str, description: str):
        """Add a new location to the world map"""
        self.world_map[hex_id] = {
            "name": name,
            "type": location_type,
            "description": description,
            "connections": {}
        }
        self.refresh_display()
    
    def add_connection(self, from_hex: str, to_hex: str, direction: str):
        """Add a connection between two locations"""
        if from_hex in self.world_map:
            if "connections" not in self.world_map[from_hex]:
                self.world_map[from_hex]["connections"] = {}
            self.world_map[from_hex]["connections"][direction] = to_hex