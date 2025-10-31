"""
Fantasy RPG - Basic Action Handler

Minimal action processing for only the features that actually work.
Currently supports: inventory and character sheet.

CRITICAL REQUIREMENT: All actions that pass time MUST use the time system's perform_activity() method
to ensure condition effects (like damage from "Freezing") are properly applied during time passage.
Never set time_passed without calling the time system!
"""

from typing import Dict, Any, Optional, Tuple, List


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
    
    def __init__(self, character=None, player_state=None, game_engine=None):
        self.character = character
        self.player_state = player_state
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
            "dump_log": self.handle_save_log,
            
            # Object Interaction Actions (location only)
            "examine": self.handle_examine,
            "search": self.handle_search,
            "use": self.handle_use,
            
            # Resource Gathering Actions (location only)
            "forage": self.handle_forage,
            "harvest": self.handle_harvest,
            "chop": self.handle_chop,
            "cut": self.handle_chop,        # Alias for chop
            "drink": self.handle_drink,
            "water": self.handle_drink,     # Alias for drink
            "unlock": self.handle_unlock,
            "pick_lock": self.handle_unlock, # Alias for unlock
            
            # Rest and Recovery (location only)
            "rest": self.handle_rest,
            "sleep": self.handle_sleep,
            
            # Wait/Time actions
            "wait": self.handle_wait,
            
            # New comprehensive object interactions
            "cut": self.handle_cut,
            "climb": self.handle_climb,
            "light": self.handle_light_fire,
            "place": self.handle_place_items,
            "repair": self.handle_repair,
            "disarm": self.handle_disarm_trap,
            
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
            "save": self.handle_save_game,
            "load": self.handle_load_game,
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
  enter - Enter a location in this hex (no arguments needed)
  exit - Exit current location to overworld
  
Object Interaction (location only):
  examine <object> - Examine an object closely (shows available actions)
  search <object> - Search an object for items
  use <object> - Use an object (context-specific)
  
Resource Gathering (location only):
  forage <object> - Gather resources using Survival skill (e.g., 'forage berry bush')
  harvest <object> - Gather resources using Nature skill (e.g., 'harvest berry bush')
  chop/cut <object> - Chop wood from trees or objects (e.g., 'chop tree')
  drink/water <object> - Drink from water sources (e.g., 'drink well')
  
Object Manipulation (location only):
  unlock/pick_lock <object> - Pick locks on containers (e.g., 'unlock chest')
  disarm <object> - Disarm traps on objects (e.g., 'disarm chest')
  cut <object> - Cut through vines or similar obstacles
  climb <object> - Climb trees, rocks, or other climbable objects
  light <object> - Light fires in fireplaces or similar objects
  place <item> <object> - Place items on tables or storage surfaces
  repair <object> - Repair broken objects like fences
  
Rest & Recovery (location only):
  rest - Rest in current location (basic recovery)
  sleep <object> - Sleep on beds or other comfortable objects (better recovery)
  wait <duration> - Wait and pass time:
    • quick/15min - Wait 15 minutes
    • short/30min - Wait 30 minutes  
    • medium/1hr - Wait 1 hour
    • long/3hr - Wait 3 hours
    • extended/8hr - Wait 8 hours
  
Movement (overworld only):
  north, south, east, west (or n, s, e, w) - Move in that direction
  
Character:
  inventory, i - View your inventory
  character, c - View character sheet
  
System:
  save - Save game to save.json
  load - Load game from save.json
  debug - Show debug information
  dump_location - Dump current location data to JSON file
  dump_hex - Dump current hex data to JSON file
  dump_world - Dump entire world data to JSON file
  help - Show this help
  
