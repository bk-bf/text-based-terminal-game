"""
Fantasy RPG - Action Manager

Central coordinator for all game actions, separating mechanics from UI.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

try:
    from .movement_actions import MovementActions
    from .exploration_actions import ExplorationActions
    from .survival_actions import SurvivalActions
    from .character_actions import CharacterActions
except ImportError:
    from movement_actions import MovementActions
    from exploration_actions import ExplorationActions
    from survival_actions import SurvivalActions
    from character_actions import CharacterActions


class ActionType(Enum):
    """Types of actions available in the game"""
    # Movement
    MOVE_OVERWORLD = "move_overworld"      # Move between hexes (slow)
    MOVE_LOCATION = "move_location"        # Move between locations in hex (fast)
    ENTER_LOCATION = "enter_location"      # Enter hex from overworld
    EXIT_LOCATION = "exit_location"        # Exit to overworld
    
    # Exploration
    LOOK = "look"
    EXAMINE = "examine"
    SEARCH = "search"
    
    # Survival
    FORAGE = "forage"
    MAKE_CAMP = "make_camp"
    DETECT_SHELTER = "detect_shelter"
    REST = "rest"
    SLEEP = "sleep"
    
    # Character
    INVENTORY = "inventory"
    CHARACTER_SHEET = "character"
    EQUIP = "equip"
    UNEQUIP = "unequip"
    
    # Interaction
    INTERACT = "interact"
    USE_ITEM = "use_item"


@dataclass
class ActionResult:
    """Standardized result from any game action"""
    success: bool
    message: str
    time_passed_minutes: int = 0
    experience_gained: int = 0
    items_gained: List[str] = None
    items_lost: List[str] = None
    status_changes: Dict[str, Any] = None
    ui_updates: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.items_gained is None:
            self.items_gained = []
        if self.items_lost is None:
            self.items_lost = []
        if self.status_changes is None:
            self.status_changes = {}
        if self.ui_updates is None:
            self.ui_updates = {}


class ActionManager:
    """Central manager for all game actions"""
    
    def __init__(self, character, world_coordinator, time_system=None):
        self.character = character
        self.world_coordinator = world_coordinator
        self.time_system = time_system
        
        # Current game state
        self.current_hex = (0, 0)
        self.current_location = None
        self.in_location = False  # True if in micro-location, False if on overworld
        
        # Initialize action handlers
        self.movement = MovementActions(self)
        self.exploration = ExplorationActions(self)
        self.survival = SurvivalActions(self)
        self.character_actions = CharacterActions(self)
        
        print("ActionManager initialized")
    
    def execute_action(self, action_type: ActionType, **kwargs) -> ActionResult:
        """Execute any game action and return standardized result"""
        
        # Route to appropriate handler
        if action_type in [ActionType.MOVE_OVERWORLD, ActionType.MOVE_LOCATION, 
                          ActionType.ENTER_LOCATION, ActionType.EXIT_LOCATION]:
            return self.movement.handle_action(action_type, **kwargs)
        
        elif action_type in [ActionType.LOOK, ActionType.EXAMINE, ActionType.SEARCH]:
            return self.exploration.handle_action(action_type, **kwargs)
        
        elif action_type in [ActionType.FORAGE, ActionType.MAKE_CAMP, 
                            ActionType.DETECT_SHELTER, ActionType.REST, ActionType.SLEEP]:
            return self.survival.handle_action(action_type, **kwargs)
        
        elif action_type in [ActionType.INVENTORY, ActionType.CHARACTER_SHEET, 
                            ActionType.EQUIP, ActionType.UNEQUIP]:
            return self.character_actions.handle_action(action_type, **kwargs)
        
        else:
            return ActionResult(
                success=False,
                message=f"Unknown action type: {action_type.value}"
            )
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get list of currently available actions based on game state"""
        actions = []
        
        # Always available actions
        actions.extend([
            {"action": ActionType.LOOK, "command": "look", "description": "Look around"},
            {"action": ActionType.INVENTORY, "command": "inventory", "description": "Check inventory"},
            {"action": ActionType.CHARACTER_SHEET, "command": "character", "description": "View character sheet"}
        ])
        
        # Context-sensitive actions
        if self.in_location:
            # In micro-location
            actions.extend([
                {"action": ActionType.MOVE_LOCATION, "command": "go <direction>", "description": "Move to another location"},
                {"action": ActionType.EXIT_LOCATION, "command": "exit", "description": "Return to overworld"},
                {"action": ActionType.EXAMINE, "command": "examine <object>", "description": "Examine an object"},
                {"action": ActionType.FORAGE, "command": "forage <object>", "description": "Forage from object"},
                {"action": ActionType.INTERACT, "command": "interact <object>", "description": "Interact with object"}
            ])
        else:
            # On overworld
            actions.extend([
                {"action": ActionType.MOVE_OVERWORLD, "command": "go <direction>", "description": "Travel to adjacent hex"},
                {"action": ActionType.ENTER_LOCATION, "command": "enter", "description": "Enter hex location"}
            ])
        
        # Survival actions (available everywhere)
        actions.extend([
            {"action": ActionType.DETECT_SHELTER, "command": "shelter", "description": "Look for shelter"},
            {"action": ActionType.MAKE_CAMP, "command": "camp", "description": "Make camp"},
            {"action": ActionType.REST, "command": "rest", "description": "Take a short rest"},
            {"action": ActionType.SLEEP, "command": "sleep", "description": "Sleep for the night"}
        ])
        
        return actions
    
    def parse_command(self, command_text: str) -> Tuple[ActionType, Dict[str, Any]]:
        """Parse text command into action type and parameters"""
        parts = command_text.lower().strip().split()
        if not parts:
            return None, {}
        
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Movement commands
        if command in ["go", "move", "travel"]:
            if args:
                direction = args[0]
                if self.in_location:
                    return ActionType.MOVE_LOCATION, {"direction": direction}
                else:
                    return ActionType.MOVE_OVERWORLD, {"direction": direction}
        
        elif command in ["enter", "explore"]:
            return ActionType.ENTER_LOCATION, {}
        
        elif command in ["exit", "leave", "return"]:
            return ActionType.EXIT_LOCATION, {}
        
        # Exploration commands
        elif command in ["look", "l"]:
            return ActionType.LOOK, {}
        
        elif command in ["examine", "ex", "inspect"]:
            target = " ".join(args) if args else ""
            return ActionType.EXAMINE, {"target": target}
        
        elif command in ["search"]:
            return ActionType.SEARCH, {}
        
        # Survival commands
        elif command in ["forage", "gather"]:
            target = " ".join(args) if args else ""
            return ActionType.FORAGE, {"target": target}
        
        elif command in ["camp", "makecamp"]:
            return ActionType.MAKE_CAMP, {}
        
        elif command in ["shelter"]:
            return ActionType.DETECT_SHELTER, {}
        
        elif command in ["rest"]:
            return ActionType.REST, {}
        
        elif command in ["sleep"]:
            return ActionType.SLEEP, {}
        
        # Character commands
        elif command in ["inventory", "inv", "i"]:
            return ActionType.INVENTORY, {}
        
        elif command in ["character", "char", "stats"]:
            return ActionType.CHARACTER_SHEET, {}
        
        elif command in ["equip"]:
            item = " ".join(args) if args else ""
            return ActionType.EQUIP, {"item": item}
        
        elif command in ["unequip", "remove"]:
            slot = " ".join(args) if args else ""
            return ActionType.UNEQUIP, {"slot": slot}
        
        # Interaction commands
        elif command in ["interact", "use"]:
            target = " ".join(args) if args else ""
            return ActionType.INTERACT, {"target": target}
        
        return None, {}
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current game context for UI updates"""
        context = {
            "current_hex": self.current_hex,
            "in_location": self.in_location,
            "current_location": self.current_location,
            "character": self.character
        }
        
        if self.in_location and self.current_location:
            # Add location-specific context
            context["location_objects"] = getattr(self.current_location, 'objects', [])
            context["location_exits"] = getattr(self.current_location, 'exits', {})
        else:
            # Add overworld context
            hex_data = self.world_coordinator.get_hex_complete_data(self.current_hex)
            context["hex_data"] = hex_data
            context["available_locations"] = self.world_coordinator.get_explorable_locations(self.current_hex)
        
        return context


def test_action_manager():
    """Test the action manager system"""
    print("=== Testing Action Manager ===")
    
    # Create mock objects
    class MockCharacter:
        def __init__(self):
            self.name = "Test Character"
    
    class MockWorldCoordinator:
        def get_hex_complete_data(self, coords):
            return {"biome": "forest", "terrain": "dense"}
        
        def get_explorable_locations(self, coords):
            return []
    
    character = MockCharacter()
    world_coordinator = MockWorldCoordinator()
    
    # Create action manager
    manager = ActionManager(character, world_coordinator)
    
    # Test command parsing
    test_commands = [
        "look",
        "go north", 
        "enter",
        "forage berry bush",
        "inventory",
        "examine altar",
        "camp"
    ]
    
    print("Testing command parsing:")
    for command in test_commands:
        action_type, params = manager.parse_command(command)
        if action_type:
            print(f"  '{command}' -> {action_type.value} {params}")
        else:
            print(f"  '{command}' -> Unknown command")
    
    # Test available actions
    print(f"\nAvailable actions (overworld): {len(manager.get_available_actions())}")
    
    manager.in_location = True
    print(f"Available actions (in location): {len(manager.get_available_actions())}")
    
    print("✓ Action manager test complete!")
    return manager


if __name__ == "__main__":
    test_action_manager()