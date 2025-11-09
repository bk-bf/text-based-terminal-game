"""
Fantasy RPG - Action Handler (Refactored)

Thin coordinator that routes commands to specialized handlers using the registry pattern.
This file now serves as the main entry point, delegating to:
- MovementHandler: movement, look, enter, exit, wait
- CharacterHandler: inventory, character, rest, sleep
- ObjectInteractionHandler: examine, search, use, forage, harvest, chop, drink, unlock, etc.
- DebugHandler: debug, dump_*, save, load, help

CRITICAL REQUIREMENT: All actions that pass time MUST use the time system's perform_activity() method
to ensure condition effects (like damage from "Freezing") are properly applied during time passage.
Never set time_passed without calling the time system!

LOGGING ARCHITECTURE: Handlers return ActionResult with METADATA, not pre-formatted messages.
The UI calls action_logger.log_action_result() which logs command FIRST, then generates NLP
from metadata. This ensures correct chronology: "> command" appears before "Action message".
See .kiro/architecture/action-logging-pattern.md for full details.
"""

from .base_handler import ActionResult
from .handler_registry import ActionHandlerRegistry
from .movement_handler import MovementHandler
from .character_handler import CharacterHandler
from .object_interaction_handler import ObjectInteractionHandler
from .debug_handler import DebugHandler


class ActionHandler:
    """Main action handler that routes commands to specialized handlers via registry"""
    
    def __init__(self, character=None, player_state=None, game_engine=None):
        self.character = character
        self.player_state = player_state
        self.game_engine = game_engine
        
        # Create registry
        self.registry = ActionHandlerRegistry()
        
        # Instantiate specialized handlers
        self.movement_handler = MovementHandler(character, player_state, game_engine)
        self.character_handler = CharacterHandler(character, player_state, game_engine)
        self.object_handler = ObjectInteractionHandler(character, player_state, game_engine)
        self.debug_handler = DebugHandler(character, player_state, game_engine)
        
        # Register movement commands
        self.registry.register_handler(self.movement_handler, {
            "north": "handle_movement",
            "south": "handle_movement",
            "east": "handle_movement",
            "west": "handle_movement",
            "n": "handle_movement",
            "s": "handle_movement",
            "e": "handle_movement",
            "w": "handle_movement",
            "look": "handle_look",
            "l": "handle_look",
            "enter": "handle_enter_location",
            "exit": "handle_exit_location",
            "wait": "handle_wait",
            "wa": "handle_wait",  # 'w' is for west movement
        })
        
        # Register character commands
        self.registry.register_handler(self.character_handler, {
            "inventory": "handle_inventory",
            "i": "handle_inventory",
            "character": "handle_character",
            "c": "handle_character",
            "rest": "handle_rest",
            "r": "handle_rest",
            "equip": "handle_equip",
            "eq": "handle_equip",
            "unequip": "handle_unequip",
            "uneq": "handle_unequip",
        })
        
        # Register object interaction commands
        self.registry.register_handler(self.object_handler, {
            "examine": "handle_examine",
            "x": "handle_examine",
            "search": "handle_search",
            "a": "handle_search",
            "use": "handle_use",
            "u": "handle_use",
            "forage": "handle_forage",
            "g": "handle_forage",
            "harvest": "handle_harvest",
            "v": "handle_harvest",
            "chop": "handle_chop",
            "h": "handle_chop",
            "drink": "handle_drink",
            "b": "handle_drink",
            "unlock": "handle_unlock",
            "k": "handle_unlock",
            "disarm": "handle_disarm_trap",
            "light": "handle_light_fire",
            "f": "handle_light_fire",
        })
        
        # Register debug commands
        self.registry.register_handler(self.debug_handler, {
            "help": "handle_help",
            "?": "handle_help",
            "debug": "handle_debug",
            "dump_location": "handle_dump_location",
            "dump_hex": "handle_dump_hex",
            "dump_world": "handle_dump_world",
            "save": "handle_save_game",
            "load": "handle_load_game",
            "dump_log": "handle_save_log",
            "dump_history": "handle_dump_history",
            "research": "handle_research",
        })
        
        # Store current command for direction detection in movement handler
        self._current_command = ''
    
    def process_command(self, command_text: str) -> ActionResult:
        """
        Process a text command and return standardized result.
        
        Delegates to specialized handlers via the registry pattern.
        
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
        
        # Store current command for direction detection in movement handler
        self._current_command = command
        self.movement_handler._current_command = command
        
        # Route through registry
        result = self.registry.route_command(command, args)
        
        # Handle unknown commands
        if result is None:
            return ActionResult(
                success=False,
                message=f"Unknown command: '{command}'. Type 'help' for available commands."
            )
        
        return result
    
    def update_references(self, character=None, player_state=None, game_engine=None):
        """Update game object references - propagates to all handlers"""
        if character:
            self.character = character
        if player_state:
            self.player_state = player_state
        if game_engine:
            self.game_engine = game_engine
        
        # Update all handlers via registry
        self.registry.update_handlers(
            self.character,
            self.player_state,
            self.game_engine
        )
