"""
Debug utilities for testing and development.

Toggle debugging features here rather than scattered throughout the codebase.

## Usage

To enable shortkey debugging:
1. Set ENABLE_SHORTKEY_DEBUG = True
2. Run the game normally
3. Check `shortkey_debug.txt` in project root for detailed logs

The debug log will show:
- Object shortkey assignments from JSON data
- Command parsing with shortkey expansion
- Argument resolution (shortkey -> object name)

Example output:
```
=== OBJECT DEBUG OUTPUT ===
Object: Stone Fireplace
Shortkey: 'f'
...

=== PARSE COMMAND DEBUG ===
Original command: 'ex f'
Action: 'ex' -> 'examine'
Arguments: ['f']
  Arg 'f' -> lookup 'f' -> result: Stone Fireplace
Final expanded: examine ['Stone Fireplace']
```
"""

# DEBUG FLAGS - Set to True to enable debug logging
ENABLE_SHORTKEY_DEBUG = False  # Set to True to log shortkey parsing to shortkey_debug.txt

def log_shortkey_debug(message: str, mode: str = "a"):
    """
    Log shortkey debug information if debugging is enabled.
    
    Args:
        message: Debug message to log
        mode: File open mode ('w' for write, 'a' for append)
    """
    if not ENABLE_SHORTKEY_DEBUG:
        return
    
    with open("shortkey_debug.txt", mode) as f:
        f.write(message)
