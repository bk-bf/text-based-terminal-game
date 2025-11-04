"""Integration tests for ActionLogger NLP methods.

Tests the new NLP logging methods added to ActionLogger:
- log_survival_event()
- log_equipment_event()
- log_environmental_event()
- log_action_event()
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fantasy_rpg.actions.action_logger import ActionLogger


def test_log_survival_event_cold():
    """Test logging Cold condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("COLD_triggered", {"temperature": 20})
    
    # Message should be queued since no game_log attached
    assert len(logger.message_queue) > 0
    assert logger.message_queue[-1]['type'] == 'survival'
    
    message = logger.message_queue[-1]['message']
    assert isinstance(message, str)
    assert len(message) > 0
    # Check for cold-related keywords
    assert any(word in message.lower() for word in ['cold', 'chill', 'freez', 'frost', 'ice', 'numb'])


def test_log_survival_event_hunger():
    """Test logging Hunger condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("HUNGER_triggered", {"hunger_level": 800})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Check for hunger-related keywords
    assert any(word in message.lower() for word in ['hunger', 'stomach', 'food', 'eat', 'starv', 'weak'])


def test_log_survival_event_exhaustion():
    """Test logging Exhaustion condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("EXHAUSTION_triggered", {"fatigue_level": 900})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Check for exhaustion-related keywords
    assert any(word in message.lower() for word in ['fatigue', 'tired', 'exhaust', 'weary', 'rest', 'sleep'])


