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
    from fantasy_rpg.world.weather_core import WeatherState
    from fantasy_rpg.world.character_weather import CharacterWeatherResistance


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
    
    # Health effects from survival
    hypothermia_risk: int = 0  # 0-100, risk of hypothermia
    hyperthermia_risk: int = 0  # 0-100, risk of overheating
    dehydration_effects: int = 0  # 0-100, dehydration severity
    starvation_effects: int = 0  # 0-100, starvation severity
    
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
    
    # Activity tracking
    last_meal_hours: int = 0  # Hours since last meal
    last_drink_hours: int = 0  # Hours since last drink
    last_sleep_hours: int = 0  # Hours since last sleep
    activity_level: str = "normal"  # "resting", "normal", "active", "strenuous"
    
    # Status effects
    status_effects: List[str] = field(default_factory=list)
    temporary_modifiers: Dict[str, int] = field(default_factory=dict)
    
    def advance_time(self, hours: float, activity: str = "normal"):
        """
        Advance game time and update survival needs.
        
        Args:
            hours: Number of hours to advance
            activity: Activity level during this time
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
        
        # Update status effects
        self._update_status_effects()
    
    def _update_hunger(self, hours: float, activity: str):
        """Update hunger based on time and activity - MUCH slower for realism"""
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
        
        # Apply hunger loss
        self.survival.hunger = max(0, self.survival.hunger - hunger_loss)
        
        # Update starvation effects
        if self.survival.hunger < 200:
            self.survival.starvation_effects = min(100, self.survival.starvation_effects + int(hours * 2))
        elif self.survival.hunger > 400:
            self.survival.starvation_effects = max(0, self.survival.starvation_effects - int(hours))
    
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
        
        # Update dehydration effects
        if self.survival.thirst < 200:
            self.survival.dehydration_effects = min(100, self.survival.dehydration_effects + int(hours * 3))
        elif self.survival.thirst > 400:
            self.survival.dehydration_effects = max(0, self.survival.dehydration_effects - int(hours))
    
    def _update_fatigue(self, hours: float, activity: str):
        """Update fatigue based on time and activity"""
        old_fatigue = self.survival.fatigue
        
        if activity == "resting":
            # Resting REDUCES fatigue (gets less tired)
            recovery = int(30 * hours)  # 30 points per hour
            self.survival.fatigue = max(0, self.survival.fatigue - recovery)
            print(f"  Fatigue: RESTING for {hours:.1f}h, -{recovery} tiredness, {old_fatigue} → {self.survival.fatigue}")
            
        elif activity == "unconscious":
            # Being unconscious also reduces fatigue (forced rest)
            recovery = int(20 * hours)  # 20 points per hour (less than active rest)
            self.survival.fatigue = max(0, self.survival.fatigue - recovery)
            print(f"  Fatigue: UNCONSCIOUS for {hours:.1f}h, -{recovery} tiredness, {old_fatigue} → {self.survival.fatigue}")
            
        else:
            # Activity DECREASES fatigue (gets more tired) - HIGH fatigue = well rested
            activity_rates = {
                "normal": -10,     # -10 points per hour (mild tiredness)
                "active": -20,     # -20 points per hour (moderate tiredness)
                "strenuous": -40   # -40 points per hour (high tiredness)
            }
            
            rate = activity_rates.get(activity, -10)
            fatigue_change = int(rate * hours)
            self.survival.fatigue = max(0, min(1000, self.survival.fatigue + fatigue_change))
            change_desc = f"+{fatigue_change}" if fatigue_change > 0 else str(fatigue_change)
            print(f"  Fatigue: {activity.upper()} for {hours:.1f}h, {change_desc} fatigue, {old_fatigue} → {self.survival.fatigue}")
    
    def _update_temperature_regulation(self, hours: float):
        """Update body temperature based on weather and clothing"""
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
        
        # Gradual temperature change
        temp_diff = target_temp - self.survival.body_temperature
        change_rate = 0.3 * hours  # 30% change per hour
        temp_change = int(temp_diff * change_rate)
        
        self.survival.body_temperature += temp_change
        self.survival.body_temperature = max(0, min(1000, self.survival.body_temperature))
        
        # Update temperature-related risks
        if self.survival.body_temperature < 300:
            risk_increase = int((300 - self.survival.body_temperature) / 10 * hours)
            self.survival.hypothermia_risk = min(100, self.survival.hypothermia_risk + risk_increase)
        elif self.survival.body_temperature > 700:
            risk_increase = int((self.survival.body_temperature - 700) / 10 * hours)
            self.survival.hyperthermia_risk = min(100, self.survival.hyperthermia_risk + risk_increase)
        else:
            # Recovery when in comfortable range
            self.survival.hypothermia_risk = max(0, self.survival.hypothermia_risk - int(hours * 5))
            self.survival.hyperthermia_risk = max(0, self.survival.hyperthermia_risk - int(hours * 5))
    
    def _update_environmental_exposure(self, hours: float):
        """Update wetness and wind chill effects"""
        if not self.current_weather:
            return
        
        # Update wetness from precipitation
        if self.current_weather.precipitation > 0:
            wetness_increase = int(self.current_weather.precipitation / 10 * hours)
            self.survival.wetness = min(400, self.survival.wetness + wetness_increase)
        else:
            # Dry off gradually
            dry_rate = 5  # Base drying rate
            if self.current_weather.wind_speed > 10:
                dry_rate += self.current_weather.wind_speed // 5  # Wind helps drying
            if self.current_weather.temperature > 70:
                dry_rate += 5  # Heat helps drying
            
            wetness_decrease = int(dry_rate * hours)
            self.survival.wetness = max(0, self.survival.wetness - wetness_decrease)
        
        # Update wind chill
        if self.current_weather.wind_speed > 5 and self.current_weather.temperature < 60:
            wind_chill_effect = int(self.current_weather.wind_speed * 2 * hours)
            self.survival.wind_chill = min(200, self.survival.wind_chill + wind_chill_effect)
        else:
            # Wind chill fades when out of wind
            self.survival.wind_chill = max(0, self.survival.wind_chill - int(hours * 10))
        
        # Wetness makes you colder
        if self.survival.wetness > 100:
            wetness_penalty = int(self.survival.wetness / 20 * hours)
            self.survival.body_temperature = max(0, self.survival.body_temperature - wetness_penalty)
    
    def _update_health_effects(self):
        """Update health effects based on survival status"""
        # Clear old survival-related status effects
        self.status_effects = [effect for effect in self.status_effects 
                             if not effect.startswith(('Hungry', 'Thirsty', 'Tired', 'Cold', 'Hot', 'Wet'))]
        
        # Add current status effects
        hunger_level = self.survival.get_hunger_level()
        if hunger_level == SurvivalLevel.CRITICAL:
            self.status_effects.append("Starving")
        elif hunger_level == SurvivalLevel.BAD:
            self.status_effects.append("Very Hungry")
        elif hunger_level == SurvivalLevel.POOR:
            self.status_effects.append("Hungry")
        
        thirst_level = self.survival.get_thirst_level()
        if thirst_level == SurvivalLevel.CRITICAL:
            self.status_effects.append("Severely Dehydrated")
        elif thirst_level == SurvivalLevel.BAD:
            self.status_effects.append("Dehydrated")
        elif thirst_level == SurvivalLevel.POOR:
            self.status_effects.append("Thirsty")
        
        fatigue_level = self.survival.get_fatigue_level()
        if fatigue_level == SurvivalLevel.CRITICAL:
            self.status_effects.append("Exhausted")
        elif fatigue_level == SurvivalLevel.BAD:
            self.status_effects.append("Very Tired")
        elif fatigue_level == SurvivalLevel.POOR:
            self.status_effects.append("Tired")
        
        temp_status = self.survival.get_temperature_status()
        if temp_status == TemperatureStatus.FREEZING:
            self.status_effects.append("Freezing")
        elif temp_status == TemperatureStatus.VERY_COLD:
            self.status_effects.append("Very Cold")
        elif temp_status == TemperatureStatus.COLD:
            self.status_effects.append("Cold")
        elif temp_status == TemperatureStatus.VERY_HOT:
            self.status_effects.append("Very Hot")
        elif temp_status == TemperatureStatus.OVERHEATING:
            self.status_effects.append("Overheating")
        
        wetness_level = self.survival.get_wetness_level()
        if wetness_level == WetnessLevel.DRENCHED:
            self.status_effects.append("Drenched")
        elif wetness_level == WetnessLevel.SOAKED:
            self.status_effects.append("Soaked")
        elif wetness_level == WetnessLevel.WET:
            self.status_effects.append("Wet")
        
        # Health risks
        if self.survival.hypothermia_risk > 70:
            self.status_effects.append("Hypothermia Risk")
        if self.survival.hyperthermia_risk > 70:
            self.status_effects.append("Heat Stroke Risk")
    
    def _update_status_effects(self):
        """Update temporary status effects and modifiers"""
        # Clear expired temporary modifiers
        # (This would be expanded with actual duration tracking)
        pass
    
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
        
        if self.status_effects:
            summary += f"\n\nstatus effects:\n"
            for effect in self.status_effects:
                summary += f"• {effect}\n"
        
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
        self.current_weather = weather
    
    def update_location(self, hex_id: str, location_name: str):
        """Update current location"""
        self.current_hex = hex_id
        self.current_location = location_name


def test_player_state():
    """Test the player state survival system"""
    print("=== Testing Player State Survival System ===")
    
    # Test 1: Basic player state creation
    print("\n1. Testing basic player state creation:")
    
    player = PlayerState()
    print(f"Initial state:")
    print(f"  Time: {player.get_time_string()}")
    print(f"  Location: {player.current_location} ({player.current_hex})")
    print(f"  Hunger: {player.survival.hunger}/1000")
    print(f"  Thirst: {player.survival.thirst}/1000")
    print(f"  Fatigue: {player.survival.fatigue}/1000")
    
    # Test 2: Time advancement and survival changes
    print("\n2. Testing time advancement:")
    
    # Create some weather
    test_weather = WeatherState(45.0, 15, "NW", 30, "rain", 70, 1000, 0.0, False, 0.0)
    player.update_weather(test_weather)
    
    print("Advancing 4 hours of normal activity...")
    player.advance_time(4.0, "normal")
    
    print(f"After 4 hours:")
    print(f"  Time: {player.get_time_string()}")
    print(f"  Hunger: {player.survival.hunger}/1000 ({player.survival.get_hunger_level().name})")
    print(f"  Thirst: {player.survival.thirst}/1000 ({player.survival.get_thirst_level().name})")
    print(f"  Fatigue: {player.survival.fatigue}/1000 ({player.survival.get_fatigue_level().name})")
    print(f"  Temperature: {player.survival.get_temperature_status().name}")
    print(f"  Wetness: {player.survival.get_wetness_level().name}")
    
    # Test 3: Survival bars
    print("\n3. Testing survival bars:")
    bars = player.get_survival_bars()
    print(f"Hunger:  [{bars['hunger']}] {player.survival.hunger}/1000")
    print(f"Thirst:  [{bars['thirst']}] {player.survival.thirst}/1000")
    print(f"Fatigue: [{bars['fatigue']}] {player.survival.fatigue}/1000")
    print(f"Warmth:  [{bars['temperature']}] {player.survival.body_temperature}/1000")
    print(f"Dryness: [{bars['wetness']}] {400 - player.survival.wetness}/400")
    
    # Test 4: Eating and drinking
    print("\n4. Testing eating and drinking:")
    
    print("Eating food (nutrition: 200)...")
    player.eat_food(200)
    print(f"Hunger after eating: {player.survival.hunger}/1000")
    
    print("Drinking water (hydration: 300)...")
    player.drink_water(300)
    print(f"Thirst after drinking: {player.survival.thirst}/1000")
    
    # Test 5: Resting
    print("\n5. Testing rest:")
    
    print("Resting for 8 hours (normal quality)...")
    old_fatigue = player.survival.fatigue
    player.rest(8.0, "normal")
    print(f"Fatigue: {old_fatigue} -> {player.survival.fatigue}")
    print(f"Time after rest: {player.get_time_string()}")
    
    # Test 6: Weather effects
    print("\n6. Testing weather effects:")
    
    # Cold, wet weather
    cold_weather = WeatherState(25.0, 25, "N", 80, "snow", 100, 200, 0.0, False, 0.0)
    player.update_weather(cold_weather)
    
    print("Experiencing cold, snowy weather for 6 hours...")
    old_temp = player.survival.body_temperature
    old_wetness = player.survival.wetness
    
    player.advance_time(6.0, "active")
    
    print(f"Body temperature: {old_temp} -> {player.survival.body_temperature}")
    print(f"Wetness: {old_wetness} -> {player.survival.wetness}")
    print(f"Temperature status: {player.survival.get_temperature_status().name}")
    print(f"Hypothermia risk: {player.survival.hypothermia_risk}%")
    
    # Test 7: Status effects
    print("\n7. Testing status effects:")
    
    if player.status_effects:
        print("Current status effects:")
        for effect in player.status_effects:
            print(f"  • {effect}")
    else:
        print("No status effects")
    
    # Test 8: Survival summary
    print("\n8. Testing survival summary:")
    print(player.get_survival_summary())
    
    # Test 9: Extreme conditions
    print("\n9. Testing extreme survival conditions:")
    
    # Simulate starvation
    player.survival.hunger = 50
    player.survival.thirst = 30
    player.survival.fatigue = 20
    player.survival.body_temperature = 150  # Very cold
    player.survival.wetness = 350  # Soaked
    
    # Update health effects
    player._update_health_effects()
    
    print("Extreme survival conditions:")
    print(f"  Hunger: {player.survival.get_hunger_level().name}")
    print(f"  Thirst: {player.survival.get_thirst_level().name}")
    print(f"  Fatigue: {player.survival.get_fatigue_level().name}")
    print(f"  Temperature: {player.survival.get_temperature_status().name}")
    print(f"  Wetness: {player.survival.get_wetness_level().name}")
    
    print("\nCritical status effects:")
    for effect in player.status_effects:
        print(f"  • {effect}")
    
    print("\n=== Player state survival system testing complete! ===")


if __name__ == "__main__":
    test_player_state()