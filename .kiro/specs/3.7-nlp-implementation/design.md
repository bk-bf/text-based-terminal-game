# NLP Implementation Design Document

## Overview

**Goal**: Replace hardcoded message strings throughout the codebase with a centralized, variance-driven natural language system that provides 10-20 message variants per event type.

**Philosophy**: Messages should feel organic and contextual, never repetitive. Players should experience different descriptions for the same mechanical event (e.g., "Cold" condition triggering 5 times shows 5 different descriptions).

---

## Architecture

### Three-Layer System

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 1: Data                            │
│  event_messages.json - Centralized message library          │
│  - survival_effects (Cold, Hunger, Exhaustion, Wet)         │
│  - equipment_effects (equip/unequip armor, weapons)         │
│  - environmental (weather changes, area transitions)        │
│  - actions (forage, hunt, rest, harvest)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                Layer 2: Message Manager                      │
│  message_manager.py - Message selection and interpolation   │
│  - get_survival_message(event, context)                     │
│  - get_equipment_message(event, **kwargs)                   │
│  - get_environmental_message(event)                         │
│  - get_action_message(event, **kwargs)                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                Layer 3: Integration                          │
│  action_logger.py - New NLP-aware logging methods           │
│  - log_survival_event(event_type, context)                  │
│  - log_equipment_event(event_type, **kwargs)                │
│  - log_environmental_event(event_type)                      │
│  - log_action_event(event_type, **kwargs)                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Existing Systems (Modified)                     │
│  conditions.py, equipment.py, object_interaction_system.py  │
│  - Replace hardcoded strings with NLP event calls           │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Data Layer: `event_messages.json`

**Location**: `fantasy_rpg/dialogue/event_messages.json`

**Structure**:
```json
{
  "survival_effects": {
    "COLD_triggered": [
      "variant 1...",
      "variant 2...",
      "..."
    ]
  },
  "equipment_effects": {
    "armor_equipped": [
      "You don the {armor_name}...",
      "..."
    ]
  },
  "environmental": {
    "weather_change_to_rain": [...]
  },
  "actions": {
    "forage_success": [...],
    "hunt_failure": [...]
  }
}
```

**Requirements**:
- **Minimum 10 variants** per survival event (Cold, Hunger, Exhaustion, Wet, Suffocation)
- **6-8 variants** per equipment event
- **5-8 variants** per environmental event
- **6-10 variants** per action outcome

**Template Variables**:
- Use `{variable_name}` for interpolation
- Examples: `{armor_name}`, `{item_name}`, `{quantity}`, `{temperature}`
- MessageManager handles missing variables gracefully (fallback to default or empty string)

**Message Categories**:

#### survival_effects
- `COLD_triggered`: Cold condition applied
- `HUNGER_triggered`: Hunger condition applied
- `EXHAUSTION_triggered`: Exhaustion condition applied
- `WET_triggered`: Wet condition applied
- `SUFFOCATION_triggered`: Suffocation (if applicable)

#### equipment_effects
- `armor_equipped`: Armor equipped (template: `{armor_name}`, `{protection_boost}`)
- `armor_removed`: Armor removed (template: `{armor_name}`)
- `weapon_equipped`: Weapon equipped (template: `{weapon_name}`, `{damage}`)
- `weapon_removed`: Weapon removed
- `shield_equipped`: Shield equipped
- `item_used`: Generic item use (template: `{item_name}`)

#### environmental
- `weather_change_to_rain`: Weather transitions to rain
- `weather_change_to_snow`: Weather transitions to snow
- `weather_change_to_clear`: Weather clears up
- `enter_cold_area`: Player enters cold biome/location
- `enter_hot_area`: Player enters hot biome/location
- `enter_wet_area`: Player enters rainy/swampy area

