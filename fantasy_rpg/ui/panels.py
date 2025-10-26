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
            from ..core.character_creation import create_character_quick
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
        info_widget = self.query_one("#character-info")
        info_widget.update(self._render_character_info())
    
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
        
        return f"""{char.name}
Lv {char.level} {char.race} {char.character_class}

HP: {char.hp}/{char.max_hp} {hp_bar}
AC: {char.armor_class}
{xp_info}
{encumbrance_info}

abilities:
{abilities_text}

environment:
{world["weather"]}

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


class GameLogPanel(ScrollableContainer):
    """Center panel showing game events and messages with scrolling"""
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.max_messages = 1000  # Keep last 1000 messages
        self.turn_counter = 1847
        self.day_counter = 5
        
        # Add some initial messages
        self._add_initial_messages()
    
    def compose(self) -> ComposeResult:
        yield Static(self._render_log(), id="game-log", markup=False)
    
    def _add_initial_messages(self):
        """Add some initial demo messages"""
        initial_messages = [
            "=== Fantasy RPG Game Log ===",
            "",
            "Welcome to the world of adventure!",
            "Your journey begins in the ancient forest...",
            "",
            "> move north",
            "You travel through the dense forest.",
            "Time passes: 30 minutes",
            "",
            "[Perception Check: 16] Success!",
            "You notice fresh wolf tracks in the mud.",
            "The tracks lead deeper into the forest.",
            "",
            "> examine tracks",
            "The wolf tracks are large and recent.",
            "You estimate they were made within the last hour.",
            "There appear to be at least 3 different wolves.",
            "",
            "[Survival Check: 14] Success!",
            "You can follow these tracks if you choose.",
            "",
            "> look around",
            "You are in a dense forest clearing.",
            "Ancient oak trees tower above you.",
            "Sunlight filters through the canopy.",
            "You hear birds chirping in the distance.",
            "",
            "Available exits: North, South, East, West",
            "",
            "--- Use arrow keys or mouse to scroll ---",
            "--- Type 'help' for available commands ---"
        ]
        
        for message in initial_messages:
            self.messages.append(message)
    
    def add_message(self, message: str, message_type: str = "normal"):
        """Add a new message to the log"""
        # Add timestamp for certain message types
        if message_type in ["system", "combat", "level_up"]:
            timestamp = f"[Turn {self.turn_counter}] "
            formatted_message = timestamp + message
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
        """Add a system message with timestamp"""
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
        log_widget = self.query_one("#game-log")
        log_widget.update(self._render_log())
    
    def _render_log(self) -> str:
        """Render game log messages"""
        if not self.messages:
            return "No messages yet..."
        
        header = f"Turn {self.turn_counter}, Day {self.day_counter}\n\n"
        
        # Join all messages
        content = "\n".join(self.messages)
        
        # Add scroll indicator at the bottom
        footer = "\n\n--- End of Log ---"
        
        return header + content + footer
    
    def get_message_count(self) -> int:
        """Get the current number of messages"""
        return len(self.messages)
    
    def get_recent_messages(self, count: int = 10) -> list:
        """Get the most recent messages"""
        return self.messages[-count:] if self.messages else []
    
    def advance_turn(self):
        """Advance the turn counter"""
        self.turn_counter += 1
        if self.turn_counter % 100 == 0:  # New day every 100 turns
            self.day_counter += 1
            self.add_system_message(f"A new day dawns... Day {self.day_counter}")
    
    def save_log_to_file(self, filename: str = "game_log.txt"):
        """Save the current log to a file"""
        try:
            with open(filename, 'w') as f:
                f.write(f"Fantasy RPG Game Log - Turn {self.turn_counter}, Day {self.day_counter}\n")
                f.write("=" * 50 + "\n\n")
                for message in self.messages:
                    f.write(message + "\n")
            self.add_system_message(f"Game log saved to {filename}")
        except Exception as e:
            self.add_system_message(f"Failed to save log: {str(e)}")
    
    def search_messages(self, search_term: str) -> list:
        """Search for messages containing a specific term"""
        matching_messages = []
        for i, message in enumerate(self.messages):
            if search_term.lower() in message.lower():
                matching_messages.append((i, message))
        return matching_messages


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