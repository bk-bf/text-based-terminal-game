"""
Fantasy RPG - World Generation and Management

This package contains world generation systems including terrain generation,
climate simulation, weather systems, and world management.

The WorldCoordinator serves as the central integration point for all world systems.
"""

# Main coordinator - primary entry point
from .world_coordinator import WorldCoordinator

# Core world classes (for advanced usage)
from .world import World, Hex

# Individual systems (for direct access if needed)
from .terrain_generation import TerrainGenerator, NoiseGenerator
from .biomes import BiomeClassifier
from .enhanced_biomes import EnhancedBiomeSystem

# Weather system components
from .weather_core import WeatherState, generate_weather_state
from .character_weather import CharacterWeatherResistance, create_character_archetypes
from .travel_system import TravelMethod, BiomeWeatherModifier, create_travel_methods, create_biome_weather_modifiers

# Location exploration (accessed through WorldCoordinator)
# Note: ExplorationInterface is now in ../locations/interface.py

__all__ = [
    # Main coordinator (recommended entry point)
    'WorldCoordinator',
    
    # Core world classes
    'World', 'Hex',
    
    # Individual systems (for advanced usage)
    'TerrainGenerator', 'NoiseGenerator', 'BiomeClassifier', 'EnhancedBiomeSystem',
    
    # Weather system
    'WeatherState', 'generate_weather_state',
    'CharacterWeatherResistance', 'create_character_archetypes',
    'TravelMethod', 'BiomeWeatherModifier', 'create_travel_methods', 'create_biome_weather_modifiers',
    
    # Note: Location systems are now in separate packages:
    # - fantasy_rpg.locations for exploration systems
    # - fantasy_rpg.combat for combat systems
]