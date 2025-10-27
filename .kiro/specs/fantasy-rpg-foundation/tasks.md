# Fantasy RPG Foundation - Integration Tasks

## Overview

**CRITICAL PIVOT:** Stop building new backend systems. Focus entirely on **integrating existing systems** through a GameEngine coordinator layer. All backend systems exist - they just need proper orchestration.

**Estimated Time:** 1 week (7 days)  
**Dependencies:** Existing backend systems (character, world, survival, locations)  
**Deliverable:** Playable game loop with character creation → hex travel → location exploration → survival mechanics

---

## Week 1: Critical Integration (Days 1-7)

### **Day 1: GameEngine Foundation**
**Goal:** Create the missing coordinator layer that ties all systems together

**Morning Tasks:**
- [ ] Create `fantasy_rpg/game/game_engine.py` with GameEngine class
- [ ] Implement GameState dataclass to hold complete game state
- [ ] Create world initialization pipeline through GameEngine
- [ ] Test world generation through GameEngine coordinator

**Afternoon Tasks:**
- [ ] Implement basic movement methods in GameEngine
- [ ] Add environmental effects application during travel
- [ ] Create hex description generation with natural language
- [ ] Test GameEngine initialization and basic functionality

**Checkpoint:** GameEngine can initialize world and handle basic operations
**Success Criteria:** `game_engine.new_game(character)` creates playable world state

### **Day 2: UI Integration**
**Goal:** Connect GameEngine to existing UI system

**Morning Tasks:**
- [ ] Modify `fantasy_rpg/ui/app.py` to use GameEngine
- [ ] Connect character creation completion to game initialization
- [ ] Update UI panels to display GameEngine state
- [ ] Test character creation → game start flow

**Afternoon Tasks:**
- [ ] Implement UI refresh methods when game state changes
- [ ] Connect character panel to GameEngine character state
- [ ] Update context panel to show current hex information
- [ ] Test UI updates when game state changes

**Checkpoint:** Character creation leads to initialized game world
**Success Criteria:** Create character → see starting hex description in game log

### **Day 3: Movement System**
**Goal:** Restore hex-to-hex movement through proper integration

**Morning Tasks:**
- [ ] Add movement commands to action handler
- [ ] Connect movement commands to GameEngine.move_player()
- [ ] Implement proper error handling for invalid moves
- [ ] Test basic north/south/east/west movement

**Afternoon Tasks:**
- [ ] Add environmental effects during travel (hunger, thirst, temperature)
- [ ] Implement time passage during movement
- [ ] Add weather effects on travel
- [ ] Test survival stat changes during movement

**Checkpoint:** Player can move between hexes with proper feedback
**Success Criteria:** `north` command moves player and updates survival stats

### **Day 4: Centralized Logging**
**Goal:** Eliminate duplicate logging and create single source of truth

**Morning Tasks:**
- [ ] Create `fantasy_rpg/game/game_logger.py` with centralized logger
- [ ] Replace all direct game log calls with centralized logger
- [ ] Remove duplicate logging from action handlers and UI
- [ ] Test message flow through single logger

**Afternoon Tasks:**
- [ ] Implement message queuing for initialization phase
- [ ] Add message type handling (normal, combat, system)
- [ ] Ensure natural language output for all messages
- [ ] Test complete logging flow

**Checkpoint:** All game messages flow through single logger
**Success Criteria:** No duplicate messages, clean log output

### **Day 5: Location Integration**
**Goal:** Connect location generation system to GameEngine

**Morning Tasks:**
- [ ] Add location generation to GameEngine hex data
- [ ] Implement enter_location() method in GameEngine
- [ ] Create location persistence (same locations on re-entry)
- [ ] Test location generation and entry

**Afternoon Tasks:**
- [ ] Implement exit_location() method to return to overworld
- [ ] Add location area navigation within locations
- [ ] Connect location descriptions to game log
- [ ] Test complete location entry/exit flow

**Checkpoint:** Player can enter and explore locations within hexes
**Success Criteria:** `enter 1` command enters location, `exit` returns to overworld

### **Day 6: Survival Commands**
**Goal:** Restore foraging, shelter, and survival mechanics

**Morning Tasks:**
- [ ] Connect foraging system to GameEngine through object interaction
- [ ] Implement context-specific object commands (examine, harvest, etc.)
- [ ] Add skill checks for resource gathering
- [ ] Test foraging mechanics with inventory updates

