"""
Historical Figure Generation

This module generates legendary heroes and villains tied to mythic events.
Figures have genealogical relationships, cultural backgrounds, and participation
in foundational historical events.

Integration Points:
- Called after mythic event generation
- Figures associated with specific mythic events as participants
- Forms foundation for future NPC genealogy system
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import json
import os
import random


# Archetype definitions for figure generation
HERO_ARCHETYPES = [
    "warrior_hero",      # Martial prowess, battles, protection
    "wise_elder",        # Knowledge, guidance, cultural memory
    "cunning_strategist", # Planning, diplomacy, clever victories
    "noble_ruler",       # Leadership, justice, unification
    "wandering_prophet", # Spiritual insight, prophecy, warnings
    "master_craftsman",  # Creation, innovation, legendary works
]

VILLAIN_ARCHETYPES = [
    "tyrant_conqueror",  # Brutal conquest, oppression
    "dark_sorcerer",     # Forbidden magic, corruption
    "treacherous_noble", # Betrayal, manipulation, backstabbing
    "cult_leader",       # Religious extremism, fanaticism
    "plague_bringer",    # Disease, destruction, chaos
    "usurper_king",      # Illegitimate rule, stolen throne
]

# Cultural name patterns by race
NAME_PATTERNS = {
    "human": {
        "male": ["Aldric", "Borin", "Cedric", "Darius", "Edmund", "Finnian", "Gareth", "Harald", 
                 "Ivor", "Jareth", "Kellen", "Leoric", "Marcus", "Nathaniel", "Orion", "Percival"],
        "female": ["Althea", "Brynn", "Celeste", "Diana", "Elara", "Fiona", "Gwendolyn", "Helena",
                   "Isolde", "Juliana", "Kassandra", "Lyanna", "Morgana", "Nessa", "Ophelia", "Rowena"],
        "surnames": ["Blackwood", "Goldwyn", "Ironheart", "Ravencrest", "Silvermane", "Stormborn",
                     "Thornhill", "Whitestone", "Ashford", "Brightblade", "Darkwater", "Fairwind"]
    },
    "elf": {
        "male": ["Aelrindel", "Celeborn", "Daeron", "Elrohir", "Finrod", "Gildor", "Haldir",
                 "Legolas", "Thranduil", "Elladan", "Cirdan", "Glorfindel"],
        "female": ["Arwen", "Galadriel", "Lúthien", "Nimrodel", "Elbereth", "Idril", "Aredhel",
                   "Morwen", "Nienor", "Finduilas", "Melian", "Yavanna"],
        "surnames": ["Morningstar", "Moonwhisper", "Starweaver", "Sunshadow", "Leafdancer",
                     "Silverleaf", "Nightbreeze", "Dawnbringer", "Forestwarden", "Skywalker"]
    },
    "dwarf": {
        "male": ["Thorin", "Balin", "Gimli", "Durin", "Thrain", "Dain", "Gloin", "Bombur",
                 "Dwalin", "Fili", "Kili", "Nori", "Bofur", "Bifur"],
        "female": ["Dis", "Katri", "Vistra", "Helga", "Bruni", "Sigrid", "Thyri", "Astrid",
                   "Hilde", "Greta", "Ingrid", "Solveig"],
        "surnames": ["Ironforge", "Stonehammer", "Golddelver", "Deepmine", "Rockcrusher",
                     "Steelbeard", "Bronzefist", "Silvervein", "Oreseeker", "Gemcutter"]
    },
    "halfling": {
        "male": ["Bilbo", "Frodo", "Samwise", "Merry", "Pippin", "Drogo", "Otho", "Fosco",
                 "Bungo", "Mungo", "Largo", "Polo"],
        "female": ["Primrose", "Rose", "Lily", "Daisy", "Poppy", "Belladonna", "Pansy", "Ruby",
                   "Pearl", "Marigold", "Peony", "Violet"],
        "surnames": ["Baggins", "Took", "Brandybuck", "Gamgee", "Boffin", "Proudfoot",
                     "Bolger", "Bracegirdle", "Goodbody", "Greenhand", "Burrows", "Sandheaver"]
    },
    "dragonborn": {
        "male": ["Arjhan", "Balasar", "Bharash", "Donaar", "Ghesh", "Heskan", "Kriv",
                 "Medrash", "Mehen", "Nadarr", "Pandjed", "Patrin", "Rhogar", "Shamash"],
        "female": ["Akra", "Biri", "Daar", "Farideh", "Harann", "Havilar", "Jheri", "Kava",
                   "Korinn", "Mishann", "Nala", "Perra", "Raiann", "Sora", "Surina", "Thava"],
        "surnames": ["Clethtinthiallor", "Daardendrian", "Delmirev", "Drachedandion", "Fenkenkabradon",
                     "Kepeshkmolik", "Kerrhylon", "Kimbatuul", "Linxakasendalor", "Myastan",
                     "Nemmonis", "Norixius", "Ophinshtalajiir", "Prexijandilin", "Shestendeliath"]
    },
    "gnome": {
        "male": ["Alston", "Alvyn", "Boddynock", "Brocc", "Burgell", "Dimble", "Eldon", "Erky",
                 "Fonkin", "Frug", "Gerbo", "Gimble", "Glim", "Jebeddo", "Kellen", "Namfoodle",
                 "Orryn", "Roondar", "Seebo", "Sindri", "Warryn", "Wrenn", "Zook"],
        "female": ["Bimpnottin", "Breena", "Caramip", "Carlin", "Donella", "Duvamil", "Ella",
                   "Ellyjobell", "Ellywick", "Lilli", "Loopmottin", "Lorilla", "Mardnab",
                   "Nissa", "Nyx", "Oda", "Orla", "Roywyn", "Shamil", "Tana", "Waywocket", "Zanna"],
        "surnames": ["Beren", "Daergel", "Folkor", "Garrick", "Nackle", "Murnig", "Ningel",
                     "Raulnor", "Scheppen", "Timbers", "Turen", "Sparklegem", "Fizzlebang"]
    },
    "half-elf": {
        "male": ["Aelar", "Arannis", "Berendil", "Caedric", "Elden", "Erandir", "Faelar", "Gaelin",
                 "Hadarai", "Immeral", "Lander", "Mindartis", "Paelias", "Peren", "Quarion",
                 "Riardon", "Soveliss", "Thamior", "Tharivol", "Varis"],
        "female": ["Amara", "Ariel", "Celestia", "Elara", "Evelyn", "Isara", "Kaelyn", "Laira",
                   "Meira", "Naevys", "Rosalie", "Sariel", "Sera", "Sylvia", "Talyn", "Thalia",
                   "Valencia", "Vanya", "Xanara", "Ysara"],
        "surnames": ["Amakiir", "Amastacia", "Brightwood", "Galanodel", "Holimion", "Liadon",
                     "Meliamne", "Naïlo", "Siannodel", "Moonwhisper", "Ravenwood", "Silversong"]
    },
    "half-orc": {
        "male": ["Dench", "Feng", "Gell", "Henk", "Holg", "Imsh", "Keth", "Krusk", "Mhurren",
                 "Ront", "Shump", "Thokk", "Grug", "Drog", "Grommash", "Thrall"],
        "female": ["Baggi", "Emen", "Engong", "Kansif", "Myev", "Neega", "Ovak", "Ownka",
                   "Shautha", "Sutha", "Vola", "Volen", "Yevelda", "Draka", "Garona"],
        "surnames": ["Bonegrinder", "Bloodaxe", "Gorehowl", "Ironjaw", "Skullsplitter", "Stonefist",
                     "Blackhand", "Doomhammer", "Fireforge", "Grimtotem", "Wolfheart"]
    },
    "tiefling": {
        "male": ["Akmenos", "Amnon", "Barakas", "Damakos", "Ekemon", "Iados", "Kairon", "Leucis",
                 "Melech", "Mordai", "Morthos", "Pelaios", "Skamos", "Therai", "Valafar", "Xarxes"],
        "female": ["Akta", "Anakis", "Bryseis", "Criella", "Damaia", "Ea", "Kallista", "Lerissa",
                   "Makaria", "Nemeia", "Orianna", "Phelaia", "Rieta", "Soraya", "Therassa", "Zariel"],
        "surnames": ["Ashborn", "Darkflame", "Emberwing", "Hellfury", "Infernus", "Nightshade",
                     "Shadowhorn", "Soulfire", "Vexmoor", "Ashguard", "Flameheart", "Cinderscar"]
    }
}


@dataclass
class HistoricalFigure:
    """Represents a legendary figure from the world's foundational history"""
    
    id: str                                    # Unique identifier (e.g., "hero-001")
    name: str                                  # Full name
    title: str                                 # Honorary title (e.g., "the Bold", "the Wise")
    race: str                                  # Character race
    alignment: str                             # Hero or villain
    archetype: str                             # Specific archetype
    
    # Genealogy
    birth_year: int                            # Year of birth (negative = years before present)
    death_year: Optional[int] = None           # Year of death (None = still alive in myth)
    parents: Optional[Tuple[str, str]] = None  # (mother_id, father_id) - None for mythic origins
    spouse: Optional[str] = None               # Spouse figure ID
    children: List[str] = field(default_factory=list)  # List of child figure IDs
    
    # Historical Impact
    participated_in_events: List[str] = field(default_factory=list)  # Event IDs
    achievements: List[str] = field(default_factory=list)            # Notable deeds
    artifacts_owned: List[str] = field(default_factory=list)         # Artifact IDs
    cultural_significance: int = 5                                    # 1-10 scale
    
    # Cultural Memory System (Task 2.2)
    memory_strength: int = 5                   # How well remembered (1-10, decays over time)
    cultural_influence: Dict[str, int] = field(default_factory=dict)  # race -> influence level
    remembered_as: str = ""                    # How they're remembered (e.g., "savior", "tyrant")
    legendary_status: str = "known"            # "known", "famous", "legendary", "mythic"
    
    # Biographical Details
    backstory: str = ""                        # Brief biography
    personality_traits: List[str] = field(default_factory=list)  # Defining characteristics
    cultural_origin: str = ""                  # Cultural/geographic origin
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoricalFigure':
        """Create from dictionary"""
        return cls(**data)
    
    def get_memory_description(self) -> str:
        """Get natural language description of how figure is remembered"""
        if self.legendary_status == "mythic":
            return f"spoken of in hushed reverence, their deeds the stuff of legend"
        elif self.legendary_status == "legendary":
            return f"celebrated in songs and stories across the land"
        elif self.legendary_status == "famous":
            return f"well-known among scholars and historians"
        else:
            return f"remembered by those who study the old histories"
    
    def calculate_cultural_influence(self, races_present: List[str]) -> Dict[str, int]:
        """Calculate influence on different cultures based on achievements and significance.
        
        Args:
            races_present: List of races in the world
            
        Returns:
            Dictionary mapping race to influence level (0-10)
        """
        influence = {}
        
        # Base influence on cultural significance
        base_influence = self.cultural_significance
        
        for race in races_present:
            if race == self.race:
                # Strongest influence on own race
                influence[race] = min(10, base_influence + 2)
            else:
                # Weaker but still present influence on other races
                # Heroes tend to have broader influence than villains
                if self.alignment == "hero":
                    influence[race] = max(1, base_influence - 2)
                else:
                    # Villains remembered more by those they affected
                    influence[race] = max(0, base_influence - 4)
        
        return influence


