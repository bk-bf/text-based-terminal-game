Perfect. Let me create a detailed Phase 3.7 task list focused on the two implementations you want: centralized NLP messages and message variance integration.[1][2]

## Phase 3.7/NLP-Implementation Task List

---

## **Part 1: Centralized Message Library (Days 1-2)**

### 1.1 Create Message Data Structure

- [ ] Create `fantasy_rpg/dialogue/` directory
- [ ] Create `fantasy_rpg/dialogue/__init__.py` (empty init file)
- [ ] Create `fantasy_rpg/dialogue/event_messages.json`

**Subtask 1.1.1:** Define survival event messages

In `event_messages.json`, create `survival_effects` object with:
- `COLD_triggered` array: 12-15 variants describing cold exposure
- `HUNGER_triggered` array: 10-12 variants describing starvation
- `EXHAUSTION_triggered` array: 10-12 variants describing fatigue
- `WET_triggered` array: 8-10 variants describing getting soaked
- `SUFFOCATION_triggered` array: 5-8 variants (if applicable)

**Example structure:**
```json
{
  "survival_effects": {
    "COLD_triggered": [
      "A chill runs through you...",
      "The bitter wind cuts...",
      "..."
    ]
  }
}
```

**Subtask 1.1.2:** Define equipment messages

Create `equipment_effects` object with:
- `armor_equipped` array: 6-8 variants (template: `{armor_name}`, `{protection_boost}`)
- `armor_removed` array: 5-6 variants (template: `{armor_name}`)
- `weapon_equipped` array: 6-8 variants
- `shield_equipped` array: 5-6 variants
- `item_used` array: 8-10 variants (template: `{item_name}`)

**Subtask 1.1.3:** Define environmental messages

Create `environmental` object with:
- `weather_change_to_rain` array: 5-8 variants
- `weather_change_to_snow` array: 5-8 variants
- `weather_change_to_clear` array: 4-6 variants
- `enter_cold_area` array: 5-8 variants
- `enter_hot_area` array: 5-8 variants

**Subtask 1.1.4:** Define action messages

Create `actions` object with:
- `forage_success` array: 6-8 variants (template: `{item_name}`, `{quantity}`)
- `forage_failure` array: 4-6 variants
- `harvest_success` array: 6-8 variants
- `hunt_success` array: 8-10 variants (template: `{prey_type}`)
- `hunt_failure` array: 5-8 variants
- `rest_complete` array: 6-8 variants

***

### 1.2 Create MessageManager Class

- [ ] Create `fantasy_rpg/dialogue/message_manager.py`

**Subtask 1.2.1:** Implement `MessageManager.__init__()`

```python
class MessageManager:
    def __init__(self, data_file: str = "event_messages.json"):
        self.data_file = Path(__file__).parent / data_file
        self.messages = self._load_messages()
        self._validate_structure()
```

- Load JSON file
- Validate all required keys exist
- Log warnings for missing categories

**Subtask 1.2.2:** Implement `_load_messages()` method

- Handle file not found gracefully
- Return dict with all message categories
- Cache loaded messages to avoid repeated file reads

**Subtask 1.2.3:** Implement `_validate_structure()` method

- Ensure all expected message types exist
- Log any missing or malformed entries
- Don't fail silently

**Subtask 1.2.4:** Implement `get_survival_message(event: str, context: dict = None) -> str`

```python
def get_survival_message(self, event: str, context: dict = None) -> str:
    """Returns random survival message variant
    
    Args:
        event: 'COLD_triggered', 'HUNGER_triggered', etc
        context: Optional dict with context data
    
    Returns:
        Random message from pool, or fallback if not found
    """
```

- Look up message array by event type
- Return random choice from array
- Provide sensible fallback if event not found

**Subtask 1.2.5:** Implement `get_equipment_message(event: str, **kwargs) -> str`

```python
def get_equipment_message(self, event: str, **kwargs) -> str:
    """Returns random equipment message with template substitution
    
    Args:
        event: 'armor_equipped', 'weapon_equipped', etc
        **kwargs: Template variables ({armor_name}, {item_name}, etc)
    
    Returns:
        Random message with variables interpolated
    """
```

- Select random message from pool
- Interpolate template variables (handle missing gracefully)
- Return formatted message

**Subtask 1.2.6:** Implement `get_environmental_message(event: str) -> str`

