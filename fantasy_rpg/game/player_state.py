"""
Fantasy RPG - Player State System

CDDA-style survival tracking with hunger, thirst, temperature regulation,
and environmental exposure mechanics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math

try:
    from ..world.weather_core import WeatherState
    from ..world.character_weather import CharacterWeatherResistance
except ImportError:
    try:
        from fantasy_rpg.world.weather_core import WeatherState
        from fantasy_rpg.world.character_weather import CharacterWeatherResistance
    except ImportError:
        # Create minimal stubs if weather system not available
        class WeatherState:
            def __init__(self):
                self.temperature = 70.0
                self.precipitation = 0
                self.wind_speed = 0
                self.precipitation_type = "rain"
                self.wind_direction = "N"
                self.cloud_cover = 50
                self.visibility = 1000
                self.feels_like = 70.0
                self.is_storm = False
                self.lightning_risk = 0.0
        class CharacterWeatherResistance:
            def __init__(self):
                pass


class SurvivalLevel(Enum):
    """Survival status levels for various needs"""
    EXCELLENT = 5
    GOOD = 4
    NORMAL = 3
    POOR = 2
    BAD = 1
    CRITICAL = 0


class TemperatureStatus(Enum):
    """Temperature comfort levels"""
    FREEZING = 0
    VERY_COLD = 1
    COLD = 2
    COOL = 3
    COMFORTABLE = 4
    WARM = 5
    HOT = 6
    VERY_HOT = 7
    OVERHEATING = 8


class WetnessLevel(Enum):
    """Wetness levels for exposure tracking"""
    DRY = 0
    DAMP = 1
    WET = 2
    SOAKED = 3
    DRENCHED = 4


@dataclass
class SurvivalNeeds:
    """Core survival needs tracking"""
    # Primary needs (0-1000 scale, 500 is neutral)
    hunger: int = 500  # 0 = starving, 1000 = stuffed
    thirst: int = 500  # 0 = dehydrated, 1000 = overhydrated
    fatigue: int = 500  # 0 = exhausted, 1000 = fully rested
    
    # Temperature regulation (0-1000 scale, 500 is comfortable)
    body_temperature: int = 500  # Core body temperature
    warmth: int = 500  # Clothing/shelter warmth
    
    # Environmental exposure
    wetness: int = 0  # 0-400, how wet the character is
    wind_chill: int = 0  # 0-200, wind chill effect
    
    def get_hunger_level(self) -> SurvivalLevel:
        """Get hunger status level"""
        if self.hunger >= 800:
            return SurvivalLevel.EXCELLENT
        elif self.hunger >= 650:
            return SurvivalLevel.GOOD
        elif self.hunger >= 350:
            return SurvivalLevel.NORMAL
        elif self.hunger >= 200:
            return SurvivalLevel.POOR
        elif self.hunger >= 50:
            return SurvivalLevel.BAD
        else:
            return SurvivalLevel.CRITICAL
    
    def get_thirst_level(self) -> SurvivalLevel:
        """Get thirst status level"""
        if self.thirst >= 800:
            return SurvivalLevel.EXCELLENT
        elif self.thirst >= 650:
            return SurvivalLevel.GOOD
        elif self.thirst >= 350:
            return SurvivalLevel.NORMAL
        elif self.thirst >= 200:
            return SurvivalLevel.POOR
        elif self.thirst >= 50:
            return SurvivalLevel.BAD
        else:
            return SurvivalLevel.CRITICAL
    
    def get_fatigue_level(self) -> SurvivalLevel:
        """Get fatigue status level - HIGH fatigue = well rested"""
        if self.fatigue >= 800:
            return SurvivalLevel.EXCELLENT  # Well rested
        elif self.fatigue >= 650:
            return SurvivalLevel.GOOD       # Rested
        elif self.fatigue >= 350:
            return SurvivalLevel.NORMAL     # Normal
        elif self.fatigue >= 200:
            return SurvivalLevel.POOR       # Tired
        elif self.fatigue >= 50:
            return SurvivalLevel.BAD        # Very tired
        else:
            return SurvivalLevel.CRITICAL   # Exhausted
    
    def get_temperature_status(self) -> TemperatureStatus:
        """Get temperature comfort status"""
        if self.body_temperature <= 100:
            return TemperatureStatus.FREEZING
        elif self.body_temperature <= 200:
            return TemperatureStatus.VERY_COLD
        elif self.body_temperature <= 300:
            return TemperatureStatus.COLD
        elif self.body_temperature <= 400:
            return TemperatureStatus.COOL
        elif self.body_temperature <= 600:
            return TemperatureStatus.COMFORTABLE
        elif self.body_temperature <= 700:
            return TemperatureStatus.WARM
        elif self.body_temperature <= 800:
            return TemperatureStatus.HOT
        elif self.body_temperature <= 900:
            return TemperatureStatus.VERY_HOT
        else:
            return TemperatureStatus.OVERHEATING
    
    def get_wetness_level(self) -> WetnessLevel:
        """Get wetness level"""
        if self.wetness <= 50:
            return WetnessLevel.DRY
        elif self.wetness <= 100:
            return WetnessLevel.DAMP
        elif self.wetness <= 200:
            return WetnessLevel.WET
        elif self.wetness <= 300:
            return WetnessLevel.SOAKED
        else:
            return WetnessLevel.DRENCHED


@dataclass
class PlayerState:
    """Complete player state with CDDA-style survival tracking"""
    # Core character reference
    character: any = None  # Reference to character object
    game_engine: any = None  # Reference to game engine for condition checking
    
    # Survival needs
    survival: SurvivalNeeds = field(default_factory=SurvivalNeeds)
    
    # Time tracking
    game_hour: float = 12.0  # Hour of day (0-23, can be fractional)
    game_day: int = 1  # Day number
    game_season: str = "spring"  # Current season
    turn_counter: int = 0  # Total turns elapsed
    
    # Location and environment
    current_hex: str = "0847"
    current_location: str = "Forest Clearing"
    current_weather: Optional[WeatherState] = None
    current_shelter: Optional[Dict[str, str]] = None  # Shelter tracking for condition system
    
    # Activity tracking
    last_meal_hours: int = 0  # Hours since last meal
    last_drink_hours: int = 0  # Hours since last drink
    last_sleep_hours: int = 0  # Hours since last sleep
    activity_level: str = "normal"  # "resting", "normal", "active", "strenuous"
    
    # Conditions system
    temporary_modifiers: Dict[str, int] = field(default_factory=dict)
    active_conditions: List[str] = field(default_factory=list)  # Conditions from conditions.json
    
    # Debug mode flag - ENABLED BY DEFAULT for development/testing
    debug_survival: bool = True  # Shows detailed survival calculations after time-passing actions
    
    # Shelter now works automatically via location flags (like "Lit Fire" system)
    
    def advance_time(self, hours: float, activity: str = "normal") -> dict:
        """
        Advance game time and update survival needs.
        
        Args:
            hours: Number of hours to advance
            activity: Activity level during this time
            
        Returns:
            Dictionary with:
                - newly_triggered_conditions: List of condition trigger messages
                - debug_output: Debug summary string (if debug_survival enabled)
        """
        self.turn_counter += 1
        self.activity_level = activity
        
        # Update time tracking
        self.game_hour += hours
        while self.game_hour >= 24:
            self.game_hour -= 24
            self.game_day += 1
        
        # Update activity counters
        self.last_meal_hours += hours
        self.last_drink_hours += hours
        self.last_sleep_hours += hours
        
        # Update survival needs based on time and activity
        self._update_hunger(hours, activity)
        self._update_thirst(hours, activity)
        self._update_fatigue(hours, activity)
        
        # Update environmental effects
        if self.current_weather:
            self._update_temperature_regulation(hours)
            self._update_environmental_exposure(hours)
        
        # Update health effects
        self._update_health_effects()
        
        # Update status effects and collect newly triggered condition messages
        newly_triggered = self._update_status_effects()
        
        # Collect debug output if enabled (return as string instead of printing)
        debug_output = None
        if self.debug_survival:
            debug_output = self._get_survival_summary_string(hours, activity)
        
        return {
            "newly_triggered_conditions": newly_triggered,
            "debug_output": debug_output
        }
    
    def _update_hunger(self, hours: float, activity: str):
        """Update hunger based on time and activity - MUCH slower for realism"""
        old_hunger = self.survival.hunger
        
        # Base hunger rate (points per hour) - GREATLY reduced for balance
        base_rate = 2  # Was 8, now 2 (4x slower)
        
        # Activity modifiers
        activity_modifiers = {
            "resting": 0.5,
            "normal": 1.0,
            "active": 1.5,
            "strenuous": 2.5
        }
        
        rate = base_rate * activity_modifiers.get(activity, 1.0)
        hunger_loss = int(rate * hours)
        
        if self.debug_survival:
            print(f"\n=== HUNGER UPDATE ===")
            print(f"  Base rate: {base_rate}/hour")
            print(f"  Activity: {activity} (×{activity_modifiers.get(activity, 1.0)})")
            print(f"  Effective rate: {rate}/hour")
            print(f"  Time passed: {hours:.2f}h")
            print(f"  Hunger loss: -{hunger_loss}")
            print(f"  Before: {old_hunger}")
        
        # Apply hunger loss
        self.survival.hunger = max(0, self.survival.hunger - hunger_loss)
        
        if self.debug_survival:
            print(f"  After: {self.survival.hunger}")
            print(f"  Change: {self.survival.hunger - old_hunger}")
    
    def _update_thirst(self, hours: float, activity: str):
        """Update thirst based on time, activity, and environment - 3x faster than hunger"""
        # Base thirst rate (points per hour) - 3x hunger rate for realism
        base_rate = 6  # Was 12, now 6 (3x hunger rate of 2)
        
        # Activity modifiers
        activity_modifiers = {
            "resting": 0.7,
            "normal": 1.0,
            "active": 1.8,
            "strenuous": 3.0
        }
        
        rate = base_rate * activity_modifiers.get(activity, 1.0)
        
        # Environmental modifiers
        if self.current_weather:
            # Hot weather increases thirst
            if self.current_weather.temperature > 80:
                rate *= 1.5
            elif self.current_weather.temperature > 90:
                rate *= 2.0
            
            # Dry conditions increase thirst
            if self.current_weather.precipitation == 0 and self.current_weather.cloud_cover < 30:
                rate *= 1.2
        
        thirst_loss = int(rate * hours)
        
        # Apply thirst loss
        self.survival.thirst = max(0, self.survival.thirst - thirst_loss)
    
    def _update_fatigue(self, hours: float, activity: str):
        """Update fatigue based on time and activity"""
        old_fatigue = self.survival.fatigue
        
        if activity == "resting":
            # Resting INCREASES fatigue (gets more rested) - HIGH fatigue = well rested
            recovery = int(30 * hours)  # 30 points per hour base rate
            
            # Apply shelter bonuses for better rest quality (subtle improvements)
            if "Excellent Shelter" in self.active_conditions:
                recovery += int(5 * hours)  # +5/hour in excellent shelter
            elif "Good Shelter" in self.active_conditions:
                recovery += int(3 * hours)  # +3/hour in good shelter
            elif "Natural Shelter" in self.active_conditions:
                recovery += int(2 * hours)  # +2/hour in natural shelter
            
            self.survival.fatigue = min(1000, self.survival.fatigue + recovery)
            print(f"  Fatigue: RESTING for {hours:.1f}h, +{recovery} rest, {old_fatigue} → {self.survival.fatigue}")
            
        elif activity == "unconscious":
            # Being unconscious also increases fatigue (forced rest)
            recovery = int(20 * hours)  # 20 points per hour (less than active rest)
            self.survival.fatigue = min(1000, self.survival.fatigue + recovery)
            print(f"  Fatigue: UNCONSCIOUS for {hours:.1f}h, +{recovery} rest, {old_fatigue} → {self.survival.fatigue}")
            
        else:
            # Activity DECREASES fatigue (gets more tired) - LOW fatigue = exhausted
            activity_rates = {
                "normal": 10,      # 10 points per hour (mild tiredness)
                "active": 20,      # 20 points per hour (moderate tiredness)
                "strenuous": 40    # 40 points per hour (high tiredness)
            }
            
            rate = activity_rates.get(activity, 10)
            fatigue_loss = int(rate * hours)
            self.survival.fatigue = max(0, self.survival.fatigue - fatigue_loss)
            print(f"  Fatigue: {activity.upper()} for {hours:.1f}h, -{fatigue_loss} rest, {old_fatigue} → {self.survival.fatigue}")
    
    def _update_temperature_regulation(self, hours: float):
        """Update body temperature based on weather, clothing, and environmental conditions"""
        if not self.current_weather:
            return
        
        # Get character weather resistance if available
        if hasattr(self.character, 'weather_resistance'):
            resistance = self.character.weather_resistance
        else:
            # Create basic resistance
            resistance = CharacterWeatherResistance()
        
        # Calculate target temperature based on weather
        ambient_temp = self.current_weather.feels_like
        
        # Convert to our 0-1000 scale (32°F = 200, 98.6°F = 500, 100°F = 520)
        target_temp = 200 + (ambient_temp - 32) * 4.5
        target_temp = max(0, min(1000, target_temp))
        
        # Apply clothing/shelter warmth
        if ambient_temp < 70:  # Cold conditions
            cold_resistance = resistance.get_effective_resistance("cold")
            warmth_bonus = cold_resistance * 15  # Up to 300 points of warmth
            target_temp += warmth_bonus
        
        # Check for environmental condition effects (fire, shelter, wetness, wind)
        has_lit_fire = "Lit Fire" in self.active_conditions
        has_natural_shelter = "Natural Shelter" in self.active_conditions
        has_good_shelter = "Good Shelter" in self.active_conditions
        has_excellent_shelter = "Excellent Shelter" in self.active_conditions
        has_wet = "Wet" in self.active_conditions
        has_soaked = "Soaked" in self.active_conditions
        has_wind_chilled = "Wind Chilled" in self.active_conditions
        
        # Calculate base temperature change rate
        temp_diff = target_temp - self.survival.body_temperature
        base_change_rate = 0.3  # 30% change per hour (base)
        
        # Shelter provides temperature stabilization (reduces change rate)
        shelter_stabilization = 1.0  # Default: no stabilization
        if has_excellent_shelter:
            shelter_stabilization = 0.15  # 85% reduction in temperature change
        elif has_good_shelter:
            shelter_stabilization = 0.35  # 65% reduction in temperature change
        elif has_natural_shelter:
            shelter_stabilization = 0.65  # 35% reduction in temperature change
        
        # Apply shelter stabilization to change rate
        change_rate = base_change_rate * shelter_stabilization * hours
        temp_change = int(temp_diff * change_rate)
        
        # Apply environmental temperature change
        self.survival.body_temperature += temp_change
        
        # Active cooling conditions (wetness, wind chill) - applied BEFORE fire warming
        # These cause continuous heat loss regardless of environmental temperature
        
        # Wetness conditions cause active heat loss (evaporative cooling + reduced insulation)
        if has_soaked:
            # Soaked: severe active cooling (20 points/hour base)
            cooling_rate = 20
            
            # Emergency cooling when dangerously hot (body_temp > 900)
            if self.survival.body_temperature > 900:
                cooling_rate = 35  # Increased cooling when critically hot
            
            # Calculate cooling for time passed (no cap - can cool to freezing)
            active_cooling = int(cooling_rate * hours)
            self.survival.body_temperature -= active_cooling
            
        elif has_wet:
            # Wet: moderate active cooling (10 points/hour base)
            cooling_rate = 10
            
            # Emergency cooling when dangerously hot (body_temp > 900)
            if self.survival.body_temperature > 900:
                cooling_rate = 18  # Increased cooling when critically hot
            
            # Calculate cooling for time passed (no cap - can cool to freezing)
            active_cooling = int(cooling_rate * hours)
            self.survival.body_temperature -= active_cooling
        
        # Wind Chilled condition causes active heat loss (wind stripping away warmth)
        if has_wind_chilled:
            # Wind chill: active cooling (15 points/hour base)
            cooling_rate = 15
            
            # Emergency cooling when dangerously hot (body_temp > 900)
            if self.survival.body_temperature > 900:
                cooling_rate = 25  # Increased cooling when critically hot
            
            # Calculate cooling for time passed (no cap - can cool to freezing)
            active_cooling = int(cooling_rate * hours)
            self.survival.body_temperature -= active_cooling
        
        # Lit Fire provides active warming (counteracts cooling, synergizes with shelter)
        if has_lit_fire:
            # Fire warming rate: 15 points per hour (can be boosted in cold conditions)
            fire_warming_rate = 15
            
            # In freezing conditions (body_temp < 100), fire provides emergency warming
            if self.survival.body_temperature < 100:
                fire_warming_rate = 25  # Increased warming when critically cold
            
            # Calculate warming for time passed (no cap - natural regulation through environmental system)
            fire_warming = int(fire_warming_rate * hours)
            self.survival.body_temperature += fire_warming
        
        # Clamp temperature to valid range
        self.survival.body_temperature = max(0, min(1000, self.survival.body_temperature))
    
    def _update_environmental_exposure(self, hours: float):
        """Update wetness and wind chill effects with shelter protection"""
        if not self.current_weather:
            return
        
        # Check for shelter conditions that provide protection
        has_lit_fire = "Lit Fire" in self.active_conditions
        has_natural_shelter = "Natural Shelter" in self.active_conditions
        has_good_shelter = "Good Shelter" in self.active_conditions
        has_excellent_shelter = "Excellent Shelter" in self.active_conditions
        
        # Calculate precipitation reduction (0.0 = full effect, 1.0 = complete immunity)
        precipitation_reduction = 0.0
        if has_excellent_shelter:
            precipitation_reduction = 1.0  # Complete immunity
        elif has_good_shelter:
            precipitation_reduction = 0.75  # 75% reduction
        elif has_natural_shelter:
            precipitation_reduction = 0.5  # 50% reduction
        
        # Calculate wind chill reduction (0.0 = full effect, 1.0 = complete immunity)
        wind_chill_reduction = 0.0
        if has_excellent_shelter:
            wind_chill_reduction = 1.0  # Complete immunity
        elif has_good_shelter:
            wind_chill_reduction = 0.75  # 75% reduction
        elif has_natural_shelter:
            wind_chill_reduction = 0.5  # 50% reduction
        
        # Update wetness from precipitation (reduced by shelter)
        if self.current_weather.precipitation > 0:
            # Apply precipitation reduction from shelter
            effective_precipitation = self.current_weather.precipitation * (1.0 - precipitation_reduction)
            wetness_increase = int(effective_precipitation / 10 * hours)
            self.survival.wetness = min(400, self.survival.wetness + wetness_increase)
        else:
            # Dry off gradually (base rate + bonuses from shelter/fire)
            dry_rate = 5  # Base drying rate
            
            # Weather bonuses (existing)
            if self.current_weather.wind_speed > 10:
                dry_rate += self.current_weather.wind_speed // 5  # Wind helps drying
            if self.current_weather.temperature > 70:
                dry_rate += 5  # Heat helps drying
            
            # Shelter/fire wetness reduction bonuses (active drying from conditions)
            if has_lit_fire:
                dry_rate += 15  # Fire provides excellent drying (most effective)
            elif has_excellent_shelter:
                dry_rate += 8  # Excellent shelter provides good drying
            elif has_good_shelter:
                dry_rate += 5  # Good shelter provides moderate drying
            elif has_natural_shelter:
                dry_rate += 3  # Natural shelter provides some drying
            
            wetness_decrease = int(dry_rate * hours)
            self.survival.wetness = max(0, self.survival.wetness - wetness_decrease)
        
        # Update wind chill (reduced by shelter)
        if self.current_weather.wind_speed > 5 and self.current_weather.temperature < 60:
            # Apply wind chill reduction from shelter
            effective_wind_speed = self.current_weather.wind_speed * (1.0 - wind_chill_reduction)
            wind_chill_effect = int(effective_wind_speed * 2 * hours)
            self.survival.wind_chill = min(200, self.survival.wind_chill + wind_chill_effect)
        else:
            # Wind chill fades when out of wind
            self.survival.wind_chill = max(0, self.survival.wind_chill - int(hours * 10))
        
        # Note: Wetness cooling now handled by condition system in _update_temperature_regulation()
        # This allows proper integration with fire/shelter effects
    
    def _apply_immediate_wetness_effects(self, new_weather: WeatherState, old_weather: WeatherState):
        """Apply immediate wetness when entering precipitation"""
        if not new_weather:
            return
        
        # Check if we're entering precipitation from dry conditions
        old_precipitation = old_weather.precipitation if old_weather else 0
        new_precipitation = new_weather.precipitation
        
        # If entering precipitation or precipitation increased significantly
        if new_precipitation > old_precipitation:
            # Apply immediate wetness based on precipitation intensity
            if new_precipitation > 50:  # Heavy precipitation
                immediate_wetness = 50  # Get quite wet immediately
            elif new_precipitation > 20:  # Moderate precipitation
                immediate_wetness = 25  # Get moderately wet
            elif new_precipitation > 5:  # Light precipitation
                immediate_wetness = 10  # Get slightly wet
            else:
                immediate_wetness = 5   # Very light wetness
            
            # Apply the wetness
            old_wetness = self.survival.wetness
            self.survival.wetness = min(400, self.survival.wetness + immediate_wetness)
            
            # Debug output to show wetness change
            if self.survival.wetness > old_wetness:
                wetness_level = self.survival.get_wetness_level()
                precip_type = getattr(new_weather, 'precipitation_type', 'precipitation')
                print(f"🌧️ You are getting wet from the {precip_type}! Wetness: {old_wetness} → {self.survival.wetness} ({wetness_level.name})")
        
        # Update health effects immediately to reflect new wetness
        self._update_health_effects()

    def _update_health_effects(self):
        """Update health effects - now handled by conditions system"""
        # The conditions system now handles all status effects
        # This method is kept for compatibility but does nothing
        pass
    
    def _update_status_effects(self) -> list[dict]:
        """Update temporary status effects and modifiers
        
        Returns:
            List of newly triggered condition messages (dicts with 'name' and 'message')
        """
        newly_triggered = []
        
        # Update conditions from conditions.json
        try:
            # Try different import paths for conditions
            try:
                from .conditions import get_conditions_manager
            except ImportError:
                from conditions import get_conditions_manager
            
            conditions_manager = get_conditions_manager()
            
            # Store previous conditions before evaluation
            previous_conditions = set(self.active_conditions)
            
            # Evaluate current conditions
            self.active_conditions = conditions_manager.evaluate_conditions(self)
            current_conditions = set(self.active_conditions)
            
            # Debug output
            if self.debug_survival:
                print(f"[DEBUG] Conditions updated: {self.active_conditions}")
                print(f"[DEBUG] Current shelter: {self.current_shelter}")
            
            # Get newly triggered conditions with their messages
            newly_triggered = conditions_manager.get_newly_triggered_conditions(
                previous_conditions, current_conditions, self
            )
            
        except Exception as e:
            print(f"Error evaluating conditions: {e}")
            self.active_conditions = []
        
        # Clear expired temporary modifiers
        # (This would be expanded with actual duration tracking)
        
        return newly_triggered
    
    def eat_food(self, nutrition_value: int):
        """Consume food to reduce hunger"""
        self.survival.hunger = min(1000, self.survival.hunger + nutrition_value)
        self.last_meal_hours = 0
    
    def drink_water(self, hydration_value: int):
        """Consume water to reduce thirst"""
        self.survival.thirst = min(1000, self.survival.thirst + hydration_value)
        self.last_drink_hours = 0
    
    def rest(self, hours: float, quality: str = "normal"):
        """Rest to recover fatigue"""
        # Note: Fatigue recovery is handled by advance_time() with "resting" activity
        # This method just tracks sleep and advances time
        
        self.last_sleep_hours = 0
        
        # Advance time during rest (this handles fatigue recovery)
        self.advance_time(hours, "resting")
    
    def get_survival_summary(self) -> str:
        """Get a text summary of survival status"""
        hunger_level = self.survival.get_hunger_level()
        thirst_level = self.survival.get_thirst_level()
        fatigue_level = self.survival.get_fatigue_level()
        temp_status = self.survival.get_temperature_status()
        wetness_level = self.survival.get_wetness_level()
        
        summary = f"""survival status:
