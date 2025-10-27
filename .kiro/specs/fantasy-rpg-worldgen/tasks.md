# Fantasy RPG - World System Integration

## Overview

**INTEGRATION FOCUS:** All world generation systems are already implemented. This spec focuses on **connecting existing world systems to the GameEngine** and ensuring they work together for the Ultimate Fantasy Sim gameplay experience.

**Philosophy:** Two-layer world structure - deadly overworld hex travel + detailed location exploration. Make existing systems work together seamlessly.

**Estimated Time:** 2-3 days (integration work)  
**Dependencies:** fantasy-rpg-foundation (GameEngine coordinator)  
**Deliverable:** Integrated world system providing deadly overworld travel and rich location exploration

---

## Integration Tasks (Days 1-3)

### **Day 1: World System Integration**
**Goal:** Connect existing world generation to GameEngine

**Morning Tasks:**
- [x] **EXISTING SYSTEMS AUDIT:** Verify WorldCoordinator, climate, biomes, weather all work
- [ ] **GameEngine Integration:** Connect world generation to GameEngine.new_game()
- [ ] **World Initialization:** Ensure world generates automatically on character creation
- [ ] **Hex Data Access:** Implement GameEngine.get_hex_data() for UI display

**Afternoon Tasks:**
- [ ] **Natural Language Output:** Convert precise weather data to natural descriptions
- [ ] **Environmental Effects:** Connect weather/terrain to survival stat changes
- [ ] **Biome Descriptions:** Generate immersive hex descriptions from biome data
- [ ] **Testing:** Verify world generates and displays properly

**Checkpoint:** GameEngine creates world and provides natural language hex descriptions
**Success Criteria:** Moving between hexes shows different biomes, weather, terrain

### **Day 2: Environmental Effects Integration**
**Goal:** Make overworld travel deadly through environmental exposure

**Morning Tasks:**
- [ ] **Travel Effects:** Apply hunger/thirst/temperature changes during hex movement
- [ ] **Weather Impact:** Connect weather conditions to survival stat drain rates
- [ ] **Terrain Difficulty:** Implement terrain-based travel time and exhaustion
- [ ] **Temperature Exposure:** Apply hypothermia/heat stroke during travel

**Afternoon Tasks:**
- [ ] **Seasonal Effects:** Connect seasonal changes to resource availability
- [ ] **Storm Systems:** Implement dangerous weather that affects travel
- [ ] **Natural Hazards:** Add biome-specific dangers (avalanches, floods, etc.)
- [ ] **Death Conditions:** Implement death from exposure, starvation, dehydration

**Checkpoint:** Overworld travel has real survival consequences
**Success Criteria:** Player can die from exposure if unprepared for travel

### **Day 3: Location-World Integration**
**Goal:** Connect location generation to world system for proper resource distribution

**Morning Tasks:**
- [ ] **Biome-Based Locations:** Generate locations appropriate to hex biome
- [ ] **Resource Distribution:** Ensure locations contain biome-appropriate resources
- [ ] **Seasonal Variation:** Connect seasonal changes to location resource availability
- [ ] **Weather Effects:** Apply current weather to location descriptions

**Afternoon Tasks:**
- [ ] **Location Persistence:** Ensure locations persist and evolve over time
- [ ] **Environmental Consistency:** Match location weather/season to overworld
- [ ] **Resource Depletion:** Implement resource consumption and regeneration
- [ ] **Testing:** Verify complete world-location integration

**Checkpoint:** Locations reflect their hex environment and change over time
**Success Criteria:** Forest hex locations have different resources than desert hex locations

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