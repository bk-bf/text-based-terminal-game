"""
Civilization Generation System

Creates distinct civilizations with unique cultures, governments, and territorial claims.
Each civilization has cultural identity, value systems, and historical development.

Integration:
- WorldCoordinator: Generates civilizations during world creation
- HistoricalFigures: Associates founding figures with civilizations
- SaveManager: Persists civilization state
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
from enum import Enum
import random


class GovernmentType(Enum):
    """Government structures for civilizations."""
    MONARCHY = "monarchy"
    REPUBLIC = "republic"
    THEOCRACY = "theocracy"
    OLIGARCHY = "oligarchy"
    TRIBAL_COUNCIL = "tribal_council"
    MAGOCRACY = "magocracy"
    MILITARY_DICTATORSHIP = "military_dictatorship"
    DEMOCRACY = "democracy"
    CLAN_CONFEDERATION = "clan_confederation"
    EMPIRE = "empire"


class CulturalValue(Enum):
    """Core values that define civilization culture."""
    HONOR = "honor"
    KNOWLEDGE = "knowledge"
    WEALTH = "wealth"
    MILITARY_MIGHT = "military_might"
    TRADITION = "tradition"
    INNOVATION = "innovation"
    NATURE = "nature"
    MAGIC = "magic"
    CRAFTSMANSHIP = "craftsmanship"
    FREEDOM = "freedom"
    ORDER = "order"
    FAITH = "faith"
    FAMILY = "family"
    GLORY = "glory"
    SURVIVAL = "survival"


class RelationshipLevel(Enum):
    """Relationship status between civilizations."""
    ALLIED = "allied"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    TENSE = "tense"
    HOSTILE = "hostile"
    AT_WAR = "at_war"


@dataclass
class Territory:
    """Represents territorial claims of a civilization."""
    hex_coordinates: List[Tuple[int, int]]
    capital_hex: Tuple[int, int]
    population_estimate: int
    territorial_description: str


@dataclass
class Civilization:
    """
    Represents a distinct civilization with unique culture and identity.
    
    Attributes:
        id: Unique identifier
        name: Civilization name
        race: Primary race (human, elf, dwarf, etc.) or "mixed" for cosmopolitan
        races: List of races in civilization (for mixed civs, single item for mono-racial)
        race_percentages: Dict of race -> percentage for mixed civilizations
        founded_year: Year of establishment
        government_type: Political structure
        cultural_values: List of 2-3 core values
        religious_beliefs: Brief description of faith/spirituality
        cultural_description: Narrative description of culture
        founding_figures: IDs of historical figures who founded civilization
        territory: Territorial claims and capital location
        population: Estimated population
        faction_relationships: Relations with other civilizations
        current_leader: Current ruler (if applicable)
        notable_features: Unique cultural traits
    """
    # Required fields (no defaults)
    id: str
    name: str
    race: str  # "mixed" for cosmopolitan civilizations
    founded_year: int
    government_type: GovernmentType
    cultural_values: List[CulturalValue]
    religious_beliefs: str
    cultural_description: str
    
    # Optional fields (with defaults)
    races: List[str] = field(default_factory=list)  # All races in civilization
    race_percentages: Dict[str, int] = field(default_factory=dict)  # Race -> percentage
    founding_figures: List[int] = field(default_factory=list)
    major_events: List[int] = field(default_factory=list)
    territory: Optional[Territory] = None
    population: int = 0
    current_leader: Optional[int] = None
    faction_relationships: Dict[str, RelationshipLevel] = field(default_factory=dict)
    notable_features: List[str] = field(default_factory=list)
    territorial_history: List[Dict[str, any]] = field(default_factory=list)  # Year -> {hexes, event_id, reason}
    
    def to_dict(self) -> dict:
        """Serialize civilization to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'race': self.race,
            'races': self.races,
            'race_percentages': self.race_percentages,
            'founded_year': self.founded_year,
            'government_type': self.government_type.value,
            'cultural_values': [v.value for v in self.cultural_values],
            'religious_beliefs': self.religious_beliefs,
            'cultural_description': self.cultural_description,
            'founding_figures': self.founding_figures,
            'major_events': self.major_events,
            'territory': {
                'hex_coordinates': self.territory.hex_coordinates,
                'capital_hex': self.territory.capital_hex,
                'population_estimate': self.territory.population_estimate,
                'territorial_description': self.territory.territorial_description
            } if self.territory else None,
            'population': self.population,
            'current_leader': self.current_leader,
            'faction_relationships': {k: v.value for k, v in self.faction_relationships.items()},
            'notable_features': self.notable_features,
            'territorial_history': self.territorial_history
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Civilization':
        """Deserialize civilization from dictionary."""
        territory = None
        if data.get('territory'):
            territory = Territory(
                hex_coordinates=data['territory']['hex_coordinates'],
                capital_hex=tuple(data['territory']['capital_hex']),
                population_estimate=data['territory']['population_estimate'],
                territorial_description=data['territory']['territorial_description']
            )
        
        return cls(
            id=data['id'],
            name=data['name'],
            race=data['race'],
            races=data.get('races', [data['race']]),
            race_percentages=data.get('race_percentages', {data['race']: 100}),
            founded_year=data['founded_year'],
            government_type=GovernmentType(data['government_type']),
            cultural_values=[CulturalValue(v) for v in data['cultural_values']],
            religious_beliefs=data['religious_beliefs'],
            cultural_description=data['cultural_description'],
            founding_figures=data.get('founding_figures', []),
            major_events=data.get('major_events', []),
            territory=territory,
            population=data.get('population', 0),
            current_leader=data.get('current_leader'),
            faction_relationships={k: RelationshipLevel(v) for k, v in data.get('faction_relationships', {}).items()},
            notable_features=data.get('notable_features', []),
            territorial_history=data.get('territorial_history', [])
        )


