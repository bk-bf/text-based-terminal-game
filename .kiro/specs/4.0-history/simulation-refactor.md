# Historical Simulation System - Complete Refactor

## Overview

Replace fake year-loop simulation with TRUE day-by-day simulation using TimeSystem. Build world generation UI showing live progress as history unfolds from civilization founding (~802) to game start (1452).

**Problem:** Current implementation loops through years with random events - no real time progression, no actual probability mechanics, no TimeSystem usage.

**Dependencies:** TimeSystem, WeatherSystem, Character dataclasses, WorldCoordinator  
**Estimated Time:** 7-10 days  
**Goal:** Real historical simulation with live UI feedback and condition-based events

---

## Implementation Tasks

### 1. World Generation UI System
Create full-screen modal showing live simulation progress during world creation.

- [ ] 1.1 Create WorldGenerationScreen
  - Implement `fantasy_rpg/ui/world_generation_screen.py`
  - Full-screen Textual modal with progress display
  - Shows: current year, progress bar, civilization count, living figures, event count
  - Real-time updates as simulation runs
  - _Priority: HIGH - build this first to see what's happening_

- [ ] 1.2 Design progress display layout
  - Progress bar showing year/total (e.g., 1156/1452)
  - Statistics panel: civilizations, figures, events
  - Scrolling recent events list (last 10 events)
  - Estimated time remaining calculation
  - _UI mockup in requirements section below_

