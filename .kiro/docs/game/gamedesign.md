# Ultimate Fantasy Sim - Core Gameplay Design Document

**Version:** 2.0  
**Date:** October 27, 2025  
**Purpose:** Reference document for gameplay vision and mechanics implementation

***

## Executive Summary

Ultimate Fantasy Sim is a hardcore permadeath text-based survival RPG with two distinct gameplay layers: **overworld hex map travel** (deadly, preparation-focused) and **location-based exploration** (detailed, interactive, resource-gathering). The core loop presents a brutal choice: seek the relative safety of civilization where the player can rent lodging, trade, and accept quests, or attempt to establish precarious survival in the unforgiving wilderness through careful resource management and luck.

**Core Philosophy:** Travel is deadly and requires extensive preparation. Survival comes from discovering and interacting with specific objects in the world through contextual commands. Every location is persistently generated and evolves over time whether explored or not. Death is permanent - no respawning, no second chances.

***

## Two-Layer World Structure

### Overworld Hex Map

**Purpose:** Long-distance travel, strategic planning, deadly exposure, death from environmental hazards

**Map Structure:**
- Large hex-based overworld (500x500+ hexes minimum for proper scale)
- Each hex represents approximately three to five square miles of terrain
- Hexes contain: biome type, terrain features, climate data, weather conditions, and generated locations

**Player Actions on Overworld:**
- **Movement:** Travel north/east/south/west to adjacent hexes
- **Inventory Management:** Access inventory and character sheet
- **Party Management:** Manage companions (future implementation)
- **No Direct Survival Actions:** Cannot forage, camp, search, or interact with environment while on overworld

**Travel Mechanics:**
- **Time Cost:** Varies from an hour to several hours per hex depending on terrain difficulty and weather severity
- **Resource Drain:** Continuous depletion of hunger, thirst, and stamina during travel
- **Environmental Exposure:** Full exposure to weather effects causing hypothermia, heatstroke, exhaustion, and other deadly conditions
- **No Shelter:** Player completely exposed to all environmental hazards
- **Death is Common:** Unprepared characters perish quickly from exposure, starvation, or dehydration

**UI Feedback Philosophy:**
All information presented in natural language without numerical values. Player learns through descriptive feedback.

**Example Travel Description:**
```
You travel northward through dense forest terrain.

The journey exhausts you. Icy rain penetrates your worn clothing, and you feel the dangerous chill settling deep into your bones. Your stomach growls with increasing urgency, and your mouth feels parched.

You arrive at the edge of a forbidding mountain range. Dark clouds gather overhead, and the temperature has dropped noticeably.

The hex contains multiple locations you could explore for shelter and resources.
```

### Locations (Micro-Level Exploration)

**Purpose:** Detailed exploration, resource gathering, survival preparation, combat encounters, NPC interactions

**Structure:**
- Upon entering hex, five to twenty locations are **permanently generated** from JSON templates
- For settlements: potentially fifty or more locations representing a proper town/village/city scale
- Mega-dungeons may contain extensive location networks rivaling major settlements
- Each location is a graph of connected areas (not spatial grid)
- Locations persist indefinitely - same locations appear on re-entry
- At least one location per hex has exit capability allowing return to overworld

**Scale Philosophy:**
The game compensates for lack of graphics through unprecedented depth and scale. A proper village should feel like exploring an actual settlement with dozens of buildings, not three generic locations. This is where text-based games excel - unlimited scope without graphical constraints.

**Player Actions in Locations:**
- **Movement:** Navigate between areas following directional connections
- **Observation:** Passive perception determines initially visible content
- **Active Searching:** Spend time searching thoroughly for hidden content
- **Object Interaction:** Context-specific interactions based on discovered objects
- **Combat:** Engage hostile entities encountered
- **Camping:** Establish temporary shelter, rest, restore needs
- **NPC Interaction:** Dialogue, trading, quest acceptance

