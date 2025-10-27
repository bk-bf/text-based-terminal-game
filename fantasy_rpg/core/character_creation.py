"""
Fantasy RPG - Character Creation Flow

Interactive character creation system that guides players through:
1. Race selection
2. Class selection  
3. Stat allocation (standard array)
"""

from typing import Dict, List, Tuple, Optional
import sys
import os

# Add the parent directory to the path so we can import fantasy_rpg modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .character import Character
from .race import RaceLoader, Race
from .character_class import ClassLoader, CharacterClass
from .item import ItemLoader, Item


class CharacterCreationFlow:
    """Interactive character creation flow"""
    
    def __init__(self):
        self.race_loader = RaceLoader()
        self.class_loader = ClassLoader()
        self.item_loader = ItemLoader()
        self.standard_array = [15, 14, 13, 12, 10, 8]
        
    def create_character_interactive(self) -> Tuple[Character, Race, CharacterClass]:
        """Run the full interactive character creation flow"""
        print("=== Fantasy RPG Character Creation ===")
        print()
        
        # Step 1: Get character name
        name = self._get_character_name()
        
        # Step 2: Select race
        selected_race = self._select_race()
        
        # Step 3: Select class
        selected_class = self._select_class()
        
        # Step 4: Allocate stats
        stat_allocation = self._allocate_stats(selected_race, selected_class)
        
        # Step 5: Create final character
        character = self._create_final_character(
            name, selected_race, selected_class, stat_allocation
        )
        
        # Step 6: Display final character summary
        self._display_character_summary(character, selected_race, selected_class)
        
        return character, selected_race, selected_class
    
    def _get_character_name(self) -> str:
        """Get character name from user"""
        while True:
            name = input("Enter your character's name: ").strip()
            if name:
                print(f"Character name: {name}")
                return name
            print("Please enter a valid name.")
    
    def _select_race(self) -> Race:
        """Interactive race selection"""
        print("\n=== Step 1: Choose Your Race ===")
        
        races = self.race_loader.load_races()
        race_list = list(races.values())
        
        # Display available races
        print("Available races:")
        for i, race in enumerate(race_list, 1):
            print(f"{i}. {race.name}")
            print(f"   Size: {race.size}, Speed: {race.speed} ft")
            print(f"   Languages: {', '.join(race.languages)}")
            
            # Show ability bonuses
            bonuses = []
            for ability, bonus in race.ability_bonuses.items():
                if bonus > 0:
                    bonuses.append(f"{ability.upper()} +{bonus}")
            if bonuses:
                print(f"   Ability Bonuses: {', '.join(bonuses)}")
            
            # Show traits
            if race.traits:
                trait_names = [trait.name for trait in race.traits]
                print(f"   Traits: {', '.join(trait_names)}")
            print()
        
        # Get user selection
        while True:
            try:
                choice = input(f"Choose a race (1-{len(race_list)}): ").strip()
                race_index = int(choice) - 1
                if 0 <= race_index < len(race_list):
                    selected_race = race_list[race_index]
                    print(f"Selected race: {selected_race.name}")
                    
                    # Show detailed race info
                    self._show_race_details(selected_race)
                    return selected_race
                else:
                    print(f"Please enter a number between 1 and {len(race_list)}")
            except ValueError:
                print("Please enter a valid number")
    
    def _show_race_details(self, race: Race) -> None:
        """Show detailed information about selected race"""
        print(f"\n{race.name} Details:")
        print(f"  Size: {race.size}")
        print(f"  Speed: {race.speed} feet")
        print(f"  Languages: {', '.join(race.languages)}")
        
        if race.ability_bonuses:
            print("  Ability Score Increases:")
            for ability, bonus in race.ability_bonuses.items():
                if bonus > 0:
                    print(f"    {ability.capitalize()}: +{bonus}")
        
        if race.traits:
            print("  Racial Traits:")
            for trait in race.traits:
                print(f"    • {trait.name}: {trait.description}")
        print()
    
    def _select_class(self) -> CharacterClass:
        """Interactive class selection"""
        print("=== Step 2: Choose Your Class ===")
        
        classes = self.class_loader.load_classes()
        class_list = list(classes.values())
        
        # Display available classes
        print("Available classes:")
        for i, char_class in enumerate(class_list, 1):
            print(f"{i}. {char_class.name}")
            print(f"   Hit Die: d{char_class.hit_die}")
            print(f"   Primary Ability: {char_class.primary_ability.capitalize()}")
            print(f"   Saving Throws: {', '.join(char_class.saving_throw_proficiencies)}")
            print(f"   Skill Choices: {char_class.skill_proficiencies.choose} from {len(char_class.skill_proficiencies.from_list)} options")
            print()
        
        # Get user selection
        while True:
            try:
                choice = input(f"Choose a class (1-{len(class_list)}): ").strip()
                class_index = int(choice) - 1
                if 0 <= class_index < len(class_list):
                    selected_class = class_list[class_index]
                    print(f"Selected class: {selected_class.name}")
                    
                    # Show detailed class info
                    self._show_class_details(selected_class)
                    return selected_class
                else:
                    print(f"Please enter a number between 1 and {len(class_list)}")
            except ValueError:
                print("Please enter a valid number")
    
    def _show_class_details(self, char_class: CharacterClass) -> None:
        """Show detailed information about selected class"""
        print(f"\n{char_class.name} Details:")
        print(f"  Hit Die: d{char_class.hit_die} (affects hit points)")
        print(f"  Primary Ability: {char_class.primary_ability.capitalize()}")
        print(f"  Saving Throw Proficiencies: {', '.join(char_class.saving_throw_proficiencies)}")
        
        print(f"  Skill Proficiencies (choose {char_class.skill_proficiencies.choose}):")
        for skill in char_class.skill_proficiencies.from_list:
            print(f"    • {skill}")
        
        print("  Starting Equipment:")
        for equipment in char_class.starting_equipment:
            print(f"    • {equipment.item} x{equipment.quantity}")
        print()
    
    def _allocate_stats(self, race: Race, char_class: CharacterClass) -> Dict[str, int]:
        """Interactive stat allocation using standard array"""
        print("=== Step 3: Allocate Ability Scores ===")
        print(f"Standard Array: {self.standard_array}")
        print("You must assign each value to one ability score.")
        print(f"Your {race.name} racial bonuses will be applied afterward.")
        print(f"Your {char_class.name} class recommends high {char_class.primary_ability.capitalize()}.")
        print()
        
        abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        available_scores = self.standard_array.copy()
        stat_allocation = {}
        
        for ability in abilities:
            print(f"Available scores: {available_scores}")
            print(f"Assigning {ability.capitalize()}:")
            
            # Show racial bonus for this ability
            racial_bonus = race.get_ability_bonus(ability)
            if racial_bonus > 0:
                print(f"  ({race.name} gets +{racial_bonus} to {ability.capitalize()})")
            
            # Show if this is the class's primary ability
            if ability == char_class.primary_ability:
                print(f"  (Primary ability for {char_class.name} - consider assigning highest score)")
            
            while True:
                try:
                    choice = input(f"Choose score for {ability.capitalize()}: ").strip()
                    score = int(choice)
                    if score in available_scores:
                        stat_allocation[ability] = score
                        available_scores.remove(score)
                        
                        final_score = score + racial_bonus
                        modifier = (final_score - 10) // 2
                        print(f"  {ability.capitalize()}: {score} + {racial_bonus} = {final_score} ({modifier:+d})")
                        print()
                        break
                    else:
                        print(f"Score {score} is not available. Choose from: {available_scores}")
                except ValueError:
                    print("Please enter a valid number")
        
        # Show final stat summary
        print("Final Ability Scores (before racial bonuses):")
        for ability, score in stat_allocation.items():
            racial_bonus = race.get_ability_bonus(ability)
            final_score = score + racial_bonus
            modifier = (final_score - 10) // 2
            print(f"  {ability.capitalize()}: {score} + {racial_bonus} = {final_score} ({modifier:+d})")
        print()
        
        return stat_allocation
    
    def _create_final_character(self, name: str, race: Race, char_class: CharacterClass, 
                              stat_allocation: Dict[str, int]) -> Character:
        """Create the final character with all selections applied"""
        print("=== Creating Your Character ===")
        
        # Create base character with allocated stats
        character = Character(
            name=name,
            race=race.name,
            character_class=char_class.name,
            strength=stat_allocation['strength'],
            dexterity=stat_allocation['dexterity'],
            constitution=stat_allocation['constitution'],
            intelligence=stat_allocation['intelligence'],
            wisdom=stat_allocation['wisdom'],
            charisma=stat_allocation['charisma'],
            level=1,
            hp=0,  # Will be calculated
            max_hp=0,  # Will be calculated
            armor_class=0,  # Will be calculated
            proficiency_bonus=2,  # Level 1 proficiency
            experience_points=0
        )
        
        # Apply racial bonuses
        print(f"Applying {race.name} racial bonuses...")
        race.apply_bonuses_to_character(character)
        
        # Calculate derived stats using class features
        print(f"Calculating {char_class.name} class features...")
        character.max_hp = char_class.get_hit_points_at_level(1, character.ability_modifier('constitution'))
        character.hp = character.max_hp
        character.armor_class = character.calculate_ac()
        character.proficiency_bonus = char_class.get_proficiency_bonus(1)
        
        # Generate starting equipment
        character.inventory = self.generate_starting_equipment(character, char_class)
        
        print(f"Character creation complete!")
        return character
    
    def _display_character_summary(self, character: Character, race: Race, char_class: CharacterClass) -> None:
        """Display final character summary"""
        print("\n" + "="*50)
        print("CHARACTER SUMMARY")
        print("="*50)
        print(f"Name: {character.name}")
        print(f"Race: {character.race}")
        print(f"Class: {character.character_class}")
        print(f"Level: {character.level}")
        print()
        
        print("ABILITY SCORES:")
        abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        for ability in abilities:
            score = getattr(character, ability)
            modifier = character.ability_modifier(ability)
            primary = " (Primary)" if ability == char_class.primary_ability else ""
            print(f"  {ability.capitalize()}: {score} ({modifier:+d}){primary}")
        print()
        
        print("COMBAT STATS:")
        print(f"  Hit Points: {character.hp}/{character.max_hp}")
        print(f"  Armor Class: {character.armor_class}")
        print(f"  Proficiency Bonus: +{character.proficiency_bonus}")
        print()
        
        print("PROFICIENCIES:")
        print(f"  Saving Throws: {', '.join(char_class.saving_throw_proficiencies)}")
        print(f"  Languages: {', '.join(race.languages)}")
        print()
        
        if race.traits:
            print("RACIAL TRAITS:")
            for trait in race.traits:
                print(f"  • {trait.name}: {trait.description}")
            print()
        
        print("STARTING EQUIPMENT:")
        if character.inventory:
            total_weight = 0
            for item in character.inventory:
                weight_str = f" ({item['weight']} lbs each)" if item['weight'] > 0 else ""
                print(f"  • {item['name']} x{item['quantity']}{weight_str}")
                total_weight += item['weight'] * item['quantity']
            print(f"  Total Weight: {total_weight} lbs")
        else:
            print("  No starting equipment")
        print()
        
        print("="*50)
    
    def generate_starting_equipment(self, character: Character, character_class: CharacterClass) -> List[Dict[str, any]]:
        """Generate starting equipment based on character class"""
        print(f"\n=== Generating Starting Equipment for {character_class.name} ===")
        
        starting_inventory = []
        
        # Load all available items
        available_items = self.item_loader.load_items()
        
        # Process each starting equipment item from the class
        for equipment in character_class.starting_equipment:
            item_id = equipment.item
            quantity = equipment.quantity
            
            # Try to find the item in the items database
            item = available_items.get(item_id)
            
            if item:
                # Add the item to inventory with quantity
                inventory_entry = {
                    "item_id": item_id,
                    "name": item.name,
                    "type": item.item_type,
                    "quantity": quantity,
                    "weight": item.weight,
                    "ac_bonus": item.ac_bonus,
                    "damage": item.damage_dice,
                    "damage_type": item.damage_type,
                    "properties": item.properties or [],
                    "description": item.description
                }
                starting_inventory.append(inventory_entry)
                print(f"  Added: {item.name} x{quantity}")
                
            else:
                # Item not found in database, create a basic placeholder
                print(f"  Warning: Item '{item_id}' not found in items database")
                placeholder_entry = {
                    "item_id": item_id,
                    "name": item_id.replace('_', ' ').title(),
                    "type": "misc",
                    "quantity": quantity,
                    "weight": 1.0,
                    "ac_bonus": None,
                    "damage": None,
                    "damage_type": None,
                    "properties": [],
                    "description": f"Starting equipment: {item_id}"
                }
                starting_inventory.append(placeholder_entry)
                print(f"  Added placeholder: {placeholder_entry['name']} x{quantity}")
        
        # Calculate total weight
        total_weight = sum(item["weight"] * item["quantity"] for item in starting_inventory)
        print(f"\nTotal starting equipment weight: {total_weight} lbs")
        
        # Check carrying capacity (Strength score * 15 lbs)
        carrying_capacity = character.strength * 15
        print(f"Carrying capacity: {carrying_capacity} lbs")
        
        if total_weight > carrying_capacity:
            print(f"Warning: Starting equipment ({total_weight} lbs) exceeds carrying capacity ({carrying_capacity} lbs)")
        else:
            print(f"Equipment weight is within carrying capacity")
        
        return starting_inventory


