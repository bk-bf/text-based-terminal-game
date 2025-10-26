# Fantasy RPG - Technical Design Document

## Overview

The Fantasy RPG system is a **text-based terminal application** that implements a layered architecture with clear separation of concerns, following Domain-Driven Design principles. The system runs entirely in the terminal using Python 3.11+ with Textual for the text-based UI framework, SQLite for persistent storage, and JSON for static content definition. 

**Key Design Principles:**
- **Text-Only Interface**: No graphics, images, or sound - all interaction through terminal text
- **Terminal-Native**: Designed for 80x24 minimum terminal size with keyboard-only input
- **Rich Text Formatting**: Uses colors, borders, and text styling for visual hierarchy
- **Modal Overlays**: Complex interactions use text-based modal screens over the main interface

## Architecture

### System Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION LAYER                                          │
│ (Textual UI - Screens, Panels, Modal Overlays)             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ APPLICATION LAYER                                           │
│ (Game Loop, Command Parser, State Manager)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ DOMAIN LAYER                                                │
│ (Game Logic - Combat, Travel, NPCs, Quests)                │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ INFRASTRUCTURE LAYER                                        │
│ (World Gen, Database, Content Loaders)                     │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
fantasy_rpg/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── src/
│   ├── ui/                   # Presentation Layer (Text-based UI)
│   │   ├── app.py           # Main Textual terminal app
│   │   ├── screens/         # Text-based modal screens
│   │   ├── panels/          # Terminal UI panels
│   │   └── styles.tcss      # Terminal styling (colors, borders)
│   ├── game/                # Application Layer
│   │   ├── state.py         # Game state manager
│   │   ├── commands.py      # Command parser
│   │   └── loop.py          # Main game loop
│   ├── core/                # Domain Layer
│   │   ├── character/       # Character system
│   │   ├── combat/          # Combat system
│   │   ├── world/           # World system
│   │   ├── entities/        # NPCs and factions
│   │   └── items/           # Item system
│   ├── generation/          # Infrastructure Layer
│   │   ├── world_gen.py     # World generation
│   │   ├── location_gen.py  # Location generation
│   │   └── npc_gen.py       # NPC generation
│   ├── data/                # Data access layer
│   │   ├── database.py      # SQLite interface
│   │   └── content_loader.py # JSON content loader
│   └── utils/               # Utilities
├── data/                    # Static content (JSON)
│   ├── biomes/
│   ├── creatures/
│   ├── items/
│   └── classes/
└── saves/                   # Save files (SQLite)
```

## Components and Interfaces

### World Generation System

The world generation uses a two-phase approach for optimal performance:

**Phase 1: Macro Generation (Startup)**
- Generate heightmap using Perlin noise
- Calculate climate zones based on latitude
- Assign biomes using height + climate lookup tables
- Place major landmarks (cities, ruins, dungeons)
- Initialize faction territories and relationships
- Create civilization history and lore

**Phase 2: Local Generation (On-Demand)**
- Generate specific hex details when player enters
- Use seeded RNG for deterministic results
- Context-aware generation based on neighboring hexes
- Populate with appropriate creatures and resources

```python
class WorldGenerator:
    def generate_world(self, seed: int, size: tuple[int, int]) -> World:
        """Generate world framework in <30 seconds"""
        world = World(seed=seed, size=size)
        world.heightmap = self._generate_heightmap(size)
        world.climate = self._generate_climate(size)
        world.biomes = self._assign_biomes(world.heightmap, world.climate)
        world.landmarks = self._place_landmarks(world.biomes)
        world.factions = self._initialize_factions()
        return world

class HexGenerator:
    def generate_hex(self, world: World, coords: tuple[int, int]) -> Hex:
        """Generate specific hex when player enters"""
        hex_seed = hash((world.seed, coords))
        rng = Random(hex_seed)
        biome = world.biomes[coords]
        location = self._roll_location(biome, rng) if coords not in world.landmarks else world.landmarks[coords]
        return Hex(coords=coords, biome=biome, location=location)
```

### Combat System

The combat system implements D&D 5e mechanics with distance-based positioning:

**Combat Flow:**
1. Roll initiative for all combatants
2. Sort by initiative (highest first)
3. Each turn: reset action economy, process effects, get player input or execute AI
4. Resolve actions using D&D 5e rules
5. Check for combat end conditions

**Distance System:**
- ENGAGED (0-5 ft): Melee range
- NEARBY (10-15 ft): 1 action to close
- SHORT (20-40 ft): Ranged weapons effective
- MEDIUM (50-100 ft): Long-range weapons
- LONG (100+ ft): Distant

```python
class CombatEngine:
    def execute_attack(self, action: AttackAction) -> AttackResult:
        """D&D 5e attack resolution"""
        attack_roll = self._roll_d20() + action.actor.attack_bonus(action.weapon)
        
        if attack_roll == 20:
            is_crit = True
        elif attack_roll == 1 or attack_roll < action.target.armor_class:
            return AttackResult(hit=False)
        
        damage = action.weapon.roll_damage(crit=is_crit)
        damage += action.actor.damage_bonus(action.weapon)
        action.target.take_damage(damage)
        
        return AttackResult(hit=True, damage=damage, crit=is_crit)
