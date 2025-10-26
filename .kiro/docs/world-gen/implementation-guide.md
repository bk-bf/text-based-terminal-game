# World Generation Implementation Guide

## Quick Start

### Basic World Generation
```python
from fantasy_rpg.world.world import generate_world_with_terrain

# Generate a 20x20 world with seed for reproducibility
world = generate_world_with_terrain(seed=12345, size=(20, 20))

# Access world data
print(f"World size: {world.size}")
print(f"Generated {len(world.heightmap)} hexes")
```

### Examining World Data
```python
# Get complete data for a specific hex
coords = (10, 10)
hex_data = world.get_hex_data(coords)

print(f"Elevation: {hex_data['elevation']:.3f}")
print(f"Climate: {hex_data['climate_type']}")
print(f"Temperature: {hex_data['base_temperature']:.0f}°F")
print(f"Biome: {hex_data['biome']}")
```

### Climate System Usage
```python
from fantasy_rpg.world.climate import ClimateSystem

# Create climate system for world
climate_system = ClimateSystem(world_height=20)

# Get temperature for specific location and season
coords = (5, 15)
elevation = world.heightmap[coords]
summer_temp = climate_system.get_temperature_at_coords(coords, elevation, "summer")
winter_temp = climate_system.get_temperature_at_coords(coords, elevation, "winter")

print(f"Summer: {summer_temp:.0f}°F, Winter: {winter_temp:.0f}°F")
```

---

## Common Use Cases

### 1. Travel Assessment System
```python
def assess_travel_conditions(world: World, from_coords: HexCoords, to_coords: HexCoords):
    """Evaluate environmental challenges for travel between hexes"""
    
    # Get terrain data
    from_hex = world.get_hex_data(from_coords)
    to_hex = world.get_hex_data(to_coords)
    
    # Calculate travel difficulty
    elevation_change = abs(to_hex['elevation'] - from_hex['elevation'])
    terrain_difficulty = get_terrain_difficulty(to_hex['biome'])
    
    # Climate considerations
    climate_zone = to_hex['climate_zone']
    seasonal_temp = climate_zone.get_seasonal_temp("winter")  # Current season
    
    # Generate travel assessment
    assessment = {
        'base_travel_time': 30,  # minutes
        'terrain_modifier': terrain_difficulty,
        'elevation_challenge': elevation_change > 0.2,
        'temperature_risk': seasonal_temp[0] < 32,  # Freezing risk
        'recommended_gear': get_recommended_gear(climate_zone, to_hex['biome'])
    }
    
    return assessment

def get_terrain_difficulty(biome: str) -> float:
    """Get travel speed modifier for different biomes"""
    difficulty_map = {
        'ocean': 0.0,      # Impassable without boat
        'mountains': 0.3,   # Very slow
        'forest': 0.7,     # Moderate
        'grassland': 1.0,  # Normal speed
        'coastal': 0.9     # Slightly slower
    }
    return difficulty_map.get(biome, 0.8)
```

### 2. Resource Availability System
```python
def check_resource_availability(world: World, coords: HexCoords, season: str):
    """Determine what resources are available at a location"""
    
    hex_data = world.get_hex_data(coords)
    climate_zone = hex_data['climate_zone']
    biome = hex_data['biome']
    elevation = hex_data['elevation']
    
    resources = {
        'water_sources': [],
        'food_sources': [],
        'shelter_options': [],
        'materials': []
    }
    
    # Water availability based on biome and season
    if biome in ['forest', 'grassland']:
        resources['water_sources'].append('streams')
    if elevation > 0.7 and season == 'spring':
        resources['water_sources'].append('snowmelt')
    
    # Food sources based on biome and climate
    if biome == 'forest' and climate_zone.zone_type in ['temperate', 'subtropical']:
        resources['food_sources'].extend(['berries', 'nuts', 'game'])
    if biome == 'grassland':
        resources['food_sources'].extend(['roots', 'small_game'])
    
    # Shelter based on terrain
    if biome == 'mountains':
        resources['shelter_options'].extend(['caves', 'rock_overhangs'])
    if biome == 'forest':
        resources['shelter_options'].extend(['dense_trees', 'fallen_logs'])
    
    # Materials based on biome
    if biome == 'forest':
        resources['materials'].extend(['wood', 'bark', 'plant_fiber'])
    if biome == 'mountains':
        resources['materials'].extend(['stone', 'minerals'])
    
    return resources
```

