"""
Fantasy RPG - Calendar System

Implements a fantasy calendar with seasons, months, and natural time tracking.
Integrates with TimeSystem for game time progression.

Calendar Structure:
- 4 seasons: Spring, Summer, Autumn, Winter
- 12 months (3 per season)
- 30 days per month
- 360 days per year
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum


class Season(Enum):
    """Four seasons of the year."""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


@dataclass
class Month:
    """Represents a month in the fantasy calendar."""
    name: str
    number: int  # 1-12
    season: Season
    days: int = 30


# Fantasy calendar months (3 per season)
CALENDAR_MONTHS = [
    # Spring (months 1-3)
    Month("Firstbloom", 1, Season.SPRING),
    Month("Greentide", 2, Season.SPRING),
    Month("Rainwatch", 3, Season.SPRING),
    
    # Summer (months 4-6)
    Month("Sunpeak", 4, Season.SUMMER),
    Month("Highsun", 5, Season.SUMMER),
    Month("Harvestmoon", 6, Season.SUMMER),
    
    # Autumn (months 7-9)
    Month("Leaffall", 7, Season.AUTUMN),
    Month("Goldwind", 8, Season.AUTUMN),
    Month("Dimlight", 9, Season.AUTUMN),
    
    # Winter (months 10-12)
    Month("Frostfall", 10, Season.WINTER),
    Month("Deepwinter", 11, Season.WINTER),
    Month("Thawbreak", 12, Season.WINTER),
]

# Constants
DAYS_PER_MONTH = 30
MONTHS_PER_YEAR = 12
DAYS_PER_YEAR = DAYS_PER_MONTH * MONTHS_PER_YEAR  # 360 days


class CalendarSystem:
    """Manages fantasy calendar with seasons and natural time tracking."""
    
    def __init__(self, starting_year: int = 1452, starting_day: int = 1, starting_hour: float = 12.0):
        """Initialize calendar system.
        
        Args:
            starting_year: Year number (e.g., 1452 in the Third Age)
            starting_day: Day of year (1-360)
            starting_hour: Hour of day (0-24)
        """
        self.year = starting_year
        self.day_of_year = max(1, min(starting_day, DAYS_PER_YEAR))
        self.hour = starting_hour
        
    def advance_time(self, hours: float) -> Tuple[bool, bool]:
        """Advance time by the given number of hours.
        
        Args:
            hours: Number of hours to advance
            
        Returns:
            Tuple of (day_changed, year_changed) booleans
        """
        self.hour += hours
        day_changed = False
        year_changed = False
        
        # Handle day rollover
        while self.hour >= 24.0:
            self.hour -= 24.0
            self.day_of_year += 1
            day_changed = True
            
            # Handle year rollover
            if self.day_of_year > DAYS_PER_YEAR:
                self.day_of_year = 1
                self.year += 1
                year_changed = True
        
        # Handle negative hours (shouldn't happen, but safety)
        while self.hour < 0:
            self.hour += 24.0
            self.day_of_year -= 1
            day_changed = True
            
            if self.day_of_year < 1:
                self.day_of_year = DAYS_PER_YEAR
                self.year -= 1
                year_changed = True
        
        return day_changed, year_changed
    
    def get_current_month(self) -> Month:
        """Get the current month based on day of year."""
        month_index = (self.day_of_year - 1) // DAYS_PER_MONTH
        month_index = max(0, min(month_index, MONTHS_PER_YEAR - 1))
        return CALENDAR_MONTHS[month_index]
    
    def get_current_season(self) -> Season:
        """Get the current season."""
        return self.get_current_month().season
    
    def get_day_of_month(self) -> int:
        """Get day within the current month (1-30)."""
        return ((self.day_of_year - 1) % DAYS_PER_MONTH) + 1
    
    def get_month_number(self) -> int:
        """Get the current month number (1-12)."""
        return self.get_current_month().number
    
    def get_season_name(self) -> str:
        """Get current season name as string."""
        return self.get_current_season().value
    
    def get_time_of_day(self) -> str:
        """Get descriptive time of day."""
        hour = int(self.hour)
        
        if 5 <= hour < 7:
            return "Early dawn"
        elif 7 <= hour < 9:
            return "Morning"
        elif 9 <= hour < 12:
            return "Late morning"
        elif 12 <= hour < 14:
            return "Midday"
        elif 14 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 19:
            return "Late afternoon"
        elif 19 <= hour < 21:
            return "Evening"
        elif 21 <= hour < 23:
            return "Late evening"
        elif 23 <= hour or hour < 2:
            return "Deep night"
        elif 2 <= hour < 5:
            return "Before dawn"
        else:
            return "Night"
    
    def get_short_time_string(self) -> str:
        """Get short time string for display (e.g., '14:30')."""
        hour_int = int(self.hour)
        minute = int((self.hour - hour_int) * 60)
        return f"{hour_int:02d}:{minute:02d}"
    
    def get_date_string(self, include_time: bool = False) -> str:
        """Get formatted date string.
        
        Args:
            include_time: Whether to include time of day
            
        Returns:
            Formatted date string like "15th of Firstbloom, 1452" or
            "15th of Firstbloom, 1452, 14:30"
        """
        month = self.get_current_month()
        day = self.get_day_of_month()
        
        # Ordinal suffix
        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        
        date_str = f"{day}{suffix} of {month.name}, {self.year}"
        
        if include_time:
            date_str += f", {self.get_short_time_string()}"
        
        return date_str
    
    def get_compact_date_string(self) -> str:
        """Get compact date for title bar display.
        
        Returns:
            String like "Firstbloom 15, 1452"
        """
        month = self.get_current_month()
        day = self.get_day_of_month()
        return f"{month.name} {day}, {self.year}"
    
    def get_title_bar_string(self) -> str:
        """Get formatted string for title bar display.
        
        Returns:
            String like "Late afternoon, Firstbloom 15, Spring 1452"
        """
        time_of_day = self.get_time_of_day()
        month = self.get_current_month()
        day = self.get_day_of_month()
        season = self.get_season_name().capitalize()
        
        return f"{time_of_day}, {month.name} {day}, {season} {self.year}"
    
    def get_natural_date_description(self) -> str:
        """Get natural language date description for narration.
        
        Returns:
            String like "It is late afternoon on the 15th of Firstbloom, 
            in the year 1452. Spring has arrived, bringing warmer weather."
        """
        time_of_day = self.get_time_of_day().lower()
        date = self.get_date_string()
        season = self.get_current_season()
        
        # Season-specific flavor text
        season_flavor = {
            Season.SPRING: "Spring has arrived, bringing warmer weather and new growth.",
            Season.SUMMER: "Summer is here, with long days and warm sunshine.",
            Season.AUTUMN: "Autumn has come, painting the world in golden hues.",
            Season.WINTER: "Winter grips the land, bringing cold winds and short days."
        }
        
        return f"It is {time_of_day} on the {date}. {season_flavor[season]}"
    
    def get_season_progress(self) -> float:
        """Get progress through current season (0.0 to 1.0).
        
        Returns:
            Float between 0.0 (start of season) and 1.0 (end of season)
        """
        month = self.get_current_month()
        month_in_season = (month.number - 1) % 3  # 0, 1, or 2
        day_of_month = self.get_day_of_month()
        
        days_into_season = (month_in_season * DAYS_PER_MONTH) + day_of_month
        total_days_in_season = 3 * DAYS_PER_MONTH  # 90 days per season
        
        return days_into_season / total_days_in_season
    
    def to_dict(self) -> dict:
        """Serialize calendar state to dictionary."""
        return {
            'year': self.year,
            'day_of_year': self.day_of_year,
            'hour': self.hour
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CalendarSystem':
        """Deserialize calendar state from dictionary."""
        return cls(
            starting_year=data.get('year', 1452),
            starting_day=data.get('day_of_year', 1),
            starting_hour=data.get('hour', 12.0)
        )
    
    def __str__(self) -> str:
        """String representation."""
        return self.get_date_string(include_time=True)
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"CalendarSystem(year={self.year}, day={self.day_of_year}, hour={self.hour:.2f})"


# Helper functions for quick calendar access

def get_season_for_day(day_of_year: int) -> Season:
    """Get season for a given day of year."""
    month_index = (day_of_year - 1) // DAYS_PER_MONTH
    month_index = max(0, min(month_index, MONTHS_PER_YEAR - 1))
    return CALENDAR_MONTHS[month_index].season


def get_month_for_day(day_of_year: int) -> Month:
    """Get month for a given day of year."""
    month_index = (day_of_year - 1) // DAYS_PER_MONTH
    month_index = max(0, min(month_index, MONTHS_PER_YEAR - 1))
    return CALENDAR_MONTHS[month_index]


def format_duration(hours: float) -> str:
    """Format duration in hours as natural language.
    
    Args:
        hours: Duration in hours
        
    Returns:
        Formatted string like "2 hours", "30 minutes", "1 hour 15 minutes"
    """
    if hours < 0.1:
        return "a moment"
    
    total_minutes = int(hours * 60)
    
    if total_minutes < 60:
        return f"{total_minutes} minute{'s' if total_minutes != 1 else ''}"
    
    hours_int = total_minutes // 60
    minutes_int = total_minutes % 60
    
    if minutes_int == 0:
        return f"{hours_int} hour{'s' if hours_int != 1 else ''}"
    else:
        return f"{hours_int} hour{'s' if hours_int != 1 else ''} {minutes_int} minute{'s' if minutes_int != 1 else ''}"


if __name__ == "__main__":
    # Quick test
    cal = CalendarSystem(starting_year=1452, starting_day=1, starting_hour=12.0)
    
    print("Calendar System Test")
    print("=" * 50)
    print(f"Current date: {cal.get_date_string(include_time=True)}")
    print(f"Month: {cal.get_current_month().name}")
    print(f"Season: {cal.get_season_name()}")
    print(f"Day of month: {cal.get_day_of_month()}")
    print(f"Time of day: {cal.get_time_of_day()}")
    print(f"Title bar: {cal.get_title_bar_string()}")
    print()
    
    print("Advancing 50 days...")
    cal.advance_time(50 * 24)
    print(f"New date: {cal.get_date_string(include_time=True)}")
    print(f"Month: {cal.get_current_month().name}")
    print(f"Season: {cal.get_season_name()}")
    print()
    
    print("Advancing 100 days...")
    cal.advance_time(100 * 24)
    print(f"New date: {cal.get_date_string(include_time=True)}")
    print(f"Month: {cal.get_current_month().name}")
    print(f"Season: {cal.get_season_name()}")
    print()
    
    print("All months:")
    for month in CALENDAR_MONTHS:
        print(f"  {month.number}. {month.name} ({month.season.value.capitalize()})")
