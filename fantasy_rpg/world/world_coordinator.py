"""
Fantasy RPG - World Coordinator

Coordinates between overworld hexes and micro-level locations.
Handles movement between different scales of the game world.
Integrates climate system and world generation.
"""

from typing import Dict, List, Optional, Any, Tuple
import json
import os

# Import world generation systems (avoiding circular imports)
try:
    from .climate import ClimateSystem, ClimateZone
    from .terrain_generation import TerrainGenerator
    from .enhanced_biomes import EnhancedBiomeSystem
except ImportError:
    try:
        from climate import ClimateSystem, ClimateZone
        from terrain_generation import TerrainGenerator
        from enhanced_biomes import EnhancedBiomeSystem
    except ImportError:
        # Create minimal stubs if imports fail
        class ClimateSystem:
            def __init__(self, *args, **kwargs):
                pass
        class ClimateZone:
            def __init__(self, *args, **kwargs):
                self.base_temperature = 65.0
                self.zone_type = "temperate"
        class TerrainGenerator:
            def __init__(self, *args, **kwargs):
                pass
            def generate_heightmap(self, *args, **kwargs):
                return {}
        class EnhancedBiomeSystem:
            def __init__(self, *args, **kwargs):
                pass
            def classify_biome(self, *args, **kwargs):
                return "temperate_grassland"
            def get_biome(self, *args, **kwargs):
                return None


