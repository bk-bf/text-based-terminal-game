# Fantasy RPG - Master Implementation Plan

## Overview

**CRITICAL PIVOT:** Stop building new systems. **Focus entirely on integration.** All backend systems exist - they need a GameEngine coordinator to work together.

**Current Status:** Strong backend, broken integration  
**Goal:** Playable Ultimate Fantasy Sim in 1-2 weeks  
**Strategy:** GameEngine coordinator layer + systematic integration

---

## Week 1: Core Integration (CRITICAL)

### **Day 1: GameEngine Foundation**
**Priority:** HIGHEST - This unlocks everything else

**Morning: Create GameEngine Coordinator**
```python
# Create fantasy_rpg/game/game_engine.py
class GameEngine:
    def new_game(self, character: Character) -> GameState
    def move_player(self, direction: str) -> tuple[bool, str]
    def get_status(self) -> dict
    def save_game(self, save_name: str)
    def load_game(self, save_name: str)
```

**Tasks:**
- [ ] Create `fantasy_rpg/game/game_engine.py` with GameEngine class
- [ ] Implement GameState dataclass holding complete game state
- [ ] Connect world generation to GameEngine initialization
- [ ] Test world generation through GameEngine

**Afternoon: Basic Integration**
- [ ] Implement movement methods in GameEngine
- [ ] Add environmental effects during travel
- [ ] Create natural language hex descriptions
- [ ] Test GameEngine basic functionality

**Success Criteria:** `game_engine.new_game(character)` creates playable world

### **Day 2: UI Integration**
**Priority:** HIGH - Makes GameEngine visible to player

**Morning: Connect UI to GameEngine**
- [ ] Modify `fantasy_rpg/ui/app.py` to use GameEngine
- [ ] Connect character creation to game initialization
- [ ] Update UI panels to display GameEngine state
- [ ] Test character creation → game start flow

**Afternoon: UI State Management**
- [ ] Implement UI refresh when game state changes
- [ ] Connect character panel to GameEngine character state
- [ ] Update context panel with current hex information
- [ ] Test UI updates when game state changes

**Success Criteria:** Create character → see starting hex description

### **Day 3: Movement System**
**Priority:** HIGH - Core gameplay mechanic

**Morning: Restore Movement**
- [ ] Add movement commands to action handler
- [ ] Connect movement to GameEngine.move_player()
- [ ] Implement error handling for invalid moves
- [ ] Test basic north/south/east/west movement

**Afternoon: Environmental Effects**
- [ ] Add survival stat changes during travel
- [ ] Implement time passage during movement
- [ ] Add weather effects on travel
- [ ] Test deadly overworld exposure

**Success Criteria:** `north` command moves player with survival consequences

### **Day 4: Centralized Logging**
**Priority:** MEDIUM - Fixes user experience issues

**Morning: Single Logger**
- [ ] Create `fantasy_rpg/game/game_logger.py`
- [ ] Replace all direct game log calls with centralized logger
- [ ] Remove duplicate logging from all systems
- [ ] Test message flow through single logger

**Afternoon: Natural Language**
- [ ] Ensure all output uses natural language (no precise numbers)
- [ ] Convert weather display to descriptive text
- [ ] Fix survival status display (Hungry/Starving, not percentages)
- [ ] Test complete natural language output

**Success Criteria:** No duplicate messages, natural language throughout

### **Day 5: Location Integration**
**Priority:** HIGH - Enables survival gameplay

**Morning: Location System**
- [ ] Connect location generation to GameEngine
- [ ] Implement enter_location() method
- [ ] Create location persistence (same locations on re-entry)
- [ ] Test location generation and entry

**Afternoon: Location Navigation**
- [ ] Implement exit_location() to return to overworld
- [ ] Add area navigation within locations
- [ ] Connect location descriptions to game log
- [ ] Test complete location entry/exit flow

**Success Criteria:** `enter 1` enters location, `exit` returns to overworld

### **Day 6: Survival Commands**
**Priority:** HIGH - Core survival mechanics

**Morning: Object Interaction**
- [ ] Connect foraging system through object interaction
- [ ] Implement context-specific commands (examine, harvest)
- [ ] Add skill checks for resource gathering
- [ ] Test foraging with inventory updates

**Afternoon: Shelter & Camping**
- [ ] Connect shelter detection system
- [ ] Implement camping mechanics with shelter quality
- [ ] Add resource consumption over time
- [ ] Test complete survival loop

**Success Criteria:** Can forage berries, find shelter, survive in wilderness