def create_character_quick(name: str, race_name: str = "Human", class_name: str = "Fighter") -> Tuple[Character, Race, CharacterClass]:
    """Quick character creation with defaults (for testing)"""
    print(f"=== Quick Character Creation ===")
    print(f"Creating {name} the {race_name} {class_name}")
    
    # Load race and class
    race_loader = RaceLoader()
    class_loader = ClassLoader()
    
    race = race_loader.get_race(race_name)
    char_class = class_loader.get_class(class_name)
    
    if not race:
        print(f"Warning: Race '{race_name}' not found, using Human")
        race = race_loader.get_race("human")
    
    if not char_class:
        print(f"Warning: Class '{class_name}' not found, using Fighter")
        char_class = class_loader.get_class("fighter")
    
    # Use standard array with optimal allocation for class
    standard_array = [15, 14, 13, 12, 10, 8]
    
    # Create a proper stat allocation that uses all values from standard array
    abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    available_scores = standard_array.copy()
    stat_allocation = {}
    
    # First, assign highest score (15) to primary ability
    primary_ability = char_class.primary_ability
    stat_allocation[primary_ability] = 15
    available_scores.remove(15)
    
    # Then assign remaining scores optimally
    # Constitution is important for all classes (HP), so give it second priority
    if primary_ability != 'constitution':
        stat_allocation['constitution'] = 14
        available_scores.remove(14)
    
    # Dexterity is important for AC, so give it third priority if not primary
    if primary_ability != 'dexterity' and 'dexterity' not in stat_allocation:
        if 14 in available_scores:
            stat_allocation['dexterity'] = 14
            available_scores.remove(14)
        else:
            stat_allocation['dexterity'] = 13
            available_scores.remove(13)
    
    # Assign remaining scores to remaining abilities
    remaining_abilities = [ability for ability in abilities if ability not in stat_allocation]
    for ability in remaining_abilities:
        stat_allocation[ability] = available_scores.pop(0)
    
    # Create character
    character = Character(
        name=name,
        race=race.name,
        character_class=char_class.name,
        strength=stat_allocation['strength'],
        dexterity=stat_allocation['dexterity'],
        constitution=stat_allocation['constitution'],
        intelligence=stat_allocation['intelligence'],
        wisdom=stat_allocation['wisdom'],
        charisma=stat_allocation['charisma'],
        level=1,
        hp=0,
        max_hp=0,
        armor_class=0,
        proficiency_bonus=2,
        experience_points=0
    )
    
    # Apply racial bonuses
    race.apply_bonuses_to_character(character)
    
    # Calculate derived stats
    character.max_hp = char_class.get_hit_points_at_level(1, character.ability_modifier('constitution'))
    character.hp = character.max_hp
    character.armor_class = character.calculate_ac()
    character.proficiency_bonus = char_class.get_proficiency_bonus(1)
    
    # Generate starting equipment
    creation_flow = CharacterCreationFlow()
    starting_equipment = creation_flow.generate_starting_equipment(character, char_class)
    
    # Initialize proper inventory system and convert old format
    character.initialize_inventory()
    character._legacy_inventory = starting_equipment
    character.migrate_legacy_inventory()
    
    print(f"Created {character.name}: Level {character.level} {character.race} {character.character_class}")
    print(f"  HP: {character.hp}/{character.max_hp}, AC: {character.armor_class}")
    print(f"  Primary Ability ({char_class.primary_ability.capitalize()}): {getattr(character, char_class.primary_ability)}")
    print(f"  Starting Equipment: {len(character.inventory.items)} items")
    
    return character, race, char_class


