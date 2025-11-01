"""
Fantasy RPG - JSON-Based Location Generator

Generates locations from JSON templates using CDDA-style data-driven approach.
Hex types map to location categories, which contain weighted location templates.
"""

import json
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import os

# Configuration constants
MIN_OBJECTS_PER_LOCATION = 10  # Minimum number of objects to spawn per location
MAX_OBJECTS_PER_LOCATION = 10  # Maximum number of objects to spawn per location


class LocationType(Enum):
    """Types of locations"""
    WILDERNESS = "wilderness"
    SETTLEMENT = "settlement"
    RUINS = "ruins"
    STRUCTURE = "structure"
    CAVE = "cave"


class AreaSize(Enum):
    """Size categories for areas"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VAST = "vast"


class TerrainType(Enum):
    """Terrain types affecting movement and combat"""
    OPEN = "open"
    CLUTTERED = "cluttered"
    DIFFICULT = "difficult"
    HAZARDOUS = "hazardous"


@dataclass
class GameObject:
    """Object within an area (furniture, features, etc.)"""
    id: str
    name: str
    shortkey: str = ""  # Permanent shortkey from JSON
    description: str = ""
    interactive: bool = True
    properties: Dict[str, Any] = field(default_factory=dict)
    item_drops: List['GameItem'] = field(default_factory=list)


@dataclass
class GameItem:
    """Item that can be picked up"""
    id: str
    name: str
    description: str = ""
    value: int = 0
    weight: float = 0.0


@dataclass
class GameEntity:
    """NPC or creature"""
    id: str
    name: str
    description: str = ""
    hostile: bool = False
    stats: Dict[str, int] = field(default_factory=dict)
    item_drops: List['GameItem'] = field(default_factory=list)


@dataclass
class Area:
    """Single area within a location"""
    id: str
    name: str
    description: str
    size: AreaSize
    terrain: TerrainType
    exits: Dict[str, str] = field(default_factory=dict)  # direction -> area_id
    objects: List[GameObject] = field(default_factory=list)
    items: List[GameItem] = field(default_factory=list)
    entities: List[GameEntity] = field(default_factory=list)
    
    def get_full_description(self) -> str:
        """Get complete description including contents"""
        desc = [self.description]
        
        if self.exits:
            exit_list = [direction.capitalize() for direction in self.exits.keys()]
            desc.append(f"Exits: {', '.join(exit_list)}")
        
        if self.objects:
            obj_list = [obj.name for obj in self.objects]
            desc.append(f"Objects: {', '.join(obj_list)}")
        
        if self.items:
            item_list = [item.name for item in self.items]
            desc.append(f"Items: {', '.join(item_list)}")
        
        if self.entities:
            entity_list = [entity.name for entity in self.entities]
            desc.append(f"Entities: {', '.join(entity_list)}")
        
        return "\n".join(desc)


@dataclass
class Location:
    """Complete location with multiple areas"""
    id: str
    name: str
    type: LocationType
    areas: Dict[str, Area] = field(default_factory=dict)
    starting_area: str = "entrance"
    exit_flag: bool = False  # Can player exit to hex overworld from here?
    # Additional location properties from templates
    size: str = "medium"
    terrain: str = "open"
    # Shelter flags for environmental condition system
    provides_some_shelter: bool = False
    provides_good_shelter: bool = False
    provides_excellent_shelter: bool = False
    
    def get_area(self, area_id: str) -> Optional[Area]:
        """Get area by ID"""
        return self.areas.get(area_id)
    
    def get_starting_area(self) -> Optional[Area]:
        """Get the starting area"""
        return self.areas.get(self.starting_area)


class LocationGenerator:
    """Generates locations from JSON templates"""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(1, 1000000)
        self.rng = random.Random(self.seed)
        
        # Initialize pool storage
        self.object_pools = {}
        self.entity_pools = {}
        self.item_pools = {}
        
        # Load location templates
        self.templates = self._load_location_templates()
        self.locations = self.templates.get("locations", {})
        self.type_mapping = self.templates.get("type_mapping", {})
        
        print(f"LocationGenerator initialized with seed {self.seed}")
        print(f"Loaded {len(self.locations)} location templates")
        print(f"Loaded {len(self.object_pools)} object pools")
        print(f"Loaded {len(self.entity_pools)} entity pools")
        print(f"Loaded {len(self.item_pools)} item pools")
    
    def _load_location_templates(self) -> Dict[str, Any]:
        """Load location templates from JSON file"""
        try:
            # Try to find the data file
            possible_paths = [
                "data/locations.json",
                "../data/locations.json",
                "../../data/locations.json",
                "fantasy_rpg/data/locations.json"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        templates = json.load(f)
                        # Also load object and entity pools
                        self._load_content_pools()
                        return templates
            
            print("Warning: locations.json not found, using minimal templates")
            return self._get_minimal_templates()
            
        except Exception as e:
            print(f"Error loading locations.json: {e}")
            return self._get_minimal_templates()
    
    def _load_content_pools(self):
        """Load object, entity, and item pools from JSON files"""
        self.object_pools = {}
        self.entity_pools = {}
        self.item_pools = {}
        
        # Load objects
        try:
            possible_paths = [
                "data/objects.json",
                "../data/objects.json", 
                "../../data/objects.json",
                "fantasy_rpg/data/objects.json"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        objects_data = json.load(f)
                        self._build_object_pools(objects_data.get("objects", {}))
                    break
        except Exception as e:
            print(f"Warning: Could not load objects.json: {e}")
        
        # Load entities
        try:
            possible_paths = [
                "data/entities.json",
                "../data/entities.json",
                "../../data/entities.json", 
                "fantasy_rpg/data/entities.json"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        entities_data = json.load(f)
                        self._build_entity_pools(entities_data.get("entities", {}))
                    break
        except Exception as e:
            print(f"Warning: Could not load entities.json: {e}")
        
        # Load items
        try:
            possible_paths = [
                "data/items.json",
                "../data/items.json",
                "../../data/items.json",
                "fantasy_rpg/data/items.json"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        items_data = json.load(f)
                        self._build_item_pools(items_data.get("items", {}))
                    break
        except Exception as e:
            print(f"Warning: Could not load items.json: {e}")
    
    def _build_object_pools(self, objects_data: Dict[str, Any]):
        """Build object pools from objects data"""
        for obj_id, obj_data in objects_data.items():
            pools = obj_data.get("pools", [])
            spawn_weight = obj_data.get("spawn_weight", 1)
            
            for pool in pools:
                if pool not in self.object_pools:
                    self.object_pools[pool] = []
                self.object_pools[pool].append({
                    "id": obj_id,
                    "weight": spawn_weight,
                    "data": obj_data
                })
    
    def _build_entity_pools(self, entities_data: Dict[str, Any]):
        """Build entity pools from entities data"""
        for entity_id, entity_data in entities_data.items():
            pools = entity_data.get("pools", [])
            spawn_weight = entity_data.get("spawn_weight", 1)
            
            for pool in pools:
                if pool not in self.entity_pools:
                    self.entity_pools[pool] = []
                self.entity_pools[pool].append({
                    "id": entity_id,
                    "weight": spawn_weight,
                    "data": entity_data
                })
    
    def _build_item_pools(self, items_data: Dict[str, Any]):
        """Build item pools from items data"""
        for item_id, item_data in items_data.items():
            pools = item_data.get("pools", [])
            drop_weight = item_data.get("drop_weight", 1)
            
            for pool in pools:
                if pool not in self.item_pools:
                    self.item_pools[pool] = []
                self.item_pools[pool].append({
                    "id": item_id,
                    "weight": drop_weight,
                    "data": item_data
                })
    
    def _get_minimal_templates(self) -> Dict[str, Any]:
        """Fallback minimal templates if JSON file not found"""
        return {
            "location_categories": {
                "generic_locations": {
                    "description": "Generic wilderness areas",
                    "locations": [
                        {
                            "id": "wilderness_clearing",
                            "name": "Wilderness Clearing",
                            "type": "wilderness",
                            "spawn_weight": 100,
                            "min_areas": 1,
                            "max_areas": 1,
                            "area_templates": [
                                {
                                    "id": "clearing",
                                    "name": "Open Clearing",
                                    "description": "A natural clearing in the wilderness.",
                                    "size": "medium",
                                    "terrain": "open",
                                    "possible_exits": ["north", "south", "east", "west"],
                                    "spawn_tables": {
                                        "objects": [],
                                        "items": [],
                                        "entities": []
                                    }
                                }
                            ]
                        }
                    ]
                }
            },
            "hex_to_category_mapping": {
                "default": "generic_locations"
            }
        }
    
    def generate_locations_for_hex(self, hex_coords: Tuple[int, int], biome: str, terrain_type: str = None) -> List[Location]:
        """Generate 1-3 locations for a hex, ensuring at least one has exit_flag=True"""
        
        # Determine location type from hex properties
        location_type = self._get_location_type(biome, terrain_type)
        
        # Get all locations of this type
        available_locations = self._get_locations_by_type(location_type)
        
        if not available_locations:
            # Fallback to forest type
            available_locations = self._get_locations_by_type("forest")
        
        # Ensure we have at least one exit location
        exit_locations = [loc for loc in available_locations if loc.get("exit_flag", False)]
        non_exit_locations = [loc for loc in available_locations if not loc.get("exit_flag", False)]
        
        # Generate 1-3 locations
        num_locations = self.rng.randint(1, 3)
        selected_locations = []
        
        # Always include at least one exit location
        if exit_locations:
            exit_location = self._select_weighted_location(exit_locations)
            selected_locations.append(self._create_location_from_template(exit_location, hex_coords, len(selected_locations)))
        
        # Fill remaining slots with any type
        remaining_slots = num_locations - len(selected_locations)
        for _ in range(remaining_slots):
            location_template = self._select_weighted_location(available_locations)
            selected_locations.append(self._create_location_from_template(location_template, hex_coords, len(selected_locations)))
        
        return selected_locations
    
    def _get_location_type(self, biome: str, terrain_type: str = None) -> str:
        """Determine location type from hex properties"""
        
        # First try terrain type mapping
        if terrain_type and terrain_type in self.type_mapping:
            return self.type_mapping[terrain_type]
        
        # Then try biome mapping
        if biome in self.type_mapping:
            return self.type_mapping[biome]
        
        # Fallback based on biome characteristics
        biome_lower = biome.lower()
        if "forest" in biome_lower or "boreal" in biome_lower:
            return "forest"
        elif "mountain" in biome_lower or "alpine" in biome_lower:
            return "cave"
        elif "grassland" in biome_lower or "temperate" in biome_lower:
            return "plains"
        elif "ruins" in biome_lower or "ancient" in biome_lower:
            return "ruins"
        else:
            return "forest"
    
    def _get_locations_by_type(self, location_type: str) -> List[Dict]:
        """Get all location templates of a specific type"""
        locations = []
        for location_id, location_data in self.locations.items():
            if location_data.get("type") == location_type:
                # Add the ID to the data for reference
                location_with_id = location_data.copy()
                location_with_id["id"] = location_id
                locations.append(location_with_id)
        return locations
    
    def _select_weighted_location(self, locations: List[Dict]) -> Dict:
        """Select location based on spawn_weight"""
        if not locations:
            # Return a minimal fallback location
            return {
                "id": "fallback_clearing",
                "name": "Clearing",
                "description": "A simple clearing.",
                "size": "medium",
                "terrain": "open",
                "type": "forest",
                "exit_flag": True,
                "spawn_weight": 1,
                "content_pools": {"objects": [], "entities": []}
            }
        
        total_weight = sum(loc.get("spawn_weight", 1) for loc in locations)
        if total_weight == 0:
            return locations[0]
            
        roll = self.rng.randint(1, total_weight)
        
        current = 0
        for location in locations:
            current += location.get("spawn_weight", 1)
            if roll <= current:
                return location
        
        return locations[0]  # Fallback
    
    def _create_location_from_template(self, template: Dict, hex_coords: Tuple[int, int], index: int) -> Location:
        """Create a single-area Location from flat template"""
        
        location_id = f"{template['id']}_{hex_coords[0]}_{hex_coords[1]}_{index}"
        area_id = f"area_{index}"
        
        # Create the single area
        area = Area(
            id=area_id,
            name=template["name"],
            description=template["description"],
            size=AreaSize(template.get("size", "medium")),
            terrain=TerrainType(template.get("terrain", "open")),
            exits={},  # Single areas don't have internal exits
            objects=self._spawn_from_pools(template.get("content_pools", {}).get("objects", []), "objects"),
            items=[],  # Items not implemented yet
            entities=self._spawn_from_pools(template.get("content_pools", {}).get("entities", []), "entities")
        )
        
        # Determine location type
        location_type_str = template.get("type", "wilderness")
        try:
            location_type = LocationType(location_type_str)
        except ValueError:
            location_type = LocationType.WILDERNESS
        
        return Location(
            id=location_id,
            name=template["name"],
            type=location_type,
            areas={area_id: area},
            starting_area=area_id,
            exit_flag=template.get("exit_flag", False),
            # Copy location properties from template
            size=template.get("size", "medium"),
            terrain=template.get("terrain", "open"),
            # Copy shelter flags from template for condition system
            provides_some_shelter=template.get("provides_some_shelter", False),
            provides_good_shelter=template.get("provides_good_shelter", False),
            provides_excellent_shelter=template.get("provides_excellent_shelter", False)
        )
    

    
    def _spawn_from_pools(self, pools: List[str], content_type: str) -> List:
        """Spawn content from pool system"""
        if not pools:
            return []
        
        # Get appropriate pool data
        if content_type == "objects":
            pool_data = self.object_pools
            item_class = GameObject
        elif content_type == "entities":
            pool_data = self.entity_pools
            item_class = GameEntity
        else:
            return []
        
        # Collect all possible spawns from pools
        possible_spawns = []
        for pool_name in pools:
            if pool_name in pool_data:
                possible_spawns.extend(pool_data[pool_name])
        
        if not possible_spawns:
            return []
        
        # Simple spawning: MIN_OBJECTS_PER_LOCATION-MAX_OBJECTS_PER_LOCATION items based on pool availability
        min_spawns = min(MIN_OBJECTS_PER_LOCATION, len(possible_spawns))
        max_spawns = min(MAX_OBJECTS_PER_LOCATION, len(possible_spawns))
        num_spawns = self.rng.randint(min_spawns, max_spawns)
        
        # Spawn items
        spawned = []
        for _ in range(num_spawns):
            # Weighted selection
            total_weight = sum(item["weight"] for item in possible_spawns)
            if total_weight == 0:
                continue
                
            roll = self.rng.randint(1, total_weight)
            current = 0
            
            for spawn_item in possible_spawns:
                current += spawn_item["weight"]
                if roll <= current:
                    spawned.append(self._create_from_pool_data(spawn_item, item_class))
                    break
        
        return spawned
    
    def _create_from_pool_data(self, spawn_item: Dict, item_class):
        """Create game object from pool data"""
        item_id = spawn_item["id"]
        data = spawn_item["data"]
        
        if item_class == GameObject:
            # Handle name as either string or list of strings
            name_data = data.get("name", item_id.replace("_", " ").title())
            if isinstance(name_data, list):
                # Randomly select one name from the list
                selected_name = self.rng.choice(name_data)
            else:
                selected_name = name_data
            
            obj = GameObject(
                id=item_id,
                name=selected_name,
                shortkey=data.get("shortkey", ""),
                description=data.get("description", ""),
                interactive=data.get("interactive", True),
                properties=data.get("properties", {})
            )
            # Add item drops if object has them
            if "item_drops" in data:
                obj.item_drops = self._generate_item_drops(data["item_drops"])
            return obj
        elif item_class == GameEntity:
            # Handle name as either string or list of strings
            name_data = data.get("name", item_id.replace("_", " ").title())
            if isinstance(name_data, list):
                # Randomly select one name from the list
                selected_name = self.rng.choice(name_data)
            else:
                selected_name = name_data
                
            entity = GameEntity(
                id=item_id,
                name=selected_name,
                description=data.get("description", ""),
                hostile=data.get("hostile", False),
                stats=data.get("stats", {})
            )
            # Add item drops if entity has them
            if "item_drops" in data:
                entity.item_drops = self._generate_item_drops(data["item_drops"])
            return entity
        elif item_class == GameItem:
            return GameItem(
                id=item_id,
                name=data.get("name", item_id.replace("_", " ").title()),
                description=data.get("description", ""),
                value=data.get("value", 0),
                weight=data.get("weight", 0.0)
            )
        
        return None
    
    def _generate_item_drops(self, drop_config: Dict) -> List[GameItem]:
        """Generate items that can be dropped from objects/entities"""
        if not drop_config:
            return []
        
        pools = drop_config.get("pools", [])
        min_drops = drop_config.get("min_drops", 0)
        max_drops = drop_config.get("max_drops", 1)
        drop_chance = drop_config.get("drop_chance", 50)
        
        # Check if drops occur
        if self.rng.randint(1, 100) > drop_chance:
            return []
        
        # Collect possible items from pools
        possible_items = []
        for pool_name in pools:
            if pool_name in self.item_pools:
                possible_items.extend(self.item_pools[pool_name])
        
        if not possible_items:
            return []
        
        # Generate drops
        num_drops = self.rng.randint(min_drops, max_drops)
        drops = []
        
        for _ in range(num_drops):
            # Weighted selection
            total_weight = sum(item["weight"] for item in possible_items)
            if total_weight == 0:
                continue
                
            roll = self.rng.randint(1, total_weight)
            current = 0
            
            for item_data in possible_items:
                current += item_data["weight"]
                if roll <= current:
                    drops.append(self._create_from_pool_data(item_data, GameItem))
                    break
        
        return drops
    



def test_location_generator():
    """Test the location generator"""
    print("=== Testing Flat Location Generator ===")
    
    generator = LocationGenerator(seed=12345)
    
    # Test different biome/terrain combinations
    test_cases = [
        ((10, 10), "temperate_forest", "dense_forest"),
        ((15, 15), "alpine_mountains", "ancient_ruins"),
        ((20, 20), "temperate_grassland", "plains"),
        ((5, 5), "boreal_forest", "cave_entrance")
    ]
    
    for coords, biome, terrain in test_cases:
        print(f"\nGenerating locations for {coords} ({biome}, {terrain}):")
        
        locations = generator.generate_locations_for_hex(coords, biome, terrain)
        
        print(f"  Generated {len(locations)} location(s):")
        
        for i, location in enumerate(locations, 1):
            exit_status = "[EXIT]" if location.exit_flag else "[NO EXIT]"
            print(f"    [{i}] {location.name} ({location.type.value}) {exit_status}")
            
            # Show area details
            if location.areas:
                area = list(location.areas.values())[0]
                print(f"        Objects: {len(area.objects)}, Entities: {len(area.entities)}")
    
    print("\n✅ Flat location generator test complete!")


if __name__ == "__main__":
    test_location_generator()