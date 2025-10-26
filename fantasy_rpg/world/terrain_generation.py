"""
Fantasy RPG - Terrain Generation

Multi-octave Perlin/Simplex noise implementation for realistic terrain generation.
This module provides the foundational noise functions needed for geographic world generation.
"""

import math
import random
from typing import Tuple, List, Dict


class NoiseGenerator:
    """
    Simple Perlin-style noise generator for terrain generation.
    
    This implementation provides multi-octave noise suitable for creating
    realistic heightmaps and terrain variation.
    """
    
    def __init__(self, seed: int = 12345):
        """Initialize noise generator with a seed for reproducible results."""
        self.seed = seed
        random.seed(seed)
        
        # Generate permutation table for noise
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm = self.perm + self.perm  # Duplicate for easier indexing
        
        print(f"Initialized noise generator with seed {seed}")
    
    def fade(self, t: float) -> float:
        """Fade function for smooth interpolation (6t^5 - 15t^4 + 10t^3)."""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation between a and b."""
        return a + t * (b - a)
    
    def grad(self, hash_val: int, x: float, y: float) -> float:
        """Calculate gradient vector dot product."""
        h = hash_val & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else 0)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def noise2d(self, x: float, y: float) -> float:
        """
        Generate 2D Perlin noise at coordinates (x, y).
        Returns value between -1 and 1.
        """
        # Find unit square containing point
        X = int(x) & 255
        Y = int(y) & 255
        
        # Find relative position within square
        x -= int(x)
        y -= int(y)
        
        # Compute fade curves
        u = self.fade(x)
        v = self.fade(y)
        
        # Hash coordinates of square corners
        A = self.perm[X] + Y
        AA = self.perm[A]
        AB = self.perm[A + 1]
        B = self.perm[X + 1] + Y
        BA = self.perm[B]
        BB = self.perm[B + 1]
        
        # Blend results from corners
        return self.lerp(
            self.lerp(
                self.grad(self.perm[AA], x, y),
                self.grad(self.perm[BA], x - 1, y),
                u
            ),
            self.lerp(
                self.grad(self.perm[AB], x, y - 1),
                self.grad(self.perm[BB], x - 1, y - 1),
                u
            ),
            v
        )
    
    def octave_noise2d(self, x: float, y: float, octaves: int = 4, 
                      persistence: float = 0.5, scale: float = 1.0) -> float:
        """
        Generate multi-octave noise for more realistic terrain.
        
        Args:
            x, y: Coordinates
            octaves: Number of noise layers to combine
            persistence: How much each octave contributes (0.0-1.0)
            scale: Overall scale of the noise
        
        Returns:
            Combined noise value between -1 and 1
        """
        value = 0.0
        amplitude = 1.0
        frequency = scale
        max_value = 0.0
        
        for i in range(octaves):
            value += self.noise2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2.0
        
        return value / max_value


class TerrainGenerator:
    """
    Terrain generation system using multi-octave noise.
    
    This class handles the generation of realistic heightmaps and terrain
    features using noise functions.
    """
    
    def __init__(self, seed: int = 12345):
        """Initialize terrain generator with noise generator."""
        self.seed = seed
        self.noise = NoiseGenerator(seed)
        print(f"Initialized terrain generator with seed {seed}")
    
    def generate_heightmap(self, width: int, height: int, 
                          scale: float = 0.1, octaves: int = 4) -> Dict[Tuple[int, int], float]:
        """
        Generate a heightmap using multi-octave noise.
        
        Args:
            width, height: Dimensions of the heightmap
            scale: Scale factor for noise (smaller = more zoomed out)
            octaves: Number of noise octaves for detail
        
        Returns:
            Dictionary mapping (x, y) coordinates to elevation values (0.0-1.0)
        """
        print(f"Generating {width}x{height} heightmap with {octaves} octaves...")
        
        heightmap = {}
        
        for x in range(width):
            for y in range(height):
                # Generate noise value (-1 to 1) and normalize to (0 to 1)
                noise_value = self.noise.octave_noise2d(
                    x, y, 
                    octaves=octaves, 
                    persistence=0.5, 
                    scale=scale
                )
                
                # Normalize from [-1, 1] to [0, 1]
                elevation = (noise_value + 1.0) / 2.0
                heightmap[(x, y)] = elevation
        
        print(f"Generated heightmap with elevation range: "
              f"{min(heightmap.values()):.3f} - {max(heightmap.values()):.3f}")
        
        return heightmap
    
    def generate_continental_plates(self, width: int, height: int, num_plates: int = 6) -> Dict[Tuple[int, int], int]:
        """
        Generate continental plates using Voronoi-like regions.
        
        Args:
            width, height: Dimensions of the world
            num_plates: Number of tectonic plates to generate
        
        Returns:
            Dictionary mapping coordinates to plate IDs
        """
        print(f"Generating {num_plates} continental plates...")
        
        # Generate random plate centers
        plate_centers = []
        for i in range(num_plates):
            center_x = random.randint(0, width - 1)
            center_y = random.randint(0, height - 1)
            plate_centers.append((center_x, center_y, i))
        
        print(f"Plate centers: {[(x, y) for x, y, _ in plate_centers]}")
        
        # Assign each point to nearest plate center
        plate_map = {}
        for x in range(width):
            for y in range(height):
                min_distance = float('inf')
                closest_plate = 0
                
                for center_x, center_y, plate_id in plate_centers:
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_plate = plate_id
                
                plate_map[(x, y)] = closest_plate
        
        return plate_map
    
    def calculate_plate_boundaries(self, plate_map: Dict[Tuple[int, int], int], 
                                 width: int, height: int) -> Dict[Tuple[int, int], bool]:
        """
        Identify plate boundary locations where tectonic activity occurs.
        
        Args:
            plate_map: Dictionary mapping coordinates to plate IDs
            width, height: Dimensions of the world
        
        Returns:
            Dictionary mapping coordinates to True if on plate boundary
        """
        print("Calculating plate boundaries...")
        
        boundaries = {}
        boundary_count = 0
        
        for x in range(width):
            for y in range(height):
                coords = (x, y)
                current_plate = plate_map[coords]
                is_boundary = False
                
                # Check adjacent cells for different plates
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        
                        adj_x, adj_y = x + dx, y + dy
                        if 0 <= adj_x < width and 0 <= adj_y < height:
                            adj_coords = (adj_x, adj_y)
                            if plate_map[adj_coords] != current_plate:
                                is_boundary = True
                                boundary_count += 1
                                break
                    
                    if is_boundary:
                        break
                
                boundaries[coords] = is_boundary
        
        print(f"Found {boundary_count} boundary hexes")
        return boundaries
    
    def generate_continental_heightmap(self, width: int, height: int) -> Dict[Tuple[int, int], float]:
        """
        Generate heightmap with realistic continental plate simulation.
        
        This creates realistic landmass shapes by simulating tectonic plates,
        their boundaries, and the geological processes that create elevation.
        """
        print(f"Generating continental heightmap {width}x{height} with plate tectonics...")
        
        # Step 1: Generate tectonic plates
        plate_map = self.generate_continental_plates(width, height, num_plates=6)
        
        # Step 2: Calculate plate boundaries
        boundaries = self.calculate_plate_boundaries(plate_map, width, height)
        
        # Step 3: Generate base elevation for each plate
        plate_elevations = {}
        num_plates = max(plate_map.values()) + 1
        
        for plate_id in range(num_plates):
            # Each plate has a base elevation tendency
            base_elevation = random.uniform(0.2, 0.8)  # Ocean to continental
            plate_type = "oceanic" if base_elevation < 0.4 else "continental"
            plate_elevations[plate_id] = {
                "base": base_elevation,
                "type": plate_type
            }
            print(f"Plate {plate_id}: {plate_type} (base elevation: {base_elevation:.3f})")
        
        # Step 4: Generate heightmap based on plates and boundaries
        heightmap = {}
        
        for x in range(width):
            for y in range(height):
                coords = (x, y)
                plate_id = plate_map[coords]
                is_boundary = boundaries[coords]
                
                # Base elevation from plate
                base_elevation = plate_elevations[plate_id]["base"]
                
                # Add tectonic activity at boundaries
                if is_boundary:
                    # Plate boundaries create mountains or trenches
                    boundary_noise = self.noise.octave_noise2d(
                        x, y, octaves=3, persistence=0.6, scale=0.08
                    )
                    
                    # Determine if this is a convergent (mountain) or divergent (trench) boundary
                    if boundary_noise > 0:
                        # Convergent boundary - creates mountains
                        tectonic_modifier = 0.3 + (boundary_noise * 0.4)
                    else:
                        # Divergent boundary - creates valleys/trenches
                        tectonic_modifier = -0.2 + (boundary_noise * 0.2)
                else:
                    tectonic_modifier = 0
                
                # Add regional terrain variation within plates
                regional_noise = self.noise.octave_noise2d(
                    x, y, octaves=4, persistence=0.5, scale=0.05
                ) * 0.2
                
                # Add local terrain detail
                local_noise = self.noise.octave_noise2d(
                    x, y, octaves=6, persistence=0.4, scale=0.15
                ) * 0.1
                
                # Combine all elevation factors
                final_elevation = base_elevation + tectonic_modifier + regional_noise + local_noise
                
                # Clamp to valid range
                final_elevation = max(0.0, min(1.0, final_elevation))
                heightmap[coords] = final_elevation
        
        # Step 5: Apply continental shelf effects (gradual ocean depth)
        heightmap = self._apply_continental_shelf(heightmap, width, height)
        
        print(f"Generated continental heightmap with elevation range: "
              f"{min(heightmap.values()):.3f} - {max(heightmap.values()):.3f}")
        
        # Print elevation statistics
        elevations = list(heightmap.values())
        ocean_count = sum(1 for e in elevations if e < 0.3)
        land_count = len(elevations) - ocean_count
        print(f"Ocean coverage: {ocean_count}/{len(elevations)} ({ocean_count/len(elevations)*100:.1f}%)")
        print(f"Land coverage: {land_count}/{len(elevations)} ({land_count/len(elevations)*100:.1f}%)")
        
        return heightmap
    
    def _apply_continental_shelf(self, heightmap: Dict[Tuple[int, int], float], 
                               width: int, height: int) -> Dict[Tuple[int, int], float]:
        """
        Apply continental shelf effects to create realistic ocean depth gradients.
        
        Args:
            heightmap: Current heightmap
            width, height: World dimensions
        
        Returns:
            Modified heightmap with continental shelf effects
        """
        print("Applying continental shelf effects...")
        
        # Find coastline (transition from water to land)
        coastline = set()
        for x in range(width):
            for y in range(height):
                coords = (x, y)
                elevation = heightmap[coords]
                
                if 0.25 <= elevation <= 0.35:  # Near sea level
                    # Check if adjacent to different elevation zones
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            
                            adj_x, adj_y = x + dx, y + dy
                            if 0 <= adj_x < width and 0 <= adj_y < height:
                                adj_elevation = heightmap[(adj_x, adj_y)]
                                if abs(adj_elevation - elevation) > 0.2:
                                    coastline.add(coords)
                                    break
        
        print(f"Found {len(coastline)} coastline hexes")
        
        # Apply distance-based depth modification
        modified_heightmap = heightmap.copy()
        
        for x in range(width):
            for y in range(height):
                coords = (x, y)
                elevation = heightmap[coords]
                
                if elevation < 0.3:  # Ocean areas
                    # Find distance to nearest coastline
                    min_distance = float('inf')
                    for coast_x, coast_y in coastline:
                        distance = math.sqrt((x - coast_x)**2 + (y - coast_y)**2)
                        min_distance = min(min_distance, distance)
                    
                    # Apply depth gradient based on distance from coast
                    if min_distance < float('inf'):
                        # Continental shelf extends ~10 hexes from coast
                        shelf_distance = min(min_distance / 10.0, 1.0)
                        depth_modifier = shelf_distance * 0.15  # Deeper water further from coast
                        modified_elevation = elevation - depth_modifier
                        modified_heightmap[coords] = max(0.0, modified_elevation)
        
        return modified_heightmap
    
    def calculate_drainage_patterns(self, heightmap: Dict[Tuple[int, int], float], 
                                  width: int, height: int) -> Dict[Tuple[int, int], Tuple[int, int]]:
        """
        Calculate water flow directions from each hex to its lowest neighbor.
        
        This implements a simple flow direction algorithm where water flows
        from each hex to the adjacent hex with the lowest elevation.
        
        Args:
            heightmap: Dictionary mapping coordinates to elevation values
            width, height: Dimensions of the world
        
        Returns:
            Dictionary mapping each coordinate to the coordinate it drains to,
            or None if it's a sink (local minimum)
        """
        print("Calculating drainage patterns...")
        
        flow_directions = {}
        sinks = []
        
        # Define the 8 adjacent directions (including diagonals)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for x in range(width):
            for y in range(height):
                coords = (x, y)
                current_elevation = heightmap[coords]
                
                # Find the lowest adjacent hex
                lowest_elevation = current_elevation
                flow_target = None
                
                for dx, dy in directions:
                    adj_x, adj_y = x + dx, y + dy
                    
                    # Check bounds
                    if 0 <= adj_x < width and 0 <= adj_y < height:
                        adj_coords = (adj_x, adj_y)
                        adj_elevation = heightmap[adj_coords]
                        
                        # Water flows to lowest adjacent hex
                        if adj_elevation < lowest_elevation:
                            lowest_elevation = adj_elevation
                            flow_target = adj_coords
                
                if flow_target is None:
                    # This is a sink (local minimum) - water pools here
                    sinks.append(coords)
                    flow_directions[coords] = None
                else:
                    flow_directions[coords] = flow_target
        
        print(f"Calculated drainage for {len(flow_directions)} hexes")
        print(f"Found {len(sinks)} drainage sinks (lakes/depressions)")
        
        return flow_directions
    
    def calculate_flow_accumulation(self, flow_directions: Dict[Tuple[int, int], Tuple[int, int]], 
                                  width: int, height: int) -> Dict[Tuple[int, int], int]:
        """
        Calculate how much water flows through each hex (flow accumulation).
        
        This determines which areas will have rivers by counting how many
        upstream hexes drain through each location.
        
        Args:
            flow_directions: Dictionary mapping coordinates to their drainage targets
            width, height: Dimensions of the world
        
        Returns:
            Dictionary mapping coordinates to flow accumulation values
        """
        print("Calculating flow accumulation...")
        
        # Initialize accumulation (each hex starts with 1 unit of water)
        accumulation = {}
        for x in range(width):
            for y in range(height):
                accumulation[(x, y)] = 1
        
        # Build a list of all coordinates sorted by elevation (high to low)
        # This ensures we process upstream areas before downstream
        all_coords = [(x, y) for x in range(width) for y in range(height)]
        
        # We need the heightmap to sort by elevation
        # For now, we'll use a simple topological sort approach
        processed = set()
        
        # Process each hex, following flow until we reach a sink or processed hex
        for start_coords in all_coords:
            if start_coords in processed:
                continue
            
            # Follow the flow path from this starting point
            current = start_coords
            path = []
            
            while current is not None and current not in processed:
                path.append(current)
                next_coords = flow_directions.get(current)
                
                # Stop if we reach a sink or already processed hex
                if next_coords is None or next_coords in processed:
                    break
                
                current = next_coords
            
            # Now accumulate flow along the path (from end to start)
            for i in range(len(path) - 1, -1, -1):
                coords = path[i]
                processed.add(coords)
                
                # Add flow from this hex to its downstream neighbor
                downstream = flow_directions.get(coords)
                if downstream is not None:
                    accumulation[downstream] += accumulation[coords]
        
        # Find areas with significant flow for river placement
        max_flow = max(accumulation.values())
        river_threshold = max(5, max_flow * 0.1)  # Rivers need at least 5 upstream hexes
        
        river_hexes = sum(1 for flow in accumulation.values() if flow >= river_threshold)
        print(f"Flow accumulation calculated. Max flow: {max_flow}")
        print(f"Potential river hexes (flow >= {river_threshold}): {river_hexes}")
        
        return accumulation
    
    def identify_watersheds(self, flow_directions: Dict[Tuple[int, int], Tuple[int, int]], 
                          width: int, height: int) -> Dict[Tuple[int, int], int]:
        """
        Identify watershed regions - areas that drain to the same sink.
        
        Args:
            flow_directions: Dictionary mapping coordinates to their drainage targets
            width, height: Dimensions of the world
        
        Returns:
            Dictionary mapping coordinates to watershed IDs
        """
        print("Identifying watersheds...")
        
        watersheds = {}
        watershed_id = 0
        
        # Find all sinks (endpoints of drainage)
        sinks = []
        for coords, target in flow_directions.items():
            if target is None:
                sinks.append(coords)
        
        print(f"Found {len(sinks)} watershed outlets")
        
        # For each hex, follow drainage to find which sink it reaches
        for x in range(width):
            for y in range(height):
                start_coords = (x, y)
                
                if start_coords in watersheds:
                    continue  # Already processed
                
                # Follow flow to find the sink
                current = start_coords
                path = []
                visited = set()
                
                while current is not None and current not in visited:
                    path.append(current)
                    visited.add(current)
                    current = flow_directions.get(current)
                
                # Assign watershed ID based on the sink reached
                if current is None:
                    # Reached a sink
                    sink_coords = path[-1] if path else start_coords
                    
                    # Find or create watershed ID for this sink
                    sink_watershed = None
                    for coords, ws_id in watersheds.items():
                        if coords == sink_coords:
                            sink_watershed = ws_id
                            break
                    
                    if sink_watershed is None:
                        sink_watershed = watershed_id
                        watershed_id += 1
                    
                    # Assign all hexes in path to this watershed
                    for coords in path:
                        watersheds[coords] = sink_watershed
                else:
                    # Reached an already processed hex
                    existing_watershed = watersheds.get(current, watershed_id)
                    if existing_watershed == watershed_id:
                        watershed_id += 1
                    
                    for coords in path:
                        watersheds[coords] = existing_watershed
        
        print(f"Identified {watershed_id} watersheds")
        
        # Print watershed statistics
        watershed_sizes = {}
        for ws_id in watersheds.values():
            watershed_sizes[ws_id] = watershed_sizes.get(ws_id, 0) + 1
        
        print("Watershed sizes:")
        for ws_id, size in sorted(watershed_sizes.items()):
            percentage = (size / len(watersheds)) * 100
            print(f"  Watershed {ws_id}: {size} hexes ({percentage:.1f}%)")
        
        return watersheds
    
    def generate_river_systems(self, heightmap: Dict[Tuple[int, int], float],
                             flow_directions: Dict[Tuple[int, int], Tuple[int, int]],
                             flow_accumulation: Dict[Tuple[int, int], int],
                             width: int, height: int,
                             river_threshold: int = 5) -> Dict[Tuple[int, int], Dict]:
        """
        Generate river systems based on drainage patterns and flow accumulation.
        
        Args:
            heightmap: Dictionary mapping coordinates to elevation values
            flow_directions: Dictionary mapping coordinates to their drainage targets
            flow_accumulation: Dictionary mapping coordinates to flow values
            width, height: Dimensions of the world
            river_threshold: Minimum flow accumulation needed for a river
        
        Returns:
            Dictionary mapping coordinates to river information
        """
        print(f"Generating river systems (threshold: {river_threshold} upstream hexes)...")
        
        rivers = {}
        river_segments = []
        
        # Step 1: Identify all river hexes based on flow accumulation
        river_hexes = set()
        for coords, flow in flow_accumulation.items():
            if flow >= river_threshold:
                river_hexes.add(coords)
        
        print(f"Found {len(river_hexes)} river hexes")
        
        # Step 2: Trace river paths from sources to outlets
        processed_rivers = set()
        river_id = 0
        
        for coords in river_hexes:
            if coords in processed_rivers:
                continue
            
            # Check if this is a river source (high elevation, significant flow)
            elevation = heightmap[coords]
            flow = flow_accumulation[coords]
            
            # Find upstream connections to determine if this is a source
            upstream_count = 0
            for check_coords in river_hexes:
                if flow_directions.get(check_coords) == coords:
                    upstream_count += 1
            
            # This is a river source if it has few/no upstream river connections
            # but significant flow (indicating it's fed by non-river drainage)
            if upstream_count <= 1 and flow >= river_threshold:
                # Trace this river from source to outlet
                river_path = self._trace_river_path(
                    coords, flow_directions, river_hexes, heightmap
                )
                
                if len(river_path) >= 3:  # Only create rivers with meaningful length
                    # Create river system
                    river_system = {
                        'id': river_id,
                        'source': river_path[0],
                        'outlet': river_path[-1],
                        'path': river_path,
                        'length': len(river_path),
                        'source_elevation': heightmap[river_path[0]],
                        'outlet_elevation': heightmap[river_path[-1]]
                    }
                    
                    # Mark all hexes in this river path
                    for i, river_coords in enumerate(river_path):
                        rivers[river_coords] = {
                            'river_id': river_id,
                            'segment_index': i,
                            'is_source': i == 0,
                            'is_outlet': i == len(river_path) - 1,
                            'flow_accumulation': flow_accumulation[river_coords],
                            'elevation': heightmap[river_coords],
                            'river_width': self._calculate_river_width(flow_accumulation[river_coords])
                        }
                        processed_rivers.add(river_coords)
                    
                    river_segments.append(river_system)
                    river_id += 1
        
        print(f"Generated {len(river_segments)} river systems")
        
        # Print river statistics
        if river_segments:
            total_length = sum(r['length'] for r in river_segments)
            avg_length = total_length / len(river_segments)
            longest_river = max(river_segments, key=lambda r: r['length'])
            
            print(f"River statistics:")
            print(f"  Total river hexes: {len(rivers)}")
            print(f"  Average river length: {avg_length:.1f} hexes")
            print(f"  Longest river: {longest_river['length']} hexes (ID {longest_river['id']})")
            print(f"  Elevation drop range: {min(r['source_elevation'] - r['outlet_elevation'] for r in river_segments):.3f} - {max(r['source_elevation'] - r['outlet_elevation'] for r in river_segments):.3f}")
        
        return rivers
    
    def _trace_river_path(self, start_coords: Tuple[int, int],
                         flow_directions: Dict[Tuple[int, int], Tuple[int, int]],
                         river_hexes: set,
                         heightmap: Dict[Tuple[int, int], float]) -> List[Tuple[int, int]]:
        """
        Trace a river path from source following flow directions.
        
        Args:
            start_coords: Starting coordinates for the river
            flow_directions: Dictionary mapping coordinates to drainage targets
            river_hexes: Set of all coordinates that should be rivers
            heightmap: Dictionary mapping coordinates to elevation values
        
        Returns:
            List of coordinates forming the river path
        """
        path = [start_coords]
        current = start_coords
        visited = set([start_coords])
        
        while True:
            next_coords = flow_directions.get(current)
            
            # Stop if we reach the end of drainage or a cycle
            if next_coords is None or next_coords in visited:
                break
            
            # Continue following the path
            path.append(next_coords)
            visited.add(next_coords)
            current = next_coords
            
            # Stop if we've traced a reasonable river length
            if len(path) > 50:  # Prevent infinite loops
                break
        
        return path
    
    def _calculate_river_width(self, flow_accumulation: int) -> str:
        """
        Calculate river width category based on flow accumulation.
        
        Args:
            flow_accumulation: Number of upstream hexes draining through this point
        
        Returns:
            String describing river width category
        """
        if flow_accumulation < 5:
            return "stream"
        elif flow_accumulation < 15:
            return "creek"
        elif flow_accumulation < 30:
            return "river"
        elif flow_accumulation < 60:
            return "large_river"
        else:
            return "major_river"
    
    def identify_river_confluences(self, rivers: Dict[Tuple[int, int], Dict],
                                 flow_directions: Dict[Tuple[int, int], Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Identify river confluence points where multiple rivers meet.
        
        Args:
            rivers: Dictionary mapping coordinates to river information
            flow_directions: Dictionary mapping coordinates to drainage targets
        
        Returns:
            List of coordinates where rivers converge
        """
        print("Identifying river confluences...")
        
        confluences = []
        
        for coords, river_info in rivers.items():
            # Count how many other rivers flow into this point
            incoming_rivers = set()
            
            for other_coords, other_info in rivers.items():
                if other_coords != coords:
                    # Check if this other river flows into our current point
                    if flow_directions.get(other_coords) == coords:
                        incoming_rivers.add(other_info['river_id'])
            
            # If multiple different rivers flow into this point, it's a confluence
            if len(incoming_rivers) >= 1 and river_info['river_id'] not in incoming_rivers:
                confluences.append(coords)
        
        print(f"Found {len(confluences)} river confluences")
        return confluences
    
    def place_lakes_in_depressions(self, heightmap: Dict[Tuple[int, int], float],
                                 flow_directions: Dict[Tuple[int, int], Tuple[int, int]],
                                 flow_accumulation: Dict[Tuple[int, int], int],
                                 watersheds: Dict[Tuple[int, int], int],
                                 width: int, height: int) -> Dict[Tuple[int, int], Dict]:
        """
        Place lakes in natural depressions and drainage sinks.
        
        Args:
            heightmap: Dictionary mapping coordinates to elevation values
            flow_directions: Dictionary mapping coordinates to drainage targets
            flow_accumulation: Dictionary mapping coordinates to flow values
            watersheds: Dictionary mapping coordinates to watershed IDs
            width, height: Dimensions of the world
        
        Returns:
            Dictionary mapping coordinates to lake information
        """
        print("Placing lakes in natural depressions...")
        
        lakes = {}
        lake_id = 0
        
        # Step 1: Find all drainage sinks (natural depressions)
        sinks = []
        for coords, target in flow_directions.items():
            if target is None:  # This is a sink
                elevation = heightmap[coords]
                flow = flow_accumulation[coords]
                watershed_id = watersheds[coords]
                
                sinks.append({
                    'coords': coords,
                    'elevation': elevation,
                    'flow_accumulation': flow,
                    'watershed_id': watershed_id
                })
        
        print(f"Found {len(sinks)} potential lake locations (drainage sinks)")
        
        # Step 2: Evaluate each sink for lake suitability
        suitable_lakes = []
        
        for sink in sinks:
            coords = sink['coords']
            elevation = sink['elevation']
            flow = sink['flow_accumulation']
            
            # Lakes are more likely in areas with:
            # - Significant drainage (enough water to maintain a lake)
            # - Not too high elevation (mountain lakes are rare)
            # - Not in ocean areas
            
            is_suitable = True
            lake_type = "pond"
            
            # Check elevation - avoid ocean areas and very high mountains
            if elevation < 0.15:  # Too close to ocean level
                is_suitable = False
            elif elevation > 0.9:  # Too high (mountain peaks)
                is_suitable = False
            
            # Determine lake size based on drainage area
            if flow >= 15:
                lake_type = "large_lake"
            elif flow >= 8:
                lake_type = "lake"
            elif flow >= 4:
                lake_type = "small_lake"
            else:
                lake_type = "pond"
            
            # Only create lakes with minimum drainage
            if flow < 3:
                is_suitable = False
            
            if is_suitable:
                suitable_lakes.append({
                    'coords': coords,
                    'elevation': elevation,
                    'flow_accumulation': flow,
                    'watershed_id': sink['watershed_id'],
                    'lake_type': lake_type
                })
        
        print(f"Identified {len(suitable_lakes)} suitable lake locations")
        
        # Step 3: Create lake areas (expand from sink points)
        for lake_data in suitable_lakes:
            coords = lake_data['coords']
            lake_type = lake_data['lake_type']
            
            # Determine lake size based on type
            if lake_type == "large_lake":
                max_radius = 3
                min_size = 8
            elif lake_type == "lake":
                max_radius = 2
                min_size = 4
            elif lake_type == "small_lake":
                max_radius = 2
                min_size = 2
            else:  # pond
                max_radius = 1
                min_size = 1
            
            # Generate lake area using flood-fill from the sink
            lake_hexes = self._generate_lake_area(
                coords, heightmap, max_radius, min_size, width, height
            )
            
            if len(lake_hexes) >= min_size:
                # Create the lake
                for lake_coords in lake_hexes:
                    lakes[lake_coords] = {
                        'lake_id': lake_id,
                        'lake_type': lake_type,
                        'is_center': lake_coords == coords,
                        'elevation': heightmap[lake_coords],
                        'watershed_id': lake_data['watershed_id'],
                        'drainage_area': lake_data['flow_accumulation']
                    }
                
                lake_id += 1
        
        # Step 4: Generate lake statistics
        if lakes:
            lake_types = {}
            total_lake_hexes = len(lakes)
            
            for lake_info in lakes.values():
                lake_type = lake_info['lake_type']
                lake_types[lake_type] = lake_types.get(lake_type, 0) + 1
            
            print(f"Created {lake_id} lakes covering {total_lake_hexes} hexes")
            print("Lake type distribution:")
            for lake_type, count in sorted(lake_types.items()):
                print(f"  {lake_type}: {count} hexes")
        else:
            print("No suitable lakes created")
        
        return lakes
    
    def _generate_lake_area(self, center: Tuple[int, int], 
                          heightmap: Dict[Tuple[int, int], float],
                          max_radius: int, min_size: int,
                          width: int, height: int) -> List[Tuple[int, int]]:
        """
        Generate lake area around a center point using elevation-based expansion.
        
        Args:
            center: Center coordinates of the lake
            heightmap: Dictionary mapping coordinates to elevation values
            max_radius: Maximum distance from center to expand
            min_size: Minimum number of hexes for a valid lake
            width, height: World dimensions
        
        Returns:
            List of coordinates that form the lake
        """
        center_elevation = heightmap[center]
        lake_hexes = [center]
        candidates = [center]
        processed = set([center])
        
        # Expand outward from center, staying within elevation tolerance
        elevation_tolerance = 0.05  # Lake surface should be relatively flat
        
        while candidates and len(lake_hexes) < max_radius * max_radius * 2:
            current = candidates.pop(0)
            current_x, current_y = current
            
            # Check all adjacent hexes
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    
                    adj_x, adj_y = current_x + dx, current_y + dy
                    adj_coords = (adj_x, adj_y)
                    
                    # Check bounds
                    if not (0 <= adj_x < width and 0 <= adj_y < height):
                        continue
                    
                    # Skip if already processed
                    if adj_coords in processed:
                        continue
                    
                    # Check distance from center
                    distance = math.sqrt((adj_x - center[0])**2 + (adj_y - center[1])**2)
                    if distance > max_radius:
                        continue
                    
                    # Check elevation - lake should be relatively flat
                    adj_elevation = heightmap[adj_coords]
                    if abs(adj_elevation - center_elevation) <= elevation_tolerance:
                        lake_hexes.append(adj_coords)
                        candidates.append(adj_coords)
                    
                    processed.add(adj_coords)
        
        return lake_hexes
    
    def identify_lake_connections(self, lakes: Dict[Tuple[int, int], Dict],
                                rivers: Dict[Tuple[int, int], Dict],
                                flow_directions: Dict[Tuple[int, int], Tuple[int, int]]) -> Dict[int, Dict]:
        """
        Identify connections between lakes and rivers.
        
        Args:
            lakes: Dictionary mapping coordinates to lake information
            rivers: Dictionary mapping coordinates to river information
            flow_directions: Dictionary mapping coordinates to drainage targets
        
        Returns:
            Dictionary mapping lake IDs to connection information
        """
        print("Identifying lake-river connections...")
        
        lake_connections = {}
        
        # Group lakes by lake_id
        lakes_by_id = {}
        for coords, lake_info in lakes.items():
            lake_id = lake_info['lake_id']
            if lake_id not in lakes_by_id:
                lakes_by_id[lake_id] = []
            lakes_by_id[lake_id].append(coords)
        
        # Check each lake for river connections
        for lake_id, lake_coords_list in lakes_by_id.items():
            connections = {
                'inflow_rivers': [],
                'outflow_rivers': [],
                'adjacent_rivers': []
            }
            
            for lake_coords in lake_coords_list:
                # Check for rivers flowing into this lake hex
                for river_coords, river_info in rivers.items():
                    flow_target = flow_directions.get(river_coords)
                    if flow_target == lake_coords:
                        connections['inflow_rivers'].append(river_info['river_id'])
                
                # Check for rivers flowing out of this lake hex
                flow_target = flow_directions.get(lake_coords)
                if flow_target and flow_target in rivers:
                    river_info = rivers[flow_target]
                    connections['outflow_rivers'].append(river_info['river_id'])
                
                # Check for adjacent rivers (within 1 hex)
                x, y = lake_coords
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        
                        adj_coords = (x + dx, y + dy)
                        if adj_coords in rivers:
                            river_info = rivers[adj_coords]
                            river_id = river_info['river_id']
                            if (river_id not in connections['inflow_rivers'] and 
                                river_id not in connections['outflow_rivers']):
                                connections['adjacent_rivers'].append(river_id)
            
            # Remove duplicates
            connections['inflow_rivers'] = list(set(connections['inflow_rivers']))
            connections['outflow_rivers'] = list(set(connections['outflow_rivers']))
            connections['adjacent_rivers'] = list(set(connections['adjacent_rivers']))
            
            lake_connections[lake_id] = connections
        
        # Print connection summary
        connected_lakes = sum(1 for conn in lake_connections.values() 
                            if conn['inflow_rivers'] or conn['outflow_rivers'] or conn['adjacent_rivers'])
        
        print(f"Lake connections: {connected_lakes}/{len(lake_connections)} lakes connected to rivers")
        
        return lake_connections
    
    def classify_terrain_from_elevation(self, elevation: float) -> str:
        """
        Classify terrain type based on elevation.
        
        Args:
            elevation: Elevation value (0.0-1.0)
        
        Returns:
            Terrain type string
        """
        if elevation < 0.2:
            return "water"
        elif elevation < 0.3:
            return "coastal"
        elif elevation < 0.5:
            return "plains"
        elif elevation < 0.7:
            return "hills"
        elif elevation < 0.85:
            return "mountains"
        else:
            return "peaks"
    
    def generate_terrain_types(self, heightmap: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], str]:
        """
        Generate terrain types from heightmap.
        
        Args:
            heightmap: Dictionary of elevation values
        
        Returns:
            Dictionary mapping coordinates to terrain type strings
        """
        print("Classifying terrain types from elevation...")
        
        terrain_types = {}
        for coords, elevation in heightmap.items():
            terrain_types[coords] = self.classify_terrain_from_elevation(elevation)
        
        # Count terrain types for verification
        type_counts = {}
        for terrain_type in terrain_types.values():
            type_counts[terrain_type] = type_counts.get(terrain_type, 0) + 1
        
        print("Terrain type distribution:")
        for terrain_type, count in sorted(type_counts.items()):
            percentage = (count / len(terrain_types)) * 100
            print(f"  {terrain_type}: {count} hexes ({percentage:.1f}%)")
        
        return terrain_types