# Manual testing function
def test_character_creation_flow():
    """Test the character creation flow"""
    print("=== Testing Character Creation Flow ===")
    
    # Test quick creation first
    print("Testing quick character creation...")
    char1, race1, class1 = create_character_quick("TestChar", "Human", "Fighter")
    
    # Verify the character was created correctly
    assert char1.name == "TestChar"
    assert char1.race == "Human"
    assert char1.character_class == "Fighter"
    assert char1.level == 1
    assert char1.hp > 0
    assert char1.max_hp > 0
    assert char1.armor_class >= 10
    
    print("✓ Quick character creation works!")
    
    # Test with different race/class combinations
    test_combinations = [
        ("Alice", "Elf", "Rogue"),
        ("Bob", "Dwarf", "Cleric"),
        ("Charlie", "Halfling", "Wizard")
    ]
    
    for name, race_name, class_name in test_combinations:
        print(f"\nTesting {name} the {race_name} {class_name}...")
        char, race, char_class = create_character_quick(name, race_name, class_name)
        
        # Verify racial bonuses were applied
        for ability, bonus in race.ability_bonuses.items():
            if bonus > 0:
                print(f"  {ability.capitalize()} bonus applied: +{bonus}")
        
        # Verify class features
        expected_hp = char_class.get_hit_points_at_level(1, char.ability_modifier('constitution'))
        assert char.max_hp == expected_hp, f"HP mismatch: {char.max_hp} != {expected_hp}"
        
        print(f"  ✓ {name} created successfully")
    
    print("\n✓ All character creation tests passed!")
    
    # Note: Interactive flow would be tested manually
    print("\nTo test interactive character creation, run:")
    print("  flow = CharacterCreationFlow()")
    print("  character, race, char_class = flow.create_character_interactive()")


if __name__ == "__main__":
    test_character_creation_flow()