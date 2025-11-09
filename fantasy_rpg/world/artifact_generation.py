"""
Legendary Artifact Generation

This module generates legendary artifacts tied to mythic events and locations.
Artifacts have creation stories, cultural significance, and are placed in
mythic locations throughout the world.

Integration Points:
- Called during mythic event generation
- Artifacts placed in corresponding mythic locations
- Creates Item instances with legendary properties
"""

from typing import List, Dict, Any, Optional
import json
import os
import random
from fantasy_rpg.core.item import Item, ItemLoader

ARTIFACTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'legendary_artifacts.json')


def _load_artifact_templates(path: Optional[str] = None) -> Dict[str, Any]:
    """Load legendary artifact templates from JSON file"""
    fp = path or ARTIFACTS_PATH
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('artifacts', {})
    except Exception as e:
        print(f"Warning: Could not load legendary artifacts: {e}")
        return {}


def select_artifact_for_event(event_type: str, seed: Optional[int] = None) -> Optional[str]:
    """Select an artifact that matches the given event type.
    
    Args:
        event_type: Type of mythic event (war, discovery, disaster, etc.)
        seed: Optional seed for deterministic selection
        
    Returns:
        Artifact ID string, or None if no match found
    """
    rng = random.Random(seed)
    templates = _load_artifact_templates()
    
    if not templates:
        return None
    
    # Find artifacts that match this event type
    matching = [
        artifact_id for artifact_id, template in templates.items()
        if event_type in template.get('event_types', [])
    ]
    
    if matching:
        return rng.choice(matching)
    
    return None