```python
def get_environmental_message(self, event: str) -> str:
    """Returns random environmental/weather message"""
```

- Similar to survival message getter
- No template variables needed

**Subtask 1.2.7:** Implement `get_action_message(event: str, **kwargs) -> str`

```python
def get_action_message(self, event: str, **kwargs) -> str:
    """Returns random action result message with templates"""
```

- Support for action outcomes (forage, hunt, etc)
- Template variable interpolation

---

### 1.3 Integration Testing for MessageManager

- [ ] Create `tests/test_message_manager.py`

**Subtask 1.3.1:** Test message loading

```python
def test_message_manager_loads_json():
    manager = MessageManager()
    assert manager.messages is not None
    assert 'survival_effects' in manager.messages
```

**Subtask 1.3.2:** Test message retrieval

```python
def test_get_survival_message():
    manager = MessageManager()
    msg = manager.get_survival_message('COLD_triggered')
    assert msg is not None
    assert len(msg) > 0
```

**Subtask 1.3.3:** Test template interpolation

```python
def test_equipment_message_interpolation():
    manager = MessageManager()
    msg = manager.get_equipment_message('armor_equipped', armor_name='Iron Breastplate')
    assert 'Iron Breastplate' in msg
```

**Subtask 1.3.4:** Test fallback behavior

```python
def test_unknown_event_fallback():
    manager = MessageManager()
    msg = manager.get_survival_message('UNKNOWN_EVENT')
    assert msg is not None  # Should return fallback, not crash
```

***

## **Part 2: ActionLogger Integration (Days 2-3)**

### 2.1 Modify ActionLogger to Use MessageManager

- [ ] Update `fantasy_rpg/actions/action_logger.py`

**Subtask 2.1.1:** Add MessageManager instance

```python
from ..dialogue.message_manager import MessageManager

class ActionLogger:
    def __init__(self):
        self.messages = []
        self.message_manager = MessageManager()  # ADD THIS
```

**Subtask 2.1.2:** Add `log_survival_event()` method

```python
def log_survival_event(self, event_type: str, context: dict = None):
    """Log survival event with message variance
    
    Args:
        event_type: 'COLD_triggered', 'HUNGER_triggered', etc
        context: Optional context data
    """
    message = self.message_manager.get_survival_message(event_type, context)
    self.log_message(message, "survival")
```

**Subtask 2.1.3:** Add `log_equipment_event()` method

```python
def log_equipment_event(self, event_type: str, **kwargs):
    """Log equipment change with message variance
    
    Args:
        event_type: 'armor_equipped', 'weapon_equipped', etc
        **kwargs: Template variables for message
    """
    message = self.message_manager.get_equipment_message(event_type, **kwargs)
    self.log_message(message, "equipment")
```

**Subtask 2.1.4:** Add `log_environmental_event()` method

```python
def log_environmental_event(self, event_type: str):
    """Log weather/environment change"""
    message = self.message_manager.get_environmental_message(event_type)
    self.log_message(message, "environment")
```

**Subtask 2.1.5:** Add `log_action_event()` method

```python
def log_action_event(self, event_type: str, **kwargs):
    """Log action results (forage, hunt, etc)"""
    message = self.message_manager.get_action_message(event_type, **kwargs)
    self.log_message(message, "action")
```

***

### 2.2 Update Conditions System to Use NLP

- [ ] Update `fantasy_rpg/game/conditions.py`

**Subtask 2.2.1:** Modify Cold status application

Find where `Cold` condition is applied and replace hardcoded string with:

```python
# OLD:
action_logger.log_message("A chill runs through you...")

# NEW:
action_logger.log_survival_event("COLD_triggered", {
    "current_temperature": current_temp,
    "severity": severity_level
})
```

**Subtask 2.2.2:** Modify Hunger status application

Same pattern for hunger events:

```python
action_logger.log_survival_event("HUNGER_triggered", {
    "hunger_level": hunger_points
})
```

**Subtask 2.2.3:** Modify Exhaustion status application

```python
action_logger.log_survival_event("EXHAUSTION_triggered", {
    "fatigue_level": fatigue_points
})
```

**Subtask 2.2.4:** Modify Wet status application

```python
action_logger.log_survival_event("WET_triggered", {
    "wetness_level": wetness_points
})
```

