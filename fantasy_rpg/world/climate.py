"""
Fantasy RPG - Climate System

Latitude-based temperature gradients and climate zone generation.
This module implements realistic climate simulation based on geographic principles.
"""

import math
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class ClimateZone:
    """
    Climate zone data structure containing temperature and precipitation patterns.
    
    This represents the long-term climate characteristics of a geographic region,
    including seasonal temperature ranges and precipitation patterns.
    """
    zone_type: str  # "arctic", "temperate", "subtropical", "tropical", "desert"
    base_temperature: float  # Average annual temperature in °F
    temp_range_summer: Tuple[float, float]  # (min, max) summer temperatures
    temp_range_winter: Tuple[float, float]  # (min, max) winter temperatures
    annual_precipitation: int  # Annual precipitation in inches
    seasonal_variation: float  # How much temperature varies seasonally (0.0-1.0)
    volatility: int  # Weather pattern stability (used for prediction difficulty)
    has_snow: bool  # Whether this zone experiences snow
    
    # Precipitation characteristics
    wet_season_months: int  # Number of months with heavy precipitation
    dry_season_severity: float  # How dry the dry season gets (0.0-1.0)
    precipitation_type: str  # "rain", "snow", "mixed"
    
    def get_seasonal_temp(self, season: str) -> Tuple[float, float]:
        """Get temperature range for a specific season."""
        if season == "summer":
            return self.temp_range_summer
        elif season == "winter":
            return self.temp_range_winter
        elif season == "spring":
            # Spring is between winter and summer
            winter_avg = sum(self.temp_range_winter) / 2
            summer_avg = sum(self.temp_range_summer) / 2
            spring_avg = (winter_avg + summer_avg) / 2
            spring_range = (summer_avg - winter_avg) * 0.3  # Moderate variation
            return (spring_avg - spring_range, spring_avg + spring_range)
        elif season == "autumn":
            # Autumn is similar to spring but slightly warmer
            winter_avg = sum(self.temp_range_winter) / 2
            summer_avg = sum(self.temp_range_summer) / 2
            autumn_avg = (winter_avg + summer_avg) / 2 + 5  # Slightly warmer than spring
            autumn_range = (summer_avg - winter_avg) * 0.3
            return (autumn_avg - autumn_range, autumn_avg + autumn_range)
        else:
            # Default to annual average
            return (self.base_temperature - 10, self.base_temperature + 10)


