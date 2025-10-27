"""
Fantasy RPG - Shelter System

Natural shelter detection, camping mechanics, and weather protection.
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from .skills import SkillSystem
except ImportError:
    from skills import SkillSystem


class ShelterType(Enum):
    """Types of shelter available"""
    NONE = "none"
    NATURAL_OVERHANG = "natural_overhang"
    CAVE_ENTRANCE = "cave_entrance"
    DENSE_TREES = "dense_trees"
    MAKESHIFT_LEAN_TO = "makeshift_lean_to"
    PROPER_CAMP = "proper_camp"
    STRUCTURE_INTERIOR = "structure_interior"


class ShelterQuality(Enum):
    """Quality levels of shelter"""
    EXPOSED = 0      # No protection
    MINIMAL = 1      # Slight protection from elements
    BASIC = 2        # Basic protection from rain/wind
    GOOD = 3         # Good protection from weather
    EXCELLENT = 4    # Excellent protection, comfortable rest


@dataclass
class ShelterInfo:
    """Information about available shelter"""
    shelter_type: ShelterType
    quality: ShelterQuality
    weather_protection: Dict[str, int]  # Protection values for different weather
    rest_bonus: int = 0                 # Bonus to rest recovery
    fire_possible: bool = True          # Can build fire here
    concealment: int = 0               # Stealth bonus when resting
    description: str = ""


@dataclass
class CampingResult:
    """Result of attempting to make camp"""
    success: bool
    shelter_created: Optional[ShelterInfo]
    skill_check_result: Dict
    message: str
    time_spent: int = 60  # minutes
    materials_used: List[str] = None


class ShelterSystem:
    """Handles shelter detection and camping mechanics"""
    
    def __init__(self):
        # Weather protection values by shelter type
        self.shelter_protection = {
            ShelterType.NONE: {
                "rain": 0, "wind": 0, "cold": 0, "heat": 0
            },
            ShelterType.NATURAL_OVERHANG: {
                "rain": 3, "wind": 1, "cold": 1, "heat": 2
            },
            ShelterType.CAVE_ENTRANCE: {
                "rain": 4, "wind": 3, "cold": 2, "heat": 3
            },
            ShelterType.DENSE_TREES: {
                "rain": 2, "wind": 2, "cold": 1, "heat": 1
            },
            ShelterType.MAKESHIFT_LEAN_TO: {
                "rain": 2, "wind": 2, "cold": 1, "heat": 1
            },
            ShelterType.PROPER_CAMP: {
                "rain": 3, "wind": 3, "cold": 2, "heat": 2
            },
            ShelterType.STRUCTURE_INTERIOR: {
                "rain": 5, "wind": 5, "cold": 3, "heat": 4
            }
        }
    
    def detect_natural_shelter(self, location_data: Dict, character) -> List[ShelterInfo]:
        """Detect available natural shelter at current location"""
        available_shelters = []
        
        # Check location objects for shelter opportunities
        objects = location_data.get("objects", [])
        terrain = location_data.get("terrain", "open")
        biome = location_data.get("biome", "temperate")
        
        # Natural shelter from objects
        for obj in objects:
            shelter = self._check_object_for_shelter(obj)
            if shelter:
                available_shelters.append(shelter)
        
        # Terrain-based shelter
        terrain_shelter = self._check_terrain_for_shelter(terrain, biome)
        if terrain_shelter:
            available_shelters.append(terrain_shelter)
        
        # Structure-based shelter
        if any(obj.get("type") == "structure" for obj in objects):
            structure_shelter = ShelterInfo(
                shelter_type=ShelterType.STRUCTURE_INTERIOR,
                quality=ShelterQuality.EXCELLENT,
                weather_protection=self.shelter_protection[ShelterType.STRUCTURE_INTERIOR],
                rest_bonus=2,
                fire_possible=True,
                concealment=3,
                description="You can take shelter inside the structure, protected from the elements."
            )
            available_shelters.append(structure_shelter)
        
        return available_shelters
    
    def attempt_camping(self, character, materials_available: List[str] = None, 
                       shelter_type: ShelterType = ShelterType.MAKESHIFT_LEAN_TO) -> CampingResult:
        """Attempt to make camp and create shelter"""
        
        if materials_available is None:
            materials_available = []
        
        # Determine difficulty based on shelter type and available materials
        difficulty, required_materials = self._get_camping_requirements(shelter_type, materials_available)
        
        # Make survival skill check
        skill_result = SkillSystem.make_skill_check(character, "Survival", difficulty)
        
        if skill_result["success"]:
            # Create shelter
            shelter = self._create_shelter(shelter_type, skill_result, materials_available)
            message = self._generate_camping_success_message(shelter, skill_result)
            materials_used = required_materials
        else:
            # Failed to make proper camp
            shelter = self._create_basic_shelter()
            message = self._generate_camping_failure_message(skill_result)
            materials_used = []
        
        return CampingResult(
            success=skill_result["success"],
            shelter_created=shelter,
            skill_check_result=skill_result,
            message=message,
            materials_used=materials_used
        )
    
    def _check_object_for_shelter(self, obj: Dict) -> Optional[ShelterInfo]:
        """Check if an object provides natural shelter"""
        obj_name = obj.get("name", "").lower()
        properties = obj.get("properties", {})
        
        # Cave entrances
        if "cave" in obj_name or "cavern" in obj_name:
            return ShelterInfo(
                shelter_type=ShelterType.CAVE_ENTRANCE,
                quality=ShelterQuality.GOOD,
                weather_protection=self.shelter_protection[ShelterType.CAVE_ENTRANCE],
                rest_bonus=1,
                fire_possible=True,
                concealment=2,
                description=f"The {obj.get('name')} provides excellent natural shelter from the elements."
            )
        
        # Rock formations and overhangs
        if any(word in obj_name for word in ["rock", "overhang", "cliff", "outcrop"]):
            return ShelterInfo(
                shelter_type=ShelterType.NATURAL_OVERHANG,
                quality=ShelterQuality.BASIC,
                weather_protection=self.shelter_protection[ShelterType.NATURAL_OVERHANG],
                rest_bonus=0,
                fire_possible=True,
                concealment=1,
                description=f"The {obj.get('name')} offers some protection from rain and wind."
            )
        
        # Dense vegetation
        if any(word in obj_name for word in ["thicket", "dense", "grove"]) or \
           properties.get("provides_concealment", False):
            return ShelterInfo(
                shelter_type=ShelterType.DENSE_TREES,
                quality=ShelterQuality.MINIMAL,
                weather_protection=self.shelter_protection[ShelterType.DENSE_TREES],
                rest_bonus=0,
                fire_possible=True,
                concealment=2,
                description=f"The {obj.get('name')} provides some shelter and concealment."
            )
        
        return None
    
    def _check_terrain_for_shelter(self, terrain: str, biome: str) -> Optional[ShelterInfo]:
        """Check terrain for natural shelter opportunities"""
        terrain_lower = terrain.lower()
        
        if "forest" in biome.lower() and terrain_lower in ["cluttered", "difficult"]:
            return ShelterInfo(
                shelter_type=ShelterType.DENSE_TREES,
                quality=ShelterQuality.MINIMAL,
                weather_protection=self.shelter_protection[ShelterType.DENSE_TREES],
                rest_bonus=0,
                fire_possible=True,
                concealment=1,
                description="The dense forest canopy provides some natural shelter."
            )
        
        return None
    
    def _get_camping_requirements(self, shelter_type: ShelterType, 
                                 available_materials: List[str]) -> Tuple[int, List[str]]:
        """Get difficulty and required materials for camping"""
        
        requirements = {
            ShelterType.MAKESHIFT_LEAN_TO: {
                "dc": 12,
                "materials": ["wood", "rope"],
                "optional": ["leaves", "branches"]
            },
            ShelterType.PROPER_CAMP: {
                "dc": 15,
                "materials": ["wood", "rope", "tarp"],
                "optional": ["stakes", "cordage"]
            }
        }
        
        req = requirements.get(shelter_type, {"dc": 15, "materials": [], "optional": []})
        
        # Reduce DC if we have required materials
        dc = req["dc"]
        required_materials = []
        
        for material in req["materials"]:
            if any(material in item.lower() for item in available_materials):
                dc -= 2
                required_materials.append(material)
        
        # Small bonus for optional materials
        for material in req["optional"]:
            if any(material in item.lower() for item in available_materials):
                dc -= 1
        
        return max(8, dc), required_materials
    
    def _create_shelter(self, shelter_type: ShelterType, skill_result: Dict, 
                       materials: List[str]) -> ShelterInfo:
        """Create shelter based on success"""
        
        # Base shelter quality
        quality = ShelterQuality.BASIC
        rest_bonus = 0
        concealment = 0
        
        # Improve quality based on skill check success
        success_margin = skill_result["total"] - skill_result["dc"]
        if success_margin >= 10:
            quality = ShelterQuality.EXCELLENT
            rest_bonus = 2
            concealment = 2
        elif success_margin >= 5:
            quality = ShelterQuality.GOOD
            rest_bonus = 1
            concealment = 1
        
        # Material bonuses
        if len(materials) >= 3:
            rest_bonus += 1
            concealment += 1
        
        description = self._generate_shelter_description(shelter_type, quality, materials)
        
        return ShelterInfo(
            shelter_type=shelter_type,
            quality=quality,
            weather_protection=self.shelter_protection[shelter_type],
            rest_bonus=rest_bonus,
            fire_possible=True,
            concealment=concealment,
            description=description
        )
    
    def _create_basic_shelter(self) -> ShelterInfo:
        """Create minimal shelter when camping fails"""
        return ShelterInfo(
            shelter_type=ShelterType.MAKESHIFT_LEAN_TO,
            quality=ShelterQuality.MINIMAL,
            weather_protection=self.shelter_protection[ShelterType.MAKESHIFT_LEAN_TO],
            rest_bonus=0,
            fire_possible=True,
            concealment=0,
            description="You manage to create a basic windbreak, but it offers minimal protection."
        )
    
    def _generate_shelter_description(self, shelter_type: ShelterType, 
                                    quality: ShelterQuality, materials: List[str]) -> str:
        """Generate description for created shelter"""
        
        quality_desc = {
            ShelterQuality.MINIMAL: "basic",
            ShelterQuality.BASIC: "decent",
            ShelterQuality.GOOD: "well-constructed",
            ShelterQuality.EXCELLENT: "expertly crafted"
        }
        
        if shelter_type == ShelterType.MAKESHIFT_LEAN_TO:
            base = f"You construct a {quality_desc[quality]} lean-to shelter"
        elif shelter_type == ShelterType.PROPER_CAMP:
            base = f"You set up a {quality_desc[quality]} camp"
        else:
            base = f"You create a {quality_desc[quality]} shelter"
        
        if materials:
            material_desc = ", ".join(materials)
            return f"{base} using {material_desc}. It provides good protection from the elements."
        else:
            return f"{base} from available natural materials."
    
    def _generate_camping_success_message(self, shelter: ShelterInfo, skill_result: Dict) -> str:
        """Generate success message for camping"""
        skill_total = skill_result.get("total", 0)
        return f"Your Survival check ({skill_total}) succeeds! {shelter.description}"
    
    def _generate_camping_failure_message(self, skill_result: Dict) -> str:
        """Generate failure message for camping"""
        skill_total = skill_result.get("total", 0)
        dc = skill_result.get("dc", 15)
        return f"Your Survival check ({skill_total}) fails (DC {dc}). You struggle to create proper shelter and end up with only basic protection from the elements."
    
    def calculate_weather_protection(self, shelter: ShelterInfo, weather_conditions: Dict) -> Dict:
        """Calculate protection provided by shelter against current weather"""
        protection = {}
        
        for condition, severity in weather_conditions.items():
            shelter_protection = shelter.weather_protection.get(condition, 0)
            effective_severity = max(0, severity - shelter_protection)
            protection[condition] = {
                "original": severity,
                "protected": effective_severity,
                "reduction": shelter_protection
            }
        
        return protection
    
    def get_rest_modifiers(self, shelter: ShelterInfo, weather_conditions: Dict) -> Dict:
        """Get rest modifiers based on shelter and weather"""
        base_rest_bonus = shelter.rest_bonus
        
        # Weather penalties
        weather_penalty = 0
        protection = self.calculate_weather_protection(shelter, weather_conditions)
        
        for condition, values in protection.items():
            if values["protected"] > 3:  # Severe weather still affecting rest
                weather_penalty += 1
        
        final_rest_bonus = max(-3, base_rest_bonus - weather_penalty)
        
        return {
            "rest_bonus": final_rest_bonus,
            "weather_penalty": weather_penalty,
            "shelter_bonus": base_rest_bonus,
            "concealment": shelter.concealment
        }


def test_shelter_system():
    """Test the shelter system"""
    print("=== Testing Shelter System ===")
    
    # Create mock character
    class MockCharacter:
        def __init__(self):
            # Create mock skill proficiencies
            class MockSkillProficiencies:
                def get_proficiency_multiplier(self, skill_name):
                    if skill_name == "Survival":
                        return 1  # Proficient
                    return 0  # Not proficient
            
            self.skill_proficiencies = MockSkillProficiencies()
            self.wisdom = 16  # +3 modifier
            self.proficiency_bonus = 2
            
        def ability_modifier(self, ability):
            """Calculate ability modifier"""
            score = getattr(self, ability, 10)
            return (score - 10) // 2
            
        def get_skill_modifier(self, skill_name):
            return 4  # +4 Survival
    
    character = MockCharacter()
    shelter_system = ShelterSystem()
    
    # Test natural shelter detection
    location_data = {
        "objects": [
            {
                "name": "Rock Overhang",
                "type": "natural_feature"
            },
            {
                "name": "Dense Thicket",
                "properties": {"provides_concealment": True}
            }
        ],
        "terrain": "cluttered",
        "biome": "temperate_forest"
    }
    
    print("Testing natural shelter detection:")
    shelters = shelter_system.detect_natural_shelter(location_data, character)
    for i, shelter in enumerate(shelters, 1):
        print(f"  {i}. {shelter.shelter_type.value} - Quality: {shelter.quality.name}")
        print(f"     {shelter.description}")
        print(f"     Weather protection: {shelter.weather_protection}")
    
    # Test camping
    print(f"\nTesting camping attempt:")
    materials = ["Firewood", "Hemp Rope", "Dried Leaves"]
    result = shelter_system.attempt_camping(character, materials, ShelterType.MAKESHIFT_LEAN_TO)
    
    print(f"  Success: {result.success}")
    print(f"  Message: {result.message}")
    if result.shelter_created:
        print(f"  Shelter quality: {result.shelter_created.quality.name}")
        print(f"  Rest bonus: {result.shelter_created.rest_bonus}")
        print(f"  Materials used: {result.materials_used}")
    
    # Test weather protection
    print(f"\nTesting weather protection:")
    weather = {"rain": 3, "wind": 2, "cold": 1}
    if result.shelter_created:
        protection = shelter_system.calculate_weather_protection(result.shelter_created, weather)
        for condition, values in protection.items():
            print(f"  {condition.title()}: {values['original']} -> {values['protected']} (reduced by {values['reduction']})")
    
    print("✓ Shelter system test complete!")
    return shelter_system


if __name__ == "__main__":
    test_shelter_system()