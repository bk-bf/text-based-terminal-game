"""
Fantasy RPG - World Generation

World generation and hex management functionality.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
try:
    from .terrain_generation import TerrainGenerator
except ImportError:
    from terrain_generation import TerrainGenerator


@dataclass
class Hex:
    """
    Hex dataclass representing a single hex tile in the world.
    
    Each hex contains coordinates, biome information, elevation,
    and optional location/features for detailed world generation.
    """
    coords: Tuple[int, int]  # (x, y) coordinates in the world grid
    biome: str  # Biome type (e.g., 'forest', 'plains', 'mountains')
    elevation: float = 0.0  # Elevation in arbitrary units
    location: Optional[Dict[str, Any]] = None  # Special location (town, dungeon, etc.)
    features: Optional[List[str]] = None  # Natural features (river, cave, etc.)
    
    def __post_init__(self):
        """Initialize empty features list if not provided."""
        if self.features is None:
            self.features = []
    
    def has_location(self) -> bool:
        """Check if this hex has a special location."""
        return self.location is not None
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if this hex has a specific feature."""
        return feature_name in (self.features or [])
    
    def add_feature(self, feature_name: str):
        """Add a feature to this hex."""
        if self.features is None:
            self.features = []
        if feature_name not in self.features:
            self.features.append(feature_name)
    
    def get_description(self) -> str:
        """Get a basic description of this hex."""
        desc = f"{self.biome.title()} hex at {self.coords}"
        if self.location:
            desc += f" with {self.location.get('name', 'special location')}"
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
    climate: Optional[Dict[Tuple[int, int], str]] = None
    biomes: Optional[Dict[Tuple[int, int], str]] = None
    landmarks: Optional[Dict[Tuple[int, int], Dict[str, Any]]] = None
    factions: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        """Initialize empty data structures if not provided."""
        if self.heightmap is None:
            self.heightmap = {}
        if self.climate is None:
            self.climate = {}
        if self.biomes is None:
            self.biomes = {}
        if self.landmarks is None:
            self.landmarks = {}
        if self.factions is None:
            self.factions = []
    
    def get_hex_data(self, coords: Tuple[int, int]) -> Dict[str, Any]:
        """Get all data for a specific hex coordinate."""
        x, y = coords
        return {
            'coords': coords,
            'elevation': self.heightmap.get(coords, 0.0),
            'climate': self.climate.get(coords, 'temperate'),
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
        World object with generated heightmap, biomes, and terrain data
    """
    print(f"Generating world with seed {seed}, size {size}")
    
    # Initialize terrain generator
    terrain_gen = TerrainGenerator(seed)
    width, height = size
    
    # Generate continental heightmap for realistic landmasses
    heightmap = terrain_gen.generate_continental_heightmap(width, height)
    
    # Generate terrain types from elevation
    terrain_types = terrain_gen.generate_terrain_types(heightmap)
    
    # Convert terrain types to biomes (simple mapping for now)
    biomes = {}
    for coords, terrain_type in terrain_types.items():
        if terrain_type == "water":
            biomes[coords] = "ocean"
        elif terrain_type == "coastal":
            biomes[coords] = "coastal"
        elif terrain_type == "plains":
            biomes[coords] = "grassland"
        elif terrain_type == "hills":
            biomes[coords] = "forest"
        elif terrain_type == "mountains":
            biomes[coords] = "mountains"
        elif terrain_type == "peaks":
            biomes[coords] = "alpine"
        else:
            biomes[coords] = "plains"  # fallback
    
    # Create world with generated data
    world = World(
        seed=seed,
        size=size,
        heightmap=heightmap,
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
            print(f"  {coords}: elevation={hex_data['elevation']:.3f}, "
                  f"biome={hex_data['biome']}")
    
    print("\nWorld generation integration test complete!")
    return world


if __name__ == "__main__":
    test_world_generation()