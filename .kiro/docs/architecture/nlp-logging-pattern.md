# NLP Logging Architecture Pattern

## Overview
This document describes the complete Natural Language Processing (NLP) and message logging architecture implemented in Phase 3.7. It covers both the metadata-driven logging pattern for correct message chronology and the centralized NLP message variance system.

---

## Part 1: Message Chronology Architecture

### Problem Statement
Message chronology was inconsistent across different actions. Equipment messages appeared AFTER commands worked correctly, but object interaction messages appeared BEFORE commands.

### Root Cause
Two different logging approaches were being used:
1. **Correct**: Handlers return metadata → UI logs through `action_logger.log_action_result()` → Command first, message second ✓
2. **Incorrect**: Systems call `action_logger` directly → Message appears immediately → Command logged later ❌

### The Correct Pattern

#### Flow Diagram
```
User Input → Handler → ActionResult (with metadata) → UI → action_logger.log_action_result()
                                                              ↓
                                                    1. Log command ("> search chest")
                                                    2. Call _log_main_result()
                                                    3. Generate NLP from event_type metadata
                                                    4. Log message ("You find treasure")
```

#### Implementation Steps

**1. System Returns Dict with Metadata (NOT tuples or messages)**
```python
# ObjectInteractionSystem (game layer)
def interact_with_object(self, object_name: str, action: str) -> Dict[str, Any]:
    # Perform action logic
    success, items_found = do_search_logic()
    
    # Return structured data with event_type
    return {
        'success': success,
        'message': f"You find: {', '.join(items_found)}",  # Factual info only
        'event_type': 'search_success',  # For NLP generation
        'object_name': object_name,
        'items_found': items_found,
        'skill_check': {'roll': 15, 'total': 18, 'dc': 12}
    }
```

**2. Handler Extracts Metadata and Returns ActionResult**
```python
# ObjectInteractionHandler (action layer)
def handle_search(self, *args) -> ActionResult:
    result = self.game_engine.interact_with_object(object_name, "search")
    
    # Extract all metadata from dict
    return ActionResult(
        success=result.get('success', False),
        message=result.get('message', ''),
        time_passed=0.1,
        event_type=result.get('event_type'),  # Critical for NLP
        object_name=result.get('object_name'),
        items_found=result.get('items_found', []),
        skill_check=result.get('skill_check')
    )
```

**3. UI Calls log_action_result()**
```python
result = handler.handle_search(args)

action_logger.log_action_result(
    result,
    character=character,
    command_text="search chest",  # CRITICAL: Must provide command text
    player_state=player_state
)
```

**4. ActionLogger Generates NLP from event_type**
```python
def _log_main_result(self, action_result):
    # Check for event_type metadata
    event_type = action_result.get('event_type')
    
    if event_type == 'search_success':
        object_name = action_result.get('object_name')
        # Generate NLP message from MessageManager
        self.log_action_event("search_success", object_name=object_name)
        # Then add factual info
        if action_result.message:
            self.game_log.add_message(action_result.message)
    
    elif event_type == 'search_empty':
        object_name = action_result.get('object_name')
        self.log_action_event("search_empty", object_name=object_name)
```

### Result: Correct Chronology
```
> search chest
Your thorough search of the chest pays off.
You find: 2x Gold Coin, 1x Healing Potion
```

NOT:
```
Your thorough search of the chest pays off.
You find: 2x Gold Coin, 1x Healing Potion
> search chest
```

---

## Part 2: NLP Message Variance System

### Architecture Overview

The NLP system separates **narrative flavor** from **factual information**:
- **Narrative flavor**: Generated from `event_messages.json` via `MessageManager`
- **Factual information**: Returned in `message` field (items found, damage dealt, etc.)

### MessageManager Flow
```
ActionLogger.log_action_event("search_success", object_name="chest")
    ↓
MessageManager.get_action_message("search_success", object_name="chest")
    ↓
Loads event_messages.json → selects random variant → interpolates template
    ↓
Returns: "Your thorough search of the chest pays off." (1 of 6 variants)
```

### Event Type Categories

