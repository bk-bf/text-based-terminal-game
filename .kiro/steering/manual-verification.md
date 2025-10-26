# Manual Verification Guidelines

## No Automated Anything

All testing, verification, and execution is done manually. This ensures you understand exactly what's happening at every step.

## Implementation Approach

### Build Incrementally
- Implement one small feature at a time
- Test it immediately before moving on
- Each feature should work standalone

### Immediate Feedback
- Every function should produce visible output
- Use print statements to show what's happening
- Make results obvious and verifiable

## Verification Patterns

### For Data Structures
```python
# Always print what you created
character = create_character("Bob", "Human", "Fighter")
print(f"Character: {character}")
print(f"HP: {character['hp']}, AC: {character['ac']}")

# Verify calculations
ac = calculate_armor_class(character)
print(f"Calculated AC: {ac}")
assert ac == character['ac'], f"AC mismatch: {ac} != {character['ac']}"
```

### For File Operations
```python
# Always confirm file operations
def save_character(character, filename):
    with open(filename, 'w') as f:
        json.dump(character, f, indent=2)
    print(f"Saved character to {filename}")
    
    # Immediately verify it worked
    with open(filename, 'r') as f:
        loaded = json.load(f)
    print(f"Verified save: {loaded['name']} loaded successfully")
```

### For UI Components
```python
# Test UI components in isolation
def test_character_panel():
    character = {"name": "Alice", "hp": 25, "max_hp": 30, "ac": 16}
    panel = create_character_panel(character)
    
    # Manually verify the panel looks right
    print("=== Character Panel Test ===")
    print(panel.render())
    print("Does this look correct? (Check manually)")
    input("Press Enter to continue...")
```

### For Game Logic
```python
# Make game state changes obvious
def move_character(character, direction):
    old_pos = character['position'].copy()
    character['position']['x'] += DIRECTIONS[direction]['x']
    character['position']['y'] += DIRECTIONS[direction]['y']
    
    print(f"Moved {direction}: {old_pos} -> {character['position']}")
    return character['position']
```

## Manual Testing Workflow

### 1. Feature Implementation
- Write the minimal code to make something work
- Add print statements to show what's happening
- Test immediately with simple inputs

### 2. Integration Testing
- Combine features one at a time
- Test each combination manually
- Verify nothing broke

### 3. User Testing
- Actually play the game as a user would
- Try to break things with unexpected inputs
- Fix issues immediately when found

## Verification Checklist

Before considering any feature "done":

- [ ] Can I run it with a simple function call?
- [ ] Does it print what it's doing?
- [ ] Can I verify the results by looking at them?
- [ ] Does it handle basic error cases gracefully?
- [ ] Can I explain what it does in one sentence?

## Examples of Good Verification

### Character Creation
```python
def test_character_creation():
    print("=== Testing Character Creation ===")
    
    # Test each race
    for race in ["Human", "Elf", "Dwarf", "Halfling"]:
        char = create_character("Test", race, "Fighter")
        print(f"{race}: STR={char['strength']}, DEX={char['dexterity']}")
    
    # Test each class
    for cls in ["Fighter", "Rogue", "Cleric", "Wizard"]:
        char = create_character("Test", "Human", cls)
        print(f"{cls}: HP={char['hp']}, Skills={char['skills']}")
    
    print("All tests completed - verify results above")
```

### World Generation
```python
def test_world_generation():
    print("=== Testing World Generation ===")
    
    # Generate small world for testing
    world = generate_world(seed=12345, size=(5, 5))
    
    print(f"World size: {len(world['hexes'])} hexes")
    print("Biome distribution:")
    biomes = {}
    for hex_data in world['hexes']:
        biome = hex_data['biome']
        biomes[biome] = biomes.get(biome, 0) + 1
    
    for biome, count in biomes.items():
        print(f"  {biome}: {count} hexes")
    
    print("Does this look reasonable? Check manually.")
```

## No Shadow Coding

- Don't implement features "for future use"
- Don't create abstract base classes unless you need them now
- Don't add configuration options until you need to configure something
- Don't optimize until you have a performance problem

## Remember

If you can't manually verify that something works, don't implement it that way. Keep it simple enough that you can always test it by hand.