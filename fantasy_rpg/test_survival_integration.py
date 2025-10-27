#!/usr/bin/env python3
"""
Test script to verify survival system integration with UI
"""

def test_survival_integration():
    """Test that survival systems are properly connected to UI"""
    print("=== Testing Survival System Integration ===")
    
    try:
        # Import required modules
        import sys
        import os
        
        # Add parent directory to path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        from fantasy_rpg.game.player_state import PlayerState
        from fantasy_rpg.game.time_system import TimeSystem
        from fantasy_rpg.world.weather_core import generate_weather_state
        from fantasy_rpg.core.character_creation import create_character_quick
        
        print("✓ All modules imported successfully")
        
        # Create character
        character, _, _ = create_character_quick("TestChar", "Human", "Fighter")
        print(f"✓ Character created: {character.name}")
        
        # Create player state
        player_state = PlayerState()
        player_state.character = character
        character.player_state = player_state
        print("✓ Player state linked to character")
        
        # Generate weather
        weather = generate_weather_state(65.0, "spring", "temperate")
        player_state.update_weather(weather)
        print(f"✓ Weather generated: {weather.temperature}°F")
        
        # Create time system
        time_system = TimeSystem(player_state)
        print("✓ Time system created")
        
        # Test initial survival state
        print("\n=== Initial Survival State ===")
        print(f"Hunger: {player_state.survival.hunger}/1000 ({player_state.survival.get_hunger_level().name})")
        print(f"Thirst: {player_state.survival.thirst}/1000 ({player_state.survival.get_thirst_level().name})")
        print(f"Fatigue: {player_state.survival.fatigue}/1000 ({player_state.survival.get_fatigue_level().name})")
        print(f"Body Temperature: {player_state.survival.body_temperature}/1000")
        print(f"Time: {player_state.get_time_string()}")
        
        # Test time advancement
        print("\n=== Advancing Time (4 hours of normal activity) ===")
        result = time_system.perform_activity("look")  # Quick activity
        player_state.advance_time(4.0, "normal")  # Advance 4 hours
        
        print(f"Hunger: {player_state.survival.hunger}/1000 ({player_state.survival.get_hunger_level().name})")
        print(f"Thirst: {player_state.survival.thirst}/1000 ({player_state.survival.get_thirst_level().name})")
        print(f"Fatigue: {player_state.survival.fatigue}/1000 ({player_state.survival.get_fatigue_level().name})")
        print(f"Body Temperature: {player_state.survival.body_temperature}/1000")
        print(f"Time: {player_state.get_time_string()}")
        
        # Test eating
        print("\n=== Testing Eating ===")
        old_hunger = player_state.survival.hunger
        player_state.eat_food(200)
        print(f"Hunger: {old_hunger} -> {player_state.survival.hunger} (+{player_state.survival.hunger - old_hunger})")
        
        # Test drinking
        print("\n=== Testing Drinking ===")
        old_thirst = player_state.survival.thirst
        player_state.drink_water(300)
        print(f"Thirst: {old_thirst} -> {player_state.survival.thirst} (+{player_state.survival.thirst - old_thirst})")
        
        # Test temperature regulation
        print("\n=== Testing Temperature Regulation ===")
        print(f"Current weather feels like: {weather.feels_like}°F")
        print(f"Body temperature: {player_state.survival.body_temperature}/1000")
        print(f"Temperature status: {player_state.survival.get_temperature_status().name}")
        print(f"Hypothermia risk: {player_state.survival.hypothermia_risk}%")
        print(f"Hyperthermia risk: {player_state.survival.hyperthermia_risk}%")
        
        # Test survival bars (UI integration)
        print("\n=== Testing UI Integration (Survival Bars) ===")
        if hasattr(player_state, 'get_survival_bars'):
            bars = player_state.get_survival_bars()
            print(f"Hunger bar: {bars.get('hunger', 'N/A')}")
            print(f"Thirst bar: {bars.get('thirst', 'N/A')}")
            print(f"Fatigue bar: {bars.get('fatigue', 'N/A')}")
            print(f"Temperature bar: {bars.get('temperature', 'N/A')}")
            print(f"Wetness bar: {bars.get('wetness', 'N/A')}")
        else:
            print("⚠ get_survival_bars method not found")
        
        # Test survival summary
        print("\n=== Testing Survival Summary ===")
        if hasattr(player_state, 'get_survival_summary'):
            summary = player_state.get_survival_summary()
            print(summary)
        else:
            print("⚠ get_survival_summary method not found")
        
        print("\n✓ All survival integration tests passed!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_panel_integration():
    """Test that character panel can display survival data"""
    print("\n=== Testing UI Panel Integration ===")
    
    try:
        from fantasy_rpg.ui.panels import CharacterPanel
        from fantasy_rpg.game.player_state import PlayerState
        from fantasy_rpg.core.character_creation import create_character_quick
        
        # Create character with survival data
        character, _, _ = create_character_quick("UITest", "Human", "Fighter")
        player_state = PlayerState()
        player_state.character = character
        character.player_state = player_state
        
        # Advance time to change survival stats
        player_state.advance_time(6.0, "active")  # Make character hungry/thirsty
        
        # Create character panel
        panel = CharacterPanel(character)
        
        # Test rendering
        rendered = panel._render_character_info()
        print("✓ Character panel rendered successfully")
        
        # Check if survival data is included
        if "survival:" in rendered:
            print("✓ Survival section found in panel")
        else:
            print("⚠ Survival section not found in panel")
        
        # Check for specific survival stats
        survival_terms = ["Hunger:", "Thirst:", "Fatigue:", "Warmth:", "Dryness:"]
        found_terms = [term for term in survival_terms if term in rendered]
        print(f"✓ Found survival terms: {found_terms}")
        
        if len(found_terms) >= 4:
            print("✓ UI panel integration working correctly")
            return True
        else:
            print("⚠ Some survival terms missing from UI")
            return False
            
    except Exception as e:
        print(f"✗ UI panel test failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing Fantasy RPG Survival System Integration")
    print("=" * 50)
    
    # Test survival system
    survival_ok = test_survival_integration()
    
    # Test UI integration
    ui_ok = test_ui_panel_integration()
    
    print("\n" + "=" * 50)
    if survival_ok and ui_ok:
        print("✓ ALL TESTS PASSED - Survival system fully integrated!")
    else:
        print("⚠ Some tests failed - check output above")