"""
Fantasy RPG - Color Definitions

Custom color palette for survival status indicators and UI elements.
"""

# Survival Status Colors (from best to worst)
SURVIVAL_COLORS = {
    "EXCELLENT": "#00AA00",    # Dark green - excellent status
    "GOOD": "#079E00",         # Bright green - good status  
    "NORMAL": "#00FF00",       # green - neutral status
    "POOR": "#FF8800",         # Orange - warning status
    "BAD": "#FF0000",          # Red - bad status
    "CRITICAL": "#AA0000"      # Dark red - critical status
}

# Temperature Status Colors (comfortable in middle, extremes bad)
TEMPERATURE_COLORS = {
    "FREEZING": "#0066FF",     # Blue - freezing
    "VERY_COLD": "#0088FF",    # Light blue - very cold
    "COLD": "#00AAFF",         # Cyan - cold
    "COOL": "#88FFFF",         # Light cyan - cool
    "COMFORTABLE": "#00FF00",  # Green - comfortable
    "WARM": "#FFFF88",         # Light yellow - warm
    "HOT": "#FF8800",          # Orange - hot
    "VERY_HOT": "#FF4400",     # Red-orange - very hot
    "OVERHEATING": "#FF0000"   # Red - overheating
}

# Wetness Status Colors (dry is good, wet is bad)
WETNESS_COLORS = {
    "DRY": "#00FF00",          # Green - dry is good
    "DAMP": "#FFFF00",         # Yellow - slightly damp
    "WET": "#FF8800",          # Orange - wet
    "SOAKED": "#FF4400",       # Red-orange - soaked
    "DRENCHED": "#AA0000"      # Dark red - drenched
}

# UI Element Colors
UI_COLORS = {
    "separator": "#666666",     # Gray for separators
    "header": "#FFFFFF",        # White for headers
    "label": "#CCCCCC",         # Light gray for labels
    "value": "#FFFFFF",         # White for values
    "warning": "#FF8800",       # Orange for warnings
    "error": "#FF0000",         # Red for errors
    "success": "#00FF00",       # Green for success
    "info": "#00AAFF"           # Blue for info
}

# Combat Colors
COMBAT_COLORS = {
    "damage": "#FF0000",        # Red for damage
    "healing": "#00FF00",       # Green for healing
    "miss": "#888888",          # Gray for misses
    "critical": "#FFFF00",      # Yellow for critical hits
    "death": "#AA0000"          # Dark red for death
}

# Environment Colors
ENVIRONMENT_COLORS = {
    "temperature": "#FFAA00",   # Orange for temperature
    "weather": "#00AAFF",       # Blue for weather
    "elevation": "#8B4513",     # Brown for elevation
    "time": "#FFD700"           # Gold for time
}


def get_survival_color(level_name: str) -> str:
    """Get color for survival status level"""
    return SURVIVAL_COLORS.get(level_name, "#FFFFFF")


def get_temperature_color(status_name: str) -> str:
    """Get color for temperature status"""
    return TEMPERATURE_COLORS.get(status_name, "#FFFFFF")


def get_wetness_color(level_name: str) -> str:
    """Get color for wetness level"""
    return WETNESS_COLORS.get(level_name, "#FFFFFF")


def format_survival_text(text: str, level_name: str) -> str:
    """Format survival text with appropriate color"""
    color = get_survival_color(level_name)
    return f"[{color}]{text}[/]"


def format_temperature_text(text: str, status_name: str) -> str:
    """Format temperature text with appropriate color"""
    color = get_temperature_color(status_name)
    return f"[{color}]{text}[/]"


def format_wetness_text(text: str, level_name: str) -> str:
    """Format wetness text with appropriate color"""
    color = get_wetness_color(level_name)
    return f"[{color}]{text}[/]"


def format_ui_text(text: str, element_type: str) -> str:
    """Format UI text with appropriate color"""
    color = UI_COLORS.get(element_type, "#FFFFFF")
    return f"[{color}]{text}[/]"


def format_combat_text(text: str, combat_type: str) -> str:
    """Format combat text with appropriate color"""
    color = COMBAT_COLORS.get(combat_type, "#FFFFFF")
    return f"[{color}]{text}[/]"


def format_environment_text(text: str, env_type: str) -> str:
    """Format environment text with appropriate color"""
    color = ENVIRONMENT_COLORS.get(env_type, "#FFFFFF")
    return f"[{color}]{text}[/]"


# Color test function for debugging
def test_colors():
    """Test color display for debugging"""
    print("=== Survival Status Colors ===")
    for level, color in SURVIVAL_COLORS.items():
        print(f"[{color}]{level}[/] - {color}")
    
    print("\n=== Temperature Colors ===")
    for status, color in TEMPERATURE_COLORS.items():
        print(f"[{color}]{status}[/] - {color}")
    
    print("\n=== Wetness Colors ===")
    for level, color in WETNESS_COLORS.items():
        print(f"[{color}]{level}[/] - {color}")


if __name__ == "__main__":
    test_colors()