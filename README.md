# 🗡️ Fantasy RPG - Ultimate Wilderness Survival Adventure

A text-based fantasy RPG that combines D&D 5e mechanics with deadly wilderness survival in a procedurally generated world. Experience the thrill of exploration where every step could be your last.

## 🎮 Game Overview

Fantasy RPG is a terminal-based adventure game that drops you into a vast, dangerous wilderness with minimal supplies. Your goal is simple: survive. Whether you seek the safety of civilization or master the art of wilderness survival is entirely up to you.

### Core Gameplay Loop

1. **Spawn in the wilderness** with basic supplies and hope
2. **Navigate deadly hex-based overworld** where exposure kills
3. **Enter locations** to escape environmental hazards
4. **Discover resources** through skill-based exploration
5. **Make critical choices** between safety and independence
6. **Experience permadeath** with persistent world consequences

## 🌍 Two-Layer World System

### Overworld Travel (Deadly Exposure)
- **Hex-based movement** across a vast procedural world
- **Environmental hazards**: Hypothermia, heat stroke, exhaustion
- **No survival actions** while traveling - you must find shelter
- **Time pressure**: Each hex takes 1-4 hours depending on terrain
- **Weather effects**: Rain, snow, and storms increase danger

### Location Exploration (Detailed Survival)
- **5-20 locations per hex** with persistent generation
- **Context-specific interactions**: Examine objects to discover resources
- **Skill-based discovery**: Perception checks reveal hidden content
- **All survival actions**: Forage, camp, craft, and interact with NPCs
- **Safe havens**: Escape deadly overworld exposure

## ⚔️ Features

### Character System
- **D&D 5e mechanics** with authentic rules and progression
- **Four races**: Human, Elf, Dwarf, Halfling
- **Four classes**: Fighter, Rogue, Cleric, Wizard
- **Skill-based interactions** with the world
- **Equipment and inventory** with realistic weight limits

### Survival Mechanics
- **Hunger, thirst, and temperature** tracking
- **Natural language feedback** (no numerical displays)
- **Environmental conditions** affect survival needs
- **Resource gathering** through exploration and foraging
- **Shelter building** for protection from elements

### World Generation
- **Procedural hex world** with diverse biomes
- **Persistent locations** that remain consistent on re-entry
- **Dynamic weather** affecting travel and survival
- **Hidden discoveries** revealed through exploration
- **Emergent storytelling** through environmental challenges

### Combat & Progression
- **Turn-based D&D 5e combat** with full tactical options
- **Experience and leveling** following official rules
- **Equipment upgrades** found through exploration
- **Death consequences** with permadeath mechanics

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fantasy-rpg
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start your adventure**
   ```bash
   python play.py
   ```

### First Steps

1. **Create your character** using the interactive creation system
2. **Learn the controls** with the `help` command
3. **Check your surroundings** with `look`
4. **Monitor your condition** with `survival`
5. **Find shelter quickly** - the wilderness is deadly!

## 🎯 Key Commands

### Movement & Exploration
- `n`, `s`, `e`, `w` - Move between hexes (dangerous!)
- `enter <location>` - Enter a location for safety
- `exit` - Leave current location
- `look` - Examine your surroundings
- `search` - Look for hidden objects and resources

### Survival
- `survival` - Check hunger, thirst, temperature status
- `forage` - Search for food and water (location only)
- `rest` - Recover health and energy
- `camp` - Set up temporary shelter

### Character Management
- `character` or `c` - View detailed character sheet
- `inventory` or `i` - Manage equipment and items
- `equip <item>` - Equip weapons and armor
- `use <item>` - Consume items or activate abilities

### System Commands
- `help` - Show all available commands
- `save` - Save your progress
- `load` - Load saved game
- `quit` - Exit game (with confirmation)

## 🎨 Interface

The game features a clean three-panel interface:

- **Left Panel**: Character status, location, and survival conditions
- **Center Panel**: Scrollable game log with all events and descriptions
- **Right Panel**: Points of interest and available interactions
- **Bottom**: Command input with context-sensitive help

## 🏗️ Technical Features

### Built With
- **Python 3.8+** for core game logic
- **Textual** for rich terminal UI
- **Rich** for enhanced text formatting
- **JSON** for game data storage
- **Modular architecture** for easy expansion

### Game Systems
- **GameEngine**: Central coordinator managing all systems
- **World Generation**: Procedural terrain and location creation
- **Character System**: Full D&D 5e implementation
- **Survival Mechanics**: Realistic environmental simulation
- **Save System**: Complete game state persistence
- **Action System**: Flexible command processing

## 🎲 Game Philosophy

### Natural Language Focus
- **Descriptive feedback** instead of raw numbers
- **Immersive descriptions** of environmental conditions
- **Contextual interactions** that feel natural
- **Atmospheric storytelling** through environmental details

### Meaningful Choices
- **Risk vs. reward** in every decision
- **Resource management** with real consequences
- **Multiple paths to success** (civilization vs. wilderness mastery)
- **Emergent gameplay** through system interactions

### Authentic Difficulty
- **Permadeath** makes every choice matter
- **Environmental hazards** create constant tension
- **Resource scarcity** forces strategic thinking
- **Skill-based progression** rewards player knowledge

## 🔧 Development Status

This is an active development project with a focus on:
- **System integration** through the GameEngine coordinator
- **Enhanced location generation** with more interactive objects
- **Expanded survival mechanics** with crafting and shelter building
- **NPC interactions** and faction systems
- **Combat encounters** with monsters and wildlife

## 🤝 Contributing

The game is built with a modular architecture that makes it easy to:
- Add new locations and objects
- Create additional character classes and races
- Implement new survival mechanics
- Expand the world generation system
- Enhance the UI and user experience

## 📜 License

This project is open source. See the LICENSE file for details.

---

**Ready to test your survival skills?** The wilderness awaits, but remember - in Fantasy RPG, nature doesn't forgive mistakes. Every decision could be your last.

*Type `python play.py` to begin your adventure.*