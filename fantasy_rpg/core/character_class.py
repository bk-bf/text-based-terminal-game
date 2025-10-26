"""
Fantasy RPG - Character Class System

Character class definitions with hit dice, proficiencies, and starting equipment.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class SkillProficiencies:
    """Skill proficiency selection rules"""
    choose: int  # Number of skills to choose
    from_list: List[str]  # Available skills to choose from


@dataclass
class StartingEquipment:
    """Starting equipment item"""
    item: str
    quantity: int


@dataclass
class CharacterClass:
    """D&D 5e character class implementation"""
    name: str
    hit_die: int  # Hit die size (d6=6, d8=8, d10=10, d12=12)
    primary_ability: str  # Primary ability score
    saving_throw_proficiencies: List[str]  # Proficient saving throws
    skill_proficiencies: SkillProficiencies  # Skill selection rules
    starting_equipment: List[StartingEquipment]  # Starting gear
    
    def get_hit_points_at_level(self, level: int, constitution_modifier: int) -> int:
        """Calculate hit points for this class at given level"""
        if level == 1:
            # First level gets max hit die + CON modifier
            return self.hit_die + constitution_modifier
        else:
            # Subsequent levels get average of hit die + CON modifier
            # Average of die = (die_size + 1) / 2
            average_roll = (self.hit_die + 1) // 2
            base_hp = self.hit_die + constitution_modifier  # Level 1 HP
            additional_hp = (level - 1) * (average_roll + constitution_modifier)
            return base_hp + additional_hp
    
    def get_proficiency_bonus(self, level: int) -> int:
        """Calculate proficiency bonus for given level"""
        return 2 + ((level - 1) // 4)
    
    def is_proficient_in_saving_throw(self, ability: str) -> bool:
        """Check if this class is proficient in a saving throw"""
        return ability in self.saving_throw_proficiencies
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CharacterClass':
        """Create CharacterClass from dictionary data"""
        skill_prof_data = data['skill_proficiencies']
        skill_proficiencies = SkillProficiencies(
            choose=skill_prof_data['choose'],
            from_list=skill_prof_data['from']
        )
        
        starting_equipment = []
        for eq_data in data['starting_equipment']:
            starting_equipment.append(StartingEquipment(
                item=eq_data['item'],
                quantity=eq_data['quantity']
            ))
        
        return cls(
            name=data['name'],
            hit_die=data['hit_die'],
            primary_ability=data['primary_ability'],
            saving_throw_proficiencies=data['saving_throw_proficiencies'],
            skill_proficiencies=skill_proficiencies,
            starting_equipment=starting_equipment
        )


class ClassLoader:
    """Loads character class data from JSON files"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Try to find the data directory relative to this file
            current_dir = Path(__file__).parent
            if (current_dir / "data").exists():
                self.data_dir = current_dir / "data"
            elif (current_dir.parent / "fantasy_rpg" / "data").exists():
                self.data_dir = current_dir.parent / "fantasy_rpg" / "data"
            else:
                self.data_dir = Path("fantasy_rpg/data")
        else:
            self.data_dir = Path(data_dir)
        self._classes_cache: Optional[Dict[str, CharacterClass]] = None
    
    def load_classes(self) -> Dict[str, CharacterClass]:
        """Load all class definitions from classes.json"""
        if self._classes_cache is not None:
            return self._classes_cache
        
        classes_file = self.data_dir / "classes.json"
        if not classes_file.exists():
            print(f"Warning: {classes_file} not found, using default classes")
            return self._get_default_classes()
        
        try:
            with open(classes_file, 'r') as f:
                data = json.load(f)
            
            classes = {}
            for class_key, class_data in data['classes'].items():
                classes[class_key] = CharacterClass.from_dict(class_data)
            
            print(f"Loaded {len(classes)} classes from {classes_file}")
            self._classes_cache = classes
            return classes
            
        except Exception as e:
            print(f"Error loading classes from {classes_file}: {e}")
            return self._get_default_classes()
    
    def get_class(self, class_name: str) -> Optional[CharacterClass]:
        """Get a specific class by name (case-insensitive)"""
        classes = self.load_classes()
        class_key = class_name.lower()
        return classes.get(class_key)
    
    def _get_default_classes(self) -> Dict[str, CharacterClass]:
        """Fallback default classes if JSON file is missing"""
        fighter = CharacterClass(
            name="Fighter",
            hit_die=10,
            primary_ability="strength",
            saving_throw_proficiencies=["strength", "constitution"],
            skill_proficiencies=SkillProficiencies(
                choose=2,
                from_list=["Acrobatics", "Animal Handling", "Athletics", "History", 
                          "Insight", "Intimidation", "Perception", "Survival"]
            ),
            starting_equipment=[
                StartingEquipment("chain_mail", 1),
                StartingEquipment("longsword", 1),
                StartingEquipment("shield", 1)
            ]
        )
        
        return {"fighter": fighter}


