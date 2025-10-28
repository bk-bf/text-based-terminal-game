# Fantasy RPG Integration - Implementation Tasks

## Overview

Connect all existing foundation systems through a GameEngine coordinator layer. All backend systems exist and work - they need proper orchestration to create a cohesive gameplay experience.

**Dependencies:** Completed foundation systems (character, world, UI, save/load)  
**Estimated Time:** 1 week (7 days)  
**Goal:** Playable game loop from character creation to survival gameplay

---

## Implementation Tasks

### 1. GameEngine Foundation
Create the central coordinator that ties all existing systems together.

- [x] 1.1 Create `fantasy_rpg/game/game_engine.py` with GameEngine class
  - Implement GameState dataclass for complete game state
  - Add world initialization through existing WorldCoordinator
  - Connect to existing character and player state systems
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 1.2 Implement new_game() method
  - Initialize world through existing world generation
  - Place character in starting hex with proper state
  - Set up initial environmental conditions
  - _Requirements: 1.1, 1.4_

- [x] 1.3 Test GameEngine initialization
  - Verify world generation works through GameEngine
  - Test character placement and initial state
  - Validate all systems are properly connected
  - _Requirements: 1.1, 1.2_

### 2. Movement System Integration
Connect movement commands to existing world and survival systems.

- [x] 2.1 Implement move_player() method in GameEngine
  - Connect to existing WorldCoordinator for hex validation
  - Apply environmental effects using existing survival mechanics
  - Update time and weather through existing systems
  - _Requirements: 2.1, 2.2, 2.3, 2.5_

- [x] 2.2 Connect movement to action handler
  - Update existing action handler to use GameEngine
  - Route movement commands through GameEngine coordinator
  - Implement proper error handling for invalid moves
  - _Requirements: 2.4, 2.5_

- [x] 2.3 Test movement with environmental effects
  - Verify survival stats change during travel
  - Test weather effects on movement
  - Validate natural language feedback   // TODO: could be improved
  - _Requirements: 2.1, 2.2, 2.3, 2.5_

### 3. Location System Integration
Connect location exploration to existing location generation and foraging systems.

- [x] 3.1 Implement location entry/exit methods
  - Connect to existing LocationGenerator
  - Implement persistent location data storage
  - Add location state management for re-entry
  - _Requirements: 3.1, 3.2, 3.5_

- [x] 3.2 Connect object interaction system
  - Link to existing action system
  - Implement context-specific object commands //TODO: extend commands result, eg. many different outcomes for harvest, cut, unlock
  - Connect to existing inventory system for resource gathering
  - _Requirements: 3.3, 3.4, 3.5_

- [x] 3.3 Test location exploration flow
  - Verify location persistence across entry/exit
  - Ensure movement between locations is functional
  - Test object discovery and interaction
  - Validate resource gathering integration
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

// TODO: action system isnt as sophisticated as desired, should be improved

### 4. UI System Integration
Connect GameEngine to existing UI framework for state synchronization.

- [x] 4.1 Update UI to use GameEngine
  - Modify existing app.py to initialize GameEngine
  - Launch game with debug seed and debug character 
  - Update UI panels to display GameEngine state
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 4.2 Implement UI state synchronization
  - Add GameEngine state change notifications
  - Update existing panels when game state changes
  - Ensure all displays show current information
  - _Requirements: 5.1, 5.3, 5.5_

- [ ] 4.3 Test complete UI integration
  - Verify character creation → game start flow
  - Test UI updates during gameplay
  - Validate natural language output consistency
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

### 5. Logging System Integration
Fix duplicate logging and ensure single source of truth for messages.

- [ ] 5.1 Create centralized game logger
  - Implement single logger for all game messages
  - Replace existing duplicate logging calls
  - Add message type handling and queuing
  - _Requirements: 6.1, 6.2, 6.4_

- [ ] 5.2 Ensure natural language output
  - Convert all numerical outputs to descriptive text
  - Maintain HP/AC as numbers, everything else descriptive
  - Fix weather and survival status displays
  - _Requirements: 6.3, 6.5_

- [ ] 5.3 Test logging system
  - Verify no duplicate messages
  - Test message flow during gameplay
  - Validate natural language consistency
  - _Requirements: 6.1, 6.2, 6.3_

### 6. Save/Load Integration
Connect GameEngine to existing save system for complete game state persistence.

- [ ] 6.1 Implement complete game state save/load
  - Extend existing save system to include world state
  - Add GameEngine state serialization
  - Implement world persistence across sessions
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 6.2 Test save/load functionality
  - Verify complete state preservation
  - Test world persistence after load
  - Validate seamless game continuation
  - _Requirements: 7.1, 7.2, 7.4, 7.5_

### 7. Integration Testing & Polish
Ensure all systems work together smoothly for complete gameplay experience.

- [ ] 7.1 Complete gameplay loop testing
  - Test character creation → world exploration → survival mechanics
  - Verify all systems coordinate properly through GameEngine
  - Fix any remaining integration bugs
  - _Requirements: All requirements_

- [ ] 7.2 Performance optimization
  - Optimize GameEngine coordination overhead
  - Ensure smooth UI updates during gameplay
  - Test extended play sessions for stability
  - _Requirements: All requirements_

- [ ] 7.3 Final polish and bug fixes
  - Fix any remaining issues discovered during testing
  - Polish natural language output
  - Ensure consistent user experience
  - _Requirements: All requirements_

---

## Success Criteria

### Integration Complete When:
- [ ] GameEngine coordinates all existing systems seamlessly
- [ ] Character creation leads to playable world exploration
- [ ] Movement between hexes works with environmental consequences
- [ ] Location exploration connects to foraging and survival
- [ ] UI displays current game state accurately
- [ ] Save/load preserves complete game state including world
- [ ] Natural language output used throughout (except HP/AC)
- [ ] Can play complete gameplay loop for 30+ minutes without issues

### Quality Benchmarks:
- [ ] GameEngine initialization completes in <3 seconds
- [ ] Movement commands respond in <200ms
- [ ] UI updates smoothly during state changes
- [ ] Save/load operations complete in <5 seconds
- [ ] No duplicate messages in game log
- [ ] All survival mechanics work through GameEngine coordination

This implementation plan leverages all existing foundation work and focuses purely on the integration layer needed to create a cohesive gameplay experience.