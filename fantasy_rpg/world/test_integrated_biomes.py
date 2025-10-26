#!/usr/bin/env python3
"""
Test script to demonstrate integrated biome systems.

This shows how the Whittaker classification system and Enhanced biome system
work together to provide both scientific accuracy and rich gameplay mechanics.
"""

from climate import ClimateSystem
from terrain_generation import TerrainGenerator
from biomes import BiomeClassifier
from enhanced_biomes import fahrenheit_to_celsius, inches_to_mm, format_temp, format_precipitation


def test_integrated_biome_systems():
    """Test both biome systems and their integration."""
    
    print("=== Testing Integrated Biome Systems ===")
    print()
    print("This demonstrates how two biome systems work together:")
    print("1. Whittaker Classification (13 biomes) - Scientific accuracy")
    print("2. Enhanced Biomes (8 biomes) - Rich gameplay mechanics")
    print()
    
    # Generate test world
    seed = 77777
    world_size = (20, 15)
    width, height = world_size
    
    print(f"Generating test world: {width}x{height}")
    
    # Generate terrain and climate
    terrain_gen = TerrainGenerator(seed)
    heightmap = terrain_gen.generate_continental_heightmap(width, height)
    
    climate_system = ClimateSystem(height)
    climate_zones = climate_system.generate_climate_zones(world_size, heightmap)
    precipitation_map = climate_system.generate_precipitation_map(world_size, heightmap, climate_zones)
    
    print("\n" + "="*80)
    print("🔬 WHITTAKER CLASSIFICATION SYSTEM (Scientific)")
    print("="*80)
    
    # Test Whittaker system (13 biomes)
    whittaker_classifier = BiomeClassifier(use_enhanced_biomes=False)
    whittaker_biomes = whittaker_classifier.generate_biome_map(world_size, climate_zones, precipitation_map, heightmap)
    
    print("\n" + "="*80)
    print("🎮 ENHANCED BIOME SYSTEM (Gameplay)")
    print("="*80)
    
    # Test Enhanced system (8 biomes)
    enhanced_classifier = BiomeClassifier(use_enhanced_biomes=True)
    enhanced_biomes = enhanced_classifier.generate_biome_map(world_size, climate_zones, precipitation_map, heightmap)
    
    print("\n" + "="*80)
    print("📊 SYSTEM COMPARISON")
    print("="*80)
    
    # Compare biome distributions
    whittaker_counts = {}
    enhanced_counts = {}
    
    for coords in heightmap.keys():
        w_biome = whittaker_biomes[coords]
        e_biome = enhanced_biomes[coords]
        
        whittaker_counts[w_biome] = whittaker_counts.get(w_biome, 0) + 1
        enhanced_counts[e_biome] = enhanced_counts.get(e_biome, 0) + 1
    
    print("Whittaker System (13 biomes):")
    for biome, count in sorted(whittaker_counts.items()):
        percentage = (count / len(heightmap)) * 100
        display_name = biome.replace('_', ' ').title()
        print(f"  {display_name}: {count} hexes ({percentage:.1f}%)")
    
    print(f"\nEnhanced System (8 biomes):")
    for biome, count in sorted(enhanced_counts.items()):
        percentage = (count / len(heightmap)) * 100
        biome_info = enhanced_classifier.get_biome_info(biome)
        display_name = biome_info.display_name if biome_info else biome.replace('_', ' ').title()
        print(f"  {display_name}: {count} hexes ({percentage:.1f}%)")
    
    # Visual comparison
    print(f"\n🗺️  BIOME MAP COMPARISON")
    print("="*80)
    
    # Whittaker symbols
    whittaker_symbols = {
        "tundra": "T", "taiga": "B", "temperate_deciduous_forest": "F",
        "temperate_coniferous_forest": "C", "temperate_grassland": "G",
        "mediterranean_scrub": "S", "tropical_rainforest": "J",
        "tropical_seasonal_forest": "R", "tropical_savanna": "V",
        "hot_desert": "D", "cold_desert": "d", "alpine": "A", "wetland": "W"
    }
    
    # Enhanced symbols
    enhanced_symbols = {
        "arctic_tundra": "T", "boreal_forest": "B", "temperate_grassland": "G",
        "temperate_forest": "F", "mediterranean_scrub": "S", "hot_desert": "D",
        "tropical_rainforest": "J", "alpine_mountains": "A"
    }
    
    print("Whittaker Classification (13 biomes):")
    for y in range(height):
        row = []
        for x in range(width):
            coords = (x, y)
            biome = whittaker_biomes[coords]
            symbol = whittaker_symbols.get(biome, "?")
            row.append(symbol)
        print(f"Y{y:2d}: {' '.join(row)}")
    
    print(f"\nEnhanced System (8 biomes):")
    for y in range(height):
        row = []
        for x in range(width):
            coords = (x, y)
            biome = enhanced_biomes[coords]
            symbol = enhanced_symbols.get(biome, "?")
            row.append(symbol)
        print(f"Y{y:2d}: {' '.join(row)}")
    
    # Detailed comparison for sample locations
    print(f"\n🔍 DETAILED COMPARISON (Sample Locations)")
    print("="*80)
    
    sample_coords = [(5, 3), (10, 7), (15, 11)]
    
    print("Location | Climate | Whittaker Biome        | Enhanced Biome      | Gameplay Properties")
    print("---------|---------|------------------------|---------------------|--------------------")
    
    for coords in sample_coords:
        climate_zone = climate_zones[coords]
        precip_data = precipitation_map[coords]
        elevation = heightmap[coords]
        
        w_biome = whittaker_biomes[coords]
        e_biome = enhanced_biomes[coords]
        
        temp_c = fahrenheit_to_celsius(climate_zone.base_temperature)
        precip_mm = inches_to_mm(precip_data["annual_precipitation"])
        
        # Get enhanced biome info
        e_biome_info = enhanced_classifier.get_biome_info(e_biome)
        
        if e_biome_info:
            travel_speed = f"{e_biome_info.base_travel_speed:.1f}x speed"
            settlement = f"{e_biome_info.settlement_suitability:.1f}/1.0 suitable"
            gameplay = f"{travel_speed}, {settlement}"
        else:
            gameplay = "No enhanced data"
        
        w_display = w_biome.replace('_', ' ').title()
        e_display = e_biome_info.display_name if e_biome_info else e_biome.replace('_', ' ').title()
        
        print(f"{coords!s:8s} | {climate_zone.zone_type:7s} | {w_display:22s} | {e_display:19s} | {gameplay}")
    
    # Gameplay mechanics demonstration
    print(f"\n🎮 ENHANCED BIOME GAMEPLAY MECHANICS")
    print("="*80)
    
    # Find different enhanced biomes in the world
    unique_enhanced_biomes = set(enhanced_biomes.values())
    
    for biome_name in sorted(unique_enhanced_biomes):
        biome_info = enhanced_classifier.get_biome_info(biome_name)
        if biome_info:
            print(f"\n{biome_info.display_name}:")
            print(f"  Travel Speed: {biome_info.base_travel_speed:.1f}x base speed")
            print(f"  Visibility: {biome_info.visibility_range:,} meters")
            print(f"  Settlement Suitability: {biome_info.settlement_suitability:.1f}/1.0")
            
            # Key resources
            key_resources = [r.resource_type.value for r in biome_info.resources if r.abundance > 0.6]
            if key_resources:
                print(f"  Abundant Resources: {', '.join(key_resources)}")
            
            # Major hazards
            major_hazards = [h.hazard_type.value.replace('_', ' ') for h in biome_info.hazards if h.frequency > 0.5]
            if major_hazards:
                print(f"  Major Hazards: {', '.join(major_hazards)}")
    
    print(f"\n🎯 INTEGRATION BENEFITS")
    print("="*80)
    print("✓ Whittaker System: Provides scientific accuracy and realistic biome distribution")
    print("✓ Enhanced System: Adds rich gameplay mechanics and environmental properties")
    print("✓ Flexible Integration: Can switch between systems based on gameplay needs")
    print("✓ Consistent Climate Input: Both systems use same temperature/precipitation data")
    print("✓ Complementary Strengths: Scientific realism + gameplay depth")
    
    print(f"\n💡 USAGE RECOMMENDATIONS")
    print("="*80)
    print("• Use Whittaker (13 biomes) for: Realistic world generation, scientific accuracy")
    print("• Use Enhanced (8 biomes) for: Rich gameplay, survival mechanics, settlement planning")
    print("• Switch systems based on: Game phase (exploration vs. settlement vs. survival)")
    print("• Combine data: Use Whittaker for world gen, Enhanced for gameplay mechanics")
    
    print(f"\n✅ Integrated biome systems test complete!")
    print("   Both systems work together to provide scientific accuracy and gameplay depth.")


if __name__ == "__main__":
    test_integrated_biome_systems()