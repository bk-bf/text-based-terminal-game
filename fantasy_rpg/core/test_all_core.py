#!/usr/bin/env python3
"""
Fantasy RPG - Core System Test Runner

Tests all core Python files to ensure they work with the new pool-based JSON system.
"""

import sys
import os
import traceback
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def test_module(module_name: str, test_function_name: str = None):
    """Test a specific module and its test function"""
    print(f"\n{'='*60}")
    print(f"TESTING: {module_name}")
    print(f"{'='*60}")
    
    try:
        # Import the module
        module = __import__(module_name)
        
        # Try to find and run the test function
        if test_function_name:
            if hasattr(module, test_function_name):
                test_function = getattr(module, test_function_name)
                print(f"Running {test_function_name}()...")
                result = test_function()
                print(f"✅ {module_name} - {test_function_name}() completed successfully")
                return True, result
            else:
                print(f"⚠️  {module_name} - No {test_function_name}() function found")
                return True, None
        else:
            # Just test import
            print(f"✅ {module_name} - Import successful")
            return True, None
            
    except Exception as e:
        print(f"❌ {module_name} - Error: {e}")
        print(f"Traceback:")
        traceback.print_exc()
        return False, None

def test_all_core_modules():
    """Test all core modules"""
    print("🧪 Fantasy RPG - Core System Test Suite")
    print("=" * 60)
    
    # Define modules to test with their test functions
    modules_to_test = [
        ("item", "test_item_system"),
        ("race", "test_race_system"),
        ("backgrounds", "test_background_system"),
        ("character_equipment", "test_equipment_generation"),
    ]
    
    # Additional modules to test (import only)
    import_only_modules = [
        "character",
        "character_class",
        "inventory",
    ]
    
    results = {}
    
    # Test modules with test functions
    print("\n🔧 Testing Core Modules with Test Functions:")
    for module_name, test_func in modules_to_test:
        success, result = test_module(module_name, test_func)
        results[module_name] = {"success": success, "result": result, "type": "full_test"}
    
    # Test import-only modules
    print(f"\n📦 Testing Module Imports:")
    for module_name in import_only_modules:
        success, result = test_module(module_name)
        results[module_name] = {"success": success, "result": result, "type": "import_only"}
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    successful = 0
    failed = 0
    
    for module_name, result_data in results.items():
        status = "✅ PASS" if result_data["success"] else "❌ FAIL"
        test_type = result_data["type"]
        print(f"{status} - {module_name} ({test_type})")
        
        if result_data["success"]:
            successful += 1
        else:
            failed += 1
    
    print(f"\nResults: {successful} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All core modules are working correctly!")
    else:
        print(f"⚠️  {failed} module(s) need attention")
    
    return results

def test_integration():
    """Test integration between modules"""
    print(f"\n{'='*60}")
    print("INTEGRATION TESTS")
    print(f"{'='*60}")
    
    try:
        print("\n🔗 Testing Item System Integration...")
        from item import ItemLoader, Item
        
        loader = ItemLoader()
        items = loader.load_items()
        print(f"✅ Loaded {len(items)} items from JSON")
        
        # Test pool functionality
        if items:
            # Find an item with pools
            pooled_items = [item for item in items.values() if item.pools]
            if pooled_items:
                test_item = pooled_items[0]
                print(f"✅ Found item with pools: {test_item.name} - pools: {test_item.pools}")
                
                # Test getting items by pool
                if test_item.pools:
                    pool_items = loader.get_items_by_pool(test_item.pools[0])
                    print(f"✅ Found {len(pool_items)} items in pool '{test_item.pools[0]}'")
        
        print("\n🔗 Testing Equipment Generation Integration...")
        from character_equipment import EquipmentGenerator
        
        generator = EquipmentGenerator(seed=12345)
        
        # Test class equipment generation
        mock_class = {
            "starting_equipment_pools": {
                "guaranteed": [
                    {"pools": ["weapons", "melee"], "min": 1, "max": 1}
                ]
            }
        }
        
        equipment = generator.generate_class_equipment(mock_class)
        print(f"✅ Generated {len(equipment)} class equipment items")
        
        print("\n🔗 Testing Race/Background Integration...")
        from race import RaceLoader
        from backgrounds import BackgroundLoader
        
        race_loader = RaceLoader()
        bg_loader = BackgroundLoader()
        
        races = race_loader.load_races()
        backgrounds = bg_loader.load_backgrounds()
        
        print(f"✅ Loaded {len(races)} races and {len(backgrounds)} backgrounds")
        
        # Test new pool-based structure
        for race_name, race in races.items():
            if hasattr(race, 'equipment_bonuses') and race.equipment_bonuses:
                print(f"✅ {race.name} has equipment bonuses: {race.equipment_bonuses.get('pools', [])}")
                break
        
        for bg_name, bg in backgrounds.items():
            if hasattr(bg, 'equipment_pools') and bg.equipment_pools:
                print(f"✅ {bg.name} has equipment pools")
                break
        
        print("✅ Integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test runner"""
    print("Starting Fantasy RPG Core System Tests...")
    
    # Test individual modules
    module_results = test_all_core_modules()
    
    # Test integration
    integration_success = test_integration()
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")
    
    module_success_count = sum(1 for r in module_results.values() if r["success"])
    module_total = len(module_results)
    
    print(f"Module Tests: {module_success_count}/{module_total} passed")
    print(f"Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    
    if module_success_count == module_total and integration_success:
        print("\n🎉 ALL TESTS PASSED! Core system is ready for use.")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)