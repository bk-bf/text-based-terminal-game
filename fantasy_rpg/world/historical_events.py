"""
Historical Event Simulation System

Generates interconnected historical events creating cause-and-effect chains.
Includes war, succession, disaster, and cultural movement events that affect
civilizations and their relationships.

Event Categories:
- War: Military conflicts between civilizations
- Succession: Leadership changes, crises, civil wars
- Disaster: Natural disasters, plagues, famines
- Cultural: Religious movements, technological advances, social reforms

Integration:
- Civilizations: Affects faction relationships and territories
- HistoricalFigures: Key participants in events
- WorldCoordinator: Stores historical timeline
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import random


class EventType(Enum):
    """Categories of historical events."""
    WAR = "war"
    SUCCESSION = "succession"
    DISASTER = "disaster"
    CULTURAL_MOVEMENT = "cultural_movement"
    ALLIANCE = "alliance"
    BETRAYAL = "betrayal"
    PLAGUE = "plague"
    FAMINE = "famine"
    CIVIL_WAR = "civil_war"
    RELIGIOUS_SCHISM = "religious_schism"
    TECHNOLOGICAL_ADVANCE = "technological_advance"
    TERRITORIAL_EXPANSION = "territorial_expansion"
    ASSASSINATION = "assassination"
    REBELLION = "rebellion"


class EventSeverity(Enum):
    """Impact level of historical events."""
    MINOR = "minor"  # Local impact, few casualties
    MODERATE = "moderate"  # Regional impact, noticeable changes
    MAJOR = "major"  # Civilization-wide impact, significant changes
    CATASTROPHIC = "catastrophic"  # World-changing impact, lasting consequences


@dataclass
class RelationshipChange:
    """Represents a change in faction relationship from an event."""
    civilization_a: str
    civilization_b: str
    old_relationship: str
    new_relationship: str
    reason: str


@dataclass
class TerritorialChange:
    """Represents territorial changes from an event."""
    civilization: str
    hexes_gained: List[Tuple[int, int]]
    hexes_lost: List[Tuple[int, int]]
    reason: str


@dataclass
class HistoricalEvent:
    """
    Represents a historical event affecting civilizations.
    
    Attributes:
        id: Unique identifier
        year: Year the event occurred
        event_type: Category of event
        severity: Impact level
        name: Event name
        description: Narrative description
        primary_civilizations: Main civilizations involved
        affected_civilizations: All civilizations affected
        key_figures: Historical figures who participated
        location: Hex coordinates where event occurred
        duration_years: How long the event lasted
        casualties: Estimated casualties (if applicable)
        relationship_changes: Changes to faction relationships
        territorial_changes: Changes to territorial control
        causes_future_events: Event IDs this event leads to
        caused_by_events: Event IDs that caused this event
        creates_artifacts: Legendary items created by this event
        significance: Historical importance (1-10)
    """
    id: str
    year: int
    event_type: EventType
    severity: EventSeverity
    name: str
    description: str
    primary_civilizations: List[str]
    affected_civilizations: List[str] = field(default_factory=list)
    key_figures: List[int] = field(default_factory=list)
    location: Optional[Tuple[int, int]] = None
    duration_years: int = 0
    casualties: int = 0
    relationship_changes: List[RelationshipChange] = field(default_factory=list)
    territorial_changes: List[TerritorialChange] = field(default_factory=list)
    causes_future_events: List[str] = field(default_factory=list)
    caused_by_events: List[str] = field(default_factory=list)
    creates_artifacts: List[str] = field(default_factory=list)
    significance: int = 5
    
    def to_dict(self) -> dict:
        """Serialize event to dictionary."""
        return {
            'id': self.id,
            'year': self.year,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'name': self.name,
            'description': self.description,
            'primary_civilizations': self.primary_civilizations,
            'affected_civilizations': self.affected_civilizations,
            'key_figures': self.key_figures,
            'location': self.location,
            'duration_years': self.duration_years,
            'casualties': self.casualties,
            'relationship_changes': [
                {
                    'civilization_a': rc.civilization_a,
                    'civilization_b': rc.civilization_b,
                    'old_relationship': rc.old_relationship,
                    'new_relationship': rc.new_relationship,
                    'reason': rc.reason
                }
                for rc in self.relationship_changes
            ],
            'territorial_changes': [
                {
                    'civilization': tc.civilization,
                    'hexes_gained': tc.hexes_gained,
                    'hexes_lost': tc.hexes_lost,
                    'reason': tc.reason
                }
                for tc in self.territorial_changes
            ],
            'causes_future_events': self.causes_future_events,
            'caused_by_events': self.caused_by_events,
            'creates_artifacts': self.creates_artifacts,
            'significance': self.significance
        }


class HistoricalEventGenerator:
    """Generates historical events with cause-and-effect chains."""
    
    def __init__(self, world_coordinator, seed: Optional[int] = None):
        """Initialize event generator.
        
        Args:
            world_coordinator: WorldCoordinator with civilizations and hex data
            seed: Random seed for reproducibility
        """
        self.world = world_coordinator
        self.rng = random.Random(seed)
        self.events: List[HistoricalEvent] = []
        self.event_counter = 0
        
    def generate_historical_timeline(self, years: int = 200) -> List[HistoricalEvent]:
        """Generate a timeline of interconnected historical events.
        
        Args:
            years: Number of years of history to simulate (default 200)
            
        Returns:
            List of historical events in chronological order
        """
        if not hasattr(self.world, 'civilizations') or not self.world.civilizations:
            return []
        
        # Start from the youngest civilization's founding
        start_year = min(civ.founded_year for civ in self.world.civilizations)
        current_year = start_year
        end_year = current_year + years
        
        # Initialize faction relationships if not set
        self._initialize_relationships()
        
        # Generate events year by year
        while current_year <= end_year:
            # Chance of event occurring this year (roughly 1 event per 2-5 years)
            if self.rng.random() < 0.3:
                event = self._generate_event(current_year)
                if event:
                    self.events.append(event)
                    self._apply_event_effects(event)
            
            current_year += 1
        
        return sorted(self.events, key=lambda e: e.year)
    
    def _initialize_relationships(self):
        """Initialize faction relationships between civilizations."""
        from .civilizations import RelationshipLevel
        
        civs = self.world.civilizations
        
        for i, civ_a in enumerate(civs):
            for civ_b in civs[i+1:]:
                # Skip if relationship already exists
                if civ_b.id in civ_a.faction_relationships:
                    continue
                
                # Determine initial relationship based on race and proximity
                relationship = self._determine_initial_relationship(civ_a, civ_b)
                
                civ_a.faction_relationships[civ_b.id] = relationship
                civ_b.faction_relationships[civ_a.id] = relationship
    
    def _determine_initial_relationship(self, civ_a, civ_b) -> 'RelationshipLevel':
        """Determine initial relationship between two civilizations."""
        from .civilizations import RelationshipLevel
        
        # Same primary race = more likely friendly
        if civ_a.race == civ_b.race:
            weights = [0.05, 0.3, 0.5, 0.1, 0.05, 0.0]  # allied, friendly, neutral, tense, hostile, at_war
        else:
            weights = [0.0, 0.2, 0.6, 0.15, 0.05, 0.0]  # More neutral, less friendly
        
        # Check territorial proximity (if territories exist)
        if civ_a.territory and civ_b.territory:
            # Check if territories are adjacent
            if self._are_territories_adjacent(civ_a.territory, civ_b.territory):
                # Adjacent territories = more potential for conflict
                weights = [w * 0.5 for w in weights]  # Reduce friendly weights
                weights[3] *= 1.5  # Increase tense
                weights[4] *= 1.2  # Increase hostile
        
        relationships = [
            RelationshipLevel.ALLIED,
            RelationshipLevel.FRIENDLY,
            RelationshipLevel.NEUTRAL,
            RelationshipLevel.TENSE,
            RelationshipLevel.HOSTILE,
            RelationshipLevel.AT_WAR
        ]
        
        # Normalize weights
        total = sum(weights)
        if total > 0:
            weights = [w/total for w in weights]
        
        return self.rng.choices(relationships, weights=weights)[0]
    
    def _are_territories_adjacent(self, territory_a, territory_b) -> bool:
        """Check if two territories share a border."""
        for hex_a in territory_a.hex_coordinates:
            for neighbor in self._get_adjacent_hexes(hex_a):
                if neighbor in territory_b.hex_coordinates:
                    return True
        return False
    
    def _get_adjacent_hexes(self, hex_coord: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get adjacent hex coordinates."""
        x, y = hex_coord
        # Hex grid neighbors (offset coordinates)
        if y % 2 == 0:  # Even row
            neighbors = [
                (x, y-1), (x+1, y-1),
                (x-1, y), (x+1, y),
                (x, y+1), (x+1, y+1)
            ]
        else:  # Odd row
            neighbors = [
                (x-1, y-1), (x, y-1),
                (x-1, y), (x+1, y),
                (x-1, y+1), (x, y+1)
            ]
        return neighbors
    
    def _generate_event(self, year: int) -> Optional[HistoricalEvent]:
        """Generate a single historical event for the given year."""
        # Determine event type
        event_type = self._choose_event_type()
        
        # Generate event based on type
        if event_type == EventType.WAR:
            return self._generate_war_event(year)
        elif event_type == EventType.SUCCESSION:
            return self._generate_succession_event(year)
        elif event_type == EventType.DISASTER:
            return self._generate_disaster_event(year)
        elif event_type == EventType.CULTURAL_MOVEMENT:
            return self._generate_cultural_event(year)
        elif event_type == EventType.ALLIANCE:
            return self._generate_alliance_event(year)
        elif event_type == EventType.BETRAYAL:
            return self._generate_betrayal_event(year)
        
        return None
    
    def _choose_event_type(self) -> EventType:
        """Choose a random event type with weighted probabilities."""
        event_types = [
            EventType.WAR,
            EventType.SUCCESSION,
            EventType.DISASTER,
            EventType.CULTURAL_MOVEMENT,
            EventType.ALLIANCE,
            EventType.BETRAYAL,
        ]
        
        weights = [0.25, 0.20, 0.15, 0.20, 0.15, 0.05]
        
        return self.rng.choices(event_types, weights=weights)[0]
    
    def _generate_war_event(self, year: int) -> Optional[HistoricalEvent]:
        """Generate a war event between civilizations."""
        from .civilizations import RelationshipLevel
        
        # Find civilizations with hostile/tense relationships
        potential_conflicts = []
        for civ_a in self.world.civilizations:
            for civ_b_id, relationship in civ_a.faction_relationships.items():
                if relationship in [RelationshipLevel.HOSTILE, RelationshipLevel.TENSE]:
                    civ_b = next((c for c in self.world.civilizations if c.id == civ_b_id), None)
                    if civ_b and (civ_a.id, civ_b.id) not in [(a, b) for a, b in potential_conflicts]:
                        potential_conflicts.append((civ_a, civ_b))
        
        if not potential_conflicts:
            # No hostile relationships, pick random pair
            if len(self.world.civilizations) < 2:
                return None
            civ_a = self.rng.choice(self.world.civilizations)
            others = [c for c in self.world.civilizations if c.id != civ_a.id]
            civ_b = self.rng.choice(others)
        else:
            civ_a, civ_b = self.rng.choice(potential_conflicts)
        
        # Generate war details
        event_id = f"war-{self.event_counter}"
        self.event_counter += 1
        
        # Determine severity based on civilization sizes
        total_pop = civ_a.population + civ_b.population
        if total_pop > 500000:
            severity = EventSeverity.CATASTROPHIC
        elif total_pop > 200000:
            severity = EventSeverity.MAJOR
        elif total_pop > 100000:
            severity = EventSeverity.MODERATE
        else:
            severity = EventSeverity.MINOR
        
        # Generate war name
        war_names = [
            f"The {civ_a.name}-{civ_b.name} War",
            f"The War of {self._get_territory_name(civ_a)}",
            f"The {year} Conflict",
            f"The Border War",
            f"The {self._get_cultural_value_name(civ_a)} War"
        ]
        name = self.rng.choice(war_names)
        
        # Generate description
        casus_belli = self.rng.choice([
            "territorial disputes",
            "trade route control",
            "historical grievances",
            "religious differences",
            "resource competition",
            "political ambitions"
        ])
        
        duration = self.rng.randint(1, 10)
        casualties = int((civ_a.population + civ_b.population) * self.rng.uniform(0.01, 0.15))
        
        description = (
            f"A {'devastating' if severity == EventSeverity.CATASTROPHIC else 'major' if severity == EventSeverity.MAJOR else 'significant'} "
            f"military conflict between {civ_a.name} and {civ_b.name} sparked by {casus_belli}. "
            f"The war lasted {duration} years and resulted in approximately {casualties:,} casualties."
        )
        
        # Determine winner (or stalemate)
        outcome = self.rng.choice(['civ_a_wins', 'civ_b_wins', 'stalemate'])
        
        # Create relationship changes
        relationship_changes = []
        new_relationship = RelationshipLevel.HOSTILE if outcome == 'stalemate' else RelationshipLevel.TENSE
        old_relationship = civ_a.faction_relationships.get(civ_b.id, RelationshipLevel.NEUTRAL)
        
        relationship_changes.append(RelationshipChange(
            civilization_a=civ_a.id,
            civilization_b=civ_b.id,
            old_relationship=old_relationship.value,
            new_relationship=new_relationship.value,
            reason=f"War of {year}"
        ))
        
        # Create territorial changes if there's a winner
        territorial_changes = []
        if outcome != 'stalemate' and civ_a.territory and civ_b.territory:
            winner = civ_a if outcome == 'civ_a_wins' else civ_b
            loser = civ_b if outcome == 'civ_a_wins' else civ_a
            
            # Transfer some border hexes
            border_hexes = self._find_border_hexes(loser.territory, winner.territory)
            if border_hexes:
                num_hexes = max(1, len(border_hexes) // 4)  # Take 25% of border
                hexes_lost = self.rng.sample(border_hexes, min(num_hexes, len(border_hexes)))
                
                territorial_changes.append(TerritorialChange(
                    civilization=winner.id,
                    hexes_gained=hexes_lost,
                    hexes_lost=[],
                    reason=f"Conquered in {name}"
                ))
                
                territorial_changes.append(TerritorialChange(
                    civilization=loser.id,
                    hexes_gained=[],
                    hexes_lost=hexes_lost,
                    reason=f"Lost in {name}"
                ))
                
                description += f" {winner.name} emerged victorious, claiming key territories."
            else:
                description += f" Despite {winner.name}'s victory, no significant territorial changes occurred."
        elif outcome == 'stalemate':
            description += " The conflict ended in a costly stalemate with no clear victor."
        
        # Location is battlefield (border between territories or random location)
        location = self._find_battlefield_location(civ_a, civ_b)
        
        return HistoricalEvent(
            id=event_id,
            year=year,
            event_type=EventType.WAR,
            severity=severity,
            name=name,
            description=description,
            primary_civilizations=[civ_a.id, civ_b.id],
            affected_civilizations=[civ_a.id, civ_b.id],
            location=location,
            duration_years=duration,
            casualties=casualties,
            relationship_changes=relationship_changes,
            territorial_changes=territorial_changes,
            significance=6 + (2 if severity == EventSeverity.CATASTROPHIC else 1 if severity == EventSeverity.MAJOR else 0)
        )
    
    def _generate_succession_event(self, year: int) -> Optional[HistoricalEvent]:
        """Generate a succession crisis or leadership change event."""
        if not self.world.civilizations:
            return None
        
        civ = self.rng.choice(self.world.civilizations)
        
        event_id = f"succession-{self.event_counter}"
        self.event_counter += 1
        
        # Determine type of succession event
        succession_types = [
            'peaceful_transition',
            'contested_succession',
            'civil_war',
            'coup',
            'assassination'
        ]
        
        succession_type = self.rng.choice(succession_types)
        
        if succession_type == 'peaceful_transition':
            severity = EventSeverity.MINOR
            name = f"The Succession of {year}"
            description = (
                f"A peaceful transition of power occurred in {civ.name}. "
                f"The new leader was accepted by all major factions, maintaining stability."
            )
            duration = 0
            casualties = 0
            
        elif succession_type == 'contested_succession':
            severity = EventSeverity.MODERATE
            name = f"The {civ.name} Succession Crisis"
            description = (
                f"Multiple claimants vied for leadership in {civ.name}, leading to "
                f"months of political turmoil. The crisis was eventually resolved through "
                f"{'negotiation' if self.rng.random() < 0.5 else 'force'}."
            )
            duration = self.rng.randint(0, 2)
            casualties = int(civ.population * self.rng.uniform(0.001, 0.01))
            
        elif succession_type == 'civil_war':
            severity = EventSeverity.MAJOR
            name = f"The {civ.name} Civil War"
            description = (
                f"A devastating civil war erupted in {civ.name} as rival factions "
                f"fought for control. The conflict tore the civilization apart, "
                f"leaving lasting scars on its people and institutions."
            )
            duration = self.rng.randint(2, 8)
            casualties = int(civ.population * self.rng.uniform(0.05, 0.20))
            
        elif succession_type == 'coup':
            severity = EventSeverity.MODERATE
            name = f"The {year} Coup"
            description = (
                f"A military coup overthrew the existing leadership in {civ.name}. "
                f"The new regime quickly consolidated power, though {'resistance movements formed' if self.rng.random() < 0.5 else 'opposition was swiftly crushed'}."
            )
            duration = 0
            casualties = int(civ.population * self.rng.uniform(0.0001, 0.005))
            
        else:  # assassination
            severity = EventSeverity.MODERATE
            name = f"The Assassination of {year}"
            description = (
                f"The leader of {civ.name} was assassinated, plunging the civilization into uncertainty. "
                f"{'A power vacuum emerged as factions maneuvered for position' if self.rng.random() < 0.5 else 'A successor was quickly appointed to prevent chaos'}."
            )
            duration = 0
            casualties = 1
        
        location = civ.territory.capital_hex if civ.territory else None
        
        return HistoricalEvent(
            id=event_id,
            year=year,
            event_type=EventType.SUCCESSION if succession_type != 'civil_war' else EventType.CIVIL_WAR,
            severity=severity,
            name=name,
            description=description,
            primary_civilizations=[civ.id],
            affected_civilizations=[civ.id],
            location=location,
            duration_years=duration,
            casualties=casualties,
            significance=4 + (2 if severity == EventSeverity.MAJOR else 1 if severity == EventSeverity.MODERATE else 0)
        )
    
    def _generate_disaster_event(self, year: int) -> Optional[HistoricalEvent]:
        """Generate a natural disaster or plague event."""
        disaster_types = [
            ('earthquake', 'A devastating earthquake'),
            ('flood', 'Catastrophic flooding'),
            ('drought', 'A prolonged drought'),
            ('plague', 'A deadly plague'),
            ('famine', 'A severe famine'),
            ('volcanic_eruption', 'A volcanic eruption'),
            ('hurricane', 'A powerful hurricane'),
            ('wildfire', 'Massive wildfires')
        ]
        
        disaster_type, disaster_desc = self.rng.choice(disaster_types)
        
        event_id = f"disaster-{self.event_counter}"
        self.event_counter += 1
        
        # Choose affected civilization(s)
        num_affected = self.rng.choices([1, 2, 3], weights=[0.7, 0.25, 0.05])[0]
        affected_civs = self.rng.sample(self.world.civilizations, min(num_affected, len(self.world.civilizations)))
        
        # Determine severity
        severity_weights = [0.5, 0.3, 0.15, 0.05]  # minor, moderate, major, catastrophic
        severity = self.rng.choices(
            [EventSeverity.MINOR, EventSeverity.MODERATE, EventSeverity.MAJOR, EventSeverity.CATASTROPHIC],
            weights=severity_weights
        )[0]
        
        # Calculate impact
        total_pop = sum(civ.population for civ in affected_civs)
        if severity == EventSeverity.CATASTROPHIC:
            casualty_rate = self.rng.uniform(0.10, 0.30)
        elif severity == EventSeverity.MAJOR:
            casualty_rate = self.rng.uniform(0.05, 0.15)
        elif severity == EventSeverity.MODERATE:
            casualty_rate = self.rng.uniform(0.01, 0.05)
        else:
            casualty_rate = self.rng.uniform(0.001, 0.01)
        
        casualties = int(total_pop * casualty_rate)
        
        # Generate description
        affected_names = ", ".join(civ.name for civ in affected_civs)
        
        description = (
            f"{disaster_desc} struck {affected_names}, causing widespread devastation. "
            f"Approximately {casualties:,} lives were lost, and "
        )
        
        if severity == EventSeverity.CATASTROPHIC:
            description += "entire regions were laid to waste. The disaster's effects would be felt for generations."
        elif severity == EventSeverity.MAJOR:
            description += "many settlements were destroyed. Recovery would take decades."
        elif severity == EventSeverity.MODERATE:
            description += "significant damage occurred to infrastructure and agriculture."
        else:
            description += "localized damage tested the resilience of affected communities."
        
        # Location (random hex from affected civilization)
        location = None
        if affected_civs and affected_civs[0].territory:
            location = self.rng.choice(affected_civs[0].territory.hex_coordinates)
        
        name = f"The {year} {disaster_type.replace('_', ' ').title()}"
        
        return HistoricalEvent(
            id=event_id,
            year=year,
            event_type=EventType.PLAGUE if disaster_type == 'plague' else EventType.FAMINE if disaster_type == 'famine' else EventType.DISASTER,
            severity=severity,
            name=name,
            description=description,
            primary_civilizations=[civ.id for civ in affected_civs],
            affected_civilizations=[civ.id for civ in affected_civs],
            location=location,
            duration_years=self.rng.randint(0, 3) if disaster_type in ['plague', 'drought', 'famine'] else 0,
            casualties=casualties,
            significance=3 + (3 if severity == EventSeverity.CATASTROPHIC else 2 if severity == EventSeverity.MAJOR else 1 if severity == EventSeverity.MODERATE else 0)
        )
    
    def _generate_cultural_event(self, year: int) -> Optional[HistoricalEvent]:
        """Generate a cultural movement or social change event."""
        cultural_types = [
            ('religious_movement', 'A new religious movement'),
            ('technological_advance', 'A technological breakthrough'),
            ('artistic_renaissance', 'An artistic renaissance'),
            ('social_reform', 'Major social reforms'),
            ('educational_expansion', 'Expansion of education'),
            ('trade_boom', 'A trade boom'),
            ('architectural_achievement', 'Architectural marvels')
        ]
        
        cultural_type, cultural_desc = self.rng.choice(cultural_types)
        
        event_id = f"cultural-{self.event_counter}"
        self.event_counter += 1
        
        # Choose originating civilization
        civ = self.rng.choice(self.world.civilizations)
        
        # Cultural events can spread to neighbors
        affected_civs = [civ]
        if self.rng.random() < 0.4:  # 40% chance to spread
            # Find friendly/allied neighbors
            for other_civ_id, relationship in civ.faction_relationships.items():
                from .civilizations import RelationshipLevel
                if relationship in [RelationshipLevel.ALLIED, RelationshipLevel.FRIENDLY]:
                    other_civ = next((c for c in self.world.civilizations if c.id == other_civ_id), None)
                    if other_civ and self.rng.random() < 0.6:
                        affected_civs.append(other_civ)
        
        severity = EventSeverity.MODERATE if len(affected_civs) > 1 else EventSeverity.MINOR
        
        # Generate description
        affected_names = civ.name if len(affected_civs) == 1 else f"{civ.name} and neighboring civilizations"
        
        name = f"The {year} {cultural_type.replace('_', ' ').title()}"
        
        if cultural_type == 'religious_movement':
            description = (
                f"{cultural_desc} emerged in {affected_names}, "
                f"{'reshaping spiritual beliefs and social structures' if severity == EventSeverity.MODERATE else 'gaining followers and influence'}."
            )
        elif cultural_type == 'technological_advance':
            tech_type = self.rng.choice(['metallurgy', 'agriculture', 'construction', 'navigation', 'medicine'])
            description = (
                f"A breakthrough in {tech_type} occurred in {affected_names}, "
                f"{'revolutionizing society and economy' if severity == EventSeverity.MODERATE else 'improving quality of life'}."
            )
        elif cultural_type == 'artistic_renaissance':
            description = (
                f"An artistic renaissance flourished in {affected_names}, producing "
                f"{'masterworks that would define an era' if severity == EventSeverity.MODERATE else 'notable cultural achievements'}."
            )
        elif cultural_type == 'social_reform':
            reform_type = self.rng.choice(['labor rights', 'legal codes', 'gender equality', 'class mobility'])
            description = (
                f"Major reforms regarding {reform_type} transformed {affected_names}, "
                f"{'fundamentally altering social structures' if severity == EventSeverity.MODERATE else 'improving conditions for many'}."
            )
        elif cultural_type == 'educational_expansion':
            description = (
                f"A dramatic expansion of education in {affected_names} "
                f"{'created a new intellectual class' if severity == EventSeverity.MODERATE else 'increased literacy and knowledge'}."
            )
        elif cultural_type == 'trade_boom':
            description = (
                f"A trade boom in {affected_names} brought unprecedented prosperity, "
                f"{'establishing new trade routes and economic power' if severity == EventSeverity.MODERATE else 'enriching merchants and cities'}."
            )
        else:  # architectural_achievement
            description = (
                f"Remarkable architectural achievements in {affected_names} "
                f"{'redefined engineering and inspired generations' if severity == EventSeverity.MODERATE else 'demonstrated cultural sophistication'}."
            )
        
        location = civ.territory.capital_hex if civ.territory else None
        
        return HistoricalEvent(
            id=event_id,
            year=year,
            event_type=EventType.TECHNOLOGICAL_ADVANCE if cultural_type == 'technological_advance' else EventType.RELIGIOUS_SCHISM if cultural_type == 'religious_movement' else EventType.CULTURAL_MOVEMENT,
            severity=severity,
            name=name,
            description=description,
            primary_civilizations=[civ.id],
            affected_civilizations=[c.id for c in affected_civs],
            location=location,
            significance=4 + (1 if severity == EventSeverity.MODERATE else 0)
        )
    
    def _generate_alliance_event(self, year: int) -> Optional[HistoricalEvent]:
        """Generate an alliance formation event."""
        from .civilizations import RelationshipLevel
        
        # Find civilizations with neutral or friendly relationships
        potential_alliances = []
        for civ_a in self.world.civilizations:
            for civ_b_id, relationship in civ_a.faction_relationships.items():
                if relationship in [RelationshipLevel.NEUTRAL, RelationshipLevel.FRIENDLY]:
                    civ_b = next((c for c in self.world.civilizations if c.id == civ_b_id), None)
                    if civ_b and (civ_a.id, civ_b.id) not in [(a, b) for a, b in potential_alliances]:
                        potential_alliances.append((civ_a, civ_b))
        
        if not potential_alliances:
            return None
        
        civ_a, civ_b = self.rng.choice(potential_alliances)
        
        event_id = f"alliance-{self.event_counter}"
        self.event_counter += 1
        
        name = f"The {civ_a.name}-{civ_b.name} Alliance"
        
        alliance_reason = self.rng.choice([
            "mutual defense against common threats",
            "economic cooperation and trade",
            "cultural and religious ties",
            "dynastic marriage",
            "shared strategic interests"
        ])
        
        description = (
            f"{civ_a.name} and {civ_b.name} formed a formal alliance based on {alliance_reason}. "
            f"The alliance strengthened both civilizations and {'reshaped regional politics' if self.rng.random() < 0.5 else 'created new opportunities for cooperation'}."
        )
        
        # Create relationship change
        old_relationship = civ_a.faction_relationships.get(civ_b.id, RelationshipLevel.NEUTRAL)
        new_relationship = RelationshipLevel.ALLIED if old_relationship == RelationshipLevel.FRIENDLY else RelationshipLevel.FRIENDLY
        
        relationship_changes = [RelationshipChange(
            civilization_a=civ_a.id,
            civilization_b=civ_b.id,
            old_relationship=old_relationship.value,
            new_relationship=new_relationship.value,
            reason=f"Alliance of {year}"
        )]
        
        return HistoricalEvent(
            id=event_id,
            year=year,
            event_type=EventType.ALLIANCE,
            severity=EventSeverity.MODERATE,
            name=name,
            description=description,
            primary_civilizations=[civ_a.id, civ_b.id],
            affected_civilizations=[civ_a.id, civ_b.id],
            relationship_changes=relationship_changes,
            significance=5
        )
    
    def _generate_betrayal_event(self, year: int) -> Optional[HistoricalEvent]:
        """Generate a betrayal event breaking an alliance."""
        from .civilizations import RelationshipLevel
        
        # Find allied civilizations
        allied_pairs = []
        for civ_a in self.world.civilizations:
            for civ_b_id, relationship in civ_a.faction_relationships.items():
                if relationship == RelationshipLevel.ALLIED:
                    civ_b = next((c for c in self.world.civilizations if c.id == civ_b_id), None)
                    if civ_b and (civ_a.id, civ_b.id) not in [(a, b) for a, b in allied_pairs]:
                        allied_pairs.append((civ_a, civ_b))
        
        if not allied_pairs:
            return None
        
        civ_a, civ_b = self.rng.choice(allied_pairs)
        
        event_id = f"betrayal-{self.event_counter}"
        self.event_counter += 1
        
        betrayer = self.rng.choice([civ_a, civ_b])
        betrayed = civ_b if betrayer == civ_a else civ_a
        
        name = f"The Betrayal of {year}"
        
        betrayal_reason = self.rng.choice([
            "secret negotiations with enemies",
            "disputed territory",
            "broken treaty terms",
            "economic rivalry",
            "leadership change and new ambitions"
        ])
        
        description = (
            f"{betrayer.name} betrayed their alliance with {betrayed.name} due to {betrayal_reason}. "
            f"The betrayal {'shocked the known world and destroyed trust between civilizations' if self.rng.random() < 0.5 else 'left lasting wounds and resentment'}."
        )
        
        # Create relationship change
        relationship_changes = [RelationshipChange(
            civilization_a=civ_a.id,
            civilization_b=civ_b.id,
            old_relationship=RelationshipLevel.ALLIED.value,
            new_relationship=RelationshipLevel.HOSTILE.value,
            reason=f"Betrayal of {year}"
        )]
        
        return HistoricalEvent(
            id=event_id,
            year=year,
            event_type=EventType.BETRAYAL,
            severity=EventSeverity.MAJOR,
            name=name,
            description=description,
            primary_civilizations=[betrayer.id, betrayed.id],
            affected_civilizations=[civ_a.id, civ_b.id],
            relationship_changes=relationship_changes,
            significance=7
        )
    
    def _apply_event_effects(self, event: HistoricalEvent):
        """Apply the effects of an event to the world state."""
        from .civilizations import RelationshipLevel
        
        # Apply relationship changes
        for change in event.relationship_changes:
            civ_a = next((c for c in self.world.civilizations if c.id == change.civilization_a), None)
            civ_b = next((c for c in self.world.civilizations if c.id == change.civilization_b), None)
            
            if civ_a and civ_b:
                new_rel = RelationshipLevel(change.new_relationship)
                civ_a.faction_relationships[civ_b.id] = new_rel
                civ_b.faction_relationships[civ_a.id] = new_rel
        
        # Apply territorial changes
        for change in event.territorial_changes:
            civ = next((c for c in self.world.civilizations if c.id == change.civilization), None)
            if civ and civ.territory:
                # Add gained hexes
                for hex_coord in change.hexes_gained:
                    if hex_coord not in civ.territory.hex_coordinates:
                        civ.territory.hex_coordinates.append(hex_coord)
                
                # Remove lost hexes
                for hex_coord in change.hexes_lost:
                    if hex_coord in civ.territory.hex_coordinates:
                        civ.territory.hex_coordinates.remove(hex_coord)
                
                # Update population estimate
                civ.territory.population_estimate = len(civ.territory.hex_coordinates) * (civ.population // max(1, len(civ.territory.hex_coordinates)))
        
        # Add event to civilization's major events
        for civ_id in event.primary_civilizations:
            civ = next((c for c in self.world.civilizations if c.id == civ_id), None)
            if civ:
                civ.major_events.append(event.id)
    
    # Helper methods
    def _get_territory_name(self, civ) -> str:
        """Get a territory name for event descriptions."""
        if civ.territory:
            return self.rng.choice([
                "the borderlands",
                "the highlands",
                "the fertile valleys",
                "the contested territories",
                "the ancestral lands"
            ])
        return "the region"
    
    def _get_cultural_value_name(self, civ) -> str:
        """Get a cultural value for event naming."""
        if civ.cultural_values:
            value = self.rng.choice(civ.cultural_values)
            return value.value.replace('_', ' ').title()
        return "Honor"
    
    def _find_battlefield_location(self, civ_a, civ_b) -> Optional[Tuple[int, int]]:
        """Find a battlefield location between two civilizations."""
        if not (civ_a.territory and civ_b.territory):
            return None
        
        # Find border hexes
        border_hexes = []
        for hex_a in civ_a.territory.hex_coordinates:
            for neighbor in self._get_adjacent_hexes(hex_a):
                if neighbor in civ_b.territory.hex_coordinates:
                    border_hexes.append(hex_a)
                    break
        
        return self.rng.choice(border_hexes) if border_hexes else None
    
    def _find_border_hexes(self, territory_a, territory_b) -> List[Tuple[int, int]]:
        """Find hexes in territory_a that border territory_b."""
        border_hexes = []
        for hex_a in territory_a.hex_coordinates:
            for neighbor in self._get_adjacent_hexes(hex_a):
                if neighbor in territory_b.hex_coordinates:
                    border_hexes.append(hex_a)
                    break
        return border_hexes
