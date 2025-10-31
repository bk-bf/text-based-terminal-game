# Condition Effects Implementation Status

## Summary
✅ **Removed**: `rest_quality_bonus` from all shelter conditions and "Lit Fire"

## All Condition Effects Used in conditions.json

### ✅ IMPLEMENTED Effects (Used by ConditionsManager)

These effects are defined in the `ConditionEffect` dataclass and properly applied via `calculate_total_effects()`:

1. **Ability Score Modifiers** (conditions.py lines 56-62)
   - `strength_modifier`
   - `dexterity_modifier`
   - `constitution_modifier`
   - `intelligence_modifier`
   - `wisdom_modifier`
   - `charisma_modifier`
   - `all_ability_modifiers` (applied to all abilities)

2. **Skill Penalties** (conditions.py line 65)
   - `skill_penalties` (dict)
   - Special key `"all"` applies to all skills

3. **Saving Throw Penalties** (conditions.py line 68)
   - `saving_throw_penalties` (dict)
   - Special key `"all"` applies to all saves

4. **Combat Effects** (conditions.py lines 71-73)
   - `attack_penalty`
   - `damage_penalty`
   - `armor_ac_penalty`

5. **Movement Effects** (conditions.py line 76)
   - `movement_penalty` (fraction of movement lost, 0.0-1.0)

6. **Special Flags** (conditions.py lines 79-82)
   - `disadvantage_on` (list)
   - `cold_vulnerability` (bool)
   - `fire_resistance` (bool)
   - `unconscious_risk` (bool)

7. **Damage Over Time** (conditions.py line 85)
   - `damage_over_time` (dict with `type`, `amount`, `interval`)
   - Applied in time_system.py `_apply_damage_over_time()`

8. **Fainting Mechanics** (conditions.py lines 88-90)
   - `faint_chance` (float 0.0-1.0)
   - `unconscious` (bool)
   - `helpless` (bool)
   - Checked in conditions.py `check_for_fainting()`

---

### ❌ NOT IMPLEMENTED Effects (Defined in JSON but no code support)

These effects are mentioned in conditions.json but have **NO implementation** in the Python code:

#### Environmental Effects (NOT IMPLEMENTED)
1. **`body_temperature_increase`** (dict)
   - Used in: "Lit Fire"
   - Structure: `{"rate": 15, "interval": "15_minutes", "max_temperature": 600}`
   - ❌ No code reads this or applies temperature changes

2. **`body_temperature_increase_rate`** (int)
   - Used in: "Lit Fire" interactions
   - ❌ No code applies this

3. **`body_temperature_stabilization`** (bool)
   - Used in: "Good Shelter", "Excellent Shelter"
   - ❌ No code reads this flag

4. **`temperature_regulation`** (bool)
   - Used in: "Excellent Shelter"
   - ❌ No code reads this flag

#### Resistance/Reduction Effects (NOT IMPLEMENTED)
5. **`cold_resistance`** (bool)
   - Used in: "Lit Fire", "Natural Shelter", "Good Shelter"
   - ❌ No code checks this flag
   - Note: Different from `cold_vulnerability` which IS implemented

6. **`heat_resistance`** (bool)
   - Used in: "Good Shelter"
   - ❌ No code checks this flag

7. **`wind_chill_reduction`** (float)
   - Used in: "Natural Shelter" (0.5), "Good Shelter" (0.75)
   - ❌ No code applies this multiplier

8. **`wind_chill_immunity`** (bool)
   - Used in: "Excellent Shelter"
   - ❌ No code checks this flag

9. **`precipitation_immunity`** (bool)
   - Used in: "Excellent Shelter"
   - ❌ No code checks this flag

10. **`hypothermia_risk_reduction`** (float)
    - Used in: "Lit Fire" (0.5), "Natural Shelter" interactions
    - ❌ No code applies this multiplier

11. **`hypothermia_risk_multiplier`** (float)
    - Used in: Wet/Soaked condition interactions (2.0, 3.0)
    - ❌ No code applies this multiplier

12. **`hyperthermia_risk_multiplier`** (float)
    - Used in: "Dehydrated" interaction with "Overheating" (3.0)
    - ❌ No code applies this multiplier

13. **`hyperthermia_risk_reduction`** (float)
    - Used in: "Good Shelter" interactions
    - ❌ No code applies this multiplier

#### Wetness/Drying Effects (NOT IMPLEMENTED)
14. **`wetness_reduction`** (dict)
    - Used in: "Natural Shelter", "Good Shelter", "Lit Fire" interactions
    - Structure: `{"rate": 10, "interval": "30_minutes"}`
    - ❌ No code applies wetness reduction over time

15. **`wetness_reduction_rate`** (int)
    - Used in: "Natural Shelter" interactions
    - ❌ No code applies this

16. **`drying_bonus`** (bool)
    - Used in: "Lit Fire" interactions with wet conditions
    - ❌ No code checks this flag

