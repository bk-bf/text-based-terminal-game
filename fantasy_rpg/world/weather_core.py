"""
Fantasy RPG - Core Weather System

Core weather data structures and basic weather generation functionality.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random
import math


@dataclass
class WeatherState:
    """Complete weather snapshot for text RPG"""
    temperature: float  # °F
    wind_speed: int  # mph
    wind_direction: str  # N, NE, E, SE, S, SW, W, NW
    precipitation: int  # 0 (none) to 100 (torrential)
    precipitation_type: str  # "rain", "snow", "sleet", "hail"
    cloud_cover: int  # 0 (clear) to 100 (overcast)
    visibility: int  # feet
    
    # Derived conditions
    feels_like: float  # Wind chill / heat index
    is_storm: bool
    lightning_risk: float  # 0.0-1.0
    
    def __post_init__(self):
        """Calculate derived weather conditions after initialization."""
        self.feels_like = self._calculate_feels_like()
        self.is_storm = self._determine_storm_conditions()
        self.lightning_risk = self._calculate_lightning_risk()
    
    def _calculate_feels_like(self) -> float:
        """Calculate wind chill or heat index based on temperature and conditions."""
        if self.temperature <= 50:
            # Wind chill calculation for cold temperatures
            if self.wind_speed > 3:
                # Wind chill formula (simplified)
                wind_chill = 35.74 + (0.6215 * self.temperature) - (35.75 * (self.wind_speed ** 0.16)) + (0.4275 * self.temperature * (self.wind_speed ** 0.16))
                return min(wind_chill, self.temperature)  # Wind chill can't be higher than actual temp
            else:
                return self.temperature
        elif self.temperature >= 80:
            # Heat index calculation for hot temperatures
            if self.precipitation > 20:  # High humidity from precipitation
                # Simplified heat index calculation
                humidity_factor = min(self.precipitation, 80) / 100  # Convert to 0-0.8 range
                heat_index = self.temperature + (humidity_factor * 15)  # Add up to 15°F for humidity
                return heat_index
            else:
                return self.temperature
        else:
            # Moderate temperatures - feels like actual temperature
            return self.temperature
    
    def _determine_storm_conditions(self) -> bool:
        """Determine if current conditions constitute a storm."""
        # Storm conditions: high wind + precipitation, or very high wind alone
        high_wind_storm = self.wind_speed >= 35
        precipitation_storm = self.wind_speed >= 20 and self.precipitation >= 50
        return high_wind_storm or precipitation_storm
    
    def _calculate_lightning_risk(self) -> float:
        """Calculate lightning risk based on weather conditions."""
        if self.precipitation_type != "rain":
            return 0.0
        
        # Lightning risk increases with precipitation intensity and storm conditions
        base_risk = min(self.precipitation / 100, 0.8)  # Max 0.8 from precipitation
        
        if self.is_storm:
            base_risk += 0.3  # Storm bonus
        
        if self.cloud_cover >= 80:
            base_risk += 0.2  # Heavy cloud bonus
        
        return min(base_risk, 1.0)
    
    def _format_temperature(self, temp_f: float) -> str:
        """Format temperature showing both Fahrenheit and Celsius."""
        temp_c = (temp_f - 32) * 5/9
        return f"{temp_f:.0f}°F ({temp_c:.0f}°C)"
    
    def get_description(self) -> str:
        """Generate detailed weather description for text display."""
        desc_parts = []
        
        # Temperature description
        if self.feels_like != self.temperature:
            desc_parts.append(f"Temperature: {self._format_temperature(self.temperature)}, feels like {self._format_temperature(self.feels_like)}")
        else:
            desc_parts.append(f"Temperature: {self._format_temperature(self.temperature)}")
        
        # Wind description
        wind_desc = self._get_wind_description()
        desc_parts.append(f"Wind: {wind_desc}")
        
        # Precipitation description
        if self.precipitation > 0:
            precip_desc = self._get_precipitation_description()
            desc_parts.append(f"Precipitation: {precip_desc}")
        
        # Cloud cover description
        cloud_desc = self._get_cloud_description()
        desc_parts.append(f"Sky: {cloud_desc}")
        
        # Visibility description
        if self.visibility < 1000:
            vis_desc = self._get_visibility_description()
            desc_parts.append(f"Visibility: {vis_desc}")
        
        # Storm warning
        if self.is_storm:
            desc_parts.append("⚠️  STORM CONDITIONS")
        
        # Lightning warning
        if self.lightning_risk > 0.5:
            desc_parts.append("⚡ Lightning risk: HIGH")
        elif self.lightning_risk > 0.2:
            desc_parts.append("⚡ Lightning risk: moderate")
        
        return "\n".join(desc_parts)
    
    def _get_wind_description(self) -> str:
        """Get descriptive wind conditions."""
        if self.wind_speed == 0:
            return "Calm"
        elif self.wind_speed <= 5:
            return f"Light breeze from the {self.wind_direction.lower()} ({self.wind_speed} mph)"
        elif self.wind_speed <= 15:
            return f"Moderate wind from the {self.wind_direction.lower()} ({self.wind_speed} mph)"
        elif self.wind_speed <= 25:
            return f"Strong wind from the {self.wind_direction.lower()} ({self.wind_speed} mph)"
        elif self.wind_speed <= 35:
            return f"Very strong wind from the {self.wind_direction.lower()} ({self.wind_speed} mph)"
        else:
            return f"Gale force winds from the {self.wind_direction.lower()} ({self.wind_speed} mph)"
    
    def _get_precipitation_description(self) -> str:
        """Get descriptive precipitation conditions."""
        if self.precipitation <= 10:
            intensity = "Light"
        elif self.precipitation <= 30:
            intensity = "Moderate"
        elif self.precipitation <= 60:
            intensity = "Heavy"
        else:
            intensity = "Torrential"
        
        return f"{intensity} {self.precipitation_type}"
    
    def _get_cloud_description(self) -> str:
        """Get descriptive cloud conditions."""
        if self.cloud_cover <= 10:
            return "Clear skies"
        elif self.cloud_cover <= 30:
            return "Partly cloudy"
        elif self.cloud_cover <= 60:
            return "Mostly cloudy"
        elif self.cloud_cover <= 80:
            return "Overcast"
        else:
            return "Heavy overcast"
    
    def _get_visibility_description(self) -> str:
        """Get descriptive visibility conditions."""
        if self.visibility >= 1000:
            return "Good"
        elif self.visibility >= 500:
            return f"Limited ({self.visibility} feet)"
        elif self.visibility >= 200:
            return f"Poor ({self.visibility} feet)"
        else:
            return f"Very poor ({self.visibility} feet)"
    
    def get_travel_modifier(self) -> Dict[str, float]:
        """Calculate travel modifiers based on weather conditions."""
        speed_penalty = 1.0
        visibility_penalty = 1.0
        safety_penalty = 1.0
        
        # Temperature effects
        if self.feels_like < 20:  # Extreme cold
            speed_penalty *= 0.7
            safety_penalty *= 0.8
        elif self.feels_like > 100:  # Extreme heat
            speed_penalty *= 0.8
            safety_penalty *= 0.9
        
        # Wind effects
        if self.wind_speed > 25:
            speed_penalty *= 0.8
            safety_penalty *= 0.7
        elif self.wind_speed > 15:
            speed_penalty *= 0.9
        
        # Precipitation effects
        if self.precipitation > 50:
            speed_penalty *= 0.6
            visibility_penalty *= 0.5
            safety_penalty *= 0.6
        elif self.precipitation > 20:
            speed_penalty *= 0.8
            visibility_penalty *= 0.7
            safety_penalty *= 0.8
        
        # Visibility effects
        if self.visibility < 200:
            speed_penalty *= 0.5
            safety_penalty *= 0.5
        elif self.visibility < 500:
            speed_penalty *= 0.7
            safety_penalty *= 0.7
        
        # Storm effects
        if self.is_storm:
            speed_penalty *= 0.5
            safety_penalty *= 0.4
        
        return {
            "speed_penalty": speed_penalty,
            "visibility_penalty": visibility_penalty,
            "safety_penalty": safety_penalty
        }
    
    def get_hazard_warnings(self) -> List[str]:
        """Get list of environmental hazards based on weather."""
        warnings = []
        
        if self.feels_like < 10:
            warnings.append(f"Extreme cold ({self._format_temperature(self.feels_like)}) - hypothermia risk")
        elif self.feels_like < 32:
            warnings.append(f"Freezing temperatures ({self._format_temperature(self.feels_like)}) - frostbite risk")
        
        if self.feels_like > 110:
            warnings.append(f"Extreme heat ({self._format_temperature(self.feels_like)}) - heat stroke risk")
        elif self.feels_like > 95:
            warnings.append(f"Very hot ({self._format_temperature(self.feels_like)}) - heat exhaustion risk")
        
        if self.wind_speed > 35:
            warnings.append("Dangerous winds - risk of being knocked down")
        elif self.wind_speed > 25:
            warnings.append("Strong winds - difficulty maintaining balance")
        
        if self.precipitation > 70:
            warnings.append("Heavy precipitation - flooding risk")
        
        if self.visibility < 200:
            warnings.append("Very poor visibility - high risk of getting lost")
        elif self.visibility < 500:
            warnings.append("Poor visibility - navigation difficulty")
        
        if self.lightning_risk > 0.7:
            warnings.append("High lightning risk - seek shelter immediately")
        elif self.lightning_risk > 0.4:
            warnings.append("Lightning possible - avoid high ground")
        
        if self.is_storm:
            warnings.append("Storm conditions - travel not recommended")
        
        return warnings


def generate_weather_state(base_temperature: float, season: str = "spring", 
                         climate_type: str = "temperate") -> WeatherState:
    """
    Generate a realistic weather state based on base conditions.
    
    Args:
        base_temperature: Base temperature for the location (°F)
        season: Current season ("spring", "summer", "autumn", "winter")
        climate_type: Climate zone type ("arctic", "temperate", "desert", "tropical")
    
    Returns:
        WeatherState object with realistic weather conditions
    """
    # Seasonal temperature adjustment
    seasonal_adjustments = {
        "winter": -15,
        "spring": -5,
        "summer": 10,
        "autumn": 0
    }
    
    # Climate-specific adjustments
    climate_adjustments = {
        "arctic": -20,
        "temperate": 0,
        "desert": 15,
        "tropical": 20
    }
    
    # Calculate actual temperature with random variation
    temp_adjustment = seasonal_adjustments.get(season, 0) + climate_adjustments.get(climate_type, 0)
    temperature = base_temperature + temp_adjustment + random.uniform(-10, 10)
    
    # Generate wind conditions
    wind_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    wind_direction = random.choice(wind_directions)
    
    # Wind speed varies by climate and season
    base_wind = 5
    if climate_type == "coastal":
        base_wind = 10
    elif climate_type == "desert":
        base_wind = 8
    
    wind_speed = max(0, int(random.normalvariate(base_wind, 8)))
    
    # Generate precipitation
    precipitation_chance = {
        "arctic": 0.3,
        "temperate": 0.4,
        "desert": 0.1,
        "tropical": 0.6
    }.get(climate_type, 0.4)
    
    if random.random() < precipitation_chance:
        precipitation = int(random.uniform(10, 80))
        
        # Determine precipitation type based on temperature
        if temperature < 32:
            precipitation_type = "snow"
        elif temperature < 35 and wind_speed > 15:
            precipitation_type = "sleet"
        elif temperature > 80 and precipitation > 60:
            precipitation_type = "hail" if random.random() < 0.1 else "rain"
        else:
            precipitation_type = "rain"
    else:
        precipitation = 0
        precipitation_type = "none"
    
    # Cloud cover correlates with precipitation
    if precipitation > 0:
        cloud_cover = max(50, int(random.uniform(60, 100)))
    else:
        cloud_cover = int(random.uniform(0, 60))
    
    # Visibility affected by precipitation and cloud cover
    base_visibility = 5000  # feet
    if precipitation > 50:
        visibility = int(random.uniform(200, 800))
    elif precipitation > 20:
        visibility = int(random.uniform(800, 2000))
    elif cloud_cover > 80:
        visibility = int(random.uniform(2000, 4000))
    else:
        visibility = base_visibility
    
    return WeatherState(
        temperature=temperature,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        precipitation=precipitation,
        precipitation_type=precipitation_type,
        cloud_cover=cloud_cover,
        visibility=visibility,
        feels_like=0.0,  # Will be calculated in __post_init__
        is_storm=False,  # Will be calculated in __post_init__
        lightning_risk=0.0  # Will be calculated in __post_init__
    )


def test_weather_core():
    """Test the core weather system."""
    print("=== Testing Core Weather System ===")
    
    # Test 1: Manual weather state creation
    print("\n1. Testing manual WeatherState creation:")
    weather = WeatherState(
        temperature=45.0,
        wind_speed=15,
        wind_direction="NW",
        precipitation=30,
        precipitation_type="rain",
        cloud_cover=70,
        visibility=1000,
        feels_like=0.0,  # Will be calculated
        is_storm=False,  # Will be calculated
        lightning_risk=0.0  # Will be calculated
    )
    
    print(f"Created weather state:")
    print(f"  Temperature: {weather._format_temperature(weather.temperature)}")
    print(f"  Feels like: {weather._format_temperature(weather.feels_like)}")
    print(f"  Wind: {weather.wind_speed} mph from {weather.wind_direction}")
    print(f"  Precipitation: {weather.precipitation}% {weather.precipitation_type}")
    print(f"  Cloud cover: {weather.cloud_cover}%")
    print(f"  Visibility: {weather.visibility} feet")
    print(f"  Storm conditions: {weather.is_storm}")
    print(f"  Lightning risk: {weather.lightning_risk:.2f}")
    
    # Test 2: Weather description
    print("\n2. Testing weather description:")
    print(weather.get_description())
    
    # Test 3: Travel modifiers
    print("\n3. Testing travel modifiers:")
    modifiers = weather.get_travel_modifier()
    for key, value in modifiers.items():
        print(f"  {key}: {value:.2f}")
    
    # Test 4: Hazard warnings
    print("\n4. Testing hazard warnings:")
    warnings = weather.get_hazard_warnings()
    if warnings:
        for warning in warnings:
            print(f"  ⚠️  {warning}")
    else:
        print("  No hazard warnings")
    
    # Test 5: Generated weather states
    print("\n5. Testing weather generation:")
    test_conditions = [
        (70, "summer", "temperate"),
        (30, "winter", "arctic"),
        (85, "summer", "desert"),
        (75, "spring", "tropical")
    ]
    
    for base_temp, season, climate in test_conditions:
        generated_weather = generate_weather_state(base_temp, season, climate)
        base_temp_c = (base_temp - 32) * 5/9
        print(f"\n  {season.title()} in {climate} climate (base {base_temp}°F ({base_temp_c:.0f}°C)):")
        print(f"    Temperature: {generated_weather._format_temperature(generated_weather.temperature)}")
        print(f"    Feels like: {generated_weather._format_temperature(generated_weather.feels_like)}")
        print(f"    Wind: {generated_weather.wind_speed} mph {generated_weather.wind_direction}")
        print(f"    Precipitation: {generated_weather.precipitation}% {generated_weather.precipitation_type}")
        print(f"    Storm: {generated_weather.is_storm}")
        
        # Show travel impact
        travel_mods = generated_weather.get_travel_modifier()
        print(f"    Travel speed: {travel_mods['speed_penalty']:.0%}")
    
    print("\n=== Core weather system testing complete! ===")


if __name__ == "__main__":
    test_weather_core()