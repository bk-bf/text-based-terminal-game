"""
Fantasy RPG - Input Controller

Handles all user input processing and coordinates with the action system.
This separates input handling from UI presentation.
"""

from typing import Dict, Any, Optional, Callable
from .action_handler import ActionHandler, ActionResult
from .action_logger import get_action_logger


class InputController:
    """
    Handles all user input and coordinates with game systems.
    The UI only needs to call process_input() and handle the response.
    """
    
    def __init__(self, character=None, player_state=None, time_system=None):
        self.character = character
        self.player_state = player_state
        self.time_system = time_system
        self.action_handler = None
        self.action_logger = get_action_logger()
        
        # UI callbacks - set by the UI system
        self.ui_callbacks = {
            'show_inventory': None,
            'show_character': None,
            'show_help': None,
            'update_location': None,
            'heal_character': None,
            'damage_character': None,
            'add_experience': None,
            'save_log': None,
            'clear_log': None,
            'quit_game': None,
            'log_message': None,
            'log_command': None,
            'refresh_display': None
        }
        
        # Debug commands that bypass the action system
        self.debug_commands = {
            'heal': self._handle_debug_heal,
            'h': self._handle_debug_heal,
            'damage': self._handle_debug_damage,
            'hurt': self._handle_debug_damage,
            'xp': self._handle_debug_xp,
            'experience': self._handle_debug_xp,
            'save': self._handle_save_log,
            'clear': self._handle_clear_log,
            'quit': self._handle_quit,
            'exit': self._handle_quit
        }
    
    def initialize(self, world_coordinator=None):
        """Initialize the input controller with game systems"""
        # Initialize action handler
        self.action_handler = ActionHandler(
            character=self.character,
            player_state=self.player_state,
            time_system=self.time_system
        )
        
        # Set world coordinator if available
        if world_coordinator:
            self.action_handler.set_world_coordinator(world_coordinator)
        
        # Set up action logger
        self.action_logger = get_action_logger()
    
    def set_ui_callback(self, callback_name: str, callback_func: Callable):
        """Set a UI callback function"""
        if callback_name in self.ui_callbacks:
            self.ui_callbacks[callback_name] = callback_func
    
    def process_input(self, command_text: str) -> Dict[str, Any]:
        """
        Process user input and return response for UI.
        
        Args:
            command_text: Raw command from user
            
        Returns:
            Dictionary with response data for UI to handle
        """
        if not command_text.strip():
            return {'type': 'error', 'message': 'Please enter a command.'}
        
        # Parse command
        parts = command_text.split()
        cmd = parts[0].lower() if parts else ""
        
        # Handle debug commands
        if cmd in self.debug_commands:
            return self.debug_commands[cmd](command_text)
        
        # Handle game actions through action system
        if not self.action_handler:
            return {'type': 'error', 'message': 'Action system not initialized.'}
        
        try:
            # Process through action handler
            result = self.action_handler.process_command(command_text)
            
            # Log the action result
            self.action_logger.log_action_result(
                result,
                character=self.character,
                command_text=command_text,
                player_state=self.player_state
            )
            
            # Convert action result to UI response
            return self._convert_action_result_to_ui_response(result, command_text)
            
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Error processing command: {str(e)}'
            }
    
    def _convert_action_result_to_ui_response(self, result: ActionResult, command_text: str) -> Dict[str, Any]:
        """Convert ActionResult to UI response format"""
        response = {
            'type': 'action_result',
            'success': result.success,
            'message': result.message,
            'time_passed': result.time_passed,
            'command': command_text
        }
        
        # Handle UI-specific actions
        if result.get('action_type') == 'ui_modal':
            modal_type = result.get('modal_type')
            response['type'] = 'show_modal'
            response['modal_type'] = modal_type
            
        elif result.get('action_type') == 'help':
            response['type'] = 'show_help'
            
        # Handle location updates
        elif result.get('movement_type') == 'overworld':
            destination = result.get('destination', {})
            hex_id = result.get('hex_id')
            if hex_id and destination:
                response['type'] = 'location_update'
                response['hex_id'] = hex_id
                response['location_name'] = destination.get('name', 'Unknown')
                response['elevation'] = destination.get('elevation', '320 ft')
        
        # Handle HP recovery
        elif result.get('hp_recovered'):
            hp_recovered = result.get('hp_recovered')
            if hp_recovered > 0:
                response['type'] = 'heal_character'
                response['amount'] = hp_recovered
                response['source'] = 'rest'
        
        # Add any additional data from the result
        response['result_data'] = result.data
        
        return response
    
    def _handle_debug_heal(self, command_text: str) -> Dict[str, Any]:
        """Handle debug heal command"""
        return {
            'type': 'debug_heal',
            'amount': 10,
            'command': command_text
        }
    
    def _handle_debug_damage(self, command_text: str) -> Dict[str, Any]:
        """Handle debug damage command"""
        return {
            'type': 'debug_damage',
            'amount': 5,
            'command': command_text
        }
    
    def _handle_debug_xp(self, command_text: str) -> Dict[str, Any]:
        """Handle debug XP command"""
        return {
            'type': 'debug_xp',
            'amount': 100,
            'command': command_text
        }
    
    def _handle_save_log(self, command_text: str) -> Dict[str, Any]:
        """Handle save log command"""
        # Parse command for custom filename
        parts = command_text.split()
        filename = None
        
        if len(parts) > 1:
            # Custom filename provided: "save my_adventure.txt"
            filename = " ".join(parts[1:])
            if not filename.endswith('.txt'):
                filename += '.txt'
        
        return {
            'type': 'save_log',
            'command': command_text,
            'filename': filename
        }
    
    def _handle_clear_log(self, command_text: str) -> Dict[str, Any]:
        """Handle clear log command"""
        return {
            'type': 'clear_log',
            'command': command_text
        }
    
    def _handle_quit(self, command_text: str) -> Dict[str, Any]:
        """Handle quit command"""
        return {
            'type': 'quit_game',
            'command': command_text
        }
    
    def get_help_text(self) -> str:
        """Get help text for display"""
        return """Available commands:

Character:
  inventory, i - View inventory and equipment
  character, c, sheet - View character sheet

System:
  heal - Heal 10 HP (debug)
  xp - Gain 100 XP (debug)
  save [filename] - Save game log to file (optional custom filename)
  clear - Clear game log
  quit, exit - Quit game
  help - Show this help text
"""
    
    def update_systems(self, character=None, player_state=None, time_system=None):
        """Update system references"""
        if character:
            self.character = character
        if player_state:
            self.player_state = player_state
        if time_system:
            self.time_system = time_system
        
        # Update action handler if it exists
        if self.action_handler:
            self.action_handler.character = self.character
            self.action_handler.player_state = self.player_state
            self.action_handler.time_system = self.time_system