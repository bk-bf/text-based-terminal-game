# Historical Figures System

## Overview

The historical figures system generates legendary heroes and villains tied to mythic events, creating a rich cultural foundation for the game world. These figures form the basis for future genealogical systems, NPC generation, and quest creation.

## Architecture

### Core Components

1. **HistoricalFigure Dataclass** (`fantasy_rpg/world/historical_figures.py`)
   - Complete biographical data (name, title, race, alignment, archetype)
   - Genealogical tracking (parents, spouse, children)
   - Historical impact (events, achievements, artifacts, cultural significance)
   - Personality and backstory

2. **Generation System** (`generate_historical_figures()`)
   - Creates 1-3 figures per mythic event based on significance
   - Weighted 65% heroes, 35% villains
   - Assigns figures to events as protagonists/antagonists
   - Generates simple parent-child relationships (20% of figures)

3. **Integration Points**
   - WorldCoordinator: Generates figures automatically during world creation
   - MythicEvents: Figures assigned to events as participants
   - SaveManager: Complete serialization/deserialization support

## Data Structure

```python
@dataclass
class HistoricalFigure:
    id: str                                    # "figure-001"
    name: str                                  # "Thorin Ironforge"
    title: str                                 # "the Bold"
    race: str                                  # "dwarf"
    alignment: str                             # "hero" or "villain"
    archetype: str                             # "warrior_hero", "dark_sorcerer", etc.
    
    # Genealogy
    birth_year: int                            # Negative = years before present
    death_year: Optional[int]                  # None = unknown/mythic
    parents: Optional[Tuple[str, str]]         # (mother_id, father_id)
    spouse: Optional[str]                      # Spouse figure ID
    children: List[str]                        # Child figure IDs
    
    # Historical Impact
    participated_in_events: List[str]          # Event IDs
    achievements: List[str]                    # Notable deeds
    artifacts_owned: List[str]                 # Artifact IDs
    cultural_significance: int                 # 1-10 scale
    
    # Biographical
    backstory: str
    personality_traits: List[str]
    cultural_origin: str
```

## Archetypes

### Heroes (6 types)
- **warrior_hero**: Martial prowess, battles, protection
- **wise_elder**: Knowledge, guidance, cultural memory
- **cunning_strategist**: Planning, diplomacy, clever victories
- **noble_ruler**: Leadership, justice, unification
- **wandering_prophet**: Spiritual insight, prophecy, warnings
- **master_craftsman**: Creation, innovation, legendary works

### Villains (6 types)
- **tyrant_conqueror**: Brutal conquest, oppression
- **dark_sorcerer**: Forbidden magic, corruption
- **treacherous_noble**: Betrayal, manipulation, backstabbing
- **cult_leader**: Religious extremism, fanaticism
- **plague_bringer**: Disease, destruction, chaos
- **usurper_king**: Illegitimate rule, stolen throne

## Generation Process

### 1. Figure Count Determination
```python
# Based on mythic event significance
if significance >= 8: num_figures = 2-3  # Major events
elif significance >= 5: num_figures = 1-2  # Moderate events
else: num_figures = 1  # Minor events

# Capped at 2× event count
```

### 2. Figure Creation
For each event:
- Determine alignment (65% hero, 35% villain)
- Select archetype from appropriate list
- Choose race with weighted distribution (40% human, 25% elf, 20% dwarf, 15% halfling)
- Generate name and title based on race
- Calculate birth/death years relative to event
- Assign personality traits matching alignment

### 3. Event Connection
- Figure added as event participant
- Achievement generated based on role and event type
- Artifacts from event assigned to protagonist/antagonist

### 4. Genealogy Generation
- 20% of figures assigned parents (same race, compatible ages)
- Parent-child age gap: 20-60 years
- Spouses assigned when creating parent pairs

## Integration with Game Systems

### World Generation
```python
# In WorldCoordinator._generate_mythic_events()
self.mythic_events = generate_mythic_events(self, num_events=10, seed=self.seed)
self._generate_historical_figures()  # Called automatically

# Figures added to events as participants
for figure in self.historical_figures:
    for event_id in figure.participated_in_events:
        event['participants'].append({
            'id': figure.id,
            'name': f"{figure.name} {figure.title}",
            'role': figure.alignment,
            'archetype': figure.archetype
        })
```

