"""
Fantasy RPG - Basic Action Handler

Minimal action processing for only the features that actually work.
Currently supports: inventory and character sheet.
"""

from typing import Dict, Any, Optional, Tuple


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
            "take": self.handle_take,
            "use": self.handle_use,
            
            # Resource Gathering Actions (location only)
            "forage": self.handle_forage,
            "harvest": self.handle_forage,  # Alias for forage
            "gather": self.handle_forage,   # Alias for forage
            "pick": self.handle_forage,     # Alias for forage
            "chop": self.handle_chop,
            "cut": self.handle_chop,        # Alias for chop
            "drink": self.handle_drink,
            "water": self.handle_drink,     # Alias for drink
            "unlock": self.handle_unlock,
            "pick_lock": self.handle_unlock, # Alias for unlock
            
            # Rest and Recovery (location only)
            # TODO: might get scrapped for a separate Fatigue and Sleep tracker, 
            # Rest restores Fatigue but can be manually interupted, 
            # Sleep is random and Fatige/Sleep dependent, but recovers both 
            "rest": self.handle_rest,
            "sleep": self.handle_rest,  # Alias for rest
            
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
  enter - Enter a location in this hex
  exit - Exit current location to overworld
  
Object Interaction (location only):
  examine <object> - Examine an object closely
  search <object> - Search an object for items
  take <item> - Take an item and add to inventory
  use <object> - Use an object (context-specific)
  
Resource Gathering (location only):
  forage/harvest/gather/pick <object> - Gather food or materials (e.g., 'forage berry bush')
  chop/cut <object> - Chop wood from trees or objects (e.g., 'chop tree')
  drink/water <object> - Drink from water sources (e.g., 'drink well')
  unlock/pick_lock <object> - Pick locks on containers (e.g., 'unlock chest')
  
Rest & Recovery (location only):
  rest, sleep - Rest in current location (duration depends on fatigue)
  
Movement (overworld only):
  north, south, east, west (or n, s, e, w) - Move in that direction
  
Character:
  inventory, i - View your inventory
  character, c - View character sheet
  
