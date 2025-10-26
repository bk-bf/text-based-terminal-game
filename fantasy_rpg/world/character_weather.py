"""
Fantasy RPG - Character Weather Resistance

Character-specific weather resistance and adaptation systems.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CharacterWeatherResistance:
    """Character's resistance and adaptation to weather conditions."""
    cold_resistance: int = 0  # Resistance to cold (0-10)
    heat_resistance: int = 0  # Resistance to heat (0-10)
    wind_resistance: int = 0  # Resistance to wind effects (0-10)
    precipitation_resistance: int = 0  # Resistance to rain/snow (0-10)
    magical_resistance: int = 0  # Resistance to magical weather (0-10)
    
    # Equipment bonuses
    clothing_warmth: int = 0  # Warmth from clothing (0-10)
    clothing_waterproof: int = 0  # Waterproofing (0-10)
    shelter_quality: int = 0  # Quality of available shelter (0-10)
    
    # Character traits
    survival_skill: int = 0  # Survival skill level (0-20)
    constitution_bonus: int = 0  # Constitution modifier
    race_bonuses: Dict[str, int] = None  # Racial bonuses to weather resistance
    
    def __post_init__(self):
        """Initialize race bonuses if not provided."""
        if self.race_bonuses is None:
            self.race_bonuses = {}
    
    def get_effective_resistance(self, weather_type: str) -> int:
        """Calculate effective resistance to a specific weather type."""
        base_resistance = {
            "cold": self.cold_resistance,
            "heat": self.heat_resistance,
            "wind": self.wind_resistance,
            "precipitation": self.precipitation_resistance,
            "magical": self.magical_resistance
        }.get(weather_type, 0)
        
        # Add equipment bonuses
        equipment_bonus = 0
        if weather_type == "cold":
            equipment_bonus = self.clothing_warmth
        elif weather_type == "precipitation":
            equipment_bonus = self.clothing_waterproof
        elif weather_type in ["wind", "heat"]:
            equipment_bonus = self.shelter_quality // 2
        
        # Add skill and constitution bonuses
        skill_bonus = self.survival_skill // 4  # 0-5 bonus
        constitution_bonus = self.constitution_bonus
        
        # Add racial bonuses
        racial_bonus = self.race_bonuses.get(weather_type, 0)
        
        total_resistance = (base_resistance + equipment_bonus + 
                          skill_bonus + constitution_bonus + racial_bonus)
        
        return max(0, min(20, total_resistance))  # Cap at 0-20


def create_character_archetypes() -> Dict[str, CharacterWeatherResistance]:
    """Create common character archetypes with their weather resistances."""
    archetypes = {}
    
    # Hardy Ranger - Experienced outdoorsman
    archetypes["hardy_ranger"] = CharacterWeatherResistance(
        cold_resistance=6, heat_resistance=4, wind_resistance=5, precipitation_resistance=7,
        clothing_warmth=8, clothing_waterproof=9, shelter_quality=6,
        survival_skill=15, constitution_bonus=3,
        race_bonuses={"cold": 2, "wind": 1}  # Hardy mountain folk
    )
    
    # City Noble - Pampered and inexperienced
    archetypes["city_noble"] = CharacterWeatherResistance(
        cold_resistance=1, heat_resistance=1, wind_resistance=0, precipitation_resistance=2,
        clothing_warmth=3, clothing_waterproof=2, shelter_quality=8,
        survival_skill=2, constitution_bonus=0,
        race_bonuses={}  # No special resistances
    )
    
    # Desert Nomad - Adapted to harsh desert conditions
    archetypes["desert_nomad"] = CharacterWeatherResistance(
        cold_resistance=2, heat_resistance=8, wind_resistance=6, precipitation_resistance=3,
        clothing_warmth=2, clothing_waterproof=1, shelter_quality=4,
        survival_skill=12, constitution_bonus=2,
        race_bonuses={"heat": 3, "wind": 2}  # Desert-adapted
    )
    
    # Arctic Explorer - Cold weather specialist
    archetypes["arctic_explorer"] = CharacterWeatherResistance(
        cold_resistance=9, heat_resistance=2, wind_resistance=7, precipitation_resistance=8,
        clothing_warmth=10, clothing_waterproof=8, shelter_quality=5,
        survival_skill=14, constitution_bonus=2,
        race_bonuses={"cold": 4, "wind": 2}  # Cold-adapted
    )
    
    # Sailor - Maritime weather experience
    archetypes["sailor"] = CharacterWeatherResistance(
        cold_resistance=4, heat_resistance=3, wind_resistance=8, precipitation_resistance=9,
        clothing_warmth=5, clothing_waterproof=10, shelter_quality=3,
        survival_skill=10, constitution_bonus=1,
        race_bonuses={"wind": 3, "precipitation": 2}  # Sea-adapted
    )
    
    # Wizard - Magical protection but physically weak
    archetypes["wizard"] = CharacterWeatherResistance(
        cold_resistance=2, heat_resistance=2, wind_resistance=1, precipitation_resistance=3,
        magical_resistance=7, clothing_warmth=4, clothing_waterproof=3, shelter_quality=7,
        survival_skill=5, constitution_bonus=-1,
        race_bonuses={"magical": 3}  # Magical resistance
    )
    
    # Barbarian - Tough and hardy
    archetypes["barbarian"] = CharacterWeatherResistance(
        cold_resistance=7, heat_resistance=6, wind_resistance=5, precipitation_resistance=4,
        clothing_warmth=3, clothing_waterproof=2, shelter_quality=2,
        survival_skill=8, constitution_bonus=4,
        race_bonuses={"cold": 2, "heat": 2}  # Natural toughness
    )
    
    return archetypes


