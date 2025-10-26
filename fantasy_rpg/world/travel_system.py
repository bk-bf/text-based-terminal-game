"""
Fantasy RPG - Travel System

Travel methods, modifiers, and weather-based travel calculations.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random
import math

try:
    from .weather_core import WeatherState
    from .character_weather import CharacterWeatherResistance
except ImportError:
    from weather_core import WeatherState
    from character_weather import CharacterWeatherResistance


@dataclass
class TravelMethod:
    """Represents different methods of travel and their weather sensitivities."""
    method_name: str
    base_speed_mph: float
    
    # Weather sensitivity factors (0.0 = immune, 1.0 = normal, >1.0 = extra sensitive)
    temperature_sensitivity: float = 1.0
    wind_sensitivity: float = 1.0
    precipitation_sensitivity: float = 1.0
    visibility_sensitivity: float = 1.0
    terrain_sensitivity: float = 1.0
    
    # Special modifiers
    magical_resistance: float = 0.0  # 0.0-1.0, resistance to magical weather
    weather_protection: float = 0.0  # 0.0-1.0, built-in weather protection
    
    # Travel method specific bonuses/penalties
    special_conditions: Dict[str, float] = None  # Condition -> speed modifier
    
    def __post_init__(self):
        """Initialize special conditions if not provided."""
        if self.special_conditions is None:
            self.special_conditions = {}


@dataclass
class BiomeWeatherModifier:
    """How different biomes modify weather effects."""
    biome_type: str
    
    # Travel modifiers
    base_travel_difficulty: float = 1.0  # Multiplier for travel speed
    weather_amplification: float = 1.0  # How much biome amplifies weather effects
    
    # Shelter availability
    natural_shelter: int = 5  # 0-10, availability of natural shelter
    visibility_modifier: float = 1.0  # Biome's effect on visibility
    
    # Hazard modifiers
    temperature_extremes: float = 1.0  # How much biome amplifies temperature effects
    wind_exposure: float = 1.0  # How exposed the biome is to wind
    precipitation_impact: float = 1.0  # How much precipitation affects travel
    
    # Special biome effects
    special_hazards: List[str] = None  # Biome-specific weather hazards
    magical_conductivity: float = 1.0  # How well biome conducts magical weather
    
    def __post_init__(self):
        """Initialize special hazards if not provided."""
        if self.special_hazards is None:
            self.special_hazards = []


def create_travel_methods() -> Dict[str, TravelMethod]:
    """Create different travel methods with their weather sensitivities."""
    methods = {}
    
    # Walking/Hiking
    methods["walking"] = TravelMethod(
        method_name="walking",
        base_speed_mph=3.0,
        temperature_sensitivity=1.2,
        wind_sensitivity=1.1,
        precipitation_sensitivity=1.3,
        visibility_sensitivity=1.0,
        terrain_sensitivity=1.5,
        special_conditions={
            "deep_snow": 0.4,
            "mud": 0.6,
            "ice": 0.3,
            "perfect_weather": 1.1
        }
    )
    
    # Horseback Riding
    methods["horseback"] = TravelMethod(
        method_name="horseback",
        base_speed_mph=8.0,
        temperature_sensitivity=0.9,  # Horses handle weather better than humans
        wind_sensitivity=1.0,
        precipitation_sensitivity=1.2,
        visibility_sensitivity=1.1,  # Horses can navigate better in poor visibility
        terrain_sensitivity=1.2,
        special_conditions={
            "lightning": 0.5,  # Horses spook at lightning
            "deep_snow": 0.5,
            "mud": 0.7,
            "ice": 0.4,
            "grassland": 1.2  # Horses excel on open terrain
        }
    )
    
    # Cart/Wagon
    methods["cart"] = TravelMethod(
        method_name="cart",
        base_speed_mph=4.0,
        temperature_sensitivity=0.8,  # Some protection from weather
        wind_sensitivity=1.3,  # Wind affects large cart
        precipitation_sensitivity=1.5,  # Wheels get stuck easily
        visibility_sensitivity=0.9,  # Driver has elevated view
        terrain_sensitivity=2.0,  # Very terrain dependent
        weather_protection=0.3,
        special_conditions={
            "mud": 0.3,  # Carts get stuck badly in mud
            "deep_snow": 0.2,
            "ice": 0.1,
            "roads": 1.5,  # Much faster on roads
            "rocky_terrain": 0.4
        }
    )
    
    # Boat/Ship (river/coastal)
    methods["boat"] = TravelMethod(
        method_name="boat",
        base_speed_mph=6.0,
        temperature_sensitivity=0.7,  # Water moderates temperature
        wind_sensitivity=1.8,  # Very wind dependent
        precipitation_sensitivity=0.8,  # Rain doesn't slow boats much
        visibility_sensitivity=1.5,  # Navigation critical
        terrain_sensitivity=0.0,  # Terrain irrelevant
        weather_protection=0.2,
        special_conditions={
            "storm": 0.2,  # Dangerous in storms
            "calm_water": 1.3,
            "favorable_wind": 1.8,
            "headwind": 0.6,
            "fog": 0.3,  # Very dangerous in fog
            "ice": 0.0  # Can't travel on frozen water
        }
    )
    
    # Flying (magical or mounted)
    methods["flying"] = TravelMethod(
        method_name="flying",
        base_speed_mph=15.0,
        temperature_sensitivity=1.5,  # Exposed to altitude effects
        wind_sensitivity=2.0,  # Very wind sensitive
        precipitation_sensitivity=1.4,
        visibility_sensitivity=1.8,  # Critical for navigation
        terrain_sensitivity=0.0,  # Terrain irrelevant
        magical_resistance=0.3,  # Some magical protection
        special_conditions={
            "storm": 0.1,  # Extremely dangerous
            "high_winds": 0.3,
            "clear_skies": 1.4,
            "magical_storm": 0.2,
            "mountain_winds": 0.5
        }
    )
    
    # Magical Transportation (teleport, dimension door, etc.)
    methods["magical_transport"] = TravelMethod(
        method_name="magical_transport",
        base_speed_mph=100.0,  # Effectively instantaneous
        temperature_sensitivity=0.0,
        wind_sensitivity=0.0,
        precipitation_sensitivity=0.0,
        visibility_sensitivity=0.0,
        terrain_sensitivity=0.0,
        magical_resistance=0.8,
        weather_protection=1.0,
        special_conditions={
            "magical_storm": 0.6,  # Magical interference
            "planar_rift": 0.3,
            "anti_magic_field": 0.0,
            "ley_line_proximity": 1.2
        }
    )
    
    return methods


def create_biome_weather_modifiers() -> Dict[str, BiomeWeatherModifier]:
    """Create weather modifiers for different biome types."""
    modifiers = {}
    
    # Forest biomes
    modifiers["forest"] = BiomeWeatherModifier(
        biome_type="forest",
        base_travel_difficulty=1.2,
        weather_amplification=0.8,  # Trees provide some protection
        natural_shelter=8,
        visibility_modifier=0.7,  # Dense trees reduce visibility
        temperature_extremes=0.7,  # Forest moderates temperature
        wind_exposure=0.6,  # Trees block wind
        precipitation_impact=1.3,  # Mud and undergrowth slow travel
        special_hazards=["falling_branches", "flash_floods"],
        magical_conductivity=1.2  # Nature magic flows well
    )
    
    # Plains/Grassland
    modifiers["grassland"] = BiomeWeatherModifier(
        biome_type="grassland",
        base_travel_difficulty=0.9,  # Easy travel normally
        weather_amplification=1.2,  # Very exposed to weather
        natural_shelter=2,  # Little natural shelter
        visibility_modifier=1.3,  # Open terrain, good visibility
        temperature_extremes=1.3,  # No protection from temperature
        wind_exposure=1.5,  # Very exposed to wind
        precipitation_impact=1.1,  # Some mud, but generally good drainage
        special_hazards=["lightning_strikes", "tornadoes"],
        magical_conductivity=0.9
    )
    
    # Mountains
    modifiers["mountains"] = BiomeWeatherModifier(
        biome_type="mountains",
        base_travel_difficulty=1.8,  # Difficult terrain
        weather_amplification=1.5,  # Weather is more extreme at altitude
        natural_shelter=6,  # Caves and overhangs available
        visibility_modifier=1.1,  # Generally good visibility when clear
        temperature_extremes=1.6,  # Extreme temperature variations
        wind_exposure=1.4,  # High winds at altitude
        precipitation_impact=1.4,  # Snow and ice make travel dangerous
        special_hazards=["avalanches", "altitude_sickness", "rockslides"],
        magical_conductivity=1.3  # High altitude enhances magic
    )
    
    # Desert
    modifiers["desert"] = BiomeWeatherModifier(
        biome_type="desert",
        base_travel_difficulty=1.4,  # Sand and heat make travel difficult
        weather_amplification=1.4,  # Extreme temperature swings
        natural_shelter=1,  # Very little natural shelter
        visibility_modifier=1.2,  # Good visibility normally
        temperature_extremes=1.8,  # Extreme heat and cold
        wind_exposure=1.3,  # Open to wind, sandstorms
        precipitation_impact=0.8,  # Rain is rare but causes flash floods
        special_hazards=["sandstorms", "heat_exhaustion", "flash_floods"],
        magical_conductivity=0.7  # Dry conditions inhibit some magic
    )
    
    # Coastal
    modifiers["coastal"] = BiomeWeatherModifier(
        biome_type="coastal",
        base_travel_difficulty=1.1,
        weather_amplification=1.1,  # Moderate weather effects
        natural_shelter=4,  # Some cliffs and dunes
        visibility_modifier=0.9,  # Fog and sea spray reduce visibility
        temperature_extremes=0.8,  # Ocean moderates temperature
        wind_exposure=1.3,  # Exposed to sea winds
        precipitation_impact=1.2,  # Salt spray and storms
        special_hazards=["storm_surge", "fog", "high_tides"],
        magical_conductivity=1.1  # Water enhances some magic
    )
    
    # Swamp/Wetlands
    modifiers["swamp"] = BiomeWeatherModifier(
        biome_type="swamp",
        base_travel_difficulty=2.0,  # Very difficult terrain
        weather_amplification=0.9,  # Humidity moderates some effects
        natural_shelter=5,  # Trees and elevated areas
        visibility_modifier=0.6,  # Fog and vegetation limit visibility
        temperature_extremes=0.6,  # Water moderates temperature
        wind_exposure=0.7,  # Vegetation blocks wind
        precipitation_impact=1.6,  # Already wet, more rain makes it worse
        special_hazards=["disease", "quicksand", "toxic_gases"],
        magical_conductivity=1.4  # High magical conductivity
    )
    
    return modifiers


def test_travel_system():
    """Test the travel system."""
    print("=== Testing Travel System ===")
    
    # Test 1: Travel method characteristics
    print("\n1. Testing travel method characteristics:")
    
    methods = create_travel_methods()
    
    for name, method in methods.items():
        print(f"\n{name.title()}:")
        print(f"  Base speed: {method.base_speed_mph} mph")
        print(f"  Temperature sensitivity: {method.temperature_sensitivity:.1f}")
        print(f"  Wind sensitivity: {method.wind_sensitivity:.1f}")
        print(f"  Weather protection: {method.weather_protection:.1f}")
        if method.special_conditions:
            print(f"  Special conditions: {len(method.special_conditions)}")
    
    # Test 2: Biome modifiers
    print("\n2. Testing biome modifiers:")
    
    biome_modifiers = create_biome_weather_modifiers()
    
    for name, modifier in biome_modifiers.items():
        print(f"\n{name.title()}:")
        print(f"  Travel difficulty: {modifier.base_travel_difficulty:.1f}x")
        print(f"  Weather amplification: {modifier.weather_amplification:.1f}x")
        print(f"  Natural shelter: {modifier.natural_shelter}/10")
        print(f"  Special hazards: {len(modifier.special_hazards)}")
    
    # Test 3: Method comparison in different weather
    print("\n3. Testing method comparison in different weather:")
    
    # Create test weather conditions
    mild_weather = WeatherState(65.0, 8, "SW", 10, "none", 30, 5000, 0.0, False, 0.0)
    storm_weather = WeatherState(35.0, 35, "NW", 80, "rain", 100, 300, 0.0, False, 0.0)
    
    weather_conditions = [("Mild", mild_weather), ("Storm", storm_weather)]
    
    for weather_name, weather in weather_conditions:
        print(f"\n{weather_name} weather travel modifiers:")
        
        travel_mods = weather.get_travel_modifier()
        print(f"  Base weather impact: {travel_mods['speed_penalty']:.1%}")
        
        # Show how different methods would be affected
        for method_name in ["walking", "horseback", "cart", "flying"]:
            method = methods[method_name]
            
            # Simple calculation of method-specific impact
            temp_impact = 1.0
            if weather.feels_like < 32 or weather.feels_like > 85:
                temp_stress = abs(weather.feels_like - 58.5) / 26.5  # Normalize around comfortable temp
                temp_impact = max(0.5, 1.0 - temp_stress * method.temperature_sensitivity * 0.3)
            
            wind_impact = max(0.6, 1.0 - (weather.wind_speed / 50.0) * method.wind_sensitivity)
            
            method_modifier = temp_impact * wind_impact * travel_mods['speed_penalty']
            
            print(f"    {method_name.title()}: {method_modifier:.1%}")
    
    print("\n=== Travel system testing complete! ===")


if __name__ == "__main__":
    test_travel_system()