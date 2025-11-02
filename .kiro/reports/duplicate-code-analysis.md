# Duplicate Code Detection Report
**Date**: November 2, 2025  
**Scope**: Post-cleanup codebase analysis for redundant implementations

## Executive Summary

Found **4 critical duplications** and **3 conflicting state representations** across the codebase. These represent architectural debt that will cause integration issues in Phase 4.

**Total Impact**: ~500 lines of duplicate code, multiple conflicting APIs, state synchronization bugs waiting to happen.

## Critical Issue #1: THREE Item Classes ⚠️

### The Problem
Three separate item representations with overlapping fields but incompatible APIs:

1. **`Item`** (core/item.py) - Base item from JSON, used by ItemLoader
2. **`InventoryItem`** (core/inventory.py) - Item with quantity tracking
3. **`GameItem`** (locations/location_generator.py) - Simplified item for locations

### Code Duplication

**Item** (item.py:14-60):
```python
@dataclass
class Item:
    name: str
    item_type: str
    weight: float
    value: int = 0
    description: str = ""
    properties: Optional[List[str]] = None
    pools: Optional[List[str]] = None
    drop_weight: int = 1
    
    # Equipment-specific
    ac_bonus: Optional[int] = None
    armor_type: Optional[str] = None
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    equippable: bool = False
    slot: Optional[str] = None
    magical: bool = False
    enchantment_bonus: int = 0
    special_properties: Optional[List[str]] = None
    capacity_bonus: float = 0.0
```

**InventoryItem** (inventory.py:14-38):
```python
@dataclass
class InventoryItem:
    item_id: str  # ⚠️ Different from Item (no item_id)
    name: str
    item_type: str
    weight: float
    value: int
    quantity: int = 1  # ⚠️ NEW: quantity tracking
    description: str = ""
    properties: List[str] = field(default_factory=list)
    
    # DUPLICATE: Same equipment fields as Item
    equippable: bool = False
    slot: Optional[str] = None
    ac_bonus: int = 0
    armor_type: Optional[str] = None
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    magical: bool = False
    enchantment_bonus: int = 0
    special_properties: List[str] = field(default_factory=list)
    capacity_bonus: float = 0.0
```

**GameItem** (location_generator.py:57-65):
```python
@dataclass
class GameItem:
    id: str  # ⚠️ Different naming: 'id' vs 'item_id'
    name: str
    description: str = ""
    value: int = 0
    weight: float = 0.0
    # ⚠️ MISSING: All equipment fields, type, properties
```

### The Impact

1. **Conversion Hell**: InventoryItem has `to_item()` method (inventory.py:120-147)
   - 30 lines of code just to convert between representations
   - Error-prone field mapping

2. **Three Loading Systems**:
   - `ItemLoader.load_items()` → Returns `Dict[str, Item]`
   - `LocationGenerator._build_item_pools()` → Creates `GameItem` instances
   - `InventoryManager.create_inventory_item_from_id()` → Returns `InventoryItem`

3. **Field Mismatch Bugs**:
   - Item has `pools` and `drop_weight` for spawning
   - GameItem lacks ALL equipment/type/properties data
   - InventoryItem duplicates ALL Item fields + adds `item_id` and `quantity`

### Files Affected
- `fantasy_rpg/core/item.py` (425 lines)
- `fantasy_rpg/core/inventory.py` (469 lines)
- `fantasy_rpg/locations/location_generator.py` (623 lines)
- `fantasy_rpg/core/equipment.py` (imports Item)
- `fantasy_rpg/game/game_engine.py` (uses all three)

### Recommended Fix
**UNIFY into single `Item` class with optional `quantity` field**:
```python
@dataclass
class Item:
    item_id: str  # Primary key
    name: str
    item_type: str
    weight: float
    value: int = 0
    quantity: int = 1  # Default to 1, increase for stacking
    # ... rest of fields from current Item
    
    # Add methods from InventoryItem
    def get_total_weight(self) -> float:
        return self.weight * self.quantity
```

**Delete**: `InventoryItem` class entirely  
**Delete**: `GameItem` class entirely  
**Update**: LocationGenerator to use unified Item  
**Estimated savings**: 200+ lines, single source of truth

---

## Critical Issue #2: Duplicate JSON Loading Logic

### The Problem
Four separate systems load the same JSON files with different caching strategies:

1. **`ItemLoader`** (item.py:215-290) - Loads items.json with caching
2. **`LocationGenerator._load_content_pools()`** (location_generator.py:190-250) - Loads items.json, objects.json, entities.json with pool building
3. **`ClassLoader`** (character_class.py:84-140) - Loads classes.json
4. **`RaceLoader`** (race.py:64-110) - Loads races.json