class ClimateSystem:
    """
    Climate system for generating realistic temperature gradients and climate zones.
    
    This system implements latitude-based temperature calculation with realistic
    climate zone assignment based on geographic principles.
    """
    
    def __init__(self, world_height: int, equator_position: Optional[float] = None):
        """
        Initialize climate system.
        
        Args:
            world_height: Height of the world in hexes
            equator_position: Position of equator as fraction of world height (0.0-1.0)
                            If None, defaults to middle of world (0.5)
        """
        self.world_height = world_height
        self.equator_position = equator_position if equator_position is not None else 0.5
        self.equator_y = int(world_height * self.equator_position)
        
        print(f"Initialized climate system:")
        print(f"  World height: {world_height} hexes")
        print(f"  Equator position: {self.equator_position:.2f} ({self.equator_y} hexes from top)")
        
        # Define climate zone templates
        self.climate_templates = self._initialize_climate_templates()
        
        # Initialize wind and precipitation system
        self.prevailing_wind_direction = "west"  # Default westerly winds
        self.wind_strength = 1.0  # Base wind strength modifier
    
    def _initialize_climate_templates(self) -> Dict[str, ClimateZone]:
        """Initialize climate zone templates based on real-world climate types."""
        return {
            "arctic": ClimateZone(
                zone_type="arctic",
                base_temperature=10.0,  # Very cold
                temp_range_summer=(-10, 32),  # Summer barely above freezing
                temp_range_winter=(-40, -10),  # Extremely cold winters
                annual_precipitation=10,  # Very dry
                seasonal_variation=0.8,  # High seasonal variation
                volatility=15,  # Unpredictable weather
                has_snow=True,
                wet_season_months=2,  # Brief summer melt
                dry_season_severity=0.9,  # Very dry most of year
                precipitation_type="snow"
            ),
            "subarctic": ClimateZone(
                zone_type="subarctic",
                base_temperature=25.0,  # Cold
                temp_range_summer=(32, 60),  # Cool summers
                temp_range_winter=(-20, 10),  # Cold winters
                annual_precipitation=20,  # Moderate precipitation
                seasonal_variation=0.9,  # Very high seasonal variation
                volatility=12,  # Somewhat unpredictable
                has_snow=True,
                wet_season_months=4,  # Spring/summer precipitation
                dry_season_severity=0.7,  # Dry winters
                precipitation_type="mixed"
            ),
            "temperate": ClimateZone(
                zone_type="temperate",
                base_temperature=50.0,  # Moderate
                temp_range_summer=(60, 80),  # Warm summers
                temp_range_winter=(20, 40),  # Cool winters
                annual_precipitation=40,  # Good precipitation
                seasonal_variation=0.6,  # Moderate seasonal variation
                volatility=8,  # Fairly predictable
                has_snow=True,
                wet_season_months=6,  # Fairly even distribution
                dry_season_severity=0.3,  # Mild dry periods
                precipitation_type="rain"
            ),
            "subtropical": ClimateZone(
                zone_type="subtropical",
                base_temperature=65.0,  # Warm
                temp_range_summer=(75, 90),  # Hot summers
                temp_range_winter=(40, 60),  # Mild winters
                annual_precipitation=50,  # High precipitation
                seasonal_variation=0.4,  # Low seasonal variation
                volatility=6,  # Predictable
                has_snow=False,
                wet_season_months=5,  # Distinct wet season
                dry_season_severity=0.4,  # Moderate dry season
                precipitation_type="rain"
            ),
            "tropical": ClimateZone(
                zone_type="tropical",
                base_temperature=80.0,  # Hot
                temp_range_summer=(80, 95),  # Very hot
                temp_range_winter=(70, 85),  # Warm winters
                annual_precipitation=80,  # Very high precipitation
                seasonal_variation=0.2,  # Very low seasonal variation
                volatility=5,  # Very predictable
                has_snow=False,
                wet_season_months=6,  # Long wet season
                dry_season_severity=0.2,  # Mild dry season
                precipitation_type="rain"
            ),
            "desert": ClimateZone(
                zone_type="desert",
                base_temperature=70.0,  # Hot but varies by latitude
                temp_range_summer=(85, 110),  # Extremely hot summers
                temp_range_winter=(40, 70),  # Cool to warm winters
                annual_precipitation=5,  # Very dry
                seasonal_variation=0.7,  # High daily/seasonal variation
                volatility=10,  # Unpredictable due to extremes
                has_snow=False,
                wet_season_months=1,  # Very brief wet period
                dry_season_severity=0.95,  # Extremely dry
                precipitation_type="rain"
            )
        }
    
    def calculate_latitude_factor(self, y: int) -> float:
        """
        Calculate latitude factor for temperature calculation.
        
        Args:
            y: Y coordinate (0 = north pole, world_height = south pole)
        
        Returns:
            Latitude factor (0.0 = poles, 1.0 = equator)
        """
        # Calculate distance from equator as fraction of world height
        distance_from_equator = abs(y - self.equator_y)
        max_distance = max(self.equator_y, self.world_height - self.equator_y)
        
        if max_distance == 0:
            return 1.0  # Avoid division by zero
        
        # Use cosine function for realistic temperature gradient
        # This creates the characteristic temperature curve of Earth
        latitude_fraction = distance_from_equator / max_distance
        latitude_radians = latitude_fraction * (math.pi / 2)  # 0 to π/2
        
        # Cosine gives us 1.0 at equator, 0.0 at poles
        latitude_factor = math.cos(latitude_radians)
        
        return latitude_factor
    
    def calculate_base_temperature(self, y: int) -> float:
        """
        Calculate base temperature for a given latitude.
        
        Args:
            y: Y coordinate in world space
        
        Returns:
            Base temperature in °F
        """
        latitude_factor = self.calculate_latitude_factor(y)
        
        # Temperature ranges from arctic (10°F) to tropical (85°F)
        min_temp = 10.0  # Arctic base temperature
        max_temp = 85.0  # Tropical base temperature
        
        base_temp = min_temp + (max_temp - min_temp) * latitude_factor
        
        return base_temp
    
    def determine_climate_zone_type(self, base_temperature: float, 
                                  elevation: float = 0.0) -> str:
        """
        Determine climate zone type based on temperature and elevation.
        
        Args:
            base_temperature: Base temperature in °F
            elevation: Elevation factor (0.0-1.0, where 1.0 is highest)
        
        Returns:
            Climate zone type string
        """
        # Apply elevation cooling effect (lapse rate)
        # Temperature drops ~3.5°F per 1000 feet, we'll use elevation factor
        elevation_cooling = elevation * 30.0  # Up to 30°F cooling at highest elevations
        adjusted_temp = base_temperature - elevation_cooling
        
        # Classify based on adjusted temperature
        if adjusted_temp < 20:
            return "arctic"
        elif adjusted_temp < 35:
            return "subarctic"
        elif adjusted_temp < 55:
            return "temperate"
        elif adjusted_temp < 70:
            return "subtropical"
        else:
            return "tropical"
    
    def generate_climate_zone(self, coords: Tuple[int, int], 
                            elevation: float = 0.0) -> ClimateZone:
        """
        Generate a climate zone for specific coordinates.
        
        Args:
            coords: (x, y) coordinates
            elevation: Elevation factor (0.0-1.0)
        
        Returns:
            ClimateZone object with calculated climate data
        """
        x, y = coords
        
        # Calculate base temperature from latitude
        base_temp = self.calculate_base_temperature(y)
        
        # Determine climate zone type
        zone_type = self.determine_climate_zone_type(base_temp, elevation)
        
        # Get template for this climate type
        template = self.climate_templates[zone_type]
        
        # Apply elevation effects to temperature ranges
        elevation_cooling = elevation * 30.0
        
        adjusted_base_temp = base_temp - elevation_cooling
        
        # Adjust seasonal temperature ranges
        summer_min, summer_max = template.temp_range_summer
        winter_min, winter_max = template.temp_range_winter
        
        adjusted_summer_range = (
            summer_min - elevation_cooling,
            summer_max - elevation_cooling
        )
        adjusted_winter_range = (
            winter_min - elevation_cooling,
            winter_max - elevation_cooling
        )
        
        # Determine if high elevation should have snow
        has_snow = template.has_snow or elevation > 0.6
        volatility = template.volatility + (3 if elevation > 0.6 else 0)
        
        # Create new ClimateZone with adjusted values
        return ClimateZone(
            zone_type=zone_type,
            base_temperature=adjusted_base_temp,
            temp_range_summer=adjusted_summer_range,
            temp_range_winter=adjusted_winter_range,
            annual_precipitation=template.annual_precipitation,
            seasonal_variation=template.seasonal_variation,
            volatility=volatility,
            has_snow=has_snow,
            wet_season_months=template.wet_season_months,
            dry_season_severity=template.dry_season_severity,
            precipitation_type=template.precipitation_type
        )
    
    def generate_climate_zones(self, world_size: Tuple[int, int],
                             heightmap: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], ClimateZone]:
        """
        Generate climate zones for entire world.
        
        Args:
            world_size: (width, height) of world in hexes
            heightmap: Dictionary mapping coordinates to elevation values (0.0-1.0)
        
        Returns:
            Dictionary mapping coordinates to ClimateZone objects
        """
        width, height = world_size
        print(f"Generating climate zones for {width}x{height} world...")
        
        climate_zones = {}
        zone_counts = {}
        
        for x in range(width):
            for y in range(height):
                coords = (x, y)
                elevation = heightmap.get(coords, 0.0)
                
                # Generate climate zone for this location
                climate_zone = self.generate_climate_zone(coords, elevation)
                climate_zones[coords] = climate_zone
                
                # Count zone types for statistics
                zone_type = climate_zone.zone_type
                zone_counts[zone_type] = zone_counts.get(zone_type, 0) + 1
        
        # Print climate statistics
        total_hexes = len(climate_zones)
        print(f"Generated {total_hexes} climate zones:")
        
        for zone_type, count in sorted(zone_counts.items()):
            percentage = (count / total_hexes) * 100
            template = self.climate_templates[zone_type]
            temp_c = (template.base_temperature - 32) * 5/9
            print(f"  {zone_type}: {count} hexes ({percentage:.1f}%) - "
                  f"avg temp: {template.base_temperature:.0f}°F ({temp_c:.0f}°C)")
        
        return climate_zones
    
    def get_temperature_at_coords(self, coords: Tuple[int, int], 
                                elevation: float = 0.0,
                                season: str = "summer") -> float:
        """
        Get current temperature at specific coordinates.
        
        Args:
            coords: (x, y) coordinates
            elevation: Elevation factor (0.0-1.0)
            season: Season name ("spring", "summer", "autumn", "winter")
        
        Returns:
            Temperature in °F
        """
        climate_zone = self.generate_climate_zone(coords, elevation)
        temp_range = climate_zone.get_seasonal_temp(season)
        
        # Return average temperature for the season
        return sum(temp_range) / 2
    
    def calculate_distance_from_ocean(self, coords: Tuple[int, int], 
                                    world_size: Tuple[int, int]) -> float:
        """
        Calculate distance from nearest ocean (world edge) for moisture calculation.
        
        Args:
            coords: (x, y) coordinates
            world_size: (width, height) of world
        
        Returns:
            Distance factor (0.0 = coast, 1.0 = continental interior)
        """
        x, y = coords
        width, height = world_size
        
        # Distance to nearest edge (ocean)
        distance_to_edge = min(x, y, width - x - 1, height - y - 1)
        max_distance = min(width, height) // 2
        
        # Normalize to 0.0-1.0 (0.0 = coast, 1.0 = interior)
        return min(distance_to_edge / max_distance, 1.0) if max_distance > 0 else 0.0
    
    def calculate_windward_leeward_effect(self, coords: Tuple[int, int],
                                        heightmap: Dict[Tuple[int, int], float],
                                        world_size: Tuple[int, int]) -> Tuple[float, str]:
        """
        Calculate rain shadow effects based on prevailing winds and terrain.
        
        Args:
            coords: (x, y) coordinates
            heightmap: Dictionary mapping coordinates to elevation values
            world_size: (width, height) of world
        
        Returns:
            Tuple of (precipitation_modifier, effect_description)
            - precipitation_modifier: 0.1-2.0 (rain shadow to windward enhancement)
            - effect_description: Human-readable description of the effect
        """
        x, y = coords
        width, height = world_size
        current_elevation = heightmap.get(coords, 0.0)
        
        # Define wind direction vectors (prevailing westerlies)
        wind_directions = {
            "west": (-1, 0),    # Wind from west (most common)
            "northwest": (-1, -1),
            "southwest": (-1, 1)
        }
        
        # Use westerly winds as primary
        wind_dx, wind_dy = wind_directions[self.prevailing_wind_direction]
        
        # Check terrain upwind (where air is coming from)
        upwind_elevation = 0.0
        upwind_distance = 0
        
        # Sample terrain in upwind direction
        for distance in range(1, 6):  # Check up to 5 hexes upwind
            upwind_x = x - (wind_dx * distance)
            upwind_y = y - (wind_dy * distance)
            
            if 0 <= upwind_x < width and 0 <= upwind_y < height:
                upwind_coords = (upwind_x, upwind_y)
                elevation = heightmap.get(upwind_coords, 0.0)
                
                if elevation > upwind_elevation:
                    upwind_elevation = elevation
                    upwind_distance = distance
        
        # Calculate orographic effects
        elevation_difference = current_elevation - upwind_elevation
        
        if elevation_difference > 0.2:  # Significant elevation gain
            # Windward side - air rises and cools, more precipitation
            orographic_effect = 1.5 + (elevation_difference * 0.5)
            effect_description = "windward_slope"
            
        elif elevation_difference < -0.2:  # Significant elevation loss
            # Leeward side - air descends and warms, rain shadow effect
            rain_shadow_strength = abs(elevation_difference) * 2.0
            orographic_effect = max(0.1, 1.0 - rain_shadow_strength)
            effect_description = "rain_shadow"
            
        else:
            # Relatively flat terrain
            orographic_effect = 1.0
            effect_description = "neutral"
        
        # Clamp to reasonable range
        orographic_effect = max(0.1, min(2.5, orographic_effect))
        
        return orographic_effect, effect_description
    
    def calculate_continental_effect(self, distance_from_ocean: float) -> float:
        """
        Calculate continental effect on precipitation.
        
        Args:
            distance_from_ocean: 0.0-1.0 (coast to interior)
        
        Returns:
            Precipitation modifier (0.3-1.0, lower = drier interior)
        """
        # Continental interiors are drier due to distance from moisture sources
        continental_dryness = 0.7 * distance_from_ocean  # Up to 70% reduction
        return 1.0 - continental_dryness
    
    def generate_precipitation_map(self, world_size: Tuple[int, int],
                                 heightmap: Dict[Tuple[int, int], float],
                                 climate_zones: Dict[Tuple[int, int], ClimateZone]) -> Dict[Tuple[int, int], Dict]:
        """
        Generate precipitation patterns for entire world including wind and rain shadow effects.
        
        Args:
            world_size: (width, height) of world in hexes
            heightmap: Dictionary mapping coordinates to elevation values
            climate_zones: Dictionary mapping coordinates to ClimateZone objects
        
        Returns:
            Dictionary mapping coordinates to precipitation data
        """
        width, height = world_size
        print(f"Generating precipitation patterns for {width}x{height} world...")
        print(f"Prevailing winds: {self.prevailing_wind_direction}erly")
        
        precipitation_map = {}
        
        # Track effects for statistics
        effect_counts = {
            "windward_slope": 0,
            "rain_shadow": 0,
            "neutral": 0,
            "coastal": 0,
            "continental": 0
        }
        
        for x in range(width):
            for y in range(height):
                coords = (x, y)
                climate_zone = climate_zones[coords]
                base_precipitation = climate_zone.annual_precipitation
                
                # Calculate distance from ocean (moisture source)
                distance_from_ocean = self.calculate_distance_from_ocean(coords, world_size)
                
                # Calculate orographic (mountain) effects
                orographic_modifier, orographic_effect = self.calculate_windward_leeward_effect(
                    coords, heightmap, world_size
                )
                
                # Calculate continental effect
                continental_modifier = self.calculate_continental_effect(distance_from_ocean)
                
                # Combine all effects
                total_modifier = orographic_modifier * continental_modifier
                final_precipitation = base_precipitation * total_modifier
                
                # Determine primary effect for classification
                primary_effect = orographic_effect
                if distance_from_ocean < 0.2:
                    primary_effect = "coastal"
                elif distance_from_ocean > 0.7:
                    primary_effect = "continental"
                
                effect_counts[primary_effect] += 1
                
                # Store precipitation data
                precipitation_map[coords] = {
                    "annual_precipitation": final_precipitation,
                    "base_precipitation": base_precipitation,
                    "orographic_modifier": orographic_modifier,
                    "continental_modifier": continental_modifier,
                    "total_modifier": total_modifier,
                    "distance_from_ocean": distance_from_ocean,
                    "primary_effect": primary_effect,
                    "climate_zone": climate_zone.zone_type,
                    "wet_season_months": climate_zone.wet_season_months,
                    "dry_season_severity": climate_zone.dry_season_severity
                }
        
        # Print precipitation statistics
        total_hexes = len(precipitation_map)
        print(f"Generated precipitation patterns for {total_hexes} hexes:")
        
        for effect, count in effect_counts.items():
            percentage = (count / total_hexes) * 100
            print(f"  {effect}: {count} hexes ({percentage:.1f}%)")
        
        # Calculate precipitation statistics
        precipitations = [data["annual_precipitation"] for data in precipitation_map.values()]
        print(f"\nPrecipitation statistics:")
        print(f"  Min: {min(precipitations):.1f} inches/year")
        print(f"  Max: {max(precipitations):.1f} inches/year")
        print(f"  Avg: {sum(precipitations)/len(precipitations):.1f} inches/year")
        
        return precipitation_map