def _generate_name(race: str, gender: str, rng: random.Random) -> Tuple[str, str]:
    """Generate a name and title based on race and gender.
    
    Returns:
        Tuple of (full_name, title)
    """
    patterns = NAME_PATTERNS.get(race, NAME_PATTERNS["human"])
    
    # Select first name
    if gender == "male":
        first_name = rng.choice(patterns["male"])
    else:
        first_name = rng.choice(patterns["female"])
    
    # Select surname
    surname = rng.choice(patterns["surnames"])
    
    # Generate title
    title_options = [
        "the Bold", "the Wise", "the Just", "the Valiant", "the Great",
        "the Mighty", "the Terrible", "the Cunning", "the Ancient", "the Magnificent",
        "the Undefeated", "the Merciful", "the Dreaded", "the Noble", "the Fierce",
        "Dragonslayer", "Kingmaker", "Oathkeeper", "Stormbreaker", "Lightbringer"
    ]
    title = rng.choice(title_options)
    
    full_name = f"{first_name} {surname}"
    return full_name, title


def _generate_backstory(figure_name: str, archetype: str, race: str, 
                        events: List[str], rng: random.Random) -> str:
    """Generate a brief backstory for the figure"""
    
    # Archetype-specific story templates
    templates = {
        "warrior_hero": [
            f"{figure_name} rose to prominence through martial prowess and unwavering courage in battle.",
            f"Trained from youth in the art of war, {figure_name} defended the realm against countless threats.",
            f"{figure_name} united fractured clans through strength and honor on the battlefield.",
        ],
        "wise_elder": [
            f"{figure_name} served as counselor and guide, preserving ancient knowledge through dark times.",
            f"Known for profound wisdom and foresight, {figure_name} shaped the fate of nations through advice.",
            f"{figure_name} maintained the sacred traditions and taught future generations the old ways.",
        ],
        "cunning_strategist": [
            f"{figure_name} achieved victory through clever tactics and diplomatic maneuvering rather than force.",
            f"Master of political intrigue, {figure_name} orchestrated alliances that changed history.",
            f"{figure_name} turned enemies into allies and defeats into victories through brilliant strategy.",
        ],
        "noble_ruler": [
            f"{figure_name} established a dynasty that brought prosperity and justice to the realm.",
            f"As a fair and capable ruler, {figure_name} unified disparate peoples under one banner.",
            f"{figure_name} ruled with wisdom and compassion, creating an age of peace and growth.",
        ],
        "wandering_prophet": [
            f"{figure_name} traveled the lands sharing visions and warnings that would prove prophetic.",
            f"Blessed with divine insight, {figure_name} guided civilization through apocalyptic trials.",
            f"{figure_name} spoke truths that others feared to hear, shaping spiritual understanding.",
        ],
        "master_craftsman": [
            f"{figure_name} created legendary works that would endure for ages, shaping culture itself.",
            f"Through unparalleled skill and innovation, {figure_name} crafted artifacts of immense power.",
            f"{figure_name} revolutionized the craft, teaching techniques that defined an entire era.",
        ],
        "tyrant_conqueror": [
            f"{figure_name} carved out an empire through ruthless conquest and brutal oppression.",
            f"Known for cruelty and ambition, {figure_name} brought entire kingdoms under tyrannical rule.",
            f"{figure_name} sought absolute power, crushing all opposition with overwhelming force.",
        ],
        "dark_sorcerer": [
            f"{figure_name} delved into forbidden magics, gaining power at terrible cost.",
            f"Corrupted by dark forces, {figure_name} unleashed horrors upon the world in pursuit of knowledge.",
            f"{figure_name} mastered sorcery that violated natural law, spreading chaos and corruption.",
        ],
        "treacherous_noble": [
            f"{figure_name} betrayed sacred oaths, orchestrating schemes that brought kingdoms to ruin.",
            f"Master of deception and manipulation, {figure_name} destroyed alliances from within.",
            f"{figure_name} played lords against each other for personal gain, leaving devastation behind.",
        ],
        "cult_leader": [
            f"{figure_name} founded a fanatical movement that spread terror in the name of twisted faith.",
            f"Leading devoted followers into darkness, {figure_name} perverted spiritual truth for power.",
            f"{figure_name} commanded absolute loyalty, driving followers to commit atrocities.",
        ],
        "plague_bringer": [
            f"{figure_name} spread disease and destruction, whether by design or curse.",
            f"Wherever {figure_name} traveled, death and decay followed in their wake.",
            f"{figure_name} was both victim and vector of a plague that decimated civilizations.",
        ],
        "usurper_king": [
            f"{figure_name} seized power through treachery, ruling through fear and illegitimate claim.",
            f"Murdering rightful heirs, {figure_name} established a reign of terror and paranoia.",
            f"{figure_name} claimed the throne by force, plunging the realm into civil war.",
        ],
    }
    
    base_story = rng.choice(templates.get(archetype, [f"{figure_name} left an indelible mark on history."]))
    
    # Add event connection if events provided
    if events:
        event_connections = [
            f"Their role in the legendary events shaped the course of civilization.",
            f"They were central to the foundational events that defined the age.",
            f"Their actions during the great events are still remembered in song and story.",
        ]
        base_story += " " + rng.choice(event_connections)
    
    return base_story


