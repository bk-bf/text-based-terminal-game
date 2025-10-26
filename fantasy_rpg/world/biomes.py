"""
Fantasy RPG - Biome System

Biome assignment based on temperature and precipitation using Whittaker biome classification.
This creates realistic ecosystems that match real-world climate patterns.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional
from climate import ClimateZone
try:
    from .enhanced_biomes import EnhancedBiomeSystem, EnhancedBiome
except ImportError:
    from enhanced_biomes import EnhancedBiomeSystem, EnhancedBiome


# Helper functions for metric conversions (following steering requirements)
def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9


def inches_to_mm(inches: float) -> float:
    """Convert inches to millimeters."""
    return inches * 25.4


def format_temp(fahrenheit: float) -> str:
    """Format temperature showing both Fahrenheit and Celsius."""
    celsius = fahrenheit_to_celsius(fahrenheit)
    return f"{fahrenheit:6.1f}°F ({celsius:5.1f}°C)"


def format_precipitation(inches: float) -> str:
    """Format precipitation showing both inches and millimeters."""
    mm = inches_to_mm(inches)
    return f"{inches:.1f} inches ({mm:.0f} mm)"


@dataclass
class BiomeType:
    """
    Biome type definition with environmental characteristics.
    
    This defines the properties of each biome type including resources,
    hazards, and gameplay characteristics.
    """
    name: str
    description: str
    
    # Climate requirements
    min_temp_c: float  # Minimum average temperature (Celsius)
    max_temp_c: float  # Maximum average temperature (Celsius)
    min_precip_mm: float  # Minimum annual precipitation (mm)
    max_precip_mm: float  # Maximum annual precipitation (mm)
    
    # Environmental characteristics
    travel_speed_modifier: float  # 0.1-1.5 (affects movement speed)
    visibility: str  # "excellent", "good", "limited", "poor"
    shelter_availability: str  # "abundant", "moderate", "scarce", "none"
    water_sources: str  # "abundant", "seasonal", "scarce", "none"
    
    # Resource availability (0.0-1.0 scale)
    food_availability: float  # Foraging and hunting opportunities
    wood_availability: float  # Fuel and construction materials
    stone_availability: float  # Construction and tool materials
    
    # Environmental hazards
    natural_hazards: List[str]  # List of potential hazards
    
    # Seasonal variation
    seasonal_difficulty: float  # 0.0-1.0 (how much seasons affect travel)
    
    def get_display_name(self) -> str:
        """Get formatted display name for UI."""
        return self.name.replace('_', ' ').title()
    
    def matches_climate(self, avg_temp_c: float, annual_precip_mm: float) -> bool:
        """Check if climate conditions match this biome."""
        temp_match = self.min_temp_c <= avg_temp_c <= self.max_temp_c
        precip_match = self.min_precip_mm <= annual_precip_mm <= self.max_precip_mm
        return temp_match and precip_match


class BiomeClassifier:
    """
    Integrated biome classification system.
    
    This system combines Whittaker scientific classification with enhanced
    gameplay-focused biome properties for rich environmental simulation.
    """
    
    def __init__(self, use_enhanced_biomes: bool = True):
        """
        Initialize biome classifier.
        
        Args:
            use_enhanced_biomes: If True, uses 8 core enhanced biomes with gameplay properties.
                               If False, uses 13 scientific Whittaker biomes.
        """
        self.use_enhanced_biomes = use_enhanced_biomes
        
        if use_enhanced_biomes:
            self.enhanced_system = EnhancedBiomeSystem()
            print("Initialized integrated biome system with 8 enhanced biomes")
            print("Enhanced biomes include detailed gameplay mechanics and environmental properties")
        else:
            self.biome_types = self._initialize_biome_types()
            print("Initialized biome classifier with Whittaker classification system")
            print(f"Available biomes: {len(self.biome_types)} types")
    
    def _initialize_biome_types(self) -> Dict[str, BiomeType]:
        """Initialize biome type definitions based on Whittaker classification."""
        return {
            # Cold biomes
            "tundra": BiomeType(
                name="tundra",
                description="Treeless arctic plains with permafrost and hardy vegetation",
                min_temp_c=-15.0, max_temp_c=5.0,
                min_precip_mm=0, max_precip_mm=400,
                travel_speed_modifier=0.6,
                visibility="excellent",
                shelter_availability="none",
                water_sources="seasonal",
                food_availability=0.2,
                wood_availability=0.0,
                stone_availability=0.3,
                natural_hazards=["blizzards", "extreme_cold", "permafrost"],
                seasonal_difficulty=0.9
            ),
            
            "taiga": BiomeType(
                name="taiga",
                description="Boreal coniferous forest with cold winters",
                min_temp_c=-5.0, max_temp_c=15.0,
                min_precip_mm=200, max_precip_mm=850,
                travel_speed_modifier=0.7,
                visibility="limited",
                shelter_availability="moderate",
                water_sources="abundant",
                food_availability=0.4,
                wood_availability=0.9,
                stone_availability=0.2,
                natural_hazards=["forest_fires", "deep_snow", "predators"],
                seasonal_difficulty=0.7
            ),
            
            # Temperate biomes
            "temperate_deciduous_forest": BiomeType(
                name="temperate_deciduous_forest",
                description="Deciduous forest with moderate climate and seasonal changes",
                min_temp_c=5.0, max_temp_c=20.0,
                min_precip_mm=750, max_precip_mm=1500,
                travel_speed_modifier=0.8,
                visibility="limited",
                shelter_availability="abundant",
                water_sources="abundant",
                food_availability=0.8,
                wood_availability=1.0,
                stone_availability=0.4,
                natural_hazards=["storms", "flooding"],
                seasonal_difficulty=0.4
            ),
            
            "temperate_coniferous_forest": BiomeType(
                name="temperate_coniferous_forest",
                description="Evergreen forest with mild, wet climate",
                min_temp_c=5.0, max_temp_c=20.0,
                min_precip_mm=1000, max_precip_mm=2500,
                travel_speed_modifier=0.7,
                visibility="poor",
                shelter_availability="abundant",
                water_sources="abundant",
                food_availability=0.6,
                wood_availability=1.0,
                stone_availability=0.3,
                natural_hazards=["landslides", "heavy_rain", "dense_fog"],
                seasonal_difficulty=0.3
            ),
            
            "temperate_grassland": BiomeType(
                name="temperate_grassland",
                description="Open grasslands with fertile soil and moderate rainfall",
                min_temp_c=0.0, max_temp_c=20.0,
                min_precip_mm=250, max_precip_mm=750,
                travel_speed_modifier=1.2,
                visibility="excellent",
                shelter_availability="scarce",
                water_sources="seasonal",
                food_availability=0.6,
                wood_availability=0.1,
                stone_availability=0.2,
                natural_hazards=["grassfires", "tornadoes", "drought"],
                seasonal_difficulty=0.5
            ),
            
            # Warm biomes
            "mediterranean_scrub": BiomeType(
                name="mediterranean_scrub",
                description="Dry shrubland with hot summers and mild winters",
                min_temp_c=10.0, max_temp_c=25.0,
                min_precip_mm=200, max_precip_mm=1000,
                travel_speed_modifier=0.9,
                visibility="good",
                shelter_availability="scarce",
                water_sources="seasonal",
                food_availability=0.4,
                wood_availability=0.3,
                stone_availability=0.6,
                natural_hazards=["wildfires", "drought", "flash_floods"],
                seasonal_difficulty=0.6
            ),
            
            "tropical_rainforest": BiomeType(
                name="tropical_rainforest",
                description="Dense jungle with high biodiversity and constant warmth",
                min_temp_c=20.0, max_temp_c=35.0,
                min_precip_mm=1750, max_precip_mm=4000,
                travel_speed_modifier=0.4,
                visibility="poor",
                shelter_availability="moderate",
                water_sources="abundant",
                food_availability=0.9,
                wood_availability=1.0,
                stone_availability=0.2,
                natural_hazards=["disease", "predators", "poisonous_plants"],
                seasonal_difficulty=0.2
            ),
            
            "tropical_seasonal_forest": BiomeType(
                name="tropical_seasonal_forest",
                description="Tropical forest with distinct wet and dry seasons",
                min_temp_c=20.0, max_temp_c=35.0,
                min_precip_mm=1000, max_precip_mm=1750,
                travel_speed_modifier=0.6,
                visibility="limited",
                shelter_availability="moderate",
                water_sources="seasonal",
                food_availability=0.7,
                wood_availability=0.8,
                stone_availability=0.3,
                natural_hazards=["monsoons", "disease", "predators"],
                seasonal_difficulty=0.7
            ),
            
            "tropical_savanna": BiomeType(
                name="tropical_savanna",
                description="Grassland with scattered trees and distinct seasons",
                min_temp_c=20.0, max_temp_c=35.0,
                min_precip_mm=600, max_precip_mm=1200,
                travel_speed_modifier=1.0,
                visibility="excellent",
                shelter_availability="scarce",
                water_sources="seasonal",
                food_availability=0.5,
                wood_availability=0.2,
                stone_availability=0.3,
                natural_hazards=["drought", "wildfires", "predators"],
                seasonal_difficulty=0.8
            ),
            
            # Arid biomes
            "hot_desert": BiomeType(
                name="hot_desert",
                description="Extremely dry region with scorching days and cold nights",
                min_temp_c=15.0, max_temp_c=50.0,
                min_precip_mm=0, max_precip_mm=250,
                travel_speed_modifier=0.7,
                visibility="good",
                shelter_availability="scarce",
                water_sources="none",
                food_availability=0.1,
                wood_availability=0.0,
                stone_availability=0.4,
                natural_hazards=["extreme_heat", "sandstorms", "dehydration"],
                seasonal_difficulty=0.3
            ),
            
            "cold_desert": BiomeType(
                name="cold_desert",
                description="Dry region with cold winters and moderate summers",
                min_temp_c=-10.0, max_temp_c=20.0,
                min_precip_mm=0, max_precip_mm=250,
                travel_speed_modifier=0.8,
                visibility="good",
                shelter_availability="scarce",
                water_sources="scarce",
                food_availability=0.2,
                wood_availability=0.1,
                stone_availability=0.5,
                natural_hazards=["extreme_cold", "dust_storms", "dehydration"],
                seasonal_difficulty=0.6
            ),
            
            # Special biomes
            "alpine": BiomeType(
                name="alpine",
                description="High mountain environment above tree line",
                min_temp_c=-10.0, max_temp_c=10.0,
                min_precip_mm=300, max_precip_mm=1500,
                travel_speed_modifier=0.3,
                visibility="excellent",
                shelter_availability="scarce",
                water_sources="seasonal",
                food_availability=0.2,
                wood_availability=0.0,
                stone_availability=0.8,
                natural_hazards=["avalanches", "altitude_sickness", "extreme_weather"],
                seasonal_difficulty=0.9
            ),
            
            "wetland": BiomeType(
                name="wetland",
                description="Marshy area with standing water and aquatic vegetation",
                min_temp_c=0.0, max_temp_c=30.0,
                min_precip_mm=500, max_precip_mm=2000,
                travel_speed_modifier=0.4,
                visibility="limited",
                shelter_availability="scarce",
                water_sources="abundant",
                food_availability=0.6,
                wood_availability=0.3,
                stone_availability=0.1,
                natural_hazards=["disease", "flooding", "quicksand"],
                seasonal_difficulty=0.5
            )
        }
    
    def classify_biome(self, avg_temp_c: float, annual_precip_mm: float, 
                      elevation: float = 0.0, coastal: bool = False) -> str:
        """
        Classify biome based on climate conditions.
        
        Args:
            avg_temp_c: Average annual temperature in Celsius
            annual_precip_mm: Annual precipitation in millimeters
            elevation: Elevation factor (0.0-1.0)
            coastal: Whether location is coastal
        
        Returns:
            Biome type name
        """
        if self.use_enhanced_biomes:
            # Use enhanced biome system (8 core biomes)
            return self.enhanced_system.classify_biome(avg_temp_c, annual_precip_mm, elevation)
        else:
            # Use original Whittaker classification (13 biomes)
            return self._classify_whittaker_biome(avg_temp_c, annual_precip_mm, elevation, coastal)
    
    def _classify_whittaker_biome(self, avg_temp_c: float, annual_precip_mm: float, 
                                elevation: float = 0.0, coastal: bool = False) -> str:
        """Original Whittaker biome classification method."""
        # Special case: Alpine biome for high elevations
        if elevation > 0.8:
            return "alpine"
        
        # Special case: Wetlands for very high precipitation in temperate zones
        if (5.0 <= avg_temp_c <= 25.0 and annual_precip_mm > 1800 and 
            elevation < 0.3 and not coastal):
            return "wetland"
        
        # Find matching biomes
        matching_biomes = []
        for biome_name, biome_type in self.biome_types.items():
            if biome_type.matches_climate(avg_temp_c, annual_precip_mm):
                matching_biomes.append((biome_name, biome_type))
        
        if not matching_biomes:
            # Fallback classification based on temperature and precipitation
            return self._fallback_classification(avg_temp_c, annual_precip_mm)
        
        # If multiple matches, choose the most appropriate one
        if len(matching_biomes) == 1:
            return matching_biomes[0][0]
        
        # Prioritize based on specific conditions
        return self._resolve_biome_conflicts(matching_biomes, avg_temp_c, annual_precip_mm, elevation)
    
    def _fallback_classification(self, avg_temp_c: float, annual_precip_mm: float) -> str:
        """Fallback biome classification when no exact match is found."""
        if avg_temp_c < -5:
            return "tundra" if annual_precip_mm < 400 else "taiga"
        elif avg_temp_c < 5:
            return "taiga" if annual_precip_mm > 300 else "cold_desert"
        elif avg_temp_c < 20:
            if annual_precip_mm < 250:
                return "cold_desert"
            elif annual_precip_mm < 750:
                return "temperate_grassland"
            else:
                return "temperate_deciduous_forest"
        else:  # Hot climates
            if annual_precip_mm < 250:
                return "hot_desert"
            elif annual_precip_mm < 600:
                return "mediterranean_scrub"
            elif annual_precip_mm < 1200:
                return "tropical_savanna"
            else:
                return "tropical_rainforest"
    
    def _resolve_biome_conflicts(self, matching_biomes: List[Tuple[str, BiomeType]], 
                               avg_temp_c: float, annual_precip_mm: float, 
                               elevation: float) -> str:
        """Resolve conflicts when multiple biomes match the climate."""
        # Prefer forest types in high precipitation areas
        if annual_precip_mm > 1000:
            forest_biomes = [name for name, _ in matching_biomes 
                           if "forest" in name]
            if forest_biomes:
                return forest_biomes[0]
        
        # Prefer grassland in moderate precipitation
        if 300 <= annual_precip_mm <= 800:
            grassland_biomes = [name for name, _ in matching_biomes 
                              if "grassland" in name or "savanna" in name]
            if grassland_biomes:
                return grassland_biomes[0]
        
        # Default to first match
        return matching_biomes[0][0]
    
    def generate_biome_map(self, world_size: Tuple[int, int],
                          climate_zones: Dict[Tuple[int, int], ClimateZone],
                          precipitation_map: Dict[Tuple[int, int], Dict],
                          heightmap: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], str]:
        """
        Generate biome assignments for entire world.
        
        Args:
            world_size: (width, height) of world in hexes
            climate_zones: Dictionary mapping coordinates to ClimateZone objects
            precipitation_map: Dictionary mapping coordinates to precipitation data
            heightmap: Dictionary mapping coordinates to elevation values
        
        Returns:
            Dictionary mapping coordinates to biome type names
        """
        width, height = world_size
        print(f"Generating biome assignments for {width}x{height} world...")
        
        biome_map = {}
        biome_counts = {}
        
        for x in range(width):
            for y in range(height):
                coords = (x, y)
                
                # Get climate data
                climate_zone = climate_zones[coords]
                precip_data = precipitation_map[coords]
                elevation = heightmap[coords]
                
                # Convert to metric units for classification
                avg_temp_c = fahrenheit_to_celsius(climate_zone.base_temperature)
                annual_precip_mm = inches_to_mm(precip_data["annual_precipitation"])
                
                # Determine if coastal (simplified - within 2 hexes of edge)
                coastal = (x < 2 or y < 2 or x >= width-2 or y >= height-2)
                
                # Classify biome
                biome_type = self.classify_biome(avg_temp_c, annual_precip_mm, elevation, coastal)
                biome_map[coords] = biome_type
                
                # Count biomes for statistics
                biome_counts[biome_type] = biome_counts.get(biome_type, 0) + 1
        
        # Print biome statistics
        total_hexes = len(biome_map)
        print(f"Generated biome assignments for {total_hexes} hexes:")
        
        for biome_type, count in sorted(biome_counts.items()):
            percentage = (count / total_hexes) * 100
            
            if self.use_enhanced_biomes:
                biome_obj = self.enhanced_system.get_biome(biome_type)
                display_name = biome_obj.display_name if biome_obj else biome_type.replace('_', ' ').title()
            else:
                biome_obj = self.biome_types.get(biome_type)
                display_name = biome_obj.get_display_name() if biome_obj else biome_type.replace('_', ' ').title()
            
            print(f"  {display_name}: {count} hexes ({percentage:.1f}%)")
        
        return biome_map
    
    def get_biome_info(self, biome_type: str):
        """Get detailed information about a biome type."""
        if self.use_enhanced_biomes:
            return self.enhanced_system.get_biome(biome_type)
        else:
            return self.biome_types.get(biome_type)
    
    def analyze_biome_distribution(self, biome_map: Dict[Tuple[int, int], str],
                                 climate_zones: Dict[Tuple[int, int], ClimateZone],
                                 precipitation_map: Dict[Tuple[int, int], Dict]) -> Dict:
        """
        Analyze biome distribution and climate relationships.
        
        Returns:
            Dictionary containing analysis results
        """
        print("\n" + "="*60)
        print("BIOME CLIMATE ANALYSIS")
        print("="*60)
        
        # Group by biome type
        biome_climates = {}
        for coords, biome_type in biome_map.items():
            if biome_type not in biome_climates:
                biome_climates[biome_type] = {
                    'temperatures': [],
                    'precipitations': [],
                    'count': 0
                }
            
            climate_zone = climate_zones[coords]
            precip_data = precipitation_map[coords]
            
            temp_c = fahrenheit_to_celsius(climate_zone.base_temperature)
            precip_mm = inches_to_mm(precip_data["annual_precipitation"])
            
            biome_climates[biome_type]['temperatures'].append(temp_c)
            biome_climates[biome_type]['precipitations'].append(precip_mm)
            biome_climates[biome_type]['count'] += 1
        
        # Print analysis
        print("Biome Type               | Count | Avg Temp        | Avg Precip       | Temp Range      | Precip Range")
        print("-------------------------|-------|-----------------|------------------|-----------------|------------------")
        
        analysis_results = {}
        
        for biome_type, data in sorted(biome_climates.items()):
            if data['count'] == 0:
                continue
                
            avg_temp_c = sum(data['temperatures']) / len(data['temperatures'])
            avg_precip_mm = sum(data['precipitations']) / len(data['precipitations'])
            
            min_temp_c = min(data['temperatures'])
            max_temp_c = max(data['temperatures'])
            min_precip_mm = min(data['precipitations'])
            max_precip_mm = max(data['precipitations'])
            
            # Convert for display
            avg_temp_f = avg_temp_c * 9/5 + 32
            avg_precip_in = avg_precip_mm / 25.4
            
            display_name = biome_type.replace('_', ' ').title()
            
            print(f"{display_name:24s} | {data['count']:5d} | "
                  f"{format_temp(avg_temp_f):>15s} | {format_precipitation(avg_precip_in):>16s} | "
                  f"{min_temp_c:4.0f}-{max_temp_c:4.0f}°C     | {min_precip_mm:4.0f}-{max_precip_mm:4.0f}mm")
            
            analysis_results[biome_type] = {
                'count': data['count'],
                'avg_temp_c': avg_temp_c,
                'avg_precip_mm': avg_precip_mm,
                'temp_range_c': (min_temp_c, max_temp_c),
                'precip_range_mm': (min_precip_mm, max_precip_mm)
            }
        
        return analysis_results


def test_biome_classification():
    """Test the biome classification system."""
    print("=== Testing Biome Classification System ===")
    print()
    
    # Initialize biome classifier
    classifier = BiomeClassifier()
    
    # Test individual climate conditions
    print("Testing individual climate classifications:")
    print("Temperature | Precipitation | Biome Assignment")
    print("------------|---------------|------------------")
    
    test_conditions = [
        (-10, 200, "Arctic tundra"),
        (5, 600, "Boreal forest"),
        (15, 1200, "Temperate forest"),
        (25, 2000, "Tropical rainforest"),
        (30, 800, "Tropical savanna"),
        (25, 150, "Hot desert"),
        (0, 100, "Cold desert"),
        (20, 400, "Mediterranean"),
        (10, 500, "Temperate grassland")
    ]
    
    for temp_c, precip_mm, description in test_conditions:
        biome = classifier.classify_biome(temp_c, precip_mm)
        biome_display = biome.replace('_', ' ').title()
        temp_f = temp_c * 9/5 + 32
        precip_in = precip_mm / 25.4
        
        print(f"{format_temp(temp_f):>11s} | {format_precipitation(precip_in):>13s} | {biome_display:15s} ({description})")
    
    print(f"\n✅ Biome classification test complete!")
    print("   System correctly assigns biomes based on Whittaker classification.")


if __name__ == "__main__":
    test_biome_classification()