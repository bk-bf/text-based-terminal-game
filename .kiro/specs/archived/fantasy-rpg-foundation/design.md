# Fantasy RPG Foundation - Technical Design Document

## Overview

The Foundation layer establishes the core infrastructure for the Fantasy RPG system, focusing on character management, world generation framework, and the terminal-based user interface. This layer provides the essential building blocks that all other systems will depend on.

## User Interface Design

### Main Layout (Three-Panel)

```
┌────────────────────────────────────────────────────────────────┐
│ Fantasy RPG - Turn 1847, Day 5                                │
├─────────────────┬──────────────────────────────┬───────────────┤
│ CHARACTER (25%) │ GAME LOG (50%)               │ POIs (25%)    │
│                 │                              │               │
│ Name: Aldric    │ > move north                 │ 📍 Ruins (NE) │
│ Level: 3        │                              │ 2 hexes       │
│ HP: 32/45 ████▓ │ You travel through forest... │               │
│ Stamina: 60/80  │ Time passes: 30 min          │ 🏰 Village (S)│
│ AC: 18          │                              │ 1 hex         │
│                 │ [Perception: 16]             │               │
│ 🌤 Weather:     │ You spot wolf tracks...      │ 🗻 Cave (W)   │
│ Clear, 68°F     │                              │ This hex      │
│                 │                              │               │
│ 📍 Hex 0847     │ ▼ Scroll for more            │ [I] Inventory │
│ Forest          │                              │ [C] Character │
│ Elev: 320 ft    │                              │ [M] Map       │
├─────────────────┴──────────────────────────────┴───────────────┤
│ > _                                                            │
└────────────────────────────────────────────────────────────────┘
```

### Panel Architecture

**Character Panel (Left - 25%):**
- Real-time character stats (HP, stamina, AC)
- Current location and weather
- Active conditions/effects
- Quick status indicators

**Game Log Panel (Center - 50%):**
- Scrollable message history
- Timestamped entries
- Color-coded message types (actions, discoveries, combat)
- Only narrative events (no UI interactions)

**POI Panel (Right - 25%):**
- Nearby locations and distances
- Quick reference commands
- Navigation shortcuts
- Context-sensitive help

### Modal Overlay System

All detailed interfaces open as modal overlays that don't clutter the game log:

**Inventory Screen:**
- Opens with 'I' key
- Displays equipped items + carried inventory
- Shows weight and encumbrance
- Actions: Use, Drop, Examine
- ESC to close

