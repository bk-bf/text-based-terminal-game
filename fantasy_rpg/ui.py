"""
Fantasy RPG - User Interface

Terminal-based user interface using Textual.
"""

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical, ScrollableContainer
    from textual.widgets import Static
    from textual.screen import Screen, ModalScreen
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
            from fantasy_rpg.character_creation import create_character_quick
            character, _, _ = create_character_quick("Aldric", "Human", "Fighter")
            # Modify some stats for demo
            character.hp = 32
            character.max_hp = 45
            character.level = 3
            character.experience_points = 900
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
            
            return MockCharacter()
    
    def compose(self) -> ComposeResult:
        yield Static(self._render_character_info(), id="character-info")
    
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
        
        return f"""CHARACTER (25%)

{char.name}
Lv {char.level} {char.race} {char.character_class}

HP: {char.hp}/{char.max_hp} {hp_bar}
AC: {char.armor_class}
{xp_info}
{encumbrance_info}

ABILITIES:
{abilities_text}

🌤 ENVIRONMENT:
{world["weather"]}

📍 LOCATION:
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
        yield Static(self._render_log(), id="game-log")
    
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
            "--- Press H/D/X/L/W to test real-time updates ---"
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
        self.add_message(f"⚔️ {message}", "combat")
    
    def add_level_up_message(self, message: str):
        """Add a level up message with special formatting"""
        self.add_message(f"🌟 {message}", "level_up")
    
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
            return "GAME LOG (50%)\n\nNo messages yet..."
        
        header = f"GAME LOG (50%) - Turn {self.turn_counter}, Day {self.day_counter}\n\n"
        
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
        self.pois = [
            {"name": "📍 Ruins (NE)", "distance": "2 hexes"},
            {"name": "🏰 Village (S)", "distance": "1 hex"},
            {"name": "🗻 Cave (W)", "distance": "This hex"}
        ]
        self.commands = [
            "[I] Inventory",
            "[C] Character", 
            "[M] Map"
        ]
    
    def compose(self) -> ComposeResult:
        yield Static(self._render_poi_info(), id="poi-info")
    
    def _render_poi_info(self) -> str:
        """Render POI and command information"""
        poi_text = "POIs (25%)\n\n"
        
        for poi in self.pois:
            poi_text += f"{poi['name']}\n{poi['distance']}\n\n"
        
        poi_text += "\n".join(self.commands)
        
        return poi_text


class QuitConfirmationScreen(ModalScreen):
    """Modal screen to confirm quitting the game"""
    
    def __init__(self):
        super().__init__()
        self.selected_option = 0  # 0 = No (default), 1 = Yes
        self.options = ["No", "Yes"]
    
    def compose(self) -> ComposeResult:
        with Vertical(id="quit-dialog"):
            yield Static("Are you sure you want to quit?", id="quit-message")
            yield Static("", id="quit-spacer")
            yield Static(self._render_options(), id="quit-options")
            yield Static("", id="quit-spacer2")
            yield Static("Use TAB/Left/Right to select, ENTER to confirm, ESC to cancel", id="quit-instruction")
    
    def _render_options(self) -> str:
        """Render the checkbox options with current selection side by side"""
        no_option = ""
        yes_option = ""
        
        # Render No option
        if self.selected_option == 0:
            no_option = "> [X] No"
        else:
            no_option = "  [ ] No"
            
        # Render Yes option  
        if self.selected_option == 1:
            yes_option = "> [X] Yes"
        else:
            yes_option = "  [ ] Yes"
        
        # Side by side layout with spacing
        return f"{no_option}        {yes_option}"
    
    def _update_display(self):
        """Update the options display"""
        options_widget = self.query_one("#quit-options")
        options_widget.update(self._render_options())
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses in the quit dialog"""
        if event.key == "tab" or event.key == "right" or event.key == "down":
            # Move to next option
            self.selected_option = (self.selected_option + 1) % len(self.options)
            self._update_display()
        elif event.key == "shift+tab" or event.key == "left" or event.key == "up":
            # Move to previous option
            self.selected_option = (self.selected_option - 1) % len(self.options)
            self._update_display()
        elif event.key == "enter":
            # Confirm selection
            if self.options[self.selected_option] == "Yes":
                self.app.exit()
            else:
                self.dismiss()
        elif event.key == "escape":
            # Cancel (always go back)
            self.dismiss()


