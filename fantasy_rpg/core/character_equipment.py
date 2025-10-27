"""
Fantasy RPG - Character Equipment System

Handles pool-based equipment generation for character creation.
"""

import random
from typing import List, Dict, Any, Optional

try:
    from .item import ItemLoader, Item
except ImportError:
    # Handle running directly from core directory
    from item import ItemLoader, Item


class EquipmentGenerator:
    """Generates equipment from pools for character creation"""
    
    def __init__(self, seed: int = None):
        self.rng = random.Random(seed)
        self.item_loader = ItemLoader()
    
    def generate_from_pools(self, pool_config: Dict[str, Any]) -> List[Item]:
        """Generate equipment from pool configuration"""
        equipment = []
        
        # Handle guaranteed equipment
        if "guaranteed" in pool_config:
            for guaranteed_config in pool_config["guaranteed"]:
                equipment.extend(self._generate_from_pool_entry(guaranteed_config))
        
        # Handle optional equipment
        if "optional" in pool_config:
            for optional_config in pool_config["optional"]:
                equipment.extend(self._generate_from_pool_entry(optional_config))
        
        return equipment
    
    def _generate_from_pool_entry(self, config: Dict[str, Any]) -> List[Item]:
        """Generate items from a single pool entry"""
        pools = config.get("pools", [])
        min_items = config.get("min", 1)
        max_items = config.get("max", 1)
        item_filter = config.get("filter")  # Specific item ID to guarantee
        
        if not pools:
            return []
        
        # Get all items from the specified pools
        available_items = self.item_loader.get_items_by_pools(pools)
        
        if not available_items:
            print(f"Warning: No items found in pools {pools}")
            return []
        
        # If filter specified, try to get that specific item first
        selected_items = []
        if item_filter:
            filtered_item = self.item_loader.get_item(item_filter)
            if filtered_item and any(pool in (filtered_item.pools or []) for pool in pools):
                selected_items.append(filtered_item)
                min_items = max(0, min_items - 1)  # Reduce remaining items needed
                max_items = max(0, max_items - 1)
        
        # Generate remaining items randomly
        if max_items > 0:
            num_items = self.rng.randint(min_items, max_items)
            for _ in range(num_items):
                # Weighted selection based on drop_weight
                total_weight = sum(item.drop_weight for item in available_items)
                if total_weight == 0:
                    continue
                
                roll = self.rng.randint(1, total_weight)
                current = 0
                
                for item in available_items:
                    current += item.drop_weight
                    if roll <= current:
                        selected_items.append(item)
                        break
        
        return selected_items
    
    def generate_class_equipment(self, class_data: Dict[str, Any]) -> List[Item]:
        """Generate starting equipment for a class"""
        equipment_pools = class_data.get("starting_equipment_pools", {})
        return self.generate_from_pools(equipment_pools)
    
    def generate_background_equipment(self, background_data: Dict[str, Any]) -> List[Item]:
        """Generate starting equipment for a background"""
        # Try new pool system first
        if "equipment_pools" in background_data:
            return self.generate_from_pools(background_data["equipment_pools"])
        
        # Fallback to legacy equipment list
        equipment = []
        for item_entry in background_data.get("equipment", []):
            item_id = item_entry.get("item")
            quantity = item_entry.get("quantity", 1)
            
            item = self.item_loader.get_item(item_id)
            if item:
                for _ in range(quantity):
                    equipment.append(item)
            else:
                print(f"Warning: Item '{item_id}' not found for background equipment")
        
        return equipment
    
    def generate_racial_equipment(self, race_data: Dict[str, Any]) -> List[Item]:
        """Generate bonus equipment for a race"""
        equipment_bonuses = race_data.get("equipment_bonuses")
        if not equipment_bonuses:
            return []
        
        pools = equipment_bonuses.get("pools", [])
        min_items = equipment_bonuses.get("min", 0)
        max_items = equipment_bonuses.get("max", 1)
        
        if not pools:
            return []
        
        config = {
            "guaranteed": [{
                "pools": pools,
                "min": min_items,
                "max": max_items
            }]
        }
        
        return self.generate_from_pools(config)


def create_character_equipment(class_data: Dict[str, Any], 
                             background_data: Dict[str, Any], 
                             race_data: Dict[str, Any],
                             seed: int = None) -> Dict[str, List[Item]]:
    """Create complete starting equipment for a character"""
    generator = EquipmentGenerator(seed)
    
    equipment = {
        "class": generator.generate_class_equipment(class_data),
        "background": generator.generate_background_equipment(background_data),
        "racial": generator.generate_racial_equipment(race_data)
    }
    
    # Combine all equipment
    all_equipment = []
    for source, items in equipment.items():
        all_equipment.extend(items)
        if items:
            print(f"{source.title()} equipment: {[item.name for item in items]}")
    
    equipment["all"] = all_equipment
    return equipment


def test_equipment_generation():
    """Test the equipment generation system"""
    print("=== Testing Equipment Generation ===")
    
    # Mock class data
    class_data = {
        "starting_equipment_pools": {
            "guaranteed": [
                {"pools": ["armor", "fighter_gear"], "min": 1, "max": 1, "filter": "chain_mail"},
                {"pools": ["weapons", "melee"], "min": 1, "max": 1, "filter": "longsword"}
            ],
            "optional": [
                {"pools": ["fighter_gear", "weapons"], "min": 1, "max": 2}
            ]
        }
    }
    
    # Mock background data
    background_data = {
        "equipment_pools": {
            "guaranteed": [
                {"pools": ["military", "soldier_gear"], "min": 2, "max": 4}
            ]
        }
    }
    
    # Mock race data
    race_data = {
        "equipment_bonuses": {
            "pools": ["human_gear", "versatile", "starting_gear"],
            "min": 1,
            "max": 2
        }
    }
    
    # Generate equipment
    equipment = create_character_equipment(class_data, background_data, race_data, seed=12345)
    
    print(f"\nTotal equipment generated: {len(equipment['all'])} items")
    for item in equipment["all"]:
        print(f"  • {item.name} ({item.item_type}) - ${item.value}")
    
    print("✓ Equipment generation test complete!")
    return equipment


if __name__ == "__main__":
    test_equipment_generation()