**Combat Screen:**
- Opens automatically when combat starts
- Shows enemy list with HP/distance
- Shows available actions based on distance
- Separate combat log (doesn't spam main log)
- Returns to exploration when combat ends

**Character Sheet:**
- Opens with 'C' key
- Full stats, skills, abilities display
- XP progress bar
- Conditions and effects
- ESC to close

**Map Screen:**
- Opens with 'M' key
- ASCII representation of explored hexes
- Player position marker
- Landmarks and POIs marked
- Distance indicators

### Implementation Architecture

```python
from textual.app import App
from textual.screen import Screen

class InventoryScreen(Screen):
    """Modal overlay - doesn't affect game log"""
    BINDINGS = [("escape", "dismiss", "Close")]
    
    def compose(self):
        # ... inventory UI ...
    
    def on_button_pressed(self, event):
        if event.button.id == "close":
            self.dismiss()  # Returns to main screen

class MainGame(App):
    BINDINGS = [
        ("i", "toggle_inventory", "Inventory"),
        ("c", "toggle_character", "Character"),
        ("m", "toggle_map", "Map"),
    ]
    
    def action_toggle_inventory(self):
        # Open as modal - main UI stays underneath
        self.push_screen(InventoryScreen())
```

**Key Principle:** UI interactions don't create log entries. Only narrative events (moving, fighting, discovering) appear in game log.

## Character System Architecture

### D&D 5e Implementation

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
    level: int
    hp: int
    max_hp: int
    armor_class: int
    proficiency_bonus: int
    
    # Progression
    experience_points: int
    
    def ability_modifier(self, ability: str) -> int:
        """Calculate D&D ability modifier"""
        score = getattr(self, ability)
        return (score - 10) // 2
    
    def calculate_ac(self) -> int:
        """Calculate armor class from equipment"""
        base_ac = 10 + self.ability_modifier('dexterity')
        armor_bonus = self.equipment.get_armor_bonus()
        return base_ac + armor_bonus
    
    def level_up(self):
        """Handle level advancement"""
        self.level += 1
        self.proficiency_bonus = 2 + ((self.level - 1) // 4)
        hp_gain = self.character_class.hit_die + self.ability_modifier('constitution')
        self.max_hp += max(1, hp_gain)
        self.hp = self.max_hp
```

### Equipment System

```python
class Equipment:
    def __init__(self):
        self.slots = {
            'head': None,
            'body': None,
            'hands': None,
            'feet': None,
            'main_hand': None,
            'off_hand': None,
            'ring_1': None,
            'ring_2': None,
            'amulet': None,
        }
    
    def equip(self, item: Item, slot: str) -> bool:
        """Equip item to specific slot"""
        if not item.can_equip_to(slot):
            return False
        
        # Unequip current item
        if self.slots[slot]:
            self.unequip(slot)
        
        self.slots[slot] = item
        item.on_equip()
        return True
    
    def get_armor_bonus(self) -> int:
        """Calculate total AC bonus from equipment"""
        armor = self.slots['body']
        shield = self.slots['off_hand']
        
        ac_bonus = 0
        if armor:
            ac_bonus += armor.ac_bonus
        if shield and shield.is_shield:
            ac_bonus += shield.ac_bonus
        
        return ac_bonus
```

## World Generation Framework

### Two-Phase Generation

**Phase 1: Macro Generation (Startup)**
```python
class WorldGenerator:
    def generate_world(self, seed: int, size: tuple[int, int]) -> World:
        """Generate world framework in <30 seconds"""
        world = World(seed=seed, size=size)
        
        # Generate heightmap using Perlin noise
        world.heightmap = self._generate_heightmap(size)
        
        # Calculate climate zones
        world.climate = self._generate_climate(size)
        
        # Assign biomes
        world.biomes = self._assign_biomes(world.heightmap, world.climate)
        
        # Place major landmarks
        world.landmarks = self._place_landmarks(world.biomes)
        
        # Initialize factions
        world.factions = self._initialize_factions()
        
        return world
```

**Phase 2: Local Generation (On-Demand)**
```python
class HexGenerator:
    def generate_hex(self, world: World, coords: tuple[int, int]) -> Hex:
        """Generate specific hex when player enters"""
        hex_seed = hash((world.seed, coords))
        rng = Random(hex_seed)
        
        biome = world.biomes[coords]
        elevation = world.heightmap[coords]
        
        # Check for pre-placed landmarks
        if coords in world.landmarks:
            location = world.landmarks[coords]
        else:
            location = self._roll_location(biome, rng)
        
        features = self._generate_features(biome, elevation, rng)
        
        return Hex(
            coords=coords,
            biome=biome,
            elevation=elevation,
            location=location,
            features=features
        )
```

## Save System Architecture

### SQLite Schema

```sql
-- Game metadata
CREATE TABLE game_metadata (
    slot_id INTEGER PRIMARY KEY,
    character_name TEXT,
    created_at TIMESTAMP,
    last_played TIMESTAMP,
    play_time_minutes INTEGER
);

-- World state
CREATE TABLE world_state (
    slot_id INTEGER,
    seed INTEGER,
    current_day INTEGER,
    world_size_x INTEGER,
    world_size_y INTEGER,
    FOREIGN KEY (slot_id) REFERENCES game_metadata(slot_id)
);

-- Player character
CREATE TABLE player_character (
    slot_id INTEGER,
    name TEXT,
    race TEXT,
    character_class TEXT,
    level INTEGER,
    experience_points INTEGER,
    strength INTEGER,
    dexterity INTEGER,
    constitution INTEGER,
    intelligence INTEGER,
    wisdom INTEGER,
    charisma INTEGER,
    hp INTEGER,
    max_hp INTEGER,
    position_x INTEGER,
    position_y INTEGER,
    FOREIGN KEY (slot_id) REFERENCES game_metadata(slot_id)
);

-- Explored hexes
CREATE TABLE explored_hexes (
    slot_id INTEGER,
    x INTEGER,
    y INTEGER,
    biome TEXT,
    elevation INTEGER,
    explored_turn INTEGER,
    FOREIGN KEY (slot_id) REFERENCES game_metadata(slot_id)
);
```

### Save/Load Implementation

```python
class SaveSystem:
    def save_game(self, game_state: GameState, slot: int) -> bool:
        """Save complete game state"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Save metadata
            self._save_metadata(conn, game_state, slot)
            
            # Save world state
            self._save_world(conn, game_state.world, slot)
            
            # Save player
            self._save_player(conn, game_state.player, slot)
            
            # Save explored hexes
            self._save_hexes(conn, game_state.explored_hexes, slot)
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Save failed: {e}")
            return False
        finally:
            conn.close()
```

## Content Loading System

### JSON Structure

```json
// data/races/human.json
{
    "name": "Human",
    "ability_bonuses": {
        "strength": 1,
        "dexterity": 1,
        "constitution": 1,
        "intelligence": 1,
        "wisdom": 1,
        "charisma": 1
    },
    "size": "Medium",
    "speed": 30,
    "languages": ["Common"],
    "traits": [
        {
            "name": "Extra Skill",
            "description": "Gain proficiency in one additional skill"
        }
    ]
}

// data/classes/fighter.json
{
    "name": "Fighter",
    "hit_die": 10,
    "primary_ability": "strength",
    "saving_throw_proficiencies": ["strength", "constitution"],
    "skill_proficiencies": {
        "choose": 2,
        "from": ["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"]
    },
    "starting_equipment": [
        {"item": "chain_mail", "quantity": 1},
        {"item": "longsword", "quantity": 1},
        {"item": "shield", "quantity": 1}
    ]
}
```

### Content Loader

```python
class ContentLoader:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._cache = {}
    
    def load_races(self) -> dict[str, Race]:
        """Load all race definitions"""
        if 'races' not in self._cache:
            races = {}
            race_dir = self.data_dir / 'races'
            for file_path in race_dir.glob('*.json'):
                with open(file_path) as f:
                    data = json.load(f)
                    races[data['name']] = Race.from_dict(data)
            self._cache['races'] = races
        return self._cache['races']
    
    def load_classes(self) -> dict[str, CharacterClass]:
        """Load all class definitions"""
        if 'classes' not in self._cache:
            classes = {}
            class_dir = self.data_dir / 'classes'
            for file_path in class_dir.glob('*.json'):
                with open(file_path) as f:
                    data = json.load(f)
                    classes[data['name']] = CharacterClass.from_dict(data)
            self._cache['classes'] = classes
        return self._cache['classes']
```

## Performance Considerations

### Optimization Targets
- Character creation: <1 second
- World generation: <30 seconds
- Hex generation: <100ms
- Save/load: <2 seconds
- UI response: <100ms

### Memory Management
- Lazy loading of hex data
- Content caching with LRU eviction
- Efficient SQLite queries with proper indexing
- Minimal object creation in hot paths

## Error Handling

### Graceful Degradation
- Invalid save files trigger backup restoration
- Missing content files use default templates
- Corrupted character data shows error and offers new character creation
- Database connection failures offer manual save export

### Recovery Mechanisms
- Automatic backup saves every 10 minutes
- Save file integrity checks on load
- Content validation on startup
- Memory leak detection in debug mode