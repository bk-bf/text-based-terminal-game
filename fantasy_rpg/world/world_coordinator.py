"""
Fantasy RPG - World Coordinator

Central coordinator for all world-related systems. This file serves as the single
point of integration between terrain generation, climate systems, biome classification,
location exploration, and all other world components.

This prevents circular imports and provides clear data flow architecture.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import random

# Core world components
from world import World, Hex
from terrain_generation import TerrainGenerator
from climate import ClimateSystem
from biomes import BiomeClassifier
from enhanced_biomes import EnhancedBiomeSystem

# Location systems (from separate locations package)
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from locations.location_generator import LocationGenerator, Location, LocationType
except ImportError:
    print("Warning: Could not import location systems, using placeholders")
    # Placeholder classes if import fails
    class LocationGenerator:
        def __init__(self, seed=None):
            self.seed = seed
        def generate_location_for_hex(self, coords, biome, terrain=None):
            return Location("placeholder", "Placeholder Location", "wilderness")
    
    class Location:
        def __init__(self, id, name, type):
            self.id = id
            self.name = name
            self.type = type
            self.areas = {}
    
    class LocationType:
        WILDERNESS = "wilderness"

# Simple location manager for world coordinator
class LocationManager:
    def __init__(self, world):
        self.world = world
        self.location_generator = LocationGenerator()
    
    def get_explorable_locations(self, coords):
        # Get hex data
        hex_data = self.world.get_hex_data(coords)
        biome = hex_data.get('biome', 'plains')
        
        # Generate a location for this hex
        location = self.location_generator.generate_location_for_hex(coords, biome)
        return [location]
    
    def display_hex_locations(self, coords):
        locations = self.get_explorable_locations(coords)
        hex_data = self.world.get_hex_data(coords)
        biome = hex_data.get('biome', 'plains')
        
        output = []
        output.append("╔" + "═" * 58 + "╗")
        output.append(f"║ HEX {coords}: {biome.title()} " + " " * (58 - len(f"HEX {coords}: {biome.title()} ")) + "║")
        output.append("╠" + "═" * 58 + "╣")
        output.append("║ EXPLORABLE LOCATIONS:" + " " * 36 + "║")
        
        for i, location in enumerate(locations, 1):
            location_desc = f"[{i}] {location.name}"
            if len(location_desc) > 56:
                location_desc = location_desc[:53] + "..."
            output.append(f"║ {location_desc:<56} ║")
        
        output.append("╚" + "═" * 58 + "╝")
        return "\n".join(output)

class ExplorationInterface:
    def __init__(self, world):
        self.world = world
        self.location_manager = LocationManager(world)

# Weather and travel systems
from weather_core import WeatherState, generate_weather_state
from travel_system import create_travel_methods, create_biome_weather_modifiers


@dataclass
class WorldGenerationConfig:
    """Configuration for world generation"""
    seed: int
    size: Tuple[int, int]  # (width, height)
    use_enhanced_biomes: bool = True
    generate_locations: bool = True
    enable_weather_system: bool = True
    enable_travel_system: bool = True


class WorldCoordinator:
    """
    Central coordinator for all world systems.
    
    This class manages the integration between:
    - Terrain generation
    - Climate simulation  
    - Biome classification
    - Location exploration systems
    - Weather systems
    - Travel mechanics
    
    It provides a clean API and prevents circular imports.
    """
    
    def __init__(self, config: WorldGenerationConfig):
        """Initialize the world coordinator with configuration."""
        self.config = config
        self.world: Optional[World] = None
        
        # Initialize core systems
        self.terrain_generator = TerrainGenerator(config.seed)
        self.climate_system = ClimateSystem(config.size[1])  # height for latitude calculations
        self.biome_classifier = BiomeClassifier(use_enhanced_biomes=config.use_enhanced_biomes)
        
        # Initialize location systems (will be set up after world generation)
        self.location_generator: Optional[LocationGenerator] = None
        self.location_manager: Optional[LocationManager] = None
        self.exploration_interface: Optional[ExplorationInterface] = None
        
        # Initialize optional systems
        self.travel_methods = create_travel_methods() if config.enable_travel_system else {}
        self.biome_weather_modifiers = create_biome_weather_modifiers() if config.enable_weather_system else {}
        
        print(f"WorldCoordinator initialized with seed {config.seed}")
        print(f"World size: {config.size[0]}x{config.size[1]} hexes")
        print(f"Enhanced biomes: {config.use_enhanced_biomes}")
        print(f"Locations: {config.generate_locations}")
    
    def generate_world(self) -> World:
        """
        Generate a complete world with all systems integrated.
        
        Returns:
            Generated World object with all systems initialized
        """
        print("\n" + "="*60)
        print("WORLD GENERATION - INTEGRATED SYSTEMS")
        print("="*60)
        
        # Step 1: Generate terrain
        print("\n1. Generating terrain...")
        heightmap = self.terrain_generator.generate_continental_heightmap(
            self.config.size[0], self.config.size[1]
        )
        
        # Step 2: Generate climate zones
        print("\n2. Generating climate zones...")
        climate_zones = self.climate_system.generate_climate_zones(
            self.config.size, heightmap
        )
        
        # Step 3: Generate precipitation patterns
        print("\n3. Calculating precipitation patterns...")
        precipitation_map = self._generate_precipitation_map(climate_zones, heightmap)
        
        # Step 4: Classify biomes using integrated biome system
        print("\n4. Classifying biomes...")
        biomes = self.biome_classifier.generate_biome_map(
            self.config.size, climate_zones, precipitation_map, heightmap
        )
        
        # Step 5: Create world object
        print("\n5. Creating world object...")
        self.world = World(
            seed=self.config.seed,
            size=self.config.size,
            heightmap=heightmap,
            climate_zones=climate_zones,
            biomes=biomes
        )
        
        # Step 6: Initialize location systems
        if self.config.generate_locations:
            print("\n6. Initializing location exploration systems...")
            self._initialize_location_systems()
        
        # Step 7: Generate initial weather if enabled
        if self.config.enable_weather_system:
            print("\n7. Initializing weather systems...")
            self._initialize_weather_systems()
        
        print(f"\n✅ World generation complete!")
        print(f"Generated {len(heightmap)} hexes with integrated systems")
        
        return self.world
    
    def _generate_precipitation_map(self, climate_zones: Dict[Tuple[int, int], Any], 
                                  heightmap: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], Dict]:
        """Generate precipitation patterns based on climate and elevation."""
        precipitation_map = {}
        
        for coords, climate_zone in climate_zones.items():
            elevation = heightmap[coords]
            
            # Base precipitation by climate zone
            base_precip_inches = {
                "arctic": 8.0,
                "subarctic": 15.0,
                "temperate": 35.0,
                "subtropical": 45.0,
                "tropical": 80.0
            }.get(climate_zone.zone_type, 25.0)
            
            # Orographic precipitation effect (mountains get more rain)
            elevation_multiplier = 1.0 + (elevation * 0.8)
            
            # Rain shadow effect (simplified)
            if elevation > 0.6:
                # Leeward side gets less precipitation
                rain_shadow_factor = 0.7
            else:
                rain_shadow_factor = 1.0
            
            annual_precip = base_precip_inches * elevation_multiplier * rain_shadow_factor
            
            precipitation_map[coords] = {
                "annual_precipitation": annual_precip,
                "seasonal_variation": 0.4,  # 40% variation between seasons
                "monthly_distribution": self._generate_monthly_precipitation(climate_zone.zone_type)
            }
        
        return precipitation_map
    
    def _generate_monthly_precipitation(self, climate_type: str) -> List[float]:
        """Generate monthly precipitation distribution based on climate type."""
        if climate_type == "tropical":
            # Wet season (May-Oct), dry season (Nov-Apr)
            return [0.5, 0.4, 0.6, 0.8, 1.5, 1.8, 1.9, 1.7, 1.4, 1.2, 0.7, 0.5]
        elif climate_type == "temperate":
            # More even distribution with spring/fall peaks
            return [0.8, 0.7, 1.1, 1.3, 1.2, 1.0, 0.9, 0.8, 1.0, 1.2, 1.0, 0.9]
        elif climate_type == "arctic":
            # Most precipitation as snow in winter
            return [1.2, 1.1, 0.9, 0.6, 0.4, 0.3, 0.3, 0.4, 0.6, 0.8, 1.0, 1.4]
        else:
            # Default even distribution
            return [1.0] * 12
    
    def _initialize_location_systems(self):
        """Initialize location exploration systems."""
        if not self.world:
            raise RuntimeError("World must be generated before initializing location systems")
        
        # Initialize location generator
        self.location_generator = LocationGenerator(seed=self.config.seed)
        
        # Initialize location manager
        self.location_manager = LocationManager(self.world)
        
        # Initialize exploration interface
        self.exploration_interface = ExplorationInterface(self.world)
        
        print("  ✓ Location generator initialized")
        print("  ✓ Location manager initialized") 
        print("  ✓ Exploration interface initialized")
    
    def _initialize_weather_systems(self):
        """Initialize weather systems for the world."""
        if not self.world:
            raise RuntimeError("World must be generated before initializing weather systems")
        
        # Generate initial weather for all hexes
        weather_map = {}
        for coords in self.world.heightmap.keys():
            climate_zone = self.world.climate_zones[coords]
            weather_state = generate_weather_state(
                base_temperature=climate_zone.base_temperature,
                season="summer",  # Default to summer
                climate_type=climate_zone.zone_type
            )
            weather_map[coords] = weather_state
        
        # Store weather map in world (extend World class if needed)
        if not hasattr(self.world, 'current_weather'):
            self.world.current_weather = weather_map
        
        print(f"  ✓ Weather initialized for {len(weather_map)} hexes")
    
    def get_hex_complete_data(self, coords: Tuple[int, int]) -> Dict[str, Any]:
        """
        Get complete data for a hex including all systems.
        
        This is the main API for getting hex information.
        """
        if not self.world:
            raise RuntimeError("World not generated yet")
        
        if not self.world.is_valid_coordinate(coords):
            raise ValueError(f"Invalid coordinates: {coords}")
        
        # Get base hex data
        hex_data = self.world.get_hex_data(coords)
        
        # Add biome information
        biome_name = hex_data['biome']
        biome_info = self.biome_classifier.get_biome_info(biome_name)
        
        # Add locations if available
        explorable_locations = []
        if self.location_manager:
            explorable_locations = self.location_manager.get_explorable_locations(coords)
        
        # Add weather if available
        current_weather = None
        if hasattr(self.world, 'current_weather'):
            current_weather = self.world.current_weather.get(coords)
        
        # Add travel information
        travel_info = {}
        if self.travel_methods and biome_name in self.biome_weather_modifiers:
            travel_info = {
                'biome_modifier': self.biome_weather_modifiers[biome_name],
                'available_methods': list(self.travel_methods.keys())
            }
        
        return {
            **hex_data,  # Base hex data (coords, elevation, climate, biome, etc.)
            'biome_details': biome_info,
            'explorable_locations': explorable_locations,
            'current_weather': current_weather,
            'travel_info': travel_info,
            'has_exploration': len(explorable_locations) > 0
        }
    
    def enter_hex_exploration(self, player, hex_coords: Tuple[int, int]) -> bool:
        """
        Enter location exploration for a hex.
        
        Args:
            player: Player object
            hex_coords: Hex coordinates to explore
            
        Returns:
            True if exploration interface is ready, False otherwise
        """
        if not self.exploration_interface:
            print("Location exploration not available (disabled in config)")
            return False
        
        # Set player's current hex
        player.current_hex = hex_coords
        
        # Display available locations
        display = self.exploration_interface.location_manager.display_hex_locations(hex_coords)
        print(display)
        
        return True
    
    def process_exploration_command(self, player, command: str) -> bool:
        """
        Process an exploration command through the integrated interface.
        
        Args:
            player: Player object
            command: Command string
            
        Returns:
            True if command was handled, False otherwise
        """
        if not self.exploration_interface:
            return False
        
        return self.exploration_interface.process_command(player, command)
    
    def get_biome_analysis(self) -> Dict[str, Any]:
        """Get analysis of biome distribution and properties."""
        if not self.world:
            raise RuntimeError("World not generated yet")
        
        # Get biome counts
        biome_counts = {}
        total_hexes = len(self.world.biomes)
        
        for biome_name in self.world.biomes.values():
            biome_counts[biome_name] = biome_counts.get(biome_name, 0) + 1
        
        # Get biome details
        biome_details = {}
        for biome_name in biome_counts.keys():
            biome_info = self.biome_classifier.get_biome_info(biome_name)
            if biome_info:
                biome_details[biome_name] = {
                    'display_name': getattr(biome_info, 'display_name', biome_name.replace('_', ' ').title()),
                    'description': getattr(biome_info, 'description', 'No description available'),
                    'count': biome_counts[biome_name],
                    'percentage': (biome_counts[biome_name] / total_hexes) * 100
                }
        
        return {
            'total_hexes': total_hexes,
            'biome_counts': biome_counts,
            'biome_details': biome_details,
            'diversity_index': len(biome_counts)  # Simple diversity measure
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all integrated systems."""
        return {
            'world_generated': self.world is not None,
            'world_size': self.config.size if self.world else None,
            'total_hexes': len(self.world.heightmap) if self.world else 0,
            'systems': {
                'terrain_generation': True,
                'climate_system': True,
                'biome_classification': True,
                'enhanced_biomes': self.config.use_enhanced_biomes,
                'location_generation': self.location_generator is not None,
                'location_manager': self.location_manager is not None,
                'exploration_interface': self.exploration_interface is not None,
                'weather_system': self.config.enable_weather_system,
                'travel_system': self.config.enable_travel_system
            },
            'biome_system': 'Enhanced (8 core biomes)' if self.config.use_enhanced_biomes else 'Whittaker (13 biomes)',
            'seed': self.config.seed
        }


