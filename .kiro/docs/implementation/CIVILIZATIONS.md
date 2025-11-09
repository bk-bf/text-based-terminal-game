# Civilization System

Complete implementation of Task 3.1: Civilization Archetype System

## Overview

The civilization system generates 5-8 distinct civilizations with unique cultural identities, governments, and value systems. Each civilization is associated with founding historical figures and has relationships with other civilizations.

## Architecture

### Core Components

**`fantasy_rpg/world/civilizations.py`** (~750 lines)
- `Civilization` dataclass: Complete civilization definition
- `GovernmentType` enum: 10 government types (monarchy, republic, theocracy, etc.)
- `CulturalValue` enum: 15 cultural values (honor, knowledge, wealth, etc.)
- `RelationshipLevel` enum: 6 relationship states (allied, friendly, neutral, tense, hostile, at_war)
- `generate_civilizations()`: Main generation function
- `CIVILIZATION_ARCHETYPES`: Race-specific templates for all 9 D&D races

### Data Flow

```
WorldCoordinator.generate_world()
    ↓
_generate_mythic_events() → creates historical events
    ↓
_generate_historical_figures() → creates legendary heroes/villains
    ↓
_generate_civilizations() → creates civilizations with:
    - Race-specific naming templates
    - Government types (weighted by race)
    - Cultural values (2-3 per civ)
    - Founding figures from historical_figures
    - Inter-civilization relationships
```

## Civilization Dataclass

```python
@dataclass
class Civilization:
    # Identity
    id: str
    name: str
    race: str  # One of 9 D&D races
    founded_year: int
    
    # Cultural Identity
    government_type: GovernmentType
    cultural_values: List[CulturalValue]  # 2-3 values
    religious_beliefs: str
    cultural_description: str
    
    # Historical Context
    founding_figures: List[int]  # IDs of HistoricalFigure
    major_events: List[int]
    
    # Territory & Population
    territory: Optional[Territory]
    population: int  # 50,000-500,000
    
    # Current State
    current_leader: Optional[int]
    faction_relationships: Dict[str, RelationshipLevel]
    notable_features: List[str]  # 2-4 cultural traits
```

## Race-Specific Archetypes

Each of the 9 races has unique civilization templates:

### Human Civilizations
- **Name Templates**: "{adjective} Kingdom of {place}", "The {adjective} Empire", etc.
- **Government Weights**: Monarchy (35%), Empire (25%), Republic (15%)
- **Values**: Glory, Wealth, Order, Innovation, Military Might
- **Features**: Road networks, merchant guilds, professional armies, universities

### Elf Civilizations
- **Name Templates**: "{place} Court", "The {adjective} Realm of {place}", etc.
- **Government Weights**: Monarchy (40%), Oligarchy (30%), Magocracy (20%)
- **Values**: Tradition, Nature, Magic, Knowledge, Honor
- **Features**: Tree cities, arcane masters, isolation, legendary craftsmen

### Dwarf Civilizations
- **Name Templates**: "Clan {name}", "The {place} Hold", "Kingdom Under {place}", etc.
- **Government Weights**: Clan Confederation (45%), Monarchy (35%), Oligarchy (15%)
- **Values**: Honor, Craftsmanship, Tradition, Family, Wealth
- **Features**: Underground cities, master smiths, clan hierarchy, ancient grudges

### Halfling Civilizations
- **Name Templates**: "The {place} Shire", "{adjective} Fields", etc.
- **Government Weights**: Democracy (40%), Republic (30%), Tribal Council (20%)
- **Values**: Family, Tradition, Freedom, Wealth, Nature
- **Features**: Underground homes, agriculture, hospitality, peaceful culture

### Dragonborn Civilizations
- **Name Templates**: "The {adjective} Empire of {place}", "{place} Dominion", etc.
- **Government Weights**: Empire (35%), Monarchy (30%), Military Dictatorship (20%)
- **Values**: Honor, Military Might, Glory, Tradition, Order
- **Features**: Honor codes, martial tradition, draconic reverence, breath weapon mastery