**Note:** Don't replace **all** log messages yet—just the survival condition triggers for this phase.

***

### 2.3 Update Equipment System to Use NLP

- [ ] Update `fantasy_rpg/core/equipment.py`

**Subtask 2.3.1:** Modify equip() method

```python
# OLD:
action_logger.log_message(f"You equip {self.name}")

# NEW:
action_logger.log_equipment_event("armor_equipped", armor_name=self.name, protection_boost=self.ac)
```

**Subtask 2.3.2:** Modify unequip() method

```python
action_logger.log_equipment_event("armor_removed", armor_name=self.name)
```

**Subtask 2.3.3:** Apply to all equipment slots

- Do this for armor, weapons, shields, helmets, gloves, boots

***

### 2.4 Update Object Interaction System to Use NLP

- [ ] Update `fantasy_rpg/game/object_interaction_system.py` (if exists) or relevant handler

**Subtask 2.4.1:** Modify forage success message

```python
# OLD:
return True, f"You forage and find {item_name}"

# NEW:
action_logger.log_action_event("forage_success", item_name=item_name, quantity=quantity)
return True, action_logger.get_last_message()
```

**Subtask 2.4.2:** Modify forage failure message

```python
action_logger.log_action_event("forage_failure")
return False, action_logger.get_last_message()
```

**Subtask 2.4.3:** Apply to harvest, hunt, other actions

- Same pattern for harvest, hunting, etc

***

### 2.5 Integration Testing for ActionLogger Changes

- [ ] Update `tests/test_action_logger.py` (or create if doesn't exist)

**Subtask 2.5.1:** Test survival event logging

```python
def test_log_cold_event():
    logger = ActionLogger()
    logger.log_survival_event("COLD_triggered", {"temperature": 20})
    assert len(logger.messages) > 0
    assert "cold" in logger.messages[-1].lower() or "chill" in logger.messages[-1].lower()
```

**Subtask 2.5.2:** Test equipment logging

```python
def test_log_equipment_equip():
    logger = ActionLogger()
    logger.log_equipment_event("armor_equipped", armor_name="Iron Breastplate", protection_boost=2)
    assert len(logger.messages) > 0
    assert "Iron Breastplate" in logger.messages[-1]
```

**Subtask 2.5.3:** Test action logging

```python
def test_log_forage_success():
    logger = ActionLogger()
    logger.log_action_event("forage_success", item_name="mushroom", quantity=3)
    assert len(logger.messages) > 0
    msg = logger.messages[-1]
    assert "mushroom" in msg.lower() or "3" in msg
```

***

### 2.6 Identify and Replace Remaining Hardcoded Strings (Optional for Phase 3.7)

- [ ] Audit codebase for remaining hardcoded message strings
- [ ] Document remaining strings for Phase 4 follow-up

**Subtask 2.6.1:** Search for hardcoded messages

```bash
grep -r "log_message(" fantasy_rpg/ | grep -v "action_logger" | head -20
```

Document any that aren't using the new system yet—these can be addressed incrementally.

---

## Summary Checklist

```markdown
## Phase 3.7 Deliverables

### Data Layer (Day 1)
- [x] event_messages.json created with 4 categories
- [x] 70+ total message variants across all types
- [x] Template variables documented

### MessageManager (Day 1-2)
- [x] MessageManager class implemented
- [x] All 4 getter methods working
- [x] Fallback behavior graceful
- [x] Unit tests passing (80%+ coverage)

### Integration (Day 2-3)
- [x] ActionLogger uses MessageManager
- [x] Conditions system uses NLP events
- [x] Equipment system uses NLP events
- [x] Object interaction uses NLP events
- [x] Integration tests passing

### Quality
- [x] No hardcoded survival/equipment/action messages in code
- [x] All messages come from JSON
- [x] Variance confirmed (re-run game 5+ times, see different messages)
- [x] Game runs without errors
- [x] All survival conditions trigger correctly with new messages

***

## Estimated Timeline

- **Day 1:** Subtasks 1.1 + 1.2.1-1.2.6 (message library + MessageManager core)
- **Day 2:** Subtasks 1.3 + 2.1 (testing + ActionLogger integration)
- **Day 3:** Subtasks 2.2-2.5 (conditions/equipment/actions integration + testing)
- **Day 3.5:** Polish, edge case handling, documentation

**Total: 3 days**
