# Fantasy RPG - Geographic & Environmental Simulation Design

## Overview

This design implements a comprehensive geographic and environmental simulation system for a text-based RPG, focusing on realistic terrain, weather systems, and survival mechanics that make travel meaningful and challenging.

**Philosophy:** Full environmental simulation creates meaningful travel decisions. Weather, terrain, and survival needs should drive player strategy and create emergent gameplay moments.

**Core Principle:** CDDA-level environmental depth adapted for text-based gameplay - every hex crossing should involve real risk assessment and resource management.

---

## Architecture Philosophy

### Why Deep Environmental Simulation for Text RPG

**The Problem with Shallow Travel Systems:**
- Movement between locations feels trivial and meaningless
- Weather is cosmetic rather than mechanically significant
- No resource management or survival considerations
- Travel decisions lack strategic depth

**The Environmental Simulation Approach:**
- Weather patterns affect travel speed, visibility, and safety
- Terrain creates real navigation challenges and route planning
- Survival mechanics (hunger, thirst, temperature) drive resource management
- Environmental hazards create meaningful risk/reward decisions
- Seasonal changes affect available routes and strategies

### Environmental Simulation Pipeline

```
Terrain Generation (Elevation, Geology, Hydrology)
    ↓
Climate Simulation (Temperature, Rainfall, Wind Patterns)
    ↓
Biome Assignment (Resource Distribution, Hazards)
    ↓
Weather System Initialization (Seasonal Patterns, Storm Tracks)
    ↓
Real-Time Environmental Updates (Weather Changes, Seasonal Effects)
    ↓
Player Travel Commands (move, camp, forage, predict weather)
    ↓
Environmental Challenge Resolution (Survival checks, resource consumption)
```

---

## Geographic Foundation

### Realistic Terrain Generation

**Multi-Layer Terrain System:**
- Continental plates simulation for realistic landmass shapes
- Multi-octave Perlin/Simplex noise for natural terrain variation
- Hydraulic erosion simulation for realistic valley formation
- Drainage calculation for logical water flow patterns

**Elevation & Geology:**
- Elevation affects temperature, weather patterns, and travel difficulty
- Rock types determine resource availability and natural shelter
- Geological features create natural hazards (avalanche zones, unstable ground)
- Mineral deposits affect long-term settlement viability

**Terrain Types with Gameplay Impact:**
```python
TERRAIN_TYPES = {
    "plains": {
        "travel_speed": 1.0,
        "visibility": "excellent",
        "shelter": "poor",
        "water_sources": "rare"
    },
    "forest": {
        "travel_speed": 0.7,
        "visibility": "limited", 
        "shelter": "good",
        "foraging": "excellent"
    },
    "mountains": {
        "travel_speed": 0.3,
        "altitude_effects": True,
        "avalanche_risk": True,
        "shelter": "caves_available"
    },
    "swamp": {
        "travel_speed": 0.4,
        "disease_risk": True,
        "navigation_dc": 15,
        "water_sources": "abundant_unsafe"
    }
}
```

### Hydrology & Water Systems

**Water Source Distribution:**
- Rivers provide reliable water but may require purification
- Springs offer clean water but limited quantity
- Lakes and ponds may be seasonal or contaminated
- Wells in settled areas provide safe water access

**Seasonal Water Availability:**
- Spring snowmelt creates flooding and abundant water
- Summer drought reduces water sources and increases travel difficulty
- Winter freezing makes water sources inaccessible
- Monsoon seasons create temporary flooding and navigation hazards

**Water Quality & Safety:**
- Stagnant water sources risk disease
- Fast-flowing rivers are generally safe but may be difficult to access
- Magical contamination creates dangerous but detectable water sources
- Purification methods: boiling, magical purification, alchemical treatments

---

## Climate & Weather Systems

### Climate Zone Generation

**Temperature Zones:**
- Latitude-based temperature gradients with realistic variation
- Elevation effects: temperature drops 3.5°F per 1000 feet elevation
- Seasonal temperature swings based on distance from equator
- Coastal moderation effects reduce temperature extremes

