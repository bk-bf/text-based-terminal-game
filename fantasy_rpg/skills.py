"""
Fantasy RPG - Skill System

D&D 5e skill system with proficiency bonuses and skill checks.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
import random


class SkillName(Enum):
    """All D&D 5e skills with their associated ability scores"""
    ACROBATICS = ("Acrobatics", "dexterity")
    ANIMAL_HANDLING = ("Animal Handling", "wisdom")
    ARCANA = ("Arcana", "intelligence")
    ATHLETICS = ("Athletics", "strength")
    DECEPTION = ("Deception", "charisma")
    HISTORY = ("History", "intelligence")
    INSIGHT = ("Insight", "wisdom")
    INTIMIDATION = ("Intimidation", "charisma")
    INVESTIGATION = ("Investigation", "intelligence")
    MEDICINE = ("Medicine", "wisdom")
    NATURE = ("Nature", "intelligence")
    PERCEPTION = ("Perception", "wisdom")
    PERFORMANCE = ("Performance", "charisma")
    PERSUASION = ("Persuasion", "charisma")
    RELIGION = ("Religion", "intelligence")
    SLEIGHT_OF_HAND = ("Sleight of Hand", "dexterity")
    STEALTH = ("Stealth", "dexterity")
    SURVIVAL = ("Survival", "wisdom")
    
    def __init__(self, display_name: str, ability: str):
        self.display_name = display_name
        self.ability = ability


@dataclass
class SkillProficiencies:
    """Character's skill proficiencies"""
    proficient_skills: Set[str] = field(default_factory=set)
    expertise_skills: Set[str] = field(default_factory=set)  # Double proficiency (Rogue feature)
    
    def add_proficiency(self, skill_name: str):
        """Add proficiency in a skill"""
        self.proficient_skills.add(skill_name)
        print(f"Gained proficiency in {skill_name}")
    
    def add_expertise(self, skill_name: str):
        """Add expertise in a skill (double proficiency bonus)"""
        if skill_name not in self.proficient_skills:
            self.add_proficiency(skill_name)
        self.expertise_skills.add(skill_name)
        print(f"Gained expertise in {skill_name}")
    
    def is_proficient(self, skill_name: str) -> bool:
        """Check if character is proficient in a skill"""
        return skill_name in self.proficient_skills
    
    def has_expertise(self, skill_name: str) -> bool:
        """Check if character has expertise in a skill"""
        return skill_name in self.expertise_skills
    
    def get_proficiency_multiplier(self, skill_name: str) -> int:
        """Get proficiency multiplier (0=not proficient, 1=proficient, 2=expertise)"""
        if skill_name in self.expertise_skills:
            return 2
        elif skill_name in self.proficient_skills:
            return 1
        else:
            return 0


class SkillSystem:
    """Handles skill checks and proficiency management"""
    
    @staticmethod
    def get_skill_ability(skill_name: str) -> str:
        """Get the ability score associated with a skill"""
        for skill in SkillName:
            if skill.display_name == skill_name:
                return skill.ability
        
        # Fallback for unknown skills
        print(f"Warning: Unknown skill '{skill_name}', defaulting to wisdom")
        return "wisdom"
    
    @staticmethod
    def calculate_skill_modifier(character, skill_name: str) -> int:
        """Calculate total skill modifier (ability + proficiency)"""
        # Get base ability modifier
        ability = SkillSystem.get_skill_ability(skill_name)
        ability_modifier = character.ability_modifier(ability)
        
        # Get proficiency bonus if applicable
        proficiency_bonus = 0
        if hasattr(character, 'skill_proficiencies'):
            multiplier = character.skill_proficiencies.get_proficiency_multiplier(skill_name)
            proficiency_bonus = multiplier * character.proficiency_bonus
        
        return ability_modifier + proficiency_bonus
    
    @staticmethod
    def make_skill_check(character, skill_name: str, dc: int = 15, advantage: bool = False, disadvantage: bool = False) -> dict:
        """
        Make a skill check for a character
        
        Returns dict with:
        - roll: the d20 roll result
        - modifier: the total modifier applied
        - total: roll + modifier
        - success: whether the check succeeded
        - details: breakdown of the calculation
        """
        # Roll d20 (with advantage/disadvantage)
        if advantage and disadvantage:
            # Advantage and disadvantage cancel out
            roll = random.randint(1, 20)
            roll_type = "normal"
        elif advantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            roll = max(roll1, roll2)
            roll_type = f"advantage ({roll1}, {roll2})"
        elif disadvantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            roll = min(roll1, roll2)
            roll_type = f"disadvantage ({roll1}, {roll2})"
        else:
            roll = random.randint(1, 20)
            roll_type = "normal"
        
        # Calculate modifier
        modifier = SkillSystem.calculate_skill_modifier(character, skill_name)
        total = roll + modifier
        success = total >= dc
        
        # Get ability and proficiency breakdown
        ability = SkillSystem.get_skill_ability(skill_name)
        ability_mod = character.ability_modifier(ability)
        
        proficiency_bonus = 0
        proficiency_type = "not proficient"
        if hasattr(character, 'skill_proficiencies'):
            multiplier = character.skill_proficiencies.get_proficiency_multiplier(skill_name)
            if multiplier > 0:
                proficiency_bonus = multiplier * character.proficiency_bonus
                proficiency_type = "expertise" if multiplier == 2 else "proficient"
        
        return {
            'roll': roll,
            'modifier': modifier,
            'total': total,
            'success': success,
            'dc': dc,
            'skill': skill_name,
            'ability': ability,
            'ability_modifier': ability_mod,
            'proficiency_bonus': proficiency_bonus,
            'proficiency_type': proficiency_type,
            'roll_type': roll_type,
            'details': f"{skill_name} check: {roll} ({roll_type}) + {modifier} = {total} vs DC {dc}"
        }
    
    @staticmethod
    def get_all_skills() -> List[str]:
        """Get list of all available skills"""
        return [skill.display_name for skill in SkillName]
    
    @staticmethod
    def get_skills_by_ability(ability: str) -> List[str]:
        """Get all skills that use a specific ability score"""
        return [skill.display_name for skill in SkillName if skill.ability == ability]


