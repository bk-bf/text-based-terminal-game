#!/usr/bin/env python3
"""
Simple test to verify the pool-based location system works
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_pool_system():
    """Test the pool-based location generation"""
    print("🧪 Testing Pool-Based Location System")
    print("=" * 50)
    
    try:
        from locations.location_generator import LocationGenerator
        
        # Create generator
        generator = LocationGenerator(seed=12345)
        
        print(f"✅ Generator created successfully")
        print(f"📦 Object pools: {list(generator.object_pools.keys())}")
        print(f"👥 Entity pools: {list(generator.entity_pools.keys())}")
        print()
        
        # Test location generation
        print("🏗️ Testing Location Generation...")
        locations = generator.generate_locations_for_hex((10, 10), "temperate_forest", "dense_forest")
        
        print(f"📍 Generated {len(locations)} location(s):")
        
        for i, location in enumerate(locations, 1):
            exit_status = "[EXIT]" if location.exit_flag else "[NO EXIT]"
            print(f"\n  [{i}] {location.name} ({location.type.value}) {exit_status}")
            
            # Show area details
            if location.areas:
                area = list(location.areas.values())[0]
                print(f"  📝 Description: {area.description}")
                print(f"  🪑 Objects: {len(area.objects)}")
                
                # Show objects
                for obj in area.objects:
                    print(f"    • {obj.name} - {obj.description[:50]}...")
                
                print(f"  👥 Entities: {len(area.entities)}")
                
                # Show entities
                for entity in area.entities:
                    hostile = "[Hostile]" if entity.hostile else "[Peaceful]"
                    print(f"    • {entity.name} {hostile} - {entity.description[:50]}...")
        
        print("\n✅ Pool system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pool_system()