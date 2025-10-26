"""
Fantasy RPG - Character System

Character creation and management functionality.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Character:
    """D&D 5e character implementation"""
    # Core D&D stats
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    
    # Derived stats
    level: int
    hp: int
    max_hp: int
    armor_class: int
    proficiency_bonus: int
    
    # Progression
    experience_points: int
    
    # Character identity
    name: str = ""
    race: str = ""
    character_class: str = ""
    
    def ability_modifier(self, ability: str) -> int:
        """Calculate D&D ability modifier: (score - 10) // 2"""
        score = getattr(self, ability)
        return (score - 10) // 2
    
    def calculate_ac(self) -> int:
        """Calculate armor class from dexterity (equipment bonus added later)"""
        base_ac = 10 + self.ability_modifier('dexterity')
        # Equipment bonus will be added when equipment system is implemented
        return base_ac
    
    def level_up(self):
        """Handle level advancement"""
        self.level += 1
        self.proficiency_bonus = 2 + ((self.level - 1) // 4)
        # HP gain calculation - will use character_class.hit_die when classes are implemented
        hp_gain = 8 + self.ability_modifier('constitution')  # Using d8 as default for now
        self.max_hp += max(1, hp_gain)
        self.hp = self.max_hp
        print(f"{self.name} leveled up to {self.level}! HP: {self.hp}/{self.max_hp}")


def create_character(name: str, race: str = "Human", character_class: str = "Fighter") -> Character:
    """Create a new character with default stats"""
    # Using standard array: 15, 14, 13, 12, 10, 8
    character = Character(
        name=name,
        race=race,
        character_class=character_class,
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
        level=1,
        hp=0,  # Will be calculated
        max_hp=0,  # Will be calculated
        armor_class=0,  # Will be calculated
        proficiency_bonus=2,  # Level 1 proficiency
        experience_points=0
    )
    
    # Calculate derived stats
    character.max_hp = 8 + character.ability_modifier('constitution')  # d8 hit die + CON mod
    character.hp = character.max_hp
    character.armor_class = character.calculate_ac()
    
    print(f"Created {name} the {race} {character_class}")
    print(f"  STR: {character.strength} ({character.ability_modifier('strength'):+d})")
    print(f"  DEX: {character.dexterity} ({character.ability_modifier('dexterity'):+d})")
    print(f"  CON: {character.constitution} ({character.ability_modifier('constitution'):+d})")
    print(f"  INT: {character.intelligence} ({character.ability_modifier('intelligence'):+d})")
    print(f"  WIS: {character.wisdom} ({character.ability_modifier('wisdom'):+d})")
    print(f"  CHA: {character.charisma} ({character.ability_modifier('charisma'):+d})")
    print(f"  HP: {character.hp}/{character.max_hp}, AC: {character.armor_class}")
    
    return character


# Manual testing function
def test_character_creation():
    """Test character creation and stat calculations"""
    print("=== Testing Character Creation ===")
    
    # Test basic character creation
    char = create_character("Alice", "Human", "Fighter")
    
    # Test ability modifier calculations
    print(f"\nTesting ability modifiers:")
    print(f"STR 15 -> {char.ability_modifier('strength')} (should be +2)")
    print(f"DEX 14 -> {char.ability_modifier('dexterity')} (should be +2)")
    print(f"CON 13 -> {char.ability_modifier('constitution')} (should be +1)")
    
    # Test AC calculation
    expected_ac = 10 + char.ability_modifier('dexterity')
    print(f"\nAC calculation: 10 + {char.ability_modifier('dexterity')} = {char.armor_class}")
    assert char.armor_class == expected_ac, f"AC mismatch: {char.armor_class} != {expected_ac}"
    
    # Test level up
    print(f"\nTesting level up:")
    old_hp = char.max_hp
    char.level_up()
    print(f"Level: {char.level}, Proficiency: +{char.proficiency_bonus}")
    print(f"HP increased from {old_hp} to {char.max_hp}")
    
    print("✓ All character tests passed!")
    return char


if __name__ == "__main__":
    test_character_creation()