**Precipitation Patterns:**
- Prevailing wind patterns carry moisture from oceans
- Mountain ranges create rain shadows (dry leeward sides)
- Seasonal monsoons in appropriate climate zones
- Desert formation in rain shadow areas and continental interiors

**Climate Zone Types:**
```python
CLIMATE_ZONES = {
    "arctic": {
        "temp_range": (-40, 32),
        "growing_season": 0,
        "precipitation": "low_snow",
        "hazards": ["blizzards", "extreme_cold"]
    },
    "temperate": {
        "temp_range": (20, 80),
        "growing_season": 180,
        "precipitation": "moderate_rain",
        "hazards": ["storms", "flooding"]
    },
    "desert": {
        "temp_range": (40, 120),
        "growing_season": 60,
        "precipitation": "very_low",
        "hazards": ["sandstorms", "extreme_heat"]
    },
    "tropical": {
        "temp_range": (60, 95),
        "growing_season": 365,
        "precipitation": "high_rain",
        "hazards": ["hurricanes", "disease"]
    }
}
```

### Weather Simulation System

**Real-Time Weather Generation:**
```python
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
    
    def get_travel_description(self) -> str:
        """Generate text description for player"""
        desc = f"Temperature: {self.feels_like}°F (feels like)\n"
        desc += f"Wind: {self.wind_speed} mph from the {self.wind_direction}\n"
        
        if self.precipitation > 0:
            intensity = "light" if self.precipitation < 30 else "heavy" if self.precipitation < 70 else "torrential"
            desc += f"{intensity.title()} {self.precipitation_type}\n"
        
        if self.visibility < 500:
            desc += "Visibility severely limited\n"
        
        return desc
```

**Weather Prediction System:**
```python
class WeatherSystem:
    """Predictable weather with skill-based forecasting"""
    
    def player_predict_weather(self, player: Player, location: HexCoords) -> PredictionResult:
        """Player attempts weather prediction (Survival check)"""
        
        # Base DC depends on climate stability
        base_dc = 10 + self.climate_zones[location].volatility
        
        # Survival skill check
        roll = player.skill_check("survival")
        
        if roll >= base_dc + 10:
            # Excellent - accurate 7-day forecast
            return PredictionResult(
                accuracy="excellent",
                forecast=self.forecast[:7],
                confidence=0.9,
                description="You read the signs clearly - the weather patterns are obvious to you."
            )
        elif roll >= base_dc + 5:
            # Good - accurate 3-day forecast
            return PredictionResult(
                accuracy="good", 
                forecast=self.forecast[:3],
                confidence=0.7,
                description="You can predict the next few days with reasonable confidence."
            )
        elif roll >= base_dc:
            # Basic - next day only
            return PredictionResult(
                accuracy="basic",
                forecast=self.forecast[:1], 
                confidence=0.5,
                description="You can make a rough guess about tomorrow's weather."
            )
        else:
            # Failed - inaccurate forecast
            return PredictionResult(
                accuracy="failed",
                forecast=self._generate_false_forecast(),
                confidence=0.2,
                description="The signs are unclear - you're not sure what to expect."
            )
```

## Survival Mechanics

### Player Environmental State

**CDDA-Style Survival Tracking:**
```python
@dataclass
class PlayerState:
    """Complete survival state tracking"""
    
    # Core D&D stats
    hp: int
    stamina: int
    
    # Survival needs (0-100 scale)
    hunger: int  # 0 (starving) to 100 (full)
    thirst: int  # 0 (dying of thirst) to 100 (hydrated)
    
    # Temperature regulation
    body_temperature: float  # 98.6°F normal, death at <95°F or >104°F
    warmth: int  # From clothing/shelter, 0-100
    
    # Environmental exposure
    wetness: int  # 0 (dry) to 100 (soaked)
    exposure_time: int  # Minutes exposed to harsh conditions
    
    # Status effects
    conditions: list[Condition]  # Hypothermia, Heatstroke, Exhaustion, etc.
    
    # Carried resources
    carried_food: int  # Days of rations
    carried_water: int  # Days of water
    firewood: int  # Hours of warmth
    
    def apply_environmental_effects(self, environment: Environment, duration_minutes: int):
        """Process survival mechanics every game minute"""
        
        # Temperature effects
        temp_diff = environment.temperature - self.body_temperature
        if abs(temp_diff) > 10:
            self._apply_temperature_stress(temp_diff, duration_minutes)
        
        # Exposure (wind, rain, snow)
        if environment.precipitation > 0 and not self.has_shelter:
            self.wetness += environment.precipitation * duration_minutes
            self.warmth -= self.wetness / 10
        
        # Resource consumption
        self.hunger -= duration_minutes * 0.1
        self.thirst -= duration_minutes * 0.2  # Thirst faster than hunger
        
        # Check for conditions
        if self.body_temperature < 95:
            self.add_condition(Condition.HYPOTHERMIA)
        if self.hunger < 10:
            self.add_condition(Condition.STARVING)
        if self.thirst < 10:
            self.add_condition(Condition.DEHYDRATED)
```