- [ ] 1.3 Implement simulation callbacks
  - Callback system for year-by-year updates
  - Non-blocking UI updates (don't slow simulation)
  - Progress estimation based on elapsed time
  - Event queue for recent events display
  - _Callback every sim-year to update UI_

- [ ] 1.4 Integrate with GameEngine
  - Show WorldGenerationScreen in GameEngine.new_game()
  - Pass simulation reference for live updates
  - Return to main game screen after completion
  - Handle user cancellation (if desired)
  - _Requirements: 1.1, 1.2, 1.3_

### 2. Simulation Core Infrastructure
Build real simulation using TimeSystem for day-by-day progression.

- [ ] 2.1 Create SimulationState dataclass
  - Implement `fantasy_rpg/world/simulation_state.py`
  - Contains: civilizations, figures, relationships, resources
  - Uses TimeSystem instance for time progression
  - Tracks territories, populations, diplomatic relations
  - _No year loops - only TimeSystem.advance_time()_

- [ ] 2.2 Create HistoricalSimulation coordinator
  - Implement `fantasy_rpg/world/historical_simulation.py`
  - Manages main simulation loop using TimeSystem
  - Coordinates figure behavior, events, civilization changes
  - Provides callbacks for UI updates
  - Handles simulation speed (batch time advancement)
  - _Requirements: 2.1_

- [ ] 2.3 Extend TimeSystem for simulation mode
  - Add `simulation_mode` flag to TimeSystem
  - When enabled: skip player state effects, allow faster progression
  - Support batch advancement (e.g., 30 days at once)
  - Keep all calendar/weather logic intact
  - _Requirements: 2.1_

- [ ] 2.4 Test simulation infrastructure
  - Verify TimeSystem advances correctly in simulation mode
  - Test callback system fires properly
  - Validate state tracking across time progression
  - Performance test: target <5 min for 150 years
  - _Requirements: 2.1, 2.2, 2.3_

### 3. Condition-Based Event System
Replace random event generator with real probability calculations based on simulation state.

- [ ] 3.1 Create EventProbabilityEngine
  - Implement `fantasy_rpg/world/event_probability.py`
  - Calculate daily/monthly probability for each event type
  - Based on: population, resources, relationships, geography, history
  - Example: War probability = f(territory_overlap, resource_scarcity, grudges)
  - _NO `if random() < 0.3:` - use actual conditions_

- [ ] 3.2 Implement event trigger system
  - Events happen when probabilities exceed thresholds
  - Check event conditions daily/monthly during simulation
  - Wars: territorial disputes, resource conflicts
  - Succession: ruler death from age/war
  - Disasters: tied to WeatherSystem and geography
  - Cultural movements: population happiness, prosperity
  - _Requirements: 3.1_

- [ ] 3.3 Create event consequence system
  - Events immediately affect SimulationState
  - Wars: reduce population, shift territories
  - Disasters: damage infrastructure, reduce resources
  - Successions: change leadership, affect stability
  - Cultural movements: change government/values
  - _Consequences feed back into probability calculations_

- [ ] 3.4 Test event system
  - Verify events happen for logical reasons
  - Test cause-and-effect chains
  - Validate event consequences affect future probabilities
  - Check event timing uses TimeSystem dates
  - _Requirements: 3.1, 3.2, 3.3_

### 4. Real Figure Life Simulation
Replace fake figure generation with actual life simulation using TimeSystem.

- [ ] 4.1 Create FigureLifeSimulator
  - Implement `fantasy_rpg/world/figure_life_simulator.py`
  - Figures live day-by-day using TimeSystem
  - Birth rates based on population and prosperity
  - Deaths from: old age (TimeSystem tracks), wars, disasters
  - Marriages based on age, social class, culture
  - _Requirements: 2.1_

- [ ] 4.2 Implement daily figure routines
  - Each figure has occupation, location, status
  - Rulers make civilization decisions
  - Soldiers participate in wars (casualties tracked)
  - Merchants affect trade and resources
  - All activities tied to simulation time
  - _Requirements: 4.1_

- [ ] 4.3 Create genealogy tracking
  - Track parent-child relationships as births occur
  - Record marriages with TimeSystem dates
  - Build family trees naturally over time
  - Store life events with actual calendar dates
  - _Requirements: 4.1, 4.2_

- [ ] 4.4 Test figure simulation
  - Verify birth/death rates are realistic
  - Test genealogy tracking across generations
  - Validate figure participation in events
  - Check life event dates match TimeSystem
  - _Requirements: 4.1, 4.2, 4.3_

### 5. Real Civilization Evolution
Replace fake territorial changes with resource-based expansion system.

- [ ] 5.1 Implement resource system
  - Each hex has resources: food, minerals, etc.
  - Civilizations consume resources based on population
  - Resource scarcity increases war probability
  - Prosperity affects birth rates, cultural movements
  - _Stored in SimulationState_

- [ ] 5.2 Create territorial expansion mechanics
  - Expansion happens when: population > threshold, adjacent hex available, resources sufficient
  - Contraction from: war losses, disasters, resource depletion
  - Calculate expansion probability based on actual conditions
  - NO random "civil war loses 10-30%" - real causes only
  - _Requirements: 5.1_

- [ ] 5.3 Implement diplomatic system
  - Relationships change based on events and interactions
  - Trade agreements form based on resource needs
  - Alliances form against common threats
  - Historical events create lasting bonds/grudges
  - _Requirements: 5.1, 5.2_

- [ ] 5.4 Test civilization evolution
  - Verify expansion happens for logical reasons
  - Test resource consumption affects behavior
  - Validate diplomatic relationships evolve naturally
  - Check territorial changes tracked properly
  - _Requirements: 5.1, 5.2, 5.3_

### 6. Integration & Cleanup
Connect new simulation to existing systems and remove fake code.

- [ ] 6.1 Replace fake simulation in WorldCoordinator
  - Delete `historical_events.py` (fake event generator)
  - Delete `historical_figure_simulator.py` (fake figure sim)
  - Replace `_generate_historical_events()` with `run_historical_simulation()`
  - Use HistoricalSimulation coordinator
  - _Requirements: ALL previous tasks_

- [ ] 6.2 Integrate with existing systems
  - Use existing TimeSystem for ALL time progression
  - Use existing WeatherSystem for disaster probabilities
  - Use existing Character dataclasses for figure stats
  - Reuse D&D 5e mechanics for combat/skills
  - _Requirements: 6.1_

- [ ] 6.3 Update save/load system
  - Extend save format for simulation state
  - Serialize civilizations, figures, relationships
  - Store resource states and territories
  - Maintain backward compatibility
  - _Requirements: 6.1_

- [ ] 6.4 Test integration
  - Full end-to-end world generation test
  - Verify UI shows during simulation
  - Test save/load preserves all data
  - Validate performance <5 minutes for 150 years
  - _Requirements: 6.1, 6.2, 6.3_

### 7. Performance & Validation
Optimize simulation and validate results are logical.

- [ ] 7.1 Performance optimization
  - Target: 150 years in <5 minutes
  - Batch time advancement when no events scheduled
  - Optimize event probability calculations
  - Efficient figure lifecycle updates
  - Profile and fix bottlenecks
  - _Requirements: 6.4_

- [ ] 7.2 Simulation validation
  - Verify cause-and-effect chains are logical
  - Check population growth/decline realistic
  - Validate territorial changes make sense geographically
  - Ensure genealogy tracking accurate across generations
  - Test edge cases (all figures die, civilization collapses)
  - _Requirements: 7.1_

- [ ] 7.3 UI responsiveness testing
  - Ensure UI updates don't slow simulation
  - Progress bar updates smoothly
  - Recent events scroll properly
  - Time estimation reasonably accurate
  - Handle long-running simulations gracefully
  - _Requirements: 1.4, 7.1_

---

## Success Criteria

### Real Simulation Complete When:
- [ ] Uses TimeSystem for ALL time progression (no year loops)
- [ ] Events happen based on actual conditions (not random dice)
- [ ] Figures live day-by-day with real aging and life events
- [ ] Civilizations expand/contract based on population and resources
- [ ] Wars happen for territorial or resource reasons
- [ ] Genealogy builds naturally from births/marriages over simulation time
- [ ] UI shows live progress during world generation
- [ ] Simulation completes in <5 minutes for 150 years
- [ ] Results deterministic with same seed
- [ ] Historical events reference actual TimeSystem dates

### Quality Benchmarks:
- [ ] World generation UI provides engaging feedback
- [ ] Event probability calculations use real simulation conditions
- [ ] Figure life simulation creates realistic genealogies
- [ ] Territorial changes have clear causes (war, expansion, disaster)
- [ ] Diplomatic relationships evolve based on interactions
- [ ] Performance meets <5 minute target for 150 years
- [ ] Save/load preserves complete simulation state

### Red Flags to Eliminate:
- ❌ `while year < end_year: year += 1` loops
- ❌ `if random() < 0.3:` event triggers
- ❌ Hardcoded consequences ("lose 10-30% territory")
- ❌ Figures generated without life simulation
- ❌ Events disconnected from simulation state
- ❌ No UI feedback during generation
- ❌ Time progression not using TimeSystem

---

## Architecture Overview

### Current (Broken)
```python
WorldCoordinator.__init__()
  └─> _generate_historical_events()
      └─> while year < end_year:
            if random() < 0.3:
                make_random_event()
            year += 1
```

### New (Real Simulation)
```python
WorldCoordinator.__init__()
  └─> HistoricalSimulation(callback=ui_update)
      └─> SimulationState with TimeSystem
      └─> Loop:
          ├─> time_system.advance_time(days=1)
          ├─> event_probability.check_events(state)
          ├─> figure_simulator.update_figures(state)
          ├─> civilization.update_territories(state)
          └─> callback(progress) -> UI updates
```

---

## File Structure

### New Files
```
fantasy_rpg/world/
  ├── simulation_state.py          # Core simulation state with TimeSystem
  ├── historical_simulation.py     # Simulation coordinator
  ├── event_probability.py         # Condition-based probabilities
  └── figure_life_simulator.py     # Real figure life simulation

fantasy_rpg/ui/
  └── world_generation_screen.py   # UI for world gen progress
```

### Modified Files
```
fantasy_rpg/world/
  ├── world_coordinator.py         # Use new simulation
  └── civilizations.py             # Real expansion mechanics

fantasy_rpg/game/
  ├── time_system.py              # Add simulation_mode flag
  └── game_engine.py              # Show WorldGenerationScreen

fantasy_rpg/ui/
  └── app.py                      # Handle WorldGenerationScreen
```

### Files to Delete
```
fantasy_rpg/world/
  ├── historical_events.py         # DELETE - fake event generator
  └── historical_figure_simulator.py  # DELETE - fake figure sim
```

---

## UI Mockup

```
┌─────────────────────────────────────────────────────┐
│         GENERATING WORLD - SIMULATING HISTORY       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Current Year: 1156 / 1452                         │
│  Progress: ████████████░░░░░░░░░░░░ 52%           │
│                                                     │
│  Civilizations: 7                                  │
│  Living Figures: 342                               │
│  Historical Events: 187                            │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │ Recent Events:                              │  │
│  │ • Year 1155: War declared between Aeloria  │  │
│  │   and Khaz-Modan over border dispute       │  │
│  │ • Year 1154: King Aldric III died, son    │  │
│  │   crowned as Aldric IV                     │  │
│  │ • Year 1153: Drought in southern plains   │  │
│  │   caused famine in 3 settlements           │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  Estimated time remaining: 2 minutes               │
└─────────────────────────────────────────────────────┘
```

---

## Notes

- **COMPLETE REWRITE** - delete fake simulation code entirely
- Build UI FIRST (Phase 1) so you can see what's happening
- Use TimeSystem for ALL time progression - no year loops
- Events must have real causes based on simulation state
- Performance critical - optimize batch time advancement
- Deterministic results required for reproducibility with seed
