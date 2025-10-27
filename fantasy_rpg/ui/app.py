"""
Fantasy RPG - Main Application

Main app class with visual presentation and UI coordination.
All input processing is handled by the InputController.
"""

from typing import Dict, Any

try:
    from textual.app import App
except ImportError:
    import sys
    print("Error: Textual library not found!")
    exit(1)

try:
    from .screens import MainGameScreen, InventoryScreen, CharacterScreen, QuitConfirmationScreen
    from ..actions.input_controller import InputController
    from ..actions.action_logger import get_action_logger
except ImportError:
    from screens import MainGameScreen, InventoryScreen, CharacterScreen, QuitConfirmationScreen
    from fantasy_rpg.actions.input_controller import InputController
    from fantasy_rpg.actions.action_logger import get_action_logger


class FantasyRPGApp(App):
    """Main Textual application with input handling"""
    
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
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }
    
    GameLogPanel {
        width: 50%;
        height: 1fr;
        border: solid $primary;
        padding: 1;
        scrollbar-size: 1 0;
        scrollbar-color: transparent;
        scrollbar-color-hover: $background 50%;
        scrollbar-color-active: $background 70%;
        scrollbar-background: transparent;
        scrollbar-background-hover: transparent;
        scrollbar-background-active: transparent;
    }
    
    POIPanel {
        width: 25%;
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }
    
    #command-input {
        dock: bottom;
        height: 1;
        margin: 0 1;
        padding: 0;
        border: none;
        background: $surface;
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
    
    /* Inventory screen styles */
    InventoryScreen {
        align: center middle;
    }
    
    #inventory-dialog {
        background: $surface;
        border: solid $primary;
        width: 80;
        height: 25;
        padding: 1;
    }
    
    #inventory-title {
        text-align: center;
        margin-bottom: 1;
    }
    
    #equipment-column {
        width: 50%;
        padding: 0 1;
    }
    
    #inventory-column {
        width: 50%;
        padding: 0 1;
    }
    
    #inventory-instruction {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    
    /* Character screen styles */
    CharacterScreen {
        align: center middle;
    }
    
    #character-dialog {
        background: $surface;
        border: solid $primary;
        width: 90;
        height: 35;
        padding: 1;
    }
    
    #character-title {
        text-align: center;
        margin-bottom: 1;
    }
    
    #character-left-column {
        width: 50%;
        padding: 0 1;
    }
    
    #character-right-column {
        width: 50%;
        padding: 0 1;
    }
    
    #character-features {
        padding: 0 1;
        margin-top: 1;
    }
    
    #character-instruction {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.character = None
        self.character_panel = None
        self.game_log_panel = None
        self.poi_panel = None
        self.player_state = None
        self.time_system = None
        self.input_controller = None
        self.world_coordinator = None
    
    def on_mount(self) -> None:
        """Initialize the app"""
        main_screen = MainGameScreen()
        self.character_panel = main_screen.character_panel
        self.game_log_panel = main_screen.game_log_panel
        self.poi_panel = main_screen.poi_panel
        self.character = self.character_panel.character
        
        self.push_screen(main_screen)
        
        # Initialize survival system first, then action handler
        self.call_after_refresh(self._initialize_survival_system)
    
    def process_command(self, command: str):
        """Process a typed command through the input controller"""
        if not self.input_controller:
            self.log_message("Input system not initialized.")
            return
        
        # Process input through the input controller
        response = self.input_controller.process_input(command)
        
        # Handle the response based on type
        self._handle_input_response(response)
    
    def _handle_input_response(self, response: Dict[str, Any]):
        """Handle response from input controller"""
        response_type = response.get('type', 'unknown')
        
        if response_type == 'error':
            self.log_message(response.get('message', 'Unknown error'))
            
        elif response_type == 'show_modal':
            modal_type = response.get('modal_type')
            if modal_type == 'inventory':
                self.push_screen(InventoryScreen(self.character))
            elif modal_type == 'character':
                self.push_screen(CharacterScreen(self.character))
                
        elif response_type == 'show_help':
            self.show_help()
            
        elif response_type == 'location_update':
            hex_id = response.get('hex_id')
            location_name = response.get('location_name')
            elevation = response.get('elevation')
            if hex_id and location_name:
                self.update_location(hex_id, location_name, elevation)
                
        elif response_type == 'heal_character':
            amount = response.get('amount', 0)
            source = response.get('source', 'unknown')
            if amount > 0:
                self.heal_character(amount, source)
                
        elif response_type == 'debug_heal':
            command = response.get('command', 'heal')
            self.log_command(command)
            self.heal_character(10)
            
        elif response_type == 'debug_damage':
            command = response.get('command', 'damage')
            self.log_command(command)
            self.damage_character(5)
            
        elif response_type == 'debug_xp':
            command = response.get('command', 'xp')
            self.log_command(command)
            self.add_experience(100)
            
        elif response_type == 'save_log':
            command = response.get('command', 'save')
            filename = response.get('filename')
            self.log_command(command)
            self.save_log(filename)
            
        elif response_type == 'clear_log':
            command = response.get('command', 'clear')
            self.log_command(command)
            self.clear_log()
            
        elif response_type == 'quit_game':
            self.push_screen(QuitConfirmationScreen())
        
        # Always refresh display after processing input
        if self.character_panel:
            self.character_panel.refresh_display()
    
    def show_help(self):
        """Show available commands"""
        if self.input_controller:
            help_text = self.input_controller.get_help_text()
            for line in help_text.split('\n'):
                self.log_message(line)
        else:
            self.log_message("Help system not available.")
    
    # Character actions
    def heal_character(self, amount: int, source: str = "unknown"):
        """Heal character by amount"""
        if self.character:
            old_hp = self.character.hp
            self.character.hp = min(self.character.hp + amount, self.character.max_hp)
            healed = self.character.hp - old_hp
            if healed > 0:
                # Use action logger for consistent healing logging
                from ..actions.action_logger import get_action_logger
                action_logger = get_action_logger()
                action_logger.log_healing_received(
                    heal_amount=healed,
                    source=source,
                    old_hp=old_hp,
                    new_hp=self.character.hp
                )
                
                if self.character.hp == self.character.max_hp:
                    self.log_message("💚 You are now at full health!")
            else:
                self.log_message("Already at full health.")
            self.log_message("")  # Add separator
            self.character_panel.refresh_display()
    
    def damage_character(self, amount: int, source: str = "unknown"):
        """Damage character by amount"""
        if self.character:
            old_hp = self.character.hp
            self.character.hp = max(0, self.character.hp - amount)
            damage_taken = old_hp - self.character.hp
            if damage_taken > 0:
                # Use action logger for consistent damage logging
                from ..actions.action_logger import get_action_logger
                action_logger = get_action_logger()
                action_logger.log_damage_taken(
                    damage_amount=damage_taken,
                    damage_type="generic",
                    source=source,
                    old_hp=old_hp,
                    new_hp=self.character.hp
                )
                
                if self.character.hp == 0:
                    self.log_combat_message("💀 You have fallen unconscious!")
                elif self.character.hp <= self.character.max_hp * 0.25:
                    self.log_message("[!] You are badly wounded!")
            self.log_message("")  # Add separator
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
                    self.log_message(f"[*] {self.character.name} gains {xp} XP")
                    try:
                        xp_needed = self.character.get_xp_to_next_level()
                        self.log_message(f"({xp_needed} XP needed for level {self.character.level + 1})")
                    except:
                        pass
                self.log_message("")  # Add separator
                self.character_panel.refresh_display()
            except:
                self.character.experience_points += xp
                self.log_message(f"[*] {self.character.name} gains {xp} XP")
                self.log_message("")  # Add separator
                self.character_panel.refresh_display()
    
    # rest_character is now handled by ActionHandler
    
    # travel_direction is now handled by ActionHandler
    
    def update_location(self, hex_id: str, location: str, elevation: str = None):
        """Update character location (UI state only - logging handled by ActionHandler)"""
        if self.character_panel:
            self.character_panel.update_world_data(
                hex_id=hex_id, 
                location=location, 
                elevation=elevation
            )
        
        # Update POI panel with new location
        if self.poi_panel:
            self.poi_panel.update_location(hex_id, location)
    
    # look_around is now handled by ActionHandler
    
    # show_map is now handled by ActionHandler
    
    def update_weather(self, weather: str):
        """Update weather conditions (UI only - logging handled by ActionLogger)"""
        if self.character_panel:
            self.character_panel.update_world_data(weather=weather)
    
    # System actions
    def save_log(self, filename: str = None):
        """Save game log"""
        if self.game_log_panel:
            if filename:
                self.game_log_panel.save_log_to_file(filename)
            else:
                self.game_log_panel.save_log_to_file()
            self.log_message("")
    
    def clear_log(self):
        """Clear game log"""
        self.log_command("clear log")
        if self.game_log_panel:
            self.game_log_panel.clear_log()
            self.log_system_message("Game log cleared")
            self.log_message("")
    
    # Simple logging methods (for debug commands only)
    def log_message(self, message: str, message_type: str = "normal"):
        """Add a message to the game log (for debug commands only)"""
        if self.game_log_panel:
            self.game_log_panel.add_message(message, message_type)
    
    def log_command(self, command: str):
        """Log a player command (for debug commands only)"""
        if self.game_log_panel:
            self.game_log_panel.add_command(command)
    
    def log_system_message(self, message: str):
        """Log a system message (for system initialization only)"""
        if self.game_log_panel:
            self.game_log_panel.add_system_message(message)
    
    def log_combat_message(self, message: str):
        """Log a combat message (for debug commands only)"""
        if self.game_log_panel:
            self.game_log_panel.add_combat_message(message)
    
    def log_level_up_message(self, message: str):
        """Log a level up message (for debug commands only)"""
        if self.game_log_panel:
            self.game_log_panel.add_level_up_message(message)
    
    def _initialize_survival_system(self):
        """Initialize survival system after UI is mounted"""
        try:
            try:
                from ..game.player_state import PlayerState
                from ..game.time_system import TimeSystem
                from ..world.weather_core import generate_weather_state
            except ImportError:
                from fantasy_rpg.game.player_state import PlayerState
                from fantasy_rpg.game.time_system import TimeSystem
                from fantasy_rpg.world.weather_core import generate_weather_state
            
            # Create player state and time system
            self.player_state = PlayerState()
            self.player_state.character = self.character
            
            # Generate initial weather
            initial_weather = generate_weather_state(65.0, "spring", "temperate")
            self.player_state.update_weather(initial_weather)
            
            # Create time system
            self.time_system = TimeSystem(self.player_state)
            
            # Add callbacks for UI updates
            self.time_system.add_time_callback(self._on_time_advance)
            self.time_system.add_weather_callback(self._on_weather_change)
            
            # Link player state to character and game log for UI display
            self.character.player_state = self.player_state
            self.game_log_panel.player_state = self.player_state
            
            # Update initial weather display
            weather_desc = f"{initial_weather.get_description().split(chr(10))[0]}"  # First line only
            self.character_panel.update_world_data(weather=weather_desc)
            
                # Update title bar with initial time
            current_screen = self.screen
            if hasattr(current_screen, 'update_title_bar'):
                current_screen.update_title_bar(self.player_state)
            
            # Initialize action logger with player state for weather tracking
            action_logger = get_action_logger()
            action_logger.set_game_log(self.game_log_panel)
            action_logger.last_weather = initial_weather
            
            # Initialize world coordinator (placeholder for now)
            try:
                from ..world.world_coordinator import WorldCoordinator
                self.world_coordinator = WorldCoordinator()
            except ImportError:
                self.world_coordinator = None
            
            # Initialize input controller with all systems
            self.input_controller = InputController(
                character=self.character,
                player_state=self.player_state,
                time_system=self.time_system
            )
            
            # Initialize the input controller
            self.input_controller.initialize(self.world_coordinator)
            
            # Set up UI callbacks for the input controller
            self._setup_input_controller_callbacks()
            
            self.log_system_message("Welcome to your adventure!\n")
            
        except ImportError as e:
            self.log_system_message(f"Could not initialize survival system: {e}")
        except Exception as e:
            self.log_system_message(f"Error initializing survival system: {e}")
    
    def _setup_input_controller_callbacks(self):
        """Set up UI callbacks for the input controller"""
        if not self.input_controller:
            return
        
        # Set up callbacks so input controller can trigger UI actions
        self.input_controller.set_ui_callback('show_inventory', 
            lambda: self.push_screen(InventoryScreen(self.character)))
        self.input_controller.set_ui_callback('show_character', 
            lambda: self.push_screen(CharacterScreen(self.character)))
        self.input_controller.set_ui_callback('show_help', self.show_help)
        self.input_controller.set_ui_callback('update_location', self.update_location)
        self.input_controller.set_ui_callback('heal_character', self.heal_character)
        self.input_controller.set_ui_callback('damage_character', self.damage_character)
        self.input_controller.set_ui_callback('add_experience', self.add_experience)
        self.input_controller.set_ui_callback('save_log', self.save_log)
        self.input_controller.set_ui_callback('clear_log', self.clear_log)
        self.input_controller.set_ui_callback('quit_game', 
            lambda: self.push_screen(QuitConfirmationScreen()))
        self.input_controller.set_ui_callback('log_message', self.log_message)
        self.input_controller.set_ui_callback('log_command', self.log_command)
        self.input_controller.set_ui_callback('refresh_display', 
            lambda: self.character_panel.refresh_display() if self.character_panel else None)
    
    # Survival system callbacks
    def _on_time_advance(self, old_time: str, new_time: str, hours_passed: float):
        """Callback for when time advances"""
        if hours_passed > 0:
            # Update character panel
            if self.character_panel:
                self.character_panel.refresh_display()
            
            # Update title bar
            current_screen = self.screen
            if hasattr(current_screen, 'update_title_bar'):
                current_screen.update_title_bar(self.player_state)
            
            # Check for weather changes (handled by ActionLogger)
            action_logger = get_action_logger()
            action_logger._log_weather_changes(self.player_state)
    
    def _on_weather_change(self, old_weather, new_weather):
        """Callback for when weather changes"""
        if new_weather:
            weather_desc = new_weather.get_description().split('\n')[0]  # First line only
            self.update_weather(weather_desc)
            # Weather change logging is now handled by ActionLogger
    
    # _format_duration is now handled by the time system
    
    # Survival-related commands are now handled by ActionHandler