# Civilization Archetypes by Race
CIVILIZATION_ARCHETYPES = {
    "human": {
        "name_templates": [
            "{adjective} Kingdom of {place}",
            "The {adjective} Empire",
            "{place} Confederation",
            "Free Cities of {place}",
            "The {adjective} Realm"
        ],
        "adjectives": ["Golden", "Iron", "Silver", "Crimson", "Azure", "Emerald", "United", "Holy", "Imperial"],
        "places": ["Avalon", "Camelot", "Nordmark", "Southreach", "Westmarch", "Easthold", "Heartland"],
        "governments": [
            (GovernmentType.MONARCHY, 0.35),
            (GovernmentType.EMPIRE, 0.25),
            (GovernmentType.REPUBLIC, 0.15),
            (GovernmentType.DEMOCRACY, 0.10),
            (GovernmentType.OLIGARCHY, 0.10),
            (GovernmentType.THEOCRACY, 0.05)
        ],
        "values": [CulturalValue.GLORY, CulturalValue.WEALTH, CulturalValue.ORDER, CulturalValue.INNOVATION, CulturalValue.MILITARY_MIGHT],
        "religions": [
            "Worship the Pantheon of Light",
            "Follow the Old Gods of the Land",
            "Revere the Sun and Moon deities",
            "Honor ancestral spirits and heroes",
            "Practice diverse faiths with religious tolerance"
        ],
        "features": [
            "Extensive road networks connecting cities",
            "Strong merchant guilds and trade traditions",
            "Professional standing armies",
            "Diverse cultural practices across regions",
            "Renowned universities and centers of learning"
        ],
        "biome_preferences": {
            # Biome -> preference score (0-10)
            "temperate_grassland": 9,
            "temperate_forest": 8,
            "mediterranean": 9,
            "temperate_deciduous_forest": 8,
            "savanna": 7,
            "temperate_plains": 9,
            "coastal": 8,
            "river_valley": 10  # Humans love fertile river valleys
        }
    },
    
    "elf": {
        "name_templates": [
            "{place} Court",
            "The {adjective} Realm of {place}",
            "{place} Enclave",
            "The Eternal {place}",
            "{adjective} Haven"
        ],
        "adjectives": ["Starlight", "Moonlit", "Ancient", "Verdant", "Sylvan", "Celestial", "Twilight"],
        "places": ["Silverpine", "Moonshadow", "Starfall", "Evermist", "Brightwood", "Crystalvale"],
        "governments": [
            (GovernmentType.MONARCHY, 0.40),
            (GovernmentType.OLIGARCHY, 0.30),
            (GovernmentType.MAGOCRACY, 0.20),
            (GovernmentType.REPUBLIC, 0.10)
        ],
        "values": [CulturalValue.TRADITION, CulturalValue.NATURE, CulturalValue.MAGIC, CulturalValue.KNOWLEDGE, CulturalValue.HONOR],
        "religions": [
            "Revere the ancient forest spirits",
            "Worship the Star Goddesses",
            "Follow the Way of the Eternal Tree",
            "Honor the Moon Court deities",
            "Practice nature-based mysticism"
        ],
        "features": [
            "Cities woven into living trees",
            "Masters of arcane arts and ancient lore",
            "Isolation from younger races",
            "Legendary craftsmen of magical items",
            "Deep connection to natural world"
        ],
        "biome_preferences": {
            "temperate_forest": 10,
            "temperate_deciduous_forest": 10,
            "tropical_rainforest": 8,
            "coniferous_forest": 9,
            "temperate_rainforest": 9,
            "woodland": 8,
            "mediterranean": 7
        }
    },
    
    "dwarf": {
        "name_templates": [
            "Clan {name}",
            "The {place} Hold",
            "Kingdom Under {place}",
            "The Deep Halls of {place}",
            "{adjective} Mountain Confederation"
        ],
        "adjectives": ["Iron", "Stone", "Gold", "Steel", "Granite", "Forge"],
        "places": ["Ironpeak", "Stoneheart", "Deepdelve", "Goldvein", "Steelgate", "Hammerhome"],
        "name_clans": ["Ironforge", "Stonefist", "Goldbeard", "Steelhammer", "Battleborn", "Oathkeeper"],
        "governments": [
            (GovernmentType.CLAN_CONFEDERATION, 0.45),
            (GovernmentType.MONARCHY, 0.35),
            (GovernmentType.OLIGARCHY, 0.15),
            (GovernmentType.TRIBAL_COUNCIL, 0.05)
        ],
        "values": [CulturalValue.HONOR, CulturalValue.CRAFTSMANSHIP, CulturalValue.TRADITION, CulturalValue.FAMILY, CulturalValue.WEALTH],
        "religions": [
            "Worship the Forge Father",
            "Honor the Stone Mother",
            "Revere ancestral spirits in the deep",
            "Follow the Path of the Eternal Flame",
            "Venerate the First Smith"
        ],
        "features": [
            "Vast underground cities carved from living rock",
            "Master smiths and miners without equal",
            "Complex clan hierarchy and traditions",
            "Legendary warriors and craftsmen",
            "Ancient grudges remembered for centuries"
        ],
        "biome_preferences": {
            "alpine_mountains": 10,
            "highland": 9,
            "rocky_hills": 9,
            "mountains": 10,
            "underground": 10,  # Dwarves prefer mountains/underground
            "temperate_mountains": 9,
            "tundra": 6  # Can survive but not ideal
        }
    },
    
    "halfling": {
        "name_templates": [
            "The {place} Shire",
            "{adjective} Fields",
            "The {place} Valley",
            "Greenfields of {place}",
            "The Peaceful {place}"
        ],
        "adjectives": ["Green", "Pleasant", "Quiet", "Merry", "Comfortable", "Peaceful"],
        "places": ["Hillhome", "Meadowbrook", "Riverbend", "Greenvale", "Brightfield", "Sunnyhill"],
        "governments": [
            (GovernmentType.DEMOCRACY, 0.40),
            (GovernmentType.REPUBLIC, 0.30),
            (GovernmentType.TRIBAL_COUNCIL, 0.20),
            (GovernmentType.OLIGARCHY, 0.10)
        ],
        "values": [CulturalValue.FAMILY, CulturalValue.TRADITION, CulturalValue.FREEDOM, CulturalValue.WEALTH, CulturalValue.NATURE],
        "religions": [
            "Honor the hearth gods and home spirits",
            "Worship the Provider of harvests",
            "Revere ancestral families",
            "Follow the Simple Way",
            "Practice folk traditions and seasonal festivals"
        ],
        "features": [
            "Cozy underground homes with round doors",
            "Rich agricultural traditions",
            "Close-knit family clans",
            "Renowned for hospitality and cooking",
            "Prefer peace but brave when necessary"
        ],
        "biome_preferences": {
            "temperate_grassland": 10,
            "temperate_plains": 10,
            "savanna": 8,
            "mediterranean": 9,
            "temperate_deciduous_forest": 8,
            "rolling_hills": 10,  # Halflings love gentle hills
            "river_valley": 9
        }
    },
    
    "dragonborn": {
        "name_templates": [
            "The {adjective} Empire of {place}",
            "{place} Dominion",
            "The {adjective} Scales",
            "{place} Sovereignty",
            "The {adjective} Dragonhold"
        ],
        "adjectives": ["Brass", "Copper", "Bronze", "Silver", "Gold", "Crimson", "Sapphire", "Emerald"],
        "places": ["Pyrathos", "Draconia", "Scaleheart", "Flamespire", "Drakkenfell", "Wyrmkeep"],
        "governments": [
            (GovernmentType.EMPIRE, 0.35),
            (GovernmentType.MONARCHY, 0.30),
            (GovernmentType.MILITARY_DICTATORSHIP, 0.20),
            (GovernmentType.OLIGARCHY, 0.15)
        ],
        "values": [CulturalValue.HONOR, CulturalValue.MILITARY_MIGHT, CulturalValue.GLORY, CulturalValue.TRADITION, CulturalValue.ORDER],
        "religions": [
            "Revere the ancient dragons as divine",
            "Worship Bahamut the Platinum Dragon",
            "Honor Tiamat the Chromatic Queen",
            "Follow the Draconic Code",
            "Venerate elemental dragon spirits"
        ],
        "features": [
            "Strict codes of honor and conduct",
            "Martial tradition and warrior culture",
            "Reverence for draconic ancestry",
            "Breath weapon mastery and combat schools",
            "Clan-based social structure"
        ],
        "biome_preferences": {
            "mountains": 8,
            "highland": 8,
            "volcanic": 9,  # Draconic affinity for dramatic landscapes
            "desert": 7,
            "badlands": 7,
            "temperate_mountains": 8,
            "canyon": 8,
            "mesa": 7
        }
    },
    
    "gnome": {
        "name_templates": [
            "The {place} Collective",
            "{adjective} Tinkertown",
            "The {place} Innovation District",
            "{adjective} Burrow",
            "The Ingenious {place}"
        ],
        "adjectives": ["Brilliant", "Whimsical", "Curious", "Gleaming", "Clockwork", "Sparkle"],
        "places": ["Cogsworth", "Geargrind", "Sparklemine", "Tinkerton", "Brightburrow", "Wonderworks"],
        "governments": [
            (GovernmentType.DEMOCRACY, 0.35),
            (GovernmentType.REPUBLIC, 0.30),
            (GovernmentType.MAGOCRACY, 0.20),
            (GovernmentType.OLIGARCHY, 0.15)
        ],
        "values": [CulturalValue.INNOVATION, CulturalValue.KNOWLEDGE, CulturalValue.MAGIC, CulturalValue.CRAFTSMANSHIP, CulturalValue.FREEDOM],
        "religions": [
            "Worship Garl Glittergold, the Watchful Protector",
            "Revere the Tinkerer's Muse",
            "Honor the spirits of curiosity and invention",
            "Follow the Path of Endless Discovery",
            "Practice illusion-based mysticism"
        ],
        "features": [
            "Underground warrens filled with workshops",
            "Incredible inventors and illusionists",
            "Playful and mischievous culture",
            "Complex mechanical devices everywhere",
            "Strong traditions of pranks and jokes"
        ],
        "biome_preferences": {
            "rolling_hills": 10,
            "rocky_hills": 9,
            "temperate_forest": 8,
            "temperate_deciduous_forest": 8,
            "woodland": 9,
            "underground": 7,  # Gnomes like burrows but not as deep as dwarves
            "temperate_grassland": 7
        }
    },
    
    "half-elf": {
        "name_templates": [
            "The {place} Alliance",
            "{adjective} Haven",
            "The {place} Trading League",
            "{adjective} Crossroads",
            "The United {place}"
        ],
        "adjectives": ["Twilight", "Bridge", "Harmonious", "Mixed", "Border", "Crossroad"],
        "places": ["Halfhaven", "Twinshore", "Middlereach", "Bordermark", "Harmonydale", "Unionport"],
        "governments": [
            (GovernmentType.REPUBLIC, 0.35),
            (GovernmentType.DEMOCRACY, 0.30),
            (GovernmentType.OLIGARCHY, 0.20),
            (GovernmentType.MONARCHY, 0.15)
        ],
        "values": [CulturalValue.FREEDOM, CulturalValue.INNOVATION, CulturalValue.WEALTH, CulturalValue.KNOWLEDGE, CulturalValue.FAMILY],
        "religions": [
            "Blend human and elven spiritual traditions",
            "Worship both pantheons in harmony",
            "Honor the Bridge Between Worlds",
            "Practice inclusive multi-faith traditions",
            "Revere the spirits of unity"
        ],
        "features": [
            "Cultural melting pot of traditions",
            "Talented diplomats and mediators",
            "Diverse skills combining heritage",
            "Trading hubs between civilizations",
            "Adaptable and versatile populace"
        ],
        "biome_preferences": {
            # Half-elves are adaptable - moderate preference for many biomes
            "temperate_forest": 8,
            "temperate_grassland": 8,
            "mediterranean": 8,
            "coastal": 9,  # Trading hubs
            "river_valley": 9,
            "temperate_deciduous_forest": 8,
            "savanna": 7,
            "temperate_plains": 8
        }
    },
    
    "half-orc": {
        "name_templates": [
            "The {place} Warband",
            "{adjective} Horde",
            "The {place} Clans",
            "{adjective} Stronghold",
            "The {place} Warriors"
        ],
        "adjectives": ["Blood", "Iron", "Stone", "War", "Grim", "Battle"],
        "places": ["Grimfort", "Ironhide", "Bloodrock", "Warbreach", "Stonehand", "Battlecrag"],
        "governments": [
            (GovernmentType.TRIBAL_COUNCIL, 0.40),
            (GovernmentType.MILITARY_DICTATORSHIP, 0.30),
            (GovernmentType.CLAN_CONFEDERATION, 0.20),
            (GovernmentType.MONARCHY, 0.10)
        ],
        "values": [CulturalValue.SURVIVAL, CulturalValue.MILITARY_MIGHT, CulturalValue.HONOR, CulturalValue.FREEDOM, CulturalValue.FAMILY],
        "religions": [
            "Honor Gruumsh the One-Eyed God",
            "Worship the spirits of strength and endurance",
            "Revere both human and orc ancestral spirits",
            "Follow the warrior's code",
            "Practice shamanistic traditions"
        ],
        "features": [
            "Warrior culture valuing strength",
            "Struggle for acceptance in both worlds",
            "Strong survival instincts",
            "Fierce loyalty to chosen tribe",
            "Proud of mixed heritage"
        ],
        "biome_preferences": {
            # Half-orcs prefer harsh, frontier environments
            "badlands": 9,
            "scrubland": 8,
            "steppe": 9,
            "tundra": 8,
            "taiga": 8,
            "wasteland": 8,
            "mountains": 7,
            "highland": 7
        }
    },
    
    "tiefling": {
        "name_templates": [
            "The {place} Covenant",
            "{adjective} Enclave",
            "The {place} Syndicate",
            "{adjective} Quarter",
            "The Infernal {place}"
        ],
        "adjectives": ["Crimson", "Shadow", "Infernal", "Dark", "Hidden", "Outcast"],
        "places": ["Hellgate", "Shadowhaven", "Ashmoor", "Brimstone", "Darkhold", "Embervale"],
        "governments": [
            (GovernmentType.OLIGARCHY, 0.35),
            (GovernmentType.REPUBLIC, 0.25),
            (GovernmentType.DEMOCRACY, 0.20),
            (GovernmentType.MAGOCRACY, 0.20)
        ],
        "values": [CulturalValue.FREEDOM, CulturalValue.SURVIVAL, CulturalValue.INNOVATION, CulturalValue.MAGIC, CulturalValue.WEALTH],
        "religions": [
            "Reject infernal heritage, worship redemption",
            "Embrace heritage, honor infernal patrons",
            "Follow diverse paths of individual choice",
            "Worship gods of outcasts and survivors",
            "Practice dark mysticism and arcane arts"
        ],
        "features": [
            "Communities of outcasts and survivors",
            "Strong traditions of self-reliance",
            "Innate magical abilities",
            "Complex relationship with heritage",
            "Suspicious of authority and persecution"
        ],
        "biome_preferences": {
            # Tieflings settle in marginal lands or urban centers
            "urban": 10,  # Cities where they can blend in
            "coastal": 8,  # Port cities
            "volcanic": 8,  # Infernal affinity
            "desert": 7,
            "wasteland": 7,
            "badlands": 7,
            "scrubland": 6
        }
    },
    
    "mixed": {
        "name_templates": [
            "The {place} Alliance",
            "{place} Cosmopolis",
            "The United {place}",
            "Free City of {place}",
            "{adjective} Federation",
            "The {place} Coalition",
            "{adjective} Commonwealth"
        ],
        "adjectives": ["Diverse", "United", "Cosmopolitan", "Free", "Open", "Harmonious", "Multicultural"],
        "places": ["Crossroads", "Haven", "Unity", "Harmony", "Gateway", "Confluence", "Nexus", "Sanctuary"],
        "governments": [
            (GovernmentType.REPUBLIC, 0.30),
            (GovernmentType.DEMOCRACY, 0.25),
            (GovernmentType.OLIGARCHY, 0.20),
            (GovernmentType.MONARCHY, 0.15),
            (GovernmentType.EMPIRE, 0.10)
        ],
        "values": [CulturalValue.FREEDOM, CulturalValue.INNOVATION, CulturalValue.WEALTH, CulturalValue.KNOWLEDGE, CulturalValue.ORDER],
        "religions": [
            "Practice religious pluralism with tolerance",
            "Blend traditions from multiple faiths",
            "Worship pantheon of diverse deities",
            "Honor unity through diversity",
            "Follow secular humanistic philosophy"
        ],
        "features": [
            "Melting pot of cultures and traditions",
            "Centers of trade and commerce",
            "Renowned for tolerance and diversity",
            "Multiple languages and customs coexist",
            "Rich artistic and culinary fusion",
            "Diplomatic mediators between other civilizations",
            "Universities attracting scholars from all races",
            "Complex legal systems balancing diverse needs"
        ],
        "biome_preferences": {
            # Mixed civilizations prefer accessible, central locations
            "coastal": 10,  # Trade access
            "river_valley": 10,  # Fertile and accessible
            "temperate_grassland": 9,
            "mediterranean": 9,
            "temperate_plains": 9,
            "crossroads": 10,  # Metaphorical - any central location
            "temperate_forest": 8,
            "savanna": 7
        }
    }
}


