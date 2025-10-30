#!/usr/bin/env python3
"""
Test script for improved save/load functionality
"""

import sys
import os
import json

# Add fantasy_rpg to path
sys.path.insert(0, '.')

def test_save_load():
    """Test the improved save/load functionality"""
    print("=== Testing Improved Save/Load System ===")
    
    try:
        # Import required modules
        from fantasy_rpg.game.game_engine import GameEngine
        from fantasy_rpg.core.character_creation import create_character_quick
        
        print("✓ Imports successful")
        
        # Create GameEngine
        engine = GameEngine()
        print("✓ GameEngine created")
        
        # Create test character
        character, race, char_class = create_character_quick('TestHero', 'Human', 'Fighter')
        print("✓ Test character created")
        print(f"  Character has {len(character.inventory.items)} inventory items")
        
        # Debug: Show what's in the inventory
        if character.inventory and character.inventory.items:
            print("  Inventory contents:")
            for item in character.inventory.items:
                print(f"    - {item.name} x{item.quantity}")
        else:
            print("  ⚠ Inventory is empty or None")
        
        # Start new game
        game_state = engine.new_game(character, world_seed=54321)
        print(f"✓ New game started at {game_state.world_position.hex_data['name']}")
        print(f"  Starting hex: {game_state.world_position.hex_id}")
        
        # Move player to change state
        success, message = engine.move_player("north")
        if success:
            print(f"✓ Moved north to hex: {game_state.world_position.hex_id}")
        else:
            print(f"✗ Movement failed: {message}")
        
        # Save the game
        print("\n--- Testing Save ---")
        success, message = engine.save_game("test_save")
        if success:
            print(f"✓ Save successful: {message}")
        else:
            print(f"✗ Save failed: {message}")
            return False
        
        # Check if save file exists and analyze it
        if os.path.exists("test_save.json"):
            print("✓ Save file created")
            
            # Show file size
            size = os.path.getsize("test_save.json")
            print(f"✓ Save file size: {size} bytes")
            
            # Analyze save file contents
            with open("test_save.json", 'r') as f:
                save_data = json.load(f)
            
            print("\n--- Analyzing Save File ---")
            
            # Check inventory
            inventory = save_data["character"]["inventory"]
            print(f"✓ Character inventory: {len(inventory)} items")
            if inventory:
                for item in inventory[:3]:  # Show first 3 items
                    print(f"  - {item['name']} x{item['quantity']}")
            
            # Check world data
            world_data = save_data["world_data"]
            if "hex_data" in world_data:
                hex_count = len(world_data["hex_data"])
                print(f"✓ World data: {hex_count} hexes saved")
            else:
                print("✗ No hex data in world_data")
            
            # Check coordinates consistency
            world_hex = save_data["world_position"]["hex_id"]
            player_hex = save_data["player_state"]["location"]["current_hex"]
            print(f"✓ World position hex: {world_hex}")
            print(f"✓ Player state hex: {player_hex}")
            if world_hex == player_hex:
                print("✓ Hex coordinates are consistent")
            else:
                print("⚠ Hex coordinate mismatch detected")
            
            # Check time system
            game_time = save_data["game_time"]
            player_time = save_data["player_state"]["game_time"]
            print(f"✓ Game time: Day {game_time['day']}, {game_time['hour']}:{game_time['minute']:02d}")
            print(f"✓ Player time: Day {player_time['game_day']}, {player_time['game_hour']:.1f}h")
                
        else:
            print("✗ Save file not found")
            return False
        
        # Create new engine to test loading
        print("\n--- Testing Load ---")
        new_engine = GameEngine()
        
        success, message = new_engine.load_game("test_save")
        if success:
            print(f"✓ Load successful: {message}")
        else:
            print(f"✗ Load failed: {message}")
            return False
        
        # Verify loaded state with detailed comparison
        loaded_state = new_engine.game_state
        print(f"✓ Loaded character: {loaded_state.character.name}")
        print(f"✓ Loaded location: {loaded_state.world_position.hex_data['name']}")
        print(f"✓ Loaded hex: {loaded_state.world_position.hex_id}")
        print(f"✓ Loaded time: {loaded_state.game_time.get_time_string()}")
        print(f"✓ Loaded inventory: {len(loaded_state.character.inventory.items)} items")
        
        # Show loaded inventory contents
        if loaded_state.character.inventory.items:
            print("  Loaded inventory contents:")
            for item in loaded_state.character.inventory.items:
                print(f"    - {item.name} x{item.quantity}")
        else:
            print("  ⚠ Loaded inventory is empty!")
        
        print("\n--- Detailed State Comparison ---")
        
        # Character stats comparison
        orig_char = game_state.character
        load_char = loaded_state.character
        print(f"Character Stats:")
        print(f"  Name: {orig_char.name} → {load_char.name} {'✓' if orig_char.name == load_char.name else '✗'}")
        print(f"  HP: {orig_char.hp}/{orig_char.max_hp} → {load_char.hp}/{load_char.max_hp} {'✓' if orig_char.hp == load_char.hp else '✗'}")
        print(f"  STR: {orig_char.strength} → {load_char.strength} {'✓' if orig_char.strength == load_char.strength else '✗'}")
        print(f"  Level: {orig_char.level} → {load_char.level} {'✓' if orig_char.level == load_char.level else '✗'}")
        
        # Inventory comparison
        orig_inv_count = len(orig_char.inventory.items)
        load_inv_count = len(load_char.inventory.items)
        print(f"Inventory: {orig_inv_count} items → {load_inv_count} items {'✓' if orig_inv_count == load_inv_count else '✗'}")
        
        # Time comparison
        orig_time = game_state.game_time
        load_time = loaded_state.game_time
        orig_player_time = game_state.player_state
        load_player_time = loaded_state.player_state
        print(f"Game Time: Day {orig_time.day}, {orig_time.hour}:{orig_time.minute:02d} → Day {load_time.day}, {load_time.hour}:{load_time.minute:02d}")
        print(f"Player Time: Day {orig_player_time.game_day}, {orig_player_time.game_hour:.1f}h → Day {load_player_time.game_day}, {load_player_time.game_hour:.1f}h")
        
        # Location comparison
        orig_hex = game_state.world_position.hex_id
        load_hex = loaded_state.world_position.hex_id
        print(f"Location: {orig_hex} → {load_hex} {'✓' if orig_hex == load_hex else '✗'}")
        
        # Overall verification
        stats_match = (orig_char.name == load_char.name and 
                      orig_char.hp == load_char.hp and 
                      orig_char.strength == load_char.strength)
        inventory_match = orig_inv_count == load_inv_count
        location_match = orig_hex == load_hex
        
        if stats_match and inventory_match and location_match:
            print("✓ Complete state preservation verified")
        else:
            print("✗ State preservation failed:")
            if not stats_match:
                print("  - Character stats mismatch")
            if not inventory_match:
                print("  - Inventory count mismatch")
            if not location_match:
                print("  - Location mismatch")
            return False
        
        # Test world data preservation
        if hasattr(new_engine.world_coordinator, 'hex_data'):
            loaded_hex_count = len(new_engine.world_coordinator.hex_data)
            print(f"✓ Loaded world data: {loaded_hex_count} hexes")
        else:
            print("⚠ No world data loaded")
        
        # Also create save.json to test real startup behavior
        print("\n--- Testing Real Startup Behavior ---")
        success, message = engine.save_game("save")
        if success:
            print(f"✓ Created save.json for startup testing: {message}")
        else:
            print(f"✗ Failed to create save.json: {message}")
        
        # Clean up test files
        os.remove("test_save.json")
        print("✓ Test file cleaned up")
        print("✓ save.json created for real game startup testing")
        
        # Test what happens when we start fresh with existing save.json
        print("\n--- Testing Fresh Start with Existing save.json ---")
        fresh_engine = GameEngine()
        
        # Check if save.json exists
        if os.path.exists("save.json"):
            print("✓ save.json exists for fresh startup test")
            
            # Load the save file
            success, message = fresh_engine.load_game("save")
            if success:
                print(f"✓ Fresh engine loaded save.json: {message}")
                
                # Check world data count
                if hasattr(fresh_engine.world_coordinator, 'hex_data'):
                    fresh_hex_count = len(fresh_engine.world_coordinator.hex_data)
                    print(f"✓ Fresh engine world data: {fresh_hex_count} hexes")
                    
                    if fresh_hex_count == 400:
                        print("✓ No duplicate world generation detected!")
                    elif fresh_hex_count == 800:
                        print("⚠ Duplicate world generation detected - 800 hexes instead of 400")
                    else:
                        print(f"⚠ Unexpected hex count: {fresh_hex_count}")
                else:
                    print("⚠ No world data found in fresh engine")
            else:
                print(f"✗ Fresh engine failed to load save.json: {message}")
        
        # Clean up save.json
        if os.path.exists("save.json"):
            os.remove("save.json")
            print("✓ save.json cleaned up")
        
        print("\n=== Improved Save/Load Test PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_save_load()
    sys.exit(0 if success else 1)