### Code Duplication Pattern

Every loader has this pattern (95% identical code):

```python
class SomeLoader:
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            # Try to find the data directory
            current_dir = Path(__file__).parent
            parent_data_dir = current_dir.parent / "data"
            core_data_dir = current_dir / "data"
            relative_data_dir = Path("fantasy_rpg/data")
            
            if parent_data_dir.exists():
                data_dir = parent_data_dir
            elif core_data_dir.exists():
                data_dir = core_data_dir
            elif relative_data_dir.exists():
                data_dir = relative_data_dir
            else:
                data_dir = parent_data_dir
        
        self.data_dir = data_dir
        self._cache = {}
    
    def load_something(self) -> Dict[str, SomeClass]:
        if 'cache_key' not in self._cache:
            file_path = self.data_dir / "something.json"
            # ... load and parse JSON
```

**30-40 lines duplicated across 4+ loaders** = 120-160 lines of redundant path resolution code

### LocationGenerator's Duplicate Path Search

LocationGenerator has its OWN path searching (location_generator.py:166-180):
```python
possible_paths = [
    "data/locations.json",
    "../data/locations.json",
    "../../data/locations.json",
    "fantasy_rpg/data/locations.json"
]

for path in possible_paths:
    if os.path.exists(path):
        with open(path, 'r') as f:
            templates = json.load(f)
```

This is repeated 4 times in `_load_content_pools()`:
- Lines 197-208 (objects.json)
- Lines 212-223 (entities.json)
- Lines 227-238 (items.json)
- Lines 166-180 (locations.json)

**60 lines of duplicate path searching within ONE file**

### Recommended Fix
**Create `DataLoader` base class**:
```python
class DataLoader:
    """Base class for all JSON data loaders"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = self._find_data_dir(data_dir)
        self._cache = {}
    
    @staticmethod
    def _find_data_dir(data_dir: Path = None) -> Path:
        """Single implementation of data directory discovery"""
        if data_dir is not None:
            return data_dir
        
        current_dir = Path(__file__).parent
        candidates = [
            current_dir.parent / "data",
            current_dir / "data",
            Path("fantasy_rpg/data")
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        return candidates[0]  # Fallback
    
    def load_json(self, filename: str, cache_key: str = None) -> Dict:
        """Load JSON with optional caching"""
        cache_key = cache_key or filename
        
        if cache_key not in self._cache:
            file_path = self.data_dir / filename
            with open(file_path, 'r') as f:
                self._cache[cache_key] = json.load(f)
        
        return self._cache[cache_key]
```

**Then**: All loaders inherit from DataLoader  
**Estimated savings**: 120+ lines

---

## Critical Issue #3: Shelter State Conflict 🔥

### The Problem
**TWO conflicting representations** of player shelter status:

1. **PlayerState.current_shelter** (player_state.py:187)
   ```python
   current_shelter: Optional[Dict[str, str]] = None
   ```

2. **Conditions System** (conditions.py:329-350)
   ```python
   def _evaluate_shelter_conditions(self, player_state) -> List[str]:
       if hasattr(player_state, 'current_shelter') and player_state.current_shelter:
           shelter_quality = player_state.current_shelter.get("quality", "none")
       # ... but also checks location-based shelter flags
   ```

3. **Location Shelter Flags** (location_generator.py:122-125)
   ```python
   class Location:
       provides_some_shelter: bool = False
       provides_good_shelter: bool = False
       provides_excellent_shelter: bool = False
   ```

### The Conflict

**GameEngine sets PlayerState.current_shelter** (game_engine.py:2014-2032):
```python
if hasattr(gs.player_state, 'current_shelter'):
    gs.player_state.current_shelter = {
        "type": "location",
        "quality": quality
    }
# ...
gs.player_state.current_shelter = None  # On exit
```

**But Conditions also checks location flags directly** (conditions.py:335-350):
```python
# Fallback: check current location for shelter flags
if gs.current_location:
    if hasattr(gs.current_location, 'provides_excellent_shelter') and gs.current_location.provides_excellent_shelter:
        shelter_quality = "excellent"
```

**Result**: TWO sources of truth for the same state!

### Usage Analysis
- **PlayerState.current_shelter**: 15 references
  - Set in: game_engine.py (3 places)
  - Read in: conditions.py (1 place), player_state.py (2 places)
  - hasattr checks: 5 places

- **Location shelter flags**: 3 references
  - Defined in: location_generator.py
  - Checked in: conditions.py
  - Never set by GameEngine!

### The Bug
If you enter a location with `provides_excellent_shelter=True` but GameEngine doesn't set `current_shelter`, the condition system will use location flags as fallback. But if GameEngine sets `current_shelter` to "some" quality, it overrides the location's "excellent" quality.