### Save/Load System
```python
# In SaveManager
def _serialize_world_data(self):
    return {
        "mythic_events": self.game_engine.world_coordinator.mythic_events,
        "historical_figures": [f.to_dict() for f in figures]
    }

def _deserialize_world_data(self, data):
    self.world_coordinator.historical_figures = [
        HistoricalFigure.from_dict(fig_data) 
        for fig_data in data["historical_figures"]
    ]
```

## In-Game Research Commands

Players can research historical information using the `research` command:

```
research events          # View all mythic events
research figures         # View all historical figures
research heroes          # View only heroes
research villains        # View only villains
research artifacts       # View legendary artifacts
```

Example output:
```
=== LEGENDARY HEROES (12) ===

Aldric Ironheart the Bold
  Race: Human
  Role: Hero (Warrior Hero)
  Born: Year -734
  Died: Year -689
  Significance: 9/10
  Traits: Brave, Honorable, Determined
  Story: Aldric Ironheart the Bold rose to prominence through martial 
         prowess and unwavering courage in battle. Their role in the 
         legendary events shaped the course of civilization.
  Achievements:
    • Led forces to victory in The Broken Crown
    • Defended the realm against countless threats
  Artifacts: ancestors_blade
```

## Testing

### Test Suite
Run `python tests/test_historical_figures.py` to verify:

1. **Basic Generation**: Figures created from mythic events
2. **Figure Details**: Complete biographical data
3. **Event Integration**: Figures properly connected to events
4. **Genealogy**: Parent-child relationships functional
5. **Serialization**: Save/load preserves all data
6. **World Integration**: Seamless integration with world generation

### Expected Results
- 15-25 figures per world (typical 10 event world)
- ~65% heroes, ~35% villains
- ~20% of figures have genealogical connections
- All figures have complete biographical data
- Event participants properly linked

## Future Extensions

### Phase 2: Cultural Memory System (Task 2.2)
- Add significance tracking for how figures are remembered
- Implement hero/villain categorization by civilization
- Create cultural influence mechanics affecting NPC attitudes

### Phase 3: NPC Generation (Task 5.1)
- Generate NPCs as descendants of historical figures
- Derive NPC motivations from ancestral history
- Family feuds and alliances based on historical connections

### Phase 4: Quest Generation (Task 6.1-6.3)
- Artifact recovery quests for lost legendary items
- Family honor restoration based on genealogy
- Historical mystery investigations

## Implementation Notes

### Performance
- Generation happens during world creation (~100ms for 20 figures)
- No runtime overhead after generation
- Full serialization adds ~10KB to save file

### Memory Efficiency
- Figures stored as dataclasses (efficient Python representation)
- Genealogy uses ID references, not nested objects
- Events store participant summaries, not full figure data

### Extensibility
- Easy to add new archetypes (update HERO_ARCHETYPES/VILLAIN_ARCHETYPES)
- Name patterns extensible for new races (update NAME_PATTERNS)
- Achievement templates support new event types
- Genealogy system ready for multi-generation expansion

## Data Files

### Generated Data
- `fantasy_rpg/data/historical_figures.json` (optional save)
  - Complete figure data in JSON format
  - Can be loaded separately from world save
  - Useful for debugging and content design

### Templates Used
- `fantasy_rpg/data/mythic_event_templates.json` - Event archetypes
- `fantasy_rpg/data/legendary_artifacts.json` - Artifact definitions
- `fantasy_rpg/data/races.json` - Race name patterns

## Design Philosophy

The historical figures system follows the project's core principles:

1. **Data-Driven**: All content defined in configuration data, not hardcoded
2. **Emergent Narrative**: Figures generated procedurally create unique stories each game
3. **Integration-First**: Built to slot into existing world generation seamlessly
4. **Natural Language**: Research output uses descriptive text, not raw data dumps
5. **Genealogy Foundation**: Simple parent-child system ready for expansion

The system provides immediate value (enriched world lore) while laying groundwork for future social systems (NPC generation, quest creation, dynamic world history).
