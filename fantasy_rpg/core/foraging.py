"""
Fantasy RPG - Foraging System

Skill-based foraging mechanics for interacting with forageable objects.
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from .item import Item, ItemLoader
    from .skills import SkillSystem
except ImportError:
    from item import Item, ItemLoader
    from skills import SkillSystem


class ForagingDifficulty(Enum):
    """Difficulty levels for foraging checks"""
    TRIVIAL = 5      # Berry bushes in season
    EASY = 10        # Common edible plants
    MODERATE = 15    # Hidden or seasonal items
    HARD = 20        # Rare or dangerous foraging
    VERY_HARD = 25   # Expert-level foraging


@dataclass
class ForagingResult:
    """Result of a foraging attempt"""
    success: bool
    items_found: List[Item]
    skill_check_result: Dict
    message: str
    experience_gained: int = 0
    time_spent: int = 30  # minutes


class ForagingSystem:
    """Handles foraging mechanics and skill checks"""
    
    def __init__(self):
        self.item_loader = ItemLoader()
        
        # Foraging skill mappings
        self.skill_mappings = {
            "food": "Survival",
            "herbs": "Nature", 
            "materials": "Survival",
            "treasure": "Investigation",
            "natural": "Survival"
        }
        
        # Seasonal modifiers
        self.seasonal_modifiers = {
            "spring": {"herbs": 2, "food": 0},
            "summer": {"food": 2, "herbs": 1},
            "autumn": {"food": 3, "materials": 1},
            "winter": {"food": -3, "herbs": -2, "materials": 0}
        }
    
    def attempt_foraging(self, character, forageable_object: Dict, season: str = "summer") -> ForagingResult:
        """Attempt to forage from an object"""
        
        # Get object properties
        properties = forageable_object.get("properties", {})
        if not properties.get("can_forage", False):
            return ForagingResult(
                success=False,
                items_found=[],
                skill_check_result={},
                message="This object cannot be foraged from."
            )
        
        # Determine difficulty and skill
        difficulty, skill_name = self._determine_foraging_difficulty(forageable_object, season)
        
        # Make skill check
        skill_result = SkillSystem.make_skill_check(character, skill_name, difficulty.value)
        
        # Determine success and items found
        if skill_result["success"]:
            items_found = self._generate_foraged_items(forageable_object, skill_result, season)
            message = self._generate_success_message(forageable_object, items_found, skill_result)
            experience = self._calculate_experience(difficulty, len(items_found))
        else:
            items_found = []
            message = self._generate_failure_message(forageable_object, skill_result)
            experience = 1  # Small consolation XP
        
        return ForagingResult(
            success=skill_result["success"],
            items_found=items_found,
            skill_check_result=skill_result,
            message=message,
            experience_gained=experience
        )
    
    def _determine_foraging_difficulty(self, obj: Dict, season: str) -> Tuple[ForagingDifficulty, str]:
        """Determine the difficulty and skill for foraging this object"""
        properties = obj.get("properties", {})
        pools = obj.get("pools", [])
        
        # Base difficulty from object properties
        if properties.get("seasonal", False) and season == "winter":
            base_difficulty = ForagingDifficulty.HARD
        elif properties.get("renewable", True):
            base_difficulty = ForagingDifficulty.EASY
        else:
            base_difficulty = ForagingDifficulty.MODERATE
        
        # Determine skill based on object pools
        skill_name = "Survival"  # Default
        for pool in pools:
            if pool in self.skill_mappings:
                skill_name = self.skill_mappings[pool]
                break
        
        # Adjust difficulty based on food value
        food_value = properties.get("food_value", 1)
        if food_value >= 3:
            base_difficulty = ForagingDifficulty.MODERATE
        elif food_value >= 5:
            base_difficulty = ForagingDifficulty.HARD
        
        return base_difficulty, skill_name
    
    def _generate_foraged_items(self, obj: Dict, skill_result: Dict, season: str) -> List[Item]:
        """Generate items found during successful foraging"""
        items_found = []
        properties = obj.get("properties", {})
        pools = obj.get("pools", [])
        
        # Base number of items based on skill check success margin
        success_margin = skill_result["total"] - skill_result["dc"]
        base_items = 1 + max(0, success_margin // 5)  # Extra item every 5 points over DC
        
        # Apply seasonal modifiers
        seasonal_bonus = 0
        for pool in pools:
            if pool in self.seasonal_modifiers.get(season, {}):
                seasonal_bonus += self.seasonal_modifiers[season][pool]
        
        total_items = max(1, base_items + seasonal_bonus)
        
        # Get items from the object's drop pools if available
        if "item_drops" in obj:
            # Use existing item drop system
            drop_pools = obj["item_drops"].get("pools", [])
            available_items = self.item_loader.get_items_by_pools(drop_pools)
        else:
            # Generate items based on object pools
            available_items = self.item_loader.get_items_by_pools(pools)
        
        # Filter to appropriate items (food, materials, etc.)
        forageable_items = [item for item in available_items 
                           if item.item_type in ["consumable", "material", "tool"]]
        
        if not forageable_items:
            # Create a basic item if none available
            basic_item = self._create_basic_foraged_item(obj)
            if basic_item:
                forageable_items = [basic_item]
        
        # Select items
        for _ in range(min(total_items, len(forageable_items))):
            if forageable_items:
                # Weighted selection based on drop_weight
                total_weight = sum(item.drop_weight for item in forageable_items)
                if total_weight > 0:
                    roll = random.randint(1, total_weight)
                    current = 0
                    for item in forageable_items:
                        current += item.drop_weight
                        if roll <= current:
                            items_found.append(item)
                            break
        
        return items_found
    
    def _create_basic_foraged_item(self, obj: Dict) -> Optional[Item]:
        """Create a basic foraged item if none are available in pools"""
        obj_name = obj.get("name", "Unknown Object")
        properties = obj.get("properties", {})
        
        if "berry" in obj_name.lower() or "food" in obj.get("pools", []):
            return Item(
                name="Wild Berries",
                item_type="consumable",
                weight=0.1,
                value=1,
                description=f"Fresh berries foraged from {obj_name.lower()}.",
                pools=["food", "foraged", "natural"]
            )
        elif "herb" in obj_name.lower() or "medicinal" in str(properties):
            return Item(
                name="Wild Herbs",
                item_type="consumable", 
                weight=0.1,
                value=3,
                description=f"Medicinal herbs gathered from {obj_name.lower()}.",
                pools=["herbs", "foraged", "natural"]
            )
        
        return None
    
    def _generate_success_message(self, obj: Dict, items: List[Item], skill_result: Dict) -> str:
        """Generate success message for foraging"""
        obj_name = obj.get("name", "the object")
        skill_name = skill_result.get("skill", "Survival")
        total_roll = skill_result.get("total", 0)
        
        if len(items) == 0:
            return f"You search {obj_name.lower()} but find nothing useful."
        elif len(items) == 1:
            item_name = items[0].name
            return f"Your {skill_name} check ({total_roll}) succeeds! You forage {item_name} from {obj_name.lower()}."
        else:
            item_names = [item.name for item in items]
            return f"Your {skill_name} check ({total_roll}) succeeds! You forage {len(items)} items from {obj_name.lower()}: {', '.join(item_names)}."
    
    def _generate_failure_message(self, obj: Dict, skill_result: Dict) -> str:
        """Generate failure message for foraging"""
        obj_name = obj.get("name", "the object")
        skill_name = skill_result.get("skill", "Survival")
        total_roll = skill_result.get("total", 0)
        dc = skill_result.get("dc", 15)
        
        margin = dc - total_roll
        if margin <= 2:
            return f"Your {skill_name} check ({total_roll}) barely fails (DC {dc}). You search {obj_name.lower()} but find nothing useful this time."
        elif margin <= 5:
            return f"Your {skill_name} check ({total_roll}) fails (DC {dc}). You spend time searching {obj_name.lower()} but come up empty-handed."
        else:
            return f"Your {skill_name} check ({total_roll}) fails badly (DC {dc}). You're unable to find anything worthwhile in {obj_name.lower()}."
    
    def _calculate_experience(self, difficulty: ForagingDifficulty, items_found: int) -> int:
        """Calculate experience gained from foraging"""
        base_xp = {
            ForagingDifficulty.TRIVIAL: 5,
            ForagingDifficulty.EASY: 10,
            ForagingDifficulty.MODERATE: 25,
            ForagingDifficulty.HARD: 50,
            ForagingDifficulty.VERY_HARD: 100
        }
        
        xp = base_xp.get(difficulty, 10)
        # Bonus XP for finding multiple items
        if items_found > 1:
            xp += (items_found - 1) * 5
        
        return xp
    
    def can_forage_object(self, obj: Dict) -> bool:
        """Check if an object can be foraged from"""
        properties = obj.get("properties", {})
        return properties.get("can_forage", False)
    
    def get_foraging_info(self, obj: Dict, character, season: str = "summer") -> Dict:
        """Get information about foraging this object"""
        if not self.can_forage_object(obj):
            return {"can_forage": False, "reason": "This object cannot be foraged from."}
        
        difficulty, skill_name = self._determine_foraging_difficulty(obj, season)
        skill_modifier = character.get_skill_modifier(skill_name)
        
        # Estimate success chance
        success_chance = max(5, min(95, (skill_modifier + 10.5 - difficulty.value) * 5))
        
        properties = obj.get("properties", {})
        
        return {
            "can_forage": True,
            "skill_required": skill_name,
            "difficulty": difficulty.name,
            "dc": difficulty.value,
            "success_chance": f"{success_chance:.0f}%",
            "seasonal": properties.get("seasonal", False),
            "renewable": properties.get("renewable", True),
            "food_value": properties.get("food_value", 1)
        }


def test_foraging_system():
    """Test the foraging system"""
    print("=== Testing Foraging System ===")
    
    # Create a mock character with survival skill
    class MockCharacter:
        def __init__(self):
            # Create mock skill proficiencies
            class MockSkillProficiencies:
                def get_proficiency_multiplier(self, skill_name):
                    if skill_name in ["Survival", "Nature"]:
                        return 1  # Proficient
                    return 0  # Not proficient
            
            self.skill_proficiencies = MockSkillProficiencies()
            self.wisdom = 14  # +2 modifier
            self.intelligence = 12  # +1 modifier
            self.proficiency_bonus = 2
            
        def ability_modifier(self, ability):
            """Calculate ability modifier"""
            score = getattr(self, ability, 10)
            return (score - 10) // 2
            
        def get_skill_modifier(self, skill_name):
            return 3  # +3 modifier
    
    character = MockCharacter()
    foraging_system = ForagingSystem()
    
    # Test berry bush foraging
    berry_bush = {
        "name": "Berry Bush",
        "pools": ["forest", "wilderness", "food", "common"],
        "properties": {
            "can_forage": True,
            "food_value": 2,
            "seasonal": True,
            "renewable": True
        },
        "item_drops": {
            "pools": ["food", "forest", "natural"],
            "min_drops": 1,
            "max_drops": 3,
            "drop_chance": 80
        }
    }
    
    print("Testing berry bush foraging:")
    info = foraging_system.get_foraging_info(berry_bush, character, "summer")
    print(f"  Can forage: {info['can_forage']}")
    print(f"  Skill: {info['skill_required']}")
    print(f"  Difficulty: {info['difficulty']} (DC {info['dc']})")
    print(f"  Success chance: {info['success_chance']}")
    
    # Test foraging attempt
    result = foraging_system.attempt_foraging(character, berry_bush, "summer")
    print(f"\nForaging attempt:")
    print(f"  Success: {result.success}")
    print(f"  Items found: {len(result.items_found)}")
    print(f"  Message: {result.message}")
    print(f"  Experience: {result.experience_gained}")
    
    print("✓ Foraging system test complete!")
    return foraging_system


if __name__ == "__main__":
    test_foraging_system()