class MainGameScreen(Screen):
    """Main game screen with three-panel layout"""
    
    def __init__(self):
        super().__init__()
        self.character_panel = CharacterPanel()
        self.game_log_panel = GameLogPanel()
        self.poi_panel = POIPanel()
    
    def compose(self) -> ComposeResult:
        """Create the three-panel layout"""
        with Vertical():
            # Title bar
            yield Static("Fantasy RPG - Turn 1847, Day 5 | Press ESC to quit", id="title-bar")
            
            # Main three-panel layout
            with Horizontal():
                yield self.character_panel
                yield self.game_log_panel
                yield self.poi_panel
            
            # Command input area
            yield Static("> _ (H=heal, D=damage, X=xp, L=move, W=weather, S=save log, ESC=quit)", id="command-input")
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses"""
        if event.key == "escape":
            self.app.push_screen(QuitConfirmationScreen())
        
        # Demo key bindings for testing real-time updates
        elif event.key == "h":
            # Heal 10 HP
            self.app.log_command("heal")
            self.app.heal_character(10)
        elif event.key == "d":
            # Take 5 damage
            self.app.log_command("take damage")
            self.app.damage_character(5)
        elif event.key == "x":
            # Gain 100 XP
            self.app.log_command("gain experience")
            self.app.add_experience(100)
        elif event.key == "l":
            # Change location (cycle through different locations)
            locations = [
                ("0848", "Mountain Pass", "450 ft"),
                ("0849", "Ancient Ruins", "380 ft"),
                ("0850", "Crystal Cave", "200 ft"),
                ("0847", "Forest Clearing", "320 ft")
            ]
            import random
            location = random.choice(locations)
            self.app.update_location(*location)
        elif event.key == "w":
            # Change weather (cycle through different weather)
            weather_options = [
                "Sunny, 72°F",
                "Rainy, 55°F", 
                "Cloudy, 65°F",
                "Stormy, 48°F",
                "Foggy, 58°F",
                "Clear, 68°F"
            ]
            import random
            weather = random.choice(weather_options)
            self.app.update_weather(weather)
        elif event.key == "s":
            # Save game log
            self.app.log_command("save log")
            if self.app.game_log_panel:
                self.app.game_log_panel.save_log_to_file()
        elif event.key == "c":
            # Clear log (for testing)
            self.app.log_command("clear log")
            if self.app.game_log_panel:
                self.app.game_log_panel.clear_log()
                self.app.log_system_message("Game log cleared")


class FantasyRPGApp(App):
    """Main Textual application"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #title-bar {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
        text-align: center;
    }
    
    Horizontal {
        height: 1fr;
    }
    
    CharacterPanel {
        width: 25%;
        border: solid $primary;
        padding: 1;
    }
    
    GameLogPanel {
        width: 50%;
        border: solid $primary;
        padding: 1;
    }
    
    POIPanel {
        width: 25%;
        border: solid $primary;
        padding: 1;
    }
    
    #command-input {
        dock: bottom;
        height: 1;
        background: $surface;
        padding: 0 1;
    }
    
    /* Quit confirmation dialog styles */
    QuitConfirmationScreen {
        align: center middle;
    }
    
    #quit-dialog {
        background: $surface;
        border: thick $primary;
        width: 35;
        height: 10;
        padding: 1;
    }
    
    #quit-message {
        text-align: center;
        margin-bottom: 1;
    }
    
    #quit-options {
        text-align: center;
        margin: 1 0;
    }
    
    #quit-instruction {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.character = None
        self.character_panel = None
    
    def on_mount(self) -> None:
        """Initialize the app"""
        main_screen = MainGameScreen()
        self.character_panel = main_screen.character_panel
        self.game_log_panel = main_screen.game_log_panel
        self.poi_panel = main_screen.poi_panel
        self.character = self.character_panel.character
        self.push_screen(main_screen)
    
    def update_character_hp(self, new_hp: int):
        """Update character HP and refresh display"""
        if self.character and self.character_panel:
            self.character.hp = max(0, min(new_hp, self.character.max_hp))
            self.character_panel.refresh_display()
    
    def heal_character(self, amount: int):
        """Heal character by amount"""
        if self.character:
            old_hp = self.character.hp
            self.character.hp = min(self.character.hp + amount, self.character.max_hp)
            healed = self.character.hp - old_hp
            if healed > 0:
                self.log_message(f"💚 {self.character.name} healed {healed} HP ({old_hp} → {self.character.hp})")
                if self.character.hp == self.character.max_hp:
                    self.log_message("You are now at full health!")
            else:
                self.log_message("Already at full health.")
            self.character_panel.refresh_display()
    
    def damage_character(self, amount: int):
        """Damage character by amount"""
        if self.character:
            old_hp = self.character.hp
            self.character.hp = max(0, self.character.hp - amount)
            damage_taken = old_hp - self.character.hp
            if damage_taken > 0:
                self.log_combat_message(f"{self.character.name} takes {damage_taken} damage ({old_hp} → {self.character.hp})")
                if self.character.hp == 0:
                    self.log_combat_message("💀 You have fallen unconscious!")
                elif self.character.hp <= self.character.max_hp * 0.25:
                    self.log_message("⚠️ You are badly wounded!")
            self.character_panel.refresh_display()
    
    def add_experience(self, xp: int):
        """Add experience points to character"""
        if self.character:
            old_level = self.character.level
            try:
                leveled_up = self.character.add_experience(xp)
                if leveled_up:
                    self.log_level_up_message(f"{self.character.name} leveled up to level {self.character.level}!")
                    self.log_message(f"New HP: {self.character.hp}/{self.character.max_hp}")
                    self.log_message(f"New AC: {self.character.armor_class}")
                else:
                    self.log_message(f"✨ {self.character.name} gains {xp} XP")
                    try:
                        xp_needed = self.character.get_xp_to_next_level()
                        self.log_message(f"({xp_needed} XP needed for level {self.character.level + 1})")
                    except:
                        pass
                self.character_panel.refresh_display()
            except:
                self.character.experience_points += xp
                self.log_message(f"✨ {self.character.name} gains {xp} XP")
                self.character_panel.refresh_display()
    
    def update_location(self, hex_id: str, location: str, elevation: str = None):
        """Update character location"""
        if self.character_panel:
            self.character_panel.update_world_data(
                hex_id=hex_id, 
                location=location, 
                elevation=elevation
            )
            self.log_command(f"move to {location}")
            self.log_message(f"🗺️ You travel to {location} (Hex {hex_id})")
            if elevation:
                self.log_message(f"Elevation: {elevation}")
            self.log_message("Time passes: 1 hour")
            
            # Advance turn counter
            if self.game_log_panel:
                self.game_log_panel.advance_turn()
    
    def update_weather(self, weather: str):
        """Update weather conditions"""
        if self.character_panel:
            self.character_panel.update_world_data(weather=weather)
            self.log_system_message(f"🌤️ Weather changed: {weather}")
    
    def log_level_up_message(self, message: str):
        """Log a level up message with special formatting"""
        if self.game_log_panel:
            self.game_log_panel.add_level_up_message(message)
    
    def log_message(self, message: str, message_type: str = "normal"):
        """Add a message to the game log"""
        if hasattr(self, 'game_log_panel') and self.game_log_panel:
            self.game_log_panel.add_message(message, message_type)
    
    def log_command(self, command: str):
        """Log a player command"""
        if hasattr(self, 'game_log_panel') and self.game_log_panel:
            self.game_log_panel.add_command(command)
    
    def log_system_message(self, message: str):
        """Log a system message"""
        if hasattr(self, 'game_log_panel') and self.game_log_panel:
            self.game_log_panel.add_system_message(message)
    
    def log_combat_message(self, message: str):
        """Log a combat message"""
        if hasattr(self, 'game_log_panel') and self.game_log_panel:
            self.game_log_panel.add_combat_message(message)


def run_ui():
    """Run the Fantasy RPG UI"""
    app = FantasyRPGApp()
    app.run()


def test_game_log_panel():
    """Test the game log panel with scrolling and real-time updates"""
    print("Testing Game Log Panel with scrolling...")
    print("Available test keys:")
    print("  H - Heal 10 HP (with log messages)")
    print("  D - Take 5 damage (with combat messages)")
    print("  X - Gain 100 XP (with level up messages)")
    print("  L - Change location (with travel messages)")
    print("  W - Change weather (with system messages)")
    print("  S - Save game log to file")
    print("  C - Clear game log")
    print("  ESC - Quit with confirmation")
    print()
    print("Features:")
    print("  • Scrollable log with mouse wheel or arrow keys")
    print("  • Auto-scroll to bottom for new messages")
    print("  • Different message types with icons")
    print("  • Turn counter and day tracking")
    print("  • Message history (up to 1000 messages)")
    print()
    
    app = FantasyRPGApp()
    app.run()


if __name__ == "__main__":
    test_game_log_panel()