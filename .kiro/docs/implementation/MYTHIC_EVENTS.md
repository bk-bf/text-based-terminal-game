# Mythic Event Generation System

## Overview

The mythic event generation system creates 8-12 foundational legendary events that form the cultural and historical bedrock of the generated world. These events are procedurally generated during world creation and anchored to specific hex locations.

## Architecture

### Core Components

1. **`fantasy_rpg/world/mythic_generation.py`**
   - Main generator module with `generate_mythic_events()` function
   - Seeded random generation for reproducibility
   - Template-based event creation

2. **`fantasy_rpg/data/mythic_event_templates.json`**
   - 12 foundational event templates
   - Event types: discovery, war, disaster, treaty, siege, loss, omen, artifact
   - Each template includes: name, type, description, significance (1-10)

3. **Integration with `WorldCoordinator`**
   - Events generated automatically during `_generate_world()`
   - Events stored in `world.mythic_events` list
   - Hexes marked with `mythic_sites` array containing event IDs

## Event Structure

Each generated event contains:

```python
{
    'id': 'mythic-1',                    # Unique identifier
    'name': 'The First Flame',           # Event name
    'year': -842,                        # Years before present (negative = ancient)
    'event_type': 'discovery',           # Category of event
    'description': '...',                # Narrative description
    'location': '0507',                  # Hex ID where event occurred
    'significance': 7,                   # Impact rating (1-10)
    'creates_artifacts': []              # Optional artifact IDs
}
```

## Usage

### Automatic Generation

Events are automatically generated when creating a new world:

```python
from fantasy_rpg.world.world_coordinator import WorldCoordinator

# World generation includes mythic events by default
world = WorldCoordinator(world_size=(20, 20), seed=12345)

# Access generated events
for event in world.mythic_events:
    print(f"{event['name']} occurred in year {event['year']}")

# Find hexes with mythic significance
for hex_id, hex_data in world.hex_data.items():
    if 'mythic_sites' in hex_data:
        print(f"Hex {hex_id} has {len(hex_data['mythic_sites'])} mythic events")
```

### Manual Generation

You can also generate events independently:

```python
from fantasy_rpg.world.mythic_generation import generate_mythic_events

# Generate 10 events with custom seed
events = generate_mythic_events(world, num_events=10, seed=42)
```

## Testing

### Unit Tests

```bash
PYTHONPATH=. pytest tests/test_mythic_generation.py -v
```

Tests verify:
- Correct number of events generated (8-12)
- All required fields present
- Locations map to valid hex IDs
- Events sorted chronologically

### Integration Verification

```bash
python3 tests/verify_mythic_integration.py
```

This interactive script:
- Generates a test world
- Displays all mythic events chronologically
- Shows which hexes contain mythic sites
- Validates integration with WorldCoordinator

## Design Principles

1. **Lightweight & Fast**: Minimal computation during world generation
2. **Deterministic**: Same seed always produces same events
3. **Anchored**: Events tied to physical locations on the map
4. **Template-Driven**: Easy to extend by adding templates
5. **Historical Foundation**: Events occur in ancient times (-200 to -1200 years)

## Future Extensions

This system provides the foundation for:
- **Mythic location generation** (sacred sites, battlefields, ruins)
- **Legendary artifacts** referenced in event descriptions
- **Cultural heroes/villains** linked to events
- **Civilization founding** influenced by mythic history
- **Quest generation** based on lost artifacts or unfinished sagas

## Event Types

Current template categories:

- **discovery**: Revolutionary findings (fire, magic, resources)
- **war**: Conflicts that reshaped borders/power
- **disaster**: Floods, plagues, earthquakes
- **treaty**: Alliances and peace agreements
- **siege**: Famous military engagements
- **loss**: Vanished cities or peoples
- **omen**: Celestial/supernatural signs
- **artifact**: Creation of legendary items

## Adding New Templates

To add more event templates, edit `fantasy_rpg/data/mythic_event_templates.json`:

```json
{
  "name": "The Dragon's Fall",
  "type": "war",
  "base_description": "The last dragon was slain by alliance of kingdoms.",
  "creates_artifacts": ["dragonbone_sword"],
  "significance": 9
}
```

Templates are randomly selected during generation, allowing for infinite variation with a finite set of archetypes.
