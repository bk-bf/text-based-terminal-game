"""
Test Historical Figure Generation

Manual test script to verify historical figure generation works correctly
with mythic events and integrates properly into the world system.

Run with: python tests/test_historical_figures.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fantasy_rpg.world.world_coordinator import WorldCoordinator
from fantasy_rpg.world.historical_figures import (
    generate_historical_figures,
    HistoricalFigure,
    save_historical_figures,
    load_historical_figures
)
import json


def test_figure_generation():
    """Test basic figure generation from mythic events"""
    print("\n" + "="*70)
    print("TEST: Historical Figure Generation")
    print("="*70)
    
    # Create a world coordinator (generates mythic events automatically)
    print("\n1. Creating world with mythic events...")
    world = WorldCoordinator(world_size=(10, 10), seed=42)
    
    print(f"   ✓ Generated {len(world.mythic_events)} mythic events")
    
    # Check if historical figures were generated
    print(f"\n2. Checking historical figures...")
    if hasattr(world, 'historical_figures') and world.historical_figures:
        print(f"   ✓ Generated {len(world.historical_figures)} historical figures")
        
        # Count heroes vs villains
        heroes = [f for f in world.historical_figures if f.alignment == "hero"]
        villains = [f for f in world.historical_figures if f.alignment == "villain"]
        
        print(f"   • {len(heroes)} heroes")
        print(f"   • {len(villains)} villains")
    else:
        print("   ✗ No historical figures found!")
        return False
    
    return True


def test_figure_details():
    """Test that figures have proper details and connections"""
    print("\n" + "="*70)
    print("TEST: Figure Details and Connections")
    print("="*70)
    
    world = WorldCoordinator(world_size=(10, 10), seed=42)
    figures = world.historical_figures
    
    if not figures:
        print("   ✗ No figures to test!")
        return False
    
    print(f"\n1. Examining first 3 figures...")
    for i, figure in enumerate(figures[:3], 1):
        print(f"\n   Figure {i}: {figure.name} {figure.title}")
        print(f"   • Race: {figure.race}")
        print(f"   • Alignment: {figure.alignment}")
        print(f"   • Archetype: {figure.archetype}")
        print(f"   • Birth Year: {figure.birth_year}")
        print(f"   • Death Year: {figure.death_year or 'Unknown'}")
        print(f"   • Events Participated: {len(figure.participated_in_events)}")
        print(f"   • Achievements: {len(figure.achievements)}")
        print(f"   • Artifacts Owned: {len(figure.artifacts_owned)}")
        print(f"   • Cultural Significance: {figure.cultural_significance}/10")
        print(f"   • Personality: {', '.join(figure.personality_traits)}")
        
        if figure.backstory:
            print(f"   • Backstory: {figure.backstory[:100]}...")
    
    return True


def test_event_integration():
    """Test that figures are properly connected to mythic events"""
    print("\n" + "="*70)
    print("TEST: Event Integration")
    print("="*70)
    
    world = WorldCoordinator(world_size=(10, 10), seed=42)
    
    print(f"\n1. Checking event-figure connections...")
    
    events_with_participants = 0
    total_participants = 0
    
    for event in world.mythic_events:
        if 'participants' in event and event['participants']:
            events_with_participants += 1
            total_participants += len(event['participants'])
            
            if events_with_participants <= 3:  # Show first 3 events
                print(f"\n   Event: {event['name']}")
                print(f"   • Type: {event['event_type']}")
                print(f"   • Year: {event['year']}")
                print(f"   • Significance: {event['significance']}/10")
                print(f"   • Participants ({len(event['participants'])}):")
                
                for participant in event['participants']:
                    print(f"      - {participant['name']} ({participant['role']}, {participant['archetype']})")
    
    print(f"\n2. Summary:")
    print(f"   • {events_with_participants}/{len(world.mythic_events)} events have participants")
    print(f"   • Total participant assignments: {total_participants}")
    
    return events_with_participants > 0


def test_genealogy():
    """Test genealogical relationships between figures"""
    print("\n" + "="*70)
    print("TEST: Genealogy System")
    print("="*70)
    
    world = WorldCoordinator(world_size=(10, 10), seed=42)
    figures = world.historical_figures
    
    print(f"\n1. Checking genealogical connections...")
    
    figures_with_parents = [f for f in figures if f.parents is not None]
    figures_with_spouses = [f for f in figures if f.spouse is not None]
    figures_with_children = [f for f in figures if f.children]
    
    print(f"   • Figures with parents: {len(figures_with_parents)}")
    print(f"   • Figures with spouses: {len(figures_with_spouses)}")
    print(f"   • Figures with children: {len(figures_with_children)}")
    
    # Show an example family if any exists
    for figure in figures:
        if figure.parents or figure.children:
            print(f"\n2. Example Family Tree:")
            print(f"   {figure.name} {figure.title}")
            
            if figure.parents:
                mother_id, father_id = figure.parents
                mother = next((f for f in figures if f.id == mother_id), None)
                father = next((f for f in figures if f.id == father_id), None)
                
                if mother and father:
                    print(f"   • Parents:")
                    print(f"      - Mother: {mother.name} {mother.title}")
                    print(f"      - Father: {father.name} {father.title}")
            
            if figure.children:
                print(f"   • Children ({len(figure.children)}):")
                for child_id in figure.children:
                    child = next((f for f in figures if f.id == child_id), None)
                    if child:
                        print(f"      - {child.name} {child.title}")
            
            break  # Only show one example
    
    return True


def test_cultural_memory():
    """Test cultural memory system (Task 2.2)"""
    print("\n" + "="*70)
    print("TEST: Cultural Memory System (Task 2.2)")
    print("="*70)
    
    world = WorldCoordinator(world_size=(10, 10), seed=42)
    figures = world.historical_figures
    
    print(f"\n1. Checking cultural memory attributes...")
    
    has_memory_strength = sum(1 for f in figures if hasattr(f, 'memory_strength'))
    has_legendary_status = sum(1 for f in figures if hasattr(f, 'legendary_status'))
    has_cultural_influence = sum(1 for f in figures if hasattr(f, 'cultural_influence'))
    has_remembered_as = sum(1 for f in figures if hasattr(f, 'remembered_as'))
    
    print(f"   • Figures with memory_strength: {has_memory_strength}/{len(figures)}")
    print(f"   • Figures with legendary_status: {has_legendary_status}/{len(figures)}")
    print(f"   • Figures with cultural_influence: {has_cultural_influence}/{len(figures)}")
    print(f"   • Figures with remembered_as: {has_remembered_as}/{len(figures)}")
    
    print(f"\n2. Legendary status distribution:")
    status_counts = {}
    for figure in figures:
        if hasattr(figure, 'legendary_status'):
            status = figure.legendary_status
            status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {status}: {count} figures")
    
    print(f"\n3. Example cultural memory data:")
    # Show first figure with full details
    if figures:
        figure = figures[0]
        print(f"   {figure.name} {figure.title}")
        print(f"   • Memory Strength: {getattr(figure, 'memory_strength', 'N/A')}/10")
        print(f"   • Legendary Status: {getattr(figure, 'legendary_status', 'N/A')}")
        print(f"   • Remembered As: {getattr(figure, 'remembered_as', 'N/A')}")
        
        if hasattr(figure, 'cultural_influence'):
            print(f"   • Cultural Influence:")
            for race, influence in sorted(figure.cultural_influence.items(), key=lambda x: x[1], reverse=True):
                print(f"      - {race.title()}: {influence}/10")
    
    # Verify all required attributes are present
    all_have_memory = all(hasattr(f, 'memory_strength') for f in figures)
    all_have_status = all(hasattr(f, 'legendary_status') for f in figures)
    all_have_influence = all(hasattr(f, 'cultural_influence') for f in figures)
    all_have_remembered = all(hasattr(f, 'remembered_as') for f in figures)
    
    if all_have_memory and all_have_status and all_have_influence and all_have_remembered:
        print(f"\n   ✓ All figures have complete cultural memory data")
        return True
    else:
        print(f"\n   ✗ Some figures missing cultural memory attributes")
        return False


def test_serialization():
    """Test saving and loading historical figures"""
    print("\n" + "="*70)
    print("TEST: Serialization (Save/Load)")
    print("="*70)
    
    world = WorldCoordinator(world_size=(10, 10), seed=42)
    original_figures = world.historical_figures
    
    print(f"\n1. Saving {len(original_figures)} figures to test file...")
    test_file = "test_figures.json"
    save_historical_figures(original_figures, test_file)
    print(f"   ✓ Saved to {test_file}")
    
    print(f"\n2. Loading figures from test file...")
    loaded_figures = load_historical_figures(test_file)
    print(f"   ✓ Loaded {len(loaded_figures)} figures")
    
    print(f"\n3. Verifying data integrity...")
    if len(loaded_figures) != len(original_figures):
        print(f"   ✗ Count mismatch: {len(loaded_figures)} vs {len(original_figures)}")
        return False
    
    # Check first figure
    orig = original_figures[0]
    loaded = loaded_figures[0]
    
    checks = [
        ("name", orig.name == loaded.name),
        ("title", orig.title == loaded.title),
        ("race", orig.race == loaded.race),
        ("alignment", orig.alignment == loaded.alignment),
        ("birth_year", orig.birth_year == loaded.birth_year),
        ("events", len(orig.participated_in_events) == len(loaded.participated_in_events)),
    ]
    
    all_passed = True
    for field, passed in checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {field}")
        if not passed:
            all_passed = False
    
    # Clean up test file
    import os
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\n4. Cleaned up test file")
    
    return all_passed


def test_integration_with_world():
    """Test that historical figures integrate properly with world generation"""
    print("\n" + "="*70)
    print("TEST: World Integration")
    print("="*70)
    
    print("\n1. Testing world generation with historical figures...")
    world = WorldCoordinator(world_size=(15, 15), seed=123)
    
    print(f"   ✓ World generated: {len(world.hex_data)} hexes")
    print(f"   ✓ Mythic events: {len(world.mythic_events)}")
    print(f"   ✓ Historical figures: {len(world.historical_figures)}")
    
    print("\n2. Checking artifacts assigned to figures...")
    figures_with_artifacts = [f for f in world.historical_figures if f.artifacts_owned]
    
    print(f"   • {len(figures_with_artifacts)} figures own artifacts")
    
    if figures_with_artifacts:
        example = figures_with_artifacts[0]
        print(f"\n   Example: {example.name} {example.title}")
        print(f"   • Artifacts: {', '.join(example.artifacts_owned)}")
    
    print("\n3. Checking figure distribution across races...")
    race_counts = {}
    for figure in world.historical_figures:
        race_counts[figure.race] = race_counts.get(figure.race, 0) + 1
    
    for race, count in sorted(race_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {race}: {count} figures")
    
    return True


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*70)
    print("HISTORICAL FIGURE GENERATION - TEST SUITE")
    print("="*70)
    
    tests = [
        ("Basic Generation", test_figure_generation),
        ("Figure Details", test_figure_details),
        ("Event Integration", test_event_integration),
        ("Genealogy", test_genealogy),
        ("Cultural Memory (Task 2.2)", test_cultural_memory),
        ("Serialization", test_serialization),
        ("World Integration", test_integration_with_world),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