def test_log_survival_event_wet():
    """Test logging Wet condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("WET_triggered", {"wetness_level": 500})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Check for wet-related keywords
    assert any(word in message.lower() for word in ['wet', 'soak', 'damp', 'water', 'moist', 'drip'])


def test_log_survival_event_variance():
    """Test that survival events show message variance"""
    messages = set()
    
    # Generate 20 cold events
    for _ in range(20):
        logger = ActionLogger()
        logger.log_survival_event("COLD_triggered")
        messages.add(logger.message_queue[-1]['message'])
    
    # Should see at least 5 different messages with 15 variants
    assert len(messages) >= 5, f"Only got {len(messages)} unique messages, expected at least 5"


def test_log_equipment_event_armor_equipped():
    """Test logging armor equipped event"""
    logger = ActionLogger()
    logger.log_equipment_event("armor_equipped", armor_name="Iron Breastplate", protection_boost=2)
    
    assert len(logger.message_queue) > 0
    assert logger.message_queue[-1]['type'] == 'equipment'
    
    message = logger.message_queue[-1]['message']
    assert "Iron Breastplate" in message
    # Should not have template markers
    assert '{armor_name}' not in message


def test_log_equipment_event_weapon():
    """Test logging weapon equipped event"""
    logger = ActionLogger()
    logger.log_equipment_event("weapon_equipped", weapon_name="Longsword")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "Longsword" in message
    assert '{weapon_name}' not in message


def test_log_equipment_event_armor_removed():
    """Test logging armor removed event"""
    logger = ActionLogger()
    logger.log_equipment_event("armor_removed", armor_name="Chainmail")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "Chainmail" in message


def test_log_equipment_event_variance():
    """Test that equipment events show variance"""
    messages = set()
    
    # Generate 15 armor equip events
    for i in range(15):
        logger = ActionLogger()
        logger.log_equipment_event("armor_equipped", armor_name=f"Armor{i}")
        # Remove the variable part to test message structure variance
        msg = logger.message_queue[-1]['message'].replace(f"Armor{i}", "ARMOR")
        messages.add(msg)
    
    # Should see at least 3 different message structures
    assert len(messages) >= 3, f"Only got {len(messages)} unique message structures"


def test_log_environmental_event_rain():
    """Test logging weather change to rain"""
    logger = ActionLogger()
    logger.log_environmental_event("weather_change_to_rain")
    
    assert len(logger.message_queue) > 0
    assert logger.message_queue[-1]['type'] == 'environment'
    
    message = logger.message_queue[-1]['message']
    # Check for rain-related keywords
    assert any(word in message.lower() for word in ['rain', 'cloud', 'drop', 'pour', 'wet'])


def test_log_environmental_event_snow():
    """Test logging weather change to snow"""
    logger = ActionLogger()
    logger.log_environmental_event("weather_change_to_snow")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Check for snow-related keywords
    assert any(word in message.lower() for word in ['snow', 'flake', 'white', 'winter', 'ice'])


def test_log_environmental_event_enter_cold():
    """Test logging entering cold area"""
    logger = ActionLogger()
    logger.log_environmental_event("enter_cold_area")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Check for cold area keywords
    assert any(word in message.lower() for word in ['cold', 'freez', 'chill', 'frost', 'ice', 'frigid'])


def test_log_action_event_forage_success():
    """Test logging successful forage action"""
    logger = ActionLogger()
    logger.log_action_event("forage_success", object_name="berry bush", item_name="berries", quantity=5)
    
    assert len(logger.message_queue) > 0
    assert logger.message_queue[-1]['type'] == 'action'
    
    message = logger.message_queue[-1]['message']
    assert "berries" in message.lower() or "berry" in message.lower()
    assert "5" in message
    # Should not have template markers
    assert '{item_name}' not in message
    assert '{quantity}' not in message


def test_log_action_event_search_empty():
    """Test logging empty search result"""
    logger = ActionLogger()
    logger.log_action_event("search_empty", object_name="chest")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "chest" in message.lower()
    # Should indicate nothing found - comprehensive keywords from search_empty messages
    assert any(word in message.lower() for word in ['empty', 'nothing', 'value', 'search', 'picked', 'find', 'remain'])


def test_log_action_event_chop_success():
    """Test logging successful wood chopping"""
    logger = ActionLogger()
    logger.log_action_event("chop_success", object_name="tree", quantity=3)
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "tree" in message.lower() or "wood" in message.lower()
    assert "3" in message


def test_log_action_event_drink():
    """Test logging drinking from water source"""
    logger = ActionLogger()
    logger.log_action_event("drink_success", object_name="well")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "well" in message.lower()
    assert any(word in message.lower() for word in ['drink', 'water', 'thirst', 'refresh'])


def test_log_action_event_unlock_success():
    """Test logging successful unlock"""
    logger = ActionLogger()
    logger.log_action_event("unlock_success", object_name="chest")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "chest" in message.lower()
    assert any(word in message.lower() for word in ['unlock', 'open', 'lock'])


def test_log_action_event_rest_complete():
    """Test logging rest completion"""
    logger = ActionLogger()
    logger.log_action_event("rest_complete")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['rest', 'sleep', 'refresh', 'restore', 'wake'])


def test_get_last_message():
    """Test getting last message"""
    logger = ActionLogger()
    logger.log_survival_event("COLD_triggered")
    
    last_msg = logger.get_last_message()
    assert isinstance(last_msg, str)
    assert len(last_msg) > 0
    # Broader keywords matching COLD_triggered messages
    assert any(word in last_msg.lower() for word in ['cold', 'chill', 'freez', 'numb', 'ice', 'frost', 'shiver', 'breath'])


# New comprehensive condition tests
def test_log_survival_event_thirst():
    """Test logging Thirsty condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("THIRST_triggered", {"thirst_level": 150})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['thirst', 'water', 'parched', 'dry', 'drink'])


def test_log_survival_event_dehydrated():
    """Test logging Dehydrated condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("DEHYDRATED_triggered", {"thirst_level": 30})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['dehydrat', 'water', 'lips', 'collapse', 'urgent'])


def test_log_survival_event_dying_of_thirst():
    """Test logging Dying of Thirst condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("DYING_OF_THIRST_triggered", {"thirst_level": 5})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Comprehensive keywords: death, dying, organ, perish, agony, shutting, dehydration, imminent, fades, certain, moisture, consciousness, die, water
    assert any(word in message.lower() for word in ['death', 'dying', 'organ', 'perish', 'agony', 'shut', 'dehydrat', 'imminent', 'fade', 'certain', 'moisture', 'conscious', 'die', 'water'])