def add_skill_proficiencies_to_character(character):
    """Add skill proficiency system to an existing character"""
    if not hasattr(character, 'skill_proficiencies') or character.skill_proficiencies is None:
        character.skill_proficiencies = SkillProficiencies()
        print(f"Added skill proficiency system to {character.name}")
    return character


def display_character_skills(character):
    """Display all skills with their modifiers for a character"""
    if not hasattr(character, 'skill_proficiencies'):
        print(f"{character.name} has no skill proficiency system")
        return
    
    print(f"\n=== {character.name}'s Skills ===")
    
    # Group skills by ability
    abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    
    for ability in abilities:
        ability_skills = SkillSystem.get_skills_by_ability(ability)
        if ability_skills:
            print(f"\n{ability.upper()} ({character.ability_modifier(ability):+d}):")
            
            for skill in ability_skills:
                modifier = SkillSystem.calculate_skill_modifier(character, skill)
                proficiency_type = ""
                
                if character.skill_proficiencies.has_expertise(skill):
                    proficiency_type = " (expertise)"
                elif character.skill_proficiencies.is_proficient(skill):
                    proficiency_type = " (proficient)"
                
                print(f"  {skill:<18} {modifier:+2d}{proficiency_type}")


# Manual testing function
def test_skill_system():
    """Test the skill system implementation"""
    print("=== Testing Skill System ===")
    
    # Import character creation
    try:
        from fantasy_rpg.character import create_character
    except ImportError:
        from character import create_character
    
    # Create a test character
    character = create_character("TestChar", "Human", "Rogue")
    
    # Add skill system
    add_skill_proficiencies_to_character(character)
    
    # Add some skill proficiencies (simulate class selection)
    character.add_skill_proficiency("Stealth")
    character.add_skill_proficiency("Perception")
    character.add_skill_proficiency("Sleight of Hand")
    character.add_skill_proficiency("Investigation")
    
    # Add expertise (Rogue feature)
    character.add_skill_expertise("Stealth")
    character.add_skill_expertise("Sleight of Hand")
    
    # Display all skills
    display_character_skills(character)
    
    # Test skill checks
    print(f"\n=== Testing Skill Checks ===")
    
    test_skills = ["Stealth", "Perception", "Athletics", "Arcana"]
    
    for skill in test_skills:
        result = SkillSystem.make_skill_check(character, skill, dc=15)
        status = "SUCCESS" if result['success'] else "FAILURE"
        print(f"{skill}: {result['details']} - {status}")
        
        # Verify calculation
        expected_modifier = SkillSystem.calculate_skill_modifier(character, skill)
        assert result['modifier'] == expected_modifier, f"Modifier mismatch for {skill}"
    
    # Test advantage/disadvantage
    print(f"\nTesting advantage/disadvantage:")
    adv_result = SkillSystem.make_skill_check(character, "Stealth", dc=15, advantage=True)
    print(f"Stealth with advantage: {adv_result['details']}")
    
    dis_result = SkillSystem.make_skill_check(character, "Athletics", dc=15, disadvantage=True)
    print(f"Athletics with disadvantage: {dis_result['details']}")
    
    # Test all skills exist
    print(f"\nTesting all skills:")
    all_skills = SkillSystem.get_all_skills()
    print(f"Total skills available: {len(all_skills)}")
    
    for skill in all_skills:
        ability = SkillSystem.get_skill_ability(skill)
        modifier = SkillSystem.calculate_skill_modifier(character, skill)
        print(f"  {skill:<18} ({ability[:3].upper()}) {modifier:+2d}")
    
    print("✓ All skill system tests passed!")
    return character


if __name__ == "__main__":
    test_skill_system()