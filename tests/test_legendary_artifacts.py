"""
Test script for legendary artifact generation and integration with mythic system.

This script verifies:
1. Artifact templates load correctly
2. Artifacts are associated with mythic events
3. Artifacts are placed in mythic locations
4. Legendary items can be created from artifact templates
5. Full integration with world generation system
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fantasy_rpg.world.mythic_generation import generate_mythic_events
from fantasy_rpg.world.artifact_generation import (
    list_all_artifacts,
    get_artifact_template,
    create_legendary_item,
    get_artifact_lore,
    generate_artifacts_for_events
)
from fantasy_rpg.locations.mythic_locations import get_mythic_location_for_hex
from fantasy_rpg.core.item import ItemLoader


class DummyWorld:
    """Mock world object for testing"""
    def __init__(self):
        self.hex_data = {f"{x:02d}{y:02d}": {} for x in range(10) for y in range(10)}


def test_artifact_templates():
    """Test that artifact templates load correctly"""
    print("=" * 70)
    print("TEST 1: Artifact Template Loading")
    print("=" * 70)
    
    artifacts = list_all_artifacts()
    print(f"✓ Loaded {len(artifacts)} legendary artifacts\n")
    
    for artifact_id in artifacts:
        template = get_artifact_template(artifact_id)
        print(f"  • {template['name']}")
        print(f"    Event Types: {', '.join(template['event_types'])}")
        print(f"    Base Item: {template['item_base']}")
        print(f"    Properties: {len(template.get('legendary_properties', []))} legendary abilities")
        print()
    
    return len(artifacts) > 0


def test_mythic_events_with_artifacts():
    """Test that mythic events generate with artifact associations"""
    print("=" * 70)
    print("TEST 2: Mythic Events with Artifact Generation")
    print("=" * 70)
    
    world = DummyWorld()
    events = generate_mythic_events(world, num_events=10, seed=42)
    
    print(f"✓ Generated {len(events)} mythic events\n")
    
    events_with_artifacts = [e for e in events if e.get('artifact_id')]
    print(f"✓ {len(events_with_artifacts)} events have associated artifacts\n")
    
    for event in events:
        print(f"  • {event['name']} (Year {event['year']})")
        print(f"    Type: {event['event_type']}, Significance: {event['significance']}")
        print(f"    Location: Hex {event['location']}")
        
        if event.get('artifact_id'):
            artifact_id = event['artifact_id']
            print(f"    ⚔ Creates Artifact: {artifact_id}")
            
            if event.get('artifact_lore'):
                lore = event['artifact_lore']
                print(f"       Name: {lore.get('name', 'Unknown')}")
                print(f"       Story: {lore.get('creation_story', '')[:80]}...")
        print()
    
    return len(events_with_artifacts) > 0


def test_legendary_item_creation():
    """Test creating legendary Item instances from artifacts"""
    print("=" * 70)
    print("TEST 3: Legendary Item Creation")
    print("=" * 70)
    
    loader = ItemLoader()
    artifacts = list_all_artifacts()
    
    print(f"Creating legendary items from {len(artifacts)} artifact templates...\n")
    
    success_count = 0
    for artifact_id in artifacts[:5]:  # Test first 5
        item = create_legendary_item(artifact_id, loader)
        if item:
            success_count += 1
            print(f"  ✓ {item.name}")
            print(f"    Type: {item.item_type}, Slot: {item.slot}")
            print(f"    Value: {item.value} gp, Weight: {item.weight} lbs")
            print(f"    Magical: {item.magical}, Enchantment: +{item.enchantment_bonus}")
            
            if item.damage_dice:
                print(f"    Damage: {item.damage_dice} {item.damage_type}")
            if item.ac_bonus:
                print(f"    AC Bonus: +{item.ac_bonus}")
            
            print(f"    Pools: {', '.join(item.pools)}")
            print(f"    Special Properties: {len(item.special_properties)} abilities")
            print()
        else:
            print(f"  ✗ Failed to create {artifact_id}")
    
    print(f"✓ Successfully created {success_count}/{len(artifacts[:5])} legendary items\n")
    return success_count > 0


def test_artifact_lore():
    """Test artifact lore retrieval"""
    print("=" * 70)
    print("TEST 4: Artifact Lore System")
    print("=" * 70)
    
    artifacts = list_all_artifacts()
    test_artifact = artifacts[0] if artifacts else None
    
    if not test_artifact:
        print("  ✗ No artifacts available for testing")
        return False
    
    lore = get_artifact_lore(test_artifact)
    
    print(f"Testing lore for: {test_artifact}\n")
    print(f"  Name: {lore['name']}")
    print(f"\n  Creation Story:")
    print(f"    {lore['creation_story']}")
    print(f"\n  Cultural Significance:")
    print(f"    {lore['cultural_significance']}")
    print(f"\n  Legendary Properties:")
    for i, prop in enumerate(lore['legendary_properties'], 1):
        print(f"    {i}. {prop}")
    print(f"\n  Location Hint:")
    print(f"    {lore['location_hint']}")
    print()
    
    return True


def test_mythic_location_artifact_placement():
    """Test that artifacts are placed in mythic locations"""
    print("=" * 70)
    print("TEST 5: Artifact Placement in Mythic Locations")
    print("=" * 70)
    
    world = DummyWorld()
    events = generate_mythic_events(world, num_events=10, seed=42)
    
    # Mark hexes with mythic sites (simulating WorldCoordinator)
    for event in events:
        hex_id = event['location']
        if hex_id in world.hex_data:
            if 'mythic_sites' not in world.hex_data[hex_id]:
                world.hex_data[hex_id]['mythic_sites'] = []
            world.hex_data[hex_id]['mythic_sites'].append(event['id'])
    
    # Test location generation with artifacts
    locations_with_artifacts = 0
    for event in events:
        if not event.get('artifact_id'):
            continue
        
        hex_id = event['location']
        hex_coords = (int(hex_id[:2]), int(hex_id[2:]))
        hex_data = world.hex_data.get(hex_id, {})
        
        location = get_mythic_location_for_hex(
            hex_data,
            hex_coords,
            events,
            seed=42
        )
        
        if location and location.get('artifact_id'):
            locations_with_artifacts += 1
            print(f"  ✓ {location['name']} (Hex {hex_id})")
            print(f"    Type: {location['type']}")
            print(f"    Event: {location['mythic_event_id']}")
            print(f"    Artifact: {location['artifact_id']}")
            print()
    
    print(f"✓ {locations_with_artifacts} mythic locations contain legendary artifacts\n")
    return locations_with_artifacts > 0


def test_items_json_integration():
    """Test that legendary artifacts are loadable from items.json"""
    print("=" * 70)
    print("TEST 6: items.json Integration")
    print("=" * 70)
    
    loader = ItemLoader()
    items = loader.load_items()
    
    legendary_items = [
        item for item in items.values()
        if 'legendary' in (item.pools or [])
    ]
    
    print(f"✓ Found {len(legendary_items)} legendary items in items.json\n")
    
    for item in legendary_items:
        print(f"  • {item.name}")
        print(f"    Type: {item.item_type}, Value: {item.value} gp")
        print(f"    Magical: {item.magical}, Pools: {', '.join(item.pools or [])}")
        print()
    
    return len(legendary_items) > 0


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("LEGENDARY ARTIFACT SYSTEM - INTEGRATION TEST")
    print("=" * 70 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Artifact Template Loading", test_artifact_templates()))
    results.append(("Mythic Events with Artifacts", test_mythic_events_with_artifacts()))
    results.append(("Legendary Item Creation", test_legendary_item_creation()))
    results.append(("Artifact Lore System", test_artifact_lore()))
    results.append(("Artifact Placement in Locations", test_mythic_location_artifact_placement()))
    results.append(("items.json Integration", test_items_json_integration()))
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Legendary artifact system is fully integrated.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")
    
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
