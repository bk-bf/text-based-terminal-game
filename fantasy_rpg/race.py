"""
Fantasy RPG - Race System

Race definitions with ability bonuses and traits.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class RaceTrait:
    """A racial trait with name and description"""
    name: str
    description: str


@dataclass
class Race:
    """D&D 5e race implementation"""
    name: str
    ability_bonuses: Dict[str, int]
    size: str
    speed: int
    languages: List[str]
    traits: List[RaceTrait]
    
    def get_ability_bonus(self, ability: str) -> int:
        """Get the racial bonus for a specific ability"""
        return self.ability_bonuses.get(ability, 0)
    
    def apply_bonuses_to_character(self, character) -> None:
        """Apply racial ability bonuses to a character"""
        for ability, bonus in self.ability_bonuses.items():
            if hasattr(character, ability):
                current_value = getattr(character, ability)
                setattr(character, ability, current_value + bonus)
                print(f"Applied {self.name} {ability.upper()} bonus: +{bonus}")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Race':
        """Create Race from dictionary data"""
        traits = []
        for trait_data in data.get('traits', []):
            traits.append(RaceTrait(
                name=trait_data['name'],
                description=trait_data['description']
            ))
        
        return cls(
            name=data['name'],
            ability_bonuses=data['ability_bonuses'],
            size=data['size'],
            speed=data['speed'],
            languages=data['languages'],
            traits=traits
        )


class RaceLoader:
    """Loads race data from JSON files"""
    
    def __init__(self, data_dir: str = "fantasy_rpg/data"):
        self.data_dir = Path(data_dir)
        self._races_cache: Optional[Dict[str, Race]] = None
    
    def load_races(self) -> Dict[str, Race]:
        """Load all race definitions from races.json"""
        if self._races_cache is not None:
            return self._races_cache
        
        races_file = self.data_dir / "races.json"
        if not races_file.exists():
            print(f"Warning: {races_file} not found, using default races")
            return self._get_default_races()
        
        try:
            with open(races_file, 'r') as f:
                data = json.load(f)
            
            races = {}
            for race_key, race_data in data['races'].items():
                races[race_key] = Race.from_dict(race_data)
            
            print(f"Loaded {len(races)} races from {races_file}")
            self._races_cache = races
            return races
            
        except Exception as e:
            print(f"Error loading races from {races_file}: {e}")
            return self._get_default_races()
    
    def get_race(self, race_name: str) -> Optional[Race]:
        """Get a specific race by name (case-insensitive)"""
        races = self.load_races()
        race_key = race_name.lower()
        return races.get(race_key)
    
    def _get_default_races(self) -> Dict[str, Race]:
        """Fallback default races if JSON file is missing"""
        human = Race(
            name="Human",
            ability_bonuses={
                "strength": 1, "dexterity": 1, "constitution": 1,
                "intelligence": 1, "wisdom": 1, "charisma": 1
            },
            size="Medium",
            speed=30,
            languages=["Common"],
            traits=[RaceTrait("Extra Skill", "Gain proficiency in one additional skill")]
        )
        
        return {"human": human}


def create_character_with_race(name: str, race_name: str, character_class: str = "Fighter"):
    """Create a character and apply racial bonuses"""
    try:
        from fantasy_rpg.character import create_character
    except ImportError:
        # Handle running from within the fantasy_rpg directory
        from character import create_character
    
    # Load race data
    race_loader = RaceLoader()
    race = race_loader.get_race(race_name)
    
    if not race:
        print(f"Warning: Race '{race_name}' not found, using Human")
        race = race_loader.get_race("human")
    
    # Create base character
    character = create_character(name, race.name, character_class)
    
    # Apply racial bonuses
    print(f"\nApplying {race.name} racial bonuses:")
    race.apply_bonuses_to_character(character)
    
    # Recalculate derived stats after racial bonuses
    character.max_hp = 8 + character.ability_modifier('constitution')
    character.hp = character.max_hp
    character.armor_class = character.calculate_ac()
    
    # Display racial traits
    if race.traits:
        print(f"\n{race.name} Traits:")
        for trait in race.traits:
            print(f"  • {trait.name}: {trait.description}")
    
    print(f"\nFinal stats after racial bonuses:")
    print(f"  STR: {character.strength} ({character.ability_modifier('strength'):+d})")
    print(f"  DEX: {character.dexterity} ({character.ability_modifier('dexterity'):+d})")
    print(f"  CON: {character.constitution} ({character.ability_modifier('constitution'):+d})")
    print(f"  INT: {character.intelligence} ({character.ability_modifier('intelligence'):+d})")
    print(f"  WIS: {character.wisdom} ({character.ability_modifier('wisdom'):+d})")
    print(f"  CHA: {character.charisma} ({character.ability_modifier('charisma'):+d})")
    print(f"  HP: {character.hp}/{character.max_hp}, AC: {character.armor_class}")
    
    return character, race


# Manual testing function
def test_race_system():
    """Test race loading and character creation with racial bonuses"""
    print("=== Testing Race System ===")
    
    # Test race loading
    race_loader = RaceLoader()
    races = race_loader.load_races()
    print(f"Available races: {list(races.keys())}")
    
    # Test getting specific race
    human_race = race_loader.get_race("human")
    if human_race:
        print(f"\nHuman race loaded:")
        print(f"  Name: {human_race.name}")
        print(f"  Size: {human_race.size}, Speed: {human_race.speed}")
        print(f"  Languages: {human_race.languages}")
        print(f"  Ability bonuses: {human_race.ability_bonuses}")
        print(f"  Traits: {[trait.name for trait in human_race.traits]}")
    
    # Test character creation with race
    print(f"\n=== Creating Character with Race ===")
    character, race = create_character_with_race("Bob", "Human", "Fighter")
    
    # Verify racial bonuses were applied
    print(f"\nVerifying racial bonuses:")
    for ability, bonus in race.ability_bonuses.items():
        expected_base = 15 if ability == 'strength' else (14 if ability == 'dexterity' else (13 if ability == 'constitution' else (12 if ability == 'intelligence' else (10 if ability == 'wisdom' else 8))))
        expected_final = expected_base + bonus
        actual_value = getattr(character, ability)
        print(f"  {ability.upper()}: {expected_base} + {bonus} = {expected_final} (actual: {actual_value})")
        assert actual_value == expected_final, f"{ability} mismatch: {actual_value} != {expected_final}"
    
    print("✓ All race tests passed!")
    return character, race


if __name__ == "__main__":
    test_race_system()