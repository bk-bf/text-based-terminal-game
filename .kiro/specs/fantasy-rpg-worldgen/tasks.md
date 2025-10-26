# Fantasy RPG - Geographic & Environmental Simulation

## Overview

This spec implements a comprehensive geographic and environmental simulation system for text-based RPG gameplay, focusing on realistic terrain, weather systems, and survival mechanics that make travel meaningful and challenging.

**Philosophy:** CDDA-level environmental depth adapted for text RPG. Every hex crossing should involve real risk assessment and resource management.

**Estimated Time:** 3-4 days (based on demonstrated pace)  
**Dependencies:** fantasy-rpg-foundation (character system, UI)  
**Deliverable:** Complete environmental simulation with weather, terrain, and survival systems

---

## Milestone 1.1: Geographic Foundation (Day 1)

### **1.1.1: Terrain Generation (Morning)**
- [x] Implement multi-octave Perlin/Simplex noise for realistic terrain
- [x] Generate heightmap with continental plates simulation
- [x] Calculate drainage patterns (water flow from high to low)
- [x] Generate river systems following realistic drainage
- [x] Place lakes in drainage basins and natural depressions
- **Checkpoint:** Realistic geography with logical water systems

### **1.1.2: Climate & Biome System (Afternoon)**
- [ ] Implement latitude-based temperature gradients
- [ ] Add elevation-based temperature modification (lapse rate)
- [ ] Simulate rainfall patterns (prevailing winds, rain shadows)
- [ ] Create biome assignment from temperature + rainfall matrix
- [ ] Generate 6-8 biomes with distinct environmental properties
- [ ] Assign resource distribution and natural hazards per biome
- **Checkpoint:** Biomes distributed realistically with gameplay impact

---

## Milestone 1.2: Weather & Climate Systems (Day 2)

### **1.2.1: Weather Simulation Engine (Morning)**
- [ ] Implement WeatherState dataclass with complete weather data
- [ ] Create seasonal weather pattern generation
- [ ] Build weather transition system (realistic weather changes)
- [ ] Implement storm systems and extreme weather events
- [ ] Add magical weather disruption system
- **Checkpoint:** Dynamic weather system generating realistic patterns

### **1.2.2: Weather Prediction & Forecasting (Afternoon)**
- [ ] Implement 7-day weather forecasting system
- [ ] Create player weather prediction mechanics (Survival skill checks)
- [ ] Build weather impact calculation (travel speed, visibility, hazards)
- [ ] Add seasonal weather pattern variations
- [ ] Implement weather-based travel modifiers
- **Checkpoint:** Complete weather system with player prediction mechanics

---

## Milestone 1.3: Survival & Environmental Systems (Day 3)

### **1.3.1: Player Survival Mechanics (Morning)**
- [ ] Implement PlayerState with CDDA-style survival tracking
- [ ] Create hunger, thirst, and temperature regulation systems
- [ ] Build environmental exposure mechanics (wetness, wind chill)
- [ ] Implement survival condition system (hypothermia, dehydration, etc.)
- [ ] Add environmental damage and status effect calculations
- **Checkpoint:** Complete survival mechanics affecting player stats

### **1.3.2: Resource & Shelter Systems (Afternoon)**
- [ ] Implement resource availability per hex (food, water, firewood)
- [ ] Create foraging mechanics with skill-based success
- [ ] Build shelter system (natural shelter, camping, protection)
- [ ] Add seasonal resource variation
- [ ] Implement resource consumption during travel and rest
- **Checkpoint:** Resource management system integrated with survival

---

## Milestone 1.4: Travel & Navigation Systems (Day 4)

### **1.4.1: Travel Assessment Engine (Morning)**
- [ ] Implement comprehensive travel assessment system
- [ ] Create travel risk calculation (weather, terrain, party status)
- [ ] Build travel time estimation with environmental modifiers
- [ ] Add travel decision interface with detailed information display
- [ ] Implement travel option system (proceed, camp, wait, predict weather)
- **Checkpoint:** Complete travel assessment and decision system

### **1.4.2: Environmental Interaction Commands (Afternoon)**
- [ ] Create environmental query system (examine weather, assess terrain)
- [ ] Implement camping mechanics with shelter quality assessment
- [ ] Build foraging command system with skill checks
- [ ] Add weather prediction command interface
- [ ] Create environmental hazard warning system
- **Checkpoint:** Full environmental interaction system for text RPG

---

## Milestone 1.5: Integration & Optimization (Day 4-5)

### **1.5.1: Real-Time Environmental Updates (Morning)**
- [ ] Implement continuous environmental simulation during gameplay
- [ ] Create seasonal transition system affecting terrain and resources
- [ ] Build weather progression system with realistic changes
- [ ] Add environmental hazard monitoring and warnings
- [ ] Implement resource regeneration and seasonal availability
- **Checkpoint:** Dynamic environmental changes during gameplay