def test_character_weather():
    """Test character weather resistance system."""
    print("=== Testing Character Weather Resistance System ===")
    
    # Test 1: Character archetype resistances
    print("\n1. Testing character archetype resistances:")
    
    archetypes = create_character_archetypes()
    
    for name, character in archetypes.items():
        print(f"\n{name.replace('_', ' ').title()}:")
        for weather_type in ["cold", "heat", "wind", "precipitation", "magical"]:
            resistance = character.get_effective_resistance(weather_type)
            print(f"  {weather_type.title()}: {resistance}/20")
    
    # Test 2: Equipment impact
    print("\n2. Testing equipment impact:")
    
    base_character = CharacterWeatherResistance(
        cold_resistance=2, heat_resistance=2, wind_resistance=2, precipitation_resistance=2,
        survival_skill=5, constitution_bonus=1
    )
    
    print("Base character resistances:")
    for weather_type in ["cold", "heat", "wind", "precipitation"]:
        resistance = base_character.get_effective_resistance(weather_type)
        print(f"  {weather_type.title()}: {resistance}/20")
    
    # Add equipment
    equipped_character = CharacterWeatherResistance(
        cold_resistance=2, heat_resistance=2, wind_resistance=2, precipitation_resistance=2,
        clothing_warmth=8, clothing_waterproof=7, shelter_quality=6,
        survival_skill=5, constitution_bonus=1
    )
    
    print("\nWith equipment:")
    for weather_type in ["cold", "heat", "wind", "precipitation"]:
        resistance = equipped_character.get_effective_resistance(weather_type)
        print(f"  {weather_type.title()}: {resistance}/20")
    
    # Test 3: Racial bonuses
    print("\n3. Testing racial bonuses:")
    
    # Dwarf - mountain folk
    dwarf = CharacterWeatherResistance(
        cold_resistance=3, heat_resistance=1, wind_resistance=3, precipitation_resistance=2,
        survival_skill=8, constitution_bonus=2,
        race_bonuses={"cold": 3, "wind": 2}  # Mountain adaptation
    )
    
    # Fire Genasi - elemental heritage
    fire_genasi = CharacterWeatherResistance(
        cold_resistance=1, heat_resistance=3, wind_resistance=2, precipitation_resistance=1,
        survival_skill=6, constitution_bonus=1,
        race_bonuses={"heat": 5, "magical": 2}  # Fire resistance
    )
    
    races = [("Dwarf", dwarf), ("Fire Genasi", fire_genasi)]
    
    for race_name, character in races:
        print(f"\n{race_name}:")
        for weather_type in ["cold", "heat", "wind", "precipitation", "magical"]:
            resistance = character.get_effective_resistance(weather_type)
            print(f"  {weather_type.title()}: {resistance}/20")
    
    # Test 4: Skill progression impact
    print("\n4. Testing skill progression impact:")
    
    skill_levels = [0, 5, 10, 15, 20]
    
    print("Survival skill impact on cold resistance:")
    for skill in skill_levels:
        character = CharacterWeatherResistance(
            cold_resistance=3, survival_skill=skill, constitution_bonus=1
        )
        resistance = character.get_effective_resistance("cold")
        print(f"  Skill {skill:2d}: {resistance}/20 resistance")
    
    print("\n=== Character weather resistance system testing complete! ===")


if __name__ == "__main__":
    test_character_weather()