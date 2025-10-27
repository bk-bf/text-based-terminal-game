# Condition System Rules

## Core Principle: Complete Self-Containment

Every condition MUST be completely self-contained with ALL its effects, interactions, and ramifications defined within the condition itself. NO scattering of condition logic across multiple sections or files.

## What This Means

### ✅ CORRECT - All Effects in One Place
```json
{
  "Wet": {
    "description": "Wet clothing and equipment cause discomfort",
    "trigger": "wetness >= 200 AND wetness < 350",
    "hierarchy": "wetness",
    "priority": 1,
    "effects": {
      "dexterity_modifier": -1,
      "skill_penalties": {
        "stealth": -1,
        "acrobatics": -1
      },
      "cold_vulnerability": true
    },
    "interactions": {
      "with_cold_conditions": {
        "additional_effects": {
          "constitution_modifier": -1,
          "hypothermia_risk_multiplier": 2.0
        },
        "description": "Wet clothing in cold weather dramatically increases heat loss"
      }
    },
    "severity": "mild",
    "category": "wetness"
  }
}
```

### ❌ WRONG - Scattered Logic
```json
{
  "conditions": {
    "Wet": {
      "effects": {"dexterity_modifier": -1}
    }
  },
  "condition_interactions": {
    "wet_and_cold": {
      "conditions": ["Wet", "Cold"],
      "combined_effect": {"constitution_modifier": -1}
    }
  }
}
```

## Implementation Rules

### 1. Single Source of Truth
- Each condition contains ALL its logic
- No external interaction tables
- No scattered effect definitions
- No duplicate condition names anywhere

### 2. Interaction Handling
- Conditions can define how they interact with other condition categories
- Use generic interaction rules (e.g., "with_cold_conditions") rather than specific condition names
- Interactions are evaluated when the condition is active

### 3. Effect Calculation
- All base effects defined in the condition
- All conditional effects (interactions) defined in the condition
- No external calculation rules or modifiers

### 4. Data Structure
```json
{
  "condition_name": {
    "description": "What this condition does",
    "trigger": "when this condition activates",
    "hierarchy": "group_name",
    "priority": 1,
    "exclusion_group": "mutually_exclusive_group",
    "effects": {
      "base_effects": "always applied when condition is active"
    },
    "interactions": {
      "interaction_name": {
        "condition_check": "how to detect the interaction",
        "additional_effects": "extra effects when interaction occurs",
        "description": "what the interaction does"
      }
    },
    "severity": "mild|moderate|critical|life_threatening",
    "category": "condition_type"
  }
}
```

## Benefits

1. **No Duplication**: Each condition appears exactly once
2. **Easy Maintenance**: All condition logic in one place
3. **Clear Dependencies**: Interactions are explicit within each condition
4. **Simple Loading**: No complex cross-referencing during data loading
5. **Predictable Behavior**: All effects traceable to their source condition

## Enforcement

- Code reviews MUST reject any scattered condition logic
- All condition effects MUST be traceable to a single condition definition
- No external interaction tables or effect modifiers allowed
- Conditions system MUST load from a single, flat structure

This rule ensures that the conditions system remains maintainable, predictable, and easy to understand.