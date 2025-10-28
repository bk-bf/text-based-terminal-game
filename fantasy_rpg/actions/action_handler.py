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
            "i": self.handle_inventory,  # Shortcut for inventory
            "character": self.handle_character,
            "c": self.handle_character,  # Shortcut for character
            "save": self.handle_save_log,
            
            # Object Interaction Actions (location only)
            "examine": self.handle_examine,
            "search": self.handle_search,
            "take": self.handle_take,
            "use": self.handle_use,
            
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
            "dump_location": self.handle_dump_location,
            "dump_hex": self.handle_dump_hex,
            "dump_world": self.handle_dump_world,
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
  
Object Interaction (location only):
  examine <object> - Examine an object closely
  search <object> - Search an object for items
  take <item> - Take an item and add to inventory
  use <object> - Use an object (context-specific)
  
Movement (overworld only):
  north, south, east, west (or n, s, e, w) - Move in that direction
  
Character:
  inventory, i - View your inventory
  character, c - View character sheet
  
System:
  save - Save game log to text file
  debug - Show debug information
  dump_location - Dump current location data to JSON file
  dump_hex - Dump current hex data to JSON file
  dump_world - Dump entire world data to JSON file
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
        
        # Check if player is inside a location
        gs = self.game_engine.game_state
        if gs.world_position.current_location_id:
            # Player is inside a location - try location-to-location movement
            try:
                success, message = self.game_engine.move_between_locations(direction)
                
                if success:
                    return ActionResult(
                        success=True,
                        message=message,
                        time_passed=0.5,  # Moving between locations takes some time
                        action_type="location_movement"
                    )
                else:
                    return ActionResult(False, message)
                    
            except Exception as e:
                return ActionResult(False, f"Movement failed: {str(e)}")
        
        # Route movement through GameEngine (overworld movement)
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
                # Inside a location - show location description and contents
                location_data = gs.world_position.current_location_data
                if location_data:
                    location_name = location_data.get("name", "Unknown Location")
                    location_desc = location_data.get("description", "An unremarkable area.")
                    description = f"**{location_name}**\n\n{location_desc}"
                    
                    # Add location contents
                    contents = self.game_engine.get_location_contents()
                    if contents:
                        description += f"\n\n{contents}"
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
            
            # Add location content debug info
            if gs.world_position.current_location_id:
                location_data = gs.world_position.current_location_data
                if location_data:
                    areas = location_data.get("areas", {})
                    starting_area_id = location_data.get("starting_area", "entrance")
                    debug_info.append(f"Location: {location_data.get('name', 'Unknown')}")
                    debug_info.append(f"Starting area: {starting_area_id}")
                    
                    if starting_area_id in areas:
                        area_data = areas[starting_area_id]
                        objects = area_data.get("objects", [])
                        items = area_data.get("items", [])
                        
                        debug_info.append(f"Objects in area: {len(objects)}")
                        for i, obj in enumerate(objects[:5]):  # Show first 5
                            obj_name = obj.get('name', 'Unknown')
                            obj_id = obj.get('id', 'unknown')
                            debug_info.append(f"  {i+1}. {obj_name} (id: {obj_id})")
                        
                        debug_info.append(f"Items in area: {len(items)}")
                        for i, item in enumerate(items[:5]):  # Show first 5
                            item_name = item.get('name', 'Unknown')
                            item_id = item.get('id', 'unknown')
                            debug_info.append(f"  {i+1}. {item_name} (id: {item_id})")
        else:
            debug_info.append("No game state available")
        
        return ActionResult(
            success=True,
            message="\n".join(debug_info),
            time_passed=0.0,
            action_type="debug"
        )
    
    def handle_examine(self, *args) -> ActionResult:
        """Handle examining objects in current location"""
        if not self.game_engine:
            return ActionResult(False, "Object interaction system not available.")
        
        if not args:
            return ActionResult(False, "Examine what? Specify an object name.")
        
        object_name = " ".join(args).lower()
        
        try:
            success, message = self.game_engine.examine_object(object_name)
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.1 if success else 0.0,  # Examining takes a little time
                action_type="object_interaction"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to examine object: {str(e)}")
    
    def handle_search(self, *args) -> ActionResult:
        """Handle searching objects in current location"""
        if not self.game_engine:
            return ActionResult(False, "Object interaction system not available.")
        
        if not args:
            return ActionResult(False, "Search what? Specify an object name.")
        
        object_name = " ".join(args).lower()
        
        try:
            success, message = self.game_engine.search_object(object_name)
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25 if success else 0.0,  # Searching takes time
                action_type="object_interaction"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to search object: {str(e)}")
    
    def handle_take(self, *args) -> ActionResult:
        """Handle taking items from objects"""
        if not self.game_engine:
            return ActionResult(False, "Object interaction system not available.")
        
        if not args:
            return ActionResult(False, "Take what? Specify an item name.")
        
        item_name = " ".join(args).lower()
        
        try:
            success, message = self.game_engine.take_item(item_name)
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.1 if success else 0.0,  # Taking items is quick
                action_type="object_interaction"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to take item: {str(e)}")
    
    def handle_use(self, *args) -> ActionResult:
        """Handle using objects in current location"""
        if not self.game_engine:
            return ActionResult(False, "Object interaction system not available.")
        
        if not args:
            return ActionResult(False, "Use what? Specify an object name.")
        
        object_name = " ".join(args).lower()
        
        try:
            success, message = self.game_engine.use_object(object_name)
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25 if success else 0.0,  # Using objects takes time
                action_type="object_interaction"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to use object: {str(e)}")
    
    def handle_dump_world(self, *args) -> ActionResult:
        """Handle dumping world data to JSON file"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
        try:
            # Dump world data (convert tuple keys to strings for JSON compatibility)
            import json
            
            # Convert climate_zones (has tuple keys) to string keys
            climate_zones_str = {}
            for key, value in self.game_engine.world_coordinator.climate_zones.items():
                if isinstance(key, tuple):
                    climate_zones_str[f"{key[0]:02d}{key[1]:02d}"] = value
                else:
                    climate_zones_str[str(key)] = value
            
            world_data = {
                "world_size": self.game_engine.world_coordinator.world_size,
                "seed": self.game_engine.world_coordinator.seed,
                "hex_data": self.game_engine.world_coordinator.hex_data,
                "climate_zones": climate_zones_str,
                "loaded_locations": self.game_engine.world_coordinator.loaded_locations
            }
            
            filename = "debug_world_data.json"
            with open(filename, 'w') as f:
                json.dump(world_data, f, indent=2, default=str)
            
            return ActionResult(
                success=True,
                message=f"World data dumped to {filename}",
                time_passed=0.0,
                action_type="debug"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to dump world data: {str(e)}")
    
    def handle_dump_location(self, *args) -> ActionResult:
        """Handle dumping current location data to JSON file"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
        try:
            success, message = self.game_engine.dump_location_data()
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.0,
                action_type="debug"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to dump location data: {str(e)}")
    
    def handle_dump_hex(self, *args) -> ActionResult:
        """Handle dumping current hex data to JSON file"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
        try:
            success, message = self.game_engine.dump_hex_data()
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.0,
                action_type="debug"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to dump hex data: {str(e)}")