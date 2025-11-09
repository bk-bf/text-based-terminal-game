"""
Historical Figure Simulator

Simulates 150 years of births, deaths, marriages, and life events for 500-1000 figures.
Integrates with historical event system to create cause-and-effect chains.

Architecture:
- Uses existing HistoricalFigure dataclass from historical_figures.py
- Generates founding figures at civilization creation
- Simulates year-by-year life events (births, deaths, marriages)
- Links figures to historical events as participants
- Tracks genealogical relationships automatically
- Scales to 500-1000 figures with realistic demographics
"""

from typing import List, Dict, Optional, Tuple
import random
from dataclasses import dataclass

# Import existing HistoricalFigure and supporting structures
from .historical_figures import (
    HistoricalFigure, FigureRole, LegendaryStatus,
    _generate_name, _generate_backstory, HERO_ARCHETYPES, VILLAIN_ARCHETYPES
)


@dataclass
class LifeEvent:
    """Represents a significant event in a figure's life."""
    year: int
    month: str
    day: int
    season: str
    event_type: str  # "birth", "death", "marriage", "achievement", "tragedy"
    description: str
    related_figures: List[str] = None  # Other figure IDs involved
    related_events: List[str] = None  # Historical event IDs
    significance: int = 1  # 1-10
    
    def __post_init__(self):
        if self.related_figures is None:
            self.related_figures = []
        if self.related_events is None:
            self.related_events = []


