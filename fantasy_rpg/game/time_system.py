"""
Fantasy RPG - Time System

Manages game time progression, turn-based mechanics, and activity duration.
"""

from dataclasses import dataclass
from typing import Dict, List, Callable, Optional, Tuple
from enum import Enum

try:
    from .player_state import PlayerState
    from ..world.weather_core import WeatherState, generate_weather_state
except ImportError:
    try:
        from player_state import PlayerState
        from fantasy_rpg.world.weather_core import WeatherState, generate_weather_state
    except ImportError:
        # When running as module, use absolute imports
        from fantasy_rpg.game.player_state import PlayerState
        from fantasy_rpg.world.weather_core import WeatherState, generate_weather_state


class ActivityType(Enum):
    """Types of activities that take time"""
    INSTANT = "instant"          # No time passes (looking, checking inventory)
    QUICK = "quick"              # 15 minutes (quick actions)
    SHORT = "short"              # 30 minutes (basic actions)
    MEDIUM = "medium"            # 1 hour (travel, rest)
    LONG = "long"                # 2-4 hours (extended activities)
    EXTENDED = "extended"        # 6-8 hours (sleep, crafting)


@dataclass
class ActivityDefinition:
    """Defines how long an activity takes and its effects"""
    name: str
    activity_type: ActivityType
    base_duration_hours: float
    exertion_level: str  # "resting", "normal", "active", "strenuous"
    description: str
    
    # Optional modifiers
    weather_affected: bool = True
    skill_can_reduce: bool = False
    equipment_can_reduce: bool = False