**Environmental Hazards:**
- **Hypothermia:** -4 DEX, -10 movement speed, eventual death
- **Heatstroke:** -2 CON, -4 INT, confusion effects
- **Dehydration:** -2 all physical stats, hallucinations
- **Starvation:** -2 STR/CON, reduced healing
- **Exhaustion:** -2 all rolls, -50% max stamina

### Travel Decision System

**Comprehensive Travel Assessment:**
```python
class TravelEngine:
    """Handle hex-to-hex travel with full environmental simulation"""
    
    def initiate_travel(self, party: Party, destination: HexCoords):
        """Present travel assessment to player"""
        
        current_hex = self.world.get_hex(party.position)
        dest_hex = self.world.get_hex(destination)
        
        # Calculate travel challenge
        terrain_difficulty = self._calculate_terrain_difficulty(current_hex, dest_hex)
        base_time = 30 * terrain_difficulty  # 30 min to 4+ hours
        
        # Weather impact
        weather = self.weather_system.current_weather
        travel_mod = weather.get_travel_modifier()
        actual_time = base_time / travel_mod.speed_penalty
        
        # Display comprehensive assessment
        self._display_travel_assessment(party, dest_hex, weather, actual_time)
        
        # Player choice
        choice = self._get_player_choice()
        
        if choice == "proceed":
            self._execute_travel(party, destination, actual_time, travel_mod)
        elif choice == "make_camp":
            self._make_camp(party, current_hex)
        elif choice == "predict_weather":
            self._attempt_weather_prediction(party)
    
    def _display_travel_assessment(self, party: Party, dest_hex: Hex, 
                                 weather: WeatherState, time: int):
        """Show detailed travel information"""
        
        ui.display(f"""
╔══════════════════════════════════════════════════════════╗
║ TRAVEL ASSESSMENT: To {dest_hex.name}                    ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║ TERRAIN: {dest_hex.terrain_description}                 ║
║ DISTANCE: {dest_hex.distance} miles                     ║
║ ESTIMATED TIME: {time} minutes                          ║
║                                                          ║
║ CURRENT WEATHER: {weather.description}                  ║
║ Temperature: {weather.feels_like}°F (feels like)        ║
║ Visibility: {weather.visibility} feet                   ║
║ Wind: {weather.wind_speed} mph from {weather.wind_dir}  ║
║                                                          ║
║ RISKS:                                                   ║
║ {self._list_environmental_risks(weather, dest_hex)}     ║
║                                                          ║
║ PARTY STATUS:                                            ║
║ Food: {party.total_food} days                           ║
║ Water: {party.total_water} days                         ║
║ Warmth: {party.average_warmth}/100                      ║
║ Fatigue: {party.average_fatigue}%                       ║
║                                                          ║
║ SURVIVAL CHECK (DC {self._calculate_survival_dc()}):    ║
║ Your Survival: +{party.best_survival_bonus}             ║
║ Estimated Success: {self._estimate_success()}%          ║
╚══════════════════════════════════════════════════════════╝

OPTIONS:
[1] Proceed with travel (risk exposure, faster arrival)
[2] Make camp and wait out weather (use supplies, stay safe)
[3] Try to predict weather pattern (Survival check)
[4] Turn back

> _
        """)
```

### Real-Time Environmental Updates