def generate_civilizations(
    world_size: Tuple[int, int],
    historical_figures: List,
    target_count: int = None
) -> List[Civilization]:
    """
    Generate 5-8 distinct civilizations with unique cultures.
    
    Args:
        world_size: (width, height) of world in hexes
        historical_figures: List of HistoricalFigure objects to associate
        target_count: Specific number of civilizations (default: random 5-8)
    
    Returns:
        List of Civilization objects
    """
    if target_count is None:
        target_count = random.randint(5, 8)
    
    civilizations = []
    used_names = set()
    
    # Determine race distribution (including mixed)
    # About 20-30% of civilizations should be mixed-race
    mono_racial_races = ["human", "elf", "dwarf", "halfling", "dragonborn", "gnome", "half-elf", "half-orc", "tiefling"]
    
    for i in range(target_count):
        # 20-30% chance of mixed civilization
        is_mixed = random.random() < 0.25
        
        if is_mixed:
            race = "mixed"
            archetype = CIVILIZATION_ARCHETYPES["mixed"]
        else:
            # Select mono-racial civilization (weighted random)
            race_weights = [30, 20, 15, 10, 8, 7, 5, 3, 2]  # Matches historical figure weights
            race = random.choices(mono_racial_races, weights=race_weights[:len(mono_racial_races)])[0]
            archetype = CIVILIZATION_ARCHETYPES[race]
        
        # Generate unique name
        name = _generate_civilization_name(archetype, used_names)
        used_names.add(name)
        
        # Select government (weighted by archetype)
        governments = archetype["governments"]
        gov_types, gov_weights = zip(*governments)
        government = random.choices(gov_types, weights=gov_weights)[0]
        
        # Select 2-3 cultural values
        num_values = random.randint(2, 3)
        values = random.sample(archetype["values"], num_values)
        
        # Select religion
        religion = random.choice(archetype["religions"])
        
        # Generate cultural description
        description = _generate_cultural_description(name, race, government, values, archetype)
        
        # Select notable features
        num_features = random.randint(2, 4)
        features = random.sample(archetype["features"], num_features)
        
        # Determine racial composition
        if is_mixed:
            races_list, race_percentages = _generate_mixed_race_composition()
        else:
            races_list = [race]
            race_percentages = {race: 100}
        
        # Create civilization
        # Calendar system: Current year is 1452, history goes back 150 years
        # Civilizations founded 50-500 years before start of simulation
        # So founding years: 1452 - 150 - (50 to 500) = 852 to 1252
        current_year = 1452
        history_years = 150
        simulation_start = current_year - history_years  # 1302
        founding_year = random.randint(simulation_start - 500, simulation_start - 50)  # 802 to 1252
        
        civilization = Civilization(
            id=f"civ_{i+1}",
            name=name,
            race=race,
            races=races_list,
            race_percentages=race_percentages,
            founded_year=founding_year,  # Calendar year (e.g., 1052)
            government_type=government,
            cultural_values=values,
            religious_beliefs=religion,
            cultural_description=description,
            notable_features=features,
            population=random.randint(50000, 500000)
        )
        
        civilizations.append(civilization)
    
    # Associate founding figures
    _associate_founding_figures(civilizations, historical_figures)
    
    # Generate initial relationships
    _generate_relationships(civilizations)
    
    return civilizations


