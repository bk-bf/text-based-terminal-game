# Shelter Protection System

## Overview
Shelters now provide comprehensive protection from environmental hazards through four complementary systems:
1. **Temperature Stabilization** - Reduces rate of body temperature change
2. **Wind Chill Protection** - Reduces wind chill accumulation
3. **Precipitation Protection** - Reduces wetness from rain/snow
4. **Wetness Reduction (Active Drying)** - Accelerates removal of existing wetness

All four systems scale with shelter quality: Natural → Good → Excellent, with Fire providing the strongest drying effect.

---

## Temperature Stabilization
**Implementation**: `player_state.py` `_update_temperature_regulation()` (lines 334-420)

### How It Works
Shelter reduces the **rate** at which your body temperature changes toward ambient temperature:

- **Natural Shelter**: 35% reduction (0.65 multiplier) → Environmental change happens at 65% speed
- **Good Shelter**: 65% reduction (0.35 multiplier) → Environmental change happens at 35% speed
- **Excellent Shelter**: 85% reduction (0.15 multiplier) → Environmental change happens at 15% speed

### Example: Blizzard Survival
**Scenario**: Ambient temperature = -20°F (converted to scale: ~-30), body_temp = 300, no shelter
- Temperature difference: -30 - 300 = -330
- Change rate: 30% per hour
- **Temperature loss per hour**: -330 × 0.30 = -99 points/hour → **DEADLY**

**With Excellent Shelter**:
- Same temperature difference: -330
- **Reduced change rate**: 30% × 0.15 = 4.5% per hour
- **Temperature loss per hour**: -330 × 0.045 = -15 points/hour → **SURVIVABLE**

**With Excellent Shelter + Lit Fire**:
- Shelter slows cooling to -15/hour
- Fire actively warms at +15/hour (or +25/hour if critically cold)
- **Net effect**: Neutral to positive warming → **SAFE INDEFINITELY**

---

## Wind Chill Protection
**Implementation**: `player_state.py` `_update_environmental_exposure()` (lines 421-478)

### How It Works
Shelter blocks wind, reducing the **effective wind speed** that affects you:

- **Natural Shelter**: 50% reduction → Only half the wind reaches you
- **Good Shelter**: 75% reduction → Only quarter of the wind reaches you
- **Excellent Shelter**: 100% reduction → Complete immunity to wind

### Wind Chill Calculation
```python
# Without shelter
wind_chill_effect = wind_speed × 2 × hours

# With shelter
effective_wind_speed = wind_speed × (1.0 - wind_chill_reduction)
wind_chill_effect = effective_wind_speed × 2 × hours
```

### Example: Windy Night
**Scenario**: Wind speed = 20 mph, exposed for 1 hour
- **No shelter**: 20 × 2 × 1 = **40 wind_chill points** accumulated
- **Natural Shelter**: 20 × 0.5 × 2 × 1 = **20 wind_chill points** (50% reduction)
- **Good Shelter**: 20 × 0.25 × 2 × 1 = **10 wind_chill points** (75% reduction)
- **Excellent Shelter**: 20 × 0.0 × 2 × 1 = **0 wind_chill points** (complete immunity)

### Gameplay Impact
- **Wind Chilled Condition** triggers at wind_chill ≥ 50
- Reduces CON -2, WIS -1, movement -15%, adds cold vulnerability
- Shelters prevent/reduce this dangerous condition
- Excellent shelter guarantees safety from wind effects

---

## Precipitation Protection
**Implementation**: `player_state.py` `_update_environmental_exposure()` (lines 421-478)

### How It Works
Shelter blocks rain/snow, reducing the **effective precipitation** that wets you:

- **Natural Shelter**: 50% reduction → Only half the rain reaches you
- **Good Shelter**: 75% reduction → Only quarter of the rain reaches you
- **Excellent Shelter**: 100% reduction → Complete immunity, stay completely dry