class WorldCoordinator:
    """Coordinates world-level and location-level interactions with full world generation"""
    
    def __init__(self, world_size: Tuple[int, int] = (20, 20), seed: int = 12345, 
                 skip_generation: bool = False):
        """
        Initialize WorldCoordinator.
        
        Args:
            world_size: Size of world grid (width, height)
            seed: Random seed for world generation
            skip_generation: If True, don't generate world (used for load_game)
        """
        self.world_size = world_size
        self.seed = seed
        self.hex_data = {}
        self.location_data = {}
        self.loaded_locations = {}
        
        # World generation systems
        self.terrain_generator = None
        self.enhanced_biomes = None
        self.climate_system = None
        self.climate_zones = {}
        
        # Generate world unless explicitly skipped
        if not skip_generation:
            self.generate_world()
    
    def generate_world(self):
        """Generate the complete world (terrain, biomes, climate, locations)"""
        # Debug logging for world generation
        try:
            from ..actions.action_logger import get_action_logger
            action_logger = get_action_logger()
            action_logger.log_system_message(f"WorldCoordinator generating world - size: {self.world_size}, seed: {self.seed}")
        except ImportError:
            print(f"DEBUG: WorldCoordinator generating world - size: {self.world_size}, seed: {self.seed}")
        
        # Initialize all world systems
        self._initialize_world_systems()
        
        # Generate the world
        self._generate_world()
        
        # Load location data
        self._load_location_index()
    
    def _initialize_world_systems(self):
        """Initialize all world generation systems"""
        print(f"Initializing world systems with seed {self.seed}...")
        
        # Initialize terrain generation
        self.terrain_generator = TerrainGenerator(self.seed)
        
        # Initialize biome systems
        self.enhanced_biomes = EnhancedBiomeSystem()
        
        # Initialize climate system
        self._initialize_climate_system()
        
        print("World systems initialized successfully")
    
    def _generate_world(self):
        """Generate the complete world using all systems"""
        print(f"Generating {self.world_size[0]}x{self.world_size[1]} world...")
        
        # Generate heightmap
        heightmap = self.terrain_generator.generate_heightmap(
            self.world_size[0], 
            self.world_size[1],
            scale=0.1,
            octaves=4
        )
        
        # Generate each hex
        for x in range(self.world_size[0]):
            for y in range(self.world_size[1]):
                hex_id = f"{x:02d}{y:02d}"
                
                # Get elevation
                elevation = heightmap.get((x, y), 0.5)
                
                # Get climate zone
                climate_zone = self.climate_zones.get(hex_id)
                
                # Determine biome using enhanced biome system
                if climate_zone and hasattr(self.enhanced_biomes, 'classify_biome'):
                    # Convert temperature to Celsius for biome classification
                    temp_c = (climate_zone.base_temperature - 32) * 5/9
                    # Estimate precipitation (simplified)
                    precip_mm = 500  # Default moderate precipitation
                    
                    # Use enhanced biome system for gameplay-focused biomes
                    biome_type = self.enhanced_biomes.classify_biome(
                        temp_c, 
                        precip_mm,
                        elevation
                    )
                    biome_data = self.enhanced_biomes.get_biome(biome_type)
                    biome_name = biome_data.display_name if biome_data else biome_type.replace('_', ' ').title()
                    description = biome_data.description if biome_data else f"A {biome_name.lower()} area"
                else:
                    # Fallback - simple biome based on elevation and climate
                    if elevation > 0.7:
                        biome_name = "Mountains"
                        biome_type = "alpine_mountains"
                        description = "Rugged mountain terrain with steep slopes"
                    elif elevation < 0.3:
                        biome_name = "Plains"
                        biome_type = "temperate_grassland"
                        description = "Rolling grasslands with scattered trees"
                    else:
                        biome_name = "Forest"
                        biome_type = "temperate_forest"
                        description = "Dense woodland with mixed trees"
                
                # Create hex data dictionary (locations generated on-demand)
                self.hex_data[hex_id] = {
                    "name": f"{biome_name} {hex_id}",
                    "type": biome_type,
                    "description": description,
                    "elevation": f"{int(elevation * 1000)}ft",
                    "biome": biome_type,
                    "locations": [],  # Will be populated on first visit
                    "locations_generated": False,  # Flag to track if locations have been generated
                    "coords": (x, y),
                    "elevation_raw": elevation
                }
        
        print(f"Generated world with {len(self.hex_data)} hexes")
        print("Locations will be generated on-demand when hexes are first visited")
        
        # Add some special locations to interesting hexes
        self._add_special_locations()
    
    def _add_special_locations(self):
        """Add special locations to interesting hexes"""
        # Add a few special locations for gameplay
        special_locations = [
            ("0847", ["forest_clearing_01", "old_oak_grove"]),
            ("0746", ["ruined_temple", "collapsed_tower"]),
            ("0848", ["narrow_pass", "cave_entrance"]),
            ("0948", ["village_center", "merchant_quarter", "inn"])
        ]
        
        for hex_id, locations in special_locations:
            if hex_id in self.hex_data:
                self.hex_data[hex_id]["locations"] = locations
                # Update the name to be more interesting
                if hex_id == "0847":
                    self.hex_data[hex_id]["name"] = "Forest Clearing"
                    self.hex_data[hex_id]["description"] = "A peaceful clearing surrounded by ancient oaks"
                elif hex_id == "0746":
                    self.hex_data[hex_id]["name"] = "Ancient Ruins"
                    self.hex_data[hex_id]["description"] = "Crumbling stone structures from a forgotten age"
                elif hex_id == "0848":
                    self.hex_data[hex_id]["name"] = "Mountain Pass"
                    self.hex_data[hex_id]["description"] = "A narrow path through rocky peaks"
                elif hex_id == "0948":
                    self.hex_data[hex_id]["name"] = "Trading Village"
                    self.hex_data[hex_id]["description"] = "A bustling village with merchants and travelers"
    
    def _generate_hex_locations(self, coords: Tuple[int, int], biome: str, elevation: float) -> List[Dict[str, Any]]:
        """Generate locations for a hex using LocationGenerator"""
        try:
            # Import LocationGenerator here to avoid circular imports
            from locations.location_generator import LocationGenerator
            
            # Create a LocationGenerator if we don't have one (use consistent seed)
            if not hasattr(self, '_location_generator'):
                self._location_generator = LocationGenerator(seed=self.seed)
            
            # Generate locations using the LocationGenerator
            locations = self._location_generator.generate_locations_for_hex(
                coords, 
                biome, 
                terrain_type=self._get_terrain_type(elevation)
            )
            
            # Convert Location objects to dictionaries for storage
            location_dicts = []
            for location in locations:
                if hasattr(location, '__dict__'):
                    # Convert Location object to dictionary
                    location_type = getattr(location, 'type', 'wilderness')
                    # Handle LocationType enum
                    if hasattr(location_type, 'value'):
                        location_type = location_type.value
                    elif hasattr(location_type, 'name'):
                        location_type = location_type.name.lower()
                    
                    # Get description from starting area if available
                    areas = getattr(location, 'areas', {})
                    starting_area_id = getattr(location, 'starting_area', 'entrance')
                    description = getattr(location, 'description', 'An unremarkable area.')
                    
                    # Convert areas to dictionaries
                    areas_dict = {}
                    for area_id, area in areas.items():
                        if hasattr(area, '__dict__'):
                            # Convert Area object to dictionary
                            area_dict = {
                                "id": getattr(area, 'id', area_id),
                                "name": getattr(area, 'name', 'Unknown Area'),
                                "description": getattr(area, 'description', 'An unremarkable area.'),
                                "size": getattr(area, 'size', 'medium'),
                                "terrain": getattr(area, 'terrain', 'open'),
                                "exits": getattr(area, 'exits', {}),
                                "objects": self._convert_objects_to_dict(getattr(area, 'objects', [])),
                                "items": self._convert_items_to_dict(getattr(area, 'items', [])),
                                "entities": self._convert_entities_to_dict(getattr(area, 'entities', []))
                            }
                            areas_dict[area_id] = area_dict
                        else:
                            # Already a dictionary
                            areas_dict[area_id] = area
                    
                    # Try to get description from starting area
                    if areas_dict and starting_area_id in areas_dict:
                        starting_area = areas_dict[starting_area_id]
                        description = starting_area.get('description', description)
                    
                    location_dict = {
                        "id": getattr(location, 'id', f"loc_{coords[0]}_{coords[1]}_{len(location_dicts)}"),
                        "name": getattr(location, 'name', 'Unknown Location'),
                        "type": str(location_type),
                        "description": description,
                        "exit_flag": getattr(location, 'exit_flag', True),
                        "size": getattr(location, 'size', 'medium'),
                        "terrain": getattr(location, 'terrain', 'open'),
                        "areas": areas_dict,
                        "starting_area": starting_area_id,
                        # Shelter flags for condition system
                        "provides_some_shelter": getattr(location, 'provides_some_shelter', False),
                        "provides_good_shelter": getattr(location, 'provides_good_shelter', False),
                        "provides_excellent_shelter": getattr(location, 'provides_excellent_shelter', False)
                    }
                else:
                    # Already a dictionary
                    location_dict = location
                
                location_dicts.append(location_dict)
            
            return location_dicts
            
        except Exception as e:
            print(f"Warning: Could not generate locations for hex {coords}: {e}")
            # Return basic fallback locations
            return self._get_fallback_locations(biome, coords)
    
    def _convert_objects_to_dict(self, objects: List) -> List[Dict]:
        """Convert GameObject objects to dictionaries"""
        objects_dict = []
        for obj in objects:
            if hasattr(obj, '__dict__'):
                # Convert GameObject to dictionary
                obj_dict = {
                    "id": getattr(obj, 'id', 'unknown'),
                    "name": getattr(obj, 'name', 'Unknown Object'),
                    "shortkey": getattr(obj, 'shortkey', ''),
                    "description": getattr(obj, 'description', ''),
                    "interactive": getattr(obj, 'interactive', True),
                    "properties": getattr(obj, 'properties', {}),
                    "item_drops": self._convert_items_to_dict(getattr(obj, 'item_drops', []))
                }
                objects_dict.append(obj_dict)
            else:
                # Already a dictionary
                objects_dict.append(obj)
        return objects_dict
    
    def _convert_items_to_dict(self, items: List) -> List[Dict]:
        """Convert Item objects to dictionaries (using unified Item class)"""
        items_dict = []
        for item in items:
            if hasattr(item, '__dict__'):
                # Convert Item to dictionary using its to_dict method if available
                if hasattr(item, 'to_dict'):
                    items_dict.append(item.to_dict())
                else:
                    # Fallback for legacy items
                    item_dict = {
                        "item_id": getattr(item, 'item_id', getattr(item, 'id', 'unknown')),
                        "name": getattr(item, 'name', 'Unknown Item'),
                        "type": getattr(item, 'item_type', 'misc'),
                        "description": getattr(item, 'description', ''),
                        "value": getattr(item, 'value', 0),
                        "weight": getattr(item, 'weight', 0.0),
                        "quantity": getattr(item, 'quantity', 1)
                    }
                    items_dict.append(item_dict)
            else:
                # Already a dictionary
                items_dict.append(item)
        return items_dict
    
    def _convert_entities_to_dict(self, entities: List) -> List[Dict]:
        """Convert GameEntity objects to dictionaries"""
        entities_dict = []
        for entity in entities:
            if hasattr(entity, '__dict__'):
                # Convert GameEntity to dictionary
                entity_dict = {
                    "id": getattr(entity, 'id', 'unknown'),
                    "name": getattr(entity, 'name', 'Unknown Entity'),
                    "description": getattr(entity, 'description', ''),
                    "hostile": getattr(entity, 'hostile', False),
                    "stats": getattr(entity, 'stats', {}),
                    "item_drops": self._convert_items_to_dict(getattr(entity, 'item_drops', []))
                }
                entities_dict.append(entity_dict)
            else:
                # Already a dictionary
                entities_dict.append(entity)
        return entities_dict

    def _get_terrain_type(self, elevation: float) -> str:
        """Determine terrain type from elevation"""
        if elevation > 0.7:
            return "mountain"
        elif elevation > 0.5:
            return "hills"
        elif elevation < 0.3:
            return "lowland"
        else:
            return "plains"
    
    def _get_fallback_locations(self, biome: str, coords: Tuple[int, int]) -> List[Dict[str, Any]]:
        """Generate basic fallback locations if LocationGenerator fails"""
        locations = []
        
        # Create 1-2 basic locations based on biome
        if "forest" in biome.lower():
            locations.append({
                "id": f"forest_clearing_{coords[0]}_{coords[1]}",
                "name": "Forest Clearing",
                "type": "wilderness",
                "description": "A small clearing surrounded by trees.",
                "exit_flag": True,
                "size": "medium",
                "terrain": "open"
            })
            locations.append({
                "id": f"dense_woods_{coords[0]}_{coords[1]}",
                "name": "Dense Woods",
                "type": "wilderness", 
                "description": "Thick forest with limited visibility.",
                "exit_flag": True,
                "size": "large",
                "terrain": "difficult"
            })
        elif "mountain" in biome.lower():
            locations.append({
                "id": f"rocky_outcrop_{coords[0]}_{coords[1]}",
                "name": "Rocky Outcrop",
                "type": "wilderness",
                "description": "A jutting formation of weathered stone.",
                "exit_flag": True,
                "size": "small",
                "terrain": "difficult"
            })
        else:
            locations.append({
                "id": f"open_area_{coords[0]}_{coords[1]}",
                "name": "Open Area",
                "type": "wilderness",
                "description": "An open stretch of land.",
                "exit_flag": True,
                "size": "medium", 
                "terrain": "open"
            })
        
        return locations
    
    def _load_location_index(self):
        """Load location index data"""
        # Debug logging for location loading
        try:
            from ..actions.action_logger import get_action_logger
            action_logger = get_action_logger()
            action_logger.log_system_message("📍 Loading location index...")
        except ImportError:
            print("DEBUG: Loading location index...")
        
        # Try to load from locations.json
        try:
            locations_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'locations.json')
            
            try:
                action_logger.log_system_message(f"📂 Loading locations from: {locations_path}")
            except:
                print(f"DEBUG: Loading locations from: {locations_path}")
            
            if os.path.exists(locations_path):
                with open(locations_path, 'r') as f:
                    self.location_data = json.load(f)
                
                # Debug: Show what was loaded
                locations = self.location_data.get("locations", {})
                try:
                    action_logger.log_system_message(f"✅ Loaded {len(locations)} location templates")
                    
                    # Show a few examples with shelter flags
                    shelter_examples = []
                    for loc_id, loc_data in list(locations.items())[:3]:
                        shelter_flags = [k for k in loc_data.keys() if k.startswith("provides_")]
                        if shelter_flags:
                            shelter_examples.append(f"{loc_data.get('name', loc_id)}: {shelter_flags}")
                    
                    if shelter_examples:
                        action_logger.log_system_message(f"🏠 Shelter examples: {'; '.join(shelter_examples)}")
                    else:
                        action_logger.log_system_message("⚠️ No shelter flags found in location templates!")
                        
                except:
                    print(f"DEBUG: Loaded {len(locations)} location templates")
                    
            else:
                try:
                    action_logger.log_system_message(f"❌ locations.json not found at {locations_path}")
                except:
                    print(f"DEBUG: locations.json not found at {locations_path}")
                # Fallback to basic location data
                self._create_basic_locations()
        except Exception as e:
            try:
                action_logger.log_system_message(f"❌ Error loading locations.json: {e}")
            except:
                print(f"Warning: Could not load locations.json: {e}")
            self._create_basic_locations()
    
    def _create_basic_locations(self):
        """Create basic location data as fallback"""
        self.location_data = {
            "forest_clearing_01": {
                "name": "Forest Clearing",
                "type": "location",
                "description": "A small clearing in the forest with wildflowers and berry bushes.",
                "can_enter": True,
                "exit_flags": ["forest"],
                "objects": [
                    {
                        "name": "Berry Bush",
                        "properties": {"can_forage": True},
                        "pools": ["forest_berries", "common_herbs"]
                    },
                    {
                        "name": "Fallen Log", 
                        "properties": {"can_forage": True},
                        "pools": ["dead_wood", "insects"]
                    }
                ],
                "exits": {}
            },
            "old_oak_grove": {
                "name": "Old Oak Grove",
                "type": "location", 
                "description": "A grove of ancient oak trees with thick canopy overhead.",
                "can_enter": True,
                "exit_flags": ["forest"],
                "objects": [
                    {
                        "name": "Ancient Oak",
                        "properties": {"can_forage": True},
                        "pools": ["tree_bark", "acorns", "medicinal_herbs"]
                    }
                ],
                "exits": {}
            }
        }
    
    def can_travel_to_hex(self, from_hex: str, to_hex: str) -> bool:
        """Check if travel between hexes is possible"""
        # Simplified - in real system would check terrain, roads, etc.
        from_data = self.hex_data.get(from_hex)
        to_data = self.hex_data.get(to_hex)
        
        if not from_data or not to_data:
            return False
        
        # Check if hexes are adjacent (simplified hex math)
        try:
            from_col = int(from_hex[:2])
            from_row = int(from_hex[2:])
            to_col = int(to_hex[:2])
            to_row = int(to_hex[2:])
            
            col_diff = abs(to_col - from_col)
            row_diff = abs(to_row - from_row)
            
            # Adjacent if difference is 1 in any direction
            return (col_diff <= 1 and row_diff <= 1) and (col_diff + row_diff > 0)
        except:
            return False
    
    def get_hex_info(self, hex_id: str) -> Dict[str, Any]:
        """Get information about a hex"""
        if hex_id in self.hex_data:
            return self.hex_data[hex_id]
        
        # Generate basic hex data on-demand for valid coordinates
        try:
            col = int(hex_id[:2])
            row = int(hex_id[2:])
            
            # Check if coordinates are within world bounds
            if 0 <= col < self.world_size[0] and 0 <= row < self.world_size[1]:
                # Generate basic hex based on climate zone
                climate_zone = self.climate_zones.get(hex_id)
                if climate_zone:
                    terrain_types = {
                        "arctic": ("Frozen Wasteland", "A desolate expanse of ice and snow"),
                        "subarctic": ("Tundra", "Cold, windswept plains with sparse vegetation"),
                        "temperate": ("Rolling Hills", "Gentle hills covered in grass and scattered trees"),
                        "subtropical": ("Warm Plains", "Sun-warmed grasslands with occasional groves"),
                        "tropical": ("Jungle", "Dense tropical vegetation and humid air")
                    }
                    
                    terrain_name, terrain_desc = terrain_types.get(
                        climate_zone.zone_type, 
                        ("Wilderness", "An unremarkable stretch of land")
                    )
                    
                    generated_hex = {
                        "name": f"{terrain_name} {hex_id}",
                        "type": climate_zone.zone_type,
                        "description": terrain_desc,
                        "elevation": f"{300 + (row * 20)}ft",
                        "biome": climate_zone.zone_type,
                        "locations": [],
                        "generated": True  # Mark as auto-generated
                    }
                    
                    # Cache the generated hex
                    self.hex_data[hex_id] = generated_hex
                    return generated_hex
        except:
            pass
        
        # Fallback for invalid coordinates
        return {
            "name": f"Unknown Hex {hex_id}",
            "type": "unknown",
            "description": "An unexplored area beyond the known world",
            "elevation": "320 ft",
            "locations": []
        }
    
    def get_nearby_hexes(self, hex_id: str) -> List[Dict[str, Any]]:
        """Get nearby hexes with their information"""
        nearby = []
        
        try:
            col = int(hex_id[:2])
            row = int(hex_id[2:])
            
            # Check all adjacent hexes
            directions = [
                (-1, -1, "northwest"), (-1, 0, "north"), (-1, 1, "northeast"),
                (0, -1, "west"), (0, 1, "east"),
                (1, -1, "southwest"), (1, 0, "south"), (1, 1, "southeast")
            ]
            
            for dc, dr, direction in directions:
                nearby_hex = f"{col + dc:02d}{row + dr:02d}"
                if nearby_hex in self.hex_data:
                    hex_info = self.hex_data[nearby_hex].copy()
                    hex_info["direction"] = direction
                    hex_info["hex"] = nearby_hex
                    nearby.append(hex_info)
        except:
            pass
        
        return nearby
    
    def get_hex_locations(self, hex_id: str) -> List[Dict[str, Any]]:
        """Get locations available in a hex (generate on-demand)"""
        hex_info = self.get_hex_info(hex_id)
        
        # Check if locations have been generated for this hex
        if not hex_info.get("locations_generated", False):
            # Generate locations on first access
            coords = hex_info.get("coords", (0, 0))
            biome = hex_info.get("biome", "temperate_forest")
            elevation = hex_info.get("elevation_raw", 0.5)
            
            # Generate locations for this hex
            generated_locations = self._generate_hex_locations(coords, biome, elevation)
            
            # Update hex data with generated locations
            hex_info["locations"] = generated_locations
            hex_info["locations_generated"] = True
            
            # Update the stored hex data
            self.hex_data[hex_id] = hex_info
            
            print(f"Generated {len(generated_locations)} locations for hex {hex_id}")
        
        return hex_info.get("locations", [])
    
    def get_location_by_id(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get location data by ID"""
        return self.location_data.get(location_id)
    
    def load_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Load full location data for gameplay"""
        if location_id in self.loaded_locations:
            return self.loaded_locations[location_id]
        
        base_data = self.location_data.get(location_id)
        if not base_data:
            return None
        
        # Create a copy for gameplay (so we can modify it)
        location = base_data.copy()
        location["id"] = location_id
        
        # Cache the loaded location
        self.loaded_locations[location_id] = location
        
        return location
    
    def update_location(self, location_id: str, updates: Dict[str, Any]):
        """Update a loaded location with changes"""
        if location_id in self.loaded_locations:
            self.loaded_locations[location_id].update(updates)
    
    def get_current_scale(self, player_state) -> str:
        """Determine if player is on overworld or in a location"""
        if hasattr(player_state, 'current_location') and player_state.current_location:
            return "location"
        else:
            return "overworld"
    
    def get_movement_time_multiplier(self, scale: str) -> float:
        """Get time multiplier for movement at different scales"""
        if scale == "overworld":
            return 2.0  # Overworld movement takes longer
        elif scale == "location":
            return 0.1  # Location movement is faster
        else:
            return 1.0  # Default
    
    def _initialize_climate_system(self):
        """Initialize the climate system for world generation"""
        try:
            width, height = self.world_size
            self.climate_system = ClimateSystem(height)
            
            # Generate basic heightmap for climate calculation
            heightmap = self._generate_basic_heightmap()
            
            # Generate climate zones
            self.climate_zones = self.climate_system.generate_climate_zones(
                self.world_size, heightmap
            )
            
        except Exception as e:
            print(f"Warning: Could not initialize climate system: {e}")
            self.climate_system = None
            self.climate_zones = {}
    
    def _generate_basic_heightmap(self) -> Dict[Tuple[int, int], float]:
        """Generate a basic heightmap for climate calculations"""
        import math
        
        width, height = self.world_size
        heightmap = {}
        center_x, center_y = width // 2, height // 2
        
        for x in range(width):
            for y in range(height):
                # Simple heightmap - higher in center, lower at edges
                dx = abs(x - center_x)
                dy = abs(y - center_y)
                distance = math.sqrt(dx*dx + dy*dy)
                max_distance = math.sqrt(center_x*center_x + center_y*center_y)
                
                # Normalize to 0.0-1.0
                if max_distance > 0:
                    elevation = max(0.0, 1.0 - (distance / max_distance))
                else:
                    elevation = 0.5
                
                heightmap[(x, y)] = elevation
        
        return heightmap
    
    def get_climate_info(self, hex_id: str) -> Optional[Dict[str, Any]]:
        """Get climate information for a hex"""
        try:
            # Parse hex coordinates
            col = int(hex_id[:2])
            row = int(hex_id[2:])
            coords = (col, row)
            
            if coords in self.climate_zones:
                climate_zone = self.climate_zones[coords]
                return {
                    "zone_type": climate_zone.zone_type,
                    "base_temperature": climate_zone.base_temperature,
                    "annual_precipitation": climate_zone.annual_precipitation,
                    "has_snow": climate_zone.has_snow,
                    "seasonal_variation": climate_zone.seasonal_variation
                }
        except:
            pass
        
        return None
    
    def get_hex_ambient_temperature(self, hex_id: str, season: str = "summer") -> float:
        """
        Get ambient environmental temperature at a specific hex.
        
        This is a convenience wrapper around ClimateSystem.get_ambient_temperature()
        that handles hex ID parsing and climate zone lookup. Returns the seasonal
        average temperature for the hex's climate zone.
        
        Args:
            hex_id: Hex identifier string (e.g., "0510" for column 5, row 10)
            season: Season name ("spring", "summer", "autumn", "winter")
        
        Returns:
            Ambient temperature in °F (average for the season), or 65.0 if hex not found
            
        Usage Context:
            - Getting hex-level climate data
            - World generation (location placement based on temperature)
            - NOT for current weather conditions (use WeatherSystem)
            - NOT for player body temperature (use PlayerState.get_body_temperature_status)
        """
        try:
            col = int(hex_id[:2])
            row = int(hex_id[2:])
            coords = (col, row)
            
            if coords in self.climate_zones:
                climate_zone = self.climate_zones[coords]
                temp_range = climate_zone.get_seasonal_temp(season)
                return sum(temp_range) / 2  # Return average temperature
        except:
            pass
        
        # Default temperature
        return 65.0