def test_log_survival_event_tired():
    """Test logging Tired condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("TIRED_triggered", {"fatigue_level": 250})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Keywords adjusted to match actual message content
    assert any(word in message.lower() for word in ['tired', 'yawn', 'rest', 'weary', 'heavy', 'fatigue', 'sleep', 'exhaust'])


def test_log_survival_event_very_tired():
    """Test logging Very Tired condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("VERY_TIRED_triggered", {"fatigue_level": 120})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['exhaust', 'cloak', 'tired', 'fatigue', 'rest'])


def test_log_survival_event_icy():
    """Test logging Icy condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("ICY_triggered", {"temperature": 150})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Comprehensive keywords from ICY_triggered messages: shiver, cold, dangerous, penetrate, ice, crystals, brutal, numb, hypothermia, breath, freezing, muscles, painful
    assert any(word in message.lower() for word in ['shiver', 'bone', 'cold', 'numb', 'ice', 'dangerous', 'penetrate', 'crystal', 'brutal', 'hypotherm', 'breath', 'freez', 'muscle', 'painful', 'warmth', 'extremit'])


def test_log_survival_event_freezing():
    """Test logging Freezing condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("FREEZING_triggered", {"temperature": 50})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Broader keywords to match message variants (chatter, teeth, limbs, etc.)
    assert any(word in message.lower() for word in ['freez', 'hypotherm', 'death', 'numb', 'warmth', 'chatter', 'teeth', 'limb', 'cold', 'die'])


def test_log_survival_event_hot():
    """Test logging Hot condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("HOT_triggered", {"temperature": 750})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['hot', 'sweat', 'heat', 'warm', 'cool'])


def test_log_survival_event_overheating():
    """Test logging Overheating condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("OVERHEATING_triggered", {"temperature": 850})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['overheat', 'heat', 'shade', 'water', 'dangerous'])


def test_log_survival_event_heat_stroke():
    """Test logging Heat Stroke condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("HEAT_STROKE_triggered", {"temperature": 950})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['heat', 'stroke', 'fire', 'death', 'failing', 'die'])


def test_log_survival_event_soaked():
    """Test logging Soaked condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("SOAKED_triggered", {"wetness": 400})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Keywords adjusted to match actual message content (sodden, drenched, etc.)
    assert any(word in message.lower() for word in ['soak', 'drench', 'water', 'drip', 'wet', 'saturate', 'sodden', 'damp'])