### **1.5.2: Performance & Save System (Afternoon)**
- [ ] Optimize environmental data structures for memory efficiency
- [ ] Implement spatial indexing for fast hex queries
- [ ] Create efficient weather system updates
- [ ] Design save/load system for environmental state
- [ ] Add performance monitoring and optimization
- **Checkpoint:** Environmental system runs efficiently with save/load

---

## Environmental Data Architecture

### Core Environmental Data Structures

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

@dataclass
class PlayerState:
    """CDDA-style survival tracking"""
    
    # Core D&D stats
    hp: int
    stamina: int
    
    # Survival needs (0-100 scale)
    hunger: int  # 0 (starving) to 100 (full)
    thirst: int  # 0 (dying of thirst) to 100 (hydrated)
    
    # Temperature regulation
    body_temperature: float  # 98.6°F normal
    warmth: int  # From clothing/shelter, 0-100
    
    # Environmental exposure
    wetness: int  # 0 (dry) to 100 (soaked)
    exposure_time: int  # Minutes exposed to harsh conditions
    
    # Status effects
    conditions: list[Condition]  # Hypothermia, Heatstroke, etc.
    
    # Carried resources
    carried_food: int  # Days of rations
    carried_water: int  # Days of water
    firewood: int  # Hours of warmth

@dataclass
class Hex:
    """Complete environmental hex data"""
    coords: HexCoords
    
    # Terrain (static)
    elevation: int  # feet above sea level
    terrain_type: str  # "mountains", "forest", "plains", "swamp"
    biome: str  # "temperate_forest", "alpine", etc.
    
    # Climate
    climate_zone: ClimateZone
    average_temp_summer: float
    average_temp_winter: float
    annual_rainfall: int
    
    # Resources (seasonal variation)
    forageable_food: int  # 0-100 base abundance
    game_animals: int  # 0-100 hunting opportunities
    firewood: int  # 0-100 availability
    natural_shelter: int  # 0-100 (caves, overhangs)
    water_sources: list[WaterSource]
    
    # Hazards & Travel
    natural_hazards: list[str]  # ["avalanche_risk", "flooding"]
    base_travel_time: int  # minutes to cross
    terrain_difficulty: float  # 1.0 (easy) to 5.0 (extreme)
    
    # Current state (updates with weather/season)
    current_weather: WeatherState
    seasonal_conditions: list[str]  # ["muddy", "frozen", "flooded"]

@dataclass
class GeographicWorld:
    """Environmental world container"""
    seed: int
    size: tuple[int, int]
    
    # Static geography
    heightmap: np.ndarray
    climate_zones: dict[HexCoords, ClimateZone]
    hexes: dict[HexCoords, Hex]
    
    # Dynamic systems
    weather_system: WeatherSystem
    seasonal_tracker: SeasonalTracker
    environmental_engine: EnvironmentalEngine
```

### Query System for Discovery

```python
class HistoryDatabase:
    """Player can research history in-game"""
    
    def research_location(self, coords: HexCoords) -> HistoricalSummary:
        """What happened here?"""
        events = [e for e in self.events if e.location == coords]
        return self._summarize_events(events)
    
    def research_figure(self, figure_id: int) -> Biography:
        """Who was this person?"""
        figure = self.figures[figure_id]
        events = [e for e in self.events if figure_id in e.primary_actors]
        return Biography(figure, events)
    
    def research_artifact(self, artifact_id: int) -> ArtifactHistory:
        """Where did this come from?"""
        artifact = self.artifacts[artifact_id]
        creation_event = self.events[artifact.created_in_event]
        owners = self._trace_ownership(artifact)
        return ArtifactHistory(artifact, creation_event, owners)
    
    def research_civilization(self, civ_id: str) -> CivilizationHistory:
        """What happened to this empire?"""
        civ = self.civilizations[civ_id]
        major_events = [e for e in self.events if e.significance >= 7
                        and any(fig in civ.rulers.values()
                               for fig in e.primary_actors)]
        return self._build_timeline(civ, major_events)
```

---

## Environmental Gameplay Examples

### Travel Decision Making
```python
# Player attempts to travel in harsh weather:
player.command("travel north")

