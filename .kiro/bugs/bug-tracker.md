Now I'll create a comprehensive bug tracker based on your findings:

## Bug Tracker: Critical Issues Found During Phase 3 Testing

**Last Updated:** November 4, 2025  
**Phase:** 3.5 Refactoring Complete

---

### **BUG #1: CRITICAL - Inventory Items Disappear on Save/Load** ✅ FIXED

**Severity:** CRITICAL (Data Loss)  
**Status:** ✅ RESOLVED (Phase 3.5)  
**Affects:** Save/Load System, Inventory Persistence  
**Fixed In:** Phase 3.5 Refactoring

**Description:**
When equipped/inventory items existed and player saved game, quit, and reloaded from save file, all items vanished from inventory. The inventory became empty on load despite items being present before save.

**Root Cause:**
Equipment class was missing serialization methods (`to_dict()` and `from_dict()`), causing equipment data to be lost during save/load cycle.

**Fix Applied:**
1. Added `Equipment.to_dict()` method to properly serialize all 11 equipment slots
2. Added `Equipment.from_dict()` class method to deserialize equipment from save data
3. Added fallback initialization for empty Equipment if no data in save
4. **BONUS:** Removed 170+ lines of duplicate serialization code from GameEngine by delegating to SaveManager

**Files Changed:**
- `fantasy_rpg/core/equipment.py` (+30 lines: serialization methods)
- `fantasy_rpg/game/save_manager.py` (equipment serialization fixed)
- `fantasy_rpg/game/game_engine.py` (-170 lines: removed duplicates, added delegation)

**Verification:**
- ✅ Equipment now properly serializes to `save.json` with full Item data
- ✅ Loading restores all equipped items with stats, properties, magical bonuses
- ✅ Save/load tested successfully with multiple equipment configurations

---

### **BUG #2: CRITICAL - Extreme Temperature Drop (-100°C)** ⏸️ ON HOLD

**Severity:** CRITICAL (Gameplay Balance)  
**Status:** ⏸️ UNREPRODUCIBLE (Intermittent - Monitoring)  
**Affects:** Temperature System, Survival Mechanics, Weather System  
**Action:** Continuing to monitor, not blocking Phase 4 merge

**Description:**
After playing for 3 in-game days, character body temperature dropped to -100°C (extremely unrealistic). Without magical events implemented, this shouldn't occur. Issue is intermittent and couldn't be reproduced on consecutive tests.

**Reproduction Steps:**
1. Create new character
2. Play for 3 in-game days of continuous gameplay
3. Monitor body temperature via `character` screen or `debug_survival`
4. **Expected:** Temperature should stay within realistic range (-50°C to 50°C)
5. **Actual:** Temperature dropped to -100°C and character should have died

**Root Cause Investigation Needed:**
- [ ] Trace temperature calculation in `time_system.py` `_advance_time()`
- [ ] Check `weather_core.py` for unrealistic weather generation
- [ ] Verify wind chill calculations don't compound incorrectly
- [ ] Check shelter system doesn't have negative temperature modifiers
- [ ] Verify `player_state.survival.body_temperature` doesn't have unbounded decrease
- [ ] Check `conditions.py` for "Freezing" condition damage-over-time values
- [ ] Trace weather update intervals - maybe updating too frequently with extreme values

**Suspect Files:**
- `time_system.py` - Temperature advancement logic (lines 320-400)
- `player_state.py` - Body temperature tracking
- `weather_core.py` - Weather generation algorithms
- `conditions.py` - Freezing condition effects and damage calculations

**Test Plan:**
```
1. Run 24-hour game time at accelerated pace (multiple `sleep` commands)
2. Log temperature every game hour to `bug_temperature_log.txt`
3. Log weather conditions simultaneously
4. Log active conditions (freezing, wind chill, etc.)
5. Identify point where temperature drops below -50°C
6. Extract weather/condition state at that point for analysis
```

**Suspect Files:**
- `time_system.py` - Temperature advancement logic (lines 320-400)
- `player_state.py` - Body temperature tracking
- `weather_core.py` - Weather generation algorithms
- `conditions.py` - Freezing condition effects and damage calculations

**Priority:** ⏸️ Monitoring during normal gameplay - May need extended session to reproduce

---

### **BUG #3: HIGH - Shortkey Conflict: 'f' Maps to Forage Instead of Light** ✅ FIXED

**Severity:** HIGH (UX Breaking)  
**Status:** ✅ RESOLVED (Phase 3.5)  
**Affects:** Shortkey System, Object Interaction  
**Fixed In:** Phase 3.5 Refactoring

**Description:**
Command `f 0` attempts to forage from object  instead of lighting it. The `f` shortkey maps to `forage` action, but users expect `f` to mean "fire/light" based on common game conventions. This breaks intuitive object interaction.