**Location Generation Rules:**
1. Generated once when player first enters hex
2. Cached permanently in game state
3. Type determined by hex biome and terrain type
4. Weighted spawn from JSON templates
5. Objects, entities, and items populated from defined pools
6. Content visibility determined by multiple skill checks
7. Time-based changes occur whether player present or not

---

## Perception and Discovery System

### Passive Discovery on Entry

When entering a location area, multiple skill checks occur automatically in the background:

**Relevant Skills:**
- **Perception:** Spotting visual details, hidden objects, movement
- **Survival:** Recognizing tracks, natural resources, environmental clues
- **Nature:** Identifying plants, animal signs, weather patterns
- **Investigation:** Noticing inconsistencies, hidden mechanisms, architectural details

The game never reveals check results to the player. They simply see what their character notices based on their skills and the situation.

**Visibility Framework:**

Objects in `objects.json` define visibility properties determining detection difficulty:

- **Obvious:** Large features impossible to miss (altar, fireplace, doorway, large tree)
- **Clear:** Normal objects in plain sight (chest, table, berry bush, campfire remains)
- **Hidden:** Concealed items requiring attention (hollow tree, buried cache, trap, small container)
- **Very Hidden:** Secret content demanding expertise (vault entrance, hidden passage, ancient treasure)

**Design Intent:**
The world naturally conceals some content without artificial gating. This creates exciting discovery moments and rewards character builds focused on observation and wilderness skills. High perception characters notice more, but survival-focused characters identify different aspects. The world feels larger than what's immediately apparent.

### Discovery Example

**Entering Forest Clearing:**

```
You step into a sun-dappled clearing where wildflowers carpet the grass beneath ancient oak trees. A gentle breeze carries the sweet scent of berries. Birds chirp overhead, and you notice fresh deer tracks leading into the undergrowth to the north.

You see:
- A massive oak tree dominating the clearing's center
- Several berry bushes laden with ripe fruit
- A fallen log covered in moss
- Animal trails leading in multiple directions
```

**Actually Present (Not Initially Revealed):**
- Hidden hollow in oak tree containing medicinal herbs (requires higher perception or active search)
- Rabbit warren beneath fallen log (requires survival check or investigation)
- Edible mushrooms growing in the shade (requires nature knowledge)
- Abandoned bird's nest with useful twine (very hidden, requires thorough search)

**Active Searching:**
Player can invest time searching specific objects or areas:

```
> search oak tree

You spend time carefully examining the ancient oak, running your hands along the rough bark and peering into shadowed crevices.

You discover a natural hollow concealed by hanging moss. Inside, you find a small cache of dried herbs - someone knowledgeable about healing stored these here long ago.
```

The game handles skill checks invisibly. Player receives appropriate feedback based on success or failure without seeing numerical results.

***

## Object Interaction System

### Context-Specific Commands

All resource gathering occurs through direct object interaction. There are no generic "forage" or "gather" commands disconnected from specific objects.

**Design Principle:**
Every interaction references a specific object the player has discovered. Commands are contextual and natural.

**Berry Bush Example:**

```
> examine berry bush

A healthy bush stands before you, branches heavy with ripe blackberries. The berries appear fresh and edible, though you'll need to pick carefully to avoid the thorns.

> harvest berries

You carefully pick berries, selecting the ripest ones while avoiding thorns. Your wilderness experience helps you identify the best fruit.

You gather a substantial amount of fresh blackberries. They'll provide good nourishment.

Your hands are slightly scratched from the thorns, but nothing serious.
```

Behind the scenes: Survival check determines quantity harvested. Time passes. Berries added to inventory. Bush marked as depleted temporarily.

**Locked Chest Example:**

