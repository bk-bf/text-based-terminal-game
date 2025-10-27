"""
Fantasy RPG - World Generation

World generation and hex management functionality.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
try:
    from .terrain_generation import TerrainGenerator
    from .climate import ClimateSystem, ClimateZone
except ImportError:
    from terrain_generation import TerrainGenerator
    from climate import ClimateSystem, ClimateZone


@dataclass
class Hex:
    """
    Hex dataclass representing a single hex tile in the world.
    
    Each hex contains coordinates, biome information, elevation,
    and optional location/features for detailed world generation.
    Now supports micro-level locations for detailed exploration.
    """
    coords: Tuple[int, int]  # (x, y) coordinates in the world grid
    biome: str  # Biome type (e.g., 'forest', 'plains', 'mountains')
    elevation: float = 0.0  # Elevation in arbitrary units
    location: Optional[Dict[str, Any]] = None  # Special location (town, dungeon, etc.)
    features: Optional[List[str]] = None  # Natural features (river, cave, etc.)
    
    # Location exploration support
    locations: Optional[List[Any]] = None  # List of Location objects for detailed exploration
    has_been_explored: bool = False  # Track if player has explored locations
    
    def __post_init__(self):
        """Initialize empty features list if not provided."""
        if self.features is None:
            self.features = []
        if self.locations is None:
            self.locations = []
    
    def has_location(self) -> bool:
        """Check if this hex has a special location."""
        return self.location is not None or len(self.locations) > 0
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if this hex has a specific feature."""
        return feature_name in (self.features or [])
    
    def add_feature(self, feature_name: str):
        """Add a feature to this hex."""
        if self.features is None:
            self.features = []
        if feature_name not in self.features:
            self.features.append(feature_name)
    
    def add_location(self, location):
        """Add a location to this hex."""
        if self.locations is None:
            self.locations = []
        self.locations.append(location)
    
    def get_explorable_locations(self) -> List[Any]:
        """Get all locations that can be explored in this hex."""
        return self.locations or []
    
    def get_description(self) -> str:
        """Get a basic description of this hex."""
        desc = f"{self.biome.title()} hex at {self.coords}"
        if self.location:
            desc += f" with {self.location.get('name', 'special location')}"
        if self.locations:
            desc += f" ({len(self.locations)} explorable locations)"
        if self.features:
            desc += f" (features: {', '.join(self.features)})"
        return desc


@dataclass
class World:
    """
    World dataclass containing all world generation data.
    
    This class holds the complete world state including heightmap,
    climate zones, biomes, landmarks, and factions.
    """
    seed: int
    size: Tuple[int, int]  # (width, height) in hexes
    heightmap: Optional[Dict[Tuple[int, int], float]] = None
    climate_zones: Optional[Dict[Tuple[int, int], ClimateZone]] = None
    biomes: Optional[Dict[Tuple[int, int], str]] = None
    landmarks: Optional[Dict[Tuple[int, int], Dict[str, Any]]] = None
    factions: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        """Initialize empty data structures if not provided."""
        if self.heightmap is None:
            self.heightmap = {}
        if self.climate_zones is None:
            self.climate_zones = {}
        if self.biomes is None:
            self.biomes = {}
        if self.landmarks is None:
            self.landmarks = {}
        if self.factions is None:
            self.factions = []
    
    def get_hex_data(self, coords: Tuple[int, int]) -> Dict[str, Any]:
        """Get all data for a specific hex coordinate."""
        x, y = coords
        climate_zone = self.climate_zones.get(coords)
        return {
            'coords': coords,
            'elevation': self.heightmap.get(coords, 0.0),
            'climate_zone': climate_zone,
            'climate_type': climate_zone.zone_type if climate_zone else 'temperate',
            'base_temperature': climate_zone.base_temperature if climate_zone else 50.0,
            'biome': self.biomes.get(coords, 'plains'),
            'landmark': self.landmarks.get(coords, None)
        }
    
    def is_valid_coordinate(self, coords: Tuple[int, int]) -> bool:
        """Check if coordinates are within world bounds."""
        x, y = coords
        width, height = self.size
        return 0 <= x < width and 0 <= y < height


