# Shortkey System - Complete Implementation

## Overview

The shortkey system provides seamless UX by allowing every action and object to be referenced with minimal typing. Players can use 1-2 letter commands for actions and permanent 2-letter shortcuts for objects defined in JSON.

## Architecture

### Components

1. **ShortkeyManager** (`actions/shortkey_manager.py`)
   - Manages permanent action shortcuts (40+ mappings)
   - Builds object shortkey mappings from location data
   - Parses commands and expands shortcuts
   - Singleton pattern via `get_shortkey_manager()`

2. **InputController** (`actions/input_controller.py`)
   - Updates shortcuts BEFORE parsing every command
   - Expands shortcuts via ShortkeyManager
   - Passes expanded commands to ActionHandler

3. **GameEngine** (`game/game_engine.py`)
   - Formats location contents with object shortcuts
   - Displays objects as: `Object Name [shortkey]`

4. **WorldCoordinator** (`world/world_coordinator.py`)
   - Converts GameObject instances to dicts (includes shortkey field)
   - Preserves shortcuts through save/load cycle

5. **LocationGenerator** (`locations/location_generator.py`)
   - GameObject dataclass has `shortkey` field
   - Copies shortkey from JSON when creating objects

6. **Data Files** (`data/objects.json`)
   - Each object has permanent `"shortkey": "xx"` field
   - Shortcuts assigned manually (2-letter codes)

## Usage Examples

### Action Shortcuts

```
# Navigation (1 letter)
n/s/e/w    → north/south/east/west
en/et      → enter/exit

# Character (1 letter)
i          → inventory
c          → character
m          → map

# Core (1 letter)
l          → look
h          → help
q          → quit

# Interactions (2 letters)
ex         → examine
ha         → harvest
ch         → chop
dr         → drink
un         → unlock
li         → light
se         → search
di         → disarm
cl         → climb
pl         → place
re         → rest
wa         → wait
```

### Object Shortcuts (Permanent from JSON)

When you enter a location:
```
You notice Stone Fireplace [fp], Old Well [we], Wooden Table [tb], Berry Bush [bb].
```

Quick interactions:
```
li fp     → light fireplace
dr we     → drink well
ex tb     → examine wooden table
ha bb     → harvest berry bush
```

### Combined Examples

```
Command    Expands To
-------    ----------
i          inventory
l          look
li fp      light Stone Fireplace
dr we      drink Old Well
ex tb      examine Wooden Table
ha bb      harvest Berry Bush
se tc      search Treasure Chest
ch fl      chop Fallen Log
```

## Implementation Details

### Action Shortkeys (Permanent)

```python
ACTION_SHORTCUTS = {
    # Navigation (first letter)
    'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
    'en': 'enter', 'et': 'exit',
    
    # Character (first letter)
    'i': 'inventory', 'c': 'character', 'm': 'map',
    
    # Core actions (first letter)
    'l': 'look', 'h': 'help', 'q': 'quit',
    
    # Interactions (2 letters to avoid conflicts)
    'ex': 'examine', 'ha': 'harvest', 'ch': 'chop', 'dr': 'drink',
    'un': 'unlock', 'li': 'light', 'se': 'search', 'di': 'disarm',
    'cl': 'climb', 'pl': 'place', 're': 'rest', 'wa': 'wait',
}
```

### Object Shortkeys (Permanent from JSON)

**Structure** (`data/objects.json`):
```json
{
  "fireplace": {
    "name": "Stone Fireplace",
    "shortkey": "fp",
    "description": "...",
    "interactive": true,
    "properties": {...}
  }
}
```

**Common Shortcuts**:
- `fp` - Fireplace (various types)
- `we` - Well (various types)
- `bd` - Bed
- `tb` - Table
- `wp` - Woodpile
- `bb` - Berry Bush
- `tc` - Treasure Chest
- `sa` - Stone Altar
- `rc` - Root Cellar
- `bf` - Broken Fence
- `cb` - Chopping Block
- `ba` - Barrel
- `fl` - Fallen Log

### Command Parsing Flow

