# Fantasy RPG UI Architecture

## Purpose and Responsibilities

### App.py - Main Application Controller
**Core Purpose**: UI coordination, system initialization, and debug commands

**Responsibilities**:
- Initialize Textual UI components
- Set up game systems (player state, time system, weather)
- Route commands to appropriate handlers
- Handle debug commands (heal, damage, xp)
- Manage system callbacks (time advance, weather change)
- Coordinate UI updates (character panel, title bar)

**What it should NOT do**:
- Action logging (handled by ActionLogger)
- Action execution (handled by ActionHandler)
- Complex game logic (handled by game systems)

### ActionHandler.py - Action Execution Coordinator
**Core Purpose**: Execute actions and coordinate between systems

**Responsibilities**:
- Execute game actions (move, look, rest, etc.)
- Coordinate with time system for action results
- Gather data needed for logging
- Call ActionLogger with complete action results
- Handle action-specific logic

### ActionLogger.py - Centralized Action Logging
**Core Purpose**: Standardized, immersive action output

**Responsibilities**:
- Log all action results in consistent format
- Generate dice rolls for actions
- Track and log weather changes
- Display time passage in natural language
- Show survival warnings
- Convert technical data to natural language

**Standard Action Flow**:
1. Command executed
2. Dice rolls (if applicable)
3. Main action result
4. Time passage (natural language)
5. Weather changes (natural language)
6. Secondary effects
7. Separator

## Benefits of This Architecture

### 1. Clear Separation of Concerns
- **App**: UI and system coordination
- **ActionHandler**: Action execution
- **ActionLogger**: Consistent output

### 2. No More Redundancy
- Single source of truth for action logging
- No duplicate weather logging
- No scattered time formatting

### 3. Immersive Experience
- All actions have dice rolls
- Natural language throughout
- Consistent formatting
- Medieval-appropriate descriptions

### 4. Easy Maintenance
- Add new actions by extending ActionHandler
- Modify output format in one place (ActionLogger)
- Debug commands isolated in App

## Example Action Flow

```
User types: "look"
↓
App.process_command() → ActionHandler.handle_look()
↓
ActionHandler gathers location/weather data
↓
ActionHandler calls ActionLogger.log_action_result()
↓
ActionLogger outputs:
> look
[Perception: 15 + 2 = 17]
You look around Forest Clearing:
A peaceful clearing surrounded by ancient oaks
You observe your environment carefully.

Current weather:
The air is mild. Light breeze. Clear skies.

A few moments passes.
[~] The wind picks up.
```

## Natural Language Requirements

### Weather Descriptions
- **Temperature**: "The air is mild" (not "68°F")
- **Wind**: "Light breeze" (not "5 mph")
- **Precipitation**: "Light rain" (not "0.2 inches/hour")

### Time Descriptions
- **Duration**: "A couple of hours passes" (not "2.3 hours")
- **Time of Day**: "Afternoon, Day 1" (not "14:30")

### Dice Rolls
- **Format**: "[Perception: 15 + 2 = 17]"
- **Context**: Appropriate to action type
- **Results**: Descriptive outcomes based on roll