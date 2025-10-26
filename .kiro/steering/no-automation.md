# No Automation Policy

## Manual Control Philosophy

Everything is done manually and explicitly. No automatic testing, building, launching, or deployment. You control every step.

## What NOT to Implement

### ❌ No Automated Testing
- No pytest runners or test discovery
- No continuous integration
- No automated test suites
- No test fixtures or complex test setup

### ❌ No Build Automation
- No Makefiles or build scripts
- No automatic dependency installation
- No automated environment setup
- No deployment scripts

### ❌ No Background Processes
- No automatic file watching
- No hot reloading
- No background services
- No daemon processes

### ❌ No Complex Configuration
- No configuration management systems
- No environment variable magic
- No automatic configuration discovery
- No complex initialization chains

## What TO Do Instead

### ✅ Manual Testing
```python
# Simple manual test functions
def test_character_stats():
    char = create_character("Bob", "Human", "Fighter")
    print(f"Created: {char}")
    
    # Manually verify each stat
    assert char['strength'] >= 8, "Strength too low"
    assert char['hp'] > 0, "HP must be positive"
    print("✓ Character stats look good")

# Run tests manually when you want
if __name__ == "__main__":
    test_character_stats()
    test_equipment_system()
    test_world_generation()
```

### ✅ Explicit Execution
```python
# Clear, explicit main function
def main():
    print("Starting Fantasy RPG...")
    
    # Load data explicitly
    races = load_races_from_json()
    classes = load_classes_from_json()
    print(f"Loaded {len(races)} races, {len(classes)} classes")
    
    # Start game explicitly
    game = create_new_game()
    run_game_loop(game)

if __name__ == "__main__":
    main()
```

### ✅ Simple Dependencies
```python
# requirements.txt - only what you need
textual>=0.40.0
rich>=13.0.0
# That's it - no testing frameworks, no build tools
```

### ✅ Manual Verification Steps
```python
# Include verification in your functions
def save_game(game_state, filename):
    # Save the data
    with open(filename, 'w') as f:
        json.dump(game_state, f, indent=2)
    
    # Immediately verify it worked
    print(f"Saved game to {filename}")
    file_size = os.path.getsize(filename)
    print(f"File size: {file_size} bytes")
    
    # Let user verify
    print(f"Check that {filename} exists and looks correct")
```

## Development Workflow

### 1. Write Code
- Write minimal code to solve immediate problem
- Add print statements to show what's happening
- Keep functions small and focused

### 2. Test Manually
- Run the code directly: `python character.py`
- Check the output manually
- Try different inputs by hand

### 3. Verify Integration
- Import modules manually in Python REPL
- Test combinations by hand
- Fix issues immediately when found

### 4. Document What Works
- Write simple comments about what you verified
- Note any manual steps needed to test
- Keep a simple changelog of what's working

## File Organization

### Simple Structure
```
fantasy_rpg/
├── main.py              # Simple entry point
├── character.py         # Character creation and management
├── world.py            # World generation
├── ui.py               # User interface
├── save.py             # Save/load functions
└── data/               # JSON data files
    ├── races.json
    ├── classes.json
    └── items.json
```

### No Complex Build Systems
- No setup.py or pyproject.toml unless absolutely necessary
- No virtual environment automation
- No dependency management beyond requirements.txt
- No package building or distribution

## Manual Testing Examples

### Character System Test
```python
# Run this manually when you change character code
def manual_character_test():
    print("=== Manual Character Test ===")
    
    # Test character creation
    char = create_character("Alice", "Human", "Fighter")
    print(f"1. Created character: {char['name']}")
    
    # Test stat calculations
    ac = calculate_ac(char)
    print(f"2. AC calculation: {ac}")
    
    # Test equipment
    equip_item(char, "chain_mail")
    new_ac = calculate_ac(char)
    print(f"3. AC after armor: {new_ac}")
    
    print("✓ Manual test complete - verify results above")

# Run it when you want to test
if __name__ == "__main__":
    manual_character_test()
```

### UI Test
```python
# Test UI components manually
def manual_ui_test():
    from textual.app import App
    
    class TestApp(App):
        def compose(self):
            yield CharacterPanel()
            yield GameLog()
    
    print("Starting UI test - check that panels display correctly")
    app = TestApp()
    app.run()
    print("UI test complete")

# Run when you want to see the UI
if __name__ == "__main__":
    manual_ui_test()
```

## Benefits of Manual Approach

1. **Full Control**: You know exactly what's running and when
2. **Immediate Feedback**: See results instantly, no waiting for test runners
3. **Simple Debugging**: Just add print statements and run again
4. **No Hidden Complexity**: No magic happening behind the scenes
5. **Easy to Understand**: Anyone can read and run your code

## Remember

- If you can't run it manually and see the results, don't build it
- Every feature should be testable with a simple function call
- Keep the barrier to testing as low as possible
- Manual doesn't mean sloppy - be thorough in your manual testing