class TimeSystem:
    """Manages game time, activities, and their effects on player state"""
    
    def __init__(self, player_state: PlayerState):
        """Initialize time system with player state"""
        self.player_state = player_state
        self.activity_definitions = self._create_activity_definitions()
        
        # Callbacks for UI updates
        self.on_time_advance: List[Callable] = []
        self.on_weather_change: List[Callable] = []
        self.on_status_change: List[Callable] = []
        
        # Weather update tracking
        self.hours_since_weather_update = 0
        self.weather_update_interval = 2  # Update weather every 2 hours
    
    def _create_activity_definitions(self) -> Dict[str, ActivityDefinition]:
        """Create definitions for all game activities"""
        activities = {}
        
        # Instant actions (no time passes)
        activities["look"] = ActivityDefinition(
            "look", ActivityType.INSTANT, 0.0, "normal",
            "Examine your surroundings", weather_affected=False
        )
        
        activities["inventory"] = ActivityDefinition(
            "inventory", ActivityType.INSTANT, 0.0, "normal",
            "Check your inventory", weather_affected=False
        )
        
        activities["character"] = ActivityDefinition(
            "character", ActivityType.INSTANT, 0.0, "normal",
            "Review character sheet", weather_affected=False
        )
        
        activities["map"] = ActivityDefinition(
            "map", ActivityType.INSTANT, 0.0, "normal",
            "Consult your map", weather_affected=False
        )
        
        # Quick actions (15 minutes)
        activities["eat"] = ActivityDefinition(
            "eat", ActivityType.QUICK, 0.25, "normal",
            "Eat a meal or snack"
        )
        
        activities["drink"] = ActivityDefinition(
            "drink", ActivityType.QUICK, 0.25, "normal",
            "Drink water or other beverages"
        )
        
        activities["equip"] = ActivityDefinition(
            "equip", ActivityType.QUICK, 0.25, "normal",
            "Change equipment or clothing"
        )
        
        # Short actions (30 minutes)
        activities["search"] = ActivityDefinition(
            "search", ActivityType.SHORT, 0.5, "active",
            "Search an area thoroughly", skill_can_reduce=True
        )
        
        activities["forage"] = ActivityDefinition(
            "forage", ActivityType.SHORT, 0.5, "active",
            "Look for food or useful materials", skill_can_reduce=True
        )
        
        activities["short_rest"] = ActivityDefinition(
            "short_rest", ActivityType.SHORT, 0.5, "resting",
            "Take a brief rest", weather_affected=True
        )
        
        activities["rest"] = ActivityDefinition(
            "rest", ActivityType.MEDIUM, 1.0, "resting",
            "Rest for an hour", weather_affected=True
        )
        
        # Medium actions (1 hour base, modified by speed)
        activities["travel"] = ActivityDefinition(
            "travel", ActivityType.MEDIUM, 1.0, "active",
            "Travel to an adjacent location", weather_affected=True
        )
        
        activities["explore"] = ActivityDefinition(
            "explore", ActivityType.MEDIUM, 1.0, "active",
            "Explore current location in detail", skill_can_reduce=True
        )
        
        activities["craft_simple"] = ActivityDefinition(
            "craft_simple", ActivityType.MEDIUM, 1.0, "normal",
            "Craft simple items", skill_can_reduce=True
        )
        
        activities["hunt"] = ActivityDefinition(
            "hunt", ActivityType.MEDIUM, 1.0, "active",
            "Hunt for food", skill_can_reduce=True, weather_affected=True
        )
        
        # Long actions (2-4 hours)
        activities["long_rest"] = ActivityDefinition(
            "long_rest", ActivityType.LONG, 3.0, "resting",
            "Rest for several hours", weather_affected=True
        )
        
        activities["craft_complex"] = ActivityDefinition(
            "craft_complex", ActivityType.LONG, 3.0, "normal",
            "Craft complex items", skill_can_reduce=True
        )
        
        activities["study"] = ActivityDefinition(
            "study", ActivityType.LONG, 2.0, "normal",
            "Study books or practice skills"
        )
        
        # Extended actions (6-8 hours)
        activities["sleep"] = ActivityDefinition(
            "sleep", ActivityType.EXTENDED, 8.0, "resting",
            "Sleep through the night", weather_affected=True
        )
        
        activities["craft_masterwork"] = ActivityDefinition(
            "craft_masterwork", ActivityType.EXTENDED, 6.0, "normal",
            "Craft masterwork items", skill_can_reduce=True
        )
        
        activities["camp"] = ActivityDefinition(
            "camp", ActivityType.EXTENDED, 8.0, "resting",
            "Set up camp and rest", weather_affected=True
        )
        
        return activities
    
    def perform_activity(self, activity_name: str, **kwargs) -> Dict[str, any]:
        """
        Perform an activity and advance time accordingly.
        
        Args:
            activity_name: Name of the activity to perform
            **kwargs: Additional parameters (skill_level, equipment_bonus, etc.)
            
        Returns:
            Dictionary with activity results and time information
        """
        # Check if character is dead
        if hasattr(self.player_state, 'character') and self.player_state.character:
            if self.player_state.character.hp <= 0:
                print("💀 CHARACTER DIED! Cannot perform any actions.")
                return {
                    "success": False,
                    "message": "💀 CHARACTER DIED! You cannot perform any actions while dead.",
                    "time_passed": 0.0,
                    "character_dead": True
                }
        
        if activity_name not in self.activity_definitions:
            return {
                "success": False,
                "message": f"Unknown activity: {activity_name}",
                "time_passed": 0.0
            }
        
        activity = self.activity_definitions[activity_name]
        
        # Calculate actual duration
        duration = self._calculate_activity_duration(activity, **kwargs)
        
        # Get warnings about dangerous conditions (but never block)
        warnings = self._get_activity_warnings(activity, duration)
        can_perform, _ = self._can_perform_activity(activity, duration)  # Always returns True now
        
        # Perform the activity
        if duration > 0:
            self._advance_time(duration, activity.exertion_level)
        
        # Check if character died during the activity
        if hasattr(self.player_state, 'character') and self.player_state.character:
            if self.player_state.character.hp <= 0:
                print("💀 CHARACTER DIED during the activity!")
                return {
                    "success": False,
                    "message": "💀 CHARACTER DIED! You collapsed and died during the activity.",
                    "time_passed": duration,
                    "character_dead": True,
                    "activity": activity_name,
                    "duration_hours": duration,
                    "time_passed_description": self._format_duration(duration),
                    "new_time": self.player_state.get_time_string()
                }
        
        # Get activity-specific results
        results = self._get_activity_results(activity_name, duration, **kwargs)
        
        return {
            "success": True,
            "activity": activity_name,
            "duration_hours": duration,
            "time_passed_description": self._format_duration(duration),
            "new_time": self.player_state.get_time_string(),
            "exertion_level": activity.exertion_level,
            "warnings": warnings,
            **results
        }
    
    def _calculate_activity_duration(self, activity: ActivityDefinition, **kwargs) -> float:
        """Calculate actual duration for an activity with modifiers"""
        base_duration = activity.base_duration_hours
        
        if base_duration == 0:
            return 0.0  # Instant actions
        
        duration = base_duration
        
        # Skill reduction
        if activity.skill_can_reduce and "skill_level" in kwargs:
            skill_level = kwargs["skill_level"]
            # Higher skill reduces time (up to 25% reduction)
            skill_reduction = min(0.25, skill_level * 0.025)
            duration *= (1.0 - skill_reduction)
        
        # Equipment bonus
        if activity.equipment_can_reduce and "equipment_bonus" in kwargs:
            equipment_bonus = kwargs["equipment_bonus"]
            # Good equipment reduces time (up to 20% reduction)
            equipment_reduction = min(0.20, equipment_bonus * 0.05)
            duration *= (1.0 - equipment_reduction)
        
        # Weather effects
        if activity.weather_affected and self.player_state.current_weather:
            weather_modifier = self._get_weather_time_modifier()
            duration *= weather_modifier
        
        # Fatigue effects
        fatigue_level = self.player_state.survival.get_fatigue_level()
        if fatigue_level.value <= 2:  # BAD or CRITICAL fatigue
            duration *= 1.5  # Takes 50% longer when exhausted
        elif fatigue_level.value <= 3:  # POOR fatigue
            duration *= 1.2  # Takes 20% longer when tired
        
        # Speed effects for travel activities
        if activity.name == "travel" and hasattr(self.player_state, 'character'):
            character = self.player_state.character
            if hasattr(character, 'get_effective_speed'):
                effective_speed = character.get_effective_speed()
                base_speed = getattr(character, 'base_speed', 30)
                
                # Calculate speed modifier (slower = takes longer)
                # Standard travel assumes 30ft speed, adjust proportionally
                speed_modifier = base_speed / max(5, effective_speed)  # Prevent division by zero
                duration *= speed_modifier
                
                # Cap maximum travel time at 5x normal (for very slow characters)
                duration = min(duration, activity.base_duration_hours * 5.0)
        
        return duration
    
    def _get_weather_time_modifier(self) -> float:
        """Calculate how weather affects activity duration"""
        if not self.player_state.current_weather:
            return 1.0
        
        weather = self.player_state.current_weather
        modifier = 1.0
        
        # Temperature effects
        if weather.feels_like < 32:  # Freezing
            modifier *= 1.4
        elif weather.feels_like < 50:  # Cold
            modifier *= 1.2
        elif weather.feels_like > 90:  # Hot
            modifier *= 1.3
        elif weather.feels_like > 100:  # Very hot
            modifier *= 1.5
        
        # Precipitation effects
        if weather.precipitation > 50:  # Heavy precipitation
            modifier *= 1.3
        elif weather.precipitation > 20:  # Moderate precipitation
            modifier *= 1.1
        
        # Wind effects
        if weather.wind_speed > 25:  # Strong wind
            modifier *= 1.2
        
        # Visibility effects
        if weather.visibility < 500:  # Poor visibility
            modifier *= 1.3
        
        # Storm effects
        if weather.is_storm:
            modifier *= 1.5
        
        return modifier
    
    def _can_perform_activity(self, activity: ActivityDefinition, duration: float) -> Tuple[bool, str]:
        """Check if an activity can be performed - now only provides warnings, never blocks"""
        # Never block activities - player agency is paramount
        # All checks now return warnings that will be shown but won't prevent action
        return True, ""
    
    def _get_activity_warnings(self, activity: ActivityDefinition, duration: float) -> List[str]:
        """Get warnings about dangerous conditions for an activity"""
        warnings = []
        
        # Check survival conditions and add warnings
        if self.player_state.survival.get_fatigue_level().value == 0:  # CRITICAL fatigue
            warnings.append("[!] You are exhausted!")
        elif self.player_state.survival.get_fatigue_level().value <= 2:  # BAD fatigue
            warnings.append("[!] You are very tired.")
        
        if self.player_state.survival.get_thirst_level().value == 0:  # CRITICAL thirst
            warnings.append("[!] You are severely dehydrated!")
        elif self.player_state.survival.get_thirst_level().value <= 2:  # BAD thirst
            warnings.append("[!] You are very thirsty.")
        
        if self.player_state.survival.get_hunger_level().value == 0:  # CRITICAL hunger
            warnings.append("[!] You are starving!")
        elif self.player_state.survival.get_hunger_level().value <= 2:  # BAD hunger
            warnings.append("[!] You are very hungry.")
        
        # Temperature warnings
        if self.player_state.survival.hypothermia_risk > 80:
            warnings.append("[!] You are dangerously cold!")
        elif self.player_state.survival.hypothermia_risk > 60:
            warnings.append("[!] You are getting very cold.")
        
        if self.player_state.survival.hyperthermia_risk > 80:
            warnings.append("[!] You are dangerously overheated!")
        elif self.player_state.survival.hyperthermia_risk > 60:
            warnings.append("[!] You are getting very hot.")
        
        # Weather warnings
        if activity.weather_affected and self.player_state.current_weather:
            weather = self.player_state.current_weather
            
            if weather.is_storm and activity.name in ["travel", "explore", "hunt"]:
                warnings.append("[!] Storm conditions make this very dangerous!")
            
            if weather.visibility < 100 and activity.name in ["travel", "explore"]:
                warnings.append("[!] Very poor visibility makes this risky!")
            
            if weather.feels_like < 32 and activity.name in ["travel", "explore"]:
                warnings.append("[!] Freezing temperatures increase exposure risk!")
            
            if weather.feels_like > 100 and activity.name in ["travel", "explore"]:
                warnings.append("[!] Extreme heat increases heat stroke risk!")
        
        return warnings
    
    def _advance_time(self, hours: float, exertion_level: str):
        """Advance game time and update all systems"""
        old_time = self.player_state.get_time_string()
        
        # Advance player state
        self.player_state.advance_time(hours, exertion_level)
        
        # Apply damage-over-time effects
        self._apply_damage_over_time(hours)
        
        # Check for fainting
        self._check_for_fainting()
        
        # Update weather if needed
        self.hours_since_weather_update += hours
        if self.hours_since_weather_update >= self.weather_update_interval:
            self._update_weather()
            self.hours_since_weather_update = 0
        
        # Notify callbacks
        for callback in self.on_time_advance:
            callback(old_time, self.player_state.get_time_string(), hours)
    
    def _update_weather(self):
        """Update weather conditions"""
        # Generate new weather based on current conditions
        if self.player_state.current_weather:
            base_temp = self.player_state.current_weather.temperature
        else:
            base_temp = 60.0  # Default temperature
        
        # Add some variation
        import random
        base_temp += random.uniform(-5, 5)
        
        new_weather = generate_weather_state(
            base_temp, 
            self.player_state.game_season, 
            "temperate"  # Default climate
        )
        
        old_weather = self.player_state.current_weather
        self.player_state.update_weather(new_weather)
        
        # Notify callbacks
        for callback in self.on_weather_change:
            callback(old_weather, new_weather)
    
    def _apply_damage_over_time(self, hours_passed: float):
        """Apply damage-over-time effects from active conditions"""
        try:
            from .conditions import get_conditions_manager
            conditions_manager = get_conditions_manager()
            
            # Get active conditions
            active_conditions = conditions_manager.evaluate_conditions(self.player_state)
            
            # Check each condition for damage-over-time effects
            for condition_name in active_conditions:
                condition_data = conditions_manager.conditions_data.get(condition_name, {})
                effects = condition_data.get("effects", {})
                damage_over_time = effects.get("damage_over_time")
                
                if damage_over_time:
                    interval_str = damage_over_time.get("interval", "10_minutes")
                    damage_amount = damage_over_time.get("amount", 1)
                    damage_type = damage_over_time.get("type", "generic")
                    
                    # Convert interval string to hours
                    interval_hours = self._parse_time_interval(interval_str)
                    
                    if interval_hours > 0:
                        # Calculate how many damage applications should occur
                        damage_applications = int(hours_passed / interval_hours)
                        
                        if damage_applications > 0:
                            total_damage = damage_applications * damage_amount
                            
                            # Apply damage to character
                            if hasattr(self.player_state, 'character'):
                                character = self.player_state.character
                                old_hp = character.hp
                                character.hp = max(0, character.hp - total_damage)
                                
                                # Log the damage using action logger
                                try:
                                    from ..actions.action_logger import get_action_logger
                                    action_logger = get_action_logger()
                                    action_logger.log_damage_taken(
                                        damage_amount=total_damage,
                                        damage_type=damage_type,
                                        source=condition_name,
                                        old_hp=old_hp,
                                        new_hp=character.hp
                                    )
                                except ImportError:
                                    # Fallback to print if action logger not available
                                    print(f"Condition '{condition_name}' deals {total_damage} {damage_type} damage over time ({old_hp} → {character.hp} HP)")
                                
                                # Notify status change callbacks
                                for callback in self.on_status_change:
                                    callback(f"Took {total_damage} {damage_type} damage from {condition_name}")
                        else:
                            # Debug: show why no damage was applied
                            print(f"Condition '{condition_name}': {hours_passed:.2f}h passed, {interval_hours:.2f}h interval → {damage_applications} applications")
        
        except (ImportError, Exception) as e:
            # Conditions system not available or error occurred
            pass
    
    def _parse_time_interval(self, interval_str: str) -> float:
        """Parse time interval string to hours"""
        interval_map = {
            "1_minute": 1/60,
            "5_minutes": 5/60,
            "10_minutes": 10/60,
            "15_minutes": 15/60,
            "30_minutes": 0.5,
            "1_hour": 1.0,
            "2_hours": 2.0,
            "4_hours": 4.0,
            "6_hours": 6.0,
            "8_hours": 8.0,
            "12_hours": 12.0,
            "24_hours": 24.0
        }
        
        return interval_map.get(interval_str, 10/60)  # Default to 10 minutes
    
    def _check_for_fainting(self):
        """Check if the character should faint and handle fainting"""
        try:
            from .conditions import get_conditions_manager
            conditions_manager = get_conditions_manager()
            
            # Check if character should faint
            should_faint = conditions_manager.check_for_fainting(self.player_state)
            
            print(f"  Fainting check: should_faint={should_faint}")
            
            if should_faint:
                # Apply fainting
                faint_result = conditions_manager.apply_fainting(self.player_state)
                
                # Force the character to rest for the fainting duration
                faint_hours = faint_result["duration_minutes"] / 60.0
                
                # Apply the unconscious time (unconscious activity provides some fatigue recovery)
                self.player_state.advance_time(faint_hours, "unconscious")
                
                # Notify callbacks about fainting
                for callback in self.on_status_change:
                    callback(faint_result["message"])
                    callback(f"Recovered some fatigue while unconscious, but underlying conditions persist")
                
                return faint_result
        
        except (ImportError, Exception) as e:
            # Conditions system not available
            pass
        
        return None
    
    def _get_activity_results(self, activity_name: str, duration: float, **kwargs) -> Dict[str, any]:
        """Get specific results for different activities"""
        results = {}
        
        if activity_name == "eat":
            nutrition = kwargs.get("nutrition_value", 200)
            self.player_state.eat_food(nutrition)
            results["message"] = f"You eat and feel less hungry"
        
        elif activity_name == "drink":
            hydration = kwargs.get("hydration_value", 300)
            self.player_state.drink_water(hydration)
            results["message"] = f"You drink and feel less thirsty"
        
        elif activity_name in ["short_rest", "long_rest"]:
            quality = kwargs.get("rest_quality", "normal")
            # Rest was already applied in player_state.advance_time for resting activities
            results["message"] = f"You rest and feel more refreshed"
        
        elif activity_name == "sleep":
            quality = kwargs.get("sleep_quality", "normal")
            # Sleep recovery is handled by the resting exertion level
            results["message"] = f"You sleep peacefully and wake up refreshed"
        
        elif activity_name == "travel":
            destination = kwargs.get("destination", "unknown location")
            results["message"] = f"You travel to {destination}"
            results["destination"] = destination
        
        elif activity_name == "explore":
            # Exploration results would be determined by the specific location
            results["message"] = f"You explore the area and discover new details"
            results["discoveries"] = kwargs.get("discoveries", [])
        
        elif activity_name == "forage":
            # Foraging results based on skill and location
            success = kwargs.get("forage_success", True)
            if success:
                items_found = kwargs.get("items_found", ["berries"])
                results["message"] = f"You forage and find: {', '.join(items_found)}"
                results["items_found"] = items_found
            else:
                results["message"] = f"You forage but find nothing useful"
        
        elif activity_name == "hunt":
            success = kwargs.get("hunt_success", False)
            if success:
                prey = kwargs.get("prey", "small game")
                results["message"] = f"You successfully hunt {prey}"
                results["prey"] = prey
            else:
                results["message"] = f"Your hunting expedition is unsuccessful"
        
        else:
            results["message"] = f"You {activity_name.replace('_', ' ')}"
        
        return results
    
    def _format_duration(self, hours: float) -> str:
        """Format duration in natural language without precise measurements"""
        if hours == 0:
            return "No time passes"
        elif hours < 0.25:  # Less than 15 minutes
            return "A few moments"
        elif hours < 0.5:   # Less than 30 minutes
            return "A short while"
        elif hours < 1:     # Less than 1 hour
            return "Some time"
        elif hours < 1.5:   # About 1 hour
            return "About an hour"
        elif hours < 2.5:   # About 2 hours
            return "A couple of hours"
        elif hours < 4:     # 2-4 hours
            return "Several hours"
        elif hours < 6:     # 4-6 hours
            return "Much of the day"
        elif hours < 8:     # 6-8 hours
            return "Most of the day"
        else:               # 8+ hours
            return "The better part of a day"
    
    def get_available_activities(self) -> List[Dict[str, any]]:
        """Get list of activities available to the player"""
        available = []
        
        for name, activity in self.activity_definitions.items():
            warnings = self._get_activity_warnings(activity, activity.base_duration_hours)
            
            available.append({
                "name": name,
                "display_name": activity.name.replace("_", " ").title(),
                "description": activity.description,
                "duration": self._format_duration(activity.base_duration_hours),
                "exertion": activity.exertion_level,
                "available": True,  # All activities are always available
                "warnings": warnings
            })
        
        return available
    
    def add_time_callback(self, callback: Callable):
        """Add callback for time advancement"""
        self.on_time_advance.append(callback)
    
    def add_weather_callback(self, callback: Callable):
        """Add callback for weather changes"""
        self.on_weather_change.append(callback)
    
    def add_status_callback(self, callback: Callable):
        """Add callback for status changes"""
        self.on_status_change.append(callback)