**Continuous Environmental Simulation:**
```python
class EnvironmentalEngine:
    """Manages real-time environmental changes during gameplay"""
    
    def update_environment(self, world: World, time_passed_minutes: int):
        """Update environmental state as game progresses"""
        
        # Weather progression
        self.weather_system.advance_time(time_passed_minutes)
        
        # Seasonal changes
        if self._season_changed():
            self._update_seasonal_conditions(world)
        
        # Resource regeneration
        self._update_resource_availability(world, time_passed_minutes)
        
        # Natural hazard checks
        self._check_natural_hazards(world)
    
    def _update_seasonal_conditions(self, world: World):
        """Apply seasonal changes to terrain"""
        
        current_season = self._get_current_season()
        
        for hex_coords, hex_data in world.hexes.items():
            if current_season == "winter":
                if hex_data.climate_zone.has_snow:
                    hex_data.seasonal_conditions = "snow_covered"
                    hex_data.travel_difficulty *= 2.0
                    hex_data.water_sources = self._freeze_water_sources(hex_data.water_sources)
            
            elif current_season == "spring":
                if hex_data.elevation > 3000:
                    hex_data.seasonal_conditions = "muddy_from_snowmelt"
                    hex_data.travel_difficulty *= 1.5
                hex_data.forageable_food *= 1.5  # Spring growth
            
            elif current_season == "summer":
                if hex_data.climate_zone == "desert":
                    hex_data.temperature_modifier += 20
                    hex_data.water_sources = self._reduce_water_availability(hex_data.water_sources)
            
            elif current_season == "autumn":
                hex_data.forageable_food *= 2.0  # Harvest season
                hex_data.firewood *= 1.5  # Fallen branches
```

---

## Emergent Storytelling Examples

### Location Discovery with Real History

**Example: Ruined Capital**
```python
# Player examines ruins - all details below are from REAL simulation
player.examine_ruins()

> "These are the ruins of Khaz-Durim, capital of the Dwarven Empire.
> 
> Founded in year 134 by King Thorin Ironforge, the city prospered for 
> 400 years as the center of dwarven metalworking.
> 
> In year 537, during the War of Five Kingdoms, Emperor Kazimir the Bold 
> laid siege to the city. After a brutal 2-year siege, the city fell when 
> Prince Durin betrayed his father and opened the gates.
> 
> The last king, Thrain VII, died defending the throne room - his axe 
> still lies somewhere in these ruins.
> 
> The betrayer-prince Durin fled and founded New Khaz-Durim to the north, 
> but his line is still cursed to this day."

# Every detail above emerged from simulation:
# - Thorin Ironforge was a real generated historical figure
# - The War of Five Kingdoms was a real simulated conflict
# - Prince Durin's betrayal was a real succession crisis event
# - Thrain VII's death was a real battle outcome
# - The axe is a real legendary artifact with provenance
# - New Khaz-Durim exists and NPCs there remember the betrayal
```

### Quest Generation from Historical Events

**Example: Ancestral Weapon Recovery**
```python
# NPC quest emerges naturally from genealogy + history
npc = NPC("Grimli Ironforge")  # Generated as descendant of Thorin

npc.generate_quest()
> "My ancestor, King Thrain VII, wielded the legendary Axe of Ancestors.
> It was lost when Khaz-Durim fell 300 years ago. The ruins are dangerous,
> but if you recover it, I'll pay handsomely. It belongs in Ironforge hands."

# This quest exists because:
# 1. Thrain VII was a real historical figure (genealogy system)
# 2. He died in the throne room (battle simulation result)
# 3. The axe was his legendary weapon (artifact generation)
# 4. Grimli is his descendant (genealogy tracking)
# 5. Khaz-Durim's fall was a real historical event
# 6. The Ironforge clan has legitimate claim (cultural system)

# Player can verify ALL of this through in-game historical research
```

### NPC Motivations from Real History

**Example: Faction Relationships**
```python
# NPCs have real motivations based on historical events
dwarf_npc = NPC("Balin Ironforge")  # Descendant of betrayed king
human_npc = NPC("Marcus Kazimir")   # Descendant of conquering emperor

# Their relationship is determined by real history
if player.introduce(dwarf_npc, human_npc):
    > "Balin's eyes narrow as he hears the name Kazimir."
    > "'Your ancestor destroyed my people's greatest city. The debt 
    >  of blood remains unpaid after three centuries.'"
    
    # This hostility is REAL - based on actual simulated events
    # Not randomly generated or scripted
```