def get_artifact_template(artifact_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific artifact template by ID.
    
    Args:
        artifact_id: ID of the artifact to retrieve
        
    Returns:
        Dictionary containing artifact template data, or None if not found
    """
    templates = _load_artifact_templates()
    return templates.get(artifact_id)


def create_legendary_item(artifact_id: str, item_loader: Optional[ItemLoader] = None) -> Optional[Item]:
    """Create a legendary Item instance from an artifact template.
    
    Args:
        artifact_id: ID of the artifact to instantiate
        item_loader: Optional ItemLoader instance (creates new one if not provided)
        
    Returns:
        Item instance with legendary properties, or None if artifact not found
    """
    template = get_artifact_template(artifact_id)
    if not template:
        return None
    
    # Get base item to inherit properties from
    if item_loader is None:
        item_loader = ItemLoader()
    
    base_item_id = template.get('item_base', 'longsword')
    base_item = item_loader.get_item(base_item_id)
    
    # Start with base item properties or defaults
    if base_item:
        item_data = {
            'name': template['name'],
            'item_type': base_item.item_type,
            'weight': base_item.weight,
            'value': base_item.value,
            'description': template.get('creation_story', ''),
            'properties': (base_item.properties or []).copy(),
            'pools': ['legendary', 'artifact', 'mythic'],
            'drop_weight': 1,  # Extremely rare
            'ac_bonus': base_item.ac_bonus,
            'armor_type': base_item.armor_type,
            'damage_dice': base_item.damage_dice,
            'damage_type': base_item.damage_type,
            'equippable': base_item.equippable,
            'slot': base_item.slot,
            'magical': True,  # All legendary artifacts are magical
            'enchantment_bonus': base_item.enchantment_bonus,
            'special_properties': (base_item.special_properties or []).copy(),
        }
    else:
        # Create from scratch if base item not found
        item_data = {
            'name': template['name'],
            'item_type': 'weapon',
            'weight': 3.0,
            'value': 50000,
            'description': template.get('creation_story', ''),
            'properties': [],
            'pools': ['legendary', 'artifact', 'mythic'],
            'drop_weight': 1,
            'equippable': True,
            'magical': True,
        }
    
    # Apply overrides from artifact template
    overrides = template.get('item_overrides', {})
    for key, value in overrides.items():
        if key == 'type':
            item_data['item_type'] = value
        elif key == 'special_properties':
            # Merge special properties
            existing = item_data.get('special_properties', [])
            item_data['special_properties'] = existing + value
        else:
            item_data[key] = value
    
    # Add legendary properties as special_properties if not already there
    legendary_props = template.get('legendary_properties', [])
    if legendary_props:
        current_special = item_data.get('special_properties', [])
        for prop in legendary_props:
            if prop not in current_special:
                current_special.append(prop)
        item_data['special_properties'] = current_special
    
    # Store cultural significance and location hint as metadata
    item_data['cultural_significance'] = template.get('cultural_significance', '')
    item_data['current_location_hint'] = template.get('current_location_hint', '')
    
    # Create the item
    return Item(
        item_id=artifact_id,
        name=item_data['name'],
        item_type=item_data['item_type'],
        weight=item_data.get('weight', 1.0),
        value=item_data.get('value', 50000),
        description=item_data['description'],
        properties=item_data.get('properties', []),
        pools=item_data['pools'],
        drop_weight=item_data['drop_weight'],
        ac_bonus=item_data.get('ac_bonus'),
        armor_type=item_data.get('armor_type'),
        damage_dice=item_data.get('damage_dice'),
        damage_type=item_data.get('damage_type'),
        equippable=item_data.get('equippable', False),
        slot=item_data.get('slot'),
        magical=item_data.get('magical', True),
        enchantment_bonus=item_data.get('enchantment_bonus', 0),
        special_properties=item_data.get('special_properties', [])
    )


def generate_artifacts_for_events(mythic_events: List[Dict[str, Any]], 
                                 seed: Optional[int] = None) -> Dict[str, str]:
    """Generate artifact associations for mythic events.
    
    Args:
        mythic_events: List of mythic event dictionaries
        seed: Optional seed for deterministic selection
        
    Returns:
        Dictionary mapping event_id -> artifact_id for events that have artifacts
    """
    rng = random.Random(seed)
    artifact_assignments = {}
    
    for event in mythic_events:
        event_type = event.get('event_type', 'myth')
        event_id = event.get('id')
        
        # Check if event already specifies artifacts
        creates_artifacts = event.get('creates_artifacts', [])
        if creates_artifacts:
            # Use explicitly specified artifact
            artifact_assignments[event_id] = creates_artifacts[0]
            continue
        
        # 30% chance to generate an artifact for major events
        significance = event.get('significance', 5)
        if significance >= 7 and rng.random() < 0.3:
            artifact_id = select_artifact_for_event(event_type, seed=rng.randint(0, 10000))
            if artifact_id:
                artifact_assignments[event_id] = artifact_id
    
    return artifact_assignments


def get_artifact_lore(artifact_id: str) -> Dict[str, Any]:
    """Get the complete lore information for an artifact.
    
    Args:
        artifact_id: ID of the artifact
        
    Returns:
        Dictionary containing creation_story, cultural_significance, 
        legendary_properties, and location_hint
    """
    template = get_artifact_template(artifact_id)
    if not template:
        return {}
    
    return {
        'name': template.get('name', 'Unknown Artifact'),
        'creation_story': template.get('creation_story', ''),
        'cultural_significance': template.get('cultural_significance', ''),
        'legendary_properties': template.get('legendary_properties', []),
        'location_hint': template.get('current_location_hint', '')
    }


def list_all_artifacts() -> List[str]:
    """Get a list of all available artifact IDs.
    
    Returns:
        List of artifact ID strings
    """
    templates = _load_artifact_templates()
    return list(templates.keys())


# Manual testing
if __name__ == '__main__':
    print("=== Testing Legendary Artifact Generation ===\n")
    
    # Test loading artifacts
    print("1. Loading artifact templates...")
    artifacts = list_all_artifacts()
    print(f"   Found {len(artifacts)} legendary artifacts: {artifacts}\n")
    
    # Test artifact selection by event type
    print("2. Testing artifact selection by event type...")
    test_types = ['war', 'discovery', 'omen', 'treaty', 'siege']
    for event_type in test_types:
        artifact = select_artifact_for_event(event_type, seed=42)
        print(f"   {event_type}: {artifact}")
    print()
    
    # Test creating legendary items
    print("3. Creating legendary items...")
    loader = ItemLoader()
    for artifact_id in artifacts[:3]:  # Test first 3
        item = create_legendary_item(artifact_id, loader)
        if item:
            print(f"\n   {item.name}")
            print(f"   Type: {item.item_type}, Value: {item.value}gp")
            print(f"   Magical: {item.magical}, Bonus: +{item.enchantment_bonus}")
            print(f"   Properties: {item.special_properties[:2]}...")  # Show first 2
    print()
    
    # Test artifact lore
    print("4. Testing artifact lore retrieval...")
    if artifacts:
        lore = get_artifact_lore(artifacts[0])
        print(f"\n   {lore['name']}")
        print(f"   Story: {lore['creation_story'][:100]}...")
        print(f"   Significance: {lore['cultural_significance'][:100]}...")
    
    print("\n✓ All artifact tests completed!")