def apply_class_to_character(character, character_class: CharacterClass):
    """Apply class features to a character"""
    print(f"\nApplying {character_class.name} class features:")
    
    # Update character class name
    character.character_class = character_class.name
    
    # Recalculate all derived stats using the new class
    print(f"  Recalculating derived stats with d{character_class.hit_die} hit die...")
    character.recalculate_derived_stats(character_class)
    
    # Initialize skill proficiencies if not already present
    if character.skill_proficiencies is None:
        try:
            from .skills import SkillProficiencies
        except ImportError:
            from skills import SkillProficiencies
        character.skill_proficiencies = SkillProficiencies()
    
    # Apply class skill proficiencies (for now, auto-select based on class)
    class_skills = _get_default_class_skills(character_class)
    print(f"  Skill Proficiencies: Automatically selected {len(class_skills)} skills:")
    for skill in class_skills:
        character.add_skill_proficiency(skill)
        print(f"    • {skill}")
    
    # Display saving throw proficiencies
    print(f"  Saving Throw Proficiencies: {', '.join(character_class.saving_throw_proficiencies)}")
    
    # Display starting equipment
    print(f"  Starting Equipment:")
    for equipment in character_class.starting_equipment:
        print(f"    • {equipment.item} x{equipment.quantity}")
    
    return character


def _get_default_class_skills(character_class: CharacterClass) -> List[str]:
    """Get default skill selection for a class (for automatic character creation)"""
    available_skills = character_class.skill_proficiencies.from_list
    num_to_choose = character_class.skill_proficiencies.choose
    
    # Smart selection based on class type
    class_priorities = {
        "Fighter": ["Athletics", "Intimidation", "Perception", "Survival"],
        "Rogue": ["Stealth", "Sleight of Hand", "Perception", "Investigation"],
        "Cleric": ["Insight", "Medicine", "Persuasion", "Religion"],
        "Wizard": ["Arcana", "Investigation", "History", "Medicine"]
    }
    
    priority_skills = class_priorities.get(character_class.name, [])
    selected_skills = []
    
    # First, select priority skills that are available
    for skill in priority_skills:
        if skill in available_skills and len(selected_skills) < num_to_choose:
            selected_skills.append(skill)
    
    # Fill remaining slots with other available skills
    for skill in available_skills:
        if skill not in selected_skills and len(selected_skills) < num_to_choose:
            selected_skills.append(skill)
    
    return selected_skills[:num_to_choose]


def create_character_with_class(name: str, race_name: str = "Human", class_name: str = "Fighter"):
    """Create a character with race and class applied"""
    try:
        from .race import create_character_with_race
    except ImportError:
        # Handle running from within the fantasy_rpg directory
        from race import create_character_with_race
    
    # Create character with race
    character, race = create_character_with_race(name, race_name, class_name)
    
    # Load and apply class
    class_loader = ClassLoader()
    char_class = class_loader.get_class(class_name)
    
    if not char_class:
        print(f"Warning: Class '{class_name}' not found, using Fighter")
        char_class = class_loader.get_class("fighter")
    
    # Apply class features
    character = apply_class_to_character(character, char_class)
    
    print(f"\nFinal character summary:")
    print(f"  Name: {character.name}")
    print(f"  Race: {character.race}")
    print(f"  Class: {character.character_class}")
    print(f"  Level: {character.level}")
    print(f"  HP: {character.hp}/{character.max_hp}")
    print(f"  AC: {character.armor_class}")
    print(f"  Proficiency Bonus: +{character.proficiency_bonus}")
    
    return character, race, char_class


# Manual testing function
def test_character_class_system():
    """Test character class loading and application"""
    print("=== Testing Character Class System ===")
    
    # Test class loading
    class_loader = ClassLoader()
    classes = class_loader.load_classes()
    print(f"Available classes: {list(classes.keys())}")
    
    # Test getting specific class
    fighter_class = class_loader.get_class("fighter")
    if fighter_class:
        print(f"\nFighter class loaded:")
        print(f"  Name: {fighter_class.name}")
        print(f"  Hit Die: d{fighter_class.hit_die}")
        print(f"  Primary Ability: {fighter_class.primary_ability}")
        print(f"  Saving Throws: {fighter_class.saving_throw_proficiencies}")
        print(f"  Skill Options: Choose {fighter_class.skill_proficiencies.choose} from {len(fighter_class.skill_proficiencies.from_list)} skills")
        print(f"  Starting Equipment: {len(fighter_class.starting_equipment)} items")
    
    # Test HP calculation at different levels
    print(f"\nTesting HP calculation (CON modifier +1):")
    for level in [1, 2, 3, 5]:
        hp = fighter_class.get_hit_points_at_level(level, 1)
        prof_bonus = fighter_class.get_proficiency_bonus(level)
        print(f"  Level {level}: {hp} HP, +{prof_bonus} proficiency")
    
    # Test character creation with class
    print(f"\n=== Creating Character with Class ===")
    character, race, char_class = create_character_with_class("Charlie", "Human", "Fighter")
    
    # Verify class features were applied
    print(f"\nVerifying class application:")
    expected_hp = char_class.get_hit_points_at_level(1, character.ability_modifier('constitution'))
    print(f"  Expected HP: {expected_hp}, Actual HP: {character.max_hp}")
    assert character.max_hp == expected_hp, f"HP mismatch: {character.max_hp} != {expected_hp}"
    
    expected_prof = char_class.get_proficiency_bonus(character.level)
    print(f"  Expected Proficiency: +{expected_prof}, Actual: +{character.proficiency_bonus}")
    assert character.proficiency_bonus == expected_prof, f"Proficiency mismatch: {character.proficiency_bonus} != {expected_prof}"
    
    print("✓ All character class tests passed!")
    return character, race, char_class


if __name__ == "__main__":
    test_character_class_system()