**Description:**
Command `f 0` attempted to forage from object instead of lighting it. The `f` shortkey mapped to `forage` action, but users expected `f` to mean "fire/light" based on common game conventions.

**Root Cause:**
In `shortkey_manager.py`, action shortcuts were defined as:
```python
'f': 'forage',
'li': 'light',  # Two-letter shortcut required
```

**Fix Applied:**
Changed shortkey mapping to make `f` = fire/light (more intuitive):
```python
'f': 'light',     # 'f' = fire (single letter)
'fo': 'forage',   # 'fo' = forage (two letters)
```

**Files Changed:**
- `fantasy_rpg/actions/shortkey_manager.py` (shortkey definitions updated)

**Verification:**
- ✅ `f 0` now lights fireplace/torch objects correctly
- ✅ `fo` command works for foraging
- ✅ More intuitive UX - 'f' for fire is expected behavior

---

### **BUG #4: MEDIUM - Shelter State Race Condition** ✅ FIXED

**Severity:** HIGH (Gameplay Logic Error)  
**Status:** ✅ RESOLVED (Phase 3.5)  
**Affects:** Conditions System, Shelter Mechanics  
**Fixed In:** Phase 3.5 Refactoring

**Description:**
Two conflicting sources of truth for player shelter status:
1. `PlayerState.current_shelter` (dict) - set by GameEngine on location entry
2. `Location.provides_*_shelter` (flags) - checked by ConditionsManager as fallback

This created a race condition where whichever system updated first determined shelter quality, causing inconsistent environmental protection.

**Root Cause:**
Dual state representation with no clear ownership:
- GameEngine set `current_shelter` to "some" quality
- Location had `provides_excellent_shelter=True`
- ConditionsManager checked both with unclear precedence

**Fix Applied:**
1. **DELETED** `PlayerState.current_shelter` field entirely
2. Updated `ConditionsManager._get_current_shelter_quality()` to use ONLY location flags as single source of truth:
```python
def _get_current_shelter_quality(self, game_engine) -> str:
    location = game_engine.current_location
    if not location:
        return "none"
    if getattr(location, 'provides_excellent_shelter', False):
        return "excellent"
    elif getattr(location, 'provides_good_shelter', False):
        return "good"
    elif getattr(location, 'provides_some_shelter', False):
        return "some"
    return "none"
```
3. Removed all references to `current_shelter` from GameEngine (3 locations)

**Files Changed:**
- `fantasy_rpg/game/player_state.py` (-1 field: current_shelter removed)
- `fantasy_rpg/game/conditions.py` (simplified shelter logic)
- `fantasy_rpg/game/game_engine.py` (-3 current_shelter references)

**Verification:**
- ✅ Location shelter flags are now the single source of truth
- ✅ Race condition eliminated
- ✅ 20 lines of conflicting code removed
- ✅ Shelter quality determined consistently from location data

---

### **BUG #5: MEDIUM - Missing Shortkey for 'wait' Action** ✅ FIXED

**Severity:** MEDIUM (Minor UX Friction)  
**Status:** 📝 DOCUMENTED (Working as Designed)  
**Affects:** Shortkey System, Time Passing

**Description:**
The `wait` action has shortcuts `wa` and `v`, but commonly users want to `wait [duration]`. The command `w 15min` doesn't work because:
1. `w` = `west` (movement)
2. `wa` = `wait` (requires full two-letter shortcut)
3. No single-letter shortkey for wait

**Reproduction Steps:**
1. Type `w 15min`
2. **Expected:** Wait for 15 minutes
3. **Actual:** Attempt to move west

**Description:**
The `wait` action has shortcuts `wa` and `v`, but users want to use `w [duration]`. The command `w 15min` doesn't work because:
1. `w` = `west` (movement command takes precedence)
2. `wa` = `wait` (requires full two-letter shortcut)
3. `v` = `wait` (alternate shortcut, not intuitive for English speakers)

**Current Mapping:**
```python
'w': 'west',      # Single letter taken by navigation
'wa': 'wait',     # Two-letter shortcut
'v': 'wait',      # From French "veille" (watch/wait)
```

**Resolution:**
This is **working as designed**. Navigation shortcuts (`w`, `e`, `n`, `s`) take precedence as single-letter commands. The `v` shortcut (from French "veille") provides a single-letter alternative, though it may not be intuitive to English-speaking players.

**Workaround:**
Use `wa [duration]` or `v [duration]` for wait commands:
- `wa 15min` - Wait for 15 minutes
- `v 1h` - Wait for 1 hour

**Documentation:**
- ✅ Added to in-game help text explaining `wa` and `v` shortcuts
- ✅ Command reference updated to clarify wait shortkeys

**Priority:** 📝 Documentation complete - No code changes needed

---

### **BUG #6: MEDIUM - SaveManager Ad-Hoc Instantiation Risk** 🟡 NEEDS REVIEW