Hunger: {hunger_level.name.title()} ({self.survival.hunger}/1000)
Thirst: {thirst_level.name.title()} ({self.survival.thirst}/1000)
Fatigue: {fatigue_level.name.title()} ({self.survival.fatigue}/1000)
Temperature: {temp_status.name.replace('_', ' ').title()}
Wetness: {wetness_level.name.title()}"""
        
        if self.active_conditions:
            summary += f"\n\nactive conditions:\n"
            for condition in self.active_conditions:
                summary += f"• {condition}\n"
        
        return summary
    
    def get_survival_bars(self) -> Dict[str, str]:
        """Get visual bars for survival needs"""
        def create_bar(value: int, max_value: int = 1000, width: int = 10) -> str:
            filled = int((value / max_value) * width)
            empty = width - filled
            return "█" * filled + "▓" * empty
        
        return {
            "hunger": create_bar(self.survival.hunger),
            "thirst": create_bar(self.survival.thirst),
            "fatigue": create_bar(self.survival.fatigue),
            "temperature": create_bar(self.survival.body_temperature),
            "wetness": create_bar(400 - self.survival.wetness, 400)  # Inverted for dryness
        }
    
    def get_time_string(self) -> str:
        """Get formatted time string with natural language"""
        # Round to nearest hour to avoid float precision issues
        hour = int(round(self.game_hour)) % 24
        
        # Time of day descriptions
        if 5 <= hour < 7:
            time_desc = "Early dawn"
        elif 7 <= hour < 9:
            time_desc = "Morning"
        elif 9 <= hour < 12:
            time_desc = "Late morning"
        elif 12 <= hour < 14:
            time_desc = "Midday"
        elif 14 <= hour < 17:
            time_desc = "Afternoon"
        elif 17 <= hour < 19:
            time_desc = "Late afternoon"
        elif 19 <= hour < 21:
            time_desc = "Evening"
        elif 21 <= hour < 23:
            time_desc = "Late evening"
        elif 23 <= hour or hour < 2:
            time_desc = "Deep night"
        elif 2 <= hour < 5:
            time_desc = "Before dawn"
        else:
            time_desc = "Night"
        
        return f"{time_desc}, Day {self.game_day}"
    
    def update_weather(self, weather: WeatherState):
        """Update current weather conditions"""
        old_weather = self.current_weather
        self.current_weather = weather
        
        # Apply immediate wetness effects when entering precipitation
        if weather and weather.precipitation > 0:
            self._apply_immediate_wetness_effects(weather, old_weather)
    
    def update_location(self, hex_id: str, location_name: str):
        """Update current location"""
        self.current_hex = hex_id
        self.current_location = location_name
    
    def _get_survival_summary_string(self, hours: float, activity: str) -> str:
        """Generate comprehensive survival stats summary string for debugging
        
        Args:
            hours: Hours that passed
            activity: Activity type
            
        Returns:
            Formatted debug string with all survival stats
        """
        lines = []
        lines.append(f"\n{'='*74}")
        lines.append(f"SURVIVAL STATS SUMMARY (after {hours:.2f}h of '{activity}' activity)")
        lines.append(f"{'='*74}")
        
        # Current conditions - EVALUATE FRESH (same as character panel) to avoid race conditions
        lines.append(f"\nACTIVE CONDITIONS:")
        current_conditions = []
        try:
            # Evaluate conditions fresh (same pattern as panels.py)
            try:
                from .conditions import get_conditions_manager
            except ImportError:
                from conditions import get_conditions_manager
            
            conditions_manager = get_conditions_manager()
            current_conditions = conditions_manager.evaluate_conditions(self)
            
            if current_conditions:
                for cond in current_conditions:
                    lines.append(f"  • {cond}")
            else:
                lines.append(f"  (none)")
        except Exception as e:
            # Fallback to self.active_conditions if conditions system fails
            if self.active_conditions:
                for cond in self.active_conditions:
                    lines.append(f"  • {cond}")
            else:
                lines.append(f"  (none)")
                lines.append(f"  [Error evaluating conditions: {e}]")
        
        # Survival stats
        lines.append(f"\nHUNGER: {self.survival.hunger}/1000")
        lines.append(f"   Level: {self.survival.get_hunger_level().name}")
        
        lines.append(f"\nTHIRST: {self.survival.thirst}/1000")
        lines.append(f"   Level: {self.survival.get_thirst_level().name}")
        
        lines.append(f"\nFATIGUE: {self.survival.fatigue}/1000 (HIGH = well rested)")
        lines.append(f"   Level: {self.survival.get_fatigue_level().name}")
        
        # Temperature stats
        lines.append(f"\nWARMTH: {self.survival.body_temperature}/1000")
        lines.append(f"   Status: {self.survival.get_temperature_status().name}")
        if self.current_weather:
            temp_f = self.current_weather.temperature
            temp_c = (temp_f - 32) * 5 / 9
            feels_f = self.current_weather.feels_like
            feels_c = (feels_f - 32) * 5 / 9
            lines.append(f"   Ambient: {temp_f:.1f}°F / {temp_c:.1f}°C (feels like {feels_f:.1f}°F / {feels_c:.1f}°C)")
        
        # Environmental exposure
        lines.append(f"\nWIND CHILL: {self.survival.wind_chill}/200")
        if self.current_weather:
            lines.append(f"   Wind: {self.current_weather.wind_speed} mph from {self.current_weather.wind_direction}")
        
        lines.append(f"\nWETNESS: {self.survival.wetness}/400")
        lines.append(f"   Level: {self.survival.get_wetness_level().name}")
        if self.current_weather:
            lines.append(f"   Precipitation: {self.current_weather.precipitation} ({self.current_weather.precipitation_type})")
        
        # Shelter info - CHECK CONDITIONS (use fresh evaluation from above)
        shelter_from_conditions = None
        if "Excellent Shelter" in current_conditions:
            shelter_from_conditions = "Excellent Shelter"
        elif "Good Shelter" in current_conditions:
            shelter_from_conditions = "Good Shelter"
        elif "Natural Shelter" in current_conditions:
            shelter_from_conditions = "Natural Shelter"
        
        if shelter_from_conditions:
            lines.append(f"\nSHELTER: {shelter_from_conditions} (from location)")
        elif hasattr(self, 'current_shelter') and self.current_shelter:
            # Fallback to old system if present (obsolete)
            lines.append(f"\nSHELTER: {self.current_shelter.get('quality', 'unknown')} ({self.current_shelter.get('type', 'unknown')})")
        else:
            lines.append(f"\nSHELTER: None (exposed)")
        
        # Time info
        lines.append(f"\nTIME: Day {self.game_day}, {int(self.game_hour):02d}:{int((self.game_hour % 1) * 60):02d}")
        lines.append(f"   Season: {self.game_season}")
        lines.append(f"   Last meal: {self.last_meal_hours:.1f}h ago")
        lines.append(f"   Last drink: {self.last_drink_hours:.1f}h ago")
        lines.append(f"   Last sleep: {self.last_sleep_hours:.1f}h ago")
        
        lines.append(f"{'='*74}\n")
        
        return "\n".join(lines)