#### actions
- `forage_success`: Foraging succeeds (template: `{item_name}`, `{quantity}`)
- `forage_failure`: Foraging fails
- `harvest_success`: Harvesting object succeeds
- `harvest_failure`: Harvesting fails
- `hunt_success`: Hunting succeeds (template: `{prey_type}`)
- `hunt_failure`: Hunting fails
- `rest_complete`: Rest action completes (template: `{hours_rested}`)

---

### 2. Message Manager: `message_manager.py`

**Location**: `fantasy_rpg/dialogue/message_manager.py`

**Responsibilities**:
1. Load message library from JSON
2. Select random message variant for given event
3. Interpolate template variables
4. Provide graceful fallbacks for missing data

**Class Interface**:

```python
class MessageManager:
    def __init__(self, data_file: str = "event_messages.json")
    def _load_messages(self) -> dict
    def _validate_structure(self) -> None
    
    def get_survival_message(self, event: str, context: dict = None) -> str
    def get_equipment_message(self, event: str, **kwargs) -> str
    def get_environmental_message(self, event: str) -> str
    def get_action_message(self, event: str, **kwargs) -> str
```

**Implementation Details**:

#### `__init__(self, data_file)`
- Resolve path to `fantasy_rpg/dialogue/{data_file}`
- Call `_load_messages()`
- Call `_validate_structure()`
- Store messages in `self.messages` dict

#### `_load_messages()`
- Open and parse JSON file
- Handle `FileNotFoundError` gracefully (log warning, return empty dict)
- Return loaded message dict

#### `_validate_structure()`
- Check for required top-level keys: `survival_effects`, `equipment_effects`, `environmental`, `actions`
- Log warnings for missing keys or empty arrays
- **Don't fail silently** - validation errors should be visible during development

#### `get_survival_message(event, context)`
- Look up `self.messages['survival_effects'][event]`
- Return `random.choice()` from message array
- **Fallback**: If event not found, return `f"You experience {event.replace('_', ' ').lower()}"`
- **Context parameter**: Reserved for future severity-based selection (not implemented in Phase 3.7)

#### `get_equipment_message(event, **kwargs)`
- Look up `self.messages['equipment_effects'][event]`
- Select random message
- Interpolate template variables using `.format(**kwargs)`
- Handle `KeyError` for missing template variables (replace with empty string or generic text)
- **Fallback**: Return generic action description if event not found

#### `get_environmental_message(event)`
- Look up `self.messages['environmental'][event]`
- Return random choice
- **Fallback**: Return generic weather description

#### `get_action_message(event, **kwargs)`
- Look up `self.messages['actions'][event]`
- Select random message
- Interpolate template variables
- **Fallback**: Return generic action result

**Error Handling Philosophy**:
- **Never crash the game** due to missing messages
- Always provide fallback text (even if generic)
- Log warnings during development for missing data
- Template variable errors should log but not fail (replace with placeholder)

---

### 3. ActionLogger Integration

**Location**: `fantasy_rpg/actions/action_logger.py`

**Changes Required**:

#### Add MessageManager Instance
```python
from ..dialogue.message_manager import MessageManager

class ActionLogger:
    def __init__(self):
        self.messages = []
        self.message_manager = MessageManager()  # NEW
```

#### New Methods

**`log_survival_event(event_type: str, context: dict = None)`**
```python
def log_survival_event(self, event_type: str, context: dict = None):
    """Log survival condition trigger with message variance
    
    Args:
        event_type: 'COLD_triggered', 'HUNGER_triggered', etc
        context: Optional context data (temperature, severity, etc)
    
    Example:
        action_logger.log_survival_event("COLD_triggered", {
            "current_temperature": 20,
            "severity": "moderate"
        })
    """
    message = self.message_manager.get_survival_message(event_type, context)
    self.log_message(message, "survival")
```

