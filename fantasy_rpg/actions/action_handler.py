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
    """Basic handler for working game actions only"""
    
    def __init__(self, character=None, player_state=None, time_system=None):
        self.character = character
        self.player_state = player_state
        self.time_system = time_system
        
        # Action registry - ONLY working features
        self.action_registry = {
            "inventory": self.handle_inventory,
            "i": self.handle_inventory,
            "character": self.handle_character,
            "c": self.handle_character,
            "sheet": self.handle_character,
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
        return ActionResult(
            success=True,
            message="Available commands:",
            time_passed=0.0,
            action_type="help"
        )