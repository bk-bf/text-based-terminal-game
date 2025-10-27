"""
Fantasy RPG - Basic Action Handler

Minimal action processing for only the features that actually work.
Currently supports: inventory and character sheet.
"""

from typing import Dict, Any, Optional


class ActionResult:
    """Standardized result from any game action"""
    
    def __init__(self, success: bool = True, message: str = "", 
                 time_passed: float = 0.0, **kwargs):
        self.success = success
        self.message = message
        self.time_passed = time_passed
        self.data = kwargs
    
    def get(self, key: str, default=None):
        """Get additional data from the result"""
        return self.data.get(key, default)


class ActionHandler:
    """Basic handler for working game actions including movement"""
    
    def __init__(self, character=None, player_state=None, time_system=None, game_engine=None):
        self.character = character
        self.player_state = player_state
        self.time_system = time_system
        self.game_engine = game_engine  # GameEngine reference for movement
        
        # Action registry - essential commands only
        self.action_registry = {
            # Core Actions
            "look": self.handle_look,
            "enter": self.handle_enter_location,
            "exit": self.handle_exit_location,
            "inventory": self.handle_inventory,
            "character": self.handle_character,
            "save": self.handle_save_log,
            
            # Movement Actions (overworld only)
            "north": self.handle_movement,
            "south": self.handle_movement,
            "east": self.handle_movement,
            "west": self.handle_movement,
            "n": self.handle_movement,
            "s": self.handle_movement,
            "e": self.handle_movement,
            "w": self.handle_movement,
            
            # Debug Commands
            "debug": self.handle_debug,
            "help": self.handle_help,
        }
    
    def process_command(self, command_text: str) -> ActionResult:
        """
        Process a text command and return standardized result.
        
        Args:
            command_text: Raw command from user
            
        Returns:
            ActionResult with success, message, time_passed, and additional data
        """
        if not command_text.strip():
            return ActionResult(False, "Please enter a command.")
        
        parts = command_text.lower().strip().split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Store current command for direction detection
        self._current_command = command
        
        # Handle registered actions
        if command in self.action_registry:
            try:
                return self.action_registry[command](*args)
            except Exception as e:
                return ActionResult(False, f"Error executing {command}: {str(e)}")
        
        # Unknown command
        return ActionResult(False, f"Unknown command: {command}. Type 'help' for available commands.")

    
    def handle_inventory(self, *args) -> ActionResult:
        """Handle inventory display"""
        return ActionResult(
            success=True,
            message="Opening inventory...",
            time_passed=0.0,
            action_type="ui_modal",
            modal_type="inventory"
        )
    
    def handle_character(self, *args) -> ActionResult:
        """Handle character sheet display"""
        return ActionResult(
            success=True,
            message="Reviewing character details...",
            time_passed=0.0,
            action_type="ui_modal",
            modal_type="character"
        )
    
    def handle_help(self, *args) -> ActionResult:
        """Handle help display"""
        help_text = """Available commands:
        
Core Actions:
  look - Examine your surroundings
  enter - Enter a location in this hex
  exit - Exit current location to overworld
  
Movement (overworld only):
  north, south, east, west (or n, s, e, w) - Move in that direction
  
Character:
  inventory - View your inventory
  character - View character sheet
  
System:
  save - Save game log to text file
  debug - Show debug information
  help - Show this help
  
Type any command to try it."""
        
        return ActionResult(
            success=True,
            message=help_text,
            time_passed=0.0,
            action_type="help"
        )
    
    def handle_movement(self, *args) -> ActionResult:
        """Handle movement commands through GameEngine"""
        if not self.game_engine:
            return ActionResult(False, "Movement system not available.")
        
        # Determine direction from command and args
        parts = [arg for arg in args if arg]  # Filter out empty args
        command = getattr(self, '_current_command', '')  # Set by process_command
        
        # Map commands to directions
        direction_map = {
            'north': 'north', 'n': 'north',
            'south': 'south', 's': 'south', 
            'east': 'east', 'e': 'east',
            'west': 'west', 'w': 'west',
            'northeast': 'northeast', 'ne': 'northeast',
            'northwest': 'northwest', 'nw': 'northwest',
            'southeast': 'southeast', 'se': 'southeast',
            'southwest': 'southwest', 'sw': 'southwest'
        }
        
        direction = None
        
        # Check if command itself is a direction
        if command in direction_map:
            direction = direction_map[command]
        # Check if first argument is a direction (for "go north")
        elif parts and parts[0] in direction_map:
            direction = direction_map[parts[0]]
        else:
            return ActionResult(False, "Please specify a direction (north, south, east, west, etc.)")
        
        # Route movement through GameEngine
        try:
            success, message = self.game_engine.move_player(direction)
            
            if success:
                return ActionResult(
                    success=True,
                    message=message,
                    time_passed=2.0,  # Movement takes time
                    action_type="movement",
                    movement_type="overworld",
                    direction=direction
                )
            else:
                return ActionResult(False, message)
                
        except Exception as e:
            return ActionResult(False, f"Movement failed: {str(e)}")
    
    def handle_look(self, *args) -> ActionResult:
        """Handle look command through GameEngine"""
        if not self.game_engine:
            return ActionResult(False, "World system not available.")
        
        try:
            gs = self.game_engine.game_state
            
            # Check if player is inside a location
            if gs.world_position.current_location_id:
                # Inside a location - show location description
                # TODO: Rethink the functionality of the "look" command for locations
                # For now, just show basic location info as placeholder
                location_data = gs.world_position.current_location_data
                if location_data:
                    location_name = location_data.get("name", "Unknown Location")
                    location_desc = location_data.get("description", "An unremarkable area.")
                    description = f"**{location_name}**\n\n{location_desc}"
                else:
                    description = "You are inside a location, but cannot see much."
            else:
                # In overworld - show hex description
                description = self.game_engine.get_hex_description()
            
            return ActionResult(
                success=True,
                message=description,
                time_passed=0.0,  # Looking is instant
                action_type="observation"
            )
        except Exception as e:
            return ActionResult(False, f"Cannot look around: {str(e)}")
    
    def handle_enter_location(self, *args) -> ActionResult:
        """Handle entering a location within the current hex"""
        if not self.game_engine:
            return ActionResult(False, "Location system not available.")
        
        # Enter first available location (no arguments needed)
        try:
            success, message = self.game_engine.enter_location()
            
            if success:
                return ActionResult(
                    success=True,
                    message=message,
                    time_passed=0.25,  # Entering takes a little time
                    action_type="location_entry"
                )
            else:
                return ActionResult(False, message)
                
        except Exception as e:
            return ActionResult(False, f"Failed to enter location: {str(e)}")
    
    def handle_exit_location(self, *args) -> ActionResult:
        """Handle exiting current location back to overworld"""
        if not self.game_engine:
            return ActionResult(False, "Location system not available.")
        
        try:
            success, message = self.game_engine.exit_location()
            
            if success:
                return ActionResult(
                    success=True,
                    message=message,
                    time_passed=0.25,  # Exiting takes a little time
                    action_type="location_exit"
                )
            else:
                return ActionResult(False, message)
                
        except Exception as e:
            return ActionResult(False, f"Failed to exit location: {str(e)}")
    
    def handle_save_log(self, *args) -> ActionResult:
        """Handle saving game log to text file"""
        # TODO: Implement save log functionality
        return ActionResult(
            success=True,
            message="Save log functionality not yet implemented.",
            time_passed=0.0,
            action_type="system"
        )
    
    def handle_debug(self, *args) -> ActionResult:
        """Handle debug commands"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
        # Show debug information
        gs = self.game_state if hasattr(self, 'game_state') else None
        if hasattr(self.game_engine, 'game_state'):
            gs = self.game_engine.game_state
        
        debug_info = []
        debug_info.append("=== DEBUG INFO ===")
        
        if gs:
            debug_info.append(f"Current hex: {gs.world_position.hex_id}")
            debug_info.append(f"Coordinates: {gs.world_position.coords}")
            debug_info.append(f"In location: {gs.world_position.current_location_id or 'No'}")
            debug_info.append(f"Time: {gs.game_time.get_time_string()}, {gs.game_time.get_date_string()}")
            debug_info.append(f"Weather: {gs.current_weather.temperature:.0f}°F")
            debug_info.append(f"Character HP: {gs.character.hp}/{gs.character.max_hp}")
        else:
            debug_info.append("No game state available")
        
        return ActionResult(
            success=True,
            message="\n".join(debug_info),
            time_passed=0.0,
            action_type="debug"
        )