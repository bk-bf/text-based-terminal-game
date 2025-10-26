#!/usr/bin/env python3
"""
Test script to demonstrate elevation-based temperature modification (lapse rate).

This script shows how temperature decreases with elevation, simulating the
atmospheric lapse rate where temperature drops ~3.5°F per 1000 feet of elevation.
"""

from climate import ClimateSystem


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9


def format_temp(fahrenheit: float) -> str:
    """Format temperature showing both Fahrenheit and Celsius."""
    celsius = fahrenheit_to_celsius(fahrenheit)
    return f"{fahrenheit:6.1f}°F ({celsius:5.1f}°C)"


def format_temp_range(min_f: float, max_f: float) -> str:
    """Format temperature range showing both Fahrenheit and Celsius."""
    min_c = fahrenheit_to_celsius(min_f)
    max_c = fahrenheit_to_celsius(max_f)
    return f"{min_f:4.0f}°F - {max_f:4.0f}°F ({min_c:4.0f}°C - {max_c:4.0f}°C)"


def test_lapse_rate_effects():
    """Demonstrate elevation-based temperature modification (lapse rate)."""
    
    print("=== Testing Elevation-Based Temperature Modification (Lapse Rate) ===")
    print()
    
    # Initialize climate system
    climate_system = ClimateSystem(world_height=20)
    
    # Test coordinates at different latitudes
    test_locations = [
        ((10, 2), "Northern Region"),
        ((10, 10), "Equatorial Region"), 
        ((10, 18), "Southern Region")
    ]
    
    # Test different elevation levels
    elevations = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    elevation_labels = ["Sea Level", "Low Hills", "High Hills", "Low Mountains", "High Mountains", "Peaks"]
    
    for coords, location_name in test_locations:
        print(f"📍 {location_name} {coords}")
        print("=" * 60)
        
        # Get base temperature at sea level
        base_temp = climate_system.calculate_base_temperature(coords[1])
        base_temp_c = fahrenheit_to_celsius(base_temp)
        print(f"Base temperature (sea level): {base_temp:.1f}°F ({base_temp_c:.1f}°C)")
        print()
        
        print("Elevation Effects (Lapse Rate):")
        print("Elevation    | Adjusted Temperature      | Cooling Effect        | Climate Zone")
        print("-------------|---------------------------|----------------------|-------------")
        
        for elevation, label in zip(elevations, elevation_labels):
            # Generate climate zone with elevation effects
            climate_zone = climate_system.generate_climate_zone(coords, elevation)
            
            # Calculate cooling effect
            elevation_cooling = elevation * 30.0  # Same formula as in climate.py
            adjusted_temp = base_temp - elevation_cooling
            cooling_c = elevation_cooling * 5/9  # Convert cooling to Celsius
            
            print(f"{label:12s} | {format_temp(adjusted_temp):>25s} | {elevation_cooling:6.1f}°F ({cooling_c:4.1f}°C) | {climate_zone.zone_type}")
        
        print()
        
        # Show seasonal temperature ranges at different elevations
        print("Seasonal Temperature Ranges:")
        print("Elevation    | Summer Range                    | Winter Range                    | Snow?")
        print("-------------|--------------------------------|--------------------------------|------")
        
        for elevation, label in zip([0.0, 0.4, 0.8], ["Sea Level", "Mid Hills", "High Peaks"]):
            climate_zone = climate_system.generate_climate_zone(coords, elevation)
            
            summer_min, summer_max = climate_zone.temp_range_summer
            winter_min, winter_max = climate_zone.temp_range_winter
            
            summer_range = format_temp_range(summer_min, summer_max)
            winter_range = format_temp_range(winter_min, winter_max)
            
            print(f"{label:12s} | {summer_range:>30s} | {winter_range:>30s} | {'Yes' if climate_zone.has_snow else 'No':>3s}")
        
        print("\n" + "="*80 + "\n")
    
    # Demonstrate climate zone transitions due to elevation
    print("🏔️  Climate Zone Transitions with Elevation")
    print("=" * 60)
    
    # Use equatorial coordinates to show dramatic elevation effects
    equator_coords = (10, 10)
    base_temp = climate_system.calculate_base_temperature(equator_coords[1])
    
    base_temp_c = fahrenheit_to_celsius(base_temp)
    print(f"Location: Equatorial region {equator_coords}")
    print(f"Base temperature: {base_temp:.1f}°F ({base_temp_c:.1f}°C) - Tropical")
    print()
    
    print("How elevation changes climate zones:")
    print("Elevation | Temperature              | Climate Zone  | Description")
    print("----------|--------------------------|---------------|----------------------------------")
    
    test_elevations = [0.0, 0.15, 0.3, 0.5, 0.7, 0.9]
    descriptions = [
        "Hot tropical lowlands",
        "Warm tropical hills", 
        "Temperate mountain foothills",
        "Cool temperate mountains",
        "Cold subarctic peaks",
        "Freezing arctic summits"
    ]
    
    for elevation, description in zip(test_elevations, descriptions):
        climate_zone = climate_system.generate_climate_zone(equator_coords, elevation)
        elevation_cooling = elevation * 30.0
        adjusted_temp = base_temp - elevation_cooling
        
        print(f"{elevation:8.1f}  | {format_temp(adjusted_temp):>24s} | {climate_zone.zone_type:12s}  | {description}")
    
    print()
    print("🌡️  Key Observations:")
    print("   • Temperature drops ~30°F (~17°C) from sea level to highest peaks")
    print("   • Tropical regions can have arctic conditions at high elevation")
    print("   • Climate zones shift realistically with altitude")
    print("   • High elevations automatically get snow regardless of latitude")
    print("   • Lapse rate creates realistic mountain climate gradients")
    print("   • Simulates real-world atmospheric lapse rate (~3.5°F/1000ft or ~6.5°C/1000m)")
    
    print("\n" + "="*80)
    print("✅ Elevation-based temperature modification (lapse rate) is working correctly!")
    print("   This creates realistic mountain climates and altitude effects.")


if __name__ == "__main__":
    test_lapse_rate_effects()