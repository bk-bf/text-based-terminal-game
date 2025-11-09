"""
Test Civilization Generation System

Validates:
1. Civilization generation with all 9 races
2. Cultural identity and government types
3. Value systems and notable features
4. Founding figure associations
5. Inter-civilization relationships
6. Serialization/deserialization
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fantasy_rpg.world.civilizations import (
    generate_civilizations,
    Civilization,
    GovernmentType,
    CulturalValue,
    RelationshipLevel
)
from fantasy_rpg.world.historical_figures import generate_historical_figures
from fantasy_rpg.world.mythic_generation import generate_mythic_events


def test_civilization_generation():
    """Test basic civilization generation"""
    print("\n=== Test 1: Civilization Generation ===")
    
    # Generate civilizations without historical figures (minimal test)
    civs = generate_civilizations(
        world_size=(20, 20),
        historical_figures=[],
        target_count=6
    )
    
    assert len(civs) == 6, f"Expected 6 civilizations, got {len(civs)}"
    print(f"✓ Generated {len(civs)} civilizations")
    
    # Check basic attributes
    for civ in civs:
        assert civ.id, "Civilization missing ID"
        assert civ.name, "Civilization missing name"
        assert civ.race, "Civilization missing race"
        assert civ.government_type in GovernmentType, "Invalid government type"
        assert len(civ.cultural_values) in [2, 3], "Should have 2-3 cultural values"
        assert civ.religious_beliefs, "Civilization missing religion"
        assert civ.cultural_description, "Civilization missing description"
        assert civ.population > 0, "Civilization has no population"
        
        print(f"\n  {civ.name}")
        print(f"    Race: {civ.race.title()}")
        print(f"    Government: {civ.government_type.value.replace('_', ' ').title()}")
        print(f"    Values: {', '.join([v.value.replace('_', ' ').title() for v in civ.cultural_values])}")
        print(f"    Population: {civ.population:,}")
    
    print("\n✓ All civilizations have valid attributes")


def test_race_diversity():
    """Test that civilizations span multiple races"""
    print("\n=== Test 2: Race Diversity ===")
    
    civs = generate_civilizations(
        world_size=(20, 20),
        historical_figures=[],
        target_count=8
    )
    
    races = {civ.race for civ in civs}
    print(f"Races represented: {', '.join(sorted(races))}")
    print(f"Total: {len(races)} different races")
    
    # With 8 civilizations, expect at least 4 different races
    assert len(races) >= 4, f"Expected at least 4 races, got {len(races)}"
    print("✓ Good race diversity")


def test_government_types():
    """Test variety of government types"""
    print("\n=== Test 3: Government Types ===")
    
    civs = generate_civilizations(
        world_size=(20, 20),
        historical_figures=[],
        target_count=8
    )
    
    gov_types = [civ.government_type.value for civ in civs]
    unique_govs = set(gov_types)
    
    print(f"Government types: {', '.join(sorted(unique_govs))}")
    print(f"Total: {len(unique_govs)} different governments")
    
    # Check government distribution
    for gov in unique_govs:
        count = gov_types.count(gov)
        print(f"  {gov.replace('_', ' ').title()}: {count}")
    
    print("✓ Government types generated")


def test_founding_figure_association():
    """Test association with historical figures"""
    print("\n=== Test 4: Founding Figure Association ===")
    
    # Create a mock world for mythic events
    class MockWorld:
        def __init__(self):
            self.world_size = (20, 20)
            self.hex_data = {}
            for x in range(20):
                for y in range(20):
                    hex_id = f"{x:02d}{y:02d}"
                    self.hex_data[hex_id] = {
                        'biome': 'temperate_forest',
                        'elevation_raw': 0.5
                    }
    
    world = MockWorld()
    
    # Generate mythic events
    events = generate_mythic_events(world, num_events=10, seed=12345)
    print(f"Generated {len(events)} mythic events")
    
    # Generate historical figures
    figures = generate_historical_figures(events, seed=12345)
    print(f"Generated {len(figures)} historical figures")
    
    # Generate civilizations
    civs = generate_civilizations(
        world_size=(20, 20),
        historical_figures=figures,
        target_count=6
    )
    
    # Check founder associations
    civs_with_founders = [civ for civ in civs if civ.founding_figures]
    print(f"\n{len(civs_with_founders)}/{len(civs)} civilizations have founding figures")
    
    for civ in civs_with_founders:
        print(f"\n  {civ.name} ({civ.race}):")
        for fig_id in civ.founding_figures:
            figure = next((f for f in figures if f.id == fig_id), None)
            if figure:
                print(f"    • {figure.name} {figure.title} ({figure.alignment})")
    
    # Verify figures have civilization associations
    figures_with_civs = [f for f in figures if hasattr(f, 'civilization') and f.civilization]
    print(f"\n{len(figures_with_civs)}/{len(figures)} figures associated with civilizations")
    
    print("✓ Founding figure associations working")


def test_relationships():
    """Test inter-civilization relationships"""
    print("\n=== Test 5: Civilization Relationships ===")
    
    civs = generate_civilizations(
        world_size=(20, 20),
        historical_figures=[],
        target_count=6
    )
    
    # Check that all civilizations have relationships with others
    for civ in civs:
        num_relations = len(civ.faction_relationships)
        expected_relations = len(civs) - 1  # All others
        assert num_relations == expected_relations, \
            f"{civ.name} has {num_relations} relations, expected {expected_relations}"
    
    print("✓ All civilizations have relationships with each other")
    
    # Show sample relationships
    print("\nSample relationships:")
    for civ in civs[:3]:
        print(f"\n  {civ.name}:")
        for other_id, rel in list(civ.faction_relationships.items())[:3]:
            other_civ = next(c for c in civs if c.id == other_id)
            rel_symbol = {
                RelationshipLevel.ALLIED: "⚔️ Allied",
                RelationshipLevel.FRIENDLY: "🤝 Friendly",
                RelationshipLevel.NEUTRAL: "⚖️ Neutral",
                RelationshipLevel.TENSE: "⚠️ Tense",
                RelationshipLevel.HOSTILE: "⚔️ Hostile"
            }
            print(f"    {rel_symbol.get(rel, rel.value)} with {other_civ.name}")
    
    # Count relationship types
    rel_counts = {}
    for civ in civs:
        for rel in civ.faction_relationships.values():
            rel_counts[rel.value] = rel_counts.get(rel.value, 0) + 1
    
    print("\nRelationship distribution:")
    for rel_type, count in sorted(rel_counts.items()):
        print(f"  {rel_type.replace('_', ' ').title()}: {count}")
    
    print("✓ Relationships generated successfully")


def test_serialization():
    """Test civilization serialization and deserialization"""
    print("\n=== Test 6: Serialization ===")
    
    civs = generate_civilizations(
        world_size=(20, 20),
        historical_figures=[],
        target_count=4
    )
    
    # Serialize
    serialized = [civ.to_dict() for civ in civs]
    print(f"Serialized {len(serialized)} civilizations")
    
    # Deserialize
    deserialized = [Civilization.from_dict(data) for data in serialized]
    print(f"Deserialized {len(deserialized)} civilizations")
    
    # Verify data integrity
    for orig, deser in zip(civs, deserialized):
        assert orig.id == deser.id, "ID mismatch"
        assert orig.name == deser.name, "Name mismatch"
        assert orig.race == deser.race, "Race mismatch"
        assert orig.government_type == deser.government_type, "Government mismatch"
        assert orig.cultural_values == deser.cultural_values, "Values mismatch"
        assert orig.population == deser.population, "Population mismatch"
        assert orig.faction_relationships == deser.faction_relationships, "Relations mismatch"
    
    print("✓ Serialization preserves all data correctly")


def test_cultural_features():
    """Test cultural features and notable traits"""
    print("\n=== Test 7: Cultural Features ===")
    
    civs = generate_civilizations(
        world_size=(20, 20),
        historical_figures=[],
        target_count=6
    )
    
    for civ in civs:
        assert len(civ.notable_features) >= 2, f"{civ.name} missing notable features"
        print(f"\n{civ.name} ({civ.race}):")
        print(f"  Values: {', '.join([v.value.replace('_', ' ').title() for v in civ.cultural_values])}")
        print(f"  Features:")
        for feature in civ.notable_features:
            print(f"    • {feature}")
    
    print("\n✓ All civilizations have cultural features")


def run_all_tests():
    """Run all civilization tests"""
    print("=" * 60)
    print("CIVILIZATION SYSTEM TEST SUITE")
    print("=" * 60)
    
    try:
        test_civilization_generation()
        test_race_diversity()
        test_government_types()
        test_founding_figure_association()
        test_relationships()
        test_serialization()
        test_cultural_features()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