def _assign_figure_to_event(figure: HistoricalFigure, event: Dict[str, Any], 
                            role: str, rng: random.Random):
    """Assign a figure as a participant in an event with specific role"""
    
    event_id = event['id']
    figure.participated_in_events.append(event_id)
    
    # Add achievement based on role and event type
    event_name = event.get('name', 'Unknown Event')
    event_type = event.get('event_type', 'myth')
    
    achievement_templates = {
        "protagonist": {
            "war": f"Led forces to victory in {event_name}",
            "discovery": f"Made the pivotal discovery during {event_name}",
            "disaster": f"Saved countless lives during {event_name}",
            "treaty": f"Negotiated the historic accord of {event_name}",
            "siege": f"Held the line during {event_name}",
            "loss": f"Attempted to prevent {event_name}",
            "myth": f"Played a central role in {event_name}",
        },
        "antagonist": {
            "war": f"Brought devastation through {event_name}",
            "discovery": f"Misused the knowledge from {event_name}",
            "disaster": f"Caused or worsened {event_name}",
            "treaty": f"Betrayed the peace of {event_name}",
            "siege": f"Led the assault in {event_name}",
            "loss": f"Responsible for {event_name}",
            "myth": f"Opposed the heroes during {event_name}",
        },
        "witness": {
            "default": f"Witnessed and chronicled {event_name}",
        }
    }
    
    template_set = achievement_templates.get(role, achievement_templates["protagonist"])
    achievement = template_set.get(event_type, template_set.get("default", f"Participated in {event_name}"))
    figure.achievements.append(achievement)
    
    # Connect artifacts if event creates them
    if 'artifact_id' in event and role in ["protagonist", "antagonist"]:
        artifact_id = event['artifact_id']
        if artifact_id not in figure.artifacts_owned:
            figure.artifacts_owned.append(artifact_id)