Tip: Use 'examine <object>' to see what actions are available for each object!
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
                    # CRITICAL: Use time system to ensure condition effects are applied during time passage
                    if self.game_engine.time_system:
                        time_result = self.game_engine.time_system.perform_activity("travel", duration_override=0.5)
                        if not time_result.get("success", True):
                            return ActionResult(False, time_result.get("message", "Movement interrupted."))
                    
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
                # CRITICAL: Use time system to ensure condition effects are applied during time passage
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("travel", duration_override=2.0)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Movement interrupted."))
                
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
                # CRITICAL: Use time system to ensure condition effects are applied during time passage
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("look", duration_override=0.25)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Entry interrupted."))
                
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
                # CRITICAL: Use time system to ensure condition effects are applied during time passage
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("look", duration_override=0.25)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Exit interrupted."))
                
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
        """
        Handle examining objects - LOW RISK/LOW REWARD approach
        
        examine berry bush (Perception, DC 8) - LOW RISK/LOW REWARD
        - Success: 1-2 berries, Failure: 0-1 berries (very forgiving)
        - Best for: Perception-focused characters wanting consistency
        """
        if not self.game_engine:
            return ActionResult(False, "Object interaction system not available.")
        
        if not args:
            return ActionResult(False, "Examine what? Specify an object name.")
        
        object_name = " ".join(args).lower()
        
        try:
            # Find object using GameEngine coordination
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            # Implement multi-skill examine logic here in ActionHandler
            success, message = self._handle_examine_interaction(target_object, "examine")
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.1 if success else 0.0,  # Examining takes a little time
                action_type="object_interaction"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to examine object: {str(e)}")
    
    def handle_search(self, *args) -> ActionResult:
        """
        Handle searching objects - MEDIUM RISK/MEDIUM REWARD approach
        
        search berry bush (Perception + Nature, DC 10) - MEDIUM RISK/MEDIUM REWARD  
        - Success: 1-3 berries, Failure: 0-1 berries (forgiving)
        - Best for: Balanced perception/nature builds
        """
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Search what? Specify an object name (e.g., 'search chest')")
        
        object_name = " ".join(args)
        
        try:
            # Find object using GameEngine coordination
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            # Implement multi-skill search logic here in ActionHandler
            success, message = self._handle_search_interaction(target_object, "search")
            return ActionResult(success, message)
        except Exception as e:
            return ActionResult(False, f"Failed to search: {str(e)}")
    

    def handle_use(self, *args) -> ActionResult:
        """Handle using objects in current location"""
        if not self.game_engine:
            return ActionResult(False, "Object interaction system not available.")
        
        if not args:
            return ActionResult(False, "Use what? Specify an object name.")
        
        object_name = " ".join(args).lower()
        
        try:
            # Use the proper "use" action
            success, message = self.game_engine.interact_with_object(object_name, "use")
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25 if success else 0.0,  # Using objects takes time
                action_type="object_interaction"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to use object: {str(e)}")
    
    def handle_rest(self, *args) -> ActionResult:
        """Handle resting/sleeping in current location"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        try:
            success, message = self.game_engine.rest_in_location()
            return ActionResult(success, message)
        except Exception as e:
            return ActionResult(False, f"Failed to rest: {str(e)}")
    
    def handle_forage(self, *args) -> ActionResult:
        """Handle foraging with Survival skill check"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Forage what? Specify an object name (e.g., 'forage berry bush')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            success, message = self._handle_resource_gathering(target_object, "forage", "survival")
            
            # CRITICAL: Use time system to ensure condition effects are applied during time passage
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("forage", duration_override=0.25)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Foraging interrupted."))
            
            return ActionResult(success, message, time_passed=0.25)
        except Exception as e:
            return ActionResult(False, f"Failed to forage: {str(e)}")
    
    def handle_harvest(self, *args) -> ActionResult:
        """Handle harvesting with Nature skill check"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Harvest what? Specify an object name (e.g., 'harvest berry bush')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            success, message = self._handle_resource_gathering(target_object, "harvest", "nature")
            
            # CRITICAL: Use time system to ensure condition effects are applied during time passage
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("forage", duration_override=0.25)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Harvesting interrupted."))
            
            return ActionResult(success, message, time_passed=0.25)
        except Exception as e:
            return ActionResult(False, f"Failed to harvest: {str(e)}")
    
    def handle_chop(self, *args) -> ActionResult:
        """
        Handle chopping wood - ALTERNATIVE APPROACH for different character builds
        
        chop berry bush (Athletics + Nature, DC 11) - ALTERNATIVE APPROACH
        - Success: 1 berry + 1-2 firewood, Failure: 0 (different reward type)
        - Best for: Strength-based characters wanting mixed resources
        """
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Chop what? Specify an object name (e.g., 'chop tree')")
        
        object_name = " ".join(args)
        
        try:
            # Find object using GameEngine coordination
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            # Implement multi-skill chop logic here in ActionHandler
            success, message = self._handle_chop_interaction(target_object, "chop")
            return ActionResult(success, message)
        except Exception as e:
            return ActionResult(False, f"Failed to chop: {str(e)}")
    
    def handle_drink(self, *args) -> ActionResult:
        """Handle drinking from water sources with comprehensive water properties"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Drink from what? Specify a water source (e.g., 'drink well')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            properties = target_object.get("properties", {})
            if not properties.get("provides_water"):
                return ActionResult(False, f"The {target_object.get('name')} doesn't contain drinkable water.")
            
            # Check if bucket is required
            if properties.get("requires_bucket", False):
                # TODO: Check inventory for bucket
                return ActionResult(False, f"You need a bucket to draw water from the {target_object.get('name')}.")
            
            # Get water quality and apply benefits
            water_quality = properties.get("water_quality", "good")
            depth = properties.get("depth", "shallow")
            temperature = properties.get("temperature", "cool")
            
            # Apply water benefit based on quality
            self._apply_water_benefit(water_quality)
            
            message = f"You drink from the {target_object.get('name')}."
            message += f"\nThe {temperature} water is of {water_quality} quality and quenches your thirst."
            
            # Quality-specific effects
            if water_quality == "excellent":
                message += "\nThe pure, refreshing water makes you feel invigorated."
                # Could add small HP bonus
                if self.game_engine.game_state:
                    character = self.game_engine.game_state.character
                    character.hp = min(character.max_hp, character.hp + 1)
            elif water_quality == "poor":
                message += "\nThe water tastes stale but still helps with thirst."
                # Could add small negative effect or disease risk
            
            # CRITICAL: Use time system to ensure condition effects are applied during time passage
            if self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("drink", duration_override=0.1)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Drinking interrupted."))
            
            return ActionResult(
                success=True,
                message=message,
                time_passed=0.1,
                action_type="survival"
            )
            
        except Exception as e:
            return ActionResult(False, f"Failed to drink: {str(e)}")
    
    def handle_unlock(self, *args) -> ActionResult:
        """Handle unlocking/lockpicking objects with comprehensive DC system"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Unlock what? Specify an object name (e.g., 'unlock chest')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            properties = target_object.get("properties", {})
            if not properties.get("can_unlock"):
                return ActionResult(False, f"The {target_object.get('name')} doesn't have a lock.")
            
            # Check if already unlocked
            if target_object.get("unlocked", False):
                return ActionResult(False, f"The {target_object.get('name')} is already unlocked.")
            
            # Get lockpick DC
            dc = properties.get("dc_lockpick", 15)
            
            # Check for magical lock (higher DC or special requirements)
            if properties.get("magical_lock"):
                dc += 5
                
            # Check for traps first
            if properties.get("trapped"):
                trap_dc = properties.get("trap_dc", 18)
                
                # If object has hidden nature and it's not revealed, player doesn't know about trap
                if properties.get("hidden_nature") and not target_object.get("true_nature_revealed", False):
                    # Automatic trap trigger - player had no warning
                    damage = 2 + trap_dc // 10  # Base damage for surprise trap
                    if self.game_engine.game_state:
                        character = self.game_engine.game_state.character
                        character.hp = max(0, character.hp - damage)
                    
                    # Reveal true nature after triggering trap
                    target_object["true_nature_revealed"] = True
                    target_object["name"] = properties.get("true_name", target_object.get("name"))
                    target_object["description"] = properties.get("true_description", target_object.get("description"))
                    
                    return ActionResult(False, f"As you attempt to unlock the chest, hidden mechanisms activate! You trigger a trap and take {damage} damage. You now realize this was a {target_object['name']}!")
                else:
                    # Player knows about trap, can attempt to detect/disarm
                    trap_success, trap_total, trap_msg = self._check_skill_dc("perception", trap_dc)
                    
                    if not trap_success:
                        # Trigger trap
                        damage = 1 + (trap_dc - trap_total) // 5  # More damage for worse failure
                        if self.game_engine.game_state:
                            character = self.game_engine.game_state.character
                            character.hp = max(0, character.hp - damage)
                        
                        return ActionResult(False, f"You trigger the trap while attempting to unlock the {target_object.get('name')}! You take {damage} damage.")
            
            # Make lockpicking check
            success, total, check_msg = self._check_skill_dc("sleight_of_hand", dc)
            
            if success:
                target_object["unlocked"] = True
                
                message = f"You successfully unlock the {target_object.get('name')}."
                if properties.get("magical_lock"):
                    message += "\nThe magical wards dissipate as the lock opens."
                
                # Check for treasure
                if properties.get("contains_treasure"):
                    items_generated = self._generate_items_from_properties(target_object, total, dc)
                    success_items = self._add_items_to_inventory(items_generated)
                    if success_items:
                        message += f"\nInside you find: {', '.join(success_items)}"
                
                # CRITICAL: Use time system to ensure condition effects are applied during time passage
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("lockpick", duration_override=0.5)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Lockpicking interrupted."))
                
                return ActionResult(True, message, time_passed=0.5)
            else:
                return ActionResult(False, f"You struggle with the lock on the {target_object.get('name')} but can't open it.")
                
        except Exception as e:
            return ActionResult(False, f"Failed to unlock: {str(e)}")
    
    def _find_object_in_current_area(self, object_name: str):
        """Find an available object in the current area (GameEngine coordination)"""
        if not self.game_engine or not self.game_engine.is_initialized:
            return None
        
        gs = self.game_engine.game_state
        
        # Check if player is inside a location
        if not gs.world_position.current_location_id:
            return None
        
        # Get current area objects
        current_area_id = gs.world_position.current_area_id
        location_data = gs.world_position.current_location_data
        
        if not location_data or "areas" not in location_data:
            return None
        
        areas = location_data.get("areas", {})
        if current_area_id not in areas:
            return None
        
        area_data = areas[current_area_id]
        objects = area_data.get("objects", [])
        
        # Find the first available object with matching name
        # (not depleted, searched, chopped, etc. depending on action)
        for obj in objects:
            if obj.get("name", "").lower() == object_name.lower():
                # Check if this object is still available for interaction
                if not obj.get("depleted", False) and not obj.get("searched", False) and not obj.get("chopped", False) and not obj.get("wood_taken", False):
                    return obj
        
        # If no available objects found, return the first match anyway (for error messages)
        for obj in objects:
            if obj.get("name", "").lower() == object_name.lower():
                return obj
        
        return None
    
    def _handle_resource_gathering(self, obj: Dict, action_type: str, skill_name: str) -> Tuple[bool, str]:
        """Handle resource gathering with streamlined success categories"""
        properties = obj.get("properties", {})
        
        # Check if object can be foraged
        if not properties.get("can_forage"):
            return False, f"You can't {action_type} from the {obj.get('name', 'object')}."
        
        # Check if already depleted
        if obj.get("depleted", False):
            return False, f"The {obj.get('name')} has already been {action_type}ed recently."
        
        # Get DC from object properties or use default
        dc = properties.get("search_dc", 12)
        
        # Make skill check
        import random
        roll = random.randint(1, 20)
        skill_bonus = self._get_skill_bonus(skill_name)
        total = roll + skill_bonus
        
        # Use time system
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity(action_type, duration_override=0.25)
            if not time_result.get("success", True):
                return False, time_result.get("message", f"{action_type.title()} failed.")
        
        # Determine success category
        success_category = self._determine_success_category(roll, total, dc)
        
        if success_category in ["success"]:  # Only implementing Fail and Success for now
            # Success - mark as depleted and generate items
            obj["depleted"] = True
            
            result_msg = f"You successfully {action_type} from the {obj.get('name')}."
            
            # Handle food value
            food_value = properties.get("food_value", 0)
            if food_value > 0:
                self._apply_food_benefit(food_value)
                result_msg += f"\nYou restore {food_value} hunger."
            
            # Generate items from object properties
            items_generated = self._generate_items_from_properties(obj, total, dc)
            if items_generated:
                success_items = self._add_items_to_inventory(items_generated)
                if success_items:
                    result_msg += f"\nYou gather: {', '.join(success_items)}"
            
            return True, result_msg
        else:
            # Fail - no items, no depletion
            return False, f"You attempt to {action_type} from the {obj.get('name')} but don't find anything useful."
    
    def _determine_success_category(self, roll: int, total: int, dc: int) -> str:
        """
        Determine success category based on roll and total
        
        Categories:
        - Critical Fail: roll <= 1
        - Fail: roll > 1 and total < dc  
        - Success: total >= dc and total < 20
        - Critical Success: total >= 20
        
        For now, only implementing Fail and Success
        """
        if roll <= 1:
            return "critical_fail"  # Future implementation
        elif total < dc:
            return "fail"
        elif total >= 20:
            return "critical_success"  # Future implementation
        else:
            return "success"
    
    def _get_interaction_skill_and_dc(self, interaction_type: str, object_name: str) -> tuple[str, str, int]:
        """
        Get the primary skill, secondary skill, and DC for an interaction type on an object.
        
        Returns:
            (primary_skill, secondary_skill, dc)
        """
        object_lower = object_name.lower()
        
        # Berry bushes and food sources
        if "berry" in object_lower:
            if interaction_type in ["forage", "harvest", "gather", "pick"]:
                return ("nature", None, 12)  # High risk/high reward
            elif interaction_type in ["search"]:
                return ("perception", "nature", 10)  # Medium risk/medium reward
            elif interaction_type in ["examine"]:
                return ("perception", None, 8)  # Low risk/low reward
            elif interaction_type in ["chop", "cut"]:
                return ("athletics", "nature", 11)  # Alternative approach
        
        # Trees and wood sources
        elif any(wood_type in object_lower for wood_type in ["tree", "log", "wood"]):
            if interaction_type in ["chop", "cut"]:
                return ("athletics", "nature", 13)  # High risk/high reward
            elif interaction_type in ["search"]:
                return ("perception", "nature", 10)  # Medium risk/diverse reward
            elif interaction_type in ["examine"]:
                return ("perception", None, 9)  # Low risk/discovery reward
        
        # Containers and chests
        elif any(container in object_lower for container in ["chest", "box", "container", "barrel"]):
            if interaction_type in ["search"]:
                return ("investigation", "perception", 12)  # Medium risk/high reward
            elif interaction_type in ["examine"]:
                return ("perception", None, 10)  # Low risk/medium reward
            elif interaction_type in ["unlock"]:
                return ("sleight_of_hand", "investigation", 15)  # High risk/high reward
        
        # Wells and water sources
        elif "well" in object_lower:
            if interaction_type in ["search"]:
                return ("investigation", "perception", 11)  # Medium risk/treasure reward
            elif interaction_type in ["examine"]:
                return ("perception", None, 9)  # Low risk/small reward
        
        # Default fallback
        return ("perception", None, 10)
    
    def _get_multi_skill_bonus(self, primary_skill: str, secondary_skill: str = None) -> int:
        """Get combined skill bonus for multi-skill checks"""
        primary_bonus = self._get_skill_bonus(primary_skill)
        if secondary_skill:
            secondary_bonus = self._get_skill_bonus(secondary_skill)
            # Primary skill gets full weight, secondary gets half weight
            return primary_bonus + (secondary_bonus // 2)
        return primary_bonus
    
    def _get_skill_bonus(self, skill_name: str) -> int:
        """Get character's skill bonus"""
        if not self.game_engine or not self.game_engine.game_state:
            return 0
        
        character = self.game_engine.game_state.character
        if skill_name == "nature":
            return (character.wisdom - 10) // 2
        elif skill_name == "perception":
            return (character.wisdom - 10) // 2
        elif skill_name == "investigation":
            return (character.intelligence - 10) // 2
        elif skill_name == "athletics":
            return (character.strength - 10) // 2
        elif skill_name == "sleight_of_hand":
            return (character.dexterity - 10) // 2
        elif skill_name == "survival":
            return (character.wisdom - 10) // 2
        else:
            return 0
    
    def _generate_items_from_object(self, obj: Dict, interaction_type: str, skill_roll: int = 10, dc: int = 10) -> Dict[str, int]:
        """
        Generate items based on multi-skill risk/reward system
        
        Berry Bush -> Multi-skill approach
        """
        import random
        
        properties = obj.get("properties", {})
        items_to_generate = {}
        
        # Calculate success quality based on how much the roll exceeded DC
        success_margin = skill_roll - dc
        
        # Determine what items to generate based on object type and interaction
        object_name = obj.get("name", "").lower()
        
        # Berry Bush -> Multi-skill approach
        if "berry" in object_name:
            if interaction_type in ["forage", "harvest", "gather", "pick"]:
                # HIGH RISK/HIGH REWARD: Nature skill, DC 12, best yield but harsh failure
                # Success: 2-5 berries, Failure: 0 berries
                if success_margin >= 0:
                    quantity = 2 + max(0, success_margin // 3)  # 2-5 berries based on success
                    items_to_generate["wild_berries"] = min(5, quantity)
                # Failure handled by caller (no items)
                
            elif interaction_type in ["search"]:
                # MEDIUM RISK/MEDIUM REWARD: Perception + Nature, DC 10, steady yield
                # Success: 1-3 berries, Failure: 0-1 berries  
                if success_margin >= 0:
                    quantity = 1 + max(0, success_margin // 5)  # 1-3 berries
                    items_to_generate["wild_berries"] = min(3, quantity)
                else:
                    # Even on failure, might find 1 berry if close
                    if success_margin >= -3:
                        items_to_generate["wild_berries"] = 1
                        
            elif interaction_type in ["examine"]:
                # LOW RISK/LOW REWARD: Perception primary, DC 8, consistent small yield
                # Success: 1-2 berries, Failure: 0-1 berries
                if success_margin >= 0:
                    quantity = 1 + (1 if success_margin >= 8 else 0)  # 1-2 berries
                    items_to_generate["wild_berries"] = quantity
                else:
                    # Forgiving failure - might still spot obvious berries
                    if success_margin >= -5:
                        items_to_generate["wild_berries"] = 1
                        
            elif interaction_type in ["chop", "cut"]:
                # ALTERNATIVE APPROACH: Strength + Nature, DC 11, different rewards
                # Success: 1 berry + 1-2 firewood (clearing brush), Failure: just noise
                if success_margin >= 0:
                    items_to_generate["wild_berries"] = 1  # Shake berries loose
                    items_to_generate["firewood"] = 1 + (1 if success_margin >= 5 else 0)
                # Failure: nothing (too rough, scared away animals, etc.)
        
        # Trees/Wood -> Multi-skill approach  
        elif any(wood_type in object_name for wood_type in ["tree", "log", "wood"]):
            if interaction_type in ["chop", "cut"]:
                # HIGH RISK/HIGH REWARD: Strength + Nature, DC 13, best firewood yield
                # Success: 3-6 firewood, Failure: 0-1 firewood
                if success_margin >= 0:
                    quantity = 3 + max(0, success_margin // 3)  # 3-6 firewood
                    items_to_generate["firewood"] = min(6, quantity)
                else:
                    # Harsh failure - might get splinters or small pieces
                    if success_margin >= -2:
                        items_to_generate["firewood"] = 1
                        
            elif interaction_type in ["search"]:
                # MEDIUM RISK/DIVERSE REWARD: Perception + Nature, DC 10, mixed finds
                # Success: 1-2 firewood + chance for other items, Failure: 0-1 firewood
                if success_margin >= 0:
                    firewood_qty = 1 + (1 if success_margin >= 6 else 0)  # 1-2 firewood
                    items_to_generate["firewood"] = firewood_qty
                    
                    # Bonus finds based on success margin
                    if success_margin >= 10:
                        items_to_generate["wild_berries"] = 1  # Bird's nest
                    if success_margin >= 15:
                        items_to_generate["gold_coins"] = random.randint(1, 3)  # Hidden cache
                else:
                    # Gentle failure - might find small twigs
                    if success_margin >= -4:
                        items_to_generate["firewood"] = 1
                        
            elif interaction_type in ["examine"]:
                # LOW RISK/DISCOVERY REWARD: Perception primary, DC 9, knowledge-based
                # Success: 1 firewood + information, Failure: just information
                if success_margin >= 0:
                    items_to_generate["firewood"] = 1  # Obvious dead branches
                    # Bonus for very good examination
                    if success_margin >= 12:
                        items_to_generate["wild_berries"] = 1  # Spot bird's nest
                # Even failure gives some insight (handled by examine method)
                
            elif interaction_type in ["take"]:
                # NO RISK/LOW REWARD: No skill check, just taking obvious loose wood
                # Always succeeds: 1-2 firewood
                items_to_generate["firewood"] = 1 + (1 if random.randint(1, 100) <= 50 else 0)
        
        # Generic fallback
        else:
            # Check for specific item generation in properties
            if properties.get("generates_items"):
                generated_item = properties.get("generated_item_id")
                base_quantity = properties.get("generated_quantity", 1)
                if generated_item:
                    # Apply success-based scaling
                    if success_margin >= 0:
                        final_quantity = base_quantity + max(0, success_margin // 5)
                        items_to_generate[generated_item] = final_quantity
                    else:
                        # Gentle failure for generic items
                        if success_margin >= -3:
                            items_to_generate[generated_item] = max(1, base_quantity // 2)
        
        return items_to_generate
    
    def _handle_search_interaction(self, obj: Dict, interaction_type: str) -> Tuple[bool, str]:
        """Handle searching with MEDIUM RISK/MEDIUM REWARD approach"""
        properties = obj.get("properties", {})
        
        # Check if object can be searched
        if not properties.get("can_search"):
            return False, f"There's nothing to search in the {obj.get('name')}."
        
        # Check if already searched
        if obj.get("searched", False):
            return False, f"You have already searched the {obj.get('name')}."
        
        # Make skill check - MEDIUM RISK/MEDIUM REWARD approach
        import random
        roll = random.randint(1, 20)
        primary_skill, secondary_skill, dc = self._get_interaction_skill_and_dc("search", obj.get("name", ""))
        skill_bonus = self._get_multi_skill_bonus(primary_skill, secondary_skill)
        total = roll + skill_bonus
        
        # Use time system (GameEngine coordination)
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("search", duration_override=0.5)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Search failed.")
        
        # Mark as searched regardless of success
        obj["searched"] = True
        
        if total >= dc:
            # Success - generate items based on multi-skill system
            items_generated = self._generate_items_from_object(obj, "search", total, dc)
            
            if items_generated:
                # Add items to inventory (GameEngine coordination)
                success_items = []
                failed_items = []
                
                gs = self.game_engine.game_state
                for item_id, quantity in items_generated.items():
                    if gs.character.add_item_to_inventory(item_id, quantity):
                        success_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                    else:
                        failed_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                
                result_msg = f"You search the {obj.get('name')} thoroughly."
                if success_items:
                    result_msg += f"\nYou find: {', '.join(success_items)}"
                if failed_items:
                    result_msg += f"\nCouldn't carry: {', '.join(failed_items)} (inventory full)"
                
                return True, result_msg
            else:
                return True, f"You search the {obj.get('name')} thoroughly but find nothing of value."
        else:
            # FORGIVING FAILURE for medium-risk approach
            items_generated = self._generate_items_from_object(obj, "search", total, dc)  # Still try to generate with negative margin
            if items_generated:
                success_items = []
                gs = self.game_engine.game_state
                for item_id, quantity in items_generated.items():
                    if gs.character.add_item_to_inventory(item_id, quantity):
                        success_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                
                if success_items:
                    return True, f"You search the {obj.get('name')} and find: {', '.join(success_items)}"
            
            return False, f"You search the {obj.get('name')} but don't find anything."
    
    def _handle_chop_interaction(self, obj: Dict, interaction_type: str) -> Tuple[bool, str]:
        """Handle chopping with ALTERNATIVE APPROACH for different builds"""
        properties = obj.get("properties", {})
        
        # Check if object can be chopped
        if not properties.get("can_chop_wood"):
            return False, f"You can't chop wood from the {obj.get('name', 'object')}."
        
        # Check if already chopped
        if obj.get("chopped", False):
            return False, f"You have already chopped wood from the {obj.get('name')}."
        
        # Make skill check - ALTERNATIVE APPROACH
        import random
        roll = random.randint(1, 20)
        primary_skill, secondary_skill, dc = self._get_interaction_skill_and_dc("chop", obj.get("name", ""))
        skill_bonus = self._get_multi_skill_bonus(primary_skill, secondary_skill)
        total = roll + skill_bonus
        
        # Use time system (GameEngine coordination)
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("chop_wood", duration_override=1.0)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Chopping failed.")
        
        if total >= dc:
            # Success - generate items based on multi-skill system
            items_generated = self._generate_items_from_object(obj, "chop", total, dc)
            
            if items_generated:
                obj["chopped"] = True
                
                # Add items to inventory (GameEngine coordination)
                success_items = []
                failed_items = []
                
                gs = self.game_engine.game_state
                for item_id, quantity in items_generated.items():
                    if gs.character.add_item_to_inventory(item_id, quantity):
                        success_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                    else:
                        failed_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                
                result_msg = f"You chop wood from the {obj.get('name')}."
                if success_items:
                    result_msg += f"\nYou gather: {', '.join(success_items)}"
                if failed_items:
                    result_msg += f"\nCouldn't carry: {', '.join(failed_items)} (inventory full)"
                
                return True, result_msg
            else:
                return True, f"You chop the {obj.get('name')} but don't get much usable wood."
        else:
            # HARSH FAILURE for alternative approach (different risk profile)
            return False, f"You attempt to chop the {obj.get('name')} but don't get much usable wood."
    
    def _handle_examine_interaction(self, obj: Dict, interaction_type: str) -> Tuple[bool, str]:
        """Handle examining - available for ALL objects with property-based information"""
        properties = obj.get("properties", {})
        
        # Check for hidden nature discovery first
        if properties.get("hidden_nature") and not obj.get("true_nature_revealed", False):
            investigation_dc = properties.get("investigation_dc", 15)
            investigation_success, investigation_total, _ = self._check_skill_dc("investigation", investigation_dc)
            
            if investigation_success:
                # Reveal true nature
                obj["true_nature_revealed"] = True
                obj["name"] = properties.get("true_name", obj.get("name"))
                obj["description"] = properties.get("true_description", obj.get("description"))
                if properties.get("true_examination_text"):
                    properties["examination_text"] = properties.get("true_examination_text")
                
                result_msg = f"Upon careful investigation, you realize this is actually a {obj['name']}!"
                result_msg += f"\n\n{obj['description']}"
                
                if properties.get("true_examination_text"):
                    result_msg += f"\n\n{properties['true_examination_text']}"
                
                # Show that it's trapped if it is
                if properties.get("trapped"):
                    trap_dc = properties.get("trap_dc", "unknown")
                    result_msg += f"\n\nDANGER: This object appears to be trapped! (Trap DC {trap_dc})"
                
                return True, result_msg
        
        # Use current name and description (may have been updated by discovery)
        base_description = obj.get("description", "An unremarkable object.")
        
        # Get DC from object properties or use default
        dc = properties.get("examine_dc", 8)
        
        # Make skill check
        success, total, check_msg = self._check_skill_dc("perception", dc)
        
        # Examining takes a little time
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("look", duration_override=0.083)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Examination failed.")
        
        result_msg = base_description
        
        # Add examination text if available
        examination_text = properties.get("examination_text", "")
        if examination_text:
            result_msg += f"\n\n{examination_text}"
        
        # Show available actions based on properties
        available_actions = self._get_available_actions_for_object(obj)
        if len(available_actions) > 1:  # More than just "examine"
            other_actions = [action for action in available_actions if action != "examine"]
            result_msg += f"\n\nAvailable actions: {', '.join(other_actions)}"
        
        # Reveal property-based information on successful check
        if success:
            property_info = []
            
            # Physical properties
            if properties.get("provides_shelter"):
                property_info.append("provides shelter from weather")
            if properties.get("provides_warmth"):
                property_info.append("radiates warmth")
            if properties.get("provides_light"):
                property_info.append("gives off light")
            if properties.get("provides_water"):
                quality = properties.get("water_quality", "unknown")
                property_info.append(f"contains {quality} quality water")
            if properties.get("provides_cover"):
                cover_type = properties.get("provides_cover")
                property_info.append(f"provides {cover_type} cover")
            
            # Functional properties
            if properties.get("rest_bonus"):
                bonus = properties.get("rest_bonus")
                comfort = properties.get("comfort_level", "basic")
                property_info.append(f"offers {comfort} comfort for resting (+{bonus} rest quality)")
            if properties.get("fuel_value"):
                fuel = properties.get("fuel_value")
                property_info.append(f"could provide {fuel} units of fuel")
            if properties.get("food_value"):
                food = properties.get("food_value")
                property_info.append(f"appears to have nutritional value ({food})")
            
            # Special properties (only show if true nature revealed or not hidden)
            if not properties.get("hidden_nature") or obj.get("true_nature_revealed", False):
                if properties.get("magical_lock"):
                    property_info.append("sealed with magical wards")
                if properties.get("trapped"):
                    trap_dc = properties.get("trap_dc", "unknown")
                    property_info.append(f"may be trapped (detection DC {trap_dc})")
            
            if properties.get("historical_significance"):
                property_info.append("has historical importance")
            if properties.get("seasonal"):
                property_info.append("availability varies by season")
            if properties.get("renewable"):
                property_info.append("resources replenish over time")
            
            if property_info:
                result_msg += f"\n\nYou notice: {'; '.join(property_info)}."
        
        # Generate items on very successful examination
        if success and total >= dc + 5:
            items_generated = self._generate_items_from_properties(obj, total, dc)
            if items_generated:
                success_items = self._add_items_to_inventory(items_generated)
                if success_items:
                    result_msg += f"\n\nWhile examining closely, you find: {', '.join(success_items)}"
        
        return True, result_msg
    
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
    
    def handle_save_game(self, *args) -> ActionResult:
        """Handle saving the game to save.json"""
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
        """Handle loading the game from save.json"""
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
    
    # ===== COMPREHENSIVE OBJECT PROPERTY SYSTEM =====
    
    def _generate_items_from_properties(self, obj: Dict, skill_roll: int = 10, dc: int = 10) -> Dict[str, int]:
        """Generate items based on object properties"""
        properties = obj.get("properties", {})
        items_to_generate = {}
        
        # Check for specific item generation
        if properties.get("generates_items"):
            item_id = properties.get("generated_item_id")
            base_quantity = properties.get("generated_quantity", 1)
            if item_id:
                # Scale quantity based on skill success
                success_margin = skill_roll - dc
                final_quantity = base_quantity + max(0, success_margin // 5)
                items_to_generate[item_id] = final_quantity
        
        return items_to_generate
    
    def _add_items_to_inventory(self, items_dict: Dict[str, int]) -> List[str]:
        """Add items to character inventory and return success list"""
        success_items = []
        gs = self.game_engine.game_state
        
        for item_id, quantity in items_dict.items():
            if gs.character.add_item_to_inventory(item_id, quantity):
                success_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
        
        return success_items
    
    def _apply_food_benefit(self, food_value: int):
        """Apply food benefit to character survival stats"""
        if self.game_engine and self.game_engine.game_state:
            player_state = self.game_engine.game_state.player_state
            if hasattr(player_state, 'hunger'):
                player_state.hunger = max(0, player_state.hunger - food_value * 10)
    
    def _apply_water_benefit(self, water_quality: str = "good"):
        """Apply water benefit based on quality"""
        if self.game_engine and self.game_engine.game_state:
            player_state = self.game_engine.game_state.player_state
            if hasattr(player_state, 'thirst'):
                quality_multiplier = {"poor": 0.5, "good": 1.0, "excellent": 1.5}.get(water_quality, 1.0)
                thirst_reduction = int(20 * quality_multiplier)
                player_state.thirst = max(0, player_state.thirst - thirst_reduction)
    
    def _apply_warmth_benefit(self, warmth_bonus: int = 5):
        """Apply warmth benefit to character temperature"""
        if self.game_engine and self.game_engine.game_state:
            player_state = self.game_engine.game_state.player_state
            if hasattr(player_state, 'body_temperature'):
                player_state.body_temperature = min(98.6, player_state.body_temperature + warmth_bonus)
    
    def _apply_rest_benefit(self, rest_bonus: int = 2):
        """Apply rest benefit to character fatigue/health"""
        if self.game_engine and self.game_engine.game_state:
            character = self.game_engine.game_state.character
            player_state = self.game_engine.game_state.player_state
            
            # Heal HP based on rest quality
            heal_amount = rest_bonus
            character.hp = min(character.max_hp, character.hp + heal_amount)
            
            # Reduce fatigue if system exists
            if hasattr(player_state, 'fatigue'):
                player_state.fatigue = max(0, player_state.fatigue - rest_bonus * 10)
    
    def _check_skill_dc(self, skill_name: str, dc: int) -> Tuple[bool, int, str]:
        """Perform a skill check and return result"""
        import random
        roll = random.randint(1, 20)
        skill_bonus = self._get_skill_bonus(skill_name)
        total = roll + skill_bonus
        
        success = total >= dc
        message = f"{skill_name.title()} check: {roll} + {skill_bonus} = {total} (DC {dc})"
        
        return success, total, message
    
    def _get_available_actions_for_object(self, obj: Dict) -> List[str]:
        """Get list of available actions for an object based on its properties"""
        properties = obj.get("properties", {})
        actions = ["examine"]  # All objects can be examined
        
        # Interaction Properties
        if properties.get("can_cut"): actions.append("cut")
        if properties.get("can_unlock"): actions.append("unlock")
        if properties.get("can_search"): actions.append("search")
        if properties.get("can_forage"): actions.extend(["forage", "harvest"])
        if properties.get("can_climb"): actions.append("climb")
        if properties.get("can_chop_wood"): actions.append("chop")
        if properties.get("can_light_fire"): actions.append("light")
        if properties.get("can_sleep"): actions.extend(["sleep", "rest"])
        if properties.get("can_place_items"): actions.append("place")

        if properties.get("can_repair"): actions.append("repair")

        if properties.get("can_disarm"): actions.append("disarm")
        if properties.get("provides_water"): actions.append("drink")
        
        return actions
    
    # ===== NEW COMPREHENSIVE ACTION HANDLERS =====
    
    def handle_sleep(self, *args) -> ActionResult:
        """Handle sleeping on objects with can_sleep property"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Sleep on what? Specify an object (e.g., 'sleep bed')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            properties = target_object.get("properties", {})
            if not properties.get("can_sleep"):
                return ActionResult(False, f"You can't sleep on the {target_object.get('name')}.")
            
            # Apply rest bonus from object
            rest_bonus = properties.get("rest_bonus", 0)
            comfort_level = properties.get("comfort_level", "basic")
            
            # Base sleep duration and benefits
            base_heal = 5 + rest_bonus
            sleep_duration = 8.0  # 8 hours
            
            # Apply benefits
            self._apply_rest_benefit(rest_bonus + 3)  # Extra benefit for sleeping vs resting
            
            # Use time system
            if self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("sleep", duration_override=sleep_duration)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Sleep interrupted."))
            
            message = f"You sleep on the {comfort_level} {target_object.get('name')} for {sleep_duration} hours."
            message += f"\nYou feel refreshed and heal {base_heal} HP."
            if rest_bonus > 0:
                message += f"\nThe {comfort_level} comfort provides +{rest_bonus} rest quality."
            
            return ActionResult(
                success=True,
                message=message,
                time_passed=sleep_duration,
                action_type="rest"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to sleep: {str(e)}")
    
    def handle_cut(self, *args) -> ActionResult:
        """Handle cutting objects with can_cut property"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Cut what? Specify an object (e.g., 'cut vines')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            properties = target_object.get("properties", {})
            if not properties.get("can_cut"):
                return ActionResult(False, f"You can't cut the {target_object.get('name')}.")
            
            # Check if already cut
            if target_object.get("cut", False):
                return ActionResult(False, f"The {target_object.get('name')} has already been cut.")
            
            # Make skill check
            dc = properties.get("dc_strength", 12)
            success, total, check_msg = self._check_skill_dc("athletics", dc)
            
            if success:
                target_object["cut"] = True
                
                # Generate items if applicable
                items_generated = self._generate_items_from_properties(target_object, total, dc)
                success_items = self._add_items_to_inventory(items_generated)
                
                message = f"You successfully cut through the {target_object.get('name')}."
                if success_items:
                    message += f"\nYou gather: {', '.join(success_items)}"
                
                # CRITICAL: Use time system to ensure condition effects are applied during time passage
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("craft_simple", duration_override=0.5)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Cutting interrupted."))
                
                return ActionResult(True, message, time_passed=0.5)
            else:
                return ActionResult(False, f"You struggle to cut the {target_object.get('name')} but make no progress.")
                
        except Exception as e:
            return ActionResult(False, f"Failed to cut: {str(e)}")
    
    def handle_climb(self, *args) -> ActionResult:
        """Handle climbing objects with can_climb property"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Climb what? Specify an object (e.g., 'climb tree')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            properties = target_object.get("properties", {})
            if not properties.get("can_climb") and not properties.get("climbable"):
                return ActionResult(False, f"You can't climb the {target_object.get('name')}.")
            
            # Make athletics check
            dc = properties.get("dc_strength", 13)
            success, total, check_msg = self._check_skill_dc("athletics", dc)
            
            if success:
                message = f"You successfully climb the {target_object.get('name')}."
                message += "\nFrom your elevated position, you get a better view of the area."
                
                # Bonus perception check for elevated view
                perception_success, _, _ = self._check_skill_dc("perception", 10)
                if perception_success:
                    message += "\nYou spot something interesting from up here!"
                    # Could reveal hidden objects or provide area information
                
                # CRITICAL: Use time system to ensure condition effects are applied during time passage
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("explore", duration_override=0.25)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Climbing interrupted."))
                
                return ActionResult(True, message, time_passed=0.25)
            else:
                return ActionResult(False, f"You attempt to climb the {target_object.get('name')} but can't get a good grip.")
                
        except Exception as e:
            return ActionResult(False, f"Failed to climb: {str(e)}")
    
    def handle_light_fire(self, *args) -> ActionResult:
        """Handle lighting fires in objects with can_light_fire property"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Light fire in what? Specify an object (e.g., 'light fireplace')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            properties = target_object.get("properties", {})
            if not properties.get("can_light_fire"):
                return ActionResult(False, f"You can't light a fire in the {target_object.get('name')}.")
            
            # Check if already lit
            if target_object.get("lit", False):
                return ActionResult(False, f"The {target_object.get('name')} is already lit.")
            
            # Check if fuel is required
            if properties.get("fuel_required"):
                if not self._check_and_consume_fuel():
                    return ActionResult(False, f"You need firewood to light a fire in the {target_object.get('name')}.")
            
            # Make survival check to light fire
            success, total, check_msg = self._check_skill_dc("survival", 12)
            
            if success:
                # Transform object if it has transforms_to property
                transforms_to = properties.get("transforms_to")
                if transforms_to:
                    success = self._transform_object(target_object, transforms_to)
                    if not success:
                        return ActionResult(False, f"Failed to transform {target_object.get('name')} after lighting.")
                else:
                    target_object["lit"] = True
                
                message = f"You successfully light a fire in the {target_object.get('name')}."
                message += "\nYou consume 1 firewood to fuel the flames."
                
                # Apply warmth benefit
                self._apply_warmth_benefit(10)
                message += "\nThe fire provides comforting warmth and illuminates the area."
                
                # Use time system for lighting fire
                time_passed = 0.25  # 15 minutes to light a fire
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("craft_simple", duration_override=time_passed)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Failed to light fire due to time constraints."))
                
                return ActionResult(True, message, time_passed=time_passed)
            else:
                return ActionResult(False, f"You struggle to light a fire in the {target_object.get('name')}.")
                
        except Exception as e:
            return ActionResult(False, f"Failed to light fire: {str(e)}")
    
    def _transform_object(self, target_object: Dict, new_object_id: str) -> bool:
        """Transform an object into a different object type"""
        try:
            # Load the new object data from objects.json
            import json
            with open('fantasy_rpg/data/objects.json', 'r') as f:
                objects_data = json.load(f)
            
            if new_object_id not in objects_data['objects']:
                return False
            
            new_object_data = objects_data['objects'][new_object_id]
            
            # Update the target object with new data
            # Handle name as either string or list of strings
            name_data = new_object_data['name']
            if isinstance(name_data, list):
                # Randomly select one name from the list
                import random
                selected_name = random.choice(name_data)
            else:
                selected_name = name_data
            
            target_object['name'] = selected_name
            target_object['description'] = new_object_data['description']
            target_object['properties'] = new_object_data['properties'].copy()
            target_object['lit'] = True  # Mark as lit
            
            # Copy any item drops if they exist
            if 'item_drops' in new_object_data:
                target_object['item_drops'] = new_object_data['item_drops']
            
            return True
        except Exception as e:
            print(f"Error transforming object: {e}")
            return False
    
    def _check_and_consume_fuel(self) -> bool:
        """Check if player has firewood and consume 1 unit"""
        if not self.game_engine or not self.game_engine.game_state:
            return False
        
        character = self.game_engine.game_state.character
        
        try:
            # Method 1: Use inventory.remove_item() method (from inventory.py)
            if hasattr(character, 'inventory') and hasattr(character.inventory, 'remove_item'):
                removed_item = character.inventory.remove_item("firewood", 1)
                return removed_item is not None
            
            # Method 2: Use inventory.has_item() and manual removal
            if hasattr(character, 'inventory') and hasattr(character.inventory, 'has_item'):
                if character.inventory.has_item("firewood", 1):
                    # Find and remove the item manually
                    for item in character.inventory.items:
                        if item.item_id == "firewood" and item.quantity > 0:
                            item.quantity -= 1
                            if item.quantity <= 0:
                                character.inventory.items.remove(item)
                            return True
            
            # Method 3: Direct access to inventory.items list (InventoryItem objects)
            if hasattr(character, 'inventory') and hasattr(character.inventory, 'items'):
                for item in character.inventory.items:
                    if hasattr(item, 'item_id') and item.item_id == "firewood":
                        if hasattr(item, 'quantity') and item.quantity > 0:
                            item.quantity -= 1
                            if item.quantity <= 0:
                                character.inventory.items.remove(item)
                            return True
            
            # Method 4: Character-level remove method
            if hasattr(character, 'remove_item_from_inventory'):
                return character.remove_item_from_inventory("firewood", 1)
            
        except Exception as e:
            print(f"Error checking inventory: {e}")
        
        # No firewood found
        return False
    
    def _has_item_in_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Check if player has specified item in inventory"""
        if not self.game_engine or not self.game_engine.game_state:
            return False
        
        character = self.game_engine.game_state.character
        # TODO: Implement proper inventory checking
        return True  # Placeholder
    
    def _consume_item_from_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Remove specified item from player inventory"""
        if not self.game_engine or not self.game_engine.game_state:
            return False
        
        character = self.game_engine.game_state.character
        # TODO: Implement proper inventory item removal
        return True  # Placeholder
    
    def handle_place_items(self, *args) -> ActionResult:
        """Handle placing items on objects with can_place_items property"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if len(args) < 2:
            return ActionResult(False, "Place what on what? (e.g., 'place sword table')")
        
        item_name = args[0]
        object_name = " ".join(args[1:])
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            properties = target_object.get("properties", {})
            if not properties.get("can_place_items"):
                return ActionResult(False, f"You can't place items on the {target_object.get('name')}.")
            
            # Check storage capacity
            storage_slots = properties.get("storage_slots", 1)
            current_items = target_object.get("placed_items", [])
            
            if len(current_items) >= storage_slots:
                return ActionResult(False, f"The {target_object.get('name')} is full.")
            
            # TODO: Check if player has the item and remove from inventory
            # For now, just simulate placing
            if "placed_items" not in target_object:
                target_object["placed_items"] = []
            target_object["placed_items"].append(item_name)
            
            return ActionResult(True, f"You place the {item_name} on the {target_object.get('name')}.")
            
        except Exception as e:
            return ActionResult(False, f"Failed to place item: {str(e)}")
    
    def handle_repair(self, *args) -> ActionResult:
        """Handle repairing objects with can_repair property"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Repair what? Specify an object (e.g., 'repair fence')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            properties = target_object.get("properties", {})
            if not properties.get("can_repair"):
                return ActionResult(False, f"The {target_object.get('name')} doesn't need repair or can't be repaired.")
            
            # Check if already repaired
            if target_object.get("repaired", False):
                return ActionResult(False, f"The {target_object.get('name')} is already in good condition.")
            
            # Make skill check (could require tools)
            tool_required = properties.get("tool_required", False)
            dc = 15 if tool_required else 12
            
            success, total, check_msg = self._check_skill_dc("athletics", dc)
            
            if success:
                target_object["repaired"] = True
                
                message = f"You successfully repair the {target_object.get('name')}."
                if tool_required:
                    message += "\nThe repair work required some skill and effort."
                
                # CRITICAL: Use time system to ensure condition effects are applied during time passage
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("craft_simple", duration_override=1.0)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Repair interrupted."))
                
                return ActionResult(True, message, time_passed=1.0)
            else:
                return ActionResult(False, f"You attempt to repair the {target_object.get('name')} but lack the skill or tools needed.")
                
        except Exception as e:
            return ActionResult(False, f"Failed to repair: {str(e)}")
    

    def handle_disarm_trap(self, *args) -> ActionResult:
        """Handle disarming traps on objects with can_disarm property"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Disarm what? Specify an object (e.g., 'disarm chest')")
        
        object_name = " ".join(args)
        
        try:
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            properties = target_object.get("properties", {})
            if not properties.get("can_disarm"):
                return ActionResult(False, f"The {target_object.get('name')} doesn't appear to have any traps to disarm.")
            
            # Check if trap is already disarmed
            if target_object.get("disarmed", False):
                return ActionResult(False, f"The trap on the {target_object.get('name')} has already been disarmed.")
            
            # Check if true nature is revealed (player must know it's trapped)
            if properties.get("hidden_nature") and not target_object.get("true_nature_revealed", False):
                return ActionResult(False, f"You don't see any traps on the {target_object.get('name')}. Try examining it more carefully first.")
            
            # Get disarm DC
            disarm_dc = properties.get("disarm_dc", properties.get("trap_dc", 16))
            
            # Make sleight of hand check to disarm trap
            success, total, check_msg = self._check_skill_dc("sleight_of_hand", disarm_dc)
            
            if success:
                # Mark as disarmed
                target_object["disarmed"] = True
                
                # Transform object if it has disarm_transforms_to property
                transforms_to = properties.get("disarm_transforms_to")
                if transforms_to:
                    transform_success = self._transform_object(target_object, transforms_to)
                    if transform_success:
                        message = f"You carefully disarm the trap on the {target_object.get('name')}."
                        message += f"\nThe {target_object.get('name')} is now safe to use."
                    else:
                        message = f"You disarm the trap but something went wrong with the mechanism."
                else:
                    message = f"You successfully disarm the trap on the {target_object.get('name')}."
                
                # CRITICAL: Use time system to ensure condition effects are applied during time passage
                if self.game_engine.time_system:
                    time_result = self.game_engine.time_system.perform_activity("lockpick", duration_override=1.0)
                    if not time_result.get("success", True):
                        return ActionResult(False, time_result.get("message", "Disarming interrupted."))
                
                return ActionResult(True, message, time_passed=1.0)
            else:
                # Failed disarm attempt - trigger trap
                damage = 1 + (disarm_dc - total) // 5  # More damage for worse failure
                if self.game_engine.game_state:
                    character = self.game_engine.game_state.character
                    character.hp = max(0, character.hp - damage)
                
                return ActionResult(False, f"You fail to disarm the trap and trigger it! You take {damage} damage from the mechanism.")
                
        except Exception as e:
            return ActionResult(False, f"Failed to disarm trap: {str(e)}")
    
    def handle_wait(self, *args) -> ActionResult:
        """Handle waiting/passing time with different duration options"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Wait how long? Options: quick (15min), short (30min), medium (1hr), long (3hr), extended (8hr)")
        
        duration_arg = args[0].lower()
        
        # Map duration arguments to hours (pure time passing, no activity effects)
        duration_map = {
            # Quick wait (15 minutes)
            "quick": 0.25,
            "15min": 0.25,
            "15": 0.25,
            
            # Short wait (30 minutes)
            "short": 0.5,
            "30min": 0.5,
            "30": 0.5,
            
            # Medium wait (1 hour)
            "medium": 1.0,
            "1hr": 1.0,
            "1h": 1.0,
            "1": 1.0,
            "hour": 1.0,
            
            # Long wait (3 hours)
            "long": 3.0,
            "3hr": 3.0,
            "3h": 3.0,
            "3": 3.0,
            
            # Extended wait (8 hours)
            "extended": 8.0,
            "8hr": 8.0,
            "8h": 8.0,
            "8": 8.0,
            "night": 8.0,
        }
        
        if duration_arg not in duration_map:
            available_options = ["quick (15min)", "short (30min)", "medium (1hr)", "long (3hr)", "extended (8hr)"]
            return ActionResult(False, f"Unknown duration '{duration_arg}'. Options: {', '.join(available_options)}")
        
        duration_hours = duration_map[duration_arg]
        
        try:
            # Use time system with "wait" activity (ensures condition effects are applied)
            if self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("wait", duration_override=duration_hours)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Wait interrupted."))
            
            # Format duration for display
            if duration_hours < 1:
                duration_str = f"{int(duration_hours * 60)} minutes"
            elif duration_hours == 1:
                duration_str = "1 hour"
            else:
                duration_str = f"{duration_hours} hours"
            
            # Create descriptive message based on duration
            if duration_hours <= 0.25:
                activity_desc = "take a brief moment to rest"
            elif duration_hours <= 0.5:
                activity_desc = "rest quietly for a short while"
            elif duration_hours <= 1:
                activity_desc = "rest comfortably for an hour"
            elif duration_hours <= 3:
                activity_desc = "rest deeply for several hours"
            else:
                activity_desc = "rest extensively through an extended period"
            
            message = f"You {activity_desc}, letting {duration_str} pass peacefully."
            
            # Add environmental context
            if self.game_engine.game_state.world_position.current_location_id:
                message += f"\nYou remain in the {self.game_engine.game_state.world_position.current_location_data.get('name', 'location')} during your rest."
            else:
                message += f"\nYou rest in the wilderness of hex {self.game_engine.game_state.world_position.hex_id}."
            
            return ActionResult(
                success=True,
                message=message,
                time_passed=duration_hours,
                action_type="wait"
            )
            
        except Exception as e:
            return ActionResult(False, f"Failed to wait: {str(e)}")