### 3. Weather Prediction Interface
```python
def attempt_weather_prediction(player_survival_skill: int, coords: HexCoords, 
                             climate_zone: ClimateZone) -> dict:
    """Player attempts to predict weather based on survival skill"""
    
    # Base difficulty depends on climate volatility
    base_dc = 10 + climate_zone.volatility
    
    # Roll survival check (simulate with random for now)
    import random
    roll = random.randint(1, 20) + player_survival_skill
    
    if roll >= base_dc + 10:
        # Excellent prediction
        return {
            'success': True,
            'accuracy': 'excellent',
            'forecast_days': 7,
            'confidence': 90,
            'description': "You read the signs clearly - the weather patterns are obvious."
        }
    elif roll >= base_dc + 5:
        # Good prediction  
        return {
            'success': True,
            'accuracy': 'good',
            'forecast_days': 3,
            'confidence': 70,
            'description': "You can predict the next few days with reasonable confidence."
        }
    elif roll >= base_dc:
        # Basic prediction
        return {
            'success': True,
            'accuracy': 'basic', 
            'forecast_days': 1,
            'confidence': 50,
            'description': "You can make a rough guess about tomorrow's weather."
        }
    else:
        # Failed prediction
        return {
            'success': False,
            'accuracy': 'failed',
            'forecast_days': 0,
            'confidence': 20,
            'description': "The signs are unclear - you're not sure what to expect."
        }
```

---

## Testing Your Implementation

### 1. Basic Functionality Test
```python
def test_basic_world_generation():
    """Verify world generation works correctly"""
    
    # Generate test world
    world = generate_world_with_terrain(seed=12345, size=(10, 10))
    
    # Verify world structure
    assert len(world.heightmap) == 100  # 10x10 = 100 hexes
    assert len(world.climate_zones) == 100
    assert len(world.biomes) == 100
    
    # Check data consistency
    for coords in world.heightmap.keys():
        assert coords in world.climate_zones
        assert coords in world.biomes
        assert world.is_valid_coordinate(coords)
    
    print("✓ Basic world generation test passed")
```

### 2. Climate System Test
```python
def test_climate_gradients():
    """Verify temperature gradients work correctly"""
    
    world = generate_world_with_terrain(seed=12345, size=(10, 20))
    
    # Check temperature gradient from north to south
    center_x = 5
    temperatures = []
    
    for y in range(20):
        coords = (center_x, y)
        hex_data = world.get_hex_data(coords)
        temperatures.append(hex_data['base_temperature'])
    
    # Verify temperature increases toward equator (middle of world)
    equator_y = 10
    north_temp = temperatures[0]    # Northernmost
    equator_temp = temperatures[equator_y]  # Equator
    south_temp = temperatures[19]   # Southernmost
    
    assert equator_temp > north_temp, "Equator should be warmer than north pole"
    assert equator_temp > south_temp, "Equator should be warmer than south pole"
    
    print("✓ Climate gradient test passed")
    print(f"  North: {north_temp:.0f}°F, Equator: {equator_temp:.0f}°F, South: {south_temp:.0f}°F")
```

