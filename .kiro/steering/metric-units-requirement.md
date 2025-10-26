# Metric Units Requirement for Debug Code

## Always Include Metric Units

When writing debug output, test scripts, or any code that displays measurements, **always include metric units alongside US units** to ensure international accessibility and understanding.

## Temperature Display

**Required Format:**
```python
# ✅ CORRECT - Show both Fahrenheit and Celsius
print(f"Temperature: {temp_f:.1f}°F ({temp_c:.1f}°C)")
print(f"Range: {min_f:.0f}-{max_f:.0f}°F ({min_c:.0f}-{max_c:.0f}°C)")

# ❌ INCORRECT - Fahrenheit only
print(f"Temperature: {temp_f:.1f}°F")
```

**Conversion Function:**
```python
def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9

def format_temp(fahrenheit: float) -> str:
    """Format temperature showing both Fahrenheit and Celsius."""
    celsius = fahrenheit_to_celsius(fahrenheit)
    return f"{fahrenheit:6.1f}°F ({celsius:5.1f}°C)"
```

## Distance and Elevation

**Required Format:**
```python
# ✅ CORRECT - Show both imperial and metric
print(f"Elevation: {feet:.0f} feet ({meters:.0f} meters)")
print(f"Distance: {miles:.1f} miles ({kilometers:.1f} km)")

# ❌ INCORRECT - Imperial only
print(f"Elevation: {feet:.0f} feet")
```

## Precipitation

**Required Format:**
```python
# ✅ CORRECT - Show both inches and millimeters
print(f"Annual precipitation: {inches:.1f} inches ({mm:.0f} mm)")

# Conversion: 1 inch = 25.4 mm
mm = inches * 25.4
```

## Speed and Pressure

**Required Format:**
```python
# ✅ CORRECT - Wind speed in both units
print(f"Wind: {mph:.0f} mph ({kmh:.0f} km/h)")

# ✅ CORRECT - Pressure in both units  
print(f"Pressure: {inches_hg:.2f} inHg ({mb:.0f} mb)")
```

## Implementation Guidelines

### 1. Create Helper Functions
Always create conversion and formatting helper functions at the top of test scripts:

```python
def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32) * 5/9

def inches_to_mm(inches: float) -> float:
    return inches * 25.4

def feet_to_meters(feet: float) -> float:
    return feet * 0.3048

def miles_to_km(miles: float) -> float:
    return miles * 1.609344

def format_temp(f: float) -> str:
    c = fahrenheit_to_celsius(f)
    return f"{f:.1f}°F ({c:.1f}°C)"

def format_distance(miles: float) -> str:
    km = miles_to_km(miles)
    return f"{miles:.1f} miles ({km:.1f} km)"

def format_precipitation(inches: float) -> str:
    mm = inches_to_mm(inches)
    return f"{inches:.1f} inches ({mm:.0f} mm)"
```

### 2. Use in All Debug Output
Apply these functions consistently in:
- Test scripts
- Debug print statements
- Climate system output
- World generation statistics
- Environmental analysis
- Performance benchmarks

### 3. Table Headers
When creating tables, include both unit systems:

```python
print("Location | Temperature        | Precipitation      | Elevation")
print("---------|--------------------|--------------------|------------------")
print(f"{name:8s} | {format_temp(temp):>18s} | {format_precipitation(precip):>18s} | {format_elevation(elev):>16s}")
```

## Rationale

- **International Accessibility**: Metric system is used by most of the world
- **Scientific Accuracy**: Metric units are standard in scientific contexts
- **User Understanding**: Ensures all users can understand the measurements
- **Professional Standards**: Shows attention to international standards

## Examples in Context

### Climate System Debug Output
```python
print(f"Base temperature (sea level): {base_temp:.1f}°F ({base_temp_c:.1f}°C)")
print(f"Elevation cooling: {cooling_f:.1f}°F ({cooling_c:.1f}°C)")
print(f"Annual precipitation: {precip_in:.1f} inches ({precip_mm:.0f} mm)")
```

### World Generation Statistics
```python
print(f"World size: {width}x{height} hexes ({width*hex_size_km:.0f}x{height*hex_size_km:.0f} km)")
print(f"Temperature range: {min_temp_f:.0f}-{max_temp_f:.0f}°F ({min_temp_c:.0f}-{max_temp_c:.0f}°C)")
print(f"Precipitation range: {min_precip_in:.0f}-{max_precip_in:.0f} inches ({min_precip_mm:.0f}-{max_precip_mm:.0f} mm)")
```

### Environmental Analysis
```python
print(f"Lapse rate: {lapse_f:.1f}°F per 1000 feet ({lapse_c:.1f}°C per 1000 meters)")
print(f"Rain shadow effect: {reduction_percent:.0f}% precipitation reduction")
```

This ensures that all debug output and test results are accessible to users regardless of their familiarity with US measurement systems.