def test_climate_system():
    """Test the climate system implementation."""
    print("=== Testing Climate System ===")
    
    # Test with a small world
    world_height = 20
    climate_system = ClimateSystem(world_height)
    
    print(f"\nTesting latitude-based temperature calculation:")
    
    # Test temperature at different latitudes
    test_latitudes = [0, 5, 10, 15, 19]  # From north pole to south pole
    
    for y in test_latitudes:
        latitude_factor = climate_system.calculate_latitude_factor(y)
        base_temp = climate_system.calculate_base_temperature(y)
        zone_type = climate_system.determine_climate_zone_type(base_temp)
        
        # Calculate distance from equator for display
        distance_from_equator = abs(y - climate_system.equator_y)
        
        base_temp_c = (base_temp - 32) * 5/9
        print(f"  Y={y:2d}: distance from equator={distance_from_equator:2d}, "
              f"latitude_factor={latitude_factor:.3f}, "
              f"base_temp={base_temp:.1f}°F ({base_temp_c:.1f}°C), zone={zone_type}")
    
    # Test elevation effects
    print(f"\nTesting elevation effects on climate:")
    
    test_coords = (10, 10)  # Middle of world
    elevations = [0.0, 0.3, 0.6, 0.9]
    
    for elevation in elevations:
        climate_zone = climate_system.generate_climate_zone(test_coords, elevation)
        
        base_temp_c = (climate_zone.base_temperature - 32) * 5/9
        summer_min_c = (climate_zone.temp_range_summer[0] - 32) * 5/9
        summer_max_c = (climate_zone.temp_range_summer[1] - 32) * 5/9
        winter_min_c = (climate_zone.temp_range_winter[0] - 32) * 5/9
        winter_max_c = (climate_zone.temp_range_winter[1] - 32) * 5/9
        
        print(f"  Elevation {elevation:.1f}: {climate_zone.zone_type}, "
              f"base_temp={climate_zone.base_temperature:.1f}°F ({base_temp_c:.1f}°C), "
              f"summer={climate_zone.temp_range_summer[0]:.0f}-{climate_zone.temp_range_summer[1]:.0f}°F "
              f"({summer_min_c:.0f}-{summer_max_c:.0f}°C), "
              f"winter={climate_zone.temp_range_winter[0]:.0f}-{climate_zone.temp_range_winter[1]:.0f}°F "
              f"({winter_min_c:.0f}-{winter_max_c:.0f}°C), "
              f"snow={climate_zone.has_snow}")
    
    # Test seasonal temperature variation
    print(f"\nTesting seasonal temperature variation:")
    
    test_coords = (10, 10)
    elevation = 0.2
    seasons = ["spring", "summer", "autumn", "winter"]
    
    climate_zone = climate_system.generate_climate_zone(test_coords, elevation)
    
    print(f"  Climate zone: {climate_zone.zone_type} at elevation {elevation}")
    for season in seasons:
        temp_range = climate_zone.get_seasonal_temp(season)
        avg_temp = sum(temp_range) / 2
        avg_temp_c = (avg_temp - 32) * 5/9
        temp_min_c = (temp_range[0] - 32) * 5/9
        temp_max_c = (temp_range[1] - 32) * 5/9
        print(f"    {season}: {temp_range[0]:.0f}-{temp_range[1]:.0f}°F "
              f"({temp_min_c:.0f}-{temp_max_c:.0f}°C) avg: {avg_temp:.0f}°F ({avg_temp_c:.0f}°C)")
    
    # Test full world climate generation
    print(f"\nTesting full world climate generation:")
    
    # Create a simple heightmap for testing
    world_size = (15, 20)
    width, height = world_size
    
    # Generate simple heightmap (higher in center, lower at edges)
    heightmap = {}
    center_x, center_y = width // 2, height // 2
    
    for x in range(width):
        for y in range(height):
            # Distance from center
            dx = abs(x - center_x)
            dy = abs(y - center_y)
            distance = math.sqrt(dx*dx + dy*dy)
            max_distance = math.sqrt(center_x*center_x + center_y*center_y)
            
            # Higher elevation in center, lower at edges
            elevation = max(0.0, 1.0 - (distance / max_distance))
            heightmap[(x, y)] = elevation
    
    # Generate climate zones
    climate_zones = climate_system.generate_climate_zones(world_size, heightmap)
    
    # Display climate map
    print(f"\nClimate map (15x20 world):")
    print("Legend: A=Arctic, S=Subarctic, T=Temperate, U=Subtropical, R=Tropical")
    
    for y in range(height):
        row = []
        for x in range(width):
            coords = (x, y)
            climate_zone = climate_zones[coords]
            
            # Use first letter of climate type
            zone_letter = climate_zone.zone_type[0].upper()
            if zone_letter == 'S' and climate_zone.zone_type == 'subtropical':
                zone_letter = 'U'  # Distinguish subtropical from subarctic
            
            row.append(zone_letter)
        
        print(f"  Row {y:2d}: {' '.join(row)}")
    
    # Test temperature queries
    print(f"\nTesting temperature queries:")
    
    test_locations = [
        ((7, 2), "Northern region"),
        ((7, 10), "Equatorial region"),
        ((7, 18), "Southern region")
    ]
    
    for coords, description in test_locations:
        elevation = heightmap[coords]
        
        print(f"  {description} {coords}:")
        print(f"    Elevation: {elevation:.2f}")
        
        for season in ["summer", "winter"]:
            temp = climate_system.get_temperature_at_coords(coords, elevation, season)
            temp_c = (temp - 32) * 5/9
            print(f"    {season.title()} temperature: {temp:.0f}°F ({temp_c:.0f}°C)")
    
    # Test precipitation system
    print(f"\n" + "="*50)
    print("Testing Precipitation Patterns")
    print("="*50)
    
    # Generate precipitation map
    precipitation_map = climate_system.generate_precipitation_map(world_size, heightmap, climate_zones)
    
    # Display precipitation map
    print(f"\nPrecipitation map (15x20 world):")
    print("Legend: . = Very Dry (<10), - = Dry (10-25), + = Moderate (25-50), * = Wet (50-75), # = Very Wet (>75)")
    
    for y in range(height):
        row = []
        for x in range(width):
            coords = (x, y)
            precip_data = precipitation_map[coords]
            annual_precip = precip_data["annual_precipitation"]
            
            if annual_precip < 10:
                symbol = "."  # Very dry
            elif annual_precip < 25:
                symbol = "-"  # Dry
            elif annual_precip < 50:
                symbol = "+"  # Moderate
            elif annual_precip < 75:
                symbol = "*"  # Wet
            else:
                symbol = "#"  # Very wet
            
            row.append(symbol)
        
        print(f"  Row {y:2d}: {' '.join(row)}")
    
    # Show detailed precipitation analysis for sample locations
    print(f"\nDetailed precipitation analysis:")
    
    sample_locations = [
        ((2, 10), "Western Coast"),
        ((7, 10), "Central Region"),
        ((13, 10), "Eastern Region"),
        ((7, 5), "Northern Mountains"),
        ((7, 15), "Southern Mountains")
    ]
    
    for coords, description in sample_locations:
        if coords in precipitation_map:
            data = precipitation_map[coords]
            elevation = heightmap[coords]
            
            print(f"\n  {description} {coords}:")
            print(f"    Elevation: {elevation:.2f}")
            print(f"    Base precipitation: {data['base_precipitation']:.1f} inches/year")
            print(f"    Final precipitation: {data['annual_precipitation']:.1f} inches/year")
            print(f"    Orographic effect: {data['orographic_modifier']:.2f}x ({data['primary_effect']})")
            print(f"    Continental effect: {data['continental_modifier']:.2f}x")
            print(f"    Distance from ocean: {data['distance_from_ocean']:.2f}")
            print(f"    Climate zone: {data['climate_zone']}")
    
    # Show rain shadow demonstration
    print(f"\nRain shadow demonstration (center row Y=10):")
    print("X  | Elevation | Base Precip | Final Precip | Effect")
    print("---|-----------|-------------|--------------|------------------")
    
    for x in range(width):
        coords = (x, 10)
        if coords in precipitation_map:
            data = precipitation_map[coords]
            elevation = heightmap[coords]
            
            print(f"{x:2d} | {elevation:8.2f}  | {data['base_precipitation']:8.1f}    | {data['annual_precipitation']:9.1f}    | {data['primary_effect']}")
    
    print("\nClimate system test complete!")
    return climate_system, climate_zones


if __name__ == "__main__":
    test_climate_system()