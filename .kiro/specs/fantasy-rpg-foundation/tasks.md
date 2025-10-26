# Fantasy RPG Foundation - Implementation Tasks

## Overview

This spec implements the foundation layer for the Fantasy RPG system, establishing core infrastructure for character management, world generation, and terminal-based UI. All subsequent systems depend on this foundation.

**Estimated Time:** 3-4 weeks (17 days)  
**Dependencies:** None (foundation layer)  
**Deliverable:** Playable character creation → world exploration → basic location discovery loop with persistent saves

---

## Milestone 1.1: Project Setup & Infrastructure (Days 1-3)

### **Milestone 1.1.1: Project Structure (Day 1)**
- [x] Create directory layout per design.md
- [x] Set up Python virtual environment
- [x] Install dependencies (textual>=0.40.0, rich>=13.0.0) 
    (verified with ./venv/bin/pip list | grep -E "(textual|rich)")

- [x] Configure git repository with .gitignore
- [x] Create main.py entry point
- **Checkpoint:** `python main.py` runs without errors

### **Milestone 1.1.2: Base Data Structures (Day 2)**
- [x] Implement World dataclass with type hints
- [x] Implement Hex dataclass with coordinates and biome
- [x] Implement Character base class with D&D 5e stats
- [x] Implement Item base class with weight and properties
- [x] Create utility classes (Dice, Coordinates)
- **Checkpoint:** All dataclasses instantiate correctly

### **Milestone 1.1.3: Testing Framework (Day 3)**
- [ ] Install pytest and pytest-cov
- [ ] Create test directory structure
- [ ] Write first test (dice rolling with seeded RNG)
- [ ] Set up test coverage tracking (target >60%)
- [ ] Configure CI-friendly test runner
- **Checkpoint:** `pytest` runs and reports coverage

---

## Milestone 1.2: Character System & D&D Mechanics (Days 4-8)

### **Milestone 1.2.1: Character Creation (Days 4-5)**
- [x] Implement Race class with ability bonuses and traits
- [x] Implement CharacterClass with hit dice and proficiencies
- [x] Create character creation flow (race → class → stats)
- [x] Implement standard array stat allocation (15,14,13,12,10,8)
- [x] Load race/class data from JSON files
- [x] Generate starting equipment based on class
- **Checkpoint:** Can create valid D&D character