**Afternoon Tasks:**
- [ ] Connect shelter detection system to GameEngine
- [ ] Implement camping mechanics with shelter quality
- [ ] Add resource consumption over time
- [ ] Test complete survival loop

**Checkpoint:** Player can forage, find shelter, and manage survival needs
**Success Criteria:** Can gather berries, find shelter, survive in wilderness

### **Day 7: Polish & Testing**
**Goal:** Fix remaining issues and ensure stable gameplay loop

**Morning Tasks:**
- [ ] Fix any remaining integration bugs
- [ ] Test complete gameplay loop: create character → travel → explore → survive
- [ ] Verify natural language output throughout
- [ ] Performance optimization for smooth gameplay

**Afternoon Tasks:**
- [ ] Add save/load functionality for complete game state
- [ ] Test save/load with world persistence
- [ ] Polish UI feedback and error messages
- [ ] Final integration testing

**Checkpoint:** Complete playable game loop works smoothly
**Success Criteria:** Can play for 30+ minutes without crashes or major issues

---

## Risk Mitigation Strategies

### Technical Risks

**Risk: Save file corruption or data loss**
- **Mitigation:** Implement backup saves, integrity checks
- **Fallback:** Manual save export/import
- **Detection:** Stress testing in Week 2

**Risk: UI feels sluggish or unresponsive**
- **Mitigation:** Test on minimum terminal size (80x24), optimize rendering
- **Fallback:** Simplify UI layout, reduce real-time updates
- **Detection:** Manual testing on different terminals



### Scope Risks

**Risk: Tasks take longer than estimated**
- **Mitigation:** Track actual vs estimated time daily
- **Fallback:** Cut optional features (see De-scope List below)
- **Detection:** Daily progress reviews

**Risk: D&D mechanics too complex for timeline**
- **Mitigation:** Focus on core mechanics first (attack, damage, AC)
- **Fallback:** Simplify to basic RPG stats (no skills/saves)
- **Detection:** Milestone 1.2 review

### De-scope Options (If Behind Schedule)

**Priority 1 (Keep):**
- Character creation with 4 races, 4 classes
- Basic inventory and equipment
- UI system with modals and command parsing
- Save/load system

**Priority 2 (Keep if possible):**
- Full D&D skill system
- Character progression (leveling)
- Equipment bonuses and magical items

**Priority 3 (Can cut for MVP):**
- Advanced equipment (rings, amulets)
- Item durability system
- Container items (backpacks)
- Feat system

---

## Testing Strategy

### **Unit Tests (>60% coverage):**
- [ ] Character stat calculations (ability modifiers, AC, HP)
- [ ] Equipment slot logic (equip/unequip, restrictions)
- [ ] Inventory weight calculations and encumbrance
- [ ] Save/load serialization (round-trip data integrity)
- [ ] Dice rolling functions (seeded RNG consistency)

### **Integration Tests:**
- [ ] Character creation → stat display → save
- [ ] Equip item → recalculate AC → save → load → verify AC
- [ ] UI modal flow: open inventory → equip item → close → verify changes

### **Manual Testing:**
- [ ] Create 10 different character builds (all race/class combinations)
- [ ] Verify save/load across multiple sessions
- [ ] Test UI on different terminal sizes (80x24 minimum)

### **Testing Exit Criteria:**
- All unit tests passing with >60% coverage
- Can create character, manage inventory, save, quit, reload, continue
- No memory leaks after 30-minute session
- UI responsive on 80x24 terminal

---

## Success Criteria

### **Foundation Complete When:**
- [ ] Character creation with 4 races, 4 classes working
- [ ] Equipment system with AC calculation functional
- [ ] Inventory with weight tracking operational
- [ ] Three-panel UI with modal screens working
- [ ] Save/load preserves all character and inventory state
- [ ] All tests passing with >60% coverage

### **Quality Benchmarks:**
- [ ] Character creation completes in <5 seconds
- [ ] UI commands respond in <100ms
- [ ] Save/load operations complete in <2 seconds
- [ ] Memory usage stable during extended play

### **Deliverable Verification:**
- [ ] Can create character → manage equipment → save → reload → continue
- [ ] All D&D mechanics calculate correctly per rulebook
- [ ] UI is clear and navigable with keyboard only
- [ ] Code is documented with type hints throughout