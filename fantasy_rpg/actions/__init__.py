"""
Fantasy RPG - Actions System

Unified action system that separates game mechanics from UI presentation.
All game actions are processed through the ActionHandler for consistency.
"""

from .action_handler import ActionHandler, ActionResult
from .action_logger import get_action_logger
from .input_controller import InputController

# Legacy action manager (deprecated - use ActionHandler instead)
try:
    from .action_manager import ActionManager
except ImportError:
    ActionManager = None

__all__ = [
    'ActionHandler',
    'ActionResult', 
    'get_action_logger',
    'InputController',
    'ActionManager'  # Legacy support
]