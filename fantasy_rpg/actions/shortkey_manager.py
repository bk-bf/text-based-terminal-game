"""
Fantasy RPG - Shortkey Manager

Manages shortkeys for actions and dynamic object shortcuts in the current location.
Provides a seamless UX where every action and object can be referenced with minimal typing.
"""

from typing import Dict, List, Optional, Tuple
import string


class ShortkeyManager:
    """Manages action shortcuts and dynamic object shortcuts"""
    
    # Action shortcuts - permanent mappings (using first letter, or first 2 letters if conflict)
    ACTION_SHORTCUTS = {
        # Navigation (first letter)
        'n': 'north',
        's': 'south',
        'e': 'east',
        'w': 'west',
        'en': 'enter',
        'et': 'exit',
        
        # Character (first letter)
        'i': 'inventory',
        'c': 'character',
        'm': 'map',
        
        # Core actions (first letter)
        'l': 'look',
        'h': 'help',
        'q': 'quit',
        '?': 'help',
        
        # Interaction (first letter where possible, 2 letters for conflicts)
        'ex': 'examine',     # 'e' taken by east
        'x': 'examine',      # Also allow x
        't': 'take',
        'd': 'drop',
        'u': 'use',
        'o': 'open',
        
        # Resource gathering (first letter where possible)
        'f': 'forage',
        'ha': 'harvest',     # 'h' taken by help
        'ch': 'chop',        # 'c' taken by character
        'cu': 'cut',         # Alternative to chop
        'dr': 'drink',       # 'd' taken by drop
        'b': 'drink',        # Also allow b (beverage)
        
        # Object actions (first letter where possible)
        'un': 'unlock',      # 'u' taken by use
        'k': 'unlock',       # Also allow k (key)
        'li': 'light',       # 'l' taken by look
        'se': 'search',      # 's' taken by south
        'a': 'search',       # Also allow a
        'di': 'disarm',      # 'd' taken by drop
        'cl': 'climb',       # 'c' taken by character
        'pl': 'place',       # 'p' conflicts with sleep
        're': 'repair',      # 'r' conflicts with rest
        
        # Rest actions (first letter)
        'r': 'rest',
        'p': 'sleep',        # p for pillow/bed
        'wa': 'wait',        # 'w' taken by west
        'v': 'wait',         # Also allow v
    }
    
    # Reverse mapping for display
    REVERSE_SHORTCUTS = {v: k for k, v in ACTION_SHORTCUTS.items()}
    
    def __init__(self):
        """Initialize shortkey manager"""
        # Object shortcuts (from JSON data, permanent per object type)
        self.object_shortcuts: Dict[str, str] = {}  # shortkey -> object_name
        self.object_reverse: Dict[str, str] = {}    # object_name -> shortkey
    
    def assign_object_shortcuts_from_data(self, objects: List[Dict]) -> Dict[str, str]:
        """
        Build shortkey mappings from object data (with permanent shortkeys from JSON).
        
        Args:
            objects: List of object dictionaries from location data
            
        Returns:
            Dictionary mapping object_name -> shortkey
        """
        self.object_shortcuts.clear()
        self.object_reverse.clear()
        
        for obj in objects:
            obj_name = obj.get("name", "Unknown")
            shortkey = obj.get("shortkey", "")
            
            if shortkey:
                self.object_shortcuts[shortkey] = obj_name
                self.object_reverse[obj_name] = shortkey
        
        return self.object_reverse
    
    def get_object_shortkey(self, object_name: str) -> Optional[str]:
        """Get shortkey for an object name"""
        return self.object_reverse.get(object_name)
    
    def get_object_from_shortkey(self, shortkey: str) -> Optional[str]:
        """Get object name from shortkey"""
        return self.object_shortcuts.get(shortkey)
    
    def parse_command(self, command_str: str) -> Tuple[str, List[str]]:
        """
        Parse command string, expanding both action and object shortcuts.
        
        Returns:
            Tuple of (expanded_action, [expanded_args])
        """
        parts = command_str.strip().split()
        
        if not parts:
            return ("", [])
        
        # Only lowercase the action part for matching
        first = parts[0].lower()
        rest = parts[1:]
        
        # Check if first part is an action shortkey
        action = self.ACTION_SHORTCUTS.get(first, first)
        
        # DEBUG: Write shortkey mappings to file
        with open("shortkey_debug.txt", "a") as f:
            f.write("\n=== PARSE COMMAND DEBUG ===\n")
            f.write(f"Original command: '{command_str}'\n")
            f.write(f"Action: '{first}' -> '{action}'\n")
            f.write(f"Arguments: {rest}\n")
            f.write(f"Current object_shortcuts: {self.object_shortcuts}\n")
        
        # Process arguments - expand object shortcuts (keep original case for lookup)
        expanded_args = []
        for arg in rest:
            # Check if arg is an object shortkey (case-sensitive for shortkeys)
            obj_name = self.object_shortcuts.get(arg.lower())  # Shortkeys are lowercase
            
            # DEBUG
            with open("shortkey_debug.txt", "a") as f:
                f.write(f"  Arg '{arg}' -> lookup '{arg.lower()}' -> result: {obj_name}\n")
            
            if obj_name:
                expanded_args.append(obj_name)
            else:
                expanded_args.append(arg)
        
        # DEBUG final result
        with open("shortkey_debug.txt", "a") as f:
            f.write(f"Final expanded: {action} {expanded_args}\n")
            f.write("-" * 50 + "\n")
        
        return (action, expanded_args)
    
    def format_object_with_shortkey(self, object_name: str) -> str:
        """
        Format object name with its shortkey for display.
        
        Args:
            object_name: Name of the object
            
        Returns:
            Formatted string like "Stone Fireplace [f]"
        """
        shortkey = self.get_object_shortkey(object_name)
        if shortkey:
            return f"{object_name} [{shortkey}]"
        return object_name
    
    def get_action_help(self) -> str:
        """Get formatted help text for action shortcuts"""
        lines = ["=== ACTION SHORTCUTS ==="]
        lines.append("")
        lines.append("NAVIGATION:")
        lines.append("  n/s/e/w - Move north/south/east/west")
        lines.append("  en - Enter location")
        lines.append("  et - Exit location")
        lines.append("")
        lines.append("CHARACTER:")
        lines.append("  i - Inventory")
        lines.append("  c - Character sheet")
        lines.append("  m - Map")
        lines.append("")
        lines.append("INTERACTION:")
        lines.append("  l - Look around")
        lines.append("  ex/x [obj] - Examine object")
        lines.append("  t [obj] - Take/pickup object")
        lines.append("  d [obj] - Drop object")
        lines.append("  u [obj] - Use object")
        lines.append("  o [obj] - Open object")
        lines.append("")
        lines.append("RESOURCE GATHERING:")
        lines.append("  f [obj] - Forage/gather")
        lines.append("  ha [obj] - Harvest from object")
        lines.append("  ch [obj] - Chop wood")
        lines.append("  dr/b [obj] - Drink from object")
        lines.append("")
        lines.append("OBJECT ACTIONS:")
        lines.append("  un/k [obj] - Unlock object")
        lines.append("  li [obj] - Light fire")
        lines.append("  se/a [obj] - Search object")
        lines.append("  di [obj] - Disarm trap")
        lines.append("  cl [obj] - Climb object")
        lines.append("  pl [obj] - Place item")
        lines.append("  re [obj] - Repair object")
        lines.append("")
        lines.append("REST:")
        lines.append("  r - Rest")
        lines.append("  p - Sleep")
        lines.append("  wa/v [time] - Wait (1h, 3h, 8h)")
        lines.append("")
        lines.append("OTHER:")
        lines.append("  h/? - This help")
        lines.append("  q - Quit")
        lines.append("")
        lines.append("OBJECT SHORTCUTS:")
        lines.append("  Objects have permanent shortcuts shown in brackets")
        lines.append("  Example: 'li fp' lights the fireplace [fp]")
        lines.append("  Example: 'dr we' drinks from the well [we]")
        lines.append("")
        return "\n".join(lines)


