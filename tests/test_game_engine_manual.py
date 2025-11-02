"""
Manual integration tests for GameEngine

These tests were previously embedded in game_engine.py.
Run manually with: python tests/test_game_engine_manual.py

Note: These are NOT automated tests - they require manual observation
and validation. Consider migrating to pytest for automated testing.
"""


def test_game_engine():
    """Test GameEngine initialization and basic functionality"""
    print("=== Testing GameEngine ===")
    
    # Late imports to avoid circular dependencies
    from fantasy_rpg.core.character import Character
    from fantasy_rpg.core.race import Race
    from fantasy_rpg.core.character_class import CharacterClass, SkillProficiencies, StartingEquipment
    from fantasy_rpg.game.game_engine import GameEngine
    
    # Create basic race and class for testing
    test_race = Race(
        name="Human",
        ability_bonuses={"strength": 1, "constitution": 1},
        size="Medium",
        speed=30,
        languages=["Common"],
        traits=[]
    )
    
    test_class = CharacterClass(
        name="Fighter",
        hit_die=10,
        primary_ability="Strength",
        saving_throw_proficiencies=["Strength", "Constitution"],
        skill_proficiencies=SkillProficiencies(choose=2, from_list=["Acrobatics", "Animal Handling"]),
        starting_equipment=[StartingEquipment(item="Chain Mail", quantity=1)]
    )
    
    test_character = Character(
        # Required stats
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        # Derived stats
        level=1,
        hp=10,
        max_hp=10,
        armor_class=16,
        proficiency_bonus=2,
        experience_points=0,
        # Identity
        name="Aldric",
        race="Human",  # Use string, not object
        character_class="Fighter",  # Use string, not object
        background="Folk Hero"
    )
    
    # Initialize GameEngine
    engine = GameEngine()
    
    # Test new game creation
    game_state = engine.new_game(test_character, world_seed=12345)
    
    print(f"✓ Game state created successfully")
    print(f"✓ Character: {game_state.character.name}")
    print(f"✓ Starting hex: {game_state.world_position.hex_data['name']} ({game_state.world_position.hex_id})")
    print(f"✓ Weather: {game_state.current_weather.temperature:.0f}°F")
    
    # Test status retrieval
    status = engine.get_status()
    print(f"✓ Status retrieved: {status['character']['name']}")
    
    # Test hex description
    description = engine.get_hex_description()
    print(f"✓ Hex description generated ({len(description)} characters)")
    
    print("=== GameEngine test complete ===")
    return engine


def test_movement_system():
    """Test the movement system integration"""
    print("\n=== Testing Movement System ===")
    
    # Create test engine
    engine = test_game_engine()
    
    print(f"\nStarting position: {engine.game_state.world_position.hex_id}")
    print(f"Starting time: {engine.game_state.game_time.get_time_string()}")
    
    # Test movement in each direction
    directions = ["north", "south", "east", "west"]
    
    for direction in directions:
        print(f"\n--- Testing movement {direction} ---")
        success, message = engine.move_player(direction)
        
        if success:
            print(f"✓ Movement {direction} successful")
            print(f"✓ New position: {engine.game_state.world_position.hex_id}")
            print(f"✓ New location: {engine.game_state.world_position.hex_data['name']}")
            print(f"✓ New time: {engine.game_state.game_time.get_time_string()}")
            print(f"✓ Message: {message}")
            break  # Only test one successful movement
        else:
            print(f"✗ Movement {direction} failed: {message}")
    
    # Test invalid movement
    print(f"\n--- Testing invalid movement ---")
    success, message = engine.move_player("invalid_direction")
    if not success:
        print(f"✓ Invalid direction properly rejected: {message}")
    else:
        print(f"✗ Invalid direction should have failed")
    
    print("=== Movement System test complete ===")
    return engine


def test_action_handler_integration():
    """Test ActionHandler integration with GameEngine"""
    print("\n=== Testing Action Handler Integration ===")
    
    # Create test engine
    engine = test_game_engine()
    
    # Get connected action handler
    action_handler = engine.get_action_handler()
    
    print(f"\nStarting position: {engine.game_state.world_position.hex_id}")
    
    # Test movement commands through action handler
    test_commands = [
        "north",
        "go south", 
        "move east",
        "w",
        "look",
        "invalid_command",
        "help"
    ]
    
    for command in test_commands:
        print(f"\n--- Testing command: '{command}' ---")
        result = action_handler.process_command(command)
        
        if result.success:
            print(f"✓ Command successful")
            print(f"✓ Message: {result.message}")
            if result.time_passed > 0:
                print(f"✓ Time passed: {result.time_passed} hours")
            if hasattr(result, 'data') and result.data.get('direction'):
                print(f"✓ Direction: {result.data['direction']}")
                print(f"✓ New position: {engine.game_state.world_position.hex_id}")
        else:
            print(f"✗ Command failed: {result.message}")
    
    print("=== Action Handler Integration test complete ===")
    return engine


def test_location_system():
    """Test location entry/exit system integration"""
    print("\n=== Testing Location System ===")
    
    # Create test engine
    engine = test_game_engine()
    
    # Get connected action handler
    action_handler = engine.get_action_handler()
    
    print(f"\nStarting position: {engine.game_state.world_position.hex_id}")
    print(f"Available locations: {len(engine.game_state.world_position.available_locations)}")
    
    # Configuration for debug dumps
    ENABLE_DEBUG_DUMPS = False  # Set to True to enable location data dumps
    
    # Test location commands
    location_commands = [
        "look",           # Check current area
        "enter",          # Enter first available location
        "look",           # Look around inside location
    ]
    
    # Add debug dump if enabled
    if ENABLE_DEBUG_DUMPS:
        location_commands.append("dump_location")  # Dump location data for analysis
    
    # Continue with regular test commands
    location_commands.extend([
        "examine fireplace", # Test object examination
        "search old furniture", # Test object searching
        "take firewood",     # Test item taking
        "use fireplace",     # Test object usage
        "exit",           # Exit back to overworld
        "look",           # Confirm back in overworld
        "debug",          # Test debug command
    ])
    
    for command in location_commands:
        print(f"\n--- Testing location command: '{command}' ---")
        result = action_handler.process_command(command)
        
        if result.success:
            print(f"✓ Command successful")
            print(f"✓ Message: {result.message}")
            if result.time_passed > 0:
                print(f"✓ Time passed: {result.time_passed} hours")
            
            # Show current location status
            current_loc = engine.game_state.world_position.current_location_id
            if current_loc:
                print(f"✓ Currently in location: {current_loc}")
            else:
                print(f"✓ Currently in overworld")
        else:
            print(f"✗ Command failed: {result.message}")
    
    # Test persistence - enter location, exit, re-enter
    print(f"\n--- Testing location persistence ---")
    
    # Enter location
    result1 = action_handler.process_command("enter")
    if result1.success:
        print("✓ Entered location")
        
        # Exit location
        result2 = action_handler.process_command("exit")
        if result2.success:
            print("✓ Exited location")
            
            # Re-enter same location
            result3 = action_handler.process_command("enter")
            if result3.success:
                print("✓ Re-entered location - testing persistence")
                print(f"✓ Location data should be persistent")
            else:
                print(f"✗ Failed to re-enter: {result3.message}")
        else:
            print(f"✗ Failed to exit: {result2.message}")
    else:
        print(f"✗ Failed to enter: {result1.message}")
    
    print("=== Location System test complete ===")
    return engine


if __name__ == "__main__":
    test_location_system()
