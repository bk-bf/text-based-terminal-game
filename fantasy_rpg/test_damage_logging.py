#!/usr/bin/env python3
"""
Test damage logging in the action logger
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import fantasy_rpg modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from fantasy_rpg.core.character import Character
from fantasy_rpg.game.player_state import PlayerState
from fantasy_rpg.game.time_system import TimeSystem
from fantasy_rpg.ui.action_logger import ActionLogger


class MockGameLogPanel:
    """Mock game log panel for testing"""
    
    def __init__(self):
        self.messages = []
        self.combat_messages = []
        self.commands = []
    
    def add_message(self, message: str):
        self.messages.append(message)
        print(f"LOG: {message}")
    
    def add_combat_message(self, message: str):
        self.combat_messages.append(message)
        print(f"COMBAT: {message}")
    
    def add_command(self, command: str):
        self.commands.append(command)
        print(f"CMD: {command}")
    
    def add_level_up_message(self, message: str):
        self.messages.append(message)
        print(f"LEVEL UP: {message}")


def test_damage_logging():
    """Test that damage is properly logged"""
    print("=== Testing Damage Logging ===")
    
    # Create mock game log panel
    mock_log = MockGameLogPanel()
    
    # Create action logger with mock panel
    action_logger = ActionLogger(mock_log)
    
    # Test different damage scenarios
    damage_tests = [
        (1, "cold", "Icy", 25, 24, "Light cold damage"),
        (3, "heat", "Heat Stroke", 24, 21, "Moderate heat damage"),
        (5, "starvation", "Dying of Hunger", 21, 16, "Heavy starvation damage"),
        (16, "dehydration", "Dying of Thirst", 16, 0, "Fatal dehydration damage")
    ]
    
    print("Testing damage logging with different scenarios:")
    print()
    
    for damage, damage_type, source, old_hp, new_hp, description in damage_tests:
        print(f"Test: {description}")
        print(f"  Damage: {damage} {damage_type} from {source}")
        print(f"  HP: {old_hp} → {new_hp}")
        
        action_logger.log_damage_taken(
            damage_amount=damage,
            damage_type=damage_type,
            source=source,
            old_hp=old_hp,
            new_hp=new_hp
        )
        print()
    
    # Test healing logging
    print("Testing healing logging:")
    print()
    
    healing_tests = [
        (3, "rest", 16, 19, "Healing from rest"),
        (5, "sleep", 19, 24, "Healing from sleep"),
        (1, "food", 24, 25, "Healing from food")
    ]
    
    for heal, source, old_hp, new_hp, description in healing_tests:
        print(f"Test: {description}")
        print(f"  Healing: {heal} from {source}")
        print(f"  HP: {old_hp} → {new_hp}")
        
        action_logger.log_healing_received(
            heal_amount=heal,
            source=source,
            old_hp=old_hp,
            new_hp=new_hp
        )
        print()
    
    print("✓ Damage and healing logging tests complete")


def test_damage_over_time_integration():
    """Test that damage over time integrates with action logger"""
    print("\n=== Testing Damage Over Time Integration ===")
    
    # Create character with extreme conditions
    character = Character(
        name="Damage Test",
        race="Human",
        character_class="Fighter",
        level=1,
        hp=20,
        max_hp=20,
        armor_class=15,
        proficiency_bonus=2,
        experience_points=0,
        strength=14,
        dexterity=12,
        constitution=13,
        intelligence=10,
        wisdom=11,
        charisma=8,
        base_speed=30
    )
    
    player_state = PlayerState()
    player_state.character = character
    character.player_state = player_state
    
    # Set up extreme conditions that cause damage
    player_state.survival.hunger = 500      # Normal
    player_state.survival.thirst = 500      # Normal
    player_state.survival.fatigue = 500     # Normal
    player_state.survival.body_temperature = 80  # Icy condition (should cause damage)
    player_state.survival.wetness = 100
    player_state.survival.wind_chill = 0
    player_state.survival.hypothermia_risk = 95  # High risk
    player_state.survival.hyperthermia_risk = 0
    
    # Create mock game log panel and action logger
    mock_log = MockGameLogPanel()
    action_logger = ActionLogger(mock_log)
    
    # Set the action logger globally (this is how the time system will find it)
    import fantasy_rpg.ui.action_logger as al_module
    al_module.action_logger = action_logger
    
    time_system = TimeSystem(player_state)
    
    print(f"Character in extreme cold:")
    print(f"  HP: {character.hp}/{character.max_hp}")
    print(f"  Body Temperature: {player_state.survival.body_temperature} (Icy)")
    print(f"  Hypothermia Risk: {player_state.survival.hypothermia_risk}%")
    
    print(f"\nPerforming activity that should trigger damage over time...")
    
    # Perform an activity that takes time (should trigger damage)
    result = time_system.perform_activity("short_rest")  # 30 minutes
    
    print(f"\nAfter activity:")
    print(f"  HP: {character.hp}/{character.max_hp}")
    print(f"  Activity result: {result['success']}")
    
    if character.hp < 20:
        print(f"✓ Damage was applied (HP decreased from 20 to {character.hp})")
        print(f"✓ Check above for damage logging messages")
    else:
        print(f"✗ No damage was applied (HP still {character.hp})")
    
    # Check if any combat messages were logged
    if mock_log.combat_messages:
        print(f"\n✓ Combat messages logged: {len(mock_log.combat_messages)}")
        for msg in mock_log.combat_messages:
            print(f"  - {msg}")
    else:
        print(f"\n✗ No combat messages logged")


if __name__ == "__main__":
    test_damage_logging()
    test_damage_over_time_integration()
    print("\n=== Damage Logging Testing Complete ===")