#### Survival Effects (`log_survival_event()`)
- `COLD_triggered` - 15 variants
- `ICY_triggered` - 7 variants
- `FREEZING_triggered` - 7 variants
- `HUNGER_triggered` - 10 variants
- `STARVING_triggered` - 7 variants
- `DYING_OF_HUNGER_triggered` - 6 variants
- `THIRST_triggered` - 7 variants
- `DEHYDRATED_triggered` - 7 variants
- `DYING_OF_THIRST_triggered` - 6 variants
- `TIRED_triggered` - 6 variants
- `VERY_TIRED_triggered` - 6 variants
- `EXHAUSTED_triggered` - 10 variants
- `HOT_triggered` - 7 variants
- `OVERHEATING_triggered` - 7 variants
- `HEAT_STROKE_triggered` - 6 variants
- `WET_triggered` - 8 variants
- `SOAKED_triggered` - 7 variants
- `DRENCHED_triggered` - 7 variants

#### Equipment Events (`log_equipment_event()`)
- `armor_equipped` - 8 variants
- `armor_removed` - 6 variants
- `weapon_equipped` - 8 variants
- `weapon_removed` - 6 variants
- `shield_equipped` - 6 variants
- `shield_removed` - 5 variants

#### Object Interaction Events (`log_action_event()`)
- `search_success` - 6 variants
- `search_empty` - 5 variants
- `forage_success` - 6 variants
- `forage_depleted` - 5 variants
- `harvest_success` - 5 variants
- `harvest_depleted` - 5 variants
- `fire_started` - 8 variants
- `fire_failure` - 7 variants
- `unlock_success` - 5 variants
- `unlock_failure` - 5 variants
- `disarm_success` - 7 variants
- `disarm_failure` - 6 variants
- `chop_success` - 5 variants
- `chop_depleted` - 4 variants
- `drink_success` - 6 variants
- `rest_complete` - 8 variants

---

## Part 3: Metadata Keys Convention

### Equipment Actions
- `event_type`: "item_equipped" / "item_unequipped"
- `item_type`: "weapon", "armor", "shield"
- `slot`: Equipment slot name
- `item_name`: Name of equipped/unequipped item

### Object Interactions
- `event_type`: "search_success", "forage_depleted", "fire_started", etc.
- `object_name`: Name of object interacted with
- `items_found`: List of "quantity x Item Name" strings
- `skill_check`: Dict with `roll`, `modifier`, `total`, `dc`
- `water_quality`: For drink actions ("excellent", "good", "fair", "poor")
- `temperature`: For drink actions ("cold", "cool", "warm")
- `triggered`: For disarm actions (whether trap triggered on failure)

### Combat (Future)
- `event_type`: "attack_hit", "attack_miss", "critical_hit", "spell_cast"
- `target`: Enemy name
- `damage_dealt`: Number
- `hit_roll`: Dice result
- `damage_type`: "slashing", "piercing", "bludgeoning", "fire", etc.

### Crafting (Future)
- `event_type`: "craft_success", "craft_failure"
- `item_crafted`: Name of crafted item
- `materials_consumed`: List of materials used
- `skill_used`: "crafting", "blacksmithing", "alchemy"

---

## Part 4: System Status

### ✅ Fully Implemented (Phase 3.7 Complete)

**Conditions System** (`fantasy_rpg/game/conditions.py`):
- All survival condition triggers use `log_survival_event()`
- No hardcoded condition messages
- Full NLP variance for all condition severities

**Equipment System** (`fantasy_rpg/actions/character_handler.py`):
- `handle_equip()` / `handle_unequip()` use metadata pattern
- Returns event_type for NLP generation
- No direct action_logger calls

**Object Interaction System** (`fantasy_rpg/game/object_interaction_system.py`):
- All methods return `Dict[str, Any]` with event_type
- No direct action_logger calls (removed all 8+ instances)
- Handlers extract metadata and pass to ActionResult
- ActionLogger generates NLP from event_type

**ActionLogger** (`fantasy_rpg/actions/action_logger.py`):
- `_log_main_result()` handles all event_type metadata
- Supports 50+ event types across all systems
- No duplicate logging issues
- Proper chronology: command → NLP → factual info

