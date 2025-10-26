"""
Fantasy RPG - Utility Classes

Utility classes for dice rolling, coordinates, and other common functionality.
"""

import random
from dataclasses import dataclass
from typing import Tuple


class Dice:
    """
    Dice rolling utility with seeded random number generation.
    
    Provides D&D-style dice rolling functionality with deterministic
    results when using seeded random number generators.
    """
    
    def __init__(self, seed: int = None):
        """Initialize dice roller with optional seed for deterministic results."""
        if seed is not None:
            self.rng = random.Random(seed)
        else:
            self.rng = random.Random()
    
    def roll(self, sides: int, count: int = 1, modifier: int = 0) -> int:
        """
        Roll dice and return the total.
        
        Args:
            sides: Number of sides on each die
            count: Number of dice to roll
            modifier: Modifier to add to the total
        
        Returns:
            Total of all dice rolls plus modifier
        """
        if sides < 1 or count < 1:
            return modifier
        
        total = sum(self.rng.randint(1, sides) for _ in range(count))
        result = total + modifier
        
        print(f"Rolled {count}d{sides}{modifier:+d}: {total}{modifier:+d} = {result}")
        return result
    
    def d4(self, count: int = 1, modifier: int = 0) -> int:
        """Roll d4 dice."""
        return self.roll(4, count, modifier)
    
    def d6(self, count: int = 1, modifier: int = 0) -> int:
        """Roll d6 dice."""
        return self.roll(6, count, modifier)
    
    def d8(self, count: int = 1, modifier: int = 0) -> int:
        """Roll d8 dice."""
        return self.roll(8, count, modifier)
    
    def d10(self, count: int = 1, modifier: int = 0) -> int:
        """Roll d10 dice."""
        return self.roll(10, count, modifier)
    
    def d12(self, count: int = 1, modifier: int = 0) -> int:
        """Roll d12 dice."""
        return self.roll(12, count, modifier)
    
    def d20(self, count: int = 1, modifier: int = 0) -> int:
        """Roll d20 dice."""
        return self.roll(20, count, modifier)
    
    def d100(self, count: int = 1, modifier: int = 0) -> int:
        """Roll d100 (percentile) dice."""
        return self.roll(100, count, modifier)
    
    def parse_dice_string(self, dice_string: str, modifier: int = 0) -> int:
        """
        Parse and roll dice from string format like '2d6', '1d8+3', etc.
        
        Args:
            dice_string: String in format 'XdY' or 'XdY+Z'
            modifier: Additional modifier to add
        
        Returns:
            Total of dice roll plus modifiers
        """
        dice_string = dice_string.lower().strip()
        
        # Handle modifier in the string
        if '+' in dice_string:
            dice_part, mod_part = dice_string.split('+', 1)
            modifier += int(mod_part)
        elif '-' in dice_string:
            dice_part, mod_part = dice_string.split('-', 1)
            modifier -= int(mod_part)
        else:
            dice_part = dice_string
        
        # Parse dice notation
        if 'd' not in dice_part:
            # Just a number
            return int(dice_part) + modifier
        
        count_str, sides_str = dice_part.split('d', 1)
        count = int(count_str) if count_str else 1
        sides = int(sides_str)
        
        return self.roll(sides, count, modifier)