### **Milestone 1.2.2: Character Stats & Mechanics (Days 6-7)**
- [x] Implement ability score modifiers ((score-10)//2)
- [x] Implement skill system with proficiency bonuses
- [x] Calculate derived stats (AC, HP, proficiency bonus)
- [x] Implement saving throw calculations
- [x] Add skill check resolution (d20 + modifier + proficiency)
- **Checkpoint:** All D&D calculations match rulebook

### **Milestone 1.2.3: Character Progression (Day 8)**
- [x] Implement XP tracking and level thresholds
- [x] Implement leveling system (levels 1-5)
- [x] Calculate HP increase on level up (hit die + CON mod)
- [x] Scale proficiency bonus by level (+2 at 1st, +3 at 5th)
- [x] Add basic feat support framework
- **Checkpoint:** Character can level from 1 to 5 correctly

---

## Milestone 1.3: Inventory & Equipment System (Days 9-11)

### **Milestone 1.3.1: Equipment Slots (Days 9-10)**
- [x] Implement Equipment class with 9 slots (head, body, hands, feet, main_hand, off_hand, ring_1, ring_2, amulet)
- [x] Implement equip/unequip logic with validation
- [x] Calculate AC from equipped armor and shields
- [x] Apply stat bonuses from magical items
- [x] Handle two-handed weapon restrictions
- **Checkpoint:** Can equip items and see AC changes

### **Milestone 1.3.2: Inventory Management (Day 11)**
- [x] Implement Inventory class with weight tracking
- [x] Enforce encumbrance limits based on Strength
- [x] Implement item stacking for consumables
- [x] Add container items (backpack increases capacity)
- [ ] Create item durability system
- **Checkpoint:** Inventory respects weight limits and stacking

---

## Milestone 1.4: Basic UI Implementation (Days 12-14)

### **Milestone 1.4.1: Main Layout (Day 12)**
- [x] **UI:** Create Textual app with three-panel layout
- [x] **UI:** Implement Character panel (25% width) with real-time stats
- [x] **UI:** Implement Game Log panel (50% width) with scrolling
- [ ] **UI:** Implement POI panel (25% width) with nearby locations
- [ ] **UI:** Style panels with borders and colors
- **Checkpoint:** Three-panel layout displays correctly

### **Milestone 1.4.2: Modal Screens (Day 13)**
- [ ] **UI:** Create InventoryScreen modal with equipment display
- [ ] **UI:** Implement CharacterScreen modal with full stats
- [ ] **UI:** Add keyboard bindings (I=inventory, C=character, ESC=close)
- [ ] **UI:** Ensure modals don't affect game log
- [ ] **UI:** Test modal navigation and closing
- **Checkpoint:** Can open/close inventory and character screens

### **Milestone 1.4.3: Command System (Day 14)**
- [ ] **UI:** Implement command parser with natural language support
- [ ] **UI:** Add command history (up/down arrows)
- [ ] **UI:** Implement basic commands: look, help, quit
- [ ] **UI:** Add abbreviated command support ("i" for inventory)
- [ ] **UI:** Display command feedback in game log
- **Checkpoint:** Commands work and appear in log

---

## Milestone 1.5: World Generation Framework (Days 15-17)

### **Milestone 1.5.1: Macro World Generation (Day 15)**
- [ ] Implement heightmap generation using Perlin noise
- [ ] Calculate climate zones based on latitude
- [ ] Assign biomes using height + climate lookup tables
- [ ] Place 3 major landmarks (cities, ruins, dungeons)
- [ ] Create 2 civilizations with basic history
- **Checkpoint:** 100x100 world generates in <30 seconds

### **Milestone 1.5.2: Biome System (Day 16)**
- [ ] Create 3 biome JSON files (temperate_forest.json, plains.json, mountains.json)
- [ ] Implement biome data loader with caching
- [ ] Define terrain types and movement costs per biome
- [ ] Define natural features per biome (rivers, caves, etc.)
- [ ] Create location spawn probability tables
- **Checkpoint:** Biomes load correctly and affect terrain

### **Milestone 1.5.3: Hex Generation (Day 17)**
- [ ] Implement on-demand hex generation when player enters
- [ ] Use seeded RNG for deterministic results (same seed = same world)
- [ ] Generate terrain features based on biome and elevation
- [ ] Connect to neighboring hexes for continuity
- [ ] Test: verify same seed produces identical world
- **Checkpoint:** Hex generation is deterministic and fast (<100ms)

---

## Milestone 1.6: Save System (Days 18-19)

### **Milestone 1.6.1: Database Schema (Day 18)**
- [ ] Design SQLite schema for game saves (5 tables minimum)
- [ ] Implement database connection and migration system
- [ ] Create save slot management (multiple saves)
- [ ] Add save file integrity checks and validation
- [ ] Implement backup save system
- **Checkpoint:** Database creates and migrates correctly

### **Milestone 1.6.2: Save/Load Implementation (Day 19)**
- [ ] Implement save_game() with complete state serialization
- [ ] Implement load_game() with state restoration
- [ ] Save player character, inventory, and position
- [ ] Save explored hexes and world state
- [ ] Test save/load with mock data
- **Checkpoint:** Can save, quit, reload, and continue game

---

## Risk Mitigation Strategies

### Technical Risks

**Risk: World generation takes >30 seconds**
- **Mitigation:** Profile early (Week 2), optimize algorithm if needed
- **Fallback:** Reduce world size to 50x50 for MVP
- **Detection:** Performance test in Task 1.5

**Risk: UI feels sluggish or unresponsive**
- **Mitigation:** Test on minimum terminal size (80x24), optimize rendering
- **Fallback:** Simplify UI layout, reduce real-time updates
- **Detection:** Manual testing on different terminals

**Risk: Save file corruption or data loss**
- **Mitigation:** Implement backup saves, integrity checks
- **Fallback:** Manual save export/import
- **Detection:** Stress testing in Week 3

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
- World generation and hex exploration
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
- [ ] World generation determinism (same seed = same result)

### **Integration Tests:**
- [ ] Character creation → stat display → save
- [ ] Equip item → recalculate AC → save → load → verify AC
- [ ] World generation → hex generation → verify consistency
- [ ] UI modal flow: open inventory → equip item → close → verify changes

### **Manual Testing:**
- [ ] Create 10 different character builds (all race/class combinations)
- [ ] Generate 3 worlds with different seeds, verify uniqueness
- [ ] Verify save/load across multiple sessions
- [ ] Test UI on different terminal sizes (80x24 minimum)
- [ ] Performance test: world generation under 30 seconds

### **Testing Exit Criteria:**
- All unit tests passing with >60% coverage
- Can create character, explore 5 hexes, save, quit, reload, continue
- No memory leaks after 30-minute session
- UI responsive on 80x24 terminal
- World generation completes in <30 seconds

---

## Success Criteria

### **Foundation Complete When:**
- [ ] Character creation with 4 races, 4 classes working
- [ ] Equipment system with AC calculation functional
- [ ] Inventory with weight tracking operational
- [ ] Three-panel UI with modal screens working
- [ ] World generation creates 100x100 hex world
- [ ] Save/load preserves all character and world state
- [ ] All tests passing with >60% coverage

### **Quality Benchmarks:**
- [ ] Character creation completes in <5 seconds
- [ ] World generation completes in <30 seconds
- [ ] UI commands respond in <100ms
- [ ] Save/load operations complete in <2 seconds
- [ ] Memory usage stable during extended play

### **Deliverable Verification:**
- [ ] Can create character → explore world → save → reload → continue
- [ ] All D&D mechanics calculate correctly per rulebook
- [ ] UI is clear and navigable with keyboard only
- [ ] Code is documented with type hints throughout