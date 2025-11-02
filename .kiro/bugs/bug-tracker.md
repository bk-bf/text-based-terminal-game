Now I'll create a comprehensive bug tracker based on your findings:

## Bug Tracker: Critical Issues Found During Phase 3 Testing

Based on your findings, here's a prioritized bug tracker for the identified issues:

---

### **BUG #1: CRITICAL - Inventory Items Disappear on Save/Load** 🔴

**Severity:** CRITICAL (Data Loss)  
**Status:** UNCONFIRMED (Appears consistent)  
**Affects:** Save/Load System, Inventory Persistence

**Description:**
When equipped/inventory items exist and player saves game, quits, and reloads from save file, all items vanish from inventory. The inventory becomes empty on load despite items being present before save.

**Reproduction Steps:**
1. Equip items or add items to inventory (`t [obj]`, `equip [item]`)
2. Save game (`save`)
3. Quit game (`quit`)
4. Reload game (choose "Load" when prompted)
5. Open inventory (`i`)
6. **Expected:** Items should still be present
7. **Actual:** Inventory is empty

**Root Cause Investigation Needed:**
- [ ] Check if `inventory` is being serialized to save file (app.py line ~850)
- [ ] Verify `PlayerState.inventory` is included in game state serialization
- [ ] Check if `GameEngine.save_game()` calls correct inventory save method
- [ ] Verify `GameEngine.load_game()` properly deserializes inventory items
- [ ] Check if Item/InventoryItem classes have proper `__dict__` or `to_dict()` methods

**Suspect Files:**
- `app.py` - Save/load UI handlers (lines 750-800)
- `game_engine.py` - GameState serialization
- `player_state.py` - Inventory storage
- `inventory.py` - InventoryItem serialization

**Priority:** Fix immediately before Phase 4 (database layer won't solve this if core save mechanism is broken)[1][2]

---

### **BUG #2: CRITICAL - Extreme Temperature Drop Unrealistic** 🔴

**Severity:** CRITICAL (Gameplay Balance)  
**Status:** UNREPRODUCIBLE (Intermittent)  
**Affects:** Temperature System, Survival Mechanics, Weather System

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

**Priority:** Investigate but can defer Phase 4 start if intermittent (set as Phase 3.5 post-cleanup task)[1]

***

### **BUG #3: HIGH - Shortkey Conflict: 'f' Maps to Forage Instead of Light** 🟠

**Severity:** HIGH (UX Breaking)  
**Status:** CONFIRMED  
**Affects:** Shortkey System, Object Interaction

**Description:**
Command `f 0` attempts to forage from object  instead of lighting it. The `f` shortkey maps to `forage` action, but users expect `f` to mean "fire/light" based on common game conventions. This breaks intuitive object interaction.

**Reproduction Steps:**
1. Enter location with fireplace object assigned 
2. Type `f 0`
3. **Expected:** Light fire on fireplace
4. **Actual:** Attempt to forage from fireplace (nonsensical)
5. Workaround: Use `li 0` (light shortkey)

**Root Cause:**
In `shortkey_manager.py` line 28-29, action shortcuts defined as:
```python
'f': 'forage',
'li': 'light',  # Two-letter shortcut required
```

User expects `f` = fire/light (single letter), but it's taken by forage.

**Solution Options:**

**Option A: Change forage shortkey** (Simplest)
```python
'f': 'light',     # 'f' = fire  
'fo': 'forage',   # 'fo' = forage (two letters)
```
- Pros: 'f' for fire is intuitive
- Cons: 'forage' becomes less convenient

**Option B: Change light shortkey** (Original intent)
```python
'f': 'forage',    # Keep as-is
'l': 'light',     # Use single 'l' (conflicts with 'look')
'li': 'light',    # Keep two-letter fallback
```
- Pros: Keeps current logic
- Cons: Confusing because 'l' is already look

**Option C: Priority-based parsing** (Complex but best UX)
In `parse_command()`, prioritize action over object:
```python
# If first arg is [0-9], assume it's an object shortkey for last defined action
# If 'f 0' → check if 'f' is action (forage) but also check if user
# might mean 'light [f-type obj]'
```
- Pros: Most intuitive
- Cons: Ambiguity handling needed

**Recommended:** Option A - Change forage to 'fo', keep 'f' for fire[3]

***

### **BUG #4: MEDIUM - Missing Shortkey for 'wait' Action** 🟡

**Severity:** MEDIUM (Minor UX Friction)  
**Status:** CONFIRMED  
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

**Root Cause:**
In `shortkey_manager.py` line 45-46:
```python
'w': 'west',      # Single letter taken by navigation
'wa': 'wait',     # Only has two-letter shortcut
'v': 'wait',      # Alternate shortcut (not intuitive)
```

**Solution:**
Add a single-letter shortkey that doesn't conflict. Options in priority order:

1. Use `+` or special character: `'+': 'wait'` → `+ 15min`
2. Use number as shortkey: `'0': 'wait'` (conflicts with object )
3. Use `x` secondary meaning: `'x': 'wait'` (conflicts with examine)
4. Keep current `wa` and `v` shortcuts (acceptable but not ideal)

**Recommended:** Document that `wa` or `v` is required, add to help text. Note: `v` comes from French "veille" (watch/wait) so it's intentional but opaque to English players[3][1]

***

### **Summary Table**

| Bug # | Severity | Status         | Component       | Action                                          |
| ----- | -------- | -------------- | --------------- | ----------------------------------------------- |
| #1    | CRITICAL | Unconfirmed    | Save/Load       | Debug save serialization immediately            |
| #2    | CRITICAL | Unreproducible | Temperature     | Set up logging framework, defer if intermittent |
| #3    | HIGH     | Confirmed      | Shortkey System | Change 'f'→light, 'fo'→forage mapping           |
| #4    | MEDIUM   | Confirmed      | Shortkey System | Update help text, document 'wa' shortcut        |

**Estimated Fix Times:**
- Bug #1: 2-4 hours (tracing serialization)
- Bug #2: 3-6 hours (temperature logging + analysis)
- Bug #3: 0.5 hours (rename shortkey in one file)
- Bug #4: 0.25 hours (update help text)

**Total Phase 3.5 Bug Fixing: 5.5 - 10.5 hours**