def generate_world_with_terrain(seed: int, size: Tuple[int, int]) -> World:
    """
    Generate a complete world with realistic terrain using multi-octave noise.
    
    Args:
        seed: Random seed for reproducible generation
        size: World dimensions (width, height) in hexes
    
    Returns:
        World object with generated heightmap, climate zones, biomes, and terrain data
    """
    print(f"Generating world with seed {seed}, size {size}")
    
    # Initialize terrain generator
    terrain_gen = TerrainGenerator(seed)
    width, height = size
    
    # Generate continental heightmap for realistic landmasses
    print("Generating terrain...")
    heightmap = terrain_gen.generate_continental_heightmap(width, height)
    
    # Generate climate zones based on latitude and elevation
    print("Generating climate zones...")
    climate_system = ClimateSystem(height)
    climate_zones = climate_system.generate_climate_zones(size, heightmap)
    
    # Use existing biome system for realistic biome assignment
    print("Generating biomes using enhanced biome system...")
    try:
        from .biomes import BiomeClassifier
    except ImportError:
        from biomes import BiomeClassifier
    
    # Initialize biome classifier with enhanced biomes
    biome_classifier = BiomeClassifier(use_enhanced_biomes=True)
    
    # Generate precipitation map (simplified for now)
    precipitation_map = {}
    for coords in heightmap.keys():
        climate_zone = climate_zones[coords]
        # Estimate precipitation based on climate zone and elevation
        base_precip = 30.0  # inches per year
        if climate_zone.zone_type == "tropical":
            base_precip = 60.0
        elif climate_zone.zone_type == "arctic":
            base_precip = 10.0
        elif climate_zone.zone_type == "temperate":
            base_precip = 40.0
        
        # Modify by elevation (orographic precipitation)
        elevation_factor = heightmap[coords]
        precip_modifier = 1.0 + (elevation_factor * 0.5)
        annual_precip = base_precip * precip_modifier
        
        precipitation_map[coords] = {
            "annual_precipitation": annual_precip,
            "seasonal_variation": 0.3
        }
    
    # Generate biome map using the enhanced biome system
    biomes = biome_classifier.generate_biome_map(
        size, climate_zones, precipitation_map, heightmap
    )
    
    # Create world with generated data
    world = World(
        seed=seed,
        size=size,
        heightmap=heightmap,
        climate_zones=climate_zones,
        biomes=biomes
    )
    
    print(f"World generation complete: {len(heightmap)} hexes generated")
    return world


def test_world_generation():
    """Test the integrated world generation system."""
    print("=== Testing World Generation Integration ===")
    
    # Generate a small test world
    world = generate_world_with_terrain(seed=54321, size=(20, 20))
    
    print(f"\nWorld details:")
    print(f"  Seed: {world.seed}")
    print(f"  Size: {world.size}")
    print(f"  Hexes: {len(world.heightmap)}")
    
    # Show elevation statistics
    elevations = list(world.heightmap.values())
    print(f"\nElevation statistics:")
    print(f"  Min: {min(elevations):.3f}")
    print(f"  Max: {max(elevations):.3f}")
    print(f"  Avg: {sum(elevations)/len(elevations):.3f}")
    
    # Show climate zone distribution
    climate_counts = {}
    for climate_zone in world.climate_zones.values():
        zone_type = climate_zone.zone_type
        climate_counts[zone_type] = climate_counts.get(zone_type, 0) + 1
    
    print(f"\nClimate zone distribution:")
    for zone_type, count in sorted(climate_counts.items()):
        percentage = (count / len(world.climate_zones)) * 100
        print(f"  {zone_type}: {count} hexes ({percentage:.1f}%)")
    
    # Show biome distribution
    biome_counts = {}
    for biome in world.biomes.values():
        biome_counts[biome] = biome_counts.get(biome, 0) + 1
    
    print(f"\nBiome distribution:")
    for biome, count in sorted(biome_counts.items()):
        percentage = (count / len(world.biomes)) * 100
        print(f"  {biome}: {count} hexes ({percentage:.1f}%)")
    
    # Test specific hex data retrieval
    print(f"\nSample hex data:")
    test_coords = [(0, 0), (10, 10), (19, 19)]
    for coords in test_coords:
        if world.is_valid_coordinate(coords):
            hex_data = world.get_hex_data(coords)
            temp_c = (hex_data['base_temperature'] - 32) * 5/9
            print(f"  {coords}: elevation={hex_data['elevation']:.3f}, "
                  f"climate={hex_data['climate_type']}, "
                  f"temp={hex_data['base_temperature']:.0f}°F ({temp_c:.0f}°C), "
                  f"biome={hex_data['biome']}")
    
    # Test temperature variation across latitudes
    print(f"\nTemperature gradient test (center column):")
    width, height = world.size
    center_x = width // 2
    for y in [0, height//4, height//2, 3*height//4, height-1]:
        coords = (center_x, y)
        if world.is_valid_coordinate(coords):
            hex_data = world.get_hex_data(coords)
            climate_zone = hex_data['climate_zone']
            summer_temp = sum(climate_zone.temp_range_summer) / 2
            winter_temp = sum(climate_zone.temp_range_winter) / 2
            summer_temp_c = (summer_temp - 32) * 5/9
            winter_temp_c = (winter_temp - 32) * 5/9
            print(f"  Y={y:2d}: {hex_data['climate_type']:>10s} - "
                  f"Summer: {summer_temp:3.0f}°F ({summer_temp_c:3.0f}°C), "
                  f"Winter: {winter_temp:3.0f}°F ({winter_temp_c:3.0f}°C)")
    
    print("\nWorld generation integration test complete!")
    return world


if __name__ == "__main__":
    test_world_generation()