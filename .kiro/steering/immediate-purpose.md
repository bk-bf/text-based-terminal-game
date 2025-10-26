# Immediate Purpose Principle

## Every Line Must Serve an Immediate Need

Don't write code for hypothetical future requirements. Only implement what you need right now to make the current feature work.

## Anti-Patterns to Avoid

### ❌ Future-Proofing
```python
# DON'T DO THIS - over-engineered for future needs
class AbstractGameEntity:
    def __init__(self):
        self.components = {}
        self.event_handlers = []
        self.state_machine = StateMachine()
    
    def add_component(self, component_type, component):
        # Complex system for future flexibility
        pass

class Character(AbstractGameEntity):
    # Inherits tons of unused complexity
    pass
```

### ❌ Premature Abstraction
```python
# DON'T DO THIS - abstract before you need it
class ConfigurableFactory:
    def __init__(self, config_loader, validator, transformer):
        # Complex configuration system nobody asked for
        pass
    
    def create_with_strategy(self, strategy_name, **kwargs):
        # Flexible but unnecessary complexity
        pass
```

### ❌ Over-Generalization
```python
# DON'T DO THIS - solving problems you don't have
def process_data(data, processors=None, filters=None, 
                transformers=None, validators=None):
    # Handles every possible data processing scenario
    # But you only need to load a JSON file
    pass
```

## What to Do Instead

### ✅ Solve the Immediate Problem
```python
# DO THIS - exactly what you need right now
def create_character(name: str, race: str, character_class: str) -> dict:
    """Create a character for the game. That's it."""
    character = {
        "name": name,
        "race": race,
        "class": character_class,
        "hp": 10,  # Will calculate properly when needed
        "ac": 10   # Will calculate properly when needed
    }
    return character
```

### ✅ Add Complexity Only When Needed
```python
# Start simple
def calculate_ac(character: dict) -> int:
    return 10 + character.get("dex_modifier", 0)

# Add armor support only when you implement equipment
def calculate_ac(character: dict) -> int:
    base_ac = 10 + character.get("dex_modifier", 0)
    armor_bonus = character.get("armor_ac", 0)
    return base_ac + armor_bonus

# Add shield support only when you implement shields
def calculate_ac(character: dict) -> int:
    base_ac = 10 + character.get("dex_modifier", 0)
    armor_bonus = character.get("armor_ac", 0)
    shield_bonus = character.get("shield_ac", 0)
    return base_ac + armor_bonus + shield_bonus
```

## Implementation Guidelines

### Start with the Simplest Thing
```python
# Need to save a character? Start simple:
def save_character(character: dict, filename: str):
    with open(filename, 'w') as f:
        json.dump(character, f)
    print(f"Saved {character['name']} to {filename}")

# Add features only when you need them:
# - Pretty printing? Add indent=2 when formatting matters
# - Error handling? Add try/except when you hit errors
# - Backup saves? Add when you lose data
```

### Build Features Incrementally
```python
# Phase 1: Just create characters
def create_character(name, race, char_class):
    return {"name": name, "race": race, "class": char_class}

# Phase 2: Add stats when you need combat
def create_character(name, race, char_class):
    character = {"name": name, "race": race, "class": char_class}
    character["hp"] = 10
    character["ac"] = 10
    return character

# Phase 3: Add proper stat calculation when you implement D&D rules
def create_character(name, race, char_class):
    character = {"name": name, "race": race, "class": char_class}
    character["strength"] = 10
    character["dexterity"] = 10
    # ... other stats
    character["hp"] = calculate_hp(character)
    character["ac"] = calculate_ac(character)
    return character
```

### Refactor Only When Necessary
Don't refactor until:
- Code is actually hard to understand
- You're duplicating the same logic 3+ times
- Adding a feature requires changing many files
- Performance is actually a problem

## Decision Framework

Before writing any code, ask:

1. **Do I need this right now?** If no, don't write it
2. **What's the simplest way to solve this?** Start there
3. **Can I test this immediately?** If no, simplify
4. **Will this solve a real problem I have today?** If no, skip it

## Examples of Immediate Purpose

### Good: Character Creation
```python
# Need: Create a character for the game
def create_character(name: str, race: str) -> dict:
    return {"name": name, "race": race, "hp": 10}

# Immediate purpose: Make a character that can be used in game
# Test: char = create_character("Bob", "Human"); print(char)
```

### Good: Equipment System
```python
# Need: Characters should be able to wear armor
def equip_armor(character: dict, armor_name: str):
    character["armor"] = armor_name
    character["ac"] = 10 + get_armor_bonus(armor_name)
    print(f"{character['name']} equipped {armor_name}")

# Immediate purpose: Let characters wear armor and get AC bonus
# Test: equip_armor(char, "chain_mail"); print(char["ac"])
```

### Good: Save System
```python
# Need: Don't lose progress when quitting
def save_game(character: dict):
    filename = f"{character['name']}_save.json"
    with open(filename, 'w') as f:
        json.dump(character, f, indent=2)
    print(f"Game saved to {filename}")

# Immediate purpose: Persist character data
# Test: save_game(char); check that file exists and looks right
```

## Red Flags

If you're writing code that:
- "Might be useful later"
- "Makes the system more flexible"
- "Follows best practices" (without solving a real problem)
- "Is more maintainable" (but you haven't maintained it yet)
- "Handles edge cases" (that you haven't encountered)

Stop. Write the simplest thing that works for your immediate need.

## Remember

- Solve today's problems today
- Tomorrow's problems can wait until tomorrow
- Simple code that works is better than complex code that might work
- You can always add complexity later when you actually need it