### Gnome Civilizations
- **Name Templates**: "The {place} Collective", "{adjective} Tinkertown", etc.
- **Government Weights**: Democracy (35%), Republic (30%), Magocracy (20%)
- **Values**: Innovation, Knowledge, Magic, Craftsmanship, Freedom
- **Features**: Workshop warrens, inventors, playful culture, mechanical devices

### Half-Elf Civilizations
- **Name Templates**: "The {place} Alliance", "{adjective} Haven", etc.
- **Government Weights**: Republic (35%), Democracy (30%), Oligarchy (20%)
- **Values**: Freedom, Innovation, Wealth, Knowledge, Family
- **Features**: Cultural melting pot, diplomats, diverse skills, trading hubs

### Half-Orc Civilizations
- **Name Templates**: "The {place} Warband", "{adjective} Stronghold", etc.
- **Government Weights**: Tribal Council (40%), Military Dictatorship (30%), Clan Confederation (20%)
- **Values**: Survival, Military Might, Honor, Freedom, Family
- **Features**: Warrior culture, struggle for acceptance, survival instincts, fierce loyalty

### Tiefling Civilizations
- **Name Templates**: "The {place} Covenant", "{adjective} Enclave", etc.
- **Government Weights**: Oligarchy (35%), Republic (25%), Democracy (20%), Magocracy (20%)
- **Values**: Freedom, Survival, Innovation, Magic, Wealth
- **Features**: Outcast communities, self-reliance, innate magic, complex heritage

## Relationship System

Civilizations automatically generate relationships based on cultural compatibility:

### Relationship Calculation
```python
score = 0
+ Same race: +2
+ Shared cultural values: +1 per value
- Conflicting values (Order vs Freedom, etc.): -2
+ Same government type: +1

Score mapping:
  ≥ 4: Allied
  ≥ 2: Friendly
  ≥ 0: Neutral
  ≥-2: Tense
  < -2: Hostile
```

### Relationship Levels
- **Allied** (⚔️): Military and economic cooperation
- **Friendly** (🤝): Trade and cultural exchange
- **Neutral** (⚖️): No special relationship
- **Tense** (⚠️): Diplomatic friction
- **Hostile** (⚔️): Active antagonism
- **At War** (⚔️): Open conflict (not auto-generated)

## Integration

### WorldCoordinator Integration
```python
# In world_coordinator.py
from .civilizations import generate_civilizations, Civilization

# In __init__
self.civilizations = []

# In _generate_historical_figures()
self._generate_civilizations()

# Method added
def _generate_civilizations(self):
    self.civilizations = generate_civilizations(
        world_size=self.world_size,
        historical_figures=self.historical_figures,
        target_count=None  # Random 5-8
    )
```

### SaveManager Integration
```python
# Serialization
"civilizations": [civ.to_dict() for civ in civilizations]

# Deserialization
civilizations = [Civilization.from_dict(data) for data in saved_data]
```

### Research Command Integration
```python
# In debug_handler.py
research civilizations  # Shows all civilizations
research civs          # Alias
research kingdoms      # Alias

# Output includes:
- Name, race, government, population
- Cultural values and religious beliefs
- Founding figures
- Notable features
- Relationships with other civilizations
- Summary statistics (by race, government, total population)
```

## Generation Algorithm

### Step 1: Race Selection
Uses weighted random based on historical figure distribution:
- Human: 30%
- Elf: 20%
- Dwarf: 15%
- Halfling: 10%
- Dragonborn: 8%
- Gnome: 7%
- Half-Elf: 5%
- Half-Orc: 3%
- Tiefling: 2%

### Step 2: Name Generation
1. Select race-specific archetype templates
2. Randomly choose template with placeholders
3. Fill placeholders with race-specific names
4. Ensure uniqueness across all civilizations

### Step 3: Government & Culture
1. Select government type (weighted by race)
2. Choose 2-3 cultural values from race defaults
3. Select religion from race-specific options
4. Generate cultural description combining all elements
5. Select 2-4 notable features

### Step 4: Founding Figures
1. Filter historical figures by matching race
2. Prefer heroes over villains as founders
3. Assign 1-3 founding figures to civilization
4. Update figures' `civilization` attribute

### Step 5: Relationships
1. Calculate compatibility score with all other civilizations
2. Map score to RelationshipLevel
3. Store bidirectional relationships

