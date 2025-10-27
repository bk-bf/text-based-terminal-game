"""
Fantasy RPG - World Coordinator

Coordinates between overworld hexes and micro-level locations.
Handles movement between different scales of the game world.
Integrates climate system and world generation.
"""

from typing import Dict, List, Optional, Any, Tuple
import json
import os

# Import climate system components
try:
    from .climate import ClimateSystem, ClimateZone
except ImportError:
    from climate import ClimateSystem, ClimateZone


class WorldCoordinator:
    """Coordinates world-level and location-level interactions"""
    
    def __init__(self, world_size: Tuple[int, int] = (20, 20)):
        self.world_size = world_size
        self.hex_data = {}
        self.location_data = {}
        self.loaded_locations = {}
        self.climate_system = None
        self.climate_zones = {}
        
        # Initialize climate system
        self._initialize_climate_system()
        
        # Load basic hex data
        self._load_hex_data()
        self._load_location_index()
    
    def _load_hex_data(self):
        """Load basic hex information"""
        # Simplified hex data - in a real system this would come from world generation
        self.hex_data = {
            "0847": {
                "name": "Forest Clearing",
                "type": "forest",
                "description": "A peaceful clearing surrounded by ancient oaks",
                "elevation": "320 ft",
                "biome": "temperate_forest",
                "locations": ["forest_clearing_01", "old_oak_grove"]
            },
            "0746": {
                "name": "Ancient Ruins", 
                "type": "ruins",
                "description": "Crumbling stone structures from a forgotten age",
                "elevation": "280 ft",
                "biome": "temperate_forest",
                "locations": ["ruined_temple", "collapsed_tower"]
            },
            "0848": {
                "name": "Mountain Pass",
                "type": "mountain", 
                "description": "A narrow path through rocky peaks",
                "elevation": "1200 ft",
                "biome": "mountain",
                "locations": ["narrow_pass", "cave_entrance"]
            },
            "0948": {
                "name": "Trading Village",
                "type": "settlement",
                "description": "A bustling village with merchants and travelers", 
                "elevation": "250 ft",
                "biome": "temperate_plains",
                "locations": ["village_center", "merchant_quarter", "inn"]
            }
        }
    
    def _load_location_index(self):
        """Load location index data"""
        # Try to load from locations.json
        try:
            locations_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'locations.json')
            if os.path.exists(locations_path):
                with open(locations_path, 'r') as f:
                    self.location_data = json.load(f)
            else:
                # Fallback to basic location data
                self._create_basic_locations()
        except Exception as e:
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
        return self.hex_data.get(hex_id, {
            "name": f"Unknown Hex {hex_id}",
            "type": "unknown",
            "description": "An unexplored area",
            "elevation": "320 ft",
            "locations": []
        })
    
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
        """Get locations available in a hex"""
        hex_info = self.get_hex_info(hex_id)
        location_ids = hex_info.get("locations", [])
        
        locations = []
        for loc_id in location_ids:
            if loc_id in self.location_data:
                loc_data = self.location_data[loc_id].copy()
                loc_data["id"] = loc_id
                locations.append(loc_data)
        
        return locations
    
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
    
    def get_temperature_at_hex(self, hex_id: str, season: str = "summer") -> float:
        """Get temperature at a specific hex for a given season"""
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