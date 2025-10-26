"""
Fantasy RPG - Weather System

Main weather system module that coordinates all weather-related functionality.
This module imports and re-exports the core weather components for easy access.
"""

# Core weather functionality
try:
    from .weather_core import (
        WeatherState,
        generate_weather_state,
        test_weather_core
    )
    
    # Character weather resistance
    from .character_weather import (
        CharacterWeatherResistance,
        create_character_archetypes,
        test_character_weather
    )
    
    # Travel system
    from .travel_system import (
        TravelMethod,
        BiomeWeatherModifier,
        create_travel_methods,
        create_biome_weather_modifiers,
        test_travel_system
    )
except ImportError:
    # Fallback for direct execution
    from weather_core import (
        WeatherState,
        generate_weather_state,
        test_weather_core
    )
    
    from character_weather import (
        CharacterWeatherResistance,
        create_character_archetypes,
        test_character_weather
    )
    
    from travel_system import (
        TravelMethod,
        BiomeWeatherModifier,
        create_travel_methods,
        create_biome_weather_modifiers,
        test_travel_system
    )

# Re-export main classes for easy importing
__all__ = [
    # Core weather
    'WeatherState',
    'generate_weather_state',
    
    # Character system
    'CharacterWeatherResistance',
    'create_character_archetypes',
    
    # Travel system
    'TravelMethod',
    'BiomeWeatherModifier',
    'create_travel_methods',
    'create_biome_weather_modifiers',
    
    # Test functions
    'test_weather_core',
    'test_character_weather',
    'test_travel_system'
]


def run_all_tests():
    """Run all weather system tests."""
    print("=" * 80)
    print("FANTASY RPG WEATHER SYSTEM - COMPREHENSIVE TESTS")
    print("=" * 80)
    
    test_weather_core()
    print("\n" + "="*60 + "\n")
    
    test_character_weather()
    print("\n" + "="*60 + "\n")
    
    test_travel_system()
    print("\n" + "="*60 + "\n")
    
    print("=" * 80)
    print("ALL WEATHER SYSTEM TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()