### 🔄 Systems Ready for NLP Integration

**Combat System** (Not yet implemented):
- Architecture ready - just add event_type to combat actions
- MessageManager can handle combat events immediately
- Pattern: return damage/hit data as metadata, NLP generated from event_type

**Crafting System** (Not yet implemented):
- Same pattern as object interactions
- Add craft_success/craft_failure events to event_messages.json
- Return materials consumed as factual message

---

## Part 5: Hardcoded Message Audit

### ✅ Already Using NLP (100+ message variants)
All narrative flavor text now comes from `event_messages.json`:
- **Survival conditions** (18 event types, 130+ variants)
- **Equipment changes** (6 event types, 39 variants)
- **Object interactions** (15 event types, 87 variants)
- **Rest/recovery** (1 event type, 8 variants)

**Total: 40+ event types, 260+ message variants**

### 📊 Hardcoded But Appropriate (Keep as-is)

**1. Skill Check Display** - Pure mechanics (NOT narrative):
```python
"[Navigation: 20 + 0 = 20]"
"[Perception: 15 + 2 = 17 vs DC 12]"
```
**Reason:** Factual dice roll display, not flavor text

**2. Movement/Location System** - Template-heavy data display:
```python
"[>] You travel to Forest 1009 (Hex 1009)"
"You are now inside Farmyard."
"Elevation: Rolling hills"
```
**Reason:** Location-specific data, low priority for variance

**3. Map/Status Display** - UI structure labels:
```python
"Current: Forest 1010 (1010)"
"Nearby locations:"
"Current survival status:"
```
**Reason:** Interface labels, not narrative content

**4. Time Passage** - Already has natural variance:
```python
"Some time passes." / "A short while passes." / "An hour passes."
```
**Reason:** Already varied based on duration

**5. Debug Commands** - Development tools only:
```python
"💚 You are now at full health!"
"[*] Character gains 100 XP"
```
**Reason:** Debug feedback, not player-facing in normal gameplay

**6. Weather System** - Uses own descriptive generation:
```python
"[~] Rain begins to fall, Clouds gather overhead."
```
**Reason:** Weather system already generates atmospheric descriptions

**7. Tutorial/Help Text** - Intentionally consistent:
```python
"The adventure begins..."
"Type 'help' for available commands."
```
**Reason:** Static tutorial text should be predictable

### 🔍 Low Priority Candidates (Optional Future Work)

**Navigation Flavor** (4 variants already, minimal benefit):
```python
"You navigate confidently through the terrain."
"You take a slightly longer route but arrive safely."
```
**Potential event types:** `navigation_excellent`, `navigation_good`, `navigation_average`, `navigation_poor`

**Perception Flavor** (4 variants already, minimal benefit):
```python
"You notice fine details in your surroundings."
"You glance around casually."
```
**Potential event types:** `perception_critical`, `perception_high`, `perception_medium`, `perception_low`

**Shelter Creation** (Infrequent action, minimal benefit):
```python
"Camp established: Lean-To"
"You now have shelter from the elements."
```
**Potential event type:** `shelter_created` with template vars

---

## Part 6: Adding New Event Types

### Step-by-Step Guide

**1. Add Messages to event_messages.json**
```json
{
  "actions": {
    "new_action_success": [
      "Success variant 1 with {template_var}.",
      "Success variant 2 with {template_var}.",
      "Success variant 3 with {template_var}.",
      "Success variant 4 with {template_var}.",
      "Success variant 5 with {template_var}."
    ],
    "new_action_failure": [
      "Failure variant 1.",
      "Failure variant 2.",
      "Failure variant 3.",
      "Failure variant 4."
    ]
  }
}
```

**2. System Returns Dict with event_type**
```python
def new_action_system(self, target):
    success = perform_action_logic()
    
    return {
        'success': success,
        'message': "Factual info here",
        'event_type': 'new_action_success' if success else 'new_action_failure',
        'target': target,
        'additional_data': extra_info
    }
```