def generate_historical_figures(mythic_events: List[Dict[str, Any]], 
                                 seed: Optional[int] = None) -> List[HistoricalFigure]:
    """Generate legendary heroes and villains tied to mythic events.
    
    Args:
        mythic_events: List of mythic event dictionaries from generate_mythic_events()
        seed: Optional seed for deterministic generation
        
    Returns:
        List of HistoricalFigure objects representing legendary figures
    """
    rng = random.Random(seed)
    figures = []
    figure_counter = 0
    
    # Determine number of figures based on events (1-3 per event)
    # Major events get more figures
    total_figures = 0
    for event in mythic_events:
        significance = event.get('significance', 5)
        if significance >= 8:
            total_figures += rng.randint(2, 3)  # 2-3 figures for major events
        elif significance >= 5:
            total_figures += rng.randint(1, 2)  # 1-2 figures for moderate events
        else:
            total_figures += 1  # 1 figure for minor events
    
    # Cap total figures at reasonable number
    total_figures = min(total_figures, len(mythic_events) * 2)
    
    # Generate figures and assign to events
    assigned_events = []  # Track which events have figures assigned
    
    for event in mythic_events:
        event_id = event['id']
        event_type = event.get('event_type', 'myth')
        significance = event.get('significance', 5)
        event_year = event.get('year', -500)
        
        # Determine how many figures for this event
        if significance >= 8:
            num_figures = rng.randint(2, 3)
        elif significance >= 5:
            num_figures = rng.randint(1, 2)
        else:
            num_figures = 1
        
        # Generate figures for this event
        for i in range(num_figures):
            if len(figures) >= total_figures:
                break
            
            figure_counter += 1
            
            # Determine alignment (hero vs villain) - weighted toward heroes
            is_hero = rng.random() < 0.65  # 65% hero, 35% villain
            
            if is_hero:
                archetype = rng.choice(HERO_ARCHETYPES)
                alignment = "hero"
                role = "protagonist"
            else:
                archetype = rng.choice(VILLAIN_ARCHETYPES)
                alignment = "villain"
                role = "antagonist"
            
            # Select race (weighted distribution - core races more common)
            race_weights = [
                ("human", 30),
                ("elf", 20),
                ("dwarf", 15),
                ("halfling", 10),
                ("dragonborn", 8),
                ("gnome", 7),
                ("half-elf", 5),
                ("half-orc", 3),
                ("tiefling", 2),
            ]
            race = rng.choices(
                [r[0] for r in race_weights],
                weights=[r[1] for r in race_weights],
                k=1
            )[0]
            
            # Generate name and title
            gender = rng.choice(["male", "female"])
            name, title = _generate_name(race, gender, rng)
            
            # Generate birth/death years relative to event
            # Figures are typically 25-50 years old during their legendary deeds
            age_at_event = rng.randint(25, 50)
            birth_year = event_year - age_at_event
            
            # Death year - some survive past event, some die during/after
            if rng.random() < 0.3:  # 30% die during the event
                death_year = event_year + rng.randint(0, 5)
            elif rng.random() < 0.5:  # 35% die later
                death_year = event_year + rng.randint(10, 50)
            else:  # 35% remain mythic/unknown death
                death_year = None
            
            # Create figure
            figure = HistoricalFigure(
                id=f"figure-{figure_counter:03d}",
                name=name,
                title=title,
                race=race,
                alignment=alignment,
                archetype=archetype,
                birth_year=birth_year,
                death_year=death_year,
                cultural_significance=min(10, significance + rng.randint(-1, 2)),
            )
            
            # Generate personality traits
            trait_options = {
                "hero": ["Brave", "Honorable", "Compassionate", "Determined", "Loyal", 
                        "Wise", "Just", "Noble", "Selfless", "Inspiring"],
                "villain": ["Ruthless", "Ambitious", "Cunning", "Cruel", "Arrogant",
                           "Manipulative", "Power-hungry", "Paranoid", "Merciless", "Corrupt"]
            }
            figure.personality_traits = rng.sample(trait_options[alignment], k=rng.randint(2, 4))
            
            # Assign to event
            _assign_figure_to_event(figure, event, role, rng)
            
            # Generate backstory
            figure.backstory = _generate_backstory(
                f"{name} {title}",
                archetype,
                race,
                [event_id],
                rng
            )
            
            # Set cultural origin from event location
            figure.cultural_origin = event.get('location', 'Unknown')
            
            figures.append(figure)
            assigned_events.append(event_id)
    
    # Generate simple genealogical connections for some figures
    # Connect figures of same race who lived in overlapping times
    _generate_genealogy(figures, rng)
    
    # Initialize cultural memory system (Task 2.2)
    _initialize_cultural_memory(figures, rng)
    
    return figures