## Testing

### Test Suite: `tests/test_civilizations.py`
- **Test 1**: Basic generation (correct count, valid attributes)
- **Test 2**: Race diversity (4+ races in 8 civilizations)
- **Test 3**: Government variety (distribution check)
- **Test 4**: Founding figure association (bidirectional)
- **Test 5**: Relationships (complete graph, distribution)
- **Test 6**: Serialization (data integrity)
- **Test 7**: Cultural features (2+ per civilization)

### Quick Verification: `verify_civilizations.py`
Generates sample world and displays:
- Civilization names and basic info
- Founding figures
- Cultural features
- Population and government

### Running Tests
```bash
# Full test suite
python3 tests/test_civilizations.py

# Quick verification
python3 verify_civilizations.py

# In-game testing
python3 play.py
> research civilizations
```

## Example Output

```
=== CIVILIZATIONS (6) ===

Golden Kingdom of Avalon
  Race: Human
  Government: Monarchy
  Founded: Year -423
  Population: 342,156
  Values: Glory, Wealth, Order
  Faith: Worship the Pantheon of Light
  Golden Kingdom of Avalon is a human civilization ruled by hereditary monarchs.
  Their culture is defined by pursuit of glory and renown, prosperous trade and
  accumulation of wealth, strict laws and social order.
  Founders: Aldric the Brave Warlord (hero)
  Notable Features:
    • Extensive road networks connecting cities
    • Strong merchant guilds and trade traditions
  Relations:
    🤝 Friendly with Moonlit Realm of Silverpine
    ⚖️ Neutral with Clan Ironforge
    ⚔️ Hostile with The Shadow Covenant

Moonlit Realm of Silverpine
  Race: Elf
  Government: Monarchy
  Founded: Year -512
  Population: 128,943
  Values: Tradition, Nature, Magic
  Faith: Revere the ancient forest spirits
  [continues...]

=== CIVILIZATION SUMMARY ===

By Race:
  Human: 2 civilizations
  Elf: 1 civilization
  Dwarf: 1 civilization
  Dragonborn: 1 civilization
  Gnome: 1 civilization

By Government:
  Monarchy: 3
  Republic: 1
  Clan Confederation: 1
  Democracy: 1

Total Population: 1,245,678

Inter-Civilization Relations:
  Neutral: 8 relationships
  Friendly: 5 relationships
  Tense: 2 relationships
```

## Future Enhancements (Not in Task 3.1)

These are part of later tasks:
- **Task 3.2**: Territory placement on world map
- **Task 3.3**: Civilization testing with geographic data
- **Task 4.x**: Historical event effects on civilizations
- **Task 5.x**: NPC generation from civilizations
- **Task 6.x**: Civilization-based quest generation

## File Manifest

**Created:**
- `fantasy_rpg/world/civilizations.py` - Complete civilization system
- `tests/test_civilizations.py` - Comprehensive test suite
- `verify_civilizations.py` - Quick verification script
- `fantasy_rpg/world/CIVILIZATIONS.md` - This documentation

**Modified:**
- `fantasy_rpg/world/world_coordinator.py` - Added civilization generation
- `fantasy_rpg/game/save_manager.py` - Added civilization serialization
- `fantasy_rpg/actions/debug_handler.py` - Added research civilizations command
- `.kiro/specs/4.0-history/tasks.md` - Marked Task 3.1 complete

## Success Criteria (Task 3.1)

✅ **Civilization Dataclass**: Complete with all required fields  
✅ **Cultural Identity**: Government types (10), cultural values (15), religions  
✅ **Race Coverage**: All 9 D&D races with unique archetypes  
✅ **Government Variety**: 10 different government types with race-specific weights  
✅ **Value Systems**: 15 cultural values, 2-3 per civilization  
✅ **Founding Figures**: Association with historical figures (Task 2.1)  
✅ **Relationships**: Complete relationship graph between civilizations  
✅ **Notable Features**: 2-4 unique cultural traits per civilization  
✅ **Serialization**: Save/load support through SaveManager  
✅ **Research Commands**: In-game research system for exploring civilizations  
✅ **Testing**: Comprehensive test suite with 7 test cases  

**Task 3.1 Complete!**
