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
            
            mock_char = MockCharacter()
            # Add empty inventory for UI compatibility
            mock_char.inventory = None
            mock_char._legacy_inventory = []
            return mock_char
    
    def compose(self) -> ComposeResult:
        yield Static(self._render_character_info(), id="character-info", markup=False)
    
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
        
        # Format ability scores with modifiers
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
            
            survival_text = f"""
----------------------------
survival:
Hunger: {hunger_desc} 
Thirst: {thirst_desc} 
Fatigue: {fatigue_desc}
Warmth: {warmth_desc} 
Dryness: {wetness_desc}
----------------------------
condition:"""
            
            if player_state.status_effects:
                for effect in player_state.status_effects[:3]:  # Show first 3 effects
                    survival_text += f"\n• {effect}"
            else:
                survival_text += "\nHealthy"
        
        # Get realistic environment description
        environment_text = self._get_environment_description(char)
        
        return f"""{char.name}
Lv {char.level} {char.race} {char.character_class}

HP: {char.hp}/{char.max_hp} {hp_bar}
AC: {char.armor_class}
{xp_info}
{encumbrance_info}

----------------------------
abilities:
{abilities_text}{survival_text}

----------------------------
environment:
{environment_text}
----------------------------
location:
Hex {world["hex"]} - {world["location"]}
Elevation: {world["elevation"]}"""
    
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
Humidity: {humidity}"""
        else:
            return """Temperature: Mild
Wind: Light breeze
Sky: Clear
Weather: Sunny
Humidity: Moderate"""
    
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
        """Add some initial demo messages"""
        initial_messages = [
            "You find yourself in a forest clearing.",
            "Ancient oak trees tower above you, their branches swaying gently in the breeze.",
            "Sunlight filters through the canopy, casting dappled shadows on the forest floor.",
            "",
            "Type 'help' for available commands.",
            "Type 'look' to examine your surroundings.",
            "Type 'survival' to check your condition."
        ]
        
        for message in initial_messages:
            self.messages.append(message)
    
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
            header = f"The adventure begins...\n\n"
        
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
        try:
            with open(filename, 'w') as f:
                if self.player_state:
                    time_desc = self._get_natural_time_description()
                    f.write(f"Fantasy RPG Adventure Log - {time_desc}\n")
                else:
                    f.write("Fantasy RPG Adventure Log\n")
                f.write("=" * 50 + "\n\n")
                for message in self.messages:
                    f.write(message + "\n")
            self.add_system_message(f"Adventure log saved to {filename}")
        except Exception as e:
            self.add_system_message(f"Failed to save log: {str(e)}")
    
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
        # Current location info
        current_info = self.get_current_location_info()
        current_symbol = self._get_location_symbol(current_info["type"])
        
        poi_text = f"""current location:
{current_symbol} {current_info["name"]}
Hex: {self.current_hex}
{current_info["description"]}

nearby locations:"""
        
        # Get and display nearby locations
        nearby = self.get_nearby_locations()
        if nearby:
            for location in nearby:
                symbol = self._get_location_symbol(location["type"])
                direction = location["direction"].upper()
                poi_text += f"""
{symbol} {location["name"]} ({direction})
    {location["distance"]} - {location["type"]}"""
        else:
            poi_text += "\nNo nearby locations discovered"
        
        poi_text += "\n\navailable commands:"
        
        # Display commands
        for cmd in self.commands:
            poi_text += f"\n[{cmd['key']}] {cmd['name']}"
        
        poi_text += "\n\nmovement:"
        poi_text += "\nType: n/s/e/w or north/south/east/west"
        
        return poi_text
    
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