def _initialize_cultural_memory(figures: List[HistoricalFigure], rng: random.Random):
    """Initialize cultural memory attributes for historical figures (Task 2.2).
    
    Sets memory strength, legendary status, cultural influence, and how they're remembered
    based on their achievements, significance, and alignment.
    """
    # Get all races present
    races_present = list(set(f.race for f in figures))
    
    for figure in figures:
        # Memory strength starts equal to cultural significance
        figure.memory_strength = figure.cultural_significance
        
        # Determine legendary status based on significance and achievements
        if figure.cultural_significance >= 9:
            figure.legendary_status = "mythic"
        elif figure.cultural_significance >= 7:
            figure.legendary_status = "legendary"
        elif figure.cultural_significance >= 5:
            figure.legendary_status = "famous"
        else:
            figure.legendary_status = "known"
        
        # Calculate cultural influence across races
        figure.cultural_influence = figure.calculate_cultural_influence(races_present)
        
        # Determine how they're remembered based on archetype and alignment
        figure.remembered_as = _generate_remembered_as(figure.archetype, figure.alignment, rng)


def _generate_remembered_as(archetype: str, alignment: str, rng: random.Random) -> str:
    """Generate how a figure is remembered by culture.
    
    Args:
        archetype: Figure's archetype
        alignment: "hero" or "villain"
        rng: Random number generator
        
    Returns:
        Description of how they're culturally remembered
    """
    memory_templates = {
        # Hero archetypes
        "warrior_hero": ["legendary warrior", "champion of the people", "defender of the realm"],
        "wise_elder": ["sage advisor", "keeper of ancient wisdom", "teacher of generations"],
        "cunning_strategist": ["brilliant tactician", "master diplomat", "architect of peace"],
        "noble_ruler": ["just sovereign", "unifier of peoples", "builder of nations"],
        "wandering_prophet": ["divine messenger", "voice of prophecy", "spiritual guide"],
        "master_craftsman": ["legendary artisan", "creator of wonders", "innovator supreme"],
        
        # Villain archetypes
        "tyrant_conqueror": ["cruel tyrant", "bringer of devastation", "destroyer of kingdoms"],
        "dark_sorcerer": ["corruptor of magic", "wielder of forbidden arts", "harbinger of darkness"],
        "treacherous_noble": ["infamous betrayer", "architect of ruin", "master of treachery"],
        "cult_leader": ["dark prophet", "false messiah", "corruptor of faith"],
        "plague_bringer": ["harbinger of death", "spreader of pestilence", "cursed one"],
        "usurper_king": ["illegitimate ruler", "throne-stealer", "breaker of rightful order"],
    }
    
    templates = memory_templates.get(archetype, [f"{'legendary' if alignment == 'hero' else 'infamous'} figure"])
    return rng.choice(templates)


