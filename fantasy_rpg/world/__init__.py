"""
Fantasy RPG - World Generation and Management

This package contains world generation systems including terrain generation,
climate simulation, weather systems, and world management.
"""

# Import world classes for easy access
from .terrain_generation import TerrainGenerator, NoiseGenerator
from .world import World

# Import weather system components
from .weather_core import WeatherState, generate_weather_state
from .character_weather import CharacterWeatherResistance, create_character_archetypes
from .travel_system import TravelMethod, BiomeWeatherModifier, create_travel_methods, create_biome_weather_modifiers

__all__ = [
    # World generation
    'TerrainGenerator', 'NoiseGenerator', 'World',
    
    # Weather system
    'WeatherState', 'generate_weather_state',
    'CharacterWeatherResistance', 'create_character_archetypes',
    'TravelMethod', 'BiomeWeatherModifier', 'create_travel_methods', 'create_biome_weather_modifiers'
]