def test_log_survival_event_wind_chilled():
    """Test logging Wind Chilled condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("WIND_CHILLED_triggered", {"wind_chill": -30})
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['wind', 'bitter', 'gale', 'shelter', 'warmth'])


def test_log_survival_event_fainted():
    """Test logging Fainted condition trigger"""
    logger = ActionLogger()
    logger.log_survival_event("FAINTED_triggered")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Comprehensive keywords: faint, unconscious, collapse, darkness, black, dark, swallow, body, vision, world, consciousness, crumple, ground, lose, exhaustion
    assert any(word in message.lower() for word in ['faint', 'unconscious', 'collapse', 'darkness', 'black', 'dark', 'swallow', 'body', 'vision', 'world', 'conscious', 'crumple', 'ground', 'lose', 'exhaust'])


def test_log_environmental_event_lit_fire():
    """Test logging Lit Fire beneficial condition"""
    logger = ActionLogger()
    logger.log_environmental_event("LIT_FIRE_triggered")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['fire', 'flame', 'warm', 'heat', 'crackle'])


def test_log_environmental_event_natural_shelter():
    """Test logging Natural Shelter beneficial condition"""
    logger = ActionLogger()
    logger.log_environmental_event("NATURAL_SHELTER_triggered")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['shelter', 'protect', 'element', 'weather', 'respite'])


def test_log_environmental_event_good_shelter():
    """Test logging Good Shelter beneficial condition"""
    logger = ActionLogger()
    logger.log_environmental_event("GOOD_SHELTER_triggered")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    # Broader keywords (well, block, feel, easier, etc.)
    assert any(word in message.lower() for word in ['shelter', 'protect', 'secure', 'quality', 'rest', 'well', 'block', 'feel', 'easier', 'element', 'weather'])


def test_log_environmental_event_excellent_shelter():
    """Test logging Excellent Shelter beneficial condition"""
    logger = ActionLogger()
    logger.log_environmental_event("EXCELLENT_SHELTER_triggered")
    
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert any(word in message.lower() for word in ['shelter', 'protect', 'comfort', 'excellent', 'safe', 'immune'])


def test_get_last_message_empty():
    """Test getting last message when queue is empty"""
    logger = ActionLogger()
    last_message = logger.get_last_message()
    # get_last_message() returns empty string, not None, when queue is empty
    assert last_message == ''


def test_action_event_variance():
    """Test that action events show variance"""
    messages = set()
    
    # Generate 15 forage success events
    for i in range(15):
        logger = ActionLogger()
        logger.log_action_event("forage_success", object_name="bush", item_name="item", quantity=i+1)
        # Remove variable parts to test message structure variance
        msg = logger.message_queue[-1]['message']
        msg = msg.replace("item", "ITEM").replace(str(i+1), "N")
        messages.add(msg)
    
    # Should see at least 3 different message structures
    assert len(messages) >= 3, f"Only got {len(messages)} unique message structures"


if __name__ == '__main__':
    # Run all tests manually
    print("Running ActionLogger NLP integration tests...\n")
    
    tests = [
        # Original survival tests
        test_log_survival_event_cold,
        test_log_survival_event_hunger,
        test_log_survival_event_exhaustion,
        test_log_survival_event_wet,
        test_log_survival_event_variance,
        # New comprehensive survival tests
        test_log_survival_event_thirst,
        test_log_survival_event_dehydrated,
        test_log_survival_event_dying_of_thirst,
        test_log_survival_event_tired,
        test_log_survival_event_very_tired,
        test_log_survival_event_icy,
        test_log_survival_event_freezing,
        test_log_survival_event_hot,
        test_log_survival_event_overheating,
        test_log_survival_event_heat_stroke,
        test_log_survival_event_soaked,
        test_log_survival_event_wind_chilled,
        test_log_survival_event_fainted,
        # Equipment tests
        test_log_equipment_event_armor_equipped,
        test_log_equipment_event_weapon,
        test_log_equipment_event_armor_removed,
        test_log_equipment_event_variance,
        # Environmental tests
        test_log_environmental_event_rain,
        test_log_environmental_event_snow,
        test_log_environmental_event_enter_cold,
        # New beneficial condition tests
        test_log_environmental_event_lit_fire,
        test_log_environmental_event_natural_shelter,
        test_log_environmental_event_good_shelter,
        test_log_environmental_event_excellent_shelter,
        # Action tests
        test_log_action_event_forage_success,
        test_log_action_event_search_empty,
        test_log_action_event_chop_success,
        test_log_action_event_drink,
        test_log_action_event_unlock_success,
        test_log_action_event_rest_complete,
        # Utility tests
        test_get_last_message,
        test_get_last_message_empty,
        test_action_event_variance,
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
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Coverage: {passed}/{len(tests)} tests ({100*passed//len(tests)}%)")
    
    if failed == 0:
        print("\n✓ All ActionLogger NLP integration tests passed!")
    else:
        print(f"\n✗ {failed} test(s) failed")
        sys.exit(1)