```
> examine chest

An iron-bound chest sits against the wall, secured with a complex mechanical lock. The lock appears old but well-maintained. You notice scratches around the keyhole - someone has attempted to pick this before.

> pick lock

You kneel before the chest and carefully insert your thieves' tools, feeling for the lock's internal mechanisms.

Time passes as you work...

The lock resists your efforts. You sense you're missing something about the mechanism's design. Your tools slip, nearly breaking one of the delicate picks.

> examine lock closely

You scrutinize the lock mechanism more carefully, noting subtle markings on the casing. These appear to be dwarvish craftsmanship - the internal pins likely follow a non-standard arrangement.

> pick lock

Armed with better understanding, you approach the lock again. Your tools find the unusual pin configuration, and you carefully manipulate each one into position.

The lock yields with a satisfying click. You've successfully opened the chest.
```

Multiple skill checks occurred (Investigation to understand lock, Sleight of Hand to pick it). Time passed. Potential for tool breakage on failures. Success reveals contents.

### Interaction Properties

Objects define available interactions in `objects.json`:

**Simple Resource Object:**
```
Berry Bush
- Commands: examine, harvest
- Harvest requires: Survival check
- Success: Moderate berry quantity
- Failure: Small berry quantity  
- Time cost: A few minutes
- Depletion: Yes, temporarily unavailable
- Respawn: Returns after appropriate growing season (seasonal timing)
```

**Complex Interactive Object:**
```
Locked Iron Chest
- Commands: examine, pick lock, force open, examine lock
- Pick lock requires: Thieves' tools, Sleight of Hand check
- Force open requires: Athletics check, potential self-damage
- Examine lock requires: Investigation check, reveals information
- Failure consequences: Tool damage risk, noise alerting nearby entities
- Success contents: Items from treasure pool
```

***

## Time-Based Consequences

### Living World Systems

**Philosophy:** The world exists independently of player observation. Events occur whether witnessed or not. Hidden treasures don't wait indefinitely.

**Temporal Events:**

**Hidden Treasure:**
- Player enters ruins, misses hidden vault (insufficient perception/investigation)
- Several days pass
- Bandits happen upon the ruins
- They find and loot the vault
- Player returns to discover empty vault, evidence of recent looting

**Animal Den:**
- Player spots tracks leading to burrow but doesn't investigate
- Days pass
- Predator threatens the area
- Animals abandon burrow, migrate elsewhere
- Player returns to find abandoned burrow with old tracks

**Seasonal Resources:**
- Berry bushes fruit in appropriate seasons
- Winter eliminates foraging opportunities
- Spring brings new growth
- Game animals migrate with seasons
- Water sources freeze or flow depending on temperature

**Balance Philosophy:**
Create meaningful urgency without frustration. Timescales match content value and realism. Common resources remain available or respawn quickly. Unique treasures risk discovery by others. Wildlife behaves naturally, migrating and responding to threats.

***

## Location Persistence and Generation

### Generation Rules

When player first enters hex, five to twenty locations generate permanently based on hex characteristics. For settlements or mega-dungeons, fifty or more locations create proper scale and depth.

Location generation considers:
- Hex biome type
- Terrain features
- Climate conditions  
- Proximity to other hexes
- Historical significance (future implementation)

Generated locations cache permanently in game state. Same locations appear on every hex re-entry. Objects can be depleted, looted, or used. Entities can be killed, scared away, or become friendly. Time-based changes occur continuously.

### Exit Locations

**Critical Rule:** Every hex must contain at least one location with exit capability.

This prevents trap scenarios where player cannot return to overworld. Typically the first location generated has exit capability, representing the entry point from overworld.

**Example:**
```
Forest Clearing [EXIT AVAILABLE]
Leads to:
- Dense Thicket
- Hunter's Cabin
- Hidden Grove

From Forest Clearing, player can exit to overworld or explore deeper locations.
```

***

## Survival and Choice

### Core Gameplay Cycle

**Phase 1: Immediate Survival**

Player spawns in wilderness hex with minimal supplies. Immediate priorities:
- Locate water source
- Find food (berries, small game, edible plants)
- Secure shelter from weather
- Avoid or overcome threats
- Assess condition and resources

**Phase 2: The Critical Choice**

Player must decide between two paths:

**Path A: Seek Civilization**
- Gather enough supplies for overworld travel
- Determine direction toward nearest settlement
- Risk deadly journey through multiple hexes
- Success means access to civilization's benefits
- Failure means death from exposure, starvation, or encounters

**Path B: Establish Wilderness Survival**
- Remain in known hex or nearby hexes
- Master local resources and threats
- Build deeper knowledge of safe locations
- Success depends on skill, luck, and seasonal factors
- Much harder than reaching civilization
- Greater risk but complete independence

**Phase 3A: Civilization (If Reached)**

**Settlement Services:**
- **Inns:** Rent rooms (provides chest for storage, safe rest), or sleep in common room (cheaper, less security)
- **Streets:** Free but dangerous (theft, weather exposure, legal trouble)
- **Merchants:** Buy/sell equipment, supplies, information
- **Quest Givers:** Multiple sources of work and income
- **Craftsmen:** Repair equipment, create custom items
- **Temples:** Healing, blessings, religious quests
- **Taverns:** Information, rumors, criminal contacts

**Quest Sources:**
- Adventure guilds offering bounties and exploration contracts
- Local authorities with political or security tasks
- Merchants needing escorts or retrieval services
- Religious institutions requiring faithful assistance
- Desperate citizens with personal problems
- Criminal elements with morally questionable jobs

**Quest System Vision:**
Begin with simple, linear quest formats for initial implementation. Gradually expand toward grand, complex quest networks that remove formulaic patterns. Quests should emerge from NPC motivations, faction politics, and world events, creating organic narratives rather than generic "fetch quest" patterns.

**Phase 3B: Wilderness Survival (If Remaining)**

Significantly harder than civilization path:
- Complete self-sufficiency required
- Seasonal challenges (winter especially deadly)
- Limited access to advanced equipment
- No safe rest locations (always at risk)
- Injury or illness potentially fatal
- RNG heavily factors into success
- Rewards: Complete freedom, no rent, no social obligations

---

## Progression and Goals

### Primary Goal: Survive

In a permadeath game, survival itself is the primary goal. Everything serves this purpose.

**Secondary Goal: Reach Civilization OR Master Wilderness**

Player chooses their path based on preference, character build, and circumstances.

### Settlement Scale and Storage

**Villages (5-15 locations):**
- Small inn with limited storage chest in rented rooms
- General store merchant
- Local elder or mayor offering simple quests
- Temple or shrine
- Few residential buildings
- No bank (unrealistic for village scale)

**Towns (20-40 locations):**
- Multiple inns with varying quality/price
- Specialized merchants (weapons, armor, potions, general goods)
- Adventure guild
- Temple with full services
- Town guard offering bounties
- Residential districts
- Criminal underground presence
- Small bank or money lender

**Cities (50+ locations):**
- Extensive inn district
- Merchant quarters with specialized craftsmen
- Multiple guilds (adventure, thieves, mages, fighters)
- Major temples
- Noble districts with political quests
- Large bank with secure storage
- Underground networks
- Multiple quest hubs
- Arena or entertainment districts

**Storage Systems:**
- **Inn Chests:** Provided in rented rooms, basic security, rent-dependent access
- **Banks:** Secure storage in cities, requires account fee, highly secure
- **Magical Bags:** Purchasable expensive items increasing carrying capacity
- **No Free Storage:** Everything has cost or risk

### Permadeath Philosophy

Death is permanent. No respawning. No save scumming encouraged.

When character dies:
- World state persists
- New character spawns in same world
- Previous character's corpse may be discovered
- Some consequences of first character's actions remain
- Creates emergent narratives across character generations

***

## UI and Information Presentation

### Three-Panel Layout

**Left Panel: Character Information**
- Character name, level, race, class, background
- HP and AC (only numbers shown)
- Survival conditions in natural language:
  - Hunger state (Well-fed, Hungry, Starving)
  - Thirst state (Hydrated, Thirsty, Dehydrated)
  - Fatigue state (Rested, Tired, Exhausted)
  - Temperature state (Comfortable, Cold/Hot, Freezing/Overheating)
  - Current conditions and their effects