def place_civilizations(civilizations: List[Civilization], world_coordinator) -> None:
    """
    Place civilizations on the world map based on geographic preferences.
    Generates territorial claims for each civilization.
    
    Args:
        civilizations: List of civilizations to place
        world_coordinator: WorldCoordinator with hex_data
    """
    if not hasattr(world_coordinator, 'hex_data') or not world_coordinator.hex_data:
        print("Warning: No world data available for civilization placement")
        return
    
    # Get all available hexes
    available_hexes = []
    for hex_id, hex_info in world_coordinator.hex_data.items():
        if isinstance(hex_id, str) and len(hex_id) == 4:
            x, y = int(hex_id[:2]), int(hex_id[2:])
            available_hexes.append((x, y, hex_id, hex_info))
    
    # Track claimed hexes
    claimed_hexes = set()
    
    for civ in civilizations:
        # Get biome preferences for this civilization's race
        archetype = CIVILIZATION_ARCHETYPES.get(civ.race)
        if not archetype or "biome_preferences" not in archetype:
            # Fallback: random placement
            capital_hex = _random_unclaimed_hex(available_hexes, claimed_hexes)
        else:
            # Find best hex based on biome preferences
            capital_hex = _find_best_capital_location(
                available_hexes, 
                claimed_hexes,
                archetype["biome_preferences"]
            )
        
        if not capital_hex:
            print(f"Warning: Could not find suitable location for {civ.name}")
            continue
        
        # Mark capital as claimed
        claimed_hexes.add(capital_hex)
        
        # Generate territory around capital
        territory_hexes = _generate_territory(
            capital_hex,
            available_hexes,
            claimed_hexes,
            civ.population,
            world_coordinator.world_size
        )
        
        # Create Territory object
        territory = Territory(
            hex_coordinates=[capital_hex] + territory_hexes,
            capital_hex=capital_hex,
            population_estimate=civ.population,
            territorial_description=_generate_territory_description(
                civ, 
                len(territory_hexes) + 1,
                world_coordinator.hex_data.get(f"{capital_hex[0]:02d}{capital_hex[1]:02d}", {})
            )
        )
        
        civ.territory = territory
        
        print(f"Placed {civ.name} at {capital_hex} with {len(territory_hexes)+1} hexes")


