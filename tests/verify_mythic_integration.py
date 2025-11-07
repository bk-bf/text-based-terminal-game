#!/usr/bin/env python3
"""
Quick verification script to check mythic event integration with WorldCoordinator.
Run this to see generated mythic events and their hex placements.
"""

from fantasy_rpg.world.world_coordinator import WorldCoordinator


def main():
    print("=" * 70)
    print("MYTHIC EVENT GENERATION VERIFICATION")
    print("=" * 70)
    
    # Create a small world
    print("\n🌍 Generating 10x10 world with seed 42...")
    wc = WorldCoordinator(world_size=(10, 10), seed=42, skip_generation=False)
    
    # Check mythic events were generated
    if not hasattr(wc, 'mythic_events'):
        print("❌ ERROR: No mythic_events attribute found on WorldCoordinator")
        return
    
    events = wc.mythic_events
    print(f"✅ Generated {len(events)} mythic events\n")
    
    # Display events
    print("📜 MYTHIC EVENTS (chronological order):")
    print("-" * 70)
    for i, event in enumerate(events, 1):
        year = event['year']
        name = event['name']
        event_type = event['event_type']
        location = event['location']
        significance = event['significance']
        desc = event['description'][:60] + "..." if len(event['description']) > 60 else event['description']
        
        print(f"\n{i}. {name}")
        print(f"   Year: {year} | Type: {event_type} | Significance: {significance}/10")
        print(f"   Location: Hex {location}")
        print(f"   {desc}")
    
    # Check hex markings
    print("\n" + "=" * 70)
    print("🗺️  HEXES WITH MYTHIC SITES:")
    print("-" * 70)
    
    marked_hexes = {hex_id: data for hex_id, data in wc.hex_data.items() 
                    if 'mythic_sites' in data and data['mythic_sites']}
    
    if not marked_hexes:
        print("❌ WARNING: No hexes marked with mythic sites")
    else:
        print(f"✅ {len(marked_hexes)} hexes marked with mythic sites\n")
        for hex_id, data in sorted(marked_hexes.items())[:5]:  # Show first 5
            hex_name = data.get('name', 'Unknown')
            mythic_ids = data.get('mythic_sites', [])
            event_names = [e['name'] for e in events if e['id'] in mythic_ids]
            print(f"  • {hex_id} ({hex_name}): {', '.join(event_names)}")
        
        if len(marked_hexes) > 5:
            print(f"  ... and {len(marked_hexes) - 5} more hexes")
    
    # Test mythic location generation for one hex
    print("\n" + "=" * 70)
    print("🏛️  TESTING MYTHIC LOCATION GENERATION:")
    print("-" * 70)
    
    if marked_hexes:
        test_hex_id = list(marked_hexes.keys())[0]
        test_hex_data = marked_hexes[test_hex_id]
        coords = test_hex_data.get('coords', (0, 0))
        
        print(f"\nTesting location generation for hex {test_hex_id} (coords: {coords})")
        print(f"Biome: {test_hex_data.get('biome', 'unknown')}")
        print(f"Mythic sites: {test_hex_data.get('mythic_sites', [])}")
        
        try:
            locations = wc._generate_hex_locations(
                coords,
                test_hex_data.get('biome', 'temperate_grassland'),
                test_hex_data.get('elevation_raw', 0.5)
            )
            
            print(f"\n✅ Generated {len(locations)} location(s):")
            for loc in locations:
                loc_name = loc.get('name', 'Unknown')
                is_mythic = loc.get('is_mythic', False)
                mythic_marker = " 🏛️ MYTHIC" if is_mythic else ""
                print(f"  • {loc_name}{mythic_marker}")
                if is_mythic:
                    print(f"    Type: {loc.get('type', 'unknown')}")
                    print(f"    Event: {loc.get('mythic_event_id', 'N/A')}")
        except Exception as e:
            print(f"❌ Error generating locations: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
