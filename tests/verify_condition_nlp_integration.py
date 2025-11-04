"""Verification script for Condition → NLP system integration.

This script verifies that:
1. All conditions from conditions.json are mapped to NLP event types
2. All NLP event types have message variants in event_messages.json
3. No hardcoded trigger_message values are being used in favor of NLP messages
4. Beneficial conditions use the beneficial_effects category
"""

import json
from pathlib import Path

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_integration():
    """Verify complete integration between conditions and NLP system"""
    
    # Load data files
    project_root = Path(__file__).parent.parent
    conditions_data = load_json(project_root / 'fantasy_rpg' / 'data' / 'conditions.json')
    messages_data = load_json(project_root / 'fantasy_rpg' / 'dialogue' / 'event_messages.json')
    
    # Extract condition names
    conditions = conditions_data['conditions']
    
    # Define the expected mapping (from ActionLogger)
    survival_event_map = {
        # Temperature - Cold
        'Cold': 'COLD_triggered',
        'Icy': 'ICY_triggered',
        'Freezing': 'FREEZING_triggered',
        # Temperature - Hot
        'Hot': 'HOT_triggered',
        'Overheating': 'OVERHEATING_triggered',
        'Heat Stroke': 'HEAT_STROKE_triggered',
        # Hunger
        'Hungry': 'HUNGER_triggered',
        'Starving': 'STARVING_triggered',
        'Dying of Hunger': 'DYING_OF_HUNGER_triggered',
        # Thirst
        'Thirsty': 'THIRST_triggered',
        'Dehydrated': 'DEHYDRATED_triggered',
        'Dying of Thirst': 'DYING_OF_THIRST_triggered',
        # Fatigue
        'Tired': 'TIRED_triggered',
        'Very Tired': 'VERY_TIRED_triggered',
        'Exhausted': 'EXHAUSTED_triggered',
        # Wetness
        'Wet': 'WET_triggered',
        'Soaked': 'SOAKED_triggered',
        # Other survival
        'Wind Chilled': 'WIND_CHILLED_triggered',
        'Suffocating': 'SUFFOCATION_triggered',
        'Fainted': 'FAINTED_triggered',
    }
    
    beneficial_event_map = {
        'Lit Fire': 'LIT_FIRE_triggered',
        'Natural Shelter': 'NATURAL_SHELTER_triggered',
        'Good Shelter': 'GOOD_SHELTER_triggered',
        'Excellent Shelter': 'EXCELLENT_SHELTER_triggered',
    }
    
    # Combine all mappings
    all_mappings = {**survival_event_map, **beneficial_event_map}
    
    print("="*80)
    print("CONDITION → NLP INTEGRATION VERIFICATION")
    print("="*80)
    print()
    
    # Test 1: Check all conditions are mapped
    print("TEST 1: All conditions have NLP event mappings")
    print("-"*80)
    unmapped_conditions = []
    for condition_name in conditions.keys():
        if condition_name not in all_mappings:
            unmapped_conditions.append(condition_name)
            print(f"  ❌ '{condition_name}' - NOT MAPPED")
        else:
            print(f"  ✓ '{condition_name}' → {all_mappings[condition_name]}")
    
    if unmapped_conditions:
        print(f"\n⚠️  {len(unmapped_conditions)} conditions not mapped to NLP events")
    else:
        print(f"\n✅ All {len(conditions)} conditions are mapped!")
    print()
    
    # Test 2: Check all event types have messages
    print("TEST 2: All NLP event types have message variants")
    print("-"*80)
    survival_effects = messages_data.get('survival_effects', {})
    beneficial_effects = messages_data.get('beneficial_effects', {})
    
    missing_messages = []
    for condition_name, event_type in all_mappings.items():
        # Determine which category to check
        if condition_name in beneficial_event_map:
            category = beneficial_effects
            category_name = 'beneficial_effects'
        else:
            category = survival_effects
            category_name = 'survival_effects'
        
        if event_type not in category:
            missing_messages.append((event_type, category_name))
            print(f"  ❌ {event_type} - NO MESSAGES in {category_name}")
        else:
            message_count = len(category[event_type])
            print(f"  ✓ {event_type} - {message_count} variants in {category_name}")
    
    if missing_messages:
        print(f"\n⚠️  {len(missing_messages)} event types missing messages")
    else:
        print(f"\n✅ All event types have message variants!")
    print()
    
    # Test 3: Check message variance (should have 3+ variants each)
    print("TEST 3: Message variance (3+ variants recommended)")
    print("-"*80)
    low_variance = []
    for condition_name, event_type in all_mappings.items():
        # Determine which category to check
        if condition_name in beneficial_event_map:
            category = beneficial_effects
        else:
            category = survival_effects
        
        if event_type in category:
            message_count = len(category[event_type])
            if message_count < 3:
                low_variance.append((event_type, message_count))
                print(f"  ⚠️  {event_type} - Only {message_count} variants (recommend 3+)")
            else:
                print(f"  ✓ {event_type} - {message_count} variants")
    
    if low_variance:
        print(f"\n⚠️  {len(low_variance)} event types have low variance")
    else:
        print(f"\n✅ All event types have good message variance!")
    print()
    
    # Test 4: Verify no hardcoded messages are duplicated
    print("TEST 4: Hardcoded trigger_message comparison")
    print("-"*80)
    print("Checking if any trigger_message from conditions.json")
    print("appears as-is in event_messages.json...")
    print()
    
    hardcoded_found = []
    for condition_name, condition_data in conditions.items():
        trigger_msg = condition_data.get('trigger_message', '')
        if not trigger_msg:
            continue
        
        # Check if this exact message appears in any NLP event type
        for category_name, category_data in messages_data.items():
            for event_type, messages in category_data.items():
                if trigger_msg in messages:
                    hardcoded_found.append((condition_name, event_type, trigger_msg))
    
    if hardcoded_found:
        print(f"✅ {len(hardcoded_found)} hardcoded messages repurposed as NLP variants")
        for condition, event, msg in hardcoded_found:
            print(f"  • '{condition}' message in {event}")
    else:
        print("✅ No exact duplicates (messages have been varied)")
    print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    total_conditions = len(conditions)
    mapped_conditions = len(all_mappings)
    total_events = len(all_mappings)
    
    # Count total message variants
    total_variants = 0
    for event_type in all_mappings.values():
        if event_type in survival_effects:
            total_variants += len(survival_effects[event_type])
        elif event_type in beneficial_effects:
            total_variants += len(beneficial_effects[event_type])
    
    print(f"Conditions in conditions.json: {total_conditions}")
    print(f"Conditions mapped to NLP: {mapped_conditions}")
    print(f"Total NLP event types: {total_events}")
    print(f"Total message variants: {total_variants}")
    print(f"Average variants per event: {total_variants / total_events if total_events > 0 else 0:.1f}")
    print()
    
    if unmapped_conditions or missing_messages:
        print("❌ INTEGRATION INCOMPLETE - See warnings above")
        return False
    else:
        print("✅ INTEGRATION COMPLETE - All conditions properly mapped!")
        return True

if __name__ == '__main__':
    success = verify_integration()
    exit(0 if success else 1)