def _find_best_capital_location(
    available_hexes: List[Tuple[int, int, str, dict]],
    claimed_hexes: set,
    biome_preferences: dict
) -> Optional[Tuple[int, int]]:
    """
    Find the best hex for a civilization's capital based on biome preferences.
    
    Returns:
        (x, y) coordinates of best hex, or None if none available
    """
    unclaimed = [(x, y, hex_id, info) for x, y, hex_id, info in available_hexes 
                 if (x, y) not in claimed_hexes]
    
    if not unclaimed:
        return None
    
    # Score each hex
    scored_hexes = []
    for x, y, hex_id, hex_info in unclaimed:
        biome = hex_info.get('biome', hex_info.get('type', 'temperate_grassland'))
        score = biome_preferences.get(biome, 3)  # Default score of 3
        
        # Bonus for not being on the edge
        edge_distance = min(x, y, 19-x, 19-y) if x < 20 and y < 20 else 0
        score += edge_distance * 0.1
        
        scored_hexes.append((score, x, y))
    
    # Sort by score (descending) and return top choice
    scored_hexes.sort(reverse=True)
    
    # Add some randomness: pick from top 20% of options
    top_choices = scored_hexes[:max(1, len(scored_hexes) // 5)]
    chosen = random.choice(top_choices)
    
    return (chosen[1], chosen[2])


def _random_unclaimed_hex(
    available_hexes: List[Tuple[int, int, str, dict]],
    claimed_hexes: set
) -> Optional[Tuple[int, int]]:
    """Select a random unclaimed hex."""
    unclaimed = [(x, y) for x, y, _, _ in available_hexes if (x, y) not in claimed_hexes]
    return random.choice(unclaimed) if unclaimed else None


def _generate_territory(
    capital_hex: Tuple[int, int],
    available_hexes: List[Tuple[int, int, str, dict]],
    claimed_hexes: set,
    population: int,
    world_size: Tuple[int, int]
) -> List[Tuple[int, int]]:
    """
    Generate territorial hexes around a capital.
    Territory size based on population.
    
    Returns:
        List of (x, y) coordinates for territory hexes (excluding capital)
    """
    # Determine territory size based on population
    # 50k-100k: 2-4 hexes
    # 100k-300k: 4-8 hexes
    # 300k+: 8-15 hexes
    if population < 100000:
        target_hexes = random.randint(2, 4)
    elif population < 300000:
        target_hexes = random.randint(4, 8)
    else:
        target_hexes = random.randint(8, 15)
    
    territory = []
    candidates = _get_adjacent_hexes(capital_hex, world_size)
    
    # Expand territory in rings
    for _ in range(target_hexes):
        # Filter to unclaimed hexes
        unclaimed_candidates = [hex_coord for hex_coord in candidates 
                               if hex_coord not in claimed_hexes and hex_coord != capital_hex]
        
        if not unclaimed_candidates:
            break
        
        # Pick closest to capital (prefer contiguous territory)
        next_hex = min(unclaimed_candidates, 
                      key=lambda h: abs(h[0]-capital_hex[0]) + abs(h[1]-capital_hex[1]))
        
        territory.append(next_hex)
        claimed_hexes.add(next_hex)
        
        # Add neighbors of new hex to candidates
        new_candidates = _get_adjacent_hexes(next_hex, world_size)
        candidates.extend([c for c in new_candidates if c not in candidates])
    
    return territory


def _get_adjacent_hexes(hex_coord: Tuple[int, int], world_size: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Get all adjacent hexes (6 neighbors in hex grid)."""
    x, y = hex_coord
    width, height = world_size
    
    # Hex grid neighbors (offset coordinates)
    neighbors = [
        (x, y-1),      # North
        (x+1, y-1),    # Northeast
        (x+1, y),      # Southeast
        (x, y+1),      # South
        (x-1, y+1),    # Southwest
        (x-1, y),      # West
    ]
    
    # Filter to valid coordinates
    return [(nx, ny) for nx, ny in neighbors 
            if 0 <= nx < width and 0 <= ny < height]


def _generate_territory_description(civ: Civilization, hex_count: int, capital_hex_info: dict) -> str:
    """Generate natural language description of civilization's territory."""
    biome = capital_hex_info.get('biome', capital_hex_info.get('type', 'temperate land'))
    biome_name = biome.replace('_', ' ').title()
    
    size_desc = {
        range(1, 4): "compact",
        range(4, 8): "modest",
        range(8, 12): "substantial",
        range(12, 20): "expansive"
    }
    
    size = next((desc for r, desc in size_desc.items() if hex_count in r), "vast")
    
    return (f"{civ.name} controls a {size} territory of {hex_count} regions "
            f"centered on their capital in the {biome_name}.")


def _generate_mixed_race_composition() -> Tuple[List[str], Dict[str, int]]:
    """
    Generate racial composition for mixed civilizations.
    
    Returns:
        Tuple of (races_list, race_percentages)
    """
    mono_racial_races = ["human", "elf", "dwarf", "halfling", "dragonborn", "gnome", "half-elf", "half-orc", "tiefling"]
    
    # Select 2-4 races to be present
    num_races = random.randint(2, 4)
    selected_races = random.sample(mono_racial_races, num_races)
    
    # Generate percentages that sum to 100
    # Use Dirichlet-like distribution for natural variation
    raw_values = [random.uniform(1, 10) for _ in range(num_races)]
    total = sum(raw_values)
    percentages = [int((val / total) * 100) for val in raw_values]
    
    # Adjust to ensure sum is exactly 100
    diff = 100 - sum(percentages)
    percentages[0] += diff
    
    # Ensure no race is below 5% (cosmopolitan, not tokenism)
    for i in range(len(percentages)):
        if percentages[i] < 5:
            percentages[i] = 5
    
    # Re-normalize after minimum adjustment
    total_pct = sum(percentages)
    if total_pct != 100:
        percentages = [int((p / total_pct) * 100) for p in percentages]
        diff = 100 - sum(percentages)
        percentages[0] += diff
    
    # Sort by percentage (descending)
    race_pct_pairs = sorted(zip(selected_races, percentages), key=lambda x: x[1], reverse=True)
    sorted_races = [race for race, _ in race_pct_pairs]
    race_percentages = {race: pct for race, pct in race_pct_pairs}
    
    return sorted_races, race_percentages


def _generate_civilization_name(archetype: dict, used_names: set) -> str:
    """Generate unique civilization name from archetype templates."""
    max_attempts = 20
    for _ in range(max_attempts):
        template = random.choice(archetype["name_templates"])
        
        # Replace placeholders
        name = template
        if "{adjective}" in template:
            name = name.replace("{adjective}", random.choice(archetype["adjectives"]))
        if "{place}" in template:
            name = name.replace("{place}", random.choice(archetype["places"]))
        if "{name}" in template and "name_clans" in archetype:
            name = name.replace("{name}", random.choice(archetype["name_clans"]))
        
        if name not in used_names:
            return name
    
    # Fallback: append number
    base_name = template.split()[0]
    counter = 1
    while f"{base_name} {counter}" in used_names:
        counter += 1
    return f"{base_name} {counter}"


def _generate_cultural_description(
    name: str,
    race: str,
    government: GovernmentType,
    values: List[CulturalValue],
    archetype: dict
) -> str:
    """Generate narrative cultural description."""
    value_phrases = {
        CulturalValue.HONOR: "deeply honor-bound traditions",
        CulturalValue.KNOWLEDGE: "pursuit of knowledge and wisdom",
        CulturalValue.WEALTH: "prosperous trade and accumulation of wealth",
        CulturalValue.MILITARY_MIGHT: "formidable military strength",
        CulturalValue.TRADITION: "reverence for ancient traditions",
        CulturalValue.INNOVATION: "spirit of innovation and progress",
        CulturalValue.NATURE: "harmony with the natural world",
        CulturalValue.MAGIC: "mastery of arcane arts",
        CulturalValue.CRAFTSMANSHIP: "legendary craftsmanship",
        CulturalValue.FREEDOM: "fierce independence and personal liberty",
        CulturalValue.ORDER: "strict laws and social order",
        CulturalValue.FAITH: "unwavering religious devotion",
        CulturalValue.FAMILY: "strong family bonds and kinship",
        CulturalValue.GLORY: "pursuit of glory and renown",
        CulturalValue.SURVIVAL: "hardened by struggle and survival"
    }
    
    gov_phrases = {
        GovernmentType.MONARCHY: "ruled by hereditary monarchs",
        GovernmentType.REPUBLIC: "governed by elected councils",
        GovernmentType.THEOCRACY: "led by religious authority",
        GovernmentType.OLIGARCHY: "controlled by elite families",
        GovernmentType.TRIBAL_COUNCIL: "guided by tribal councils",
        GovernmentType.MAGOCRACY: "ruled by powerful mages",
        GovernmentType.MILITARY_DICTATORSHIP: "commanded by military leaders",
        GovernmentType.DEMOCRACY: "governed by democratic vote",
        GovernmentType.CLAN_CONFEDERATION: "united confederation of clans",
        GovernmentType.EMPIRE: "vast empire under imperial rule"
    }
    
    value_text = ", ".join([value_phrases[v] for v in values])
    gov_text = gov_phrases[government]
    
    # Handle mixed vs mono-racial descriptions
    if race == "mixed":
        race_text = "cosmopolitan, multi-racial civilization"
    else:
        race_text = f"{race} civilization"
    
    description = (
        f"{name} is a {race_text} {gov_text}. "
        f"Their culture is defined by {value_text}. "
    )
    
    return description


def _associate_founding_figures(civilizations: List[Civilization], historical_figures: List) -> None:
    """Associate historical figures with civilizations as founders."""
    if not historical_figures:
        return
    
    # Group figures by race
    figures_by_race = {}
    for figure in historical_figures:
        race = figure.race
        if race not in figures_by_race:
            figures_by_race[race] = []
        figures_by_race[race].append(figure)
    
    # Assign 1-3 founding figures per civilization
    for civ in civilizations:
        # For mixed civilizations, draw from all component races
        if civ.race == "mixed":
            matching_figures = []
            for race in civ.races:
                matching_figures.extend(figures_by_race.get(race, []))
        else:
            matching_figures = figures_by_race.get(civ.race, [])
        
        if matching_figures:
            # Prefer heroes as founders
            heroes = [f for f in matching_figures if f.alignment == "hero"]
            pool = heroes if heroes else matching_figures
            
            # Mixed civilizations may have more founders (representing different races)
            max_founders = 4 if civ.race == "mixed" else 3
            num_founders = min(random.randint(1, max_founders), len(pool))
            founders = random.sample(pool, num_founders)
            civ.founding_figures = [f.id for f in founders]
            
            # Update figures' civilization association
            for founder in founders:
                founder.civilization = civ.id


def _generate_relationships(civilizations: List[Civilization]) -> None:
    """Generate initial relationships between civilizations."""
    for i, civ1 in enumerate(civilizations):
        for civ2 in civilizations[i+1:]:
            # Determine relationship based on cultural compatibility
            relationship = _determine_relationship(civ1, civ2)
            
            civ1.faction_relationships[civ2.id] = relationship
            civ2.faction_relationships[civ1.id] = relationship


def _determine_relationship(civ1: Civilization, civ2: Civilization) -> RelationshipLevel:
    """Determine relationship between two civilizations based on culture."""
    # Base relationship: neutral
    score = 0
    
    # Racial compatibility
    if civ1.race == civ2.race:
        score += 2
    # Mixed civilizations are more tolerant
    elif civ1.race == "mixed" or civ2.race == "mixed":
        score += 1  # Bonus for cosmopolitan outlook
        # Additional bonus if they share any races
        if civ1.race == "mixed" and civ2.race == "mixed":
            shared_races = set(civ1.races) & set(civ2.races)
            score += len(shared_races) * 0.5
        elif civ1.race == "mixed" and civ2.race in civ1.races:
            score += 1
        elif civ2.race == "mixed" and civ1.race in civ2.races:
            score += 1
    
    # Shared values: +1 per shared value
    shared_values = set(civ1.cultural_values) & set(civ2.cultural_values)
    score += len(shared_values)
    
    # Conflicting values
    conflicts = {
        CulturalValue.ORDER: CulturalValue.FREEDOM,
        CulturalValue.TRADITION: CulturalValue.INNOVATION,
        CulturalValue.MILITARY_MIGHT: CulturalValue.NATURE
    }
    
    for v1 in civ1.cultural_values:
        if v1 in conflicts and conflicts[v1] in civ2.cultural_values:
            score -= 2
    
    # Government compatibility
    if civ1.government_type == civ2.government_type:
        score += 1
    
    # Map score to relationship
    if score >= 4:
        return RelationshipLevel.ALLIED
    elif score >= 2:
        return RelationshipLevel.FRIENDLY
    elif score >= 0:
        return RelationshipLevel.NEUTRAL
    elif score >= -2:
        return RelationshipLevel.TENSE
    else:
        return RelationshipLevel.HOSTILE