### 3. Integration Test
```python
def test_world_integration():
    """Test that all systems work together"""
    
    world = generate_world_with_terrain(seed=54321, size=(15, 15))
    
    # Test various coordinates
    test_coords = [(0, 0), (7, 7), (14, 14)]
    
    for coords in test_coords:
        # Get all data for this hex
        hex_data = world.get_hex_data(coords)
        
        # Verify all required data is present
        required_fields = ['elevation', 'climate_zone', 'climate_type', 
                          'base_temperature', 'biome']
        
        for field in required_fields:
            assert field in hex_data, f"Missing field {field} at {coords}"
        
        # Verify data makes sense
        assert 0.0 <= hex_data['elevation'] <= 1.0
        assert -50 <= hex_data['base_temperature'] <= 120  # Reasonable temp range
        assert hex_data['climate_zone'] is not None
        
        print(f"✓ Hex {coords}: {hex_data['climate_type']}, "
              f"{hex_data['base_temperature']:.0f}°F, {hex_data['biome']}")
    
    print("✓ Integration test passed")
```

---

## Performance Tips

### 1. Efficient World Queries
```python
# Good: Query world data once and reuse
hex_data = world.get_hex_data(coords)
elevation = hex_data['elevation']
climate = hex_data['climate_zone']
temperature = hex_data['base_temperature']

# Avoid: Multiple queries for same hex
elevation = world.heightmap[coords]  # Separate query
climate = world.climate_zones[coords]  # Another query
# ... more queries
```

### 2. Batch Processing
```python
# Good: Process multiple hexes at once
def analyze_region(world: World, region_coords: List[HexCoords]):
    """Analyze multiple hexes efficiently"""
    
    region_data = []
    for coords in region_coords:
        hex_data = world.get_hex_data(coords)
        region_data.append(hex_data)
    
    # Process all data together
    return analyze_hex_batch(region_data)

# Avoid: Processing hexes one at a time in separate function calls
```

### 3. Caching Expensive Calculations
```python
class WorldAnalyzer:
    def __init__(self, world: World):
        self.world = world
        self._travel_cache = {}  # Cache travel calculations
    
    def get_travel_time(self, from_coords: HexCoords, to_coords: HexCoords):
        """Get travel time with caching"""
        
        cache_key = (from_coords, to_coords)
        if cache_key in self._travel_cache:
            return self._travel_cache[cache_key]
        
        # Calculate travel time
        travel_time = self._calculate_travel_time(from_coords, to_coords)
        
        # Cache result
        self._travel_cache[cache_key] = travel_time
        return travel_time
```

---

## Common Pitfalls

### 1. Coordinate System Confusion
```python
# Remember: (x, y) where (0, 0) is northwest corner
# x increases eastward, y increases southward

# Good
coords = (x, y)
width, height = world.size

# Check bounds correctly
if 0 <= x < width and 0 <= y < height:
    # Valid coordinate

# Avoid: Mixing up x/y or width/height
```

### 2. Climate Zone Data Access
```python
# Good: Check if climate zone exists
climate_zone = world.climate_zones.get(coords)
if climate_zone:
    temperature = climate_zone.base_temperature

# Avoid: Direct access without checking
temperature = world.climate_zones[coords].base_temperature  # May crash
```

### 3. Elevation Scaling
```python
# Remember: Elevation is normalized 0.0-1.0
elevation = world.heightmap[coords]  # 0.0-1.0

# Convert to actual height if needed
actual_height_feet = elevation * 10000  # Scale to 0-10,000 feet

# Use elevation factor for climate calculations
climate_zone = climate_system.generate_climate_zone(coords, elevation)
```

---

## Next Steps

### Extending the System

1. **Add Weather System**: Implement dynamic weather that changes over time
2. **Enhance Biomes**: Create detailed biome system with resources and hazards  
3. **Add Seasons**: Implement seasonal changes that affect world state
4. **Resource Systems**: Add detailed resource availability and depletion
5. **Travel Mechanics**: Implement complete travel system with survival challenges

### Integration Points

- **Combat System**: Environmental effects on combat (weather, terrain)
- **Settlement System**: Towns and cities based on environmental factors
- **Quest System**: Quests that involve environmental challenges
- **Character System**: Survival skills and environmental adaptation

This implementation guide provides the foundation for building rich environmental gameplay on top of the world generation system. Start with basic world generation and gradually add more complex environmental interactions as your game develops.