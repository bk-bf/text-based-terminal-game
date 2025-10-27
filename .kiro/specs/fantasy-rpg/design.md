# Fantasy RPG - Master Design Document

**Version:** 3.0  
**Date:** October 27, 2024  
**Purpose:** Architectural blueprint for Ultimate Fantasy Sim integration

---

## Executive Summary

Ultimate Fantasy Sim is a hardcore permadeath text-based survival RPG with a **two-layer world structure**: deadly overworld hex travel and detailed location-based exploration. The core challenge is **survival through resource management** with the ultimate choice between seeking civilization's safety or mastering wilderness independence.

**Current Status:** Strong backend systems exist but are disconnected. **Priority: Integration, not more features.**

**Architecture Goal:** Create a **GameEngine coordinator layer** that orchestrates all existing systems into a cohesive gameplay experience.

---

## Architecture Overview

### Current Problem: Disconnected Systems

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI System     │    │  Backend Systems │    │  Action System  │
│                 │    │                  │    │                 │
│ • Panels        │    │ • World Gen      │    │ • Input Parser  │
│ • Modals        │    │ • Character      │    │ • Commands      │
│ • Logging       │    │ • Survival       │    │ • Responses     │
│                 │    │ • Weather        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                        ❌ NO COORDINATION
```

### Solution: GameEngine Coordinator

```
┌─────────────────────────────────────────────────────────────────┐
│                        GameEngine                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ GameState   │  │ Integration │  │ Coordination│            │
│  │             │  │             │  │             │            │
│  │ • Character │  │ • Movement  │  │ • Time      │            │
│  │ • Position  │  │ • Survival  │  │ • Weather   │            │
│  │ • World     │  │ • Location  │  │ • Events    │            │
│  │ • Time      │  │ • Actions   │  │ • State     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
        │                        │                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI System     │    │  Backend Systems │    │  Action System  │
│                 │    │                  │    │                 │
│ • Panels        │    │ • World Gen      │    │ • Input Parser  │
│ • Modals        │    │ • Character      │    │ • Commands      │
│ • Logging       │    │ • Survival       │    │ • Responses     │
│                 │    │ • Weather        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Two-Layer World Structure

### Layer 1: Overworld Hex Map (Deadly Travel)

**Purpose:** Strategic movement, resource planning, environmental survival

**Characteristics:**
- Large hex grid (20x20 minimum, expandable to 500x500+)
- Each hex = 3-5 square miles of terrain
- Travel time: 1-4 hours per hex depending on terrain/weather
- **Deadly exposure:** Continuous hunger/thirst/temperature effects
- **No direct survival actions:** Cannot forage/camp while traveling
- **Environmental hazards:** Hypothermia, heat stroke, exhaustion

**Player Actions:**
- Move north/south/east/west to adjacent hexes
- View inventory and character status
- **Enter locations** within current hex
- **No survival actions** - must enter locations to survive

### Layer 2: Location-Based Exploration (Detailed Interaction)

**Purpose:** Resource gathering, survival preparation, detailed exploration

**Characteristics:**
- 5-20 locations per hex (50+ for settlements)
- **Persistent generation:** Same locations on re-entry
- Connected areas within each location
- **Context-specific interactions** with discovered objects
- **Skill-based discovery:** Hidden content revealed by perception checks

**Player Actions:**
- Navigate between connected areas
- **Examine objects** discovered through perception
- **Interact with specific objects** using contextual commands
- **Forage, camp, search** - all survival actions happen here
- **Combat and NPC interaction**

---

## Core Gameplay Loop

### Phase 1: Immediate Survival (First Hour)
1. **Spawn in wilderness hex** with minimal supplies
2. **Enter location** to escape overworld exposure
3. **Discover objects** through automatic perception checks
4. **Interact with objects** to gather resources (berries, water, shelter)
5. **Assess situation:** Can I survive here or must I seek civilization?

### Phase 2: The Critical Choice
**Path A: Seek Civilization**
- Gather supplies for multi-hex journey
- Risk deadly overworld travel
- Success = access to inns, merchants, quests
- Failure = death from exposure

**Path B: Wilderness Survival**
- Master local resources and threats
- Build knowledge of safe locations
- Much harder but complete independence
- Success depends on skill and seasonal factors

### Phase 3: Established Gameplay
**Civilization Path:** Inn rental, trading, quest completion, safe storage
**Wilderness Path:** Seasonal survival, resource mastery, exploration

---

## System Integration Requirements

### GameEngine Responsibilities

1. **World State Management**
   - Initialize world generation on new game
   - Track player position (hex coordinates)
   - Manage current location and area within location
   - Coordinate time passage across all systems

2. **Action Coordination**
   - Route movement commands to world system
   - Route survival commands to appropriate systems
   - Route location commands to location generator
   - Ensure all actions update relevant systems

3. **State Synchronization**
   - Update UI panels when state changes
   - Apply environmental effects during travel
   - Manage resource consumption over time
   - Coordinate weather and seasonal changes

4. **Persistence Management**
   - Save/load complete game state
   - Maintain location persistence
   - Track world changes over time

### UI Integration Points

**Character Panel (Left):**
- Character stats (HP, AC only numbers shown)
- **Natural language survival status** (Hungry/Starving, not percentages)
- Equipment summary
- Current conditions and effects

**Game Log (Center):**
- **Single source of truth** for all messages
- Natural language descriptions
- Action results and environmental feedback
- **No duplicate logging**

**Context Panel (Right):**
- Current hex/location information
- Available actions based on current context
- Environmental conditions in natural language
- Time and season information

---

## Natural Language Philosophy

### Strict Requirements

