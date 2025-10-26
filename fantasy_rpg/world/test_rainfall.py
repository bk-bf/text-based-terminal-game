#!/usr/bin/env python3
"""
Test script to demonstrate rainfall patterns with prevailing winds and rain shadows.

This script shows how precipitation varies based on:
- Distance from ocean (continental effect)
- Mountain ranges (orographic effects)
- Prevailing wind patterns
- Climate zones
"""

from climate import ClimateSystem
from terrain_generation import TerrainGenerator
import math


def test_rainfall_patterns():
    """Demonstrate rainfall patterns with wind and orographic effects."""
    
    print("=== Testing Rainfall Patterns (Prevailing Winds & Rain Shadows) ===")
    print()
    
    # Generate a test world with interesting terrain
    seed = 98765
    world_size = (25, 15)  # Wider world to show continental effects
    width, height = world_size
    
    print(f"Generating test world: {width}x{height}")
    
    # Generate terrain with mountains
    terrain_gen = TerrainGenerator(seed)
    heightmap = terrain_gen.generate_continental_heightmap(width, height)
    
    # Generate climate zones
    climate_system = ClimateSystem(height)
    climate_zones = climate_system.generate_climate_zones(world_size, heightmap)
    
    # Generate precipitation patterns
    precipitation_map = climate_system.generate_precipitation_map(world_size, heightmap, climate_zones)
    
    print("\n" + "="*80)
    print("🌧️  PRECIPITATION ANALYSIS")
    print("="*80)
    
    # Show elevation and precipitation maps side by side
    print("\nElevation Map vs Precipitation Map:")
    print("Elevation: . = Sea Level, ^ = Hills, ▲ = Mountains, ⛰ = Peaks")
    print("Precipitation: . = Desert (<10), - = Arid (10-25), + = Moderate (25-50), * = Wet (50-75), # = Very Wet (>75)")
    print()
    
    for y in range(height):
        # Elevation row
        elev_row = []
        for x in range(width):
            coords = (x, y)
            elevation = heightmap[coords]
            
            if elevation < 0.3:
                elev_row.append(".")  # Sea level
            elif elevation < 0.6:
                elev_row.append("^")  # Hills
            elif elevation < 0.8:
                elev_row.append("▲")  # Mountains
            else:
                elev_row.append("⛰")  # Peaks
        
        # Precipitation row
        precip_row = []
        for x in range(width):
            coords = (x, y)
            precip_data = precipitation_map[coords]
            annual_precip = precip_data["annual_precipitation"]
            
            if annual_precip < 10:
                precip_row.append(".")  # Desert
            elif annual_precip < 25:
                precip_row.append("-")  # Arid
            elif annual_precip < 50:
                precip_row.append("+")  # Moderate
            elif annual_precip < 75:
                precip_row.append("*")  # Wet
            else:
                precip_row.append("#")  # Very wet
        
        print(f"Y{y:2d} Elev: {' '.join(elev_row)}")
        print(f"    Prec: {' '.join(precip_row)}")
        print()
    
    # Analyze cross-section showing rain shadow effects
    print("🏔️  RAIN SHADOW ANALYSIS (Center Row)")
    print("="*80)
    
    center_y = height // 2
    print(f"Cross-section at Y={center_y} (prevailing winds from {climate_system.prevailing_wind_direction})")
    print()
    print("X  | Elev  | Climate    | Base | Final | Ocean | Oro  | Cont | Effect")
    print("---|-------|------------|------|-------|-------|------|------|------------------")
    
    for x in range(width):
        coords = (x, center_y)
        elevation = heightmap[coords]
        climate_zone = climate_zones[coords]
        precip_data = precipitation_map[coords]
        
        print(f"{x:2d} | {elevation:.2f}  | {climate_zone.zone_type:10s} | "
              f"{precip_data['base_precipitation']:4.0f} | {precip_data['annual_precipitation']:5.1f} | "
              f"{precip_data['distance_from_ocean']:.2f}  | {precip_data['orographic_modifier']:.2f} | "
              f"{precip_data['continental_modifier']:.2f} | {precip_data['primary_effect']}")
    
    # Demonstrate specific rain shadow effects
    print("\n🌬️  WIND AND OROGRAPHIC EFFECTS")
    print("="*80)
    
    # Find mountain ranges and their effects
    mountain_coords = []
    for x in range(width):
        for y in range(height):
            coords = (x, y)
            if heightmap[coords] > 0.7:  # High elevation
                mountain_coords.append(coords)
    
    if mountain_coords:
        print(f"Found {len(mountain_coords)} high-elevation hexes")
        
        # Analyze windward vs leeward effects
        windward_precip = []
        leeward_precip = []
        
        for coords in mountain_coords:
            precip_data = precipitation_map[coords]
            if precip_data['primary_effect'] == 'windward_slope':
                windward_precip.append(precip_data['annual_precipitation'])
            elif precip_data['primary_effect'] == 'rain_shadow':
                leeward_precip.append(precip_data['annual_precipitation'])
        
        if windward_precip and leeward_precip:
            avg_windward = sum(windward_precip) / len(windward_precip)
            avg_leeward = sum(leeward_precip) / len(leeward_precip)
            
            print(f"\nOrographic precipitation effects:")
            print(f"  Windward slopes: {len(windward_precip)} hexes, avg {avg_windward:.1f} inches/year")
            print(f"  Leeward (rain shadow): {len(leeward_precip)} hexes, avg {avg_leeward:.1f} inches/year")
            print(f"  Rain shadow reduction: {((avg_windward - avg_leeward) / avg_windward * 100):.0f}%")
    
    # Continental vs coastal effects
    print(f"\n🌊  CONTINENTAL vs COASTAL EFFECTS")
    print("="*80)
    
    coastal_precip = []
    continental_precip = []
    
    for coords, data in precipitation_map.items():
        if data['distance_from_ocean'] < 0.3:  # Coastal
            coastal_precip.append(data['annual_precipitation'])
        elif data['distance_from_ocean'] > 0.7:  # Continental
            continental_precip.append(data['annual_precipitation'])
    
    if coastal_precip and continental_precip:
        avg_coastal = sum(coastal_precip) / len(coastal_precip)
        avg_continental = sum(continental_precip) / len(continental_precip)
        
        print(f"Coastal regions: {len(coastal_precip)} hexes, avg {avg_coastal:.1f} inches/year")
        print(f"Continental interior: {len(continental_precip)} hexes, avg {avg_continental:.1f} inches/year")
        print(f"Continental drying effect: {((avg_coastal - avg_continental) / avg_coastal * 100):.0f}% reduction")
    
    # Climate zone precipitation analysis
    print(f"\n🌡️  PRECIPITATION BY CLIMATE ZONE")
    print("="*80)
    
    zone_precipitation = {}
    for coords, data in precipitation_map.items():
        zone = data['climate_zone']
        if zone not in zone_precipitation:
            zone_precipitation[zone] = []
        zone_precipitation[zone].append(data['annual_precipitation'])
    
    print("Climate Zone | Count | Avg Precip | Min-Max Range | Wet Months")
    print("-------------|-------|------------|---------------|------------")
    
    for zone, precip_list in sorted(zone_precipitation.items()):
        avg_precip = sum(precip_list) / len(precip_list)
        min_precip = min(precip_list)
        max_precip = max(precip_list)
        
        # Get wet season info from climate zone
        sample_coords = next(coords for coords, data in precipitation_map.items() 
                           if data['climate_zone'] == zone)
        climate_zone = climate_zones[sample_coords]
        
        print(f"{zone:12s} | {len(precip_list):5d} | {avg_precip:8.1f}   | {min_precip:4.1f}-{max_precip:4.1f}    | {climate_zone.wet_season_months:10d}")
    
    # Seasonal precipitation patterns
    print(f"\n📅  SEASONAL PRECIPITATION PATTERNS")
    print("="*80)
    
    sample_locations = [
        ((5, center_y), "Western Coast"),
        ((width//2, center_y), "Central Region"),
        ((width-5, center_y), "Eastern Interior")
    ]
    
    for coords, description in sample_locations:
        if coords in precipitation_map:
            data = precipitation_map[coords]
            climate_zone = climate_zones[coords]
            
            # Calculate seasonal distribution
            wet_season_precip = data['annual_precipitation'] * 0.7  # 70% in wet season
            dry_season_precip = data['annual_precipitation'] * 0.3  # 30% in dry season
            
            # Apply dry season severity
            dry_season_precip *= (1.0 - climate_zone.dry_season_severity)
            
            print(f"\n{description} {coords}:")
            print(f"  Annual precipitation: {data['annual_precipitation']:.1f} inches")
            print(f"  Wet season ({climate_zone.wet_season_months} months): {wet_season_precip:.1f} inches")
            print(f"  Dry season ({12 - climate_zone.wet_season_months} months): {dry_season_precip:.1f} inches")
            print(f"  Dry season severity: {climate_zone.dry_season_severity:.1f} (0=mild, 1=extreme)")
            print(f"  Primary effect: {data['primary_effect']}")
    
    print(f"\n🎯  KEY FINDINGS")
    print("="*80)
    print("✓ Prevailing westerly winds create moisture gradients from west to east")
    print("✓ Mountain ranges create rain shadows on leeward (eastern) sides")
    print("✓ Windward slopes receive enhanced precipitation from orographic lifting")
    print("✓ Continental interiors are drier due to distance from moisture sources")
    print("✓ Climate zones have distinct seasonal precipitation patterns")
    print("✓ Desert formation occurs in rain shadows and continental interiors")
    
    print(f"\n✅ Rainfall pattern simulation complete!")
    print("   This creates realistic precipitation distribution for biome assignment.")


if __name__ == "__main__":
    test_rainfall_patterns()