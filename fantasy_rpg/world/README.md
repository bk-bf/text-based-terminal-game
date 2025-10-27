# Fantasy RPG - World System Architecture

This directory contains the complete world generation and management system, organized through a central coordinator pattern to provide clean integration and prevent circular imports.

## 🏗️ **Core Architecture**

### **Central Coordinator**
- **`world_coordinator.py`** - Main entry point and system integrator
- **`__init__.py`** - Clean API exports

### **Foundation Systems**
- **`terrain_generation.py`** - Continental plate tectonics and heightmap generation
- **`climate.py`** - Latitude-based climate zones and temperature systems
- **`biomes.py`** - Whittaker biome classification integration
- **`enhanced_biomes.py`** - 8 core gameplay-focused biomes with rich properties

### **Environmental Systems**
- **`weather_core.py`** - Weather state generation and management
- **`character_weather.py`** - Character weather resistance and archetypes
- **`travel_system.py`** - Travel methods and biome-specific modifiers

### **World Management**
- **`world.py`** - Core World and Hex data structures

## 🎯 **Usage Pattern**

### **Simple World Creation**
```python
from fantasy_rpg.world import create_world_coordinator

# Create coordinated world system
coordinator = create_world_coordinator(
    seed=12345,
    size=(20, 20),
    use_enhanced_biomes=True,
    generate_micro_locations=True
)

# Generate integrated world
world = coordinator.generate_world()
```

### **Hex Exploration**
```python
# Get complete hex data
hex_data = coordinator.get_hex_complete_data((10, 10))

# Enter micro-level exploration
coordinator.enter_hex_exploration(player, (10, 10))

# Process exploration commands
coordinator.process_exploration_command(player, "explore 1")
coordinator.process_exploration_command(player, "examine altar")
```

## 🌍 **System Integration**

```
Game Layer
    ↓
WorldCoordinator (Central Hub)
    ├── TerrainGenerator → Continental plates, heightmaps
    ├── ClimateSystem → Latitude-based climate zones
    ├── BiomeClassifier → Enhanced 8-biome system
    ├── LocationGenerator → Wilderness, ruins, settlements
    ├── MicroLevelManager → Area navigation and interaction
    ├── ExplorationInterface → Natural language commands
    ├── WeatherSystem → Dynamic weather generation
    └── TravelSystem → Biome-specific travel mechanics
```

## 📁 **File Organization**

### **Core Systems (Required)**
- `world_coordinator.py` - **Main coordinator**
- `terrain_generation.py` - Terrain generation
- `climate.py` - Climate systems
- `enhanced_biomes.py` - Biome definitions
- `world.py` - Data structures

### **Future Extensions**
- Location systems can be added as needed
- Combat systems can be integrated when required
- All extensions work through the WorldCoordinator

### **Environmental Systems (Optional)**
- `weather_core.py` - Weather generation
- `character_weather.py` - Weather resistance
- `travel_system.py` - Travel mechanics

## 🧹 **Cleaned Up Architecture**

**Cleaned up architecture:**
- ❌ Removed redundant test files and wrappers
- ❌ Removed problematic micro-level systems with circular imports
- ❌ Removed outdated example files

**Benefits of cleanup:**
- ✅ Single entry point through WorldCoordinator
- ✅ No circular imports or spaghetti code
- ✅ Clear separation of concerns
- ✅ Easy to extend and maintain
- ✅ Comprehensive testing in one place

## 🚀 **Getting Started**

1. **Import the coordinator:**
   ```python
   from fantasy_rpg.world import create_world_coordinator
   ```

2. **Create and generate world:**
   ```python
   coordinator = create_world_coordinator(seed=123, size=(15, 15))
   world = coordinator.generate_world()
   ```

3. **Explore hexes:**
   ```python
   hex_data = coordinator.get_hex_complete_data((7, 7))
   coordinator.enter_hex_exploration(player, (7, 7))
   ```

4. **Test the system:**
   ```bash
   cd fantasy_rpg/world && python world_coordinator.py
   ```

This architecture provides a clean, maintainable foundation for rich world generation and exploration in your text-based RPG.