def test_time_system():
    """Test the time system"""
    print("=== Testing Time System ===")
    
    # Test 1: Create time system with player state
    print("\n1. Testing time system creation:")
    
    from player_state import PlayerState
    player = PlayerState()
    time_system = TimeSystem(player)
    
    print(f"Initial time: {player.get_time_string()}")
    print(f"Available activities: {len(time_system.get_available_activities())}")
    
    # Test 2: Instant activities
    print("\n2. Testing instant activities:")
    
    result = time_system.perform_activity("look")
    print(f"Look result: {result['success']}, Time passed: {result.get('time_passed_description', 'None')}")
    
    result = time_system.perform_activity("inventory")
    print(f"Inventory result: {result['success']}, Time passed: {result.get('time_passed_description', 'None')}")
    
    # Test 3: Quick activities
    print("\n3. Testing quick activities:")
    
    result = time_system.perform_activity("eat", nutrition_value=250)
    print(f"Eat result: {result['success']}")
    print(f"Time passed: {result.get('time_passed_description')}")
    print(f"New time: {result.get('new_time')}")
    print(f"Message: {result.get('message')}")
    
    # Test 4: Medium activities
    print("\n4. Testing medium activities:")
    
    result = time_system.perform_activity("travel", destination="Ancient Ruins")
    print(f"Travel result: {result['success']}")
    print(f"Time passed: {result.get('time_passed_description')}")
    print(f"New time: {result.get('new_time')}")
    print(f"Message: {result.get('message')}")
    
    # Test 5: Extended activities
    print("\n5. Testing extended activities:")
    
    result = time_system.perform_activity("sleep", sleep_quality="normal")
    print(f"Sleep result: {result['success']}")
    print(f"Time passed: {result.get('time_passed_description')}")
    print(f"New time: {result.get('new_time')}")
    print(f"Message: {result.get('message')}")
    
    # Test 6: Weather effects on activities
    print("\n6. Testing weather effects:")
    
    # Create bad weather
    bad_weather = WeatherState(25.0, 35, "N", 80, "snow", 100, 200, 0.0, False, 0.0)
    player.update_weather(bad_weather)
    
    print("Bad weather conditions:")
    print(f"  Temperature: {bad_weather.temperature}°F")
    print(f"  Wind: {bad_weather.wind_speed} mph")
    print(f"  Precipitation: {bad_weather.precipitation}% {bad_weather.precipitation_type}")
    
    result = time_system.perform_activity("travel", destination="Mountain Pass")
    print(f"Travel in bad weather:")
    print(f"  Success: {result['success']}")
    print(f"  Time passed: {result.get('time_passed_description', 'None')}")
    if not result['success']:
        print(f"  Reason: {result.get('message')}")
    
    # Test 7: Fatigue effects
    print("\n7. Testing fatigue effects:")
    
    # Exhaust the player
    player.survival.fatigue = 20  # Very tired
    
    result = time_system.perform_activity("explore")
    print(f"Explore while exhausted:")
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Time passed: {result.get('time_passed_description')}")
        print(f"  (Should take longer due to fatigue)")
    else:
        print(f"  Reason: {result.get('message')}")
    
    # Test 8: Available activities
    print("\n8. Testing available activities:")
    
    activities = time_system.get_available_activities()
    print("Available activities:")
    for activity in activities[:5]:  # Show first 5
        status = "✓" if activity["available"] else "✗"
        print(f"  {status} {activity['display_name']}: {activity['description']}")
        print(f"    Duration: {activity['duration']}, Exertion: {activity['exertion']}")
        if not activity["available"]:
            print(f"    Reason: {activity['reason']}")
    
    print("\n=== Time system testing complete! ===")


if __name__ == "__main__":
    test_time_system()