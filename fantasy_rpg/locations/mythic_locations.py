"""
Mythic Location Generator

Handles generation and instantiation of mythic/legendary locations.
This module is called by LocationGenerator when a hex contains mythic sites.
"""

from typing import List, Dict, Any, Optional
import json
import os
import random

MYTHIC_LOCATIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mythic_locations.json')


def _load_mythic_location_templates(path: Optional[str] = None) -> Dict[str, Any]:
    """Load mythic location templates from JSON file"""
    fp = path or MYTHIC_LOCATIONS_PATH
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('location_templates', {})
    except Exception as e:
        print(f"Warning: Could not load mythic locations: {e}")
        return {}


def select_mythic_location_template(event_type: str, seed: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Select a mythic location template matching the given event type.
    
    Args:
        event_type: Type of mythic event (war, discovery, disaster, etc.)
        seed: Optional seed for deterministic selection
        
    Returns:
        Dictionary containing location template data, or None if no match found
    """
    rng = random.Random(seed)
    templates = _load_mythic_location_templates()
    
    if not templates:
        return None
    
    # Find templates that match this event type
    matching = [
        template for template in templates.values()
        if event_type in template.get('event_types', [])
    ]
    
    if matching:
        return rng.choice(matching)
    
    # Fallback: return any mythic template
    return rng.choice(list(templates.values())) if templates else None


def get_random_mythic_location_template(seed: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Get a random mythic location template for standalone placement.
    
    Args:
        seed: Optional seed for deterministic selection
        
    Returns:
        Dictionary containing location template data, or None if no templates available
    """
    rng = random.Random(seed)
    templates = _load_mythic_location_templates()
    
    if not templates:
        return None
    
    return rng.choice(list(templates.values()))


def instantiate_mythic_location(template: Dict[str, Any], 
                                hex_coords: tuple,
                                mythic_event_id: Optional[str] = None,
                                artifact_id: Optional[str] = None) -> Dict[str, Any]:
    """Convert a mythic location template into an instantiated location.
    
    Args:
        template: Mythic location template dictionary
        hex_coords: Hex coordinates (x, y) where location is placed
        mythic_event_id: Optional ID of associated mythic event
        artifact_id: Optional ID of legendary artifact to place in this location
        
    Returns:
        Dictionary representing an instantiated location
    """
    location = {
        'id': f"mythic_{template.get('type', 'site')}_{hex_coords[0]:02d}{hex_coords[1]:02d}",
        'name': template.get('name', 'Mythic Site'),
        'type': template.get('type', 'mythic'),
        'description': template.get('description', 'A place of ancient power.'),
        'size': template.get('size', 'large'),
        'terrain': template.get('terrain', 'difficult'),
        'exit_flag': template.get('exit_flag', True),
        'is_mythic': True,
        'mythic_event_id': mythic_event_id,
        'artifact_id': artifact_id,  # Store artifact ID for location generation
        'areas': template.get('areas', {}),
        'provides_some_shelter': template.get('provides_some_shelter', False),
        'provides_good_shelter': template.get('provides_good_shelter', False),
        'provides_excellent_shelter': template.get('provides_excellent_shelter', False),
    }
    
    return location


def get_mythic_location_for_hex(hex_data: Dict[str, Any], 
                                hex_coords: tuple,
                                mythic_events: List[Dict[str, Any]],
                                seed: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Generate a mythic location for a hex if it has mythic sites.
    
    This is the main entry point called by LocationGenerator.
    
    Args:
        hex_data: Hex data dictionary containing mythic_sites list
        hex_coords: Hex coordinates (x, y)
        mythic_events: List of all mythic events in the world
        seed: Optional seed for deterministic generation
        
    Returns:
        Instantiated mythic location dictionary, or None if hex has no mythic sites
    """
    mythic_site_ids = hex_data.get('mythic_sites', [])
    
    if not mythic_site_ids:
        return None
    
    # Find the event associated with this hex
    matching_event = None
    for event in mythic_events:
        if event['id'] in mythic_site_ids:
            matching_event = event
            break
    
    if not matching_event:
        return None
    
    # Select appropriate template based on event type
    template = select_mythic_location_template(
        matching_event.get('event_type', 'myth'),
        seed=seed
    )
    
    if not template:
        return None
    
    # Get artifact ID if event creates one
    artifact_id = None
    creates_artifacts = matching_event.get('creates_artifacts', [])
    if creates_artifacts:
        artifact_id = creates_artifacts[0]  # Use first artifact
    
    # Instantiate the location with artifact
    return instantiate_mythic_location(
        template,
        hex_coords,
        mythic_event_id=matching_event['id'],
        artifact_id=artifact_id
    )


if __name__ == '__main__':
    # Quick test
    template = select_mythic_location_template('war', seed=42)
    if template:
        print(f"Selected template: {template.get('name')}")
        location = instantiate_mythic_location(template, (5, 7), 'mythic-1')
        print(f"Instantiated: {location['name']} at hex 0507")
    else:
        print("No templates found")