**3. Handler Extracts Metadata**
```python
def handle_new_action(self, *args) -> ActionResult:
    result = self.game_engine.new_action_system(target)
    
    return ActionResult(
        success=result.get('success'),
        message=result.get('message'),
        time_passed=0.5,
        event_type=result.get('event_type'),
        target=result.get('target')
    )
```

**4. Add Handling in ActionLogger._log_main_result()**
```python
elif action_result.get('event_type') == 'new_action_success':
    target = action_result.get('target', 'target')
    self.log_action_event("new_action_success", target=target)
    # Add factual message if present
    if action_result.message:
        self.game_log.add_message(action_result.message)

elif action_result.get('event_type') == 'new_action_failure':
    target = action_result.get('target', 'target')
    self.log_action_event("new_action_failure", target=target)
```

**5. Test the Flow**
```python
# Should produce:
> new_action goblin
Success variant 3 with goblin.
Dealt 15 damage to goblin.
```

---

## Part 7: Benefits & Design Principles

### Architectural Benefits
1. **Consistent chronology**: Commands always appear before messages
2. **Centralized NLP**: All natural language generation in MessageManager
3. **Testable**: Systems return data, not pre-formatted strings
4. **Future-proof**: Adding combat/crafting follows same pattern
5. **Content-driven**: Writers can update message variants without code changes
6. **Variance without repetition**: 260+ message variants ensure fresh experience
7. **Separation of concerns**: Game logic separate from presentation

### Design Principles
1. **Event types describe WHAT happened** (not how to display it)
2. **Metadata provides context** (object names, quantities, dice rolls)
3. **NLP provides flavor** (varied narrative descriptions)
4. **Factual info stays factual** (item counts, damage numbers, exact data)
5. **Systems never call action_logger directly** (always return data)
6. **Handlers coordinate** (extract metadata, build ActionResult)
7. **ActionLogger presents** (generates NLP, logs to UI)

### Anti-Patterns to Avoid
❌ Systems calling `action_logger.log_message()` directly  
❌ Hardcoding narrative text in game systems  
❌ Returning pre-formatted strings instead of structured data  
❌ Mixing factual data with flavor text  
❌ Bypassing the handler layer  
❌ Logging before command is recorded  
❌ Duplicate logging in multiple places  

### Best Practices
✅ Return `Dict[str, Any]` from game systems  
✅ Include `event_type` in all action returns  
✅ Extract metadata in handlers  
✅ Pass complete data to ActionResult  
✅ Let ActionLogger generate NLP from event_type  
✅ Keep factual info separate in `message` field  
✅ Add 5+ message variants per event type  
✅ Use template variables for dynamic content  

---

## Part 8: Testing Checklist

### Integration Testing
- [ ] Command appears before message in game log
- [ ] NLP message generated correctly from event_type
- [ ] Factual message appears after NLP flavor
- [ ] Template variables interpolated correctly
- [ ] Message variance confirmed (5+ different messages observed)
- [ ] No duplicate messages in log
- [ ] Time passage logged correctly
- [ ] Skill checks formatted properly

### Variance Testing
- [ ] Run same action 10 times, observe different messages
- [ ] Verify all template variables replaced
- [ ] Check fallback behavior for unknown event types
- [ ] Confirm no "None" or "{template_var}" in output

### Chronology Testing
- [ ] Command: "> search chest"
- [ ] Then: NLP flavor ("Your thorough search...")
- [ ] Then: Factual info ("You find: 2x Gold")
- [ ] Then: Time passage ("A short while passes.")

---

## Summary

**Phase 3.7 delivered a complete NLP logging architecture:**
- ✅ 40+ event types with 260+ message variants
- ✅ Metadata-driven pattern for correct chronology
- ✅ Zero hardcoded narrative text in core systems
- ✅ Clean API ready for combat and crafting systems
- ✅ Comprehensive documentation and testing guidelines

**The system is production-ready and provides:**
- Immersive narrative variance
- Consistent message ordering
- Easy content updates (JSON-based)
- Scalable pattern for future systems
- Clear separation of concerns

**Next Phase:** Combat system can be implemented immediately using this architecture - just add combat event types to `event_messages.json` and follow the established pattern.
