# Coordinate Representation Guide

This document explains the three coordinate/direction representations used throughout the Fantasy RPG codebase and when to use each one.

---

## 📍 Three Representations

### 1. HexCoords - `Tuple[int, int]`

**Type Alias:** `HexCoords = Tuple[int, int]`

**Purpose:** Lightweight world grid position tracking

**When to Use:**
- Storing hex positions in world map
- Dictionary keys for hex lookups
- Passing coordinates between systems
- Movement calculations requiring minimal overhead

**Advantages:**
- ✅ Hashable (can be used as dict keys)
- ✅ Lightweight (minimal memory overhead)
- ✅ Fast comparisons and lookups
- ✅ Immutable (safe to share across systems)

**Examples:**
```python
# World map storage
world.hexes: Dict[HexCoords, Hex] = {
    (5, 10): Hex(coords=(5, 10), biome="forest"),
    (6, 10): Hex(coords=(6, 10), biome="plains")
}

# Movement calculations
current_position: HexCoords = (12, 8)
target_position: HexCoords = (13, 9)

# Hex class usage
hex = Hex(coords=(5, 10), biome="forest", elevation=50.0)
```

**Files Using HexCoords:**
- `fantasy_rpg/world/world.py` - `Hex.coords`
- `fantasy_rpg/game/movement_coordinator.py` - `_calculate_target_coords()`
- `fantasy_rpg/game/game_engine.py` - `WorldPosition.coords`

---

### 2. Coordinates - Dataclass

**Type:** `@dataclass class Coordinates`

**Purpose:** Rich coordinate operations with built-in methods

**When to Use:**
- Distance calculations
- Coordinate transformations
- Pathfinding algorithms
- Spatial queries requiring validation

**Advantages:**
- ✅ Type safety (enforced int types)
- ✅ Built-in validation (`__post_init__`)
- ✅ Extensible with methods (`distance_to()`, etc.)
- ✅ Clear field names (`.x`, `.y`)

**Examples:**
```python
# Distance calculations
pos1 = Coordinates(x=5, y=10)
pos2 = Coordinates(x=8, y=12)
distance = pos1.distance_to(pos2)  # Returns: 3

# Converting to HexCoords
coords = Coordinates(x=5, y=10)
hex_coords: HexCoords = coords.to_tuple()  # (5, 10)

# Type safety
coords = Coordinates(x="5", y="10")  # Auto-converts to int in __post_init__
```

**Files Using Coordinates:**
- `fantasy_rpg/utils/utils.py` - Class definition
- Pathfinding algorithms (when implemented)
- Spatial analysis utilities

**When to Convert:**
```python
# HexCoords → Coordinates (when you need rich operations)
hex_coords: HexCoords = (5, 10)
coords = Coordinates(x=hex_coords[0], y=hex_coords[1])

# Coordinates → HexCoords (when storing in world map)
coords = Coordinates(x=5, y=10)
hex_coords: HexCoords = coords.to_tuple()
world.hexes[hex_coords] = Hex(coords=hex_coords, biome="forest")
```

---

### 3. Direction - String Literal

**Type Alias:** 
```python
Direction = Literal[
    "north", "n", "south", "s", "east", "e", "west", "w",
    "northeast", "ne", "northwest", "nw", "southeast", "se", "southwest", "sw"
]
```

**Purpose:** Human-readable movement and navigation

**When to Use:**
- User input commands
- Area exit mapping
- Location navigation
- Movement direction specification

**Advantages:**
- ✅ Human-readable
- ✅ Compact in JSON templates
- ✅ Natural for cardinal/ordinal directions
- ✅ Easy to validate with Literal type

**Examples:**
```python
# Area exit mapping (locations.json)
{
    "forest_clearing": {
        "exits": {
            "n": "dense_forest",
            "e": "cave_entrance", 
            "sw": "river_bank"
        }
    }
}

# Movement commands
direction: Direction = "north"
success, message = movement.move_player(direction)

# Direction mapping in handlers
direction_map = {
    'north': 'north', 'n': 'north',
    'south': 'south', 's': 'south',
    # ...
}
```