**Race condition**: Which system updates first determines shelter quality!

### Recommended Fix
**DELETE `PlayerState.current_shelter` entirely**  
**Use ONLY location shelter flags**:
```python
# In ConditionsManager
def _get_current_shelter_quality(self, game_engine) -> str:
    location = game_engine.current_location
    if not location:
        return "none"
    
    if getattr(location, 'provides_excellent_shelter', False):
        return "excellent"
    elif getattr(location, 'provides_good_shelter', False):
        return "good"
    elif getattr(location, 'provides_some_shelter', False):
        return "some"
    return "none"
```

**Estimated savings**: 20 lines, eliminates race condition

---

## Issue #4: Duplicate Get Temperature Methods

### The Problem
THREE methods calculate/retrieve temperature at different abstraction levels:

1. **ClimateSystem.get_temperature_at_coords()** (climate.py:355)
   - Takes: coords, elevation, season
   - Returns: Base temperature from climate zones

2. **WorldCoordinator.get_temperature_at_hex()** (world_coordinator.py:751)
   - Takes: hex_id, season
   - Wraps ClimateSystem.get_temperature_at_coords()
   - Adds hex lookup

3. **PlayerState.get_temperature_status()** (player_state.py:132)
   - Takes: nothing (uses internal body_temperature)
   - Returns: TemperatureStatus enum

### The Confusion
Which one should GameEngine use?
- For ambient temperature → ClimateSystem
- For hex temperature → WorldCoordinator
- For player condition → PlayerState

**But**: No clear documentation, all three are public methods

### Recommended Fix
**Clarify responsibilities with naming**:
```python
# ClimateSystem
def get_ambient_temperature(coords, elevation, season) -> float

# WorldCoordinator  
def get_hex_ambient_temperature(hex_id, season) -> float

# PlayerState
def get_body_temperature_status() -> TemperatureStatus
```

**Add docstrings** explaining when to use each

---

## Minor Duplications

### 5. Dice Rolling (Low Priority)
- **Dice class** in utils/utils.py is only instance
- ✅ No duplication found

### 6. Multiple Coordinate Representations
- **Coordinates dataclass** (utils/utils.py:146)
- **Hex.coords** (world/world.py:19) - uses Tuple[int, int]
- **Area.exits** - uses string direction keys

**Not critical**: Different use cases, acceptable variation

---

## Summary Table

| Issue                   | Files Affected | Duplicate Lines    | Priority   | Risk                        |
| ----------------------- | -------------- | ------------------ | ---------- | --------------------------- |
| **Three Item Classes**  | 5              | ~200               | 🔴 CRITICAL | High - Integration blocker  |
| **JSON Loading**        | 6+             | ~120-160           | 🟡 HIGH     | Medium - Maintenance burden |
| **Shelter State**       | 3              | ~20                | 🔴 CRITICAL | High - Race conditions      |
| **Temperature Methods** | 3              | ~0 (API confusion) | 🟡 MEDIUM   | Low - Documentation fix     |

**Total Duplicate Code**: 340-380 lines  
**Total Files Needing Refactoring**: 11

---

## Phase 4 Integration Risks

### Immediate Blockers
1. **Item System**: Cannot add new item types without updating 3 classes
2. **Shelter System**: Adding shelter mechanics will conflict with dual state
3. **Content Loading**: New JSON files need 30 lines of boilerplate per loader

### Technical Debt Interest
- Every new feature touching items requires 3× the work
- Shelter bugs will manifest as player complaints about condition system
- JSON loading code will diverge further (already has inconsistencies)

---

## Recommended Cleanup Priority

### Phase 1: Critical Path (Before Phase 4)
1. **Unify Item classes** → Blocks all inventory/equipment/location work
2. **Fix shelter state** → Blocks condition system integration
3. **Create DataLoader base** → Required for new content systems

### Phase 2: Technical Debt
4. Clarify temperature API naming
5. Document coordinator responsibilities

**Estimated effort**: 2-3 days for Phase 1 cleanup  
**Impact**: Eliminate 340+ duplicate lines, fix 2 race conditions

---

## Verification Checklist

After refactoring:
- [ ] All item references use unified Item class
- [ ] InventoryItem class deleted
- [ ] GameItem class deleted  
- [ ] LocationGenerator uses Item directly
- [ ] PlayerState.current_shelter removed
- [ ] Conditions use ONLY location shelter flags
- [ ] All loaders inherit from DataLoader
- [ ] Temperature method naming clarified
- [ ] Integration tests pass (manual gameplay)
- [ ] Save/load system still works

---

**Next Action**: Begin Item class unification - highest impact, blocks most Phase 4 work.
