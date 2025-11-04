"""
Fantasy RPG - Action Handler Registry

Central registry for routing commands to appropriate handler classes.
Enables pluggable handler system for Phase 4 extensions (social, quests, research).
"""

from typing import Dict, Callable, Optional
from .base_handler import ActionResult


class ActionHandlerRegistry:
    """Registry for routing commands to specialized handlers"""
    
    def __init__(self):
        # Command -> handler_method mapping
        self._registry: Dict[str, Callable] = {}
        
        # Handler instances for lifecycle management
        self._handlers = []
    
    def register_handler(self, handler_instance, commands: Dict[str, str]):
        """Register a handler and its command mappings
        
        Args:
            handler_instance: Instance of a handler class (must have methods returning ActionResult)
            commands: Dict mapping command_name -> handler_method_name
                     e.g., {"move": "handle_movement", "n": "handle_movement"}
        """
        self._handlers.append(handler_instance)
        
        for command, method_name in commands.items():
            method = getattr(handler_instance, method_name, None)
            if method is None:
                raise ValueError(f"Handler {handler_instance.__class__.__name__} missing method {method_name}")
            
            # Allow override - useful for debug/test handlers
            self._registry[command] = method
    
    def route_command(self, command: str, args: list) -> Optional[ActionResult]:
        """Route a command to the appropriate handler
        
        Args:
            command: Command name (lowercase)
            args: Command arguments
            
        Returns:
            ActionResult from handler, or None if command not found
        """
        handler = self._registry.get(command)
        if handler is None:
            return None
        
        try:
            return handler(*args)
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error executing {command}: {str(e)}"
            )
    
    def has_command(self, command: str) -> bool:
        """Check if a command is registered"""
        return command in self._registry
    
    def get_all_commands(self) -> list:
        """Get list of all registered commands"""
        return sorted(self._registry.keys())
    
    def get_handler(self, handler_name: str):
        """Get a registered handler instance by name
        
        Args:
            handler_name: Name of the handler class (lowercase, without 'Handler' suffix)
                         e.g., 'character' for CharacterHandler, 'movement' for MovementHandler
        
        Returns:
            Handler instance or None if not found
        """
        for handler in self._handlers:
            class_name = handler.__class__.__name__.lower()
            # Match both 'character' and 'characterhandler'
            if class_name == f"{handler_name}handler" or class_name == handler_name:
                return handler
        return None
    
    def update_handlers(self, character=None, player_state=None, game_engine=None):
        """Update all registered handlers with new state references
        
        Called when game state changes (e.g., after load)
        """
        for handler in self._handlers:
            if hasattr(handler, 'character'):
                handler.character = character
            if hasattr(handler, 'player_state'):
                handler.player_state = player_state
            if hasattr(handler, 'game_engine'):
                handler.game_engine = game_engine
