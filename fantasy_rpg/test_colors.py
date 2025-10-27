#!/usr/bin/env python3
"""
Test script to verify custom color system
"""

def test_colors():
    """Test the custom color system"""
    print("=== Testing Custom Color System ===")
    
    try:
        from ui.colors import (
            format_survival_text, 
            format_temperature_text, 
            format_wetness_text,
            SURVIVAL_COLORS,
            TEMPERATURE_COLORS,
            WETNESS_COLORS
        )
        
        print("✓ Color module imported successfully")
        
        print("\n=== Survival Status Colors ===")
        survival_levels = ["EXCELLENT", "GOOD", "NORMAL", "POOR", "BAD", "CRITICAL"]
        for level in survival_levels:
            colored_text = format_survival_text(level, level)
            hex_color = SURVIVAL_COLORS.get(level, "#FFFFFF")
            print(f"{colored_text} - {hex_color}")
        
        print("\n=== Temperature Status Colors ===")
        temp_statuses = ["FREEZING", "VERY_COLD", "COLD", "COOL", "COMFORTABLE", "WARM", "HOT", "VERY_HOT", "OVERHEATING"]
        for status in temp_statuses:
            colored_text = format_temperature_text(status, status)
            hex_color = TEMPERATURE_COLORS.get(status, "#FFFFFF")
            print(f"{colored_text} - {hex_color}")
        
        print("\n=== Wetness Status Colors ===")
        wetness_levels = ["DRY", "DAMP", "WET", "SOAKED", "DRENCHED"]
        for level in wetness_levels:
            colored_text = format_wetness_text(level, level)
            hex_color = WETNESS_COLORS.get(level, "#FFFFFF")
            print(f"{colored_text} - {hex_color}")
        
        print("\n=== Sample Survival Display ===")
        print("survival:")
        print(f"Hunger: {format_survival_text('Satiated', 'EXCELLENT')}")
        print(f"Thirst: {format_survival_text('Well-fed', 'GOOD')}")
        print(f"Fatigue: {format_survival_text('Content', 'NORMAL')}")
        print(f"Warmth: {format_temperature_text('Pleasant', 'COMFORTABLE')}")
        print(f"Dryness: {format_wetness_text('Dry', 'DRY')}")
        
        print("\n✓ All color tests passed!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing Fantasy RPG Custom Color System")
    print("=" * 50)
    
    success = test_colors()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Color system working correctly!")
        print("\nNow run the main UI to see colors in action:")
        print("python ui/app.py")
    else:
        print("⚠ Color system test failed - check output above")