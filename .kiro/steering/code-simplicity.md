# Code Simplicity Guidelines

## KISS Principle: Keep It Simple, Stupid

Write code that is immediately understandable and verifiable. Every line should serve a clear, immediate purpose.

## Core Principles

### 1. Immediate Verifiability
- Every function should be testable by calling it directly
- No hidden side effects or complex initialization chains
- Results should be visible immediately (print statements, return values)
- Example: `print(f"Character AC: {character.calculate_ac()}")` after equipping armor

### 2. Simple Data Structures
- Use basic Python types: dict, list, int, str, bool
- Avoid complex inheritance hierarchies
- Prefer composition over inheritance
- Example: `character = {"name": "Bob", "hp": 25, "ac": 15}` over complex class hierarchies

### 3. Clear Function Names
- Function names should describe exactly what they do
- No abbreviations or clever naming
- Example: `calculate_armor_class()` not `calc_ac()` or `get_defense()`

### 4. One Thing Per Function
- Each function does exactly one thing
- Functions should be <20 lines when possible
- If you need comments to explain what a function does, split it up

## Anti-Patterns to Avoid

### ❌ Don't Do This:
```python
# Complex, hard to verify
class AbstractCharacterFactory:
    def create_character_with_advanced_configuration(self, config_dict):
        # 50 lines of complex logic
        pass

# Hidden behavior
def setup_game():
    # Automatically initializes 10 different systems
    # No way to verify what happened
    pass
```

### ✅ Do This Instead:
```python
# Simple, immediately verifiable
def create_character(name: str, race: str, character_class: str) -> dict:
    character = {
        "name": name,
        "race": race,
        "class": character_class,
        "hp": 10,
        "ac": 10
    }
    print(f"Created {name} the {race} {character_class}")
    return character

# Explicit, controllable
def load_races() -> dict:
    races = {"human": {"str_bonus": 1}, "elf": {"dex_bonus": 1}}
    print(f"Loaded {len(races)} races")
    return races
```

## Implementation Guidelines

### File Organization
- One class per file when possible
- Group related functions in modules
- Keep main.py simple - just call other functions

### Error Handling
- Use simple try/except blocks
- Print clear error messages
- Don't hide errors in complex exception hierarchies

### Data Persistence
- Save data in simple formats (JSON for config, SQLite for saves)
- Make save files human-readable when possible
- Always print what was saved/loaded

### UI Implementation
- Build UI incrementally - one panel at a time
- Test each UI component immediately after creating it
- Use simple print statements to verify UI state changes

## Verification Examples

Every major function should be immediately testable:

```python
# Character creation - immediately verifiable
character = create_character("Alice", "Human", "Fighter")
print(character)  # See the result immediately

# Equipment - verify AC changes
old_ac = character["ac"]
equip_armor(character, "chain_mail")
new_ac = character["ac"]
print(f"AC changed from {old_ac} to {new_ac}")

# World generation - verify it worked
world = generate_world(seed=12345, size=(10, 10))
print(f"Generated world with {len(world['hexes'])} hexes")
print(f"Biomes: {set(hex['biome'] for hex in world['hexes'])}")
```

## Manual Testing Philosophy

- No automated test runners
- No complex setup scripts
- Every feature gets tested by running it manually
- Use print statements liberally during development
- Remove debug prints only after feature is confirmed working

## Remember

If you can't easily explain what your code does to someone else, it's too complex. Simplify it.