```

### Character System

Characters use D&D 5e rules with full stat tracking:

```python
@dataclass
class Character:
    # Core D&D stats
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    
    # Derived stats
    hp: int
    max_hp: int
    armor_class: int
    proficiency_bonus: int
    
    # Equipment and inventory
    equipment: Equipment
    inventory: Inventory
    
    def ability_modifier(self, ability: str) -> int:
        """Calculate ability modifier"""
        score = getattr(self, ability)
        return (score - 10) // 2
    
    def skill_check(self, skill: str) -> int:
        """Roll skill check with proficiency"""
        base_ability = SKILL_ABILITIES[skill]
        mod = self.ability_modifier(base_ability)
        if self.skills.get(skill, 0) > 0:
            mod += self.proficiency_bonus
        return roll_d20() + mod
```

### NPC and Faction System

NPCs are generated from archetypes with personality traits and faction affiliations:

```python
class NPC:
    def __init__(self, template: NPCArchetype):
        self.name = generate_name(template.race)
        self.archetype = template
        self.personality = {
            'primary': random.choice(template.primary_traits),
            'secondary': random.choice(template.secondary_traits)
        }
        self.faction = None
        self.relationship = 0  # -100 to +100
    
    def generate_dialogue(self, topic: str) -> str:
        """Generate contextual dialogue based on relationship"""
        template = self.archetype.dialogue_templates[topic]
        if self.relationship < -20:
            template = self._add_hostile_tone(template)
        elif self.relationship > 20:
            template = self._add_friendly_tone(template)
        return template.format(player_name=PLAYER.name, npc_name=self.name)

class Faction:
    def daily_action(self, world: World):
        """Faction takes action to pursue goals"""
        goal = self._select_goal()
        action = self._plan_action(goal, world)
        result = action.execute(world)
        self._apply_result(result, world)
```

## Data Models

### World Data Structure

```python
@dataclass
class World:
    seed: int
    size: tuple[int, int]
    heightmap: np.ndarray
    climate: np.ndarray
    biomes: dict[tuple[int, int], str]
    landmarks: dict[tuple[int, int], Landmark]
    factions: list[Faction]
    current_day: int = 0

@dataclass
class Hex:
    coords: tuple[int, int]
    biome: str
    elevation: int
    location: Optional[Location]
    features: list[Feature]
    explored: bool = False

@dataclass
class Location:
    name: str
    type: str
    rooms: list[Room]
    connections: dict[int, list[int]]
    enemies: list[Monster]
    loot: dict[int, list[Item]]
```

### Database Schema

**SQLite Tables:**
- `game_metadata`: Save slot info, timestamps
- `world_state`: World seed, day, faction states
- `player_character`: Stats, inventory, position
- `explored_hexes`: Generated hex data
- `npc_instances`: NPC states and relationships
- `quest_progress`: Active and completed quests

**JSON Content Files:**
- `data/biomes/`: Terrain types, encounter tables
- `data/creatures/`: Monster stats and behaviors
- `data/items/`: Equipment and consumables
- `data/classes/`: Character class definitions
- `data/locations/`: Location templates

## Error Handling

### Graceful Degradation
- Invalid commands show helpful error messages
- Corrupted save files trigger backup restoration
- Missing content files use default templates
- Network issues (future) fall back to offline mode

### Recovery Mechanisms
- Automatic backup saves every 10 minutes
- Save file integrity checks on load
- Content validation on startup
- Memory leak detection in debug mode

## Testing Strategy

### Unit Tests
- Character stat calculations and D&D mechanics
- Combat resolution and damage calculations
- Procedural generation reproducibility
- Command parsing and validation
- Save/load data integrity

### Integration Tests
- Complete combat encounters from start to finish
- Hex exploration and location generation flow
- NPC dialogue and faction reputation changes
- Quest completion and reward distribution
- Full character creation and progression

### Performance Tests
- World generation within 30-second limit
- Command response time under 100ms
- Memory usage during extended play sessions
- Save file size optimization
- Hex generation speed benchmarks

### Playtesting Goals
- 2-hour play session without crashes
- Generate and explore 100+ hexes successfully
- Complete at least one quest end-to-end
- Test all combat scenarios and edge cases
- Verify faction simulation over multiple game days