**`log_equipment_event(event_type: str, **kwargs)`**
```python
def log_equipment_event(self, event_type: str, **kwargs):
    """Log equipment change with message variance
    
    Args:
        event_type: 'armor_equipped', 'weapon_equipped', etc
        **kwargs: Template variables for message interpolation
    
    Example:
        action_logger.log_equipment_event("armor_equipped", 
            armor_name="Iron Breastplate", 
            protection_boost=2
        )
    """
    message = self.message_manager.get_equipment_message(event_type, **kwargs)
    self.log_message(message, "equipment")
```

**`log_environmental_event(event_type: str)`**
```python
def log_environmental_event(self, event_type: str):
    """Log environmental/weather change
    
    Args:
        event_type: 'weather_change_to_rain', 'enter_cold_area', etc
    
    Example:
        action_logger.log_environmental_event("weather_change_to_snow")
    """
    message = self.message_manager.get_environmental_message(event_type)
    self.log_message(message, "environment")
```

**`log_action_event(event_type: str, **kwargs)`**
```python
def log_action_event(self, event_type: str, **kwargs):
    """Log action result (forage, hunt, rest, etc)
    
    Args:
        event_type: 'forage_success', 'hunt_failure', etc
        **kwargs: Template variables
    
    Example:
        action_logger.log_action_event("forage_success", 
            item_name="mushroom", 
            quantity=3
        )
    """
    message = self.message_manager.get_action_message(event_type, **kwargs)
    self.log_message(message, "action")
```

**Design Rationale**:
- Separate methods per category for clarity
- Consistent naming: `log_{category}_event()`
- All route through existing `log_message()` for consistency
- Category tags ("survival", "equipment", etc) for potential future filtering

---

### 4. System Integration Points

#### Conditions System (`fantasy_rpg/game/conditions.py`)

**Changes**:
Replace hardcoded condition trigger messages with NLP events.

**Before**:
```python
action_logger.log_message("A chill runs through you as the cold bites deeper")
```

**After**:
```python
action_logger.log_survival_event("COLD_triggered", {
    "current_temperature": current_temp,
    "severity": severity_level
})
```

**Affected Conditions**:
- Cold
- Hunger
- Exhaustion
- Wet
- (Any other survival conditions)

#### Equipment System (`fantasy_rpg/core/equipment.py`)

**Changes**:
Replace equipment change messages.

**Before**:
```python
action_logger.log_message(f"You equip {self.name}")
```

**After**:
```python
action_logger.log_equipment_event("armor_equipped", 
    armor_name=self.name, 
    protection_boost=self.ac
)
```

**Affected Methods**:
- `equip()` for all equipment types
- `unequip()` for all equipment types
- Item use actions

#### Object Interaction System (`fantasy_rpg/game/object_interaction_system.py`)

**Changes**:
Replace action outcome messages.

**Before**:
```python
return True, f"You forage and find {item_name}"
```

**After**:
```python
action_logger.log_action_event("forage_success", 
    item_name=item_name, 
    quantity=quantity
)
return True, action_logger.get_last_message()
```

**Affected Actions**:
- Foraging
- Harvesting
- Hunting
- Resting
- (Any other resource gathering)

#### Weather System (`fantasy_rpg/world/weather_core.py`)

**Changes** (Optional for Phase 3.7):
Replace weather change notifications.

**Before**:
```python
action_logger.log_message("Rain begins to fall")
```

**After**:
```python
action_logger.log_environmental_event("weather_change_to_rain")
```

---

## Testing Strategy

### Unit Tests

**Test File**: `tests/test_message_manager.py`

**Test Coverage**:
1. `test_message_manager_loads_json()` - Verify JSON loading succeeds
2. `test_message_manager_handles_missing_file()` - Graceful fallback for missing JSON
3. `test_get_survival_message()` - Returns valid message from pool
4. `test_get_survival_message_variance()` - Multiple calls return different messages
5. `test_get_equipment_message_interpolation()` - Template variables substituted correctly
6. `test_get_equipment_message_missing_variable()` - Handles missing template vars gracefully
7. `test_unknown_event_fallback()` - Returns fallback for unrecognized events
8. `test_empty_message_array()` - Handles empty message pools