@dataclass
class Coordinates:
    """
    Coordinate utility class for hex grid navigation.
    
    Provides coordinate manipulation and distance calculation
    for the hex-based world map system.
    """
    x: int
    y: int
    
    def __post_init__(self):
        """Ensure coordinates are integers."""
        self.x = int(self.x)
        self.y = int(self.y)
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to tuple format."""
        return (self.x, self.y)
    
    def distance_to(self, other: 'Coordinates') -> int:
        """
        Calculate hex distance to another coordinate.
        
        Uses hex grid distance calculation which is different
        from standard Euclidean distance.
        """
        dx = abs(self.x - other.x)
        dy = abs(self.y - other.y)
        
        # Hex distance calculation
        if (self.x % 2) == (other.x % 2):
            # Same column parity
            return max(dx, dy)
        else:
            # Different column parity
            return max(dx, dy + (dx + 1) // 2)
    
    def neighbors(self) -> list['Coordinates']:
        """Get all 6 neighboring hex coordinates."""
        # Hex grid neighbors depend on whether we're in an even or odd column
        if self.x % 2 == 0:  # Even column
            offsets = [
                (0, -1),   # North
                (1, -1),   # Northeast
                (1, 0),    # Southeast
                (0, 1),    # South
                (-1, 0),   # Southwest
                (-1, -1)   # Northwest
            ]
        else:  # Odd column
            offsets = [
                (0, -1),   # North
                (1, 0),    # Northeast
                (1, 1),    # Southeast
                (0, 1),    # South
                (-1, 1),   # Southwest
                (-1, 0)    # Northwest
            ]
        
        neighbors = []
        for dx, dy in offsets:
            neighbors.append(Coordinates(self.x + dx, self.y + dy))
        
        return neighbors
    
    def move(self, direction: str) -> 'Coordinates':
        """
        Move in a cardinal direction and return new coordinates.
        
        Args:
            direction: 'north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest'
        
        Returns:
            New Coordinates object
        """
        direction = direction.lower()
        
        # Basic cardinal directions
        if direction in ['north', 'n']:
            return Coordinates(self.x, self.y - 1)
        elif direction in ['south', 's']:
            return Coordinates(self.x, self.y + 1)
        elif direction in ['east', 'e']:
            return Coordinates(self.x + 1, self.y)
        elif direction in ['west', 'w']:
            return Coordinates(self.x - 1, self.y)
        
        # Hex diagonal directions
        neighbors = self.neighbors()
        direction_map = {
            'northeast': 1, 'ne': 1,
            'southeast': 2, 'se': 2,
            'southwest': 4, 'sw': 4,
            'northwest': 5, 'nw': 5
        }
        
        if direction in direction_map:
            return neighbors[direction_map[direction]]
        
        # If direction not recognized, return current position
        print(f"Warning: Unknown direction '{direction}', staying in place")
        return Coordinates(self.x, self.y)
    
    def __str__(self) -> str:
        """String representation of coordinates."""
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another Coordinates object."""
        if not isinstance(other, Coordinates):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        """Make coordinates hashable for use as dictionary keys."""
        return hash((self.x, self.y))


# Manual testing function
def test_utilities():
    """Test dice rolling and coordinate utilities."""
    print("=== Testing Utility Classes ===")
    
    # Test dice rolling
    print("\n1. Testing dice rolling:")
    dice = Dice(seed=12345)  # Seeded for consistent results
    
    print("Basic dice rolls:")
    dice.d6()
    dice.d20()
    dice.roll(8, 2, 3)  # 2d8+3
    
    print("\nDice string parsing:")
    dice.parse_dice_string("1d8")
    dice.parse_dice_string("2d6+3")
    dice.parse_dice_string("1d20-1")
    
    # Test with same seed for deterministic results
    print("\nTesting deterministic results:")
    dice1 = Dice(seed=42)
    dice2 = Dice(seed=42)
    roll1 = dice1.d20()
    roll2 = dice2.d20()
    print(f"Same seed results: {roll1} == {roll2} ? {roll1 == roll2}")
    
    # Test coordinates
    print("\n2. Testing coordinates:")
    coord1 = Coordinates(5, 10)
    coord2 = Coordinates(7, 12)
    
    print(f"Coord1: {coord1}")
    print(f"Coord2: {coord2}")
    print(f"Distance: {coord1.distance_to(coord2)}")
    print(f"As tuple: {coord1.to_tuple()}")
    
    # Test movement
    print("\nTesting movement:")
    start = Coordinates(0, 0)
    print(f"Start: {start}")
    
    north = start.move("north")
    print(f"Move north: {north}")
    
    east = start.move("east")
    print(f"Move east: {east}")
    
    northeast = start.move("northeast")
    print(f"Move northeast: {northeast}")
    
    # Test neighbors
    print(f"\nNeighbors of {start}:")
    for i, neighbor in enumerate(start.neighbors()):
        print(f"  {i}: {neighbor}")
    
    print("✓ All utility tests completed!")


if __name__ == "__main__":
    test_utilities()