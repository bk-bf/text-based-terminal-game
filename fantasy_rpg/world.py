"""
Fantasy RPG - World Generation

World generation and hex management functionality.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any


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