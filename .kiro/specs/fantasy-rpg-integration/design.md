# Fantasy RPG Integration - Design Document

## Overview

The integration phase connects all existing, working foundation systems through a GameEngine coordinator. This is **not** about building new systems - it's about orchestrating existing ones.

## Architecture

### Current State (Working Systems)
```
✅ Character System (core/)
✅ Equipment & Inventory (core/)
✅ UI Framework (ui/)
✅ World Generation (world/)
✅ Action Handling (actions/)
✅ Save System (game/)
✅ Location Generation (locations/)
```

### Target Integration Architecture
```
User Input → ActionHandler → GameEngine → Backend Systems → GameEngine → UI Update
```

### GameEngine Coordinator Design

The GameEngine serves as the central coordinator that:
1. **Initializes** all systems with proper dependencies
2. **Coordinates** actions between systems
3. **Maintains** single source of truth for game state
4. **Handles** save/load for complete game state

```python
class GameEngine:
    def __init__(self):
        self.character = None
        self.world_coordinator = WorldCoordinator()
        self.player_state = PlayerState()
        self.current_location = None
        self.game_time = TimeSystem()
        
    def new_game(self, character: Character) -> GameState:
        """Initialize new game with character placement in world"""
        
    def move_player(self, direction: str) -> tuple[bool, str]:
        """Handle hex-to-hex movement with environmental effects"""
        
    def enter_location(self, location_id: str) -> tuple[bool, str]:
        """Enter location within current hex"""
        
    def get_status(self) -> dict:
        """Get complete game status for UI display"""
```

## Components and Interfaces

### 1. GameState Management
**Purpose:** Single source of truth for all game data

**Components:**
- Character state (HP, stats, equipment, inventory)
- World position (current hex, location)
- Environmental state (weather, time, season)
- Player state (hunger, thirst, temperature, conditions)

### 2. Movement Integration
**Purpose:** Connect movement commands to world systems

**Flow:**
1. Player issues movement command
2. GameEngine validates movement possibility
3. Apply travel time and environmental effects
4. Update weather and world state
5. Apply survival consequences
6. Update UI with natural language feedback

### 3. Location System Integration
**Purpose:** Connect location exploration to world generation

**Flow:**
1. Player enters location within hex
2. GameEngine generates/loads persistent location data
3. Connect location objects to foraging system
4. Handle object interaction and resource gathering
5. Maintain location state for re-entry

### 4. UI State Synchronization
**Purpose:** Keep UI panels updated with current game state

**Components:**
- Character panel shows current stats and conditions
- Context panel shows current hex/location information
- Game log shows natural language event descriptions
- All panels refresh when game state changes

## Data Models

### GameState
```python
@dataclass
class GameState:
    character: Character
    world_position: WorldPosition
    player_state: PlayerState
    current_location: Optional[Location]
    game_time: GameTime
    weather: WeatherState
    
@dataclass
class WorldPosition:
    hex_id: str
    hex_data: dict
    available_locations: List[dict]
```

## Error Handling

### Movement Errors
- Invalid direction (not adjacent hex)
- Blocked movement (terrain restrictions)
- Character incapacitated (unconscious, dead)

### Location Errors
- Invalid location ID
- Location not available in current hex
- Already in a location when trying to enter

### System Integration Errors
- Save/load failures
- UI update failures
- Backend system communication errors

## Testing Strategy

### Integration Testing Priority
1. **Character Creation → World Initialization**
   - Create character → GameEngine.new_game() → World generated
   
2. **Movement System**
   - Movement commands → GameEngine.move_player() → Environmental effects applied
   
3. **Location Exploration**
   - Enter location → Persistent location data → Object interaction
   
4. **UI Synchronization**
   - Game state changes → UI panels update → Accurate display
   
5. **Save/Load Integration**
   - Save complete state → Load → Continue seamlessly

### Manual Testing Scenarios
- Create character → Move 5 hexes → Enter location → Forage → Save → Load → Continue
- Test survival mechanics: hunger/thirst effects during travel
- Test weather integration: movement penalties in storms
- Test natural language output: no precise numbers except HP/AC

## Implementation Phases

### Phase 1: GameEngine Foundation (Day 1)
- Create GameEngine class with basic structure
- Implement new_game() method
- Connect to existing world generation
- Test world initialization

### Phase 2: Movement Integration (Day 2-3)
- Implement move_player() method
- Connect to existing survival mechanics
- Add environmental effects during travel
- Test movement with consequences

### Phase 3: Location Integration (Day 4-5)
- Implement location entry/exit
- Connect to existing location generation
- Add object interaction system
- Test foraging and resource gathering

### Phase 4: UI Integration (Day 6)
- Connect GameEngine to existing UI
- Implement state synchronization
- Fix logging system (eliminate duplicates)
- Test complete UI flow

### Phase 5: Polish & Testing (Day 7)
- Complete save/load integration
- Fix remaining bugs
- Test complete gameplay loop
- Verify natural language output

This design leverages all existing systems while adding the missing coordination layer to create a cohesive gameplay experience.