# Global shortkey manager instance
_shortkey_manager = None


def get_shortkey_manager() -> ShortkeyManager:
    """Get the global shortkey manager instance"""
    global _shortkey_manager
    if _shortkey_manager is None:
        _shortkey_manager = ShortkeyManager()
    return _shortkey_manager


def test_shortkey_manager():
    """Test the shortkey manager"""
    print("=== Testing Shortkey Manager ===\n")
    
    manager = ShortkeyManager()
    
    # Test 1: Object shortkey assignment from data
    print("1. Testing object shortkey assignment from data:")
    objects = [
        {"name": "Stone Fireplace", "shortkey": "fp"},
        {"name": "Old Well", "shortkey": "we"},
        {"name": "Wooden Table", "shortkey": "tb"},
        {"name": "Berry Bush", "shortkey": "bb"},
        {"name": "Treasure Chest", "shortkey": "tc"}
    ]
    shortcuts = manager.assign_object_shortcuts_from_data(objects)
    
    for obj_name, key in shortcuts.items():
        formatted = manager.format_object_with_shortkey(obj_name)
        print(f"  {formatted}")
    print()
    
    # Test 2: Command parsing with shortcuts
    print("2. Testing command parsing:")
    test_commands = [
        "i",           # inventory
        "l",           # look
        "li fp",       # light fireplace [fp]
        "dr we",       # drink from well [we]
        "x stone fireplace",  # examine by full name
        "se tc",       # search treasure chest [tc]
        "n",           # move north
        "ex tb",       # examine table [tb]
    ]
    
    for cmd in test_commands:
        action, args = manager.parse_command(cmd)
        print(f"  '{cmd}' -> action: '{action}', args: {args}")
    print()
    
    # Test 3: Reverse lookup
    print("3. Testing reverse lookup:")
    print(f"  Shortkey for 'Stone Fireplace': {manager.get_object_shortkey('Stone Fireplace')}")
    print(f"  Object for shortkey 'we': {manager.get_object_from_shortkey('we')}")
    print()
    
    # Test 4: Help text
    print("4. Action shortcuts help:")
    print(manager.get_action_help())
    
    print("\n=== Tests Complete ===")


if __name__ == "__main__":
    test_shortkey_manager()