def create_world_coordinator(seed: int, size: Tuple[int, int], **kwargs) -> WorldCoordinator:
    """
    Convenience function to create a WorldCoordinator with default configuration.
    
    Args:
        seed: Random seed for world generation
        size: World size as (width, height) tuple
        **kwargs: Additional configuration options
        
    Returns:
        Configured WorldCoordinator instance
    """
    config = WorldGenerationConfig(
        seed=seed,
        size=size,
        use_enhanced_biomes=kwargs.get('use_enhanced_biomes', True),
        generate_locations=kwargs.get('generate_locations', True),
        enable_weather_system=kwargs.get('enable_weather_system', True),
        enable_travel_system=kwargs.get('enable_travel_system', True)
    )
    
    return WorldCoordinator(config)


def test_world_coordinator():
    """Test the world coordinator system."""
    print("=== Testing World Coordinator ===")
    
    # Create coordinator
    coordinator = create_world_coordinator(
        seed=42,
        size=(15, 15),
        use_enhanced_biomes=True,
        generate_locations=True
    )
    
    # Generate world
    world = coordinator.generate_world()
    
    # Test system status
    print("\n" + "="*60)
    print("SYSTEM STATUS")
    print("="*60)
    status = coordinator.get_system_status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for subkey, subvalue in value.items():
                print(f"  {subkey}: {subvalue}")
        else:
            print(f"{key}: {value}")
    
    # Test hex data retrieval
    print("\n" + "="*60)
    print("HEX DATA EXAMPLE")
    print("="*60)
    test_coords = (7, 7)  # Center of 15x15 world
    hex_data = coordinator.get_hex_complete_data(test_coords)
    
    print(f"Hex {test_coords}:")
    print(f"  Biome: {hex_data['biome']}")
    print(f"  Elevation: {hex_data['elevation']:.3f}")
    print(f"  Climate: {hex_data['climate_type']}")
    print(f"  Explorable locations: {len(hex_data['explorable_locations'])}")
    print(f"  Has exploration: {hex_data['has_exploration']}")
    
    # Test biome analysis
    print("\n" + "="*60)
    print("BIOME ANALYSIS")
    print("="*60)
    biome_analysis = coordinator.get_biome_analysis()
    print(f"Total hexes: {biome_analysis['total_hexes']}")
    print(f"Biome diversity: {biome_analysis['diversity_index']} different biomes")
    
    print("\nBiome distribution:")
    for biome_name, details in biome_analysis['biome_details'].items():
        print(f"  {details['display_name']}: {details['count']} hexes ({details['percentage']:.1f}%)")
    
    print("\n✅ World Coordinator test complete!")
    print("All systems integrated successfully through central coordinator.")


if __name__ == "__main__":
    test_world_coordinator()