**Test File**: `tests/test_action_logger_nlp.py`

**Test Coverage**:
1. `test_log_survival_event()` - Calls MessageManager correctly
2. `test_log_equipment_event()` - Template variables passed through
3. `test_log_action_event()` - Action messages logged correctly
4. `test_message_variance()` - Multiple identical events produce different messages

### Integration Testing

**Manual Testing Workflow**:
1. Start game with `python play.py`
2. Trigger Cold condition multiple times (expose to cold weather, wait)
3. **Verify**: Each trigger shows different message variant
4. Equip/unequip armor 5+ times
5. **Verify**: Different equipment messages each time
6. Forage 10+ times
7. **Verify**: Success/failure messages vary

**Automated Integration Test** (Optional):
```python
def test_end_to_end_cold_condition():
    """Verify Cold condition triggers NLP messages"""
    game_engine = GameEngine()
    game_engine.new_game()
    
    # Simulate cold exposure
    for _ in range(5):
        game_engine.time_system.perform_activity("wait", duration_override=1.0)
    
    # Check that messages were logged
    messages = game_engine.get_action_logger().messages
    cold_messages = [m for m in messages if "cold" in m.lower() or "chill" in m.lower()]
    
    assert len(cold_messages) > 0
    # Verify variance (not all messages identical)
    assert len(set(cold_messages)) > 1
```

---

## Migration Strategy

### Phase 3.7 Scope (3 days)

**Day 1**: Data + MessageManager
- Create `event_messages.json` with 70+ message variants
- Implement `MessageManager` class
- Write unit tests for MessageManager

**Day 2**: ActionLogger Integration
- Add NLP methods to ActionLogger
- Update Conditions system to use `log_survival_event()`
- Update Equipment system to use `log_equipment_event()`
- Write ActionLogger unit tests

**Day 3**: System Integration + Testing
- Update Object Interaction system to use `log_action_event()`
- Manual gameplay testing for variance verification
- Edge case handling and polish
- Documentation updates

### Future Phases (Post 3.7)

**Phase 4: Context-Aware Selection**
- Implement severity-based message selection (mild/moderate/severe Cold)
- Time-of-day variations (morning/evening/night messages)
- Weather-context messages (Cold in rain vs Cold in snow)

**Phase 5: Full Codebase Migration**
- Audit all remaining `log_message()` calls
- Replace combat messages with NLP system
- Replace exploration/discovery messages
- Replace dialogue/interaction messages

**Phase 6: Dynamic Message Composition**
- Combine message fragments for infinite variance
- Context-driven sentence generation
- Player action history influences message tone

---

## Success Criteria

### Phase 3.7 Completion Checklist

**Functional Requirements**:
- [ ] No hardcoded survival condition messages in `conditions.py`
- [ ] No hardcoded equipment messages in `equipment.py`
- [ ] No hardcoded action messages in `object_interaction_system.py`
- [ ] All messages sourced from `event_messages.json`
- [ ] MessageManager returns different variants on repeated calls
- [ ] Game runs without errors after integration

**Quality Requirements**:
- [ ] 70+ total message variants across all categories
- [ ] Unit test coverage ≥80% for MessageManager
- [ ] Integration tests verify variance behavior
- [ ] Graceful fallbacks for missing data (no crashes)
- [ ] Clear logging for missing message definitions (development mode)

**User Experience**:
- [ ] Player sees varied messages during gameplay
- [ ] Messages feel natural and immersive
- [ ] No repetitive text during normal play sessions
- [ ] Template interpolation seamless (no `{variable_name}` artifacts)

**Documentation**:
- [ ] MessageManager API documented in docstrings
- [ ] `event_messages.json` structure documented
- [ ] Integration examples in code comments
- [ ] Migration guide for adding new message types

---

## Non-Goals (Out of Scope for Phase 3.7)

