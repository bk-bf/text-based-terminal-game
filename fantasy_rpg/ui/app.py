"""
Fantasy RPG - Main Application

Main app class with input handling and game logic coordination.
"""

try:
    from textual.app import App
except ImportError:
    import sys
    print("Error: Textual library not found!")
    exit(1)

from .screens import MainGameScreen, InventoryScreen, QuitConfirmationScreen


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
    """
    
    def __init__(self):
        super().__init__()
        self.character = None
        self.character_panel = None
        self.game_log_panel = None
        self.poi_panel = None
    
    def on_mount(self) -> None:
        """Initialize the app"""
        main_screen = MainGameScreen()
        self.character_panel = main_screen.character_panel
        self.game_log_panel = main_screen.game_log_panel
        self.poi_panel = main_screen.poi_panel
        self.character = self.character_panel.character
        self.push_screen(main_screen)
    
    def process_command(self, command: str):
        """Process a typed command"""
        parts = command.split()
        cmd = parts[0] if parts else ""
        
        if cmd == "help":
            self.show_help()
        elif cmd in ["n", "north"]:
            self.travel_direction("north")
        elif cmd in ["s", "south"]:
            self.travel_direction("south")
        elif cmd in ["e", "east"]:
            self.travel_direction("east")
        elif cmd in ["w", "west"]:
            self.travel_direction("west")
        elif cmd in ["heal", "h"]:
            self.log_command("heal")
            self.heal_character(10)
        elif cmd in ["damage", "hurt"]:
            self.log_command("take damage")
            self.damage_character(5)
        elif cmd in ["xp", "experience"]:
            self.log_command("gain experience")
            self.add_experience(100)
        elif cmd in ["inventory", "i"]:
            self.log_command("inventory")
            self.push_screen(InventoryScreen(self.character))
        elif cmd in ["map", "m"]:
            self.show_map()
        elif cmd in ["rest", "r"]:
            self.rest_character()
        elif cmd in ["look", "l", "examine"]:
            self.look_around()
        elif cmd in ["save"]:
            self.save_log()
        elif cmd in ["clear"]:
            self.clear_log()
        elif cmd in ["quit", "exit"]:
            self.push_screen(QuitConfirmationScreen())
        else:
            self.log_message(f"Unknown command: {command}")
            self.log_message("Type 'help' for available commands.")
            self.log_message("")
    
    def show_help(self):
        """Show available commands"""
        self.log_command("help")
        self.log_message("Available commands:")
        self.log_message("")
        self.log_message("Movement:")
        self.log_message("  n, north - Move north")
        self.log_message("  s, south - Move south")
        self.log_message("  e, east - Move east")
        self.log_message("  w, west - Move west")
        self.log_message("")
        self.log_message("Actions:")
        self.log_message("  look, l - Examine current location")
        self.log_message("  rest, r - Rest and recover health")
        self.log_message("  inventory, i - View inventory and equipment")
        self.log_message("  map, m - View map and nearby locations")
        self.log_message("")
        self.log_message("System:")
        self.log_message("  heal - Heal 10 HP (debug)")
        self.log_message("  xp - Gain 100 XP (debug)")
        self.log_message("  save - Save game log")
        self.log_message("  clear - Clear game log")
        self.log_message("  quit, exit - Quit game")
        self.log_message("")
    
    # Character actions
    def heal_character(self, amount: int):
        """Heal character by amount"""
        if self.character:
            old_hp = self.character.hp
            self.character.hp = min(self.character.hp + amount, self.character.max_hp)
            healed = self.character.hp - old_hp
            if healed > 0:
                self.log_message(f"[+] {self.character.name} healed {healed} HP ({old_hp} -> {self.character.hp})")
                if self.character.hp == self.character.max_hp:
                    self.log_message("You are now at full health!")
            else:
                self.log_message("Already at full health.")
            self.log_message("")  # Add separator
            self.character_panel.refresh_display()
    
    def damage_character(self, amount: int):
        """Damage character by amount"""
        if self.character:
            old_hp = self.character.hp
            self.character.hp = max(0, self.character.hp - amount)
            damage_taken = old_hp - self.character.hp
            if damage_taken > 0:
                self.log_combat_message(f"{self.character.name} takes {damage_taken} damage ({old_hp} -> {self.character.hp})")
                if self.character.hp == 0:
                    self.log_combat_message("[X] You have fallen unconscious!")
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
    
    def rest_character(self):
        """Rest and recover health"""
        self.log_command("rest")
        self.log_message("You rest for a while...")
        self.heal_character(5)
        self.log_message("You feel refreshed.")
    
    # World actions
    def travel_direction(self, direction: str):
        """Travel in a specific direction"""
        if self.poi_panel and self.poi_panel.can_travel_to(direction):
            destination_hex = self.poi_panel.get_destination_hex(direction)
            destination_info = self.poi_panel.get_location_by_hex(destination_hex)
            
            self.update_location(
                destination_hex, 
                destination_info["name"],
                "320 ft"  # Default elevation
            )
        else:
            self.log_message(f"Cannot travel {direction} from here.")
            self.log_message("")
    
    def update_location(self, hex_id: str, location: str, elevation: str = None):
        """Update character location"""
        if self.character_panel:
            self.character_panel.update_world_data(
                hex_id=hex_id, 
                location=location, 
                elevation=elevation
            )
        
        # Update POI panel with new location
        if self.poi_panel:
            self.poi_panel.update_location(hex_id, location)
        
        self.log_command(f"move to {location}")
        self.log_message(f"[>] You travel to {location} (Hex {hex_id})")
        if elevation:
            self.log_message(f"Elevation: {elevation}")
        self.log_message("Time passes: 1 hour")
        
        # Show nearby locations
        if self.poi_panel:
            nearby = self.poi_panel.get_nearby_locations()
            if nearby:
                self.log_message("You can see:")
                for loc in nearby:
                    symbol = self.poi_panel._get_location_symbol(loc["type"])
                    self.log_message(f"  {symbol} {loc['name']} to the {loc['direction']}")
        
        self.log_message("")  # Add separator
        
        # Advance turn counter
        if self.game_log_panel:
            self.game_log_panel.advance_turn()
    
    def look_around(self):
        """Look around current location"""
        self.log_command("look")
        if self.poi_panel:
            current_info = self.poi_panel.get_current_location_info()
            self.log_message(f"You look around {current_info['name']}:")
            self.log_message(current_info['description'])
            self.log_message("")
    
    def show_map(self):
        """Show map and nearby locations"""
        self.log_command("map")
        self.log_message("Consulting map...")
        if self.poi_panel:
            current_info = self.poi_panel.get_current_location_info()
            nearby = self.poi_panel.get_nearby_locations()
            self.log_message(f"Current: {current_info['name']} ({self.poi_panel.current_hex})")
            self.log_message("Nearby locations:")
            for loc in nearby:
                symbol = self.poi_panel._get_location_symbol(loc["type"])
                self.log_message(f"  {symbol} {loc['name']} ({loc['direction']})")
        self.log_message("")
    
    def update_weather(self, weather: str):
        """Update weather conditions"""
        if self.character_panel:
            self.character_panel.update_world_data(weather=weather)
            self.log_system_message(f"[~] Weather changed: {weather}")
            self.log_message("")  # Add separator
    
    # System actions
    def save_log(self):
        """Save game log"""
        self.log_command("save log")
        if self.game_log_panel:
            self.game_log_panel.save_log_to_file()
            self.log_message("")
    
    def clear_log(self):
        """Clear game log"""
        self.log_command("clear log")
        if self.game_log_panel:
            self.game_log_panel.clear_log()
            self.log_system_message("Game log cleared")
            self.log_message("")
    
    # Logging methods
    def log_message(self, message: str, message_type: str = "normal"):
        """Add a message to the game log"""
        if self.game_log_panel:
            self.game_log_panel.add_message(message, message_type)
    
    def log_command(self, command: str):
        """Log a player command"""
        if self.game_log_panel:
            self.game_log_panel.add_command(command)
    
    def log_system_message(self, message: str):
        """Log a system message"""
        if self.game_log_panel:
            self.game_log_panel.add_system_message(message)
    
    def log_combat_message(self, message: str):
        """Log a combat message"""
        if self.game_log_panel:
            self.game_log_panel.add_combat_message(message)
    
    def log_level_up_message(self, message: str):
        """Log a level up message with special formatting"""
        if self.game_log_panel:
            self.game_log_panel.add_level_up_message(message)


def run_ui():
    """Run the Fantasy RPG UI"""
    app = FantasyRPGApp()
    app.run()


def test_inventory_screen():
    """Test the inventory screen modal with equipment display"""
    print("Testing Refactored UI with Inventory Screen...")
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
    print("Refactored Architecture:")
    print("  • ui/panels.py - Visual display components")
    print("  • ui/screens.py - Modal screens and main screen")
    print("  • ui/app.py - Main application and input handling")
    print("  • Clean separation of concerns")
    print("  • Modular, maintainable code structure")
    print()
    
    app = FantasyRPGApp()
    app.run()


if __name__ == "__main__":
    test_inventory_screen()