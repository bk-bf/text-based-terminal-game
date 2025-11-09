# Fantasy RPG - AI Coding Instructions

## Project Overview
Text-based fantasy RPG combining D&D 5e mechanics with survival gameplay in a procedurally generated world. Built with Python/Textual UI, featuring a two-layer world system (hex-based overworld + detailed locations).

**Vision** (See `.kiro/steering/fantasy-rpg-development-guide.md`):
- **Deadly overworld travel** (1-4 hours/hex, continuous exposure damage, NO survival actions)
- **Safe location exploration** (5-20 locations/hex, context-specific interactions, skill-based discovery)
- **Core loop**: Spawn in wilderness → Enter locations → Discover resources → Choose civilization vs. wilderness mastery
- **Natural language only**: No numerical displays except HP/AC (e.g., "Hungry" not "65/100 hunger")

## Natural Language Philosophy

### NEVER Display:
- Numerical hunger/thirst/fatigue values ("65/100 hunger")
- Precise temperatures ("32°F" → use "freezing cold")
- Exact distances ("3.2 miles" → use "a few miles")
- Percentage indicators for survival needs
- Precise time increments ("+15 minutes" → use "some time passes")

### ALWAYS Display:
- Descriptive states: "Well-fed", "Hungry", "Starving"
- Natural weather: "Heavy rain with strong winds"
- Relative time: "Late afternoon, spring"
- Immersive environmental descriptions

## Architecture: The Three-Layer Separation

### 1. GameEngine (Core Coordinator)
**File**: `fantasy_rpg/game/game_engine.py`
- **Single source of truth** for all game state
- Manages: WorldCoordinator, TimeSystem, PlayerState, Character
- NEVER duplicate state management - always go through GameEngine
- Provides `get_action_handler()` for command processing

### 2. Input → Action → Logger Flow
**Critical Pattern**: Commands flow in ONE direction only
```
UI Input → InputController → ActionHandler → ActionLogger → UI Display
```

- **InputController** (`actions/input_controller.py`): Receives raw commands, routes to GameEngine
- **ActionHandler** (`actions/action_handler.py`): Executes actions, returns `ActionResult` objects
- **ActionLogger** (`actions/action_logger.py`): Formats results for display (natural language, dice rolls, time passage)

**Never bypass this flow** - don't log directly from ActionHandler or execute actions from UI.

### 3. UI Presentation (Textual)
**File**: `fantasy_rpg/ui/app.py`
- Three-panel interface: CharacterPanel (left), GameLogPanel (center), POIPanel (right)
- Displays formatted output from ActionLogger
- Handles UI callbacks (`show_inventory`, `show_character`, etc.)
- See `fantasy_rpg/ui/README.md` for UI architecture details

## Critical Time System Pattern

**MANDATORY**: All time-passing actions MUST use `time_system.perform_activity()`:

```python
# ✅ CORRECT - TimeSystem handles survival effects
time_result = self.game_engine.time_system.perform_activity("rest", duration_override=2.0)
return ActionResult(success=True, message="You rest", time_passed=2.0)

# ❌ WRONG - Bypasses survival/weather/condition effects
return ActionResult(success=True, message="You rest", time_passed=2.0)
```

**Why**: `perform_activity()` applies hunger/thirst/temperature/condition damage during time passage. Without it, characters can survive indefinitely without consequences.

See: `fantasy_rpg/game/time_system.py` for activity definitions and `fantasy_rpg/actions/action_handler.py` line 7 for documentation.

## Data-Driven Design (CDDA-Style)

### JSON Structure
All game content lives in `fantasy_rpg/data/*.json` with weighted spawning:
- `locations.json`: Location templates with area layouts
- `objects.json`: Interactive objects with item_drops and pools
- `items.json`: Items with properties, pools for categorization
- `entities.json`: NPCs/creatures with stats and loot

### Pool System
Objects/items use **pools** for flexible spawning:
```json
"item_drops": [
    {
        "pool": "treasure",  // Spawn from treasure pool
        "chance": 0.3,
        "quantity": {"min": 1, "max": 3}
    }
]
```

**When adding content**: Always assign appropriate pools, don't hardcode spawn locations.

## World Generation Architecture

### Two-Layer World System

**Overworld** (`world/world_coordinator.py`):
- Hex-based grid (default 20×20)
- Generated at game start: terrain → biomes → climate → locations
- Each hex contains 5-20 location templates
- Movement between hexes is SLOW (1-4 hours) and DEADLY (exposure kills)

**Locations** (`locations/location_generator.py`):
- Generated from JSON templates when first entered
- Persistent: saved state on re-entry
- Multi-area layouts with exits (n/s/e/w)
- Contains objects, items, entities from weighted pools
- Movement between locations is FAST (30 min) and SAFE

### Known Issue: Premature World Generation
**DO NOT create GameEngine before user chooses New/Load game** - see `world-loading-issue-report.md` for detailed analysis. World generation happens in `WorldCoordinator.__init__()`, which triggers on `GameEngine.new_game()`.

## Character & Survival Systems