#### Fatigue/Recovery Effects (NOT IMPLEMENTED)
17. **`fatigue_recovery_bonus`** (int)
    - Used in: "Lit Fire" (5), "Good Shelter" (10), "Excellent Shelter" (20)
    - ❌ No code applies bonus fatigue recovery

18. **`fatigue_recovery`** (int)
    - Used in: "Fainted" (100)
    - ❌ No code applies this during fainting recovery

#### Skill/Combat Bonuses (NOT IMPLEMENTED)
19. **`skill_bonuses`** (dict)
    - Used in: "Lit Fire" (survival: 1), "Excellent Shelter" (survival: 2)
    - ❌ No code applies skill bonuses (only penalties implemented)

20. **`ranged_attack_penalty`** (int)
    - Used in: "Wind Chilled" (-2)
    - ❌ No code applies ranged-specific penalties

#### Miscellaneous (NOT IMPLEMENTED)
21. **`max_hp_modifier`** (float)
    - Used in: "Starving" (-0.25), "Dying of Starvation" (-0.5)
    - ❌ No code reduces max HP based on conditions

22. **`equipment_penalties`** (dict)
    - Used in: "Soaked" (`armor_ac_penalty`, `weapon_attack_penalty`)
    - ❌ Nested dict structure not supported (only `armor_ac_penalty` at root level works)

23. **`comfort_bonus`** (bool)
    - Used in: "Excellent Shelter"
    - ❌ No code checks this flag

24. **`forced_rest`** (bool)
    - Used in: "Fainted" effects
    - ❌ No code enforces rest during fainting

25. **`vulnerable_to_conditions`** (bool)
    - Used in: "Fainted" effects
    - ❌ No code makes character more vulnerable while fainted

26. **`all_weather_immunity`** (bool)
    - Used in: "Excellent Shelter" interactions
    - ❌ No code checks this flag

---

## Implementation Locations

### conditions.py (Condition System Core)
- **Lines 48-90**: `ConditionEffect` dataclass defines all IMPLEMENTED effects
- **Lines 396-464**: `calculate_total_effects()` applies implemented effects
- **Lines 466-490**: `_apply_condition_interactions()` applies interaction bonuses
- **Lines 541-567**: `check_for_fainting()` checks faint_chance
- **Lines 569-587**: `apply_fainting()` creates Fainted condition

### time_system.py (Time & Damage Over Time)
- **Lines 464-523**: `_apply_damage_over_time()` applies DoT from conditions
- Uses `damage_over_time` effect from conditions
- Parses `interval` strings like "15_minutes"

### player_state.py (Survival State)
- **Lines 455-471**: `_update_status_effects()` - DEPRECATED, just sets active_conditions list
- ❌ No code actually APPLIES condition effects to character stats
- ❌ No code reads any of the environmental/resistance/reduction effects

---

## What Actually Works

### ✅ Fully Functional
1. Ability modifiers (STR, DEX, CON, INT, WIS, CHA, all)
2. Skill penalties (individual or "all")
3. Saving throw penalties (individual or "all")
4. Attack/damage/armor penalties
5. Movement penalty (fractional reduction)
6. Special flags (disadvantage_on, cold_vulnerability, fire_resistance, unconscious_risk)
7. Damage over time (applied during time passage)
8. Fainting chance (random check based on conditions)

### ❌ Defined But Non-Functional
Everything else listed in the "NOT IMPLEMENTED" section above - these are **decorative JSON** that the game completely ignores.

---

## Recommendations

### Option 1: Remove Dead Code (Clean Slate)
Remove all non-implemented effects from conditions.json:
- Remove all `*_resistance`, `*_immunity`, `*_reduction`, `*_multiplier` fields
- Remove `body_temperature_*`, `wetness_reduction`, `skill_bonuses`
- Remove `fatigue_recovery_bonus`, `comfort_bonus`, etc.
- Keep only the 8 implemented effect categories

### Option 2: Implement Critical Effects
Focus on implementing only the most impactful non-functional effects:
1. **`skill_bonuses`** - mirrors skill_penalties logic
2. **`cold_resistance`** / **`heat_resistance`** - reduce temperature effects
3. **`wetness_reduction`** - dry off over time in shelter
4. **`fatigue_recovery_bonus`** - faster rest in good shelter
5. **`hypothermia_risk_reduction`** - shelters reduce hypothermia

### Option 3: Full Implementation (Large Effort)
Implement all 26 non-functional effects - requires extensive changes to:
- `player_state.py` temperature/wetness systems
- `time_system.py` activity effects
- `conditions.py` effect application
- Character stat calculation throughout codebase

---

## Status: `rest_quality_bonus` Removal Complete ✅

Removed from:
1. "Natural Shelter" (was 1)
2. "Good Shelter" (was 2)
3. "Excellent Shelter" (was 3)
4. "Lit Fire" (was 1)

This effect was never implemented anyway (no code reads it).