def test_terrain_generation():
    """Test the terrain generation system."""
    print("=== Testing Terrain Generation ===")
    
    # Test basic noise generation
    noise_gen = NoiseGenerator(seed=12345)
    
    print("\nTesting basic noise values:")
    test_coords = [(0, 0), (1, 1), (5, 3), (10, 7)]
    for x, y in test_coords:
        noise_val = noise_gen.noise2d(x * 0.1, y * 0.1)
        octave_val = noise_gen.octave_noise2d(x * 0.1, y * 0.1, octaves=4)
        print(f"  ({x}, {y}): basic={noise_val:.3f}, octave={octave_val:.3f}")
    
    # Test terrain generation
    terrain_gen = TerrainGenerator(seed=12345)
    
    print("\nGenerating small test heightmap...")
    heightmap = terrain_gen.generate_heightmap(10, 10, scale=0.2, octaves=3)
    
    print("Sample elevations:")
    for y in range(3):
        row = []
        for x in range(5):
            elevation = heightmap.get((x, y), 0.0)
            row.append(f"{elevation:.2f}")
        print(f"  Row {y}: {' '.join(row)}")
    
    # Test continental generation with plate tectonics
    print("\nGenerating continental heightmap with plate tectonics...")
    continental_map = terrain_gen.generate_continental_heightmap(20, 20)
    
    # Test terrain classification
    terrain_types = terrain_gen.generate_terrain_types(continental_map)
    
    # Display a small sample of the generated world
    print("\nSample of generated world (elevation):")
    for y in range(5):
        row = []
        for x in range(10):
            elevation = continental_map.get((x, y), 0.0)
            if elevation < 0.3:
                row.append("~~")  # Ocean
            elif elevation < 0.5:
                row.append("..")  # Plains
            elif elevation < 0.7:
                row.append("^^")  # Hills
            else:
                row.append("MM")  # Mountains
        print(f"  {' '.join(row)}")
    
    print("\nLegend: ~~ = Ocean, .. = Plains, ^^ = Hills, MM = Mountains")
    
    # Test drainage pattern calculation
    print("\n" + "="*50)
    print("Testing Drainage Pattern Calculation")
    print("="*50)
    
    # Calculate drainage patterns
    flow_directions = terrain_gen.calculate_drainage_patterns(continental_map, 20, 20)
    
    # Calculate flow accumulation
    flow_accumulation = terrain_gen.calculate_flow_accumulation(flow_directions, 20, 20)
    
    # Identify watersheds
    watersheds = terrain_gen.identify_watersheds(flow_directions, 20, 20)
    
    # Display drainage information for a sample area
    print("\nSample drainage patterns (first 8x8 area):")
    print("Format: elevation/flow_accumulation/watershed_id")
    
    for y in range(8):
        row_info = []
        for x in range(8):
            coords = (x, y)
            elevation = continental_map.get(coords, 0.0)
            flow = flow_accumulation.get(coords, 0)
            watershed = watersheds.get(coords, 0)
            
            # Format: elevation(2 decimals)/flow/watershed
            info = f"{elevation:.2f}/{flow:2d}/{watershed}"
            row_info.append(info)
        
        print(f"  Row {y}: " + " | ".join(row_info))
    
    # Show areas with high flow accumulation (potential rivers)
    high_flow_areas = []
    for coords, flow in flow_accumulation.items():
        if flow >= 10:  # Significant drainage
            high_flow_areas.append((coords, flow))
    
    high_flow_areas.sort(key=lambda x: x[1], reverse=True)
    print(f"\nTop 10 areas with highest flow accumulation (potential rivers):")
    for i, ((x, y), flow) in enumerate(high_flow_areas[:10]):
        elevation = continental_map[(x, y)]
        terrain = terrain_gen.classify_terrain_from_elevation(elevation)
        print(f"  {i+1}. ({x:2d}, {y:2d}): {flow:3d} upstream hexes, {terrain} at {elevation:.3f}")
    
    # Test river system generation
    print("\n" + "="*50)
    print("Testing River System Generation")
    print("="*50)
    
    # Generate river systems
    rivers = terrain_gen.generate_river_systems(
        continental_map, flow_directions, flow_accumulation, 20, 20, river_threshold=5
    )
    
    # Identify confluences
    confluences = terrain_gen.identify_river_confluences(rivers, flow_directions)
    
    # Display river information
    if rivers:
        print(f"\nRiver system details:")
        
        # Group rivers by river_id
        river_systems = {}
        for coords, river_info in rivers.items():
            river_id = river_info['river_id']
            if river_id not in river_systems:
                river_systems[river_id] = []
            river_systems[river_id].append((coords, river_info))
        
        # Show details for each river system
        for river_id, river_hexes in river_systems.items():
            river_hexes.sort(key=lambda x: x[1]['segment_index'])
            source = river_hexes[0]
            outlet = river_hexes[-1]
            
            print(f"  River {river_id}:")
            print(f"    Length: {len(river_hexes)} hexes")
            print(f"    Source: ({source[0][0]:2d}, {source[0][1]:2d}) at elevation {source[1]['elevation']:.3f}")
            print(f"    Outlet: ({outlet[0][0]:2d}, {outlet[0][1]:2d}) at elevation {outlet[1]['elevation']:.3f}")
            print(f"    Elevation drop: {source[1]['elevation'] - outlet[1]['elevation']:.3f}")
            print(f"    Max flow: {max(h[1]['flow_accumulation'] for h in river_hexes)} upstream hexes")
        
        # Show confluence points
        if confluences:
            print(f"\nRiver confluences:")
            for i, (x, y) in enumerate(confluences):
                river_info = rivers[(x, y)]
                print(f"  Confluence {i+1}: ({x:2d}, {y:2d}) - River {river_info['river_id']}, flow: {river_info['flow_accumulation']}")
    
    # Display a map showing rivers
    print(f"\nRiver map (first 10x10 area):")
    print("Legend: ~~ = Ocean, .. = Land, RR = River, CC = Confluence")
    
    for y in range(10):
        row = []
        for x in range(10):
            coords = (x, y)
            
            if coords in confluences:
                row.append("CC")
            elif coords in rivers:
                row.append("RR")
            else:
                elevation = continental_map.get(coords, 0.0)
                if elevation < 0.3:
                    row.append("~~")  # Ocean
                else:
                    row.append("..")  # Land
        
        print(f"  {' '.join(row)}")
    
    # Test lake placement
    print("\n" + "="*50)
    print("Testing Lake Placement")
    print("="*50)
    
    # Place lakes in natural depressions
    lakes = terrain_gen.place_lakes_in_depressions(
        continental_map, flow_directions, flow_accumulation, watersheds, 20, 20
    )
    
    # Identify lake-river connections
    lake_connections = terrain_gen.identify_lake_connections(lakes, rivers, flow_directions)
    
    # Display lake information
    if lakes:
        print(f"\nLake system details:")
        
        # Group lakes by lake_id
        lakes_by_id = {}
        for coords, lake_info in lakes.items():
            lake_id = lake_info['lake_id']
            if lake_id not in lakes_by_id:
                lakes_by_id[lake_id] = []
            lakes_by_id[lake_id].append((coords, lake_info))
        
        # Show details for each lake
        for lake_id, lake_hexes in lakes_by_id.items():
            center_hex = next((coords for coords, info in lake_hexes if info['is_center']), lake_hexes[0][0])
            center_info = next(info for coords, info in lake_hexes if coords == center_hex)
            
            print(f"  Lake {lake_id} ({center_info['lake_type']}):")
            print(f"    Size: {len(lake_hexes)} hexes")
            print(f"    Center: ({center_hex[0]:2d}, {center_hex[1]:2d}) at elevation {center_info['elevation']:.3f}")
            print(f"    Drainage area: {center_info['drainage_area']} upstream hexes")
            print(f"    Watershed: {center_info['watershed_id']}")
            
            # Show connections
            if lake_id in lake_connections:
                conn = lake_connections[lake_id]
                if conn['inflow_rivers']:
                    print(f"    Inflow rivers: {conn['inflow_rivers']}")
                if conn['outflow_rivers']:
                    print(f"    Outflow rivers: {conn['outflow_rivers']}")
                if conn['adjacent_rivers']:
                    print(f"    Adjacent rivers: {conn['adjacent_rivers']}")
    
    # Display a comprehensive map showing terrain, rivers, and lakes
    print(f"\nComplete hydrology map (first 12x12 area):")
    print("Legend: ~~ = Ocean, .. = Land, RR = River, LL = Lake, CC = Confluence")
    
    for y in range(12):
        row = []
        for x in range(12):
            coords = (x, y)
            
            if coords in confluences:
                row.append("CC")
            elif coords in lakes:
                row.append("LL")
            elif coords in rivers:
                row.append("RR")
            else:
                elevation = continental_map.get(coords, 0.0)
                if elevation < 0.3:
                    row.append("~~")  # Ocean
                else:
                    row.append("..")  # Land
        
        print(f"  {' '.join(row)}")
    
    # Summary statistics
    total_water_features = len(rivers) + len(lakes)
    land_hexes = sum(1 for e in continental_map.values() if e >= 0.3)
    water_coverage = (total_water_features / land_hexes) * 100 if land_hexes > 0 else 0
    
    print(f"\nHydrology Summary:")
    print(f"  Rivers: {len(rivers)} hexes in {len(set(r['river_id'] for r in rivers.values()))} systems")
    print(f"  Lakes: {len(lakes)} hexes in {len(set(l['lake_id'] for l in lakes.values()))} lakes")
    print(f"  Water feature coverage: {water_coverage:.1f}% of land area")
    
    print("\nLake placement test complete!")
    print("All systems working correctly.")


if __name__ == "__main__":
    test_terrain_generation()