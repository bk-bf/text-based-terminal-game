# World Generation Technical Reference

## System Architecture Overview

The world generation system follows a layered architecture where each system builds upon the previous ones:

```
┌─────────────────────────────────────────────────────────────┐
│                    Game Interface Layer                     │
│  (Player commands, travel assessment, environmental queries) │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   Integration Layer                         │
│        (world.py - orchestrates all systems)               │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                  Environmental Systems                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Weather   │ │   Biomes    │ │  Resources  │           │
│  │   System    │ │   System    │ │   System    │           │
│  │ (planned)   │ │ (planned)   │ │ (planned)   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Climate Layer                            │
│              (climate.py - temperature zones)               │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   Foundation Layer                          │
│        (terrain_generation.py - physical geography)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Data Structures

### Coordinate System
```python
# All systems use consistent (x, y) coordinate tuples
HexCoords = Tuple[int, int]  # (x, y) where (0,0) is northwest corner

# World dimensions
WorldSize = Tuple[int, int]  # (width, height) in hexes
```

### World Container
```python
@dataclass
class World:
    """Master container for all world generation data"""
    seed: int                                           # Reproducible generation
    size: Tuple[int, int]                              # (width, height) in hexes
    heightmap: Dict[HexCoords, float]                  # Elevation (0.0-1.0)
    climate_zones: Dict[HexCoords, ClimateZone]        # Climate data per hex
    biomes: Dict[HexCoords, str]                       # Biome type per hex
    landmarks: Dict[HexCoords, Dict[str, Any]]         # Special locations
    factions: List[Dict[str, Any]]                     # Political entities
```

### Climate Zone Structure
```python
@dataclass
class ClimateZone:
    """Complete climate data for a geographic region"""
    zone_type: str                          # "arctic", "temperate", etc.
    base_temperature: float                 # Average annual temp (°F)
    temp_range_summer: Tuple[float, float]  # (min, max) summer temps
    temp_range_winter: Tuple[float, float]  # (min, max) winter temps
    annual_precipitation: int               # Inches per year
    seasonal_variation: float               # 0.0-1.0 seasonal swing
    volatility: int                         # Weather unpredictability
    has_snow: bool                          # Snow in winter
```

---

## System APIs

### Terrain Generation API

#### Core Functions
```python
class TerrainGenerator:
    def __init__(self, seed: int)
    
    # Primary generation methods
    def generate_continental_heightmap(self, width: int, height: int) -> Dict[HexCoords, float]
    def generate_terrain_types(self, heightmap: Dict[HexCoords, float]) -> Dict[HexCoords, str]
    
    # Hydrology methods
    def calculate_drainage_patterns(self, heightmap: Dict[HexCoords, float], 
                                  width: int, height: int) -> Dict[HexCoords, HexCoords]
    def calculate_flow_accumulation(self, flow_directions: Dict[HexCoords, HexCoords], 
                                  width: int, height: int) -> Dict[HexCoords, int]
    def generate_river_systems(self, heightmap: Dict[HexCoords, float],
                             flow_directions: Dict[HexCoords, HexCoords],
                             flow_accumulation: Dict[HexCoords, int],
                             width: int, height: int) -> Dict[HexCoords, Dict]
    
    # Utility methods
    def classify_terrain_from_elevation(self, elevation: float) -> str
```

#### Terrain Classification
```python
# Elevation thresholds for terrain types
TERRAIN_THRESHOLDS = {
    0.0-0.2: "water",      # Ocean and deep lakes
    0.2-0.3: "coastal",    # Beaches and tidal zones  
    0.3-0.5: "plains",     # Flat lowlands
    0.5-0.7: "hills",      # Rolling hills
    0.7-0.85: "mountains", # Mountain slopes
    0.85-1.0: "peaks"      # High peaks and ridges
}
```

### Climate System API

#### Core Functions
```python
class ClimateSystem:
    def __init__(self, world_height: int, equator_position: float = 0.5)
    
    # Temperature calculation
    def calculate_latitude_factor(self, y: int) -> float
    def calculate_base_temperature(self, y: int) -> float
    def determine_climate_zone_type(self, base_temperature: float, elevation: float = 0.0) -> str
    
    # Climate zone generation
    def generate_climate_zone(self, coords: HexCoords, elevation: float = 0.0) -> ClimateZone
    def generate_climate_zones(self, world_size: WorldSize, 
                             heightmap: Dict[HexCoords, float]) -> Dict[HexCoords, ClimateZone]
    
    # Temperature queries
    def get_temperature_at_coords(self, coords: HexCoords, elevation: float = 0.0, 
                                season: str = "summer") -> float
```

#### Climate Zone Templates
```python
CLIMATE_TEMPLATES = {
    "arctic": {
        "base_temperature": 10.0,
        "temp_range_summer": (-10, 32),
        "temp_range_winter": (-40, -10),
        "annual_precipitation": 10,
        "seasonal_variation": 0.8,
        "volatility": 15,
        "has_snow": True
    },
    "temperate": {
        "base_temperature": 50.0,
        "temp_range_summer": (60, 80),
        "temp_range_winter": (20, 40),
        "annual_precipitation": 40,
        "seasonal_variation": 0.6,
        "volatility": 8,
        "has_snow": True
    },
    # ... additional climate types
}
```

### World Generation API

#### Main Generation Function
```python
def generate_world_with_terrain(seed: int, size: WorldSize) -> World:
    """
    Complete world generation pipeline:
    1. Generate terrain and hydrology
    2. Calculate climate zones
    3. Assign biomes (basic terrain mapping)
    4. Return complete World object
    """