def run_ui():
    """Run the Fantasy RPG UI"""
    app = FantasyRPGApp()
    app.run()


def test_character_screen():
    """Test the character screen modal with full stats display"""
    print("Testing Character Screen Modal...")
    print("Movement controls:")
    print("  n - Move North")
    print("  e - Move East") 
    print("  w - Move West")
    print("  s - Move South")
    print()
    print("Log scrolling:")
    print("  Arrow Keys - Scroll game log up/down")
    print()
    print("Main commands:")
    print("  c, character - Open character sheet modal")
    print("  i, inventory - Open inventory modal")
    print("  m - View map and nearby locations")
    print("  r - Rest and heal 5 HP")
    print("  l - Look around current location")
    print()
    print("Debug controls:")
    print("  heal - Heal 10 HP")
    print("  xp - Gain 100 XP")
    print("  clear - Clear game log")
    print("  help - Show all commands")
    print("  quit, exit, esc - Quit with confirmation")
    print()
    print("Modal Features:")
    print("  • Full character sheet with all stats")
    print("  • Ability scores with modifiers")
    print("  • Combat stats and saving throws")
    print("  • Experience progression tracking")
    print("  • Skills, feats, and special features")
    print("  • Equipment and encumbrance summary")
    print("  • Clean two-column layout")
    print()
    
    app = FantasyRPGApp()
    app.run()


if __name__ == "__main__":
    test_character_screen()