### Character (`core/character.py`)
- D&D 5e implementation: abilities, skills, proficiency_bonus, XP thresholds
- Equipment system: 9 slots (mainhand, offhand, armor, etc.)
- Inventory: separate from equipped items

### PlayerState (`game/player_state.py`)
- Survival tracking: hunger (0-1000), thirst (0-1000), fatigue (0-1000)
- Temperature regulation: body_temperature, warmth, wetness, wind_chill
- Natural language feedback: no raw numbers shown to player
- Condition effects: applied through TimeSystem during activities

## Development Workflows

### Running the Game
```bash
python play.py          # Recommended launcher
./play.sh              # Shell script alternative
```

### Dependencies
```bash
pip install -r requirements.txt  # textual>=0.40.0, rich>=13.0.0
```

### Save System
- Autosaves to `save.json` at project root
- Full game state: character, world, time, weather
- Load on startup with modal confirmation

### Debug Commands
Available in-game (see `InputController.debug_commands`):
- `heal` / `h`: Restore HP
- `damage` / `hurt`: Reduce HP
- `xp` / `experience`: Add XP
- `dump_log`: Save game log to file
- `save` / `load`: Manual save/load

## Common Patterns

### Adding New Actions
1. Add to `ActionHandler.action_registry` with handler method
2. Create handler: `def handle_new_action(self, args) -> ActionResult`
3. If time passes: call `time_system.perform_activity()`
4. Return `ActionResult` with message, time_passed, and any data
5. ActionLogger handles formatting automatically

### Adding New Location Types
1. Add template to `data/locations.json` under appropriate category
2. Define areas with descriptions, exits, terrain
3. Reference object/entity/item pools for spawning
4. LocationGenerator handles instantiation automatically

### Adding New Items/Objects
1. Add to `data/items.json` or `data/objects.json`
2. Assign to pools for categorization (e.g., "treasure", "food", "weapons")
3. Define properties for game mechanics
4. Items auto-spawn through pool references in locations/objects

## Code Conventions

### Import Patterns
Due to circular dependency avoidance:
- Use late imports in `GameEngine` (import inside methods, not module level)
- Type hints use `Any` for Character/PlayerState in cross-module contexts
- See `game_engine.py` lines 1-30 for circular import handling

### Error Handling
- ActionResult for standardized success/failure
- ActionLogger queues messages when UI unavailable
- GameEngine provides safe fallbacks for uninitialized systems

### File Organization
```
fantasy_rpg/
├── actions/      # Command processing (InputController, ActionHandler, ActionLogger)
├── core/         # Character, inventory, D&D mechanics
├── game/         # GameEngine, time, survival, save system
├── world/        # World generation, weather, biomes, climate
├── locations/    # Location generation from templates
├── ui/           # Textual interface (app, screens, panels)
└── data/         # JSON game content
```

## Key Files to Reference

- `fantasy_rpg/ui/README.md`: UI architecture and responsibilities
- `world-loading-issue-report.md`: World generation data flow analysis
- `README.md`: Player-facing features and commands
- `fantasy_rpg/game/game_engine.py`: Central coordinator patterns
- `fantasy_rpg/actions/action_handler.py`: Command processing examples

## Testing & Development Workflow

### Manual Testing Philosophy (See `.kiro/steering/development-workflow.md`)
**NO automated testing** - test by playing the game:
1. Start game with `python play.py`
2. Create character (quick or interactive)
3. Test commands in both overworld and locations
4. Verify time passage triggers survival effects
5. Check save/load preserves state correctly

**NEVER**:
- Use `executeBash` or run commands automatically
- Create automated test suites (pytest, unit tests)
- Add build automation (Makefiles, CI/CD)
- Execute terminal commands without user approval
- Generate .md documentation files unless explicitly requested by the user

**ALWAYS**:
- Propose commands for user to run manually
- Wait for user to provide output before proceeding
- Test integration by actually playing the game
- Include verification print statements in code
- Fix code first, document only when asked

### Integration Over New Development
**STOP building new systems. START connecting existing ones.**

Focus on GameEngine integration:
- All backend systems already exist (world, character, survival, locations)
- Priority is coordinator layer, not new features
- Every line must serve immediate integration needs
- Test integration through gameplay immediately

## Condition System Rules (See `.kiro/steering/condition-system-rules.md`)

### Complete Self-Containment
**CRITICAL**: Every condition MUST be completely self-contained in JSON:

```json
{
  "Wet": {
    "description": "Wet clothing causes discomfort",
    "trigger": "wetness >= 200 AND wetness < 350",
    "effects": {
      "dexterity_modifier": -1,
      "cold_vulnerability": true
    },
    "interactions": {
      "with_cold_conditions": {
        "additional_effects": {"constitution_modifier": -1},
        "description": "Wet clothing in cold weather increases heat loss"
      }
    },
    "severity": "mild",
    "category": "wetness"
  }
}
```

**NEVER**:
- Scatter condition logic across multiple files
- Create external interaction tables
- Duplicate condition definitions
- Use condition-specific hardcoded interactions

**ALWAYS**:
- Define ALL effects within the condition itself
- Use generic interaction rules (e.g., "with_cold_conditions")
- Single source of truth - each condition appears exactly once
- All condition logic traceable to one definition