```

#### World Query Methods
```python
class World:
    def get_hex_data(self, coords: HexCoords) -> Dict[str, Any]:
        """Get complete environmental data for a hex"""
        
    def is_valid_coordinate(self, coords: HexCoords) -> bool:
        """Check if coordinates are within world bounds"""
```

---

## Generation Algorithms

### Terrain Generation Process

#### 1. Continental Plate Simulation
```python
# Generate tectonic plates using Voronoi regions
def generate_continental_plates(width: int, height: int, num_plates: int = 6):
    # 1. Place random plate centers
    # 2. Assign each hex to nearest plate center
    # 3. Calculate plate boundaries (adjacent different plates)
    # 4. Assign plate types (oceanic vs continental)
```

#### 2. Elevation Generation
```python
# Multi-octave noise with tectonic influence
def generate_continental_heightmap(width: int, height: int):
    # 1. Generate base elevation per tectonic plate
    # 2. Add tectonic boundary effects (mountains/trenches)
    # 3. Apply regional terrain variation (multi-octave noise)
    # 4. Add local detail (high-frequency noise)
    # 5. Apply continental shelf effects (ocean depth gradients)
```

#### 3. Hydrology Calculation
```python
# Water flow simulation
def calculate_drainage_patterns(heightmap):
    # 1. For each hex, find lowest adjacent neighbor
    # 2. Create flow direction map (hex -> downstream hex)
    # 3. Calculate flow accumulation (upstream drainage area)
    # 4. Identify river systems (high flow accumulation)
    # 5. Place lakes in drainage sinks (local minima)
```

### Climate Generation Process

#### 1. Latitude-Based Temperature
```python
def calculate_base_temperature(y: int) -> float:
    # 1. Calculate distance from equator
    # 2. Apply cosine curve for realistic temperature gradient
    # 3. Scale from arctic (10°F) to tropical (85°F)
    
    latitude_factor = math.cos(distance_from_equator / max_distance * π/2)
    return 10.0 + (85.0 - 10.0) * latitude_factor
```

#### 2. Elevation Effects (Lapse Rate)
```python
def apply_elevation_cooling(base_temp: float, elevation: float) -> float:
    # Standard atmospheric lapse rate: ~3.5°F per 1000 feet
    # Elevation factor (0.0-1.0) represents relative height
    elevation_cooling = elevation * 30.0  # Up to 30°F cooling
    return base_temp - elevation_cooling
```

#### 3. Climate Zone Assignment
```python
def determine_climate_zone_type(adjusted_temperature: float) -> str:
    if adjusted_temperature < 20:   return "arctic"
    elif adjusted_temperature < 35: return "subarctic"  
    elif adjusted_temperature < 55: return "temperate"
    elif adjusted_temperature < 70: return "subtropical"
    else:                          return "tropical"
```

---

## Performance Considerations

### Memory Usage
```python
# Typical memory footprint for 100x100 world:
heightmap:      10,000 floats    = ~40 KB
climate_zones:  10,000 objects   = ~800 KB  
terrain_types:  10,000 strings   = ~200 KB
rivers:         ~500 objects     = ~50 KB
lakes:          ~50 objects      = ~10 KB
# Total: ~1.1 MB for complete world data
```

### Generation Performance
```python
# Typical generation times on modern hardware:
terrain_generation:    20x20 world = ~1 second
                      100x100 world = ~30 seconds
climate_generation:    20x20 world = ~0.1 seconds  
                      100x100 world = ~2 seconds
total_world_gen:      100x100 world = ~35 seconds
```

### Optimization Strategies
- **Lazy Loading**: Generate detailed data only when accessed
- **Spatial Indexing**: Use quadtrees for efficient spatial queries
- **Caching**: Store frequently accessed calculations
- **Vectorization**: Use NumPy for bulk mathematical operations
- **Parallel Processing**: Generate independent regions simultaneously

---

## Testing and Validation

### Terrain Validation
```python
def validate_terrain_generation():
    # Check elevation distribution (should follow natural patterns)
    # Verify river networks flow downhill
    # Ensure lakes appear in natural depressions
    # Validate continental shelf gradients
```

### Climate Validation  
```python
def validate_climate_generation():
    # Verify temperature gradients (coldest at poles)
    # Check elevation cooling effects
    # Ensure climate zones match temperature ranges
    # Validate seasonal temperature variations
```

### Integration Testing
```python
def test_world_generation_integration():
    # Generate complete world and verify all systems work together
    # Check that biomes match climate + terrain combinations
    # Ensure world data is internally consistent
    # Validate performance within acceptable limits
```

---

## Extension Points

### Adding New Climate Types
```python
# Add new climate template to ClimateSystem
new_climate = ClimateZone(
    zone_type="mediterranean",
    base_temperature=60.0,
    temp_range_summer=(70, 85),
    temp_range_winter=(45, 60),
    annual_precipitation=25,
    seasonal_variation=0.4,
    volatility=7,
    has_snow=False
)
```

### Custom Terrain Types
```python
# Extend terrain classification in TerrainGenerator
def classify_terrain_from_elevation(self, elevation: float) -> str:
    # Add new elevation thresholds and terrain types
    if elevation < 0.1:  return "deep_ocean"
    elif elevation < 0.15: return "shallow_sea"
    # ... existing classifications
    elif elevation > 0.95: return "extreme_peaks"
```

### Biome System Integration
```python
# Future biome system will use this interface:
def determine_biome(climate_zone: ClimateZone, terrain_type: str, 
                   water_availability: float) -> str:
    # Combine climate + terrain + hydrology to assign realistic biomes
    pass
```

This technical reference provides the foundation for understanding and extending the world generation system. Each component is designed to be modular and extensible, allowing for easy addition of new features while maintaining system coherence and performance.