> ╔══════════════════════════════════════════════════════════╗
> ║ TRAVEL ASSESSMENT: To Darkwood Forest                   ║
> ╠══════════════════════════════════════════════════════════╣
> ║ TERRAIN: Dense forest with muddy trails                 ║
> ║ DISTANCE: 3.2 miles                                     ║
> ║ ESTIMATED TIME: 2 hours 15 minutes                      ║
> ║                                                          ║
> ║ CURRENT WEATHER: Heavy rain with strong winds           ║
> ║ Temperature: 38°F (feels like 29°F)                     ║
> ║ Visibility: 200 feet                                    ║
> ║ Wind: 25 mph from the northwest                         ║
> ║                                                          ║
> ║ RISKS:                                                   ║
> ║ • Hypothermia risk due to cold rain                     ║
> ║ • Navigation difficulty (DC 15) due to poor visibility  ║
> ║ • Muddy terrain doubles travel time                     ║
> ║ • High chance of getting lost                           ║
> ║                                                          ║
> ║ PARTY STATUS:                                            ║
> ║ Food: 3.2 days    Water: 1.8 days                      ║
> ║ Warmth: 45/100    Fatigue: 60%                         ║
> ║                                                          ║
> ║ SURVIVAL CHECK (DC 18): Your Survival: +6               ║
> ║ Estimated Success: 45%                                   ║
> ╚══════════════════════════════════════════════════════════╝
> 
> OPTIONS:
> [1] Proceed with travel (risk hypothermia, may get lost)
> [2] Make camp and wait out storm (use 1 day food/water)
> [3] Try to predict when weather will improve (Survival check)
> [4] Turn back to previous location
```

### Environmental Survival
```python
# Player deals with environmental challenges:
player.command("predict weather")
> You study the wind patterns and cloud formations...
> [Rolling Survival check: 1d20+6 = 18 vs DC 15]
> 
> "The storm should pass by tomorrow afternoon. The wind is shifting 
> from the northwest to the west - that usually means clearing skies 
> within 18-24 hours. You're confident in this prediction."
> 
> FORECAST (Confidence: High):
> • Tonight: Heavy rain continues, temperature drops to 35°F
> • Tomorrow morning: Rain lightens, winds decrease
> • Tomorrow afternoon: Clearing skies, temperature rises to 45°F
> • Tomorrow evening: Clear and cold, good travel conditions

player.command("make camp")
> You search for shelter in the forest...
> [Rolling Survival check: 1d20+6 = 14 vs DC 12]
> 
> "You find a large oak tree with dense canopy and thick undergrowth 
> that provides good protection from wind and rain. There's enough 
> dry wood nearby for a small fire."
> 
> CAMP QUALITY: Good (75% rest effectiveness)
> RESOURCE COST: 1 day food, 1 day water, 2 hours firewood
> SAFETY: Moderate (forest predators possible)
> 
> You settle in for the night, staying warm and dry...
```

---

## Implementation Pattern

```python
class WorldSimulator:
    def generate_world(self, seed: int) -> World:
        """Full DF-style worldgen"""
        
        print("Generating geography...")
        world = self._generate_geography(seed)
        
        print("Founding civilizations...")
        self._found_civilizations(world)
        
        print("Simulating history...")
        for year in range(world.start_year, world.start_year + 500):
            if year % 10 == 0:
                print(f"  Simulating year {year}...")
            
            self._simulate_year(world, year)
        
        print("Finalizing world state...")
        self._finalize_world(world)
        
        print(f"World generation complete!")
        print(f"  {len(world.civilizations)} civilizations")
        print(f"  {len(world.historical_figures)} historical figures")
        print(f"  {len(world.historical_events)} events")
        print(f"  {len(world.artifacts)} legendary artifacts")
        
        return world
    
    def _simulate_year(self, world: World, year: int):
        """One year of history"""
        # Aging and death
        self._age_figures(world, year)
        
        # Births and succession
        self._handle_births(world, year)
        self._handle_successions(world, year)
        
        # Major events (wars, disasters, etc.)
        events = self._generate_events(world, year)
        for event in events:
            self._resolve_event(world, event)
        
        # Population and economy
        self._update_populations(world, year)
        self._simulate_economy(world, year)
```

---

## Success Criteria

### **Environmental System Complete When:**
- [ ] Realistic geography with proper drainage, climate, and biomes
- [ ] Dynamic weather system with 7-day forecasting capability
- [ ] Complete survival mechanics (hunger, thirst, temperature, exposure)
- [ ] Comprehensive travel assessment and decision system
- [ ] Resource management with seasonal availability variations
- [ ] Environmental hazards and natural disaster simulation
- [ ] Player environmental interaction commands (weather, terrain, camping)

### **Quality Benchmarks:**
- [ ] Geographic generation completes in <3 minutes
- [ ] Weather updates process in <10ms per hex
- [ ] Environmental queries respond in <5ms
- [ ] Travel assessments provide clear risk/reward information
- [ ] Survival mechanics create meaningful resource management
- [ ] Seasonal changes affect gameplay strategy

### **Environmental Depth Verification:**
- [ ] Every hex crossing involves real environmental assessment
- [ ] Weather prediction rewards survival skill investment
- [ ] Seasonal changes create dynamic exploration challenges
- [ ] Resource scarcity drives strategic decision-making
- [ ] Environmental hazards create memorable survival moments
- [ ] Travel planning becomes essential for long journeys

---

## Data Pipeline

```
World Generation
    ↓
Historical Simulation (500 years)
    ↓
Generated: Events, Figures, Civilizations, Artifacts
    ↓
Save to Database (complete history)
    ↓
Player Exploration (discovers pre-existing history)
    ↓
Quest Generation (from real history)
    ↓
NPC Dialogue (references real events)
```

This architecture ensures that every piece of content the player encounters has genuine historical depth and can be researched, creating the emergent storytelling depth of Dwarf Fortress within a playable RPG framework.