**Never Show:**
- Numerical hunger/thirst values (no "65/100 hunger")
- Precise temperatures ("32°F" → "freezing cold")
- Exact distances ("3.2 miles" → "a few miles")
- Percentage indicators for any survival needs
- Precise time increments ("+15 minutes" → "some time passes")

**Always Show:**
- Descriptive states (Well-fed, Hungry, Starving)
- Natural weather descriptions (Heavy rain with strong winds)
- Relative time (Late afternoon, spring)
- Immersive environmental descriptions

### Information Hierarchy

**Obvious Information:** Always visible
- Large terrain features, weather conditions, obvious objects

**Clear Information:** Visible with basic attention
- Normal objects, standard resources, clear paths

**Hidden Information:** Requires skill checks
- Concealed items, secret passages, valuable resources

**Very Hidden Information:** Requires expertise
- Ancient treasures, magical secrets, master-level content

---

## Development Priorities

### Week 1: Core Integration (CRITICAL)

**Day 1: GameEngine Foundation**
- Create `fantasy_rpg/game/game_engine.py`
- Implement GameState dataclass
- Create world initialization pipeline
- Test world generation through GameEngine

**Day 2: UI Integration**
- Connect GameEngine to `fantasy_rpg/ui/app.py`
- Implement character creation → game start flow
- Test basic game initialization

**Day 3: Movement System**
- Add movement commands to action handler
- Connect movement to world coordinator
- Implement environmental effects during travel
- Test hex-to-hex movement

**Day 4: Centralized Logging**
- Create `fantasy_rpg/game/game_logger.py`
- Eliminate all duplicate logging
- Ensure single source of truth for messages
- Test message flow

**Day 5: Location Integration**
- Connect location generation to GameEngine
- Implement enter/exit location mechanics
- Test location persistence

**Day 6: Survival Commands**
- Restore foraging through object interaction
- Implement shelter detection and camping
- Connect to existing survival systems
- Test resource gathering

**Day 7: Polish & Testing**
- Fix remaining integration issues
- Test complete gameplay loop
- Verify natural language output
- Performance optimization

### Week 2: Gameplay Completion

**Days 8-10: Object Interaction System**
- Implement context-specific commands
- Add skill-based discovery mechanics
- Create object interaction parser
- Test hidden content revelation

**Days 11-12: Settlement Foundation**
- Generate settlements at appropriate scale
- Implement inn system with room rental
- Add basic merchant trading
- Create safe rest mechanics

**Days 13-14: Survival Loop**
- Implement deadly overworld exposure
- Add resource consumption during travel
- Create permadeath mechanics
- Test complete survival challenge

---

## Success Criteria

### Minimum Viable Game (End of Week 1)

**Player can:**
1. ✅ Create character and start new game
2. ✅ Move between hexes with environmental effects
3. ✅ Enter locations within hexes
4. ✅ Discover objects through perception
5. ✅ Interact with objects to gather resources
6. ✅ Manage survival needs (hunger, thirst, temperature)
7. ✅ Experience natural language feedback
8. ✅ Save and load game state

### Complete Game Vision (End of Week 2)

**Player can:**
1. ✅ Experience deadly overworld travel
2. ✅ Choose between civilization and wilderness survival
3. ✅ Discover hidden content through skill checks
4. ✅ Access settlement services (inns, merchants)
5. ✅ Experience permadeath with world persistence
6. ✅ Explore locations at proper scale
7. ✅ Interact with persistent, evolving world
8. ✅ Master complex survival mechanics

---

## Technical Architecture

### Core Classes

```python
@dataclass
class GameState:
    character: Character
    player_state: PlayerState
    world_coordinator: WorldCoordinator
    location_generator: LocationGenerator
    time_system: TimeSystem
    current_hex: tuple[int, int]
    current_location: Optional[Location] = None
    current_area: Optional[Area] = None
    mode: str = "travel"  # "travel", "exploration", "combat"

class GameEngine:
    def __init__(self)
    def new_game(self, character: Character) -> GameState
    def move_player(self, direction: str) -> tuple[bool, str]
    def enter_location(self, location_index: int) -> tuple[bool, str]
    def exit_location(self) -> tuple[bool, str]
    def interact_with_object(self, object_name: str, action: str) -> tuple[bool, str]
    def get_status(self) -> dict
    def save_game(self, save_name: str)
    def load_game(self, save_name: str)
```

### Integration Flow

```
User Input → ActionHandler → GameEngine → Backend Systems → GameEngine → UI Update
```

**No direct communication between UI and backend systems.** All coordination through GameEngine.

---

## Implementation Notes

### Existing Systems to Leverage

**Keep and Integrate:**
- World generation (terrain, climate, biomes)
- Character creation and progression
- Survival mechanics (hunger, thirst, temperature)
- Weather simulation
- Location generation templates
- Item and equipment systems

**Modify for Integration:**
- Action handler (delegate to GameEngine)
- UI app (use GameEngine for state)
- Logging system (centralize through GameLogger)

**Remove/Simplify:**
- Duplicate logging calls
- Direct backend-to-UI communication
- Scattered command processing
- Inconsistent state management

### Key Design Principles

1. **GameEngine is the single source of truth** for game state
2. **All user actions flow through GameEngine** for coordination
3. **UI only handles presentation** - no game logic
4. **Natural language everywhere** except HP/AC numbers
5. **Persistent world state** - locations and changes persist
6. **Skill-based discovery** - hidden content rewards character builds
7. **Deadly travel** - overworld movement has real consequences

This architecture transforms the existing disconnected systems into a cohesive, playable survival RPG that matches the Ultimate Fantasy Sim vision.