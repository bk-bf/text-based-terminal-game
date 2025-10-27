# Ultimate Fantasy Sim - Development Guide

## Core Vision & Gameplay

### Two-Layer World Structure

#### Overworld Hex Map (Deadly Travel)
- Large hex grid where each hex = 3-5 square miles
- Travel time: 1-4 hours per hex depending on terrain/weather
- **DEADLY EXPOSURE**: Continuous hunger/thirst/temperature effects
- **NO SURVIVAL ACTIONS**: Cannot forage/camp while traveling
- Player actions: Move north/south/east/west, enter locations, view inventory
- Environmental hazards: Hypothermia, heat stroke, exhaustion, death

#### Location-Based Exploration (Detailed Interaction)
- 5-20 locations per hex (50+ for settlements)
- **PERSISTENT GENERATION**: Same locations on re-entry
- Connected areas within each location
- **CONTEXT-SPECIFIC INTERACTIONS**: Examine berry bush → harvest berries
- **SKILL-BASED DISCOVERY**: Hidden content revealed by perception checks
- All survival actions happen here: forage, camp, search, combat, NPC interaction

### Core Gameplay Loop

1. **Spawn in wilderness hex** with minimal supplies
2. **Enter location** to escape deadly overworld exposure
3. **Discover objects** through automatic perception checks
4. **Interact with specific objects** to gather resources
5. **Critical Choice**: Seek civilization OR master wilderness survival

### Success Criteria

Player can:
1. Create character and start in wilderness hex
2. Move between hexes with deadly environmental effects
3. Enter locations to escape exposure and gather resources
4. Discover hidden objects through skill-based perception
5. Choose between civilization safety and wilderness independence
6. Experience permadeath with persistent world state
7. See all feedback in natural language (except HP/AC numbers)

## Development Philosophy

### Integration Over Development

**STOP building new systems. START connecting existing systems through GameEngine.**

All backend systems exist:
- ✅ World generation (terrain, climate, biomes, weather)
- ✅ Character creation and progression
- ✅ Survival mechanics (hunger, thirst, temperature)
- ✅ Location generation templates
- ✅ Item and equipment systems

**Missing**: GameEngine coordinator layer to tie them together

### Code Simplicity
- All game state flows through GameEngine - single source of truth
- No direct UI-to-backend communication
- Use existing classes as-is, don't refactor working systems
- Focus on coordinator layer that ties systems together

### Immediate Purpose
- Every line must serve integration, not future features
- Connect existing Character, WorldCoordinator, PlayerState through GameEngine
- Don't build new systems when integration is the priority
- Test integration immediately through gameplay

## Natural Language Philosophy

### NEVER Show:
- Numerical hunger/thirst values ("65/100 hunger")
- Precise temperatures ("32°F" → "freezing cold")
- Exact distances ("3.2 miles" → "a few miles")
- Percentage indicators for survival needs
- Precise time increments ("+15 minutes" → "some time passes")

### ALWAYS Show:
- Descriptive states (Well-fed, Hungry, Starving)
- Natural weather descriptions (Heavy rain with strong winds)
- Relative time (Late afternoon, spring)
- Immersive environmental descriptions

## Integration Flow
```
User Input → ActionHandler → GameEngine → Backend Systems → GameEngine → UI Update
```

All coordination through GameEngine. No shortcuts.