---

## Data Architecture

### Core Environmental Data Structures

**Geographic World Container:**
```python
@dataclass
class GeographicWorld:
    seed: int
    size: tuple[int, int]
    
    # Static geography (generated once)
    heightmap: np.ndarray
    geology: dict[HexCoords, GeologyData]
    hydrology: dict[HexCoords, WaterSources]
    
    # Climate data (seasonal patterns)
    climate_zones: dict[HexCoords, ClimateZone]
    seasonal_patterns: dict[HexCoords, SeasonalData]
    
    # Dynamic environmental state
    current_weather: dict[HexCoords, WeatherState]
    seasonal_conditions: dict[HexCoords, str]  # "snow_covered", "flooded", etc.
    
    # Resource availability (changes seasonally)
    resource_availability: dict[HexCoords, ResourceData]

@dataclass
class Hex:
    """Complete hex data for environmental simulation"""
    coords: HexCoords
    
    # Terrain (static)
    elevation: int  # feet above sea level
    terrain_type: str  # "mountains", "forest", "plains", "swamp"
    biome: str  # "temperate_forest", "alpine", etc.
    geology: GeologyType  # affects shelter, resources, hazards
    
    # Climate (seasonal patterns)
    climate_zone: ClimateZone
    average_temp_summer: float
    average_temp_winter: float
    annual_rainfall: int
    
    # Hydrology
    water_sources: list[WaterSource]
    drainage: DrainageType  # affects flooding, mud
    
    # Resources (seasonal variation)
    forageable_food: int  # 0-100 base abundance
    game_animals: int  # 0-100 hunting opportunities  
    firewood: int  # 0-100 availability
    natural_shelter: int  # 0-100 (caves, overhangs)
    
    # Hazards
    natural_hazards: list[str]  # ["avalanche_risk", "flooding"]
    predator_density: int  # 0-100
    
    # Travel mechanics
    base_travel_time: int  # minutes to cross
    terrain_difficulty: float  # 1.0 (easy) to 5.0 (extreme)
    
    # Current state (updates with weather/season)
    current_weather: WeatherState
    seasonal_modifier: float  # affects travel time
    current_conditions: list[str]  # ["muddy", "frozen", "flooded"]
```

### Environmental Query System

**Player Environmental Commands:**
```python
class EnvironmentalInterface:
    """Handle player environmental interactions"""
    
    def examine_weather(self, location: HexCoords) -> WeatherReport:
        """Detailed weather information"""
        weather = self.weather_system.get_current_weather(location)
        
        return WeatherReport(
            current_conditions=weather.get_description(),
            temperature_effects=weather.get_temperature_effects(),
            travel_impact=weather.get_travel_modifier(),
            visibility=weather.visibility,
            hazard_warnings=weather.get_hazard_warnings()
        )
    
    def assess_terrain(self, location: HexCoords) -> TerrainAssessment:
        """Analyze terrain for travel and survival"""
        hex_data = self.world.get_hex(location)
        
        return TerrainAssessment(
            terrain_description=hex_data.get_description(),
            travel_difficulty=hex_data.get_travel_challenge(),
            resource_availability=hex_data.get_resource_summary(),
            shelter_options=hex_data.get_shelter_options(),
            water_sources=hex_data.get_water_source_summary(),
            hazards=hex_data.get_hazard_warnings()
        )
    
    def predict_weather(self, player: Player, location: HexCoords) -> WeatherPrediction:
        """Player attempts weather prediction (Survival skill)"""
        return self.weather_system.player_predict_weather(player, location)
    
    def forage_for_resources(self, player: Player, location: HexCoords) -> ForageResult:
        """Attempt to find food, water, or materials"""
        hex_data = self.world.get_hex(location)
        
        # Survival check modified by terrain and season
        dc = 10 + hex_data.forage_difficulty
        roll = player.skill_check("survival")
        
        if roll >= dc:
            resources = hex_data.generate_forage_results(roll - dc)
            return ForageResult(success=True, resources=resources)
        else:
            return ForageResult(success=False, time_wasted=30)
    
    def make_camp(self, party: Party, location: HexCoords) -> CampResult:
        """Establish camp for rest and shelter"""
        hex_data = self.world.get_hex(location)
        weather = self.weather_system.get_current_weather(location)
        
        # Check shelter availability
        shelter_quality = hex_data.get_shelter_quality()
        
        # Calculate rest effectiveness
        rest_modifier = self._calculate_rest_modifier(shelter_quality, weather)
        
        return CampResult(
            shelter_description=hex_data.get_shelter_description(),
            rest_effectiveness=rest_modifier,
            resource_consumption=self._calculate_camp_costs(party, weather),
            safety_level=hex_data.get_safety_level()
        )
```

