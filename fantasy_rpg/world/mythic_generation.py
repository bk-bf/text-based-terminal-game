"""
Mythic/Foundation event generation for the world layer

This module generates a small set (8-12) of legendary events that form
the cultural/historical foundation of the generated world. Events are
seeded for reproducibility and draw from a small templates file.

The generator is intentionally lightweight and deterministic given a seed
so it can run during world generation without heavy compute.

NOTE: Mythic LOCATIONS are handled by fantasy_rpg/locations/mythic_locations.py
This module only generates the historical EVENTS.

ARTIFACTS: Legendary artifacts are generated through artifact_generation.py
and are associated with mythic events during world generation.
"""
from typing import List, Dict, Any, Optional
import json
import os
import random

TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mythic_event_templates.json')


def _load_templates(path: Optional[str] = None) -> List[Dict[str, Any]]:
    fp = path or TEMPLATES_PATH
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # Fallback minimal templates if file missing
        return [
            {"name": "The First Fire", "type": "discovery", "base_description": "A discovery that changed lives.", "significance": 8},
            {"name": "The Broken Crown", "type": "war", "base_description": "A dynastic betrayal that reshaped borders.", "significance": 9}
        ]


def _pick_location(world, rng: random.Random) -> str:
    """Pick a hex id from the world's hex_data. Falls back to '0000' if none."""
    if not getattr(world, 'hex_data', None):
        return "0000"
    hex_ids = list(world.hex_data.keys())
    if not hex_ids:
        return "0000"
    return rng.choice(hex_ids)


def generate_mythic_events(world, num_events: int = 10, seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """Generate a list of mythic/foundational historical events.

    Args:
        world: WorldCoordinator-like object with `hex_data` mapping
        num_events: Number of events to generate (recommended 8-12)
        seed: Optional seed for deterministic results

    Returns:
        List of event dictionaries with keys: id, name, year, event_type,
        description, location, significance, creates_artifacts, artifact_lore
    """
    rng = random.Random(seed)
    templates = _load_templates()

    events: List[Dict[str, Any]] = []
    
    # Calendar system: Current year is 1452, mythic events are ancient (200-1200 years ago)
    current_year = 1452
    base_year = current_year - rng.randint(200, 1200)  # Ancient era: 252 to 1252

    for i in range(num_events):
        tpl = rng.choice(templates)
        # Spread events backward from base_year
        year = base_year - rng.randint(0, 50 * i + 50)  # Goes further back in time
        significance = tpl.get('significance', 5)
        # small random variation
        significance = max(1, min(10, significance + rng.randint(-2, 2)))

        location = _pick_location(world, rng)

        event = {
            'id': f'mythic-{i+1}',
            'name': tpl.get('name', f'Legend {i+1}'),
            'year': year,
            'event_type': tpl.get('type', 'myth'),
            'description': tpl.get('base_description', '') + " " + tpl.get('detail', ''),
            'location': location,
            'significance': significance,
            'creates_artifacts': tpl.get('creates_artifacts', []),
        }

        events.append(event)

    # Sort by year (oldest first)
    events.sort(key=lambda e: e['year'])
    
    # Generate artifact associations and lore
    _associate_artifacts_with_events(events, seed)
    
    return events


def _associate_artifacts_with_events(events: List[Dict[str, Any]], seed: Optional[int] = None):
    """Associate legendary artifacts with mythic events and add lore.
    
    This function modifies the events list in-place, adding artifact_id and
    artifact_lore fields to events that create legendary artifacts.
    
    Args:
        events: List of event dictionaries to modify
        seed: Optional seed for deterministic artifact selection
    """
    try:
        from fantasy_rpg.world.artifact_generation import (
            generate_artifacts_for_events, 
            get_artifact_lore
        )
        
        # Generate artifact assignments
        artifact_map = generate_artifacts_for_events(events, seed)
        
        # Add artifact data to events
        for event in events:
            event_id = event['id']
            if event_id in artifact_map:
                artifact_id = artifact_map[event_id]
                event['artifact_id'] = artifact_id
                event['artifact_lore'] = get_artifact_lore(artifact_id)
                
                # Ensure creates_artifacts list includes this artifact
                if artifact_id not in event.get('creates_artifacts', []):
                    if 'creates_artifacts' not in event:
                        event['creates_artifacts'] = []
                    event['creates_artifacts'].append(artifact_id)
    except ImportError as e:
        # Graceful degradation if artifact system not available
        print(f"Warning: Could not import artifact generation system: {e}")


if __name__ == '__main__':
    # Quick smoke test when run directly
    class DummyWorld:
        def __init__(self):
            self.hex_data = {f"{x:02d}{y:02d}": {} for x in range(5) for y in range(5)}

    w = DummyWorld()
    ev = generate_mythic_events(w, 10, seed=123)
    for e in ev:
        print(e)
