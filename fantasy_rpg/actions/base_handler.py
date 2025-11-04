"""
Fantasy RPG - Base Action Handler

Base class for all action handlers with shared utilities and ActionResult class.
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
    
    @classmethod
    def from_time_result(cls, time_result: dict, success: bool = True, message: str = "", **extra_kwargs):
        """Create ActionResult from TimeSystem's perform_activity result
        
        This merges time_result data (condition_messages, debug_output) with ActionResult.
        
        Args:
            time_result: Dict returned from time_system.perform_activity()
            success: Action success status (overrides time_result if provided)
            message: Action message
            **extra_kwargs: Additional data to merge (overrides time_result if conflicts)
            
        Returns:
            ActionResult with all time data included
        """
        if not time_result:
            return cls(success, message, **extra_kwargs)
        
        # Extract time passed from time_result
        time_passed = time_result.get("duration_hours", 0.0)
        
        # Merge data using union operator: time_result first, then extra_kwargs (so extra_kwargs overrides)
        # Remove keys that conflict with ActionResult.__init__ parameters
        merged_data = {k: v for k, v in time_result.items() 
                      if k not in ('success', 'message', 'time_passed')} | extra_kwargs
        
        return cls(success, message, time_passed, **merged_data)


class BaseActionHandler:
    """Base class for all action handlers with shared utilities"""
    
    def __init__(self, character=None, player_state=None, game_engine=None):
        self.character = character
        self.player_state = player_state
        self.game_engine = game_engine
    
    def _require_location(self) -> Optional[ActionResult]:
        """Check if player is in a location (not overworld)
        
        Returns:
            ActionResult with error if not in location, None if validation passes
        """
        if not self.game_engine or not self.game_engine.is_initialized:
            return ActionResult(
                success=False,
                message="Game not initialized."
            )
        
        gs = self.game_engine.game_state
        if not gs or not gs.world_position.current_location_id:
            return ActionResult(
                success=False,
                message="You must be in a location to do that. Use 'enter' to enter a nearby location."
            )
        return None
    
    def _require_overworld(self) -> Optional[ActionResult]:
        """Check if player is in overworld (not in location)
        
        Returns:
            ActionResult with error if in location, None if validation passes
        """
        if not self.game_engine or not self.game_engine.is_initialized:
            return ActionResult(
                success=False,
                message="Game not initialized."
            )
        
        gs = self.game_engine.game_state
        if gs and gs.world_position.current_location_id:
            return ActionResult(
                success=False,
                message="You must exit the location first to travel the overworld."
            )
        return None
    
    def _parse_time_duration(self, time_str: str) -> Optional[float]:
        """Parse time duration string like '1h', '30m', '45min'
        
        Args:
            time_str: Time string to parse
            
        Returns:
            Duration in hours, or None if invalid
        """
        if not time_str:
            return None
        
        time_str = time_str.lower().strip()
        
        try:
            # Handle hours: 1h, 2.5h
            if time_str.endswith('h'):
                return float(time_str[:-1])
            
            # Handle minutes: 30m, 45min
            if time_str.endswith('min'):
                return float(time_str[:-3]) / 60.0
            if time_str.endswith('m'):
                return float(time_str[:-1]) / 60.0
            
            # Try parsing as plain number (assume hours)
            return float(time_str)
        except ValueError:
            return None