**Files Using Direction:**
- `fantasy_rpg/locations/location_generator.py` - `Area.exits`
- `fantasy_rpg/actions/movement_handler.py` - `handle_move()`
- `fantasy_rpg/game/movement_coordinator.py` - `move_player()`
- `fantasy_rpg/game/location_coordinator.py` - `move_between_locations()`

**Valid Direction Strings:**
- Cardinal: `"north"`, `"n"`, `"south"`, `"s"`, `"east"`, `"e"`, `"west"`, `"w"`
- Ordinal: `"northeast"`, `"ne"`, `"northwest"`, `"nw"`, `"southeast"`, `"se"`, `"southwest"`, `"sw"`

---

## 🔄 Conversion Patterns

### HexCoords ↔ Coordinates

```python
# HexCoords → Coordinates
hex_coords: HexCoords = (5, 10)
coords = Coordinates(x=hex_coords[0], y=hex_coords[1])

# Coordinates → HexCoords
coords = Coordinates(x=5, y=10)
hex_coords: HexCoords = coords.to_tuple()
```

### Direction → HexCoords (Movement Translation)

```python
def _calculate_target_coords(self, current: HexCoords, direction: Direction) -> HexCoords:
    """Convert direction string to coordinate offset."""
    x, y = current
    offsets = {
        'north': (0, -1), 'south': (0, 1),
        'east': (1, 0), 'west': (-1, 0),
        'northeast': (1, -1), 'northwest': (-1, -1),
        'southeast': (1, 1), 'southwest': (-1, 1)
    }
    dx, dy = offsets.get(direction, (0, 0))
    return (x + dx, y + dy)
```

---

## 📋 Quick Reference Table

| Representation | Type | Use Case | Hashable | Methods | Human-Readable |
|----------------|------|----------|----------|---------|----------------|
| **HexCoords** | `Tuple[int, int]` | Position tracking | ✅ Yes | ❌ No | ⚠️ Partial |
| **Coordinates** | `@dataclass` | Rich operations | ❌ No | ✅ Yes | ✅ Yes |
| **Direction** | `Literal[str]` | Navigation | ✅ Yes | ❌ No | ✅ Yes |

---

## 🎯 Decision Tree

**Need to store hex position in world map?**
→ Use **HexCoords** (hashable dict key)

**Need distance calculation or transformations?**
→ Use **Coordinates** (rich methods)

**Need user-facing movement/navigation?**
→ Use **Direction** (human-readable)

**Need to convert user direction to world position?**
→ Direction → HexCoords via offset mapping

**Need to perform calculations on world position?**
→ HexCoords → Coordinates → operations → HexCoords

---

## 📝 Import Statements

```python
# Import type aliases
from fantasy_rpg.utils import HexCoords, Direction, Coordinates

# Use in function signatures
def move_player(self, direction: Direction) -> bool:
    ...

def get_hex(self, coords: HexCoords) -> Hex:
    ...

def calculate_path(self, start: Coordinates, end: Coordinates) -> List[HexCoords]:
    ...
```

---

## 🚫 Anti-Patterns

### ❌ Don't: Mix representations without clear conversion
```python
# BAD: Storing Coordinates dataclass as dict key
coords = Coordinates(x=5, y=10)
world.hexes[coords] = hex  # TypeError: unhashable type
```

### ✅ Do: Convert to appropriate type
```python
# GOOD: Convert to HexCoords for dict key
coords = Coordinates(x=5, y=10)
world.hexes[coords.to_tuple()] = hex
```

### ❌ Don't: Create new coordinate types
```python
# BAD: Inventing yet another representation
class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col
```

### ✅ Do: Use existing representations
```python
# GOOD: Stick to the three established patterns
position: HexCoords = (row, col)
```

---

## 📚 See Also

- `fantasy_rpg/utils/utils.py` - Type alias definitions and Coordinates class
- `fantasy_rpg/world/world.py` - Hex class using HexCoords
- `fantasy_rpg/locations/location_generator.py` - Area class using Direction
- `fantasy_rpg/actions/movement_handler.py` - Direction → HexCoords conversion

---

**Last Updated:** November 4, 2025  
**Status:** Phase 3.5 Refactoring - TODO #9 Complete
