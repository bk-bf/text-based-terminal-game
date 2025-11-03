"""
Fantasy RPG - Debug Handler

Handles all debug and system commands:
- Debug info display
- World/location/hex data dumping
- Save/load game
- Help display
- Game log saving
"""

from .base_handler import BaseActionHandler, ActionResult


class DebugHandler(BaseActionHandler):
    """Handler for debug and system commands"""
    
    def handle_help(self, *args) -> ActionResult:
        """Handle help display with shortkey support"""
        # Get shortkey help from manager
        try:
            from .shortkey_manager import get_shortkey_manager
            shortkey_manager = get_shortkey_manager()
            shortkey_help = shortkey_manager.get_action_help()
        except:
            shortkey_help = ""
        
        help_text = f"""{shortkey_help}

=== FULL COMMAND LIST ===

Core Actions:
  look / l - Examine your surroundings
  enter - Enter a location in this hex (no arguments needed)
  exit - Exit current location to overworld
  
Object Interaction (location only):
  examine/x <object> - Examine an object closely (shows available actions)
  search/a <object> - Search an object for items
  use/u <object> - Use an object (context-specific)
  
Resource Gathering (location only):
  forage/g <object> - Gather resources using Survival skill
  harvest/v <object> - Gather resources using Nature skill
  chop/h <object> - Chop wood from trees or objects (destroys object)
  drink/b <object> - Drink from water sources
  
Object Manipulation (location only):
  unlock/k <object> - Pick locks on containers
  disarm <object> - Disarm traps on objects
  light/f <object> - Light fires in fireplaces or similar objects
  
Rest & Recovery (location only):
  rest/r - Rest in current location (recovery)
  wait/wa <duration> - Wait and pass time (quick/short/medium/long/extended)
  
Movement (overworld only):
  north/n, south/s, east/e, west/w - Move in that direction
  
Character:
  inventory/i - View your inventory
  character/c - View character sheet
  
System:
  save - Save game to save.json
  load - Load game from save.json
  debug - Show debug information
  dump_location - Dump current location data to JSON file
  dump_hex - Dump current hex data to JSON file
  dump_world - Dump entire world data to JSON file
  help/? - Show this help
  
Tip: Objects have permanent shortcuts like [fp] for fireplace, [we] for well!
Example: 'f fp' lights the fireplace, 'b we' drinks from the well"""
        
        return ActionResult(
            success=True,
            message=help_text,
            time_passed=0.0,
            action_type="help"
        )
    
    def handle_debug(self, *args) -> ActionResult:
        """Handle debug information display"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
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
                        for i, obj in enumerate(objects[:5]):
                            obj_name = obj.get('name', 'Unknown')
                            obj_id = obj.get('id', 'unknown')
                            debug_info.append(f"  {i+1}. {obj_name} (id: {obj_id})")
                        
                        debug_info.append(f"Items in area: {len(items)}")
                        for i, item in enumerate(items[:5]):
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
    
    def handle_dump_world(self, *args) -> ActionResult:
        """Handle dumping world data to JSON file"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
        try:
            import json
            
            # Convert climate_zones (has tuple keys) to string keys for JSON
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
        """Handle dumping current location data to JSON file - delegates to GameEngine"""
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
        """Handle dumping current hex data to JSON file - delegates to GameEngine"""
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
    
    def handle_save_game(self, *args) -> ActionResult:
        """Handle saving the game - delegates to GameEngine"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        try:
            success, message = self.game_engine.save_game("save")
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.0,
                action_type="system"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to save game: {str(e)}")
    
    def handle_load_game(self, *args) -> ActionResult:
        """Handle loading the game - delegates to GameEngine"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        try:
            success, message = self.game_engine.load_game("save")
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.0,
                action_type="system"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to load game: {str(e)}")
    
    def handle_save_log(self, *args) -> ActionResult:
        """Handle saving game log to text file"""
        # TODO: Implement save log functionality
        return ActionResult(
            success=True,
            message="Save log functionality not yet implemented.",
            time_passed=0.0,
            action_type="system"
        )