### Wetness Calculation
```python
# Without shelter
wetness_increase = precipitation / 10 × hours

# With shelter
effective_precipitation = precipitation × (1.0 - precipitation_reduction)
wetness_increase = effective_precipitation / 10 × hours
```

### Example: Heavy Rain
**Scenario**: Precipitation = 100 (heavy rain), exposed for 1 hour
- **No shelter**: 100 / 10 × 1 = **10 wetness points** per hour
- **Natural Shelter**: 100 × 0.5 / 10 × 1 = **5 wetness points** per hour (50% reduction)
- **Good Shelter**: 100 × 0.25 / 10 × 1 = **2.5 wetness points** per hour (75% reduction)
- **Excellent Shelter**: 100 × 0.0 / 10 × 1 = **0 wetness points** per hour (stay dry)

### Wetness Conditions
- **Wet** (wetness ≥ 200): DEX -1, cold vulnerability, **-10 body_temp/hour**
- **Soaked** (wetness ≥ 350): DEX -2, CON -1, AC -1, movement -25%, **-20 body_temp/hour**

### Why This Matters
**Wetness + Cold = DEADLY**:
- Soaked condition causes -20 body_temp/hour heat loss
- Combined with cold weather environmental cooling
- Can trigger Freezing condition (unconscious_risk, damage_over_time)
- **Shelter prevents wetness = prevents compounding heat loss**

---

## Wetness Reduction (Active Drying)
**Implementation**: `player_state.py` `_update_environmental_exposure()` (lines 481-500)
**Added**: November 1, 2025

### How It Works
Shelter and fire actively **remove existing wetness** at accelerated rates (only when precipitation ≤ 0, i.e., not raining):

- **Lit Fire**: +15 points/hour (most effective)
- **Excellent Shelter**: +8 points/hour
- **Good Shelter**: +5 points/hour
- **Natural Shelter**: +3 points/hour
- **Base drying**: 5 points/hour + wind bonus + heat bonus

### Drying Rate Formula
```python
# Base drying (only when precipitation <= 0)
dry_rate = 5  # Base rate

# Weather bonuses (existing)
if wind_speed > 10:
    dry_rate += wind_speed // 5  # Wind helps drying (~2-4/hour)
if temperature > 70:
    dry_rate += 5  # Heat helps drying

# Shelter/fire bonuses (NEW)
if has_lit_fire:
    dry_rate += 15  # Fire provides excellent drying
elif has_excellent_shelter:
    dry_rate += 8   # Excellent shelter provides good drying
elif has_good_shelter:
    dry_rate += 5   # Good shelter provides moderate drying
elif has_natural_shelter:
    dry_rate += 3   # Natural shelter provides some drying

# Total wetness removed per hour
wetness_decrease = dry_rate × hours
```

### Example: Drying After Rain Storm
**Scenario**: Wetness = 350 (Soaked condition), rain just stopped, temperature = 60°F, no wind

- **No shelter/fire**: 5/hour → **70 hours to dry completely** (3 days)
- **Natural Shelter**: 5 + 3 = 8/hour → **44 hours to dry** (1.8 days)
- **Good Shelter**: 5 + 5 = 10/hour → **35 hours to dry** (1.5 days)
- **Excellent Shelter**: 5 + 8 = 13/hour → **27 hours to dry** (1.1 days)
- **Lit Fire**: 5 + 15 = 20/hour → **17.5 hours to dry** (less than a day)

**With Fire + Hot Weather (temp > 70°F)**:
- Base: 5 + heat bonus: 5 + fire: 15 = 25/hour → **14 hours to dry** (half a day)

