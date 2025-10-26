"""
Fantasy RPG - Background System

Character background definitions and management functionality.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class BackgroundFeature:
    """Background feature (special ability)"""
    name: str
    description: str


@dataclass
class Background:
    """D&D 5e background implementation"""
    name: str
    description: str
    skill_proficiencies: List[str]
    tool_proficiencies: List[str] = field(default_factory=list)
    languages: int = 0
    equipment: List[Dict[str, any]] = field(default_factory=list)
    feature: Optional[BackgroundFeature] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Background':
        """Create Background from dictionary data"""
        feature = None
        if 'feature' in data:
            feature_data = data['feature']
            feature = BackgroundFeature(
                name=feature_data['name'],
                description=feature_data['description']
            )
        
        return cls(
            name=data['name'],
            description=data['description'],
            skill_proficiencies=data.get('skill_proficiencies', []),
            tool_proficiencies=data.get('tool_proficiencies', []),
            languages=data.get('languages', 0),
            equipment=data.get('equipment', []),
            feature=feature
        )


class BackgroundLoader:
    """Loads background data from JSON files"""
    
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
        self._backgrounds_cache: Optional[Dict[str, Background]] = None
    
    def load_backgrounds(self) -> Dict[str, Background]:
        """Load all background definitions from backgrounds.json"""
        if self._backgrounds_cache is not None:
            return self._backgrounds_cache
        
        backgrounds_file = self.data_dir / "backgrounds.json"
        if not backgrounds_file.exists():
            print(f"Warning: {backgrounds_file} not found, using default backgrounds")
            return self._get_default_backgrounds()
        
        try:
            with open(backgrounds_file, 'r') as f:
                data = json.load(f)
            
            backgrounds = {}
            for bg_key, bg_data in data['backgrounds'].items():
                backgrounds[bg_key] = Background.from_dict(bg_data)
            
            print(f"Loaded {len(backgrounds)} backgrounds from {backgrounds_file}")
            self._backgrounds_cache = backgrounds
            return backgrounds
            
        except Exception as e:
            print(f"Error loading backgrounds from {backgrounds_file}: {e}")
            return self._get_default_backgrounds()
    
    def get_background(self, background_name: str) -> Optional[Background]:
        """Get a specific background by name (case-insensitive)"""
        backgrounds = self.load_backgrounds()
        bg_key = background_name.lower().replace(" ", "_")
        return backgrounds.get(bg_key)
    
    def _get_default_backgrounds(self) -> Dict[str, Background]:
        """Fallback default backgrounds if JSON file is missing"""
        soldier = Background(
            name="Soldier",
            description="War has been your life for as long as you care to remember.",
            skill_proficiencies=["Athletics", "Intimidation"],
            tool_proficiencies=["gaming_set", "vehicles_land"],
            equipment=[
                {"item": "insignia_of_rank", "quantity": 1},
                {"item": "common_clothes", "quantity": 1}
            ],
            feature=BackgroundFeature(
                name="Military Rank",
                description="You have a military rank from your career as a soldier."
            )
        )
        
        return {"soldier": soldier}


def apply_background_to_character(character, background: Background):
    """Apply background features to a character"""
    print(f"\nApplying {background.name} background:")
    
    # Update character background
    character.background = background.name
    
    # Apply skill proficiencies
    if background.skill_proficiencies:
        print(f"  Skill Proficiencies:")
        for skill in background.skill_proficiencies:
            character.add_skill_proficiency(skill)
            print(f"    • {skill}")
    
    # Display tool proficiencies (would be implemented when tool system is added)
    if background.tool_proficiencies:
        print(f"  Tool Proficiencies: {', '.join(background.tool_proficiencies)}")
    
    # Display languages (would be implemented when language system is added)
    if background.languages > 0:
        print(f"  Languages: {background.languages} additional language(s)")
    
    # Display starting equipment
    if background.equipment:
        print(f"  Starting Equipment:")
        for equipment in background.equipment:
            print(f"    • {equipment['item']} x{equipment['quantity']}")
    
    # Display background feature
    if background.feature:
        print(f"  Background Feature: {background.feature.name}")
        print(f"    {background.feature.description}")
    
    return character


def create_character_with_background(name: str, race_name: str = "Human", 
                                   class_name: str = "Fighter", 
                                   background_name: str = "Soldier"):
    """Create a character with race, class, and background applied"""
    try:
        from .character_class import create_character_with_class
    except ImportError:
        from character_class import create_character_with_class
    
    # Create character with race and class
    character, race, char_class = create_character_with_class(name, race_name, class_name)
    
    # Load and apply background
    background_loader = BackgroundLoader()
    background = background_loader.get_background(background_name)
    
    if not background:
        print(f"Warning: Background '{background_name}' not found, using Soldier")
        background = background_loader.get_background("soldier")
    
    # Apply background features
    character = apply_background_to_character(character, background)
    
    print(f"\nFinal character summary:")
    print(f"  Name: {character.name}")
    print(f"  Race: {character.race}")
    print(f"  Class: {character.character_class}")
    print(f"  Background: {character.background}")
    print(f"  Level: {character.level}")
    print(f"  HP: {character.hp}/{character.max_hp}")
    print(f"  AC: {character.armor_class}")
    
    return character, race, char_class, background


# Manual testing function
def test_background_system():
    """Test background loading and application"""
    print("=== Testing Background System ===")
    
    # Test background loading
    background_loader = BackgroundLoader()
    backgrounds = background_loader.load_backgrounds()
    print(f"Available backgrounds: {list(backgrounds.keys())}")
    
    # Test getting specific background
    soldier_bg = background_loader.get_background("soldier")
    if soldier_bg:
        print(f"\nSoldier background loaded:")
        print(f"  Name: {soldier_bg.name}")
        print(f"  Description: {soldier_bg.description}")
        print(f"  Skill Proficiencies: {soldier_bg.skill_proficiencies}")
        print(f"  Tool Proficiencies: {soldier_bg.tool_proficiencies}")
        print(f"  Equipment: {len(soldier_bg.equipment)} items")
        if soldier_bg.feature:
            print(f"  Feature: {soldier_bg.feature.name}")
    
    # Test character creation with background
    print(f"\n=== Creating Character with Background ===")
    character, race, char_class, background = create_character_with_background(
        "Background Test", "Human", "Fighter", "Soldier"
    )
    
    print("✓ Background system tests passed!")
    return character, race, char_class, background


if __name__ == "__main__":
    test_background_system()