- Equipment summary

**Center Panel: Game Log**
- Immersive descriptions in natural language
- No numerical stat displays
- No redundant command suggestions
- Environmental descriptions
- Action results
- NPC dialogue
- Combat narration

**Right Panel: Context Information**

When on Overworld:
- Current hex location description
- Environmental conditions (weather, temperature, terrain)
- Time of day and season
- Available commands reminder

When in Location:
- Current location and area name
- Visible objects (based on perception)
- Visible entities (NPCs, creatures)
- Available exits
- Basic command legend

**Header Bar:**
- Current in-game time (descriptive: "Late afternoon, spring")
- Current day and season
- Later: Moon phase, special events

### Natural Language Philosophy

**Strict Rules:**
- No numerical hunger/thirst/temperature values displayed
- No percentage indicators for survival needs
- No "you have X% warmth" or "hunger at 65/100"
- Time passage described ("several minutes pass" not "+15 minutes")
- Distance described ("a few miles" not "3.2 miles")
- Temperature described ("bitterly cold" not "32°F")
- Weather described ("heavy rain with strong winds" not "precipitation: 80, wind: 25mph")

Implemented condition system already handles this through descriptive states (Hungry/Starving, Thirsty/Dehydrated, Cold/Freezing, etc.)

---

## Implementation Priority (Revised)

### Week 1-2: Core Integration
1. GameEngine coordinator layer connecting all systems
2. Overworld hex movement with environmental effects
3. Location generation and permanent caching
4. Enter/exit hex mechanics with proper flow
5. Centralized logging system eliminating duplicates
6. Natural language output for all survival stats

### Week 3-4: Discovery and Interaction
1. Multi-skill perception system (Perception, Survival, Nature, Investigation)
2. Hidden roll system (player never sees check results)
3. Object interaction parser with contextual commands
4. Skill check resolution with appropriate feedback
5. Item acquisition and inventory integration
6. Resource depletion and time passage

### Week 5-6: Survival Loop
1. Time-based world changes (treasure looting, animal migration)
2. Camping mechanics with safety assessment
3. Resource consumption during overworld travel
4. Death from exposure and starvation
5. Permadeath system with world persistence
6. Starting scenario implementation

### Week 7-8: Settlement Foundation
1. Village/town/city generation at appropriate scale
2. Inn system with room rental and storage
3. Merchant NPC with trading
4. Simple quest system (linear format initially)
5. Safe rest mechanics in civilization
6. Street sleeping with risks

### Week 9+: Expansion
1. Complex quest networks
2. Faction systems
3. Political intrigue
4. Mega-dungeons
5. Seasonal systems
6. Advanced NPC behaviors

***

## Success Metrics

**Game achieves vision when player can:**

1. ✅ Generate massive world (500x500+ hexes)
2. ✅ Create character and spawn in wilderness hex
3. ✅ Travel overworld with deadly exposure mechanics
4. ✅ Enter hexes revealing 5-20+ persistent locations
5. ✅ Discover objects through multiple skill checks (hidden from player)
6. ✅ Interact with specific objects using contextual commands
7. ✅ Manage survival through discovered resources
8. ✅ Choose between seeking civilization or wilderness survival
9. ✅ Navigate to settlement or establish wilderness base
10. ✅ Access civilization services (inn, merchants, quests)
11. ✅ Accept and complete varied quests
12. ✅ Experience permadeath with world persistence
13. ✅ See all information in natural language (no numbers except HP/AC)
14. ✅ Explore settlements at proper scale (50+ locations for cities)
15. ✅ Experience time-based world changes
16. ✅ Save/load game with complete world state

This is the vision for Ultimate Fantasy Sim - a brutal, unforgiving, deeply immersive survival RPG that respects player intelligence and punishes poor decisions with permanent death.