def _generate_genealogy(figures: List[HistoricalFigure], rng: random.Random):
    """Generate simple parent-child relationships between compatible figures.
    
    This creates a basic genealogical structure. Rules:
    - Same race required
    - Parent must be 20+ years older than child
    - Parent must have lived past child's birth year
    - Limited to prevent excessive connections (20% of figures get parents)
    """
    
    # Sort by birth year
    sorted_figures = sorted(figures, key=lambda f: f.birth_year)
    
    for i, child in enumerate(sorted_figures):
        # Only assign parents to some figures (20% chance)
        if rng.random() > 0.2:
            continue
        
        # If already has parents, skip
        if child.parents is not None:
            continue
        
        # Find potential parents (same race, at least 20 years older)
        potential_parents = [
            f for f in sorted_figures[:i]  # Only earlier figures
            if f.race == child.race
            and (child.birth_year - f.birth_year) >= 20  # At least 20 year age gap
            and (child.birth_year - f.birth_year) <= 60  # Max 60 year gap
            and (f.death_year is None or f.death_year >= child.birth_year)  # Lived past child's birth
        ]
        
        if len(potential_parents) >= 2:
            # Select mother and father
            parent_pair = rng.sample(potential_parents, 2)
            mother = parent_pair[0]
            father = parent_pair[1]
            
            # Assign relationship
            child.parents = (mother.id, father.id)
            mother.children.append(child.id)
            father.children.append(child.id)
            
            # Make parents spouses if not already
            if mother.spouse is None:
                mother.spouse = father.id
            if father.spouse is None:
                father.spouse = mother.id


def save_historical_figures(figures: List[HistoricalFigure], filepath: str = None):
    """Save historical figures to JSON file.
    
    Args:
        figures: List of HistoricalFigure objects
        filepath: Path to save JSON (default: data/historical_figures.json)
    """
    if filepath is None:
        filepath = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'data', 
            'historical_figures.json'
        )
    
    data = {
        "figures": [fig.to_dict() for fig in figures],
        "metadata": {
            "total_figures": len(figures),
            "heroes": len([f for f in figures if f.alignment == "hero"]),
            "villains": len([f for f in figures if f.alignment == "villain"]),
        }
    }
    
    # Create directory if filepath includes a directory path
    directory = os.path.dirname(filepath)
    if directory:  # Only create if there's a directory component
        os.makedirs(directory, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_historical_figures(filepath: str = None) -> List[HistoricalFigure]:
    """Load historical figures from JSON file.
    
    Args:
        filepath: Path to JSON file (default: data/historical_figures.json)
        
    Returns:
        List of HistoricalFigure objects
    """
    if filepath is None:
        filepath = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'data', 
            'historical_figures.json'
        )
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return [HistoricalFigure.from_dict(fig_data) for fig_data in data.get('figures', [])]
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading historical figures: {e}")
        return []