### Key Differences: Precipitation Reduction vs Wetness Reduction
- **Precipitation Reduction**: Prevents **NEW** wetness (blocks rain from making you wet)
- **Wetness Reduction**: Removes **EXISTING** wetness (dries you off after you're already wet)

**Both are needed**:
1. During rain: precipitation_reduction stops you getting wetter
2. After rain: wetness_reduction dries you off faster

### Why This Matters
**Wet conditions cause severe debuffs**:
- Active cooling: -10 to -20 body_temp/hour (compounds with cold weather)
- DEX penalties (affects combat, stealth, lockpicking)
- Movement penalties (slower travel, escape)
- Cold vulnerability (environmental effects hit harder)

**Fast drying = faster recovery**:
- Fire: Remove Wet/Soaked conditions in hours, not days
- Shelter: Passive drying while you rest/sleep
- Natural synergy: Fire + Excellent Shelter = fast drying + no re-wetting from rain

---

## Synergistic Effects

### 1. Fire + Shelter (Cold Weather)
**Best Combo for Survival**:
- **Fire**: Actively warms at +15/hour (or +25/hour when critically cold)
- **Shelter**: Reduces environmental cooling by 35-85%
- **Wind Protection**: Prevents wind chill accumulation
- **Dry Environment**: Prevents wetness accumulation

**Example: Winter Night in Excellent Shelter with Fire**
- Ambient temp: 20°F → environmental cooling ~10/hour (after 85% reduction)
- Fire warming: +15/hour
- Wind chill: 0 (complete immunity)
- Wetness: 0 (stays dry)
- **Net effect**: +5 body_temp/hour → **Slowly warming despite freezing weather**

### 2. Shelter Only (Moderate Weather)
**Passive Protection**:
- Natural/Good shelter sufficient for spring/fall weather
- Slows temperature changes (both cooling and heating)
- Reduces wind chill buildup
- Reduces but doesn't eliminate wetness

### 3. Excellent Shelter (Any Weather)
**Complete Environmental Control**:
- 85% temperature stabilization
- 100% wind immunity
- 100% precipitation immunity
- **Result**: Almost complete disconnection from weather effects
- Can survive extreme conditions with just shelter (no fire needed for mild cold)

---

## Shelter Quality Comparison

| Effect                         | Natural       | Good             | Excellent       | Lit Fire       |
| ------------------------------ | ------------- | ---------------- | --------------- | -------------- |
| **Temperature Change Rate**    | 65% speed     | 35% speed        | 15% speed       | N/A            |
| **Wind Chill Protection**      | 50% reduction | 75% reduction    | 100% immunity   | N/A            |
| **Precipitation Protection**   | 50% reduction | 75% reduction    | 100% immunity   | N/A            |
| **Wetness Reduction (Drying)** | +3/hour       | +5/hour          | +8/hour         | **+15/hour**   |
| **Recommended For**            | Mild weather  | Moderate weather | Extreme weather | Wet conditions |
| **Survival Time (no fire)**    | Few hours     | Half a day       | Indefinite      | N/A            |

---

## Gameplay Implications

### Early Game Strategy
1. **Priority**: Find Natural Shelter immediately in bad weather
2. **Effect**: Cuts wetness/wind chill accumulation in half, slows freezing
3. **Survival**: Extends time before critical conditions trigger

### Mid Game Strategy
1. **Priority**: Seek Good Shelter for overnight stays
2. **Effect**: 75% protection from elements, comfortable rest
3. **Survival**: Can survive moderate weather without fire

### Late Game Strategy
1. **Priority**: Establish base in Excellent Shelter locations
2. **Effect**: Near-total environmental protection
3. **Survival**: Can weather any storm, focus on resources not survival

### Fire Usage
- **With Natural Shelter**: Fire essential in cold weather (shelter not enough alone), provides excellent drying (+15/hour)
- **With Good Shelter**: Fire recommended for comfort and fast drying, not critical for temperature survival
- **With Excellent Shelter**: Fire optional for temperature (shelter provides enough protection), useful for rapid drying
- **Wet Conditions**: Fire is **most effective** drying method regardless of shelter quality

---

## Technical Details

### Data Structure (conditions.json)
```json
"Natural Shelter": {
  "effects": {
    "wind_chill_reduction": 0.5,
    "precipitation_reduction": 0.5
  }
}

"Good Shelter": {
  "effects": {
    "wind_chill_reduction": 0.75,
    "precipitation_reduction": 0.75
  }
}

"Excellent Shelter": {
  "effects": {
    "wind_chill_reduction": 1.0,
    "precipitation_reduction": 1.0,
    "wetness_reduction": 8
  }
}

"Lit Fire": {
  "effects": {
    "body_temperature_increase": {"base_rate": 15, "emergency_rate": 25},
    "wetness_reduction": 15
  }
}
```

### Implementation Pattern
```python
# 1. Check for active shelter/fire conditions
has_lit_fire = "Lit Fire" in self.active_conditions
has_natural_shelter = "Natural Shelter" in self.active_conditions
has_good_shelter = "Good Shelter" in self.active_conditions
has_excellent_shelter = "Excellent Shelter" in self.active_conditions

# 2. Calculate reduction multiplier for wind/precipitation (0.0 = full effect, 1.0 = immunity)
reduction = 0.0
if has_excellent_shelter:
    reduction = 1.0
elif has_good_shelter:
    reduction = 0.75
elif has_natural_shelter:
    reduction = 0.5

# 3. Apply to environmental hazard
effective_hazard = base_hazard × (1.0 - reduction)

# 4. Calculate wetness reduction (active drying bonus)
dry_rate = 5  # Base
if has_lit_fire:
    dry_rate += 15
elif has_excellent_shelter:
    dry_rate += 8
elif has_good_shelter:
    dry_rate += 5
elif has_natural_shelter:
    dry_rate += 3
```

---

## Testing Recommendations

### Test 1: Wind Chill Protection
1. Find location with each shelter quality
2. Wait during high wind conditions (>15 mph)
3. Verify wind_chill stat increases at reduced rates
4. Excellent shelter should prevent Wind Chilled condition entirely

### Test 2: Precipitation Protection
1. Find location with each shelter quality
2. Wait during heavy rain/snow
3. Verify wetness stat increases at reduced rates
4. Excellent shelter should stay completely dry

### Test 3: Temperature Stabilization
1. Enter location with shelter during extreme weather
2. Monitor body_temperature change rate
3. Compare with unsheltered rate
4. Verify: Natural 65%, Good 35%, Excellent 15% of base rate

### Test 4: Fire + Shelter Synergy
1. Light fire in Excellent Shelter during blizzard
2. Monitor body_temperature over several hours
3. Should maintain or increase despite extreme cold
4. Verify no wind_chill or wetness accumulation

### Test 5: Wetness Reduction (Active Drying)
1. Get Soaked (wetness ≥ 350) during rain
2. Wait for rain to stop (precipitation = 0)
3. Test drying rates with different conditions:
   - No shelter: ~5-10/hour
   - Natural Shelter: ~8-13/hour  
   - Good Shelter: ~10-15/hour
   - Excellent Shelter: ~13-18/hour
   - Lit Fire: ~20-25/hour
4. Verify Fire provides fastest drying

---

## Future Enhancements

### Potential Additions (Not Yet Implemented)
1. **Fatigue Recovery Scaling**
   - Better shelter = better rest quality
   - Currently: fatigue_recovery_bonus is decorative

2. **Advanced Drying Interactions**
   - Clothing/armor weight affects drying time
   - Fire placement (indoor vs outdoor) affects drying efficiency
   - Wind + heat synergy bonuses

---

## Summary

The shelter protection system now provides **four layers of defense**:
1. **Slow temperature changes** (maintain body temperature longer)
2. **Block wind** (prevent wind chill condition)
3. **Block precipitation** (prevent wetness condition)
4. **Active drying** (remove existing wetness faster)

All four work together to create **meaningful survival choices**:
- Natural shelter extends survival by hours and provides basic drying
- Good shelter extends survival by half a day with moderate drying
- Excellent shelter can provide indefinite protection with good drying
- Fire provides the **most effective drying** at +15/hour (3x base rate)

Combined with fire, even **extreme weather becomes survivable** with proper preparation. Fire is now **dual-purpose**: warming in cold weather AND fastest method to dry off after getting wet.

