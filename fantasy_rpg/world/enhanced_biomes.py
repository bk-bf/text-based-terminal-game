"""
Fantasy RPG - Enhanced Biome System

8 core biomes with distinct environmental properties and rich gameplay mechanics.
Each biome has unique characteristics that create meaningful gameplay decisions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum


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


class ResourceType(Enum):
    """Types of resources available in biomes."""
    FOOD = "food"
    WATER = "water"
    WOOD = "wood"
    STONE = "stone"
    METAL = "metal"
    HERBS = "herbs"
    GAME = "game"
    FISH = "fish"


class HazardType(Enum):
    """Types of environmental hazards."""
    EXTREME_COLD = "extreme_cold"
    EXTREME_HEAT = "extreme_heat"
    PREDATORS = "predators"
    DISEASE = "disease"
    STORMS = "storms"
    AVALANCHE = "avalanche"
    FLOODING = "flooding"
    DROUGHT = "drought"
    POISONOUS_PLANTS = "poisonous_plants"
    QUICKSAND = "quicksand"


@dataclass
class ResourceAvailability:
    """Resource availability data for a biome."""
    resource_type: ResourceType
    abundance: float  # 0.0-1.0 scale
    seasonal_variation: float  # 0.0-1.0 (how much availability changes with seasons)
    difficulty_to_obtain: float  # 0.0-1.0 (skill check difficulty)
    description: str


@dataclass
class EnvironmentalHazard:
    """Environmental hazard data for a biome."""
    hazard_type: HazardType
    frequency: float  # 0.0-1.0 (how often it occurs)
    severity: float  # 0.0-1.0 (how dangerous it is)
    seasonal_modifier: float  # Multiplier for different seasons
    description: str
    mitigation_methods: List[str]


@dataclass
class SeasonalEffects:
    """Seasonal effects on biome characteristics."""
    spring: Dict[str, float]  # Modifiers for spring
    summer: Dict[str, float]  # Modifiers for summer
    autumn: Dict[str, float]  # Modifiers for autumn
    winter: Dict[str, float]  # Modifiers for winter


@dataclass
class EnhancedBiome:
    """
    Enhanced biome with detailed environmental properties and gameplay mechanics.
    
    This represents a complete ecosystem with all the information needed
    for rich environmental gameplay.
    """
    name: str
    display_name: str
    description: str
    
    # Climate requirements
    temp_range_c: Tuple[float, float]  # (min, max) temperature in Celsius
    precip_range_mm: Tuple[float, float]  # (min, max) precipitation in mm
    elevation_preference: Tuple[float, float]  # (min, max) elevation factor
    
    # Travel characteristics
    base_travel_speed: float  # 0.1-1.5 multiplier
    visibility_range: int  # meters
    navigation_difficulty: float  # 0.0-1.0 (higher = harder to navigate)
    
    # Shelter and survival
    natural_shelter_quality: float  # 0.0-1.0
    shelter_materials_available: List[str]
    fire_difficulty: float  # 0.0-1.0 (difficulty making fire)
    
    # Resources
    resources: List[ResourceAvailability] = field(default_factory=list)
    
    # Hazards
    hazards: List[EnvironmentalHazard] = field(default_factory=list)
    
    # Seasonal effects
    seasonal_effects: Optional[SeasonalEffects] = None
    
    # Gameplay characteristics
    exploration_rewards: List[str] = field(default_factory=list)  # What players might find
    settlement_suitability: float = 0.5  # 0.0-1.0 (how good for settlements)
    trade_route_value: float = 0.5  # 0.0-1.0 (value for trade routes)
    
    def get_resource_by_type(self, resource_type: ResourceType) -> Optional[ResourceAvailability]:
        """Get resource availability for a specific resource type."""
        for resource in self.resources:
            if resource.resource_type == resource_type:
                return resource
        return None
    
    def get_seasonal_modifier(self, season: str, property_name: str) -> float:
        """Get seasonal modifier for a specific property."""
        if not self.seasonal_effects:
            return 1.0
        
        season_data = getattr(self.seasonal_effects, season.lower(), {})
        return season_data.get(property_name, 1.0)
    
    def calculate_travel_time(self, base_time_minutes: int, season: str = "summer") -> int:
        """Calculate actual travel time considering biome effects."""
        speed_modifier = self.base_travel_speed
        seasonal_modifier = self.get_seasonal_modifier(season, "travel_speed")
        
        actual_time = base_time_minutes / (speed_modifier * seasonal_modifier)
        return int(actual_time)
    
    def get_hazard_risk(self, hazard_type: HazardType, season: str = "summer") -> float:
        """Get current risk level for a specific hazard type."""
        for hazard in self.hazards:
            if hazard.hazard_type == hazard_type:
                base_risk = hazard.frequency * hazard.severity
                seasonal_modifier = self.get_seasonal_modifier(season, hazard_type.value)
                return min(1.0, base_risk * seasonal_modifier)
        return 0.0


class EnhancedBiomeSystem:
    """
    Enhanced biome system with 8 core biomes featuring rich environmental properties.
    
    This system focuses on gameplay-relevant biome characteristics that create
    meaningful decisions for travel, survival, and settlement.
    """
    
    def __init__(self):
        """Initialize the enhanced biome system with 8 core biomes."""
        self.biomes = self._initialize_core_biomes()
        print("Initialized Enhanced Biome System with 8 core biomes")
        print("Each biome has detailed environmental properties and gameplay mechanics")
    
    def _initialize_core_biomes(self) -> Dict[str, EnhancedBiome]:
        """Initialize the 8 core biomes with detailed properties."""
        
        biomes = {}
        
        # 1. ARCTIC TUNDRA - Harsh survival challenge
        biomes["arctic_tundra"] = EnhancedBiome(
            name="arctic_tundra",
            display_name="Arctic Tundra",
            description="Frozen wasteland with permafrost, sparse vegetation, and extreme cold",
            temp_range_c=(-30.0, 5.0),
            precip_range_mm=(50, 400),
            elevation_preference=(0.0, 0.8),
            base_travel_speed=0.6,
            visibility_range=5000,  # Excellent visibility but harsh conditions
            navigation_difficulty=0.7,
            natural_shelter_quality=0.1,
            shelter_materials_available=["ice", "snow", "animal_hide"],
            fire_difficulty=0.9,
            resources=[
                ResourceAvailability(ResourceType.FOOD, 0.2, 0.8, 0.8, "Scarce lichens, occasional game"),
                ResourceAvailability(ResourceType.WATER, 0.3, 0.9, 0.6, "Ice and snow (needs melting)"),
                ResourceAvailability(ResourceType.WOOD, 0.0, 0.0, 1.0, "No trees available"),
                ResourceAvailability(ResourceType.STONE, 0.4, 0.1, 0.5, "Scattered rocks and permafrost"),
                ResourceAvailability(ResourceType.GAME, 0.3, 0.7, 0.9, "Seals, arctic foxes, caribou"),
            ],
            hazards=[
                EnvironmentalHazard(HazardType.EXTREME_COLD, 0.9, 0.9, 1.5, 
                                  "Life-threatening cold temperatures", 
                                  ["warm_clothing", "shelter", "fire"]),
                EnvironmentalHazard(HazardType.STORMS, 0.6, 0.7, 2.0,
                                  "Blizzards with zero visibility",
                                  ["shelter", "navigation_tools", "wait_it_out"]),
            ],
            seasonal_effects=SeasonalEffects(
                spring={"travel_speed": 0.8, "extreme_cold": 0.7},
                summer={"travel_speed": 1.2, "extreme_cold": 0.3},
                autumn={"travel_speed": 0.9, "extreme_cold": 0.8},
                winter={"travel_speed": 0.5, "extreme_cold": 1.5}
            ),
            exploration_rewards=["rare_minerals", "ancient_ice", "arctic_wildlife"],
            settlement_suitability=0.1,
            trade_route_value=0.2
        )
        
        # 2. BOREAL FOREST - Resource rich but dangerous
        biomes["boreal_forest"] = EnhancedBiome(
            name="boreal_forest",
            display_name="Boreal Forest",
            description="Dense coniferous forest with abundant resources but hidden dangers",
            temp_range_c=(-20.0, 20.0),
            precip_range_mm=(300, 800),
            elevation_preference=(0.0, 0.7),
            base_travel_speed=0.7,
            visibility_range=100,  # Limited by dense trees
            navigation_difficulty=0.6,
            natural_shelter_quality=0.7,
            shelter_materials_available=["wood", "bark", "pine_needles", "animal_hide"],
            fire_difficulty=0.3,
            resources=[
                ResourceAvailability(ResourceType.FOOD, 0.6, 0.6, 0.5, "Berries, nuts, mushrooms"),
                ResourceAvailability(ResourceType.WATER, 0.8, 0.4, 0.3, "Streams and springs"),
                ResourceAvailability(ResourceType.WOOD, 1.0, 0.2, 0.2, "Abundant conifers"),
                ResourceAvailability(ResourceType.GAME, 0.7, 0.5, 0.6, "Deer, elk, small game"),
                ResourceAvailability(ResourceType.HERBS, 0.5, 0.7, 0.4, "Medicinal plants and fungi"),
            ],
            hazards=[
                EnvironmentalHazard(HazardType.PREDATORS, 0.4, 0.6, 1.2,
                                  "Bears, wolves, and other large predators",
                                  ["fire", "noise", "weapons", "climb_trees"]),
                EnvironmentalHazard(HazardType.DISEASE, 0.2, 0.4, 0.8,
                                  "Tick-borne diseases and parasites",
                                  ["protective_clothing", "regular_checks", "herbs"]),
            ],
            seasonal_effects=SeasonalEffects(
                spring={"travel_speed": 0.8, "predators": 1.3},  # Animals more active
                summer={"travel_speed": 1.0, "disease": 1.5},    # Peak tick season
                autumn={"travel_speed": 0.9, "predators": 1.4},  # Animals preparing for winter
                winter={"travel_speed": 0.6, "predators": 0.7}   # Many animals hibernate
            ),
            exploration_rewards=["rare_herbs", "ancient_trees", "hidden_groves", "wildlife_sanctuaries"],
            settlement_suitability=0.7,
            trade_route_value=0.6
        )
        
        # 3. TEMPERATE GRASSLAND - Easy travel, moderate resources
        biomes["temperate_grassland"] = EnhancedBiome(
            name="temperate_grassland",
            display_name="Temperate Grassland",
            description="Rolling plains with excellent visibility and moderate resources",
            temp_range_c=(0.0, 25.0),
            precip_range_mm=(250, 750),
            elevation_preference=(0.0, 0.5),
            base_travel_speed=1.3,
            visibility_range=10000,  # Excellent long-distance visibility
            navigation_difficulty=0.2,
            natural_shelter_quality=0.2,
            shelter_materials_available=["grass", "mud", "scattered_stones"],
            fire_difficulty=0.4,
            resources=[
                ResourceAvailability(ResourceType.FOOD, 0.5, 0.8, 0.4, "Grains, roots, prairie plants"),
                ResourceAvailability(ResourceType.WATER, 0.4, 0.7, 0.5, "Seasonal streams and ponds"),
                ResourceAvailability(ResourceType.WOOD, 0.1, 0.3, 0.7, "Scattered trees along waterways"),
                ResourceAvailability(ResourceType.GAME, 0.6, 0.6, 0.5, "Bison, prairie dogs, birds"),
                ResourceAvailability(ResourceType.STONE, 0.2, 0.1, 0.6, "Occasional outcrops"),
            ],
            hazards=[
                EnvironmentalHazard(HazardType.STORMS, 0.5, 0.6, 1.8,
                                  "Severe thunderstorms and tornadoes",
                                  ["underground_shelter", "early_warning", "avoid_high_ground"]),
                EnvironmentalHazard(HazardType.DROUGHT, 0.3, 0.7, 2.5,
                                  "Extended dry periods affecting water sources",
                                  ["water_conservation", "deep_wells", "migration"]),
            ],
            seasonal_effects=SeasonalEffects(
                spring={"travel_speed": 1.0, "storms": 1.5},
                summer={"travel_speed": 1.2, "drought": 1.8},
                autumn={"travel_speed": 1.1, "storms": 1.2},
                winter={"travel_speed": 0.8, "extreme_cold": 0.6}
            ),
            exploration_rewards=["vast_herds", "ancient_burial_mounds", "rare_flowers"],
            settlement_suitability=0.8,
            trade_route_value=0.9
        )
        
        # 4. TEMPERATE FOREST - Balanced ecosystem
        biomes["temperate_forest"] = EnhancedBiome(
            name="temperate_forest",
            display_name="Temperate Forest",
            description="Deciduous forest with seasonal changes and abundant resources",
            temp_range_c=(5.0, 25.0),
            precip_range_mm=(600, 1500),
            elevation_preference=(0.0, 0.6),
            base_travel_speed=0.8,
            visibility_range=200,
            navigation_difficulty=0.4,
            natural_shelter_quality=0.8,
            shelter_materials_available=["hardwood", "bark", "leaves", "stone"],
            fire_difficulty=0.2,
            resources=[
                ResourceAvailability(ResourceType.FOOD, 0.8, 0.9, 0.3, "Nuts, berries, mushrooms, game"),
                ResourceAvailability(ResourceType.WATER, 0.9, 0.3, 0.2, "Streams, springs, and ponds"),
                ResourceAvailability(ResourceType.WOOD, 0.9, 0.4, 0.2, "Hardwood and softwood trees"),
                ResourceAvailability(ResourceType.GAME, 0.7, 0.5, 0.4, "Deer, boar, small game, birds"),
                ResourceAvailability(ResourceType.HERBS, 0.7, 0.8, 0.3, "Diverse medicinal plants"),
                ResourceAvailability(ResourceType.STONE, 0.4, 0.1, 0.4, "Limestone and granite outcrops"),
            ],
            hazards=[
                EnvironmentalHazard(HazardType.PREDATORS, 0.2, 0.4, 1.0,
                                  "Occasional bears and wild boar",
                                  ["noise", "fire", "climb_trees", "weapons"]),
                EnvironmentalHazard(HazardType.POISONOUS_PLANTS, 0.3, 0.3, 0.8,
                                  "Toxic berries and plants",
                                  ["plant_knowledge", "careful_foraging", "antidotes"]),
            ],
            seasonal_effects=SeasonalEffects(
                spring={"travel_speed": 0.9, "poisonous_plants": 1.2},
                summer={"travel_speed": 1.0, "poisonous_plants": 1.0},
                autumn={"travel_speed": 0.8, "poisonous_plants": 0.8},  # Leaves fall, easier to see
                winter={"travel_speed": 0.7, "poisonous_plants": 0.3}   # Most plants dormant
            ),
            exploration_rewards=["ancient_ruins", "rare_hardwoods", "hidden_clearings", "natural_springs"],
            settlement_suitability=0.9,
            trade_route_value=0.7
        )
        
        # 5. MEDITERRANEAN SCRUBLAND - Fire-prone, moderate resources
        biomes["mediterranean_scrub"] = EnhancedBiome(
            name="mediterranean_scrub",
            display_name="Mediterranean Scrubland",
            description="Dry shrubland with aromatic plants and fire-adapted vegetation",
            temp_range_c=(10.0, 30.0),
            precip_range_mm=(200, 800),
            elevation_preference=(0.0, 0.6),
            base_travel_speed=0.9,
            visibility_range=1000,
            navigation_difficulty=0.3,
            natural_shelter_quality=0.4,
            shelter_materials_available=["shrub_wood", "stone", "clay"],
            fire_difficulty=0.2,
            resources=[
                ResourceAvailability(ResourceType.FOOD, 0.4, 0.8, 0.5, "Olives, herbs, small game"),
                ResourceAvailability(ResourceType.WATER, 0.3, 0.9, 0.7, "Seasonal streams and springs"),
                ResourceAvailability(ResourceType.WOOD, 0.3, 0.3, 0.4, "Shrubs and small trees"),
                ResourceAvailability(ResourceType.HERBS, 0.8, 0.6, 0.3, "Aromatic and medicinal plants"),
                ResourceAvailability(ResourceType.STONE, 0.6, 0.1, 0.3, "Limestone and marble"),
            ],
            hazards=[
                EnvironmentalHazard(HazardType.EXTREME_HEAT, 0.6, 0.7, 2.0,
                                  "Dangerous summer heat",
                                  ["shade", "water", "travel_at_night"]),
                EnvironmentalHazard(HazardType.STORMS, 0.4, 0.5, 1.5,
                                  "Wildfires from lightning strikes",
                                  ["firebreaks", "water_sources", "escape_routes"]),
            ],
            seasonal_effects=SeasonalEffects(
                spring={"travel_speed": 1.1, "storms": 0.8},
                summer={"travel_speed": 0.7, "extreme_heat": 1.8, "storms": 1.5},
                autumn={"travel_speed": 1.0, "extreme_heat": 1.2},
                winter={"travel_speed": 1.2, "extreme_heat": 0.2}
            ),
            exploration_rewards=["ancient_olive_groves", "marble_quarries", "aromatic_gardens"],
            settlement_suitability=0.6,
            trade_route_value=0.8
        )
        
        # 6. HOT DESERT - Extreme survival challenge
        biomes["hot_desert"] = EnhancedBiome(
            name="hot_desert",
            display_name="Hot Desert",
            description="Scorching wasteland with extreme temperatures and scarce resources",
            temp_range_c=(10.0, 50.0),
            precip_range_mm=(0, 250),
            elevation_preference=(0.0, 0.5),
            base_travel_speed=0.7,
            visibility_range=8000,  # Good visibility but heat shimmer
            navigation_difficulty=0.8,
            natural_shelter_quality=0.2,
            shelter_materials_available=["sand", "rock", "rare_oasis_materials"],
            fire_difficulty=0.1,  # Easy to start, hard to maintain
            resources=[
                ResourceAvailability(ResourceType.FOOD, 0.1, 0.5, 0.9, "Cacti, desert plants, rare game"),
                ResourceAvailability(ResourceType.WATER, 0.1, 0.8, 0.9, "Rare oases and underground sources"),
                ResourceAvailability(ResourceType.WOOD, 0.0, 0.2, 0.9, "Rare desert shrubs"),
                ResourceAvailability(ResourceType.STONE, 0.5, 0.1, 0.4, "Sandstone and rare minerals"),
                ResourceAvailability(ResourceType.METAL, 0.3, 0.1, 0.8, "Mineral deposits in rocky areas"),
            ],
            hazards=[
                EnvironmentalHazard(HazardType.EXTREME_HEAT, 0.9, 0.9, 1.8,
                                  "Life-threatening daytime temperatures",
                                  ["shade", "water", "travel_at_night", "cooling_clothing"]),
                EnvironmentalHazard(HazardType.STORMS, 0.3, 0.6, 1.0,
                                  "Sandstorms with zero visibility",
                                  ["shelter", "face_protection", "wait_it_out"]),
            ],
            seasonal_effects=SeasonalEffects(
                spring={"travel_speed": 1.0, "extreme_heat": 0.8},
                summer={"travel_speed": 0.5, "extreme_heat": 1.5},
                autumn={"travel_speed": 0.9, "extreme_heat": 1.0},
                winter={"travel_speed": 1.2, "extreme_heat": 0.4}
            ),
            exploration_rewards=["rare_minerals", "ancient_ruins", "hidden_oases", "precious_gems"],
            settlement_suitability=0.2,
            trade_route_value=0.4
        )
        
        # 7. TROPICAL RAINFOREST - High biodiversity, navigation challenges
        biomes["tropical_rainforest"] = EnhancedBiome(
            name="tropical_rainforest",
            display_name="Tropical Rainforest",
            description="Dense jungle with incredible biodiversity and hidden dangers",
            temp_range_c=(20.0, 35.0),
            precip_range_mm=(1500, 4000),
            elevation_preference=(0.0, 0.4),
            base_travel_speed=0.4,
            visibility_range=50,  # Very limited by dense vegetation
            navigation_difficulty=0.9,
            natural_shelter_quality=0.6,
            shelter_materials_available=["tropical_wood", "palm_fronds", "vines", "bamboo"],
            fire_difficulty=0.8,  # Wet conditions make fire difficult
            resources=[
                ResourceAvailability(ResourceType.FOOD, 0.9, 0.4, 0.6, "Fruits, nuts, abundant game"),
                ResourceAvailability(ResourceType.WATER, 1.0, 0.2, 0.2, "Abundant rainfall and streams"),
                ResourceAvailability(ResourceType.WOOD, 1.0, 0.2, 0.4, "Diverse tropical hardwoods"),
                ResourceAvailability(ResourceType.HERBS, 0.9, 0.3, 0.7, "Incredible variety of medicinal plants"),
                ResourceAvailability(ResourceType.GAME, 0.8, 0.3, 0.7, "Monkeys, birds, jungle cats"),
            ],
            hazards=[
                EnvironmentalHazard(HazardType.DISEASE, 0.8, 0.7, 1.0,
                                  "Tropical diseases and parasites",
                                  ["protective_clothing", "medicine", "clean_water", "insect_repellent"]),
                EnvironmentalHazard(HazardType.PREDATORS, 0.6, 0.8, 1.0,
                                  "Jaguars, snakes, and venomous creatures",
                                  ["noise", "fire", "antivenom", "climb_trees"]),
                EnvironmentalHazard(HazardType.POISONOUS_PLANTS, 0.7, 0.6, 1.0,
                                  "Toxic plants and fungi",
                                  ["plant_knowledge", "protective_gear", "antidotes"]),
            ],
            seasonal_effects=SeasonalEffects(
                spring={"travel_speed": 1.0, "disease": 1.0},
                summer={"travel_speed": 0.8, "disease": 1.3, "predators": 1.2},
                autumn={"travel_speed": 0.9, "disease": 1.1},
                winter={"travel_speed": 1.1, "disease": 0.8}  # Dry season
            ),
            exploration_rewards=["rare_species", "medicinal_plants", "ancient_temples", "precious_woods"],
            settlement_suitability=0.4,
            trade_route_value=0.6
        )
        
        # 8. ALPINE MOUNTAINS - Extreme elevation, unique resources
        biomes["alpine_mountains"] = EnhancedBiome(
            name="alpine_mountains",
            display_name="Alpine Mountains",
            description="High-altitude environment above tree line with extreme conditions",
            temp_range_c=(-15.0, 15.0),
            precip_range_mm=(300, 1500),
            elevation_preference=(0.7, 1.0),
            base_travel_speed=0.3,
            visibility_range=15000,  # Excellent visibility when clear
            navigation_difficulty=0.8,
            natural_shelter_quality=0.3,
            shelter_materials_available=["stone", "ice", "sparse_vegetation"],
            fire_difficulty=0.7,  # Thin air makes fire difficult
            resources=[
                ResourceAvailability(ResourceType.FOOD, 0.2, 0.6, 0.9, "Alpine plants, rare mountain game"),
                ResourceAvailability(ResourceType.WATER, 0.6, 0.8, 0.4, "Snowmelt and mountain streams"),
                ResourceAvailability(ResourceType.WOOD, 0.0, 0.0, 1.0, "No trees at this elevation"),
                ResourceAvailability(ResourceType.STONE, 0.9, 0.1, 0.3, "Abundant granite and minerals"),
                ResourceAvailability(ResourceType.METAL, 0.7, 0.1, 0.7, "Rich mineral veins"),
            ],
            hazards=[
                EnvironmentalHazard(HazardType.EXTREME_COLD, 0.8, 0.8, 1.5,
                                  "Severe cold and wind chill",
                                  ["warm_clothing", "shelter", "fire"]),
                EnvironmentalHazard(HazardType.AVALANCHE, 0.4, 0.9, 2.0,
                                  "Deadly snow avalanches",
                                  ["route_planning", "avalanche_gear", "weather_awareness"]),
                EnvironmentalHazard(HazardType.STORMS, 0.6, 0.8, 1.8,
                                  "Sudden mountain storms",
                                  ["weather_prediction", "shelter", "descent"]),
            ],
            seasonal_effects=SeasonalEffects(
                spring={"travel_speed": 0.8, "avalanche": 1.8},  # Snowmelt increases avalanche risk
                summer={"travel_speed": 1.2, "extreme_cold": 0.6, "storms": 1.2},
                autumn={"travel_speed": 0.9, "extreme_cold": 1.0, "storms": 1.4},
                winter={"travel_speed": 0.4, "extreme_cold": 1.8, "avalanche": 1.5}
            ),
            exploration_rewards=["rare_minerals", "mountain_crystals", "ancient_peaks", "scenic_vistas"],
            settlement_suitability=0.2,
            trade_route_value=0.3
        )
        
        return biomes
    
    def get_biome(self, biome_name: str) -> Optional[EnhancedBiome]:
        """Get a biome by name."""
        return self.biomes.get(biome_name)
    
    def classify_biome(self, avg_temp_c: float, annual_precip_mm: float, 
                      elevation: float = 0.0) -> str:
        """
        Classify biome based on climate conditions.
        
        Args:
            avg_temp_c: Average annual temperature in Celsius
            annual_precip_mm: Annual precipitation in millimeters
            elevation: Elevation factor (0.0-1.0)
        
        Returns:
            Biome name from the 8 core biomes
        """
        # Check elevation first for alpine
        if elevation > 0.7:
            return "alpine_mountains"
        
        # Temperature-based classification
        if avg_temp_c < -5:
            return "arctic_tundra"
        elif avg_temp_c < 5:
            if annual_precip_mm > 300:
                return "boreal_forest"
            else:
                return "arctic_tundra"
        elif avg_temp_c < 15:
            if annual_precip_mm < 300:
                return "temperate_grassland"
            elif annual_precip_mm > 800:
                return "temperate_forest"
            else:
                return "temperate_grassland"
        elif avg_temp_c < 25:
            if annual_precip_mm < 400:
                return "mediterranean_scrub"
            elif annual_precip_mm > 1200:
                return "temperate_forest"
            else:
                return "mediterranean_scrub"
        else:  # Hot climates
            if annual_precip_mm < 400:
                return "hot_desert"
            else:
                return "tropical_rainforest"
    
    def analyze_biome_properties(self) -> None:
        """Analyze and display properties of all 8 core biomes."""
        print("\n" + "="*80)
        print("🌍 ENHANCED BIOME SYSTEM - 8 CORE BIOMES")
        print("="*80)
        
        for biome_name, biome in self.biomes.items():
            print(f"\n🌿 {biome.display_name.upper()}")
            print("-" * 60)
            print(f"Description: {biome.description}")
            
            # Climate requirements
            temp_min_f = biome.temp_range_c[0] * 9/5 + 32
            temp_max_f = biome.temp_range_c[1] * 9/5 + 32
            precip_min_in = biome.precip_range_mm[0] / 25.4
            precip_max_in = biome.precip_range_mm[1] / 25.4
            
            print(f"Temperature: {format_temp(temp_min_f)} to {format_temp(temp_max_f)}")
            print(f"Precipitation: {format_precipitation(precip_min_in)} to {format_precipitation(precip_max_in)}")
            
            # Travel characteristics
            print(f"Travel Speed: {biome.base_travel_speed:.1f}x base speed")
            print(f"Visibility: {biome.visibility_range:,} meters")
            print(f"Navigation Difficulty: {biome.navigation_difficulty:.1f}/1.0")
            
            # Key resources
            key_resources = [r.resource_type.value for r in biome.resources if r.abundance > 0.5]
            print(f"Abundant Resources: {', '.join(key_resources) if key_resources else 'None'}")
            
            # Major hazards
            major_hazards = [h.hazard_type.value for h in biome.hazards if h.frequency > 0.5]
            print(f"Major Hazards: {', '.join(major_hazards) if major_hazards else 'None'}")
            
            # Settlement suitability
            suitability = "Excellent" if biome.settlement_suitability > 0.8 else \
                         "Good" if biome.settlement_suitability > 0.6 else \
                         "Fair" if biome.settlement_suitability > 0.4 else \
                         "Poor" if biome.settlement_suitability > 0.2 else "Hostile"
            print(f"Settlement Suitability: {suitability} ({biome.settlement_suitability:.1f}/1.0)")


def test_enhanced_biomes():
    """Test the enhanced biome system."""
    print("=== Testing Enhanced Biome System ===")
    print("8 Core Biomes with Distinct Environmental Properties")
    print()
    
    # Initialize system
    biome_system = EnhancedBiomeSystem()
    
    # Analyze all biomes
    biome_system.analyze_biome_properties()
    
    # Test biome classification
    print(f"\n" + "="*80)
    print("🔍 BIOME CLASSIFICATION EXAMPLES")
    print("="*80)
    
    test_conditions = [
        (-25, 150, 0.1, "Arctic conditions"),
        (2, 500, 0.3, "Boreal conditions"),
        (12, 400, 0.2, "Temperate grassland"),
        (15, 1000, 0.3, "Temperate forest"),
        (22, 300, 0.4, "Mediterranean scrub"),
        (35, 100, 0.2, "Hot desert"),
        (28, 2500, 0.2, "Tropical rainforest"),
        (5, 800, 0.9, "Alpine mountains")
    ]
    
    print("Temperature | Precipitation | Elevation | Biome Classification")
    print("------------|---------------|-----------|----------------------")
    
    for temp_c, precip_mm, elevation, description in test_conditions:
        biome_name = biome_system.classify_biome(temp_c, precip_mm, elevation)
        biome = biome_system.get_biome(biome_name)
        
        temp_f = temp_c * 9/5 + 32
        precip_in = precip_mm / 25.4
        
        print(f"{format_temp(temp_f):>11s} | {format_precipitation(precip_in):>13s} | {elevation:8.1f}  | "
              f"{biome.display_name if biome else biome_name} ({description})")
    
    print(f"\n🎯 GAMEPLAY FEATURES")
    print("="*80)
    print("✓ 8 distinct biomes with unique environmental properties")
    print("✓ Detailed resource availability and seasonal variation")
    print("✓ Realistic environmental hazards with mitigation strategies")
    print("✓ Travel speed and navigation difficulty based on terrain")
    print("✓ Settlement suitability and trade route value")
    print("✓ Seasonal effects that change biome characteristics")
    print("✓ Rich exploration rewards encouraging biome-specific adventures")
    
    print(f"\n✅ Enhanced biome system complete!")
    print("   Each biome creates distinct gameplay experiences and strategic decisions.")


if __name__ == "__main__":
    test_enhanced_biomes()