**Not Included**:
- ❌ Context-aware message selection based on severity
- ❌ Player preference customization (verbosity settings)
- ❌ Localization/translation support
- ❌ Dynamic message composition (fragment combination)
- ❌ Full codebase migration (only survival/equipment/actions in scope)
- ❌ AI-generated message variants (all manually authored)

**Rationale**: Phase 3.7 establishes the **foundation**—centralized library + basic variance. Advanced features can build on this incrementally without changing architecture.

---

## Risks & Mitigations

### Risk 1: Message Quality Degrades with Quantity
**Problem**: Writing 70+ variants may lead to repetitive or low-quality messages.

**Mitigation**:
- Focus on quality over quantity (10 good variants > 20 mediocre)
- Review all messages for tone/style consistency
- Playtest extensively to catch repetitive phrasing

### Risk 2: Template Variable Errors Break Immersion
**Problem**: Missing template variables show `{armor_name}` to player.

**Mitigation**:
- MessageManager handles missing variables gracefully
- Log warnings during development (not visible to players)
- Integration tests verify all template variables provided

### Risk 3: Performance Impact from Random Selection
**Problem**: `random.choice()` called frequently during gameplay.

**Mitigation**:
- Negligible performance impact (microseconds per call)
- MessageManager could cache recent selections if needed (future optimization)
- No preemptive optimization required

### Risk 4: JSON File Corruption
**Problem**: Invalid JSON breaks message loading.

**Mitigation**:
- Validate JSON structure on load
- Provide fallback messages if parsing fails
- Version control ensures recovery from corruption

---

## Appendix: Example Messages

### Survival Effects - Cold (12 variants)

1. "A chill runs through you. Your fingers grow stiff and numb from the cold."
2. "The bitter wind cuts through you, sapping your warmth."
3. "Your breath becomes visible. Ice crystals form on your eyelashes."
4. "Numbness creeps into your extremities as the cold bite increases."
5. "Your body shivers uncontrollably. The cold is becoming dangerous."
6. "Frost spreads across your skin. You're dangerously close to freezing."
7. "The cold seeps into your bones, making every movement labored."
8. "Your teeth chatter as the frigid air steals your body heat."
9. "A bone-deep cold settles over you. Warmth feels like a distant memory."
10. "The icy air burns your lungs with each breath."
11. "Shivering violently, you struggle to maintain your core temperature."
12. "The relentless cold drains your strength with each passing moment."

### Equipment Effects - Armor Equipped (8 variants)

1. "You don the {armor_name}, settling into its familiar weight."
2. "Armor clicks into place. You feel more protected."
3. "{armor_name} slides over your body with a practiced motion."
4. "You buckle the {armor_name} securely, ready for what comes."
5. "The {armor_name} fits snugly, offering reassuring protection."
6. "With practiced efficiency, you equip the {armor_name}."
7. "The weight of the {armor_name} feels comfortable and secure."
8. "You adjust the {armor_name} straps until everything sits perfectly."

### Actions - Forage Success (8 variants)

1. "Your search yields {quantity} {item_name}. A fortunate find."
2. "You discover {quantity} {item_name} growing here."
3. "After careful searching, you gather {quantity} {item_name}."
4. "Your foraging efforts produce {quantity} {item_name}."
5. "You spot {quantity} {item_name} and add them to your supplies."
6. "A keen eye reveals {quantity} {item_name} among the undergrowth."
7. "Success! You've found {quantity} {item_name}."
8. "Your persistence pays off: {quantity} {item_name} secured."

---

## References

- **Project Instructions**: `.github/copilot-instructions.md` - Natural language philosophy
- **Development Workflow**: `.kiro/steering/development-workflow.md` - Manual testing approach
- **Phase 3.7 Tasks**: `tasks.md` - Detailed implementation checklist
- **UI Architecture**: `fantasy_rpg/ui/README.md` - UI integration patterns
- **ActionLogger Current**: `fantasy_rpg/actions/action_logger.py` - Existing log methods