```
User Input: "li fp"
    ↓
InputController._update_current_location_shortcuts()
    → Loads objects from current area
    → Calls shortkey_manager.assign_object_shortcuts_from_data(objects)
    → Builds mapping: {"fp": "Stone Fireplace", "we": "Old Well", ...}
    ↓
ShortkeyManager.parse_command("li fp")
    → Expands action: "li" → "light"
    → Expands object: "fp" → "Stone Fireplace"
    → Returns: ("light", ["Stone Fireplace"])
    ↓
InputController reconstructs: "light Stone Fireplace"
    ↓
ActionHandler.process_command("light Stone Fireplace")
    ↓
Result displayed to player
```

### Object Display Flow

```
Player types: "look"
    ↓
ActionHandler.handle_look()
    ↓
GameEngine.get_location_contents()
    → Reads objects from location_data["areas"]["entrance"]["objects"]
    → Each object dict has: {"name": "...", "shortkey": "fp", ...}
    → Formats: "Stone Fireplace [fp]"
    ↓
Display: "You notice Stone Fireplace [fp], Old Well [we], Wooden Table [tb]..."
```

### Data Flow (GameObject → Dict)

```
JSON Template (objects.json)
    ↓ LocationGenerator reads template
GameObject(name="Stone Fireplace", shortkey="fp", ...)
    ↓ Stored in Area.objects list
WorldCoordinator._convert_objects_to_dict()
    → Extracts: id, name, shortkey, description, interactive, properties, item_drops
    → Creates dict with ALL fields including shortkey
    ↓
Saved to location_data["areas"]["entrance"]["objects"]
    ↓
GameEngine reads dict when displaying contents
```

## Benefits

### For Players

- **Minimal Typing**: `li fp` instead of `light stone fireplace`
- **No Memorization**: Objects show their shortcuts in brackets
- **Intuitive**: Shortcuts often match object type (fp=fireplace, we=well)
- **Consistent**: Same object type always has same shortcut
- **Fast Exploration**: Quick object interaction without typing full names
- **Flexible**: Can still use full names if preferred

### For Developers

- **Data-Driven**: Shortcuts defined once in JSON
- **Centralized**: All shortkey logic in ShortkeyManager
- **Persistent**: Shortcuts survive save/load
- **Extensible**: Easy to add new action/object shortcuts
- **Maintainable**: Single source of truth per object type
- **Type-Safe**: GameObject dataclass includes shortkey field

## Testing

Test shortkey manager directly:
```bash
python fantasy_rpg/actions/shortkey_manager.py
```

Test in-game:
1. Start game: `python play.py`
2. Create/load character
3. Enter location: `en` (if near one) or walk around
4. View objects with shortcuts: `l`
5. Try quick commands: `li fp`, `dr we`, `ex tb`
6. Check help: `h` or `help`

Debug shortcuts:
- File `shortkey_debug.txt` logs object data and parse operations
- Shows: object names, shortkeys, dict keys, command expansions
- Created/appended on `look` command and command parsing

## Edge Cases Handled

1. **Missing shortkey in JSON**: Uses empty string, object won't have shortcut in UI
2. **Duplicate shortcuts**: Last object with same shortkey wins (avoid in JSON)
3. **Location changes**: Shortcuts update automatically before each command
4. **Multiple instances**: Same object type (e.g., "Broken Fence") shares shortkey
5. **Fallback**: If shortkey system fails, full names still work
6. **Case sensitivity**: Shortcuts are case-insensitive (`FP` = `fp`)

## Future Enhancements

- [ ] Validation script to check for duplicate shortcuts in JSON
- [ ] Auto-suggest shortcuts when examining objects
- [ ] Shortkey autocomplete in UI
- [ ] Item shortcuts (separate namespace from objects)
- [ ] Shortkey remapping for accessibility
- [ ] Multi-character shortcuts for objects (3+ letters)

## Known Issues

**FIXED**:
- ✅ Shortcuts not displaying in UI (WorldCoordinator missing shortkey field)
- ✅ Commands not recognizing shortcuts (shortcuts updated after parse)
- ✅ Empty object_shortcuts dict (shortcuts loaded too late in flow)

**Current**:
- None
