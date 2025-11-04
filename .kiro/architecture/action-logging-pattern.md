# Action Logging Architecture Pattern

## Problem Statement
Message chronology was inconsistent across different actions. Equipment messages appeared AFTER commands worked correctly, but object interaction messages appeared BEFORE commands.

## Root Cause
Two different logging approaches were being used:
1. **Correct**: Handlers return metadata → UI logs through `action_logger.log_action_result()` → Command first, message second ✓
2. **Incorrect**: Systems call `action_logger` directly → Message appears immediately → Command logged later ❌

## The Correct Pattern

### Flow Diagram
```
User Input → Handler → ActionResult (with metadata) → UI → action_logger.log_action_result()
                                                              ↓
                                                    1. Log command ("> search chest")
                                                    2. Call _log_main_result()
                                                    3. Generate NLP from metadata
                                                    4. Log message ("You find treasure")
```

### Implementation Steps

#### 1. Handler Returns Metadata (NOT messages)
```python
def handle_search(self, *args) -> ActionResult:
    # Perform action logic
    success, items_found, object_name = do_search_logic()
    
    # Return metadata, NOT pre-generated messages
    return ActionResult(
        success=success,
        message="",  # Empty - let ActionLogger generate NLP
        time_passed=0.1,
        search_result=success,
        object_name=object_name,
        items_found=items_found
    )
```

#### 2. UI Calls log_action_result()
```python
result = handler.handle_search(args)

action_logger.log_action_result(
    result,
    character=character,
    command_text="search chest",  # CRITICAL: Must provide command text
    player_state=player_state
)
```

#### 3. ActionLogger Generates NLP from Metadata
```python
def _log_main_result(self, action_result):
    # Check for metadata keys
    if action_result.get('search_result'):
        object_name = action_result.get('object_name')
        items_found = action_result.get('items_found', [])
        
        if items_found:
            self.log_action_event("search_success", object_name=object_name)
        else:
            self.log_action_event("search_empty", object_name=object_name)
    
    # Items are logged separately as factual info
    if items_found:
        self.game_log.add_message(f"You find: {', '.join(items_found)}")
```

## Result: Correct Chronology
```
> search chest
Success! The chest contains valuables.
You find: 2x Gold Coin, 1x Healing Potion
```

NOT:
```
Success! The chest contains valuables.
You find: 2x Gold Coin, 1x Healing Potion
> search chest
```

## Metadata Keys Convention

### Equipment
- `item_equipped` / `item_unequipped`: Item name
- `item_type`: "weapon", "armor", "shield"
- `slot`: Equipment slot name

### Object Interactions
- `search_result`: bool (success/failure)
- `forage_result`: bool
- `harvest_result`: bool
- `object_name`: Name of object interacted with
- `items_found`: List of item names/quantities

### Combat (Future)
- `combat_action`: "attack", "defend", "spell"
- `target`: Enemy name
- `damage_dealt`: Number
- `hit_roll`: Dice result
- `critical_hit`: bool

## Systems That Need Refactoring

### ✅ Fixed
- **CharacterHandler**: Equipment events use metadata pattern

### ❌ Needs Fix
- **ObjectInteractionSystem** (`fantasy_rpg/game/object_interaction_system.py`):
  - Currently calls `action_logger.log_action_event()` directly on lines 117, 125, 141, 149, 194, 209, 224, 229
  - Should return structured data instead
  - See TODO comment at top of file

## Adding New Action Types

1. **Define metadata keys** in handler return value
2. **Add handling** in `action_logger._log_main_result()` (line 160)
3. **NEVER call `action_logger` directly** from game systems
4. **Always provide `command_text`** when calling `log_action_result()`

## Benefits
- **Consistent chronology**: Commands always appear before messages
- **Centralized NLP**: All natural language generation in one place
- **Testable**: Systems return data, not pre-formatted strings
- **Future-proof**: Adding combat/crafting/etc follows same pattern