class HistoricalFigureSimulator:
    """Simulates historical figures over time with genealogy tracking."""
    
    # Race lifespan ranges (average)
    RACE_LIFESPANS = {
        'human': (50, 80),
        'elf': (500, 800),
        'dwarf': (250, 400),
        'halfling': (100, 150),
        'gnome': (300, 500),
        'half-elf': (150, 250),
        'half-orc': (60, 80),
        'dragonborn': (70, 90),
        'tiefling': (80, 100)
    }
    
    # Fertility years by race (min_age, max_age)
    FERTILITY_RANGES = {
        'human': (16, 45),
        'elf': (100, 500),
        'dwarf': (50, 300),
        'halfling': (25, 90),
        'gnome': (50, 250),
        'half-elf': (25, 150),
        'half-orc': (14, 50),
        'dragonborn': (15, 60),
        'tiefling': (16, 70)
    }
    
    # Calendar data
    MONTHS = [
        ("Firstbloom", "spring"), ("Greentide", "spring"), ("Rainwatch", "spring"),
        ("Sunpeak", "summer"), ("Highsun", "summer"), ("Harvestmoon", "summer"),
        ("Leaffall", "autumn"), ("Goldwind", "autumn"), ("Dimlight", "autumn"),
        ("Frostfall", "winter"), ("Deepwinter", "winter"), ("Thawbreak", "winter")
    ]
    
    def __init__(self, world_coordinator, seed: Optional[int] = None):
        """Initialize figure simulator.
        
        Args:
            world_coordinator: WorldCoordinator with civilizations
            seed: Random seed for reproducibility
        """
        self.world = world_coordinator
        self.rng = random.Random(seed)
        self.figures: List[HistoricalFigure] = []
        self.figure_counter = 0
        
        # Track living figures by civilization for genealogy
        self.living_figures: Dict[str, List[str]] = {}
        
        # Track figures by year for efficient queries
        self.figures_by_birth_year: Dict[int, List[str]] = {}
        self.figures_by_death_year: Dict[int, List[str]] = {}
    
    def _generate_random_date(self, year: int) -> Tuple[str, int, str]:
        """Generate random calendar date for given year."""
        month_name, season = self.rng.choice(self.MONTHS)
        day = self.rng.randint(1, 30)
        return month_name, day, season
    
    def _get_lifespan(self, race: str) -> int:
        """Get random lifespan for race."""
        race_lower = race.lower()
        if race_lower in self.RACE_LIFESPANS:
            min_age, max_age = self.RACE_LIFESPANS[race_lower]
            return self.rng.randint(min_age, max_age)
        return self.rng.randint(50, 80)  # Default to human
    
    def _can_have_children(self, figure: HistoricalFigure, year: int) -> bool:
        """Check if figure is of childbearing age."""
        age = year - figure.birth_year
        if age < 0 or (figure.death_year and year >= figure.death_year):
            return False
        
        race_lower = figure.race.lower()
        if race_lower in self.FERTILITY_RANGES:
            min_age, max_age = self.FERTILITY_RANGES[race_lower]
            return min_age <= age <= max_age
        
        return 16 <= age <= 45  # Default to human range
    
    def _is_alive(self, figure: HistoricalFigure, year: int) -> bool:
        """Check if figure is alive at given year."""
        if year < figure.birth_year:
            return False
        if figure.death_year and year >= figure.death_year:
            return False
        return True
    
    def generate_founder_figures(self, civilization, start_year: int, count: int = 5) -> List[HistoricalFigure]:
        """Generate founding figures for a civilization.
        
        Args:
            civilization: Civilization object
            start_year: Founding year
            count: Number of founders to create
            
        Returns:
            List of founder figures
        """
        founders = []
        
        for i in range(count):
            figure_id = f"figure-{self.figure_counter:04d}"
            self.figure_counter += 1
            
            # Generate name
            gender = "male" if self.rng.random() < 0.5 else "female"
            name, title = _generate_name(civilization.race, gender, self.rng)
            
            # Birth date (30 years before founding)
            birth_year = start_year - self.rng.randint(25, 40)
            birth_month, birth_day, birth_season = self._generate_random_date(birth_year)
            
            # Determine role
            if i == 0:
                role = "ruler"
                title = f"{name} the Founder"
                social_class = "ruler"
                archetype = self.rng.choice(["noble_ruler", "warrior_hero"])
            elif i < 3:
                role = self.rng.choice(["warrior", "noble", "scholar"])
                social_class = "noble"
                archetype = self.rng.choice(HERO_ARCHETYPES)
            else:
                role = self.rng.choice(["warrior", "craftsman", "merchant", "priest"])
                social_class = self.rng.choice(["noble", "commoner"])
                archetype = self.rng.choice(HERO_ARCHETYPES[:4])  # More common archetypes
            
            # Create figure using existing HistoricalFigure structure
            figure = HistoricalFigure(
                id=figure_id,
                name=name,
                title=title if i == 0 else "",
                race=civilization.race,
                alignment="hero",
                archetype=archetype,
                birth_year=birth_year,
                death_year=None,
                parents=None,  # Founders have mythic origins
                spouse=None,
                children=[],
                participated_in_events=[],
                achievements=[f"Founded {civilization.name}" if i == 0 else "Founding figure"],
                artifacts_owned=[],
                cultural_significance=9 if i == 0 else 6,
                memory_strength=8 if i == 0 else 5,
                cultural_influence={civilization.race: 9 if i == 0 else 6},
                remembered_as="founding leader" if i == 0 else "founding hero",
                legendary_status="legendary" if i == 0 else "famous",
                backstory=_generate_backstory(name, archetype, civilization.race, [], self.rng),
                personality_traits=[],
                cultural_origin=civilization.name
            )
            
            founders.append(figure)
            self.figures.append(figure)
            
            # Track by birth year
            if birth_year not in self.figures_by_birth_year:
                self.figures_by_birth_year[birth_year] = []
            self.figures_by_birth_year[birth_year].append(figure_id)
        
        # Initialize living figures tracking
        self.living_figures[civilization.id] = [f.id for f in founders]
        
        return founders
    
    def simulate_year(self, year: int) -> List[HistoricalFigure]:
        """Simulate one year of life events.
        
        Handles:
        - Deaths (natural)
        - Births (new generation)
        - Marriages
        
        Args:
            year: Current simulation year
            
        Returns:
            List of new figures born this year
        """
        new_figures = []
        
        # Process deaths
        self._process_deaths(year)
        
        # Process births
        new_figures = self._process_births(year)
        
        # Process marriages
        self._process_marriages(year)
        
        return new_figures
    
    def _process_deaths(self, year: int):
        """Process natural deaths for figures who reach end of lifespan."""
        for figure in self.figures:
            if not self._is_alive(figure, year):
                continue
            
            if figure.death_year:  # Already processed
                continue
            
            age = year - figure.birth_year
            lifespan = self._get_lifespan(figure.race)
            
            # Death probability increases with age
            if age >= lifespan:
                death_chance = 0.5
            elif age >= lifespan * 0.9:
                death_chance = 0.2
            elif age >= lifespan * 0.8:
                death_chance = 0.1
            else:
                death_chance = 0.01  # Rare early death
            
            if self.rng.random() < death_chance:
                self._kill_figure(figure, year, "natural causes")
    
    def _kill_figure(self, figure: HistoricalFigure, year: int, cause: str = "natural causes"):
        """Mark figure as deceased."""
        figure.death_year = year
        
        # Track by death year
        if year not in self.figures_by_death_year:
            self.figures_by_death_year[year] = []
        self.figures_by_death_year[year].append(figure.id)
        
        # Remove from living figures
        civ_id = figure.cultural_origin  # Use cultural_origin as civilization ID
        for civilization_id, living_ids in self.living_figures.items():
            if figure.id in living_ids:
                living_ids.remove(figure.id)
                break
    
    def _process_births(self, year: int) -> List[HistoricalFigure]:
        """Generate new births from fertile couples."""
        new_figures = []
        
        # Find potential parent couples
        for civ_id, living_ids in self.living_figures.items():
            living_in_civ = [f for f in self.figures if f.id in living_ids]
            
            # Find married couples of childbearing age
            processed_couples = set()
            
            for figure in living_in_civ:
                if not figure.spouse or figure.spouse in processed_couples:
                    continue
                
                # Get spouse
                spouse = next((f for f in self.figures if f.id == figure.spouse), None)
                if not spouse or not self._is_alive(spouse, year):
                    continue
                
                # Check at least one can have children
                can_have = self._can_have_children(figure, year) or self._can_have_children(spouse, year)
                if not can_have:
                    continue
                
                # Mark couple as processed
                processed_couples.add(figure.id)
                processed_couples.add(spouse.id)
                
                # Birth chance (15% per year for fertile couples)
                if self.rng.random() < 0.15:
                    # Determine mother/father
                    if 'female' in figure.name.lower() or self.rng.random() < 0.5:
                        mother, father = figure, spouse
                    else:
                        mother, father = spouse, figure
                    
                    child = self._create_child(mother, father, year)
                    new_figures.append(child)
                    self.figures.append(child)
                    
                    # Add to living figures
                    if civ_id not in self.living_figures:
                        self.living_figures[civ_id] = []
                    self.living_figures[civ_id].append(child.id)
        
        return new_figures
    
    def _create_child(self, mother: HistoricalFigure, father: HistoricalFigure, year: int) -> HistoricalFigure:
        """Create child figure from two parents."""
        figure_id = f"figure-{self.figure_counter:04d}"
        self.figure_counter += 1
        
        # Generate name
        gender = "male" if self.rng.random() < 0.5 else "female"
        name, _ = _generate_name(mother.race, gender, self.rng)
        
        birth_month, birth_day, birth_season = self._generate_random_date(year)
        
        # Inherit social class (with some mobility)
        parent_classes = [mother.backstory, father.backstory]  # Using backstory as proxy for class
        if "ruler" in str(parent_classes) or "noble" in str(parent_classes):
            social_class = "noble"
            role = self.rng.choice(["noble", "warrior", "scholar"])
            archetype = self.rng.choice(HERO_ARCHETYPES[:4])
        else:
            social_class = "commoner"
            role = self.rng.choice(["commoner", "craftsman", "merchant", "warrior"])
            archetype = self.rng.choice(["master_craftsman", "cunning_strategist", "wandering_prophet"])
        
        # Create child
        child = HistoricalFigure(
            id=figure_id,
            name=name,
            title="",
            race=mother.race,
            alignment="hero" if self.rng.random() < 0.9 else "villain",  # 10% villains
            archetype=archetype,
            birth_year=year,
            death_year=None,
            parents=(mother.id, father.id),
            spouse=None,
            children=[],
            participated_in_events=[],
            achievements=[],
            artifacts_owned=[],
            cultural_significance=3,
            memory_strength=2,
            cultural_influence={mother.race: 2},
            remembered_as="commoner" if social_class == "commoner" else "minor noble",
            legendary_status="known",
            backstory=f"Born to {mother.name} and {father.name} in {year}",
            personality_traits=[],
            cultural_origin=mother.cultural_origin
        )
        
        # Add to parents' children lists
        mother.children.append(child.id)
        father.children.append(child.id)
        
        # Track by birth year
        if year not in self.figures_by_birth_year:
            self.figures_by_birth_year[year] = []
        self.figures_by_birth_year[year].append(figure_id)
        
        return child
    
    def _process_marriages(self, year: int):
        """Process marriages between eligible figures."""
        for civ_id, living_ids in self.living_figures.items():
            # Find eligible bachelors/bachelorettes
            eligible = [f for f in self.figures 
                       if f.id in living_ids 
                       and not f.spouse 
                       and (year - f.birth_year) >= 18  # At least 18 years old
                       and (year - f.birth_year) <= 50]  # Not too old
            
            if len(eligible) < 2:
                continue
            
            # Random pairings
            self.rng.shuffle(eligible)
            
            # Pair up eligible figures
            for i in range(0, len(eligible) - 1, 2):
                figure_a = eligible[i]
                figure_b = eligible[i + 1]
                
                # 10% chance of marriage per year for eligible pair
                if self.rng.random() < 0.1:
                    self._marry_figures(figure_a, figure_b, year)
    
    def _marry_figures(self, figure_a: HistoricalFigure, figure_b: HistoricalFigure, year: int):
        """Create marriage between two figures."""
        figure_a.spouse = figure_b.id
        figure_b.spouse = figure_a.id
        
        # Add to achievements
        figure_a.achievements.append(f"Married {figure_b.name} in {year}")
        figure_b.achievements.append(f"Married {figure_a.name} in {year}")
    
    def link_figures_to_event(self, event):
        """Link living figures to a historical event as participants.
        
        Args:
            event: HistoricalEvent object
        """
        participants = []
        
        # Find figures in affected civilizations
        for civ_id in event.primary_civilizations:
            if civ_id in self.living_figures:
                living = [f for f in self.figures 
                         if f.id in self.living_figures[civ_id] 
                         and self._is_alive(f, event.year)]
                
                # Select participants based on event type
                if event.event_type.value in ['war', 'alliance', 'betrayal']:
                    # Rulers and warriors participate
                    candidates = [f for f in living if 'warrior' in f.archetype.lower() 
                                  or 'ruler' in f.archetype.lower() or 'noble' in f.archetype.lower()]
                    if candidates:
                        participants.extend(self.rng.sample(candidates, min(3, len(candidates))))
                
                elif event.event_type.value in ['cultural_movement', 'religious_schism']:
                    # Scholars and prophets participate
                    candidates = [f for f in living if 'wise' in f.archetype.lower() 
                                  or 'prophet' in f.archetype.lower() or 'scholar' in f.archetype.lower()]
                    if candidates:
                        participants.extend(self.rng.sample(candidates, min(2, len(candidates))))
        
        # Link participants to event
        for figure in participants:
            if event.id not in figure.participated_in_events:
                figure.participated_in_events.append(event.id)
                figure.cultural_significance = min(10, figure.cultural_significance + event.significance // 3)
                figure.memory_strength = min(10, figure.memory_strength + event.significance // 4)
                
                # Update legendary status based on participation
                if figure.cultural_significance >= 8:
                    figure.legendary_status = "legendary"
                elif figure.cultural_significance >= 6:
                    figure.legendary_status = "famous"
            
            # Add figure to event's participants
            if hasattr(event, 'key_figures') and figure.id not in event.key_figures:
                event.key_figures.append(figure.id)
    
    def get_figure_by_id(self, figure_id: str) -> Optional[HistoricalFigure]:
        """Get figure by ID."""
        return next((f for f in self.figures if f.id == figure_id), None)
    
    def get_living_count(self) -> int:
        """Get total count of living figures."""
        return sum(len(ids) for ids in self.living_figures.values())
    
    def get_total_count(self) -> int:
        """Get total count of all figures."""
        return len(self.figures)
