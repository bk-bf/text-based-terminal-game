"""Unit tests for MessageManager class.

Tests message loading, retrieval, template interpolation, variance,
and fallback behavior for the MessageManager.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fantasy_rpg.dialogue.message_manager import MessageManager


def test_message_manager_loads_json():
    """Test that MessageManager successfully loads the JSON file."""
    manager = MessageManager()
    assert manager.messages is not None
    assert isinstance(manager.messages, dict)
    assert 'survival_effects' in manager.messages
    assert 'equipment_effects' in manager.messages
    assert 'environmental' in manager.messages
    assert 'actions' in manager.messages


def test_get_survival_message():
    """Test that survival messages are retrieved correctly."""
    manager = MessageManager()
    msg = manager.get_survival_message('COLD_triggered')
    assert msg is not None
    assert len(msg) > 0
    assert isinstance(msg, str)
    # Check that message is descriptive (not just a fallback)
    assert len(msg) > 20  # Real messages are longer than fallbacks


def test_get_survival_message_variance():
    """Test that multiple calls return different messages (variance)."""
    manager = MessageManager()
    messages = set()
    
    # Get 20 messages - should see variance if pool has multiple variants
    for _ in range(20):
        msg = manager.get_survival_message('COLD_triggered')
        messages.add(msg)
    
    # With 15 variants, we should see at least 5 different messages in 20 tries
    assert len(messages) >= 5, "Message variance not working - too few unique messages"


def test_get_hunger_message():
    """Test hunger survival messages."""
    manager = MessageManager()
    msg = manager.get_survival_message('HUNGER_triggered')
    assert msg is not None
    assert len(msg) > 0
    # Check for hunger-related keywords
    assert any(word in msg.lower() for word in ['hunger', 'stomach', 'food', 'eat', 'starv'])


def test_get_exhaustion_message():
    """Test exhaustion survival messages."""
    manager = MessageManager()
    msg = manager.get_survival_message('EXHAUSTION_triggered')
    assert msg is not None
    assert len(msg) > 0
    # Check for exhaustion-related keywords
    assert any(word in msg.lower() for word in ['fatigue', 'tired', 'exhaust', 'weary', 'rest', 'sleep'])


def test_get_wet_message():
    """Test wet condition survival messages."""
    manager = MessageManager()
    msg = manager.get_survival_message('WET_triggered')
    assert msg is not None
    assert len(msg) > 0
    # Check for wet-related keywords
    assert any(word in msg.lower() for word in ['wet', 'soak', 'damp', 'water', 'moist'])


def test_equipment_message_interpolation():
    """Test that equipment messages interpolate template variables correctly."""
    manager = MessageManager()
    msg = manager.get_equipment_message('armor_equipped', armor_name='Iron Breastplate')
    assert msg is not None
    assert 'Iron Breastplate' in msg
    # Should not contain unsubstituted template markers
    assert '{armor_name}' not in msg


def test_weapon_equipped_message():
    """Test weapon equipped messages with template substitution."""
    manager = MessageManager()
    msg = manager.get_equipment_message('weapon_equipped', weapon_name='Longsword')
    assert msg is not None
    assert 'Longsword' in msg
    assert '{weapon_name}' not in msg


def test_equipment_message_variance():
    """Test that equipment messages show variance."""
    manager = MessageManager()
    messages = set()
    
    # Get 15 messages
    for _ in range(15):
        msg = manager.get_equipment_message('armor_equipped', armor_name='Chainmail')
        messages.add(msg)
    
    # Should see multiple variants (at least 3 in 15 tries)
    assert len(messages) >= 3, "Equipment message variance not working"


def test_armor_removed_message():
    """Test armor removal messages."""
    manager = MessageManager()
    msg = manager.get_equipment_message('armor_removed', armor_name='Leather Armor')
    assert msg is not None
    assert 'Leather Armor' in msg
    assert '{armor_name}' not in msg


def test_item_used_message():
    """Test item usage messages."""
    manager = MessageManager()
    msg = manager.get_equipment_message('item_used', item_name='Healing Potion')
    assert msg is not None
    assert 'Healing Potion' in msg


def test_environmental_message():
    """Test environmental messages are retrieved correctly."""
    manager = MessageManager()
    msg = manager.get_environmental_message('weather_change_to_rain')
    assert msg is not None
    assert len(msg) > 0
    # Check for rain-related keywords
    assert any(word in msg.lower() for word in ['rain', 'cloud', 'drop', 'pour', 'wet'])


def test_weather_change_to_snow():
    """Test snow weather messages."""
    manager = MessageManager()
    msg = manager.get_environmental_message('weather_change_to_snow')
    assert msg is not None
    assert any(word in msg.lower() for word in ['snow', 'flake', 'white', 'winter', 'ice'])


def test_enter_cold_area_message():
    """Test entering cold area messages."""
    manager = MessageManager()
    msg = manager.get_environmental_message('enter_cold_area')
    assert msg is not None
    assert any(word in msg.lower() for word in ['cold', 'freez', 'chill', 'frost', 'ice', 'frigid'])


def test_action_message_interpolation():
    """Test that action messages interpolate template variables correctly."""
    manager = MessageManager()
    msg = manager.get_action_message('forage_success', item_name='mushroom', quantity=3)
    assert msg is not None
    assert 'mushroom' in msg.lower()
    assert '3' in msg
    # Should not contain unsubstituted template markers
    assert '{item_name}' not in msg
    assert '{quantity}' not in msg


def test_forage_failure_message():
    """Test forage failure messages."""
    manager = MessageManager()
    msg = manager.get_action_message('forage_failure')
    assert msg is not None
    assert len(msg) > 0
    # Check for failure-related keywords
    assert any(word in msg.lower() for word in ['nothing', 'fail', 'no', 'unsuccessful', 'fruitless'])


def test_hunt_success_message():
    """Test hunting success messages."""
    manager = MessageManager()
    msg = manager.get_action_message('hunt_success', prey_type='deer')
    assert msg is not None
    assert 'deer' in msg.lower()
    # Check for success-related keywords
    assert any(word in msg.lower() for word in ['hunt', 'success', 'take', 'catch', 'kill', 'bring'])


def test_harvest_success_message():
    """Test harvest success messages."""
    manager = MessageManager()
    msg = manager.get_action_message('harvest_success', item_name='apple', quantity=5)
    assert msg is not None
    assert 'apple' in msg.lower()
    assert '5' in msg


def test_rest_complete_message():
    """Test rest completion messages."""
    manager = MessageManager()
    msg = manager.get_action_message('rest_complete')
    assert msg is not None
    assert any(word in msg.lower() for word in ['rest', 'sleep', 'refresh', 'restore', 'energy', 'better'])


def test_unknown_event_fallback():
    """Test that unknown events return fallback message without crashing."""
    manager = MessageManager()
    msg = manager.get_survival_message('UNKNOWN_EVENT')
    assert msg is not None
    assert len(msg) > 0
    # Should be a fallback message
    assert 'unknown event' in msg.lower()


def test_unknown_equipment_event_fallback():
    """Test fallback for unknown equipment events."""
    manager = MessageManager()
    msg = manager.get_equipment_message('unknown_equip_action')
    assert msg is not None
    assert len(msg) > 0


def test_unknown_environmental_event_fallback():
    """Test fallback for unknown environmental events."""
    manager = MessageManager()
    msg = manager.get_environmental_message('weather_change_to_unknown')
    assert msg is not None
    assert len(msg) > 0


def test_unknown_action_event_fallback():
    """Test fallback for unknown action events."""
    manager = MessageManager()
    msg = manager.get_action_message('unknown_action')
    assert msg is not None
    assert len(msg) > 0


def test_empty_message_array():
    """Test behavior when a message pool exists but is empty."""
    manager = MessageManager()
    # This would require modifying the JSON, so we test the fallback logic
    # by testing an event that might not have messages
    msg = manager.get_survival_message('NONEXISTENT_triggered')
    assert msg is not None
    # Should return a fallback, not crash


def test_missing_template_variable():
    """Test that missing template variables are handled gracefully."""
    manager = MessageManager()
    # Call with missing required template variable
    msg = manager.get_equipment_message('armor_equipped')  # Missing armor_name
    assert msg is not None
    # Message should still be returned (with template markers or graceful handling)


def test_action_message_variance():
    """Test that action messages show variance."""
    manager = MessageManager()
    messages = set()
    
    # Get 15 forage success messages
    for i in range(15):
        msg = manager.get_action_message('forage_success', item_name='berry', quantity=i+1)
        # Remove the variable parts to test message structure variance
        msg_template = msg.replace('berry', 'ITEM').replace(str(i+1), 'N')
        messages.add(msg_template)
    
    # Should see multiple variants (at least 3 in 15 tries)
    assert len(messages) >= 3, "Action message variance not working"


if __name__ == '__main__':
    # Run all tests manually
    print("Running MessageManager unit tests...\n")
    
    tests = [
        test_message_manager_loads_json,
        test_get_survival_message,
        test_get_survival_message_variance,
        test_get_hunger_message,
        test_get_exhaustion_message,
        test_get_wet_message,
        test_equipment_message_interpolation,
        test_weapon_equipped_message,
        test_equipment_message_variance,
        test_armor_removed_message,
        test_item_used_message,
        test_environmental_message,
        test_weather_change_to_snow,
        test_enter_cold_area_message,
        test_action_message_interpolation,
        test_forage_failure_message,
        test_hunt_success_message,
        test_harvest_success_message,
        test_rest_complete_message,
        test_unknown_event_fallback,
        test_unknown_equipment_event_fallback,
        test_unknown_environmental_event_fallback,
        test_unknown_action_event_fallback,
        test_empty_message_array,
        test_missing_template_variable,
        test_action_message_variance,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Coverage: {passed}/{len(tests)} tests ({100*passed//len(tests)}%)")
    
    if failed == 0:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {failed} test(s) failed")
        sys.exit(1)