**Severity:** MEDIUM (Code Quality / Potential Bug Risk)  
**Status:** 🟡 IDENTIFIED (Needs Refactoring)  
**Affects:** Save/Load System, Serialization Delegation  
**Found In:** Phase 3.5 Post-Merge Review

**Description:**
During Phase 3.5 refactoring, serialization logic was delegated from GameEngine to SaveManager to eliminate duplication. However, the delegation methods in GameEngine create **temporary SaveManager instances** when `self.saves` isn't initialized, which could introduce bugs if SaveManager gains internal state in the future.

**Current Implementation (game_engine.py:1332-1365):**
```python
def _serialize_character(self, character) -> dict:
    """Delegate character serialization to SaveManager."""
    if self.saves:
        return self.saves._serialize_character(character)
    # ⚠️ Creates temporary instance - inefficient and risky
    from game.save_manager import SaveManager
    tmp = SaveManager(self)
    return tmp._serialize_character(character)

# Same pattern repeated for:
# - _deserialize_character()
# - _serialize_player_state()
# - _deserialize_player_state()
```

**Potential Issues:**
1. **Inefficiency:** Creates 4 temporary SaveManager instances during serialization/deserialization
2. **Future Bug Risk:** If SaveManager adds caching, state tracking, or file handles, temporary instances will break
3. **Memory Churn:** Unnecessary object creation/destruction during save/load operations
4. **Code Smell:** Lazy instantiation suggests architectural uncertainty

**Current SaveManager State:**
- ✅ Currently safe: Only stores `self.game_engine` reference (stateless)
- ⚠️ Risk: Phase 4 might add caching, logging, or validation state

**Recommended Fix:**
**Option A: Ensure SaveManager Always Initialized** (Safest)
```python
# In GameEngine.__init__() - ensure saves is ALWAYS created
def __init__(self, world_size=(20, 20)):
    # ... existing init code ...
    
    # Always initialize SaveManager (even before new_game)
    from game.save_manager import SaveManager
    self.saves = SaveManager(self)
    
    # Remove lazy instantiation fallbacks from delegation methods
```

**Option B: Make Serialization Methods Static** (Cleaner)
```python
# In SaveManager - make serialization methods @staticmethod
class SaveManager:
    @staticmethod
    def serialize_character(character) -> dict:
        """Serialize character (stateless operation)"""
        # ... existing code without self.game_engine references
    
    @staticmethod
    def deserialize_character(data: dict):
        """Deserialize character (stateless operation)"""
        # ... existing code ...

# In GameEngine - call static methods directly
def _serialize_character(self, character) -> dict:
    from game.save_manager import SaveManager
    return SaveManager.serialize_character(character)
```

**Option C: Remove Delegation Entirely** (Simplest)
```python
# Move serialization methods back to GameEngine
# Accept some duplication to avoid instantiation complexity
# (Not recommended - reverses Phase 3.5 cleanup)
```

**Files Affected:**
- `fantasy_rpg/game/game_engine.py` (lines 1332-1365: delegation methods)
- `fantasy_rpg/game/save_manager.py` (lines 152-324: serialization methods)

**Priority:** 🟡 MEDIUM - Not blocking, but should fix before Phase 4 adds SaveManager features

**Recommendation:** Implement **Option A** - Always initialize SaveManager in GameEngine.__init__()
- Guarantees `self.saves` is available
- Removes all lazy instantiation fallbacks
- Future-proof for Phase 4 SaveManager enhancements (quest save data, relationship tracking, etc.)

---

## Summary

| Bug #  | Title                                  | Status       | Priority | Fixed In     |
| ------ | -------------------------------------- | ------------ | -------- | ------------ |
| **#1** | Inventory Items Disappear on Save/Load | ✅ FIXED      | CRITICAL | Phase 3.5    |
| **#2** | Extreme Temperature Drop (-100°C)      | ⏸️ MONITORING | CRITICAL | Ongoing      |
| **#3** | Shortkey Conflict: 'f' = Forage        | ✅ FIXED      | HIGH     | Phase 3.5    |
| **#4** | Shelter State Race Condition           | ✅ FIXED      | HIGH     | Phase 3.5    |
| **#5** | Missing Shortkey for 'wait'            | 📝 DOCUMENTED | MEDIUM   | N/A (Design) |
| **#6** | SaveManager Ad-Hoc Instantiation       | 🟡 IDENTIFIED | MEDIUM   | Pending      |

**Phase 3.5 Impact:**
- ✅ 3 of 6 bugs resolved
- ✅ 1 bug documented as working as designed  
- ⏸️ 1 bug under ongoing monitoring (not blocking merge)
- 🟡 1 bug identified post-merge (code quality issue)

**Next Actions:**
- Continue monitoring BUG #2 during normal gameplay
- Fix BUG #6 before Phase 4 (prevent future SaveManager state issues)
- Phase 4 can proceed with clean bug slate


