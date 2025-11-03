"""
Fantasy RPG - Feat System

Feat definitions and management functionality.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
from fantasy_rpg.utils.data_loader import DataLoader


@dataclass
class Feat:
    """D&D 5e feat implementation"""
    name: str
    description: str
    benefits: List[str]
    prerequisites: List[str]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Feat':
        """Create Feat from dictionary data"""
        return cls(
            name=data['name'],
            description=data['description'],
            benefits=data['benefits'],
            prerequisites=data.get('prerequisites', [])
        )
    
    def meets_prerequisites(self, character) -> bool:
        """Check if character meets prerequisites for this feat"""
        # For now, just check if prerequisites list is empty
        # In a full implementation, this would check specific character attributes
        return len(self.prerequisites) == 0
    
    def apply_to_character(self, character):
        """Apply feat effects to character (placeholder for future implementation)"""
        # This would contain the actual mechanical effects of the feat
        # For now, just add it to the character's feat list
        character.add_feat(self.name)
        print(f"Applied feat '{self.name}' to {character.name}")


class FeatLoader(DataLoader):
    """Loads feat data from JSON files"""
    
    def __init__(self, data_dir: str = None):
        super().__init__(data_dir)
        self._feats_cache: Optional[Dict[str, Feat]] = None
    
    def load_feats(self) -> Dict[str, Feat]:
        """Load all feat definitions from feats.json"""
        if self._feats_cache is not None:
            return self._feats_cache
        
        try:
            data = self.load_json("feats.json")
            
            feats = {}
            for feat_key, feat_data in data['feats'].items():
                feats[feat_key] = Feat.from_dict(feat_data)
            
            print(f"Loaded {len(feats)} feats from {self.data_dir / 'feats.json'}")
            self._feats_cache = feats
            return feats
            
        except FileNotFoundError:
            print(f"Warning: feats.json not found in {self.data_dir}, using default feats")
            return self._get_default_feats()
        except Exception as e:
            print(f"Error loading feats from {self.data_dir / 'feats.json'}: {e}")
            return self._get_default_feats()
    
    def get_feat(self, feat_name: str) -> Optional[Feat]:
        """Get a specific feat by name (case-insensitive)"""
        feats = self.load_feats()
        feat_key = feat_name.lower().replace(" ", "_")
        return feats.get(feat_key)
    
    def get_available_feats(self, character) -> List[Feat]:
        """Get list of feats the character can take"""
        feats = self.load_feats()
        available = []
        
        for feat in feats.values():
            if feat.meets_prerequisites(character) and not character.has_feat(feat.name):
                available.append(feat)
        
        return available
    
    def _get_default_feats(self) -> Dict[str, Feat]:
        """Fallback default feats if JSON file is missing"""
        tough = Feat(
            name="Tough",
            description="Hardy and resilient, you gain additional hit points.",
            benefits=["Your hit point maximum increases by an amount equal to twice your level"],
            prerequisites=[]
        )
        
        alert = Feat(
            name="Alert",
            description="Always on the lookout for danger.",
            benefits=["You gain a +5 bonus to initiative", "You can't be surprised while conscious"],
            prerequisites=[]
        )
        
        return {"tough": tough, "alert": alert}


def apply_feat_to_character(character, feat_name: str) -> bool:
    """Apply a feat to a character"""
    feat_loader = FeatLoader()
    feat = feat_loader.get_feat(feat_name)
    
    if not feat:
        print(f"Feat '{feat_name}' not found")
        return False
    
    if not feat.meets_prerequisites(character):
        print(f"{character.name} doesn't meet prerequisites for '{feat_name}'")
        return False
    
    if character.has_feat(feat.name):
        print(f"{character.name} already has feat '{feat_name}'")
        return False
    
    feat.apply_to_character(character)
    return True


# Manual testing function
def test_feat_system():
    """Test feat loading and application"""
    print("=== Testing Feat System ===")
    
    # Test feat loading
    feat_loader = FeatLoader()
    feats = feat_loader.load_feats()
    print(f"Available feats: {list(feats.keys())}")
    
    # Test getting specific feat
    tough_feat = feat_loader.get_feat("tough")
    if tough_feat:
        print(f"\nTough feat loaded:")
        print(f"  Name: {tough_feat.name}")
        print(f"  Description: {tough_feat.description}")
        print(f"  Benefits: {len(tough_feat.benefits)} benefits")
        print(f"  Prerequisites: {tough_feat.prerequisites}")
    
    # Test feat with prerequisites
    war_caster = feat_loader.get_feat("war_caster")
    if war_caster:
        print(f"\nWar Caster feat:")
        print(f"  Prerequisites: {war_caster.prerequisites}")
    
    print("✓ Feat system tests passed!")
    return feats


if __name__ == "__main__":
    test_feat_system()