---

## Performance & Optimization

### Spatial Indexing

**Efficient Entity Queries:**
- Quadtree/R-tree indexing for spatial queries
- Event indexing by year, location, and participants
- Figure relationship graphs for genealogy queries
- Artifact ownership chains with efficient traversal

### Memory Management

**Large Dataset Handling:**
- Lazy loading of historical events (load on demand)
- Compression of historical data (similar events, common patterns)
- Level-of-detail system (distant/ancient events simplified)
- Efficient serialization for save/load operations

### Environmental Performance Targets

**Generation Benchmarks:**
- Geographic generation: <3 minutes for 100x100 hex world
- Climate simulation: <2 minutes for seasonal patterns
- Weather system initialization: <30 seconds
- Real-time weather updates: <10ms per hex
- Environmental queries: <5ms for player commands

**Memory Optimization:**
- Geographic data: <500MB for complete world
- Weather system: <100MB for forecast data
- Resource tracking: <50MB for seasonal variations
- Total environmental system: <1GB memory footprint

---

## Integration with Game Systems

### Travel & Exploration

**Environmental Travel Mechanics:**
- Weather affects movement speed, visibility, and safety
- Terrain creates navigation challenges and route planning decisions
- Seasonal changes alter available paths and resource availability
- Survival needs drive strategic resource management

### Combat Integration

**Environmental Combat Factors:**
- Weather affects visibility and spell effectiveness
- Terrain provides cover, elevation advantages, and movement restrictions
- Temperature extremes cause ongoing damage during combat
- Environmental hazards create additional tactical considerations

### Resource Management

**Survival Resource Systems:**
- Food and water consumption varies with activity and environment
- Shelter requirements change with weather and season
- Equipment degradation from environmental exposure
- Seasonal availability of forageable resources and hunting opportunities

---

## Success Criteria

### Emergent Storytelling Verification

**Quality Benchmarks:**
- Every major location has discoverable historical context
- NPCs can generate quests from real historical events  
- Player can research complete provenance of any artifact
- Historical events create logical cause-and-effect chains
- Faction relationships reflect genuine historical interactions

### Technical Performance

**Performance Targets:**
- World generation completes in <10 minutes
- Historical database supports complex queries in <100ms
- Save/load preserves complete world state in <5 seconds
- Memory usage remains stable during extended exploration
- Spatial queries scale efficiently with world size

### Environmental Content Requirements

**Geographic Diversity:**
- 6-8 distinct biomes with unique environmental challenges
- 100x100 hex world with realistic terrain variation
- Comprehensive weather system with 7-day forecasting
- Seasonal changes affecting travel and resource availability
- Natural hazards creating meaningful risk/reward decisions

**Environmental Depth Success Criteria:**
- Every hex crossing involves real environmental assessment
- Weather prediction rewards survival skill investment
- Seasonal changes create dynamic world exploration
- Resource management drives strategic decision-making
- Environmental hazards create memorable gameplay moments

**Text RPG Integration:**
- Environmental descriptions enhance immersion through detailed text
- Weather and terrain information presented clearly in travel assessments
- Survival mechanics create tension without overwhelming complexity
- Environmental challenges scale appropriately with character progression

This design ensures that environmental simulation serves the text RPG experience by creating meaningful travel decisions, resource management challenges, and immersive world exploration through rich environmental storytelling.