System:
  heal - Heal 10 HP (debug)
  xp - Gain 100 XP (debug)
  save - Save game to save.json
  load - Load game from save.json
  dump_log [filename] - Save game log to file (optional custom filename)
  clear - Clear game log
  quit, exit - Quit game
  debug - Show debug information
  dump_location - Dump current location data to JSON file
  dump_hex - Dump current hex data to JSON file
  dump_world - Dump entire world data to JSON file
  save - Save game to save.json
  load - Load game from save.json
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
    
    def handle_take(self, *args) -> ActionResult:
        """Handle taking items from objects"""
        if not self.game_engine:
            return ActionResult(False, "Object interaction system not available.")
        
        if not args:
            return ActionResult(False, "Take what? Specify an item name.")
        
        item_name = " ".join(args).lower()
        
        try:
            success, message = self.game_engine.interact_with_object(item_name, "take")
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
        """
        MULTI-SKILL RISK/REWARD RESOURCE GATHERING SYSTEM
        
        Core Philosophy:
        - No "wrong" methods: Every interaction can yield something based on character build
        - Risk vs Consistency: High-reward methods have higher DCs and harsher failure penalties
        - Skill Synergy: Multiple skills work together (primary + secondary) for better results
        - Character Build Diversity: Different builds excel at different approaches
        
        Berry Bush Example - Multi-Skill Approaches:
        
        forage berry bush (Nature, DC 12) - HIGH RISK/HIGH REWARD
        - Success: 2-5 berries, Failure: 0 berries (harsh penalty)
        - Best for: Nature-focused characters willing to gamble
        
        search berry bush (Perception + Nature, DC 10) - MEDIUM RISK/MEDIUM REWARD  
        - Success: 1-3 berries, Failure: 0-1 berries (forgiving)
        - Best for: Balanced perception/nature builds
        
        examine berry bush (Perception, DC 8) - LOW RISK/LOW REWARD
        - Success: 1-2 berries, Failure: 0-1 berries (very forgiving)
        - Best for: Perception-focused characters wanting consistency
        
        chop berry bush (Athletics + Nature, DC 11) - ALTERNATIVE APPROACH
        - Success: 1 berry + 1-2 firewood, Failure: 0 (different reward type)
        - Best for: Strength-based characters wanting mixed resources
        
        Character Build Optimization:
        
        Nature Specialist (High Wisdom):
        - Excels at: forage (high reward), search (secondary skill bonus)
        - Strategy: Take calculated risks for maximum yield
        
        Perception Specialist (High Wisdom):
        - Excels at: examine (consistent), search (primary skill)  
        - Strategy: Reliable, steady resource gathering
        
        Strength Build (High Strength):
        - Excels at: chop (specialized), alternative approaches
        - Strategy: Focus on wood/mixed resources, different niche
        
        Balanced Build:
        - Excels at: search methods (uses multiple skills)
        - Strategy: Consistent medium yields across all resource types
        
        Strategic Benefits:
        1. Build Diversity: Different character builds have different optimal strategies
        2. Risk Management: Players choose their risk tolerance  
        3. Skill Investment: Investing in skills has clear mechanical benefits
        4. Experimentation: Players discover what works for their build
        5. No Dead Ends: Every approach can work with different risk/reward profiles
        """
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Forage what? Specify an object name (e.g., 'forage berry bush')")
        
        object_name = " ".join(args)
        
        try:
            # Find object using GameEngine coordination
            target_object = self._find_object_in_current_area(object_name)
            if not target_object:
                return ActionResult(False, f"You don't see any '{object_name}' here.")
            
            # Implement multi-skill forage logic here in ActionHandler
            success, message = self._handle_forage_interaction(target_object, "forage")
            return ActionResult(success, message)
        except Exception as e:
            return ActionResult(False, f"Failed to forage: {str(e)}")
    
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
        """Handle drinking from water sources"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Drink from what? Specify a water source (e.g., 'drink well')")
        
        object_name = " ".join(args)
        
        try:
            success, message = self.game_engine.interact_with_object(object_name, "drink")
            return ActionResult(success, message)
        except Exception as e:
            return ActionResult(False, f"Failed to drink: {str(e)}")
    
    def handle_unlock(self, *args) -> ActionResult:
        """Handle unlocking/lockpicking objects"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        if not args:
            return ActionResult(False, "Unlock what? Specify an object name (e.g., 'unlock chest')")
        
        object_name = " ".join(args)
        
        try:
            success, message = self.game_engine.interact_with_object(object_name, "unlock")
            return ActionResult(success, message)
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
    
    def _handle_forage_interaction(self, obj: Dict, interaction_type: str) -> Tuple[bool, str]:
        """
        Handle foraging interaction with multi-skill risk/reward system
        
        HIGH RISK/HIGH REWARD: Nature skill, DC 12, best yield but harsh failure
        - Success: 2-5 berries, Failure: 0 berries
        - Best for: Nature-focused characters willing to gamble
        """
        properties = obj.get("properties", {})
        
        # Check if object can be foraged
        if not properties.get("can_forage"):
            return False, f"You can't forage from the {obj.get('name', 'object')}."
        
        # Check if already depleted
        if obj.get("depleted", False):
            return False, f"The {obj.get('name')} has already been foraged recently."
        
        # Make skill check - HIGH RISK/HIGH REWARD approach
        import random
        roll = random.randint(1, 20)
        primary_skill, secondary_skill, dc = self._get_interaction_skill_and_dc("forage", obj.get("name", ""))
        skill_bonus = self._get_multi_skill_bonus(primary_skill, secondary_skill)
        total = roll + skill_bonus
        
        # Use time system (GameEngine coordination)
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("forage", duration_override=0.25)
            if not time_result.get("success", True):
                return False, time_result.get("message", "Foraging failed.")
        
        if total >= dc:
            # Success - generate items based on multi-skill system
            items_generated = self._generate_items_from_object(obj, "forage", total, dc)
            
            if items_generated:
                # Mark as depleted
                obj["depleted"] = True
                
                # Add items to inventory (GameEngine coordination)
                success_items = []
                failed_items = []
                
                gs = self.game_engine.game_state
                for item_id, quantity in items_generated.items():
                    if gs.character.add_item_to_inventory(item_id, quantity):
                        success_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                    else:
                        failed_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                
                result_msg = f"You successfully forage from the {obj.get('name')}."
                if success_items:
                    result_msg += f"\nYou gather: {', '.join(success_items)}"
                if failed_items:
                    result_msg += f"\nCouldn't carry: {', '.join(failed_items)} (inventory full)"
                
                return True, result_msg
            else:
                return True, f"You forage from the {obj.get('name')} but don't find much."
        else:
            # HARSH FAILURE for high-risk approach
            return False, f"You search the {obj.get('name')} but don't find anything useful."
    
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
        """Handle examining with LOW RISK/LOW REWARD approach"""
        properties = obj.get("properties", {})
        base_description = obj.get("description", "An unremarkable object.")
        
        # Make skill check - LOW RISK/LOW REWARD approach
        import random
        roll = random.randint(1, 20)
        primary_skill, secondary_skill, dc = self._get_interaction_skill_and_dc("examine", obj.get("name", ""))
        skill_bonus = self._get_multi_skill_bonus(primary_skill, secondary_skill)
        total = roll + skill_bonus
        
        # Examining takes a little time
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("look", duration_override=0.083)  # 5 minutes
            if not time_result.get("success", True):
                return False, time_result.get("message", "Examination failed.")
        
        if total >= dc:
            # Success - reveal additional information and potentially find items
            examination_text = properties.get("examination_text", "")
            
            # Check for items that can be found through examination
            items_generated = self._generate_items_from_object(obj, "examine", total, dc)
            
            result_msg = base_description
            if examination_text:
                result_msg += f"\n\nUpon closer examination: {examination_text}"
            else:
                result_msg += f"\n\nYou notice some interesting details about the {obj.get('name')}."
            
            # Add any items found during examination
            if items_generated:
                success_items = []
                failed_items = []
                
                gs = self.game_engine.game_state
                for item_id, quantity in items_generated.items():
                    if gs.character.add_item_to_inventory(item_id, quantity):
                        success_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                    else:
                        failed_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                
                if success_items:
                    result_msg += f"\n\nWhile examining, you also find: {', '.join(success_items)}"
                if failed_items:
                    result_msg += f"\nCouldn't carry: {', '.join(failed_items)} (inventory full)"
            
            return True, result_msg
        else:
            # VERY FORGIVING FAILURE for low-risk approach
            items_generated = self._generate_items_from_object(obj, "examine", total, dc)  # Still try to generate with negative margin
            if items_generated:
                success_items = []
                gs = self.game_engine.game_state
                for item_id, quantity in items_generated.items():
                    if gs.character.add_item_to_inventory(item_id, quantity):
                        success_items.append(f"{quantity}x {item_id.replace('_', ' ').title()}")
                
                if success_items:
                    return True, f"{base_description}\n\nYou also notice: {', '.join(success_items)}"
            
            return True, base_description
    
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