### **Day 7: Polish & Testing**
**Priority:** MEDIUM - Stability and user experience

**Morning: Bug Fixes**
- [ ] Fix remaining integration bugs
- [ ] Test complete gameplay loop
- [ ] Verify natural language output
- [ ] Performance optimization

**Afternoon: Save System**
- [ ] Add save/load for complete game state
- [ ] Test save/load with world persistence
- [ ] Polish UI feedback and error messages
- [ ] Final integration testing

**Success Criteria:** Can play 30+ minutes without crashes

---

## Week 2: Gameplay Completion

### **Day 8-9: Object Interaction System**
**Goal:** Rich interaction with discovered objects

**Tasks:**
- [ ] Implement multi-skill perception system
- [ ] Add hidden content discovery through skill checks
- [ ] Create context-specific object commands
- [ ] Test skill-based resource gathering

**Success Criteria:** Different characters discover different objects

### **Day 10-11: Settlement Foundation**
**Goal:** Civilization vs wilderness choice

**Tasks:**
- [ ] Generate settlements at appropriate scale (50+ locations for cities)
- [ ] Implement inn system with room rental and storage
- [ ] Add merchant NPCs with trading
- [ ] Create safe rest mechanics in civilization

**Success Criteria:** Player can rent inn room, trade with merchants

### **Day 12-13: Deadly Travel**
**Goal:** Make overworld travel genuinely dangerous

**Tasks:**
- [ ] Implement death from exposure and starvation
- [ ] Add permadeath with world persistence
- [ ] Create resource consumption during travel
- [ ] Test survival challenge balance

**Success Criteria:** Unprepared characters die from exposure

### **Day 14: Final Polish**
**Goal:** Complete playable experience

**Tasks:**
- [ ] Balance survival mechanics
- [ ] Polish natural language descriptions
- [ ] Add starting scenario and tutorial
- [ ] Final testing and bug fixes

**Success Criteria:** Complete Ultimate Fantasy Sim experience

---

## Success Metrics

### End of Week 1 (Minimum Viable Game)
**Player can:**
1. ✅ Create character and start new game
2. ✅ Move between hexes with environmental effects
3. ✅ Enter locations within hexes
4. ✅ Discover objects through perception
5. ✅ Interact with objects to gather resources
6. ✅ Manage survival needs (hunger, thirst, temperature)
7. ✅ Experience natural language feedback
8. ✅ Save and load game state

### End of Week 2 (Complete Vision)
**Player can:**
1. ✅ Experience deadly overworld travel
2. ✅ Choose between civilization and wilderness survival
3. ✅ Discover hidden content through skill checks
4. ✅ Access settlement services (inns, merchants)
5. ✅ Experience permadeath with world persistence
6. ✅ Explore locations at proper scale
7. ✅ Master complex survival mechanics

---

## Critical Path Dependencies

```
Day 1: GameEngine → Day 2: UI Integration → Day 3: Movement
                                              ↓
Day 5: Locations ← Day 4: Logging ← Day 3: Movement
        ↓
Day 6: Survival → Day 7: Polish
```

**Blocking Issues:**
- Day 1 GameEngine creation blocks everything else
- Day 2 UI integration required for testing
- Day 3 movement required for gameplay
- Day 5 locations required for survival

**Non-Blocking:**
- Day 4 logging (improves UX but doesn't block gameplay)
- Day 7 polish (improves experience but game is playable)

---

## Implementation Notes

### Existing Systems Status
**✅ Complete and Working:**
- Character creation and progression
- World generation (terrain, climate, biomes, weather)
- Survival mechanics (hunger, thirst, temperature)
- Location generation templates
- Item and equipment systems
- UI framework (panels, modals, input)

**⚠️ Partially Working:**
- Action handling (inventory/character work, movement broken)
- Logging system (works but creates duplicates)
- Save system (log saving works, game state saving missing)

**❌ Missing:**
- GameEngine coordinator layer
- System integration
- Natural language output consistency
- Location-world integration

### Key Principles
1. **GameEngine is single source of truth** for game state
2. **All actions flow through GameEngine** for coordination
3. **UI only handles presentation** - no game logic
4. **Natural language everywhere** except HP/AC
5. **Deadly overworld travel** - real survival consequences
6. **Persistent locations** - same locations on re-entry

### Architecture Goal
```
User Input → ActionHandler → GameEngine → Backend Systems → GameEngine → UI Update
```

**No direct UI-to-backend communication.** All coordination through GameEngine.

This plan transforms existing disconnected systems into Ultimate Fantasy Sim within 1-2 weeks through systematic integration rather than new feature development.