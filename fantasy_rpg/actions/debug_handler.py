"""
Fantasy RPG - Debug Handler

Handles all debug and system commands:
- Debug info display
- World/location/hex data dumping
- Save/load game
- Help display
- Game log saving
"""

from typing import Any
from .base_handler import BaseActionHandler, ActionResult


class DebugHandler(BaseActionHandler):
    """Handler for debug and system commands"""
    
    def handle_help(self, *args) -> ActionResult:
        """Handle help display with shortkey support"""
        # Get shortkey help from manager
        try:
            from .shortkey_manager import get_shortkey_manager
            shortkey_manager = get_shortkey_manager()
            shortkey_help = shortkey_manager.get_action_help()
        except ImportError:
            shortkey_help = ""
        
        help_text = f"""{shortkey_help}

=== FULL COMMAND LIST ===

Core Actions:
  look / l - Examine your surroundings
  enter - Enter a location in this hex (no arguments needed)
  exit - Exit current location to overworld
  
Object Interaction (location only):
  examine/x <object> - Examine an object closely (shows available actions)
  search/a <object> - Search an object for items
  use/u <object> - Use an object (context-specific)
  
Resource Gathering (location only):
  forage/g <object> - Gather resources using Survival skill
  harvest/v <object> - Gather resources using Nature skill
  chop/h <object> - Chop wood from trees or objects (destroys object)
  drink/b <object> - Drink from water sources
  
Object Manipulation (location only):
  unlock/k <object> - Pick locks on containers
  disarm <object> - Disarm traps on objects
  light/f <object> - Light fires in fireplaces or similar objects
  
Rest & Recovery (location only):
  rest/r - Rest in current location (recovery)
  wait/wa <duration> - Wait and pass time (quick/short/medium/long/extended)
  
Movement (overworld only):
  north/n, south/s, east/e, west/w - Move in that direction
  
Character:
  inventory/i - View your inventory
  character/c - View character sheet
  
System:
  save - Save game to save.json
  load - Load game from save.json
  help/? - Show this help
  
=== DEBUG COMMANDS (Out-of-Character Knowledge) ===
  debug - Show debug information
  dump_location - Dump current location data to JSON file
  dump_hex - Dump current hex data to JSON file
  dump_world - Dump entire world data to JSON file
  dump_history - Dump complete history and genealogy to markdown files in /history
  
  research <type> [name] - Access omniscient world knowledge (NOT character knowledge!)
    Types: events, figures, heroes, villains, artifacts, memory, civilizations, genealogy, territorial
    Examples: research genealogy - Shows genealogy statistics
              research genealogy <name> - Shows specific family tree
              research territorial - Overview of all territories
              research territorial <civ name> - Detailed territorial history
    Note: These commands show ALL world history/data for testing purposes.
          Your character would NOT know this information in-game.
          This will be replaced with proper character-knowledge system later.
  
Tip: Objects have permanent shortcuts like [fp] for fireplace, [we] for well!
Example: 'f fp' lights the fireplace, 'b we' drinks from the well"""
        
        return ActionResult(
            success=True,
            message=help_text,
            time_passed=0.0,
            action_type="help"
        )
    
    def _get_basic_debug_info(self, gs: Any) -> list[str]:
        """Extract basic game state debug information"""
        return [
            f"Current hex: {gs.world_position.hex_id}",
            f"Coordinates: {gs.world_position.coords}",
            f"In location: {gs.world_position.current_location_id or 'No'}",
            f"Time: {gs.game_time.get_time_string()}, {gs.game_time.get_date_string()}",
            f"Weather: {gs.current_weather.temperature:.0f}°F",
            f"Character HP: {gs.character.hp}/{gs.character.max_hp}"
        ]
    
    def _get_location_debug_info(self, location_data: dict[str, Any], starting_area_id: str) -> list[str]:
        """Extract location-specific debug information"""
        info = [
            f"Location: {location_data.get('name', 'Unknown')}",
            f"Starting area: {starting_area_id}"
        ]
        
        areas = location_data.get("areas", {})
        if starting_area_id not in areas:
            return info
        
        area_data = areas[starting_area_id]
        objects = area_data.get("objects", [])
        items = area_data.get("items", [])
        
        info.append(f"Objects in area: {len(objects)}")
        info.extend(
            f"  {i+1}. {obj.get('name', 'Unknown')} (id: {obj.get('id', 'unknown')})"
            for i, obj in enumerate(objects[:5])
        )
        if len(objects) > 5:
            info.append(f"  ...and {len(objects) - 5} more")

        info.append(f"Items in area: {len(items)}")
        info.extend(
            f"  {i+1}. {item.get('name', 'Unknown')} (id: {item.get('id', 'unknown')})"
            for i, item in enumerate(items[:5])
        )
        if len(items) > 5:
            info.append(f"  ...and {len(items) - 5} more")
        
        return info
    
    def handle_debug(self, *args) -> ActionResult:
        """Handle debug information display"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
        gs = self.game_engine.game_state
        if not gs:
            return ActionResult(
                success=True,
                message="=== DEBUG INFO ===\nNo game state available",
                time_passed=0.0,
                action_type="debug"
            )
        
        debug_info = ["=== DEBUG INFO ==="]
        debug_info.extend(self._get_basic_debug_info(gs))
        
        # Add location content debug info if in location
        if gs.world_position.current_location_id and (location_data := gs.world_position.current_location_data):
            starting_area_id = location_data.get("starting_area", "entrance")
            debug_info.extend(self._get_location_debug_info(location_data, starting_area_id))
        
        return ActionResult(
            success=True,
            message="\n".join(debug_info),
            time_passed=0.0,
            action_type="debug"
        )
    
    def _convert_climate_zones_for_json(self, climate_zones: dict[str, Any]) -> dict[str, Any]:
        """Convert climate_zones with tuple keys to JSON-compatible string keys"""
        return {
            f"{key[0]:02d}{key[1]:02d}" if isinstance(key, tuple) else str(key): value
            for key, value in climate_zones.items()
        }
    
    def handle_dump_world(self, *args) -> ActionResult:
        """Handle dumping world data to JSON file"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
        try:
            import json
            
            world_data = {
                "world_size": self.game_engine.world_coordinator.world_size,
                "seed": self.game_engine.world_coordinator.seed,
                "hex_data": self.game_engine.world_coordinator.hex_data,
                "climate_zones": self._convert_climate_zones_for_json(
                    self.game_engine.world_coordinator.climate_zones
                ),
                "loaded_locations": self.game_engine.world_coordinator.loaded_locations
            }
            
            filename = "debug_world_data.json"
            with open(filename, 'w') as f:
                json.dump(world_data, f, indent=2, default=str)
            
            return ActionResult(
                success=True,
                message=f"World data dumped to {filename}",
                time_passed=0.0,
                action_type="debug"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to dump world data: {str(e)}")
    
    def handle_dump_location(self, *args) -> ActionResult:
        """Handle dumping current location data to JSON file - delegates to GameEngine"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
        try:
            success, message = self.game_engine.dump_location_data()
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.0,
                action_type="debug"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to dump location data: {str(e)}")
    
    def handle_dump_hex(self, *args) -> ActionResult:
        """Handle dumping current hex data to JSON file - delegates to GameEngine"""
        if not self.game_engine:
            return ActionResult(False, "Debug system not available.")
        
        try:
            success, message = self.game_engine.dump_hex_data()
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.0,
                action_type="debug"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to dump hex data: {str(e)}")
    
    def handle_save_game(self, *args) -> ActionResult:
        """Handle saving the game - delegates to GameEngine"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        try:
            success, message = self.game_engine.save_game("save")
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.0,
                action_type="system"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to save game: {str(e)}")
    
    def handle_load_game(self, *args) -> ActionResult:
        """Handle loading the game - delegates to GameEngine"""
        if not self.game_engine:
            return ActionResult(False, "Game engine not available.")
        
        try:
            success, message = self.game_engine.load_game("save")
            return ActionResult(
                success=success,
                message=message,
                time_passed=0.0,
                action_type="system"
            )
        except Exception as e:
            return ActionResult(False, f"Failed to load game: {str(e)}")
    
    def handle_save_log(self, *args) -> ActionResult:
        """Handle saving game log to text file"""
        # TODO: Implement save log functionality
        return ActionResult(
            success=True,
            message="Save log functionality not yet implemented.",
            time_passed=0.0,
            action_type="system"
        )
    
    def handle_dump_history(self, *args) -> ActionResult:
        """Handle dumping complete historical timeline and genealogy to markdown files"""
        if not self.game_engine or not self.game_engine.world_coordinator:
            return ActionResult(False, "History system not available.")
        
        import os
        from datetime import datetime
        
        world = self.game_engine.world_coordinator
        historical_events = getattr(world, 'historical_events', [])
        historical_figures = getattr(world, 'historical_figures', [])
        mythic_events = getattr(world, 'mythic_events', [])
        civilizations = getattr(world, 'civilizations', [])
        
        if not historical_events and not mythic_events:
            return ActionResult(False, "No historical data to dump.")
        
        # Create history directory
        history_dir = os.path.join(os.getcwd(), 'history')
        os.makedirs(history_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # === CHRONOLOGICAL HISTORY FILE ===
            history_file = os.path.join(history_dir, f'chronological_history_{timestamp}.md')
            
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write("# Complete Historical Timeline\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"World Seed: {getattr(world, 'seed', 'Unknown')}\n")
                f.write(f"Total Events: {len(mythic_events) + len(historical_events)}\n")
                f.write(f"Total Figures: {len(historical_figures)}\n")
                f.write(f"Total Civilizations: {len(civilizations)}\n\n")
                
                f.write("---\n\n")
                
                # Combine and sort all events chronologically
                all_events = []
                
                # Add mythic events
                for event in mythic_events:
                    all_events.append({
                        'year': event.get('year', 0),
                        'month': event.get('month', 'Unknown'),
                        'day': event.get('day', 0),
                        'season': event.get('season', 'unknown'),
                        'type': 'mythic',
                        'data': event
                    })
                
                # Add historical events
                for event in historical_events:
                    all_events.append({
                        'year': event.year,
                        'month': event.month,
                        'day': event.day,
                        'season': event.season,
                        'type': 'historical',
                        'data': event
                    })
                
                # Sort by year, then month, then day
                month_order = ['Firstbloom', 'Sunwake', 'Highgrowth', 'Goldpeak', 'Harvestmoon', 
                              'Frostturn', 'Deepcold', 'Snowsend', 'Springthaw', 'Rainbirth', 
                              'Warmwind', 'Suncrest']
                
                def sort_key(e):
                    month_idx = month_order.index(e['month']) if e['month'] in month_order else 0
                    return (e['year'], month_idx, e['day'])
                
                all_events.sort(key=sort_key)
                
                # Write events
                current_year = None
                for event_wrapper in all_events:
                    year = event_wrapper['year']
                    month = event_wrapper['month']
                    day = event_wrapper['day']
                    season = event_wrapper['season']
                    event_type = event_wrapper['type']
                    event = event_wrapper['data']
                    
                    # Year header
                    if current_year != year:
                        current_year = year
                        f.write(f"\n## Year {year}\n\n")
                    
                    if event_type == 'mythic':
                        # Mythic event
                        name = event.get('name', 'Unknown Event')
                        description = event.get('description', '')
                        event_category = event.get('event_type', 'unknown')
                        significance = event.get('significance', 5)
                        
                        f.write(f"### {name}\n")
                        f.write(f"**Date:** {month} {day}, {season.title()}\n")
                        f.write(f"**Type:** Mythic/{event_category.replace('_', ' ').title()}\n")
                        f.write(f"**Significance:** {significance}/10\n\n")
                        f.write(f"{description}\n\n")
                        
                        if 'participants' in event and event['participants']:
                            f.write("**Key Figures:**\n")
                            for participant in event['participants']:
                                f.write(f"- {participant['name']} ({participant['role']})\n")
                            f.write("\n")
                        
                        if 'consequences' in event and event['consequences']:
                            f.write("**Consequences:**\n")
                            for consequence in event['consequences']:
                                f.write(f"- {consequence}\n")
                            f.write("\n")
                    
                    else:
                        # Historical event
                        f.write(f"### {event.name}\n")
                        f.write(f"**Date:** {month} {day}, {season.title()}\n")
                        f.write(f"**Type:** {event.event_type.value.replace('_', ' ').title()}\n")
                        f.write(f"**Severity:** {event.severity.value.title()}\n")
                        f.write(f"**Significance:** {event.significance}/10\n\n")
                        f.write(f"{event.description}\n\n")
                        
                        # Primary civilizations
                        if event.primary_civilizations:
                            civ_names = []
                            for civ_id in event.primary_civilizations:
                                civ = next((c for c in civilizations if c.id == civ_id), None)
                                civ_names.append(civ.name if civ else civ_id)
                            f.write(f"**Primary Civilizations:** {', '.join(civ_names)}\n\n")
                        
                        # Key figures
                        if event.key_figures:
                            f.write("**Key Figures:**\n")
                            for fig_id in event.key_figures:
                                figure = next((fig for fig in historical_figures if fig.id == fig_id), None)
                                if figure:
                                    status = "living" if not figure.death_year else f"died {figure.death_year}"
                                    f.write(f"- {figure.name}, {figure.title} ({status})\n")
                                else:
                                    f.write(f"- {fig_id}\n")
                            f.write("\n")
                        
                        # Duration
                        if event.duration_years and event.duration_years > 0:
                            f.write(f"**Duration:** {event.duration_years} years\n\n")
                        
                        # Casualties
                        if event.casualties and event.casualties > 0:
                            f.write(f"**Casualties:** {event.casualties:,}\n\n")
                        
                        # Relationship changes
                        if event.relationship_changes:
                            f.write("**Diplomatic Changes:**\n")
                            for rc in event.relationship_changes:
                                civ_a = next((c for c in civilizations if c.id == rc.civilization_a), None)
                                civ_b = next((c for c in civilizations if c.id == rc.civilization_b), None)
                                name_a = civ_a.name if civ_a else rc.civilization_a
                                name_b = civ_b.name if civ_b else rc.civilization_b
                                f.write(f"- {name_a} and {name_b}: {rc.old_relationship} → {rc.new_relationship}\n")
                                f.write(f"  *{rc.reason}*\n")
                            f.write("\n")
                        
                        # Territorial changes
                        if event.territorial_changes:
                            f.write("**Territorial Changes:**\n")
                            for tc in event.territorial_changes:
                                civ = next((c for c in civilizations if c.id == tc.civilization), None)
                                name = civ.name if civ else tc.civilization
                                if tc.hexes_gained:
                                    f.write(f"- {name} gained {len(tc.hexes_gained)} hexes\n")
                                if tc.hexes_lost:
                                    f.write(f"- {name} lost {len(tc.hexes_lost)} hexes\n")
                                f.write(f"  *{tc.reason}*\n")
                            f.write("\n")
                        
                        # Caused by / causes future events
                        if event.caused_by_events:
                            f.write(f"**Caused By:** {', '.join(event.caused_by_events)}\n\n")
                        if event.causes_future_events:
                            f.write(f"**Led To:** {', '.join(event.causes_future_events)}\n\n")
                    
                    f.write("---\n\n")
            
            # === GENEALOGY FILE ===
            genealogy_file = os.path.join(history_dir, f'genealogy_{timestamp}.md')
            
            with open(genealogy_file, 'w', encoding='utf-8') as f:
                f.write("# Complete Genealogical Records\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Total Figures: {len(historical_figures)}\n\n")
                
                # Statistics
                living_count = sum(1 for fig in historical_figures if not fig.death_year)
                deceased_count = len(historical_figures) - living_count
                with_children = sum(1 for fig in historical_figures if fig.children)
                founders = [fig for fig in historical_figures if not fig.parents]
                
                f.write("## Statistics\n\n")
                f.write(f"- Living Figures: {living_count}\n")
                f.write(f"- Deceased Figures: {deceased_count}\n")
                f.write(f"- Founding Figures (no parents): {len(founders)}\n")
                f.write(f"- Figures with Children: {with_children}\n")
                f.write(f"- Average Children per Parent: {sum(len(fig.children) for fig in historical_figures) / max(with_children, 1):.2f}\n\n")
                
                f.write("---\n\n")
                
                # Group by civilization
                civ_figures = {}
                for figure in historical_figures:
                    civ_id = figure.cultural_origin
                    if civ_id not in civ_figures:
                        civ_figures[civ_id] = []
                    civ_figures[civ_id].append(figure)
                
                for civ_id, figures in sorted(civ_figures.items()):
                    civ = next((c for c in civilizations if c.id == civ_id), None)
                    civ_name = civ.name if civ else civ_id
                    
                    f.write(f"## {civ_name}\n\n")
                    f.write(f"Total Figures: {len(figures)}\n\n")
                    
                    # Sort by birth year
                    figures.sort(key=lambda fig: fig.birth_year)
                    
                    for figure in figures:
                        f.write(f"### {figure.name}\n")
                        f.write(f"**Title:** {figure.title}\n")
                        f.write(f"**Race:** {figure.race}\n")
                        f.write(f"**Born:** {figure.birth_year}\n")
                        if figure.death_year:
                            age = figure.death_year - figure.birth_year
                            f.write(f"**Died:** {figure.death_year} (age {age})\n")
                        else:
                            current_year = getattr(self.game_engine.time_system, 'year', figure.birth_year)
                            age = current_year - figure.birth_year
                            f.write(f"**Status:** Living (age {age})\n")
                        
                        f.write(f"**Alignment:** {figure.alignment}\n")
                        f.write(f"**Archetype:** {figure.archetype.replace('_', ' ').title()}\n\n")
                        
                        # Family
                        f.write("**Family:**\n")
                        
                        # Parents
                        if figure.parents:
                            mother_id, father_id = figure.parents
                            mother = next((fig for fig in historical_figures if fig.id == mother_id), None)
                            father = next((fig for fig in historical_figures if fig.id == father_id), None)
                            if mother:
                                f.write(f"- Mother: {mother.name} ({mother.birth_year}-{mother.death_year or 'present'})\n")
                            if father:
                                f.write(f"- Father: {father.name} ({father.birth_year}-{father.death_year or 'present'})\n")
                        else:
                            f.write("- Founding figure (no recorded parents)\n")
                        
                        # Spouse
                        if figure.spouse:
                            spouse = next((fig for fig in historical_figures if fig.id == figure.spouse), None)
                            if spouse:
                                f.write(f"- Spouse: {spouse.name} ({spouse.birth_year}-{spouse.death_year or 'present'})\n")
                        
                        # Children
                        if figure.children:
                            f.write(f"- Children ({len(figure.children)}):\n")
                            for child_id in figure.children:
                                child = next((fig for fig in historical_figures if fig.id == child_id), None)
                                if child:
                                    status = "living" if not child.death_year else f"died {child.death_year}"
                                    f.write(f"  - {child.name} (born {child.birth_year}, {status})\n")
                        
                        f.write("\n")
                        
                        # Achievements
                        if figure.achievements:
                            f.write("**Achievements:**\n")
                            for achievement in figure.achievements:
                                f.write(f"- {achievement}\n")
                            f.write("\n")
                        
                        # Event participation
                        if figure.participated_in_events:
                            f.write(f"**Historical Events:** Participated in {len(figure.participated_in_events)} events\n")
                            for event_id in figure.participated_in_events[:5]:  # Show first 5
                                event = next((e for e in historical_events if e.id == event_id), None)
                                if event:
                                    f.write(f"- {event.name} ({event.year})\n")
                            if len(figure.participated_in_events) > 5:
                                f.write(f"- ... and {len(figure.participated_in_events) - 5} more\n")
                            f.write("\n")
                        
                        # Legacy
                        if figure.legendary_status:
                            f.write(f"**Legacy:** {figure.legendary_status.replace('_', ' ').title()}\n")
                            if figure.remembered_as:
                                f.write(f"**Remembered As:** {figure.remembered_as}\n")
                            f.write(f"**Cultural Significance:** {figure.cultural_significance}/10\n")
                            f.write(f"**Memory Strength:** {figure.memory_strength}/10\n\n")
                        
                        # Personality
                        if figure.personality_traits:
                            f.write(f"**Personality:** {', '.join(figure.personality_traits)}\n\n")
                        
                        # Backstory
                        if figure.backstory:
                            f.write("**Backstory:**\n")
                            f.write(f"{figure.backstory}\n\n")
                        
                        f.write("---\n\n")
            
            return ActionResult(
                success=True,
                message=f"History dumped successfully!\n"
                        f"Chronological History: {history_file}\n"
                        f"Genealogy Records: {genealogy_file}\n"
                        f"Total Events: {len(all_events)}\n"
                        f"Total Figures: {len(historical_figures)}",
                time_passed=0.0,
                action_type="debug"
            )
        
        except Exception as e:
            return ActionResult(False, f"Failed to dump history: {str(e)}")
    
    def handle_research(self, *args) -> ActionResult:
        """Handle researching historical events, figures, and artifacts
        
        DEBUG COMMAND: Shows omniscient world knowledge for testing.
        Character would NOT know this information in-game.
        """
        if not self.game_engine or not self.game_engine.world_coordinator:
            return ActionResult(False, "Research system not available.")
        
        if not args:
            return ActionResult(
                False, 
                "Usage: research <type> [name]\nTypes: events, figures, heroes, villains, artifacts, memory, civilizations, genealogy, territorial\n\n⚠️  DEBUG: This shows omniscient world knowledge. Your character would NOT know this in-game!"
            )
        
        research_type = args[0].lower()
        world = self.game_engine.world_coordinator
        
        # Add debug warning header
        debug_warning = "[cyan]⚠️  DEBUG MODE: Accessing omniscient world knowledge (not character knowledge!)[/cyan]\n"
        
        # Research mythic AND historical events
        if research_type in ["events", "event", "history"]:
            mythic_events = getattr(world, 'mythic_events', [])
            historical_events = getattr(world, 'historical_events', [])
            
            if not mythic_events and not historical_events:
                return ActionResult(False, "No historical events found in this world.")
            
            info = [debug_warning]
            
            # Show mythic/foundational events first
            if mythic_events:
                info.append(f"=== MYTHIC/FOUNDATIONAL EVENTS ({len(mythic_events)}) ===\n")
                
                for event in sorted(mythic_events, key=lambda e: e.get('year', 0)):
                    year = event.get('year', 0)
                    name = event.get('name', 'Unknown Event')
                    event_type = event.get('event_type', 'myth')
                    significance = event.get('significance', 5)
                    description = event.get('description', '')
                    
                    info.append(f"Year {year}: {name}")
                    info.append(f"  Type: {event_type.replace('_', ' ').title()}")
                    info.append(f"  Significance: {significance}/10")
                    info.append(f"  {description}")
                    
                    # Show participants if available
                    if 'participants' in event and event['participants']:
                        info.append(f"  Key Figures:")
                        for participant in event['participants']:
                            info.append(f"    • {participant['name']} ({participant['role']})")
                    
                    # Show artifacts if available
                    if 'artifact_id' in event:
                        info.append(f"  Legendary Artifact: {event['artifact_id']}")
                    
                    info.append("")  # Blank line between events
            
            # Show historical simulation events
            if historical_events:
                info.append(f"\n=== HISTORICAL EVENTS ({len(historical_events)}) ===\n")
                
                for event in historical_events:
                    # Display with calendar date if available
                    if hasattr(event, 'month') and hasattr(event, 'day') and hasattr(event, 'season'):
                        date_str = f"{event.month} {event.day}, {event.season.capitalize()} {event.year}"
                        info.append(f"{date_str}: {event.name}")
                    else:
                        info.append(f"Year {event.year}: {event.name}")
                    
                    info.append(f"  Type: {event.event_type.value.replace('_', ' ').title()}")
                    info.append(f"  Severity: {event.severity.value.title()}")
                    info.append(f"  Significance: {event.significance}/10")
                    
                    # Show involved civilizations
                    if event.primary_civilizations:
                        civ_names = []
                        for civ_id in event.primary_civilizations:
                            civ = next((c for c in world.civilizations if c.id == civ_id), None)
                            if civ:
                                civ_names.append(civ.name)
                        if civ_names:
                            info.append(f"  Civilizations: {', '.join(civ_names)}")
                    
                    info.append(f"  {event.description}")
                    
                    # Show casualties if significant
                    if event.casualties > 0:
                        info.append(f"  Casualties: ~{event.casualties:,}")
                    
                    # Show relationship changes
                    if event.relationship_changes:
                        info.append(f"  Diplomatic Changes:")
                        for change in event.relationship_changes:
                            civ_a = next((c for c in world.civilizations if c.id == change.civilization_a), None)
                            civ_b = next((c for c in world.civilizations if c.id == change.civilization_b), None)
                            if civ_a and civ_b:
                                info.append(f"    • {civ_a.name} & {civ_b.name}: {change.old_relationship} → {change.new_relationship}")
                    
                    # Show territorial changes
                    if event.territorial_changes:
                        info.append(f"  Territorial Changes:")
                        for change in event.territorial_changes:
                            civ = next((c for c in world.civilizations if c.id == change.civilization), None)
                            if civ:
                                gained = len(change.hexes_gained)
                                lost = len(change.hexes_lost)
                                if gained > 0:
                                    info.append(f"    • {civ.name} gained {gained} regions")
                                if lost > 0:
                                    info.append(f"    • {civ.name} lost {lost} regions")
                    
                    info.append("")  # Blank line between events
            
            return ActionResult(
                success=True,
                message="\n".join(info),
                time_passed=0.0,
                action_type="research"
            )
        
        # Research historical figures
        elif research_type in ["figures", "figure", "heroes", "villains", "people"]:
            if not hasattr(world, 'historical_figures') or not world.historical_figures:
                return ActionResult(False, "No historical figures found in this world.")
            
            # Filter by alignment if specified
            if research_type == "heroes":
                figures = [f for f in world.historical_figures if f.alignment == "hero"]
                title = "LEGENDARY HEROES"
            elif research_type == "villains":
                figures = [f for f in world.historical_figures if f.alignment == "villain"]
                title = "LEGENDARY VILLAINS"
            else:
                figures = world.historical_figures
                title = "HISTORICAL FIGURES"
            
            if not figures:
                return ActionResult(False, f"No {research_type} found in this world.")
            
            info = [debug_warning, f"=== {title} ({len(figures)}) ===\n"]
            
            for figure in sorted(figures, key=lambda f: f.birth_year):
                info.append(f"{figure.name} {figure.title}")
                info.append(f"  Race: {figure.race.title()}")
                info.append(f"  Role: {figure.alignment.title()} ({figure.archetype.replace('_', ' ').title()})")
                info.append(f"  Born: Year {figure.birth_year}")
                if figure.death_year:
                    info.append(f"  Died: Year {figure.death_year}")
                else:
                    info.append(f"  Death: Unknown/Mythic")
                
                # Cultural Memory System (Task 2.2)
                info.append(f"  Significance: {figure.cultural_significance}/10")
                
                # Show legendary status
                if hasattr(figure, 'legendary_status'):
                    status_desc = {
                        "mythic": "⭐ MYTHIC - Spoken of in hushed reverence",
                        "legendary": "★ LEGENDARY - Celebrated in songs and stories",
                        "famous": "✦ FAMOUS - Known to scholars and historians",
                        "known": "· Known - Recorded in historical texts"
                    }
                    info.append(f"  Status: {status_desc.get(figure.legendary_status, figure.legendary_status)}")
                
                # Show how they're remembered
                if hasattr(figure, 'remembered_as') and figure.remembered_as:
                    info.append(f"  Remembered As: {figure.remembered_as.title()}")
                
                # Show cultural influence
                if hasattr(figure, 'cultural_influence') and figure.cultural_influence:
                    influence_str = ", ".join([f"{race}:{val}" for race, val in figure.cultural_influence.items() if val > 0])
                    if influence_str:
                        info.append(f"  Cultural Influence: {influence_str}")
                
                info.append(f"  Traits: {', '.join(figure.personality_traits)}")
                
                if figure.backstory:
                    info.append(f"  Story: {figure.backstory}")
                
                if figure.achievements:
                    info.append(f"  Achievements:")
                    for achievement in figure.achievements[:3]:  # Limit to 3
                        info.append(f"    • {achievement}")
                
                if figure.artifacts_owned:
                    info.append(f"  Artifacts: {', '.join(figure.artifacts_owned)}")
                
                # Show family connections if any
                if figure.parents:
                    info.append(f"  Genealogy: Has recorded parents")
                if figure.children:
                    info.append(f"  Legacy: {len(figure.children)} known descendants")
                
                info.append("")  # Blank line between figures
            
            return ActionResult(
                success=True,
                message="\n".join(info),
                time_passed=0.0,
                action_type="research"
            )
        
        # Research artifacts
        elif research_type in ["artifacts", "artifact", "items", "relics"]:
            # Get artifacts from events
            artifacts = set()
            for event in getattr(world, 'mythic_events', []):
                if 'artifact_id' in event:
                    artifacts.add(event['artifact_id'])
            
            if not artifacts:
                return ActionResult(False, "No legendary artifacts found in this world.")
            
            info = [debug_warning, f"=== LEGENDARY ARTIFACTS ({len(artifacts)}) ===\n"]
            
            for artifact_id in sorted(artifacts):
                # Find the event that created it
                creating_event = None
                for event in world.mythic_events:
                    if event.get('artifact_id') == artifact_id:
                        creating_event = event
                        break
                
                info.append(f"Artifact: {artifact_id}")
                if creating_event:
                    info.append(f"  Origin Event: {creating_event.get('name', 'Unknown')}")
                    info.append(f"  Created: Year {creating_event.get('year', 0)}")
                    if 'artifact_lore' in creating_event:
                        info.append(f"  Lore: {creating_event['artifact_lore']}")
                
                # Find who owns it
                for figure in getattr(world, 'historical_figures', []):
                    if artifact_id in figure.artifacts_owned:
                        info.append(f"  Owner: {figure.name} {figure.title}")
                        break
                
                info.append("")
            
            return ActionResult(
                success=True,
                message="\n".join(info),
                time_passed=0.0,
                action_type="research"
            )
        
        # Research cultural memory (Task 2.2)
        elif research_type in ["memory", "culture", "influence", "legacy"]:
            if not hasattr(world, 'historical_figures') or not world.historical_figures:
                return ActionResult(False, "No historical figures found in this world.")
            
            info = [debug_warning, f"=== CULTURAL MEMORY & INFLUENCE ===\n"]
            
            # Sort by memory strength (how well remembered)
            figures_by_memory = sorted(
                world.historical_figures, 
                key=lambda f: getattr(f, 'memory_strength', 0), 
                reverse=True
            )
            
            # Show top 10 most remembered figures
            info.append(f"Most Remembered Figures:")
            for i, figure in enumerate(figures_by_memory[:10], 1):
                memory = getattr(figure, 'memory_strength', 0)
                status = getattr(figure, 'legendary_status', 'known')
                remembered_as = getattr(figure, 'remembered_as', 'historical figure')
                
                status_icon = {
                    "mythic": "⭐",
                    "legendary": "★",
                    "famous": "✦",
                    "known": "·"
                }.get(status, "·")
                
                info.append(f"{i}. {status_icon} {figure.name} {figure.title}")
                info.append(f"   Memory Strength: {memory}/10 | {remembered_as.title()}")
                info.append(f"   {figure.alignment.title()} of {figure.race.title()} origin")
                
                # Show influence across cultures
                if hasattr(figure, 'cultural_influence') and figure.cultural_influence:
                    influence_list = [
                        f"{race.title()}({val})" 
                        for race, val in sorted(figure.cultural_influence.items(), key=lambda x: x[1], reverse=True)
                        if val > 0
                    ]
                    if influence_list:
                        info.append(f"   Influence: {', '.join(influence_list)}")
                info.append("")
            
            # Summary by legendary status
            info.append("\nLegendary Status Distribution:")
            status_counts = {}
            for figure in world.historical_figures:
                status = getattr(figure, 'legendary_status', 'known')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status in ["mythic", "legendary", "famous", "known"]:
                count = status_counts.get(status, 0)
                if count > 0:
                    icon = {"mythic": "⭐", "legendary": "★", "famous": "✦", "known": "·"}[status]
                    info.append(f"  {icon} {status.title()}: {count} figures")
            
            # Cultural influence summary by race
            info.append("\nCultural Influence by Race:")
            race_influence = {}
            for figure in world.historical_figures:
                if hasattr(figure, 'cultural_influence'):
                    for race, influence in figure.cultural_influence.items():
                        if race not in race_influence:
                            race_influence[race] = []
                        race_influence[race].append(influence)
            
            for race, influences in sorted(race_influence.items()):
                avg_influence = sum(influences) / len(influences) if influences else 0
                total_influence = sum(influences)
                info.append(f"  {race.title()}: Avg {avg_influence:.1f}/10 | Total {total_influence} points")
            
            return ActionResult(
                success=True,
                message="\n".join(info),
                time_passed=0.0,
                action_type="research"
            )
        
        # Research civilizations
        elif research_type in ["civilizations", "civilization", "civs", "civ", "cultures", "kingdoms"]:
            if not hasattr(world, 'civilizations') or not world.civilizations:
                return ActionResult(False, "No civilizations found in this world.")
            
            info = [debug_warning, f"=== CIVILIZATIONS ({len(world.civilizations)}) ===\n"]
            
            for civ in sorted(world.civilizations, key=lambda c: c.founded_year):
                info.append(f"{civ.name}")
                
                # Display racial composition
                if civ.race == "mixed":
                    info.append(f"  Type: Cosmopolitan (Mixed-Race)")
                    if hasattr(civ, 'race_percentages') and civ.race_percentages:
                        composition = ", ".join([f"{race.title()} {pct}%" for race, pct in civ.race_percentages.items()])
                        info.append(f"  Composition: {composition}")
                else:
                    info.append(f"  Race: {civ.race.title()}")
                
                info.append(f"  Government: {civ.government_type.value.replace('_', ' ').title()}")
                info.append(f"  Founded: Year {civ.founded_year}")
                info.append(f"  Population: {civ.population:,}")
                
                # Cultural values
                values_str = ", ".join([v.value.replace('_', ' ').title() for v in civ.cultural_values])
                info.append(f"  Values: {values_str}")
                
                # Religion
                info.append(f"  Faith: {civ.religious_beliefs}")
                
                # Description
                info.append(f"  {civ.cultural_description}")
                
                # Territory
                if civ.territory:
                    info.append(f"  Territory: {len(civ.territory.hex_coordinates)} regions")
                    capital_hex = civ.territory.capital_hex
                    info.append(f"  Capital: Hex {capital_hex[0]:02d}{capital_hex[1]:02d}")
                    if civ.territory.territorial_description:
                        info.append(f"  {civ.territory.territorial_description}")
                
                # Founding figures
                if civ.founding_figures:
                    founder_names = []
                    for fig_id in civ.founding_figures:
                        # Find the figure
                        for fig in world.historical_figures:
                            if fig.id == fig_id:
                                founder_names.append(f"{fig.name} {fig.title}")
                                break
                    if founder_names:
                        info.append(f"  Founders: {', '.join(founder_names)}")
                
                # Notable features
                if civ.notable_features:
                    info.append(f"  Notable Features:")
                    for feature in civ.notable_features[:3]:  # Limit to 3
                        info.append(f"    • {feature}")
                
                # Relationships with other civilizations
                if civ.faction_relationships:
                    info.append(f"  Relations:")
                    for other_civ_id, relationship in civ.faction_relationships.items():
                        # Find the other civilization
                        other_civ_name = None
                        for other_civ in world.civilizations:
                            if other_civ.id == other_civ_id:
                                other_civ_name = other_civ.name
                                break
                        if other_civ_name:
                            rel_symbol = {
                                "allied": "⚔️ Allied",
                                "friendly": "🤝 Friendly",
                                "neutral": "⚖️ Neutral",
                                "tense": "⚠️ Tense",
                                "hostile": "⚔️ Hostile",
                                "at_war": "⚔️ AT WAR"
                            }.get(relationship.value, relationship.value)
                            info.append(f"    {rel_symbol} with {other_civ_name}")
                
                info.append("")  # Blank line between civilizations
            
            # Summary statistics
            info.append("=== CIVILIZATION SUMMARY ===")
            
            # By race
            race_counts = {}
            mixed_count = 0
            for civ in world.civilizations:
                if civ.race == "mixed":
                    mixed_count += 1
                else:
                    race_counts[civ.race] = race_counts.get(civ.race, 0) + 1
            
            info.append("\nBy Type:")
            for race, count in sorted(race_counts.items(), key=lambda x: x[1], reverse=True):
                info.append(f"  {race.title()}: {count} civilization{'s' if count > 1 else ''}")
            if mixed_count > 0:
                info.append(f"  Mixed/Cosmopolitan: {mixed_count} civilization{'s' if mixed_count > 1 else ''}")
            
            # By government type
            gov_counts = {}
            for civ in world.civilizations:
                gov_type = civ.government_type.value.replace('_', ' ').title()
                gov_counts[gov_type] = gov_counts.get(gov_type, 0) + 1
            info.append("\nBy Government:")
            for gov, count in sorted(gov_counts.items(), key=lambda x: x[1], reverse=True):
                info.append(f"  {gov}: {count}")
            
            # Total population
            total_pop = sum(civ.population for civ in world.civilizations)
            info.append(f"\nTotal Population: {total_pop:,}")
            
            # Relationship overview
            relationship_counts = {}
            for civ in world.civilizations:
                for rel in civ.faction_relationships.values():
                    rel_name = rel.value.replace('_', ' ').title()
                    relationship_counts[rel_name] = relationship_counts.get(rel_name, 0) + 1
            
            if relationship_counts:
                info.append("\nInter-Civilization Relations:")
                for rel, count in sorted(relationship_counts.items(), key=lambda x: x[1], reverse=True):
                    info.append(f"  {rel}: {count} relationships")
            
            return ActionResult(
                success=True,
                message="\n".join(info),
                time_passed=0.0,
                action_type="research"
            )
        
        # Research genealogy (Task 4.2)
        elif research_type in ["genealogy", "family", "lineage", "ancestry"]:
            if not hasattr(world, 'historical_figures') or not world.historical_figures:
                return ActionResult(False, "No historical figures found in this world.")
            
            info = [debug_warning, f"=== GENEALOGY RESEARCH ===\n"]
            
            # If name provided, show specific family tree
            if len(args) > 1:
                search_name = " ".join(args[1:]).lower()
                matching_figures = [f for f in world.historical_figures 
                                   if search_name in f.name.lower()]
                
                if not matching_figures:
                    return ActionResult(False, f"No figure found matching '{search_name}'")
                
                # Show family tree for first match
                figure = matching_figures[0]
                info.append(f"Family Tree for: {figure.name} {figure.title}")
                info.append(f"Born: {figure.birth_year}" + (f", Died: {figure.death_year}" if figure.death_year else " (no recorded death)"))
                info.append("")
                
                # Show parents
                if figure.parents:
                    info.append("Parents:")
                    mother = next((f for f in world.historical_figures if f.id == figure.parents[0]), None)
                    father = next((f for f in world.historical_figures if f.id == figure.parents[1]), None)
                    if mother:
                        info.append(f"  Mother: {mother.name} ({mother.birth_year}-{mother.death_year or '?'})")
                    if father:
                        info.append(f"  Father: {father.name} ({father.birth_year}-{father.death_year or '?'})")
                    info.append("")
                
                # Show spouse
                if figure.spouse:
                    spouse = next((f for f in world.historical_figures if f.id == figure.spouse), None)
                    if spouse:
                        info.append(f"Spouse: {spouse.name} ({spouse.birth_year}-{spouse.death_year or '?'})")
                        info.append("")
                
                # Show children
                if figure.children:
                    info.append(f"Children ({len(figure.children)}):")
                    for child_id in figure.children:
                        child = next((f for f in world.historical_figures if f.id == child_id), None)
                        if child:
                            status = " ✝" if child.death_year else ""
                            info.append(f"  • {child.name} ({child.birth_year}-{child.death_year or 'living'}){status}")
                    info.append("")
                
                # Show descendants count
                def count_descendants(fig_id, visited=None):
                    if visited is None:
                        visited = set()
                    if fig_id in visited:
                        return 0
                    visited.add(fig_id)
                    
                    fig = next((f for f in world.historical_figures if f.id == fig_id), None)
                    if not fig or not fig.children:
                        return 0
                    
                    count = len(fig.children)
                    for child_id in fig.children:
                        count += count_descendants(child_id, visited)
                    return count
                
                total_descendants = count_descendants(figure.id)
                if total_descendants > 0:
                    info.append(f"Total Descendants: {total_descendants}")
                
                # Show siblings
                if figure.parents:
                    siblings = [f for f in world.historical_figures 
                               if f.parents == figure.parents and f.id != figure.id]
                    if siblings:
                        info.append(f"\nSiblings ({len(siblings)}):")
                        for sibling in siblings:
                            info.append(f"  • {sibling.name}")
            
            else:
                # Show general genealogy statistics
                info.append("GENEALOGY STATISTICS\n")
                
                # Founder figures (no parents)
                founders = [f for f in world.historical_figures if not f.parents]
                info.append(f"Founding Figures (no known parents): {len(founders)}")
                
                # Figures with children
                parents = [f for f in world.historical_figures if f.children]
                info.append(f"Figures with children: {len(parents)}")
                
                # Average children per parent
                if parents:
                    avg_children = sum(len(f.children) for f in parents) / len(parents)
                    info.append(f"Average children per parent: {avg_children:.1f}")
                
                # Largest families (most children)
                info.append("\n=== LARGEST FAMILIES ===")
                largest_families = sorted(parents, key=lambda f: len(f.children), reverse=True)[:10]
                for i, figure in enumerate(largest_families, 1):
                    info.append(f"{i}. {figure.name}: {len(figure.children)} children")
                
                # Most generations
                info.append("\n=== DEEPEST LINEAGES ===")
                def get_max_depth(fig_id, visited=None):
                    if visited is None:
                        visited = set()
                    if fig_id in visited:
                        return 0
                    visited.add(fig_id)
                    
                    fig = next((f for f in world.historical_figures if f.id == fig_id), None)
                    if not fig or not fig.children:
                        return 1
                    
                    max_child_depth = max((get_max_depth(child_id, visited.copy()) 
                                          for child_id in fig.children), default=0)
                    return 1 + max_child_depth
                
                lineage_depths = [(f, get_max_depth(f.id)) for f in founders]
                deepest_lineages = sorted(lineage_depths, key=lambda x: x[1], reverse=True)[:5]
                for i, (figure, depth) in enumerate(deepest_lineages, 1):
                    info.append(f"{i}. {figure.name}: {depth} generations")
                
                info.append("\nUse 'research genealogy <name>' to see a specific family tree")
            
            return ActionResult(
                success=True,
                message="\n".join(info),
                time_passed=0.0,
                action_type="research"
            )
        
        # Research territorial development
        elif research_type in ["territorial", "territory", "expansion", "borders", "lands"]:
            if not hasattr(world, 'civilizations') or not world.civilizations:
                return ActionResult(False, "No civilizations found in this world.")
            
            info = [debug_warning, f"=== TERRITORIAL DEVELOPMENT ===\n"]
            
            # If civilization name provided, show specific history
            if len(args) > 1:
                search_name = " ".join(args[1:]).lower()
                matching_civs = [c for c in world.civilizations 
                               if search_name in c.name.lower()]
                
                if not matching_civs:
                    return ActionResult(False, f"No civilization found matching '{search_name}'")
                
                civ = matching_civs[0]
                info.append(f"Territorial History: {civ.name}")
                info.append(f"Founded: Year {civ.founded_year}")
                
                if civ.territory:
                    info.append(f"Current Territory: {len(civ.territory.hex_coordinates)} regions")
                    info.append(f"Current Population: {civ.territory.population_estimate:,}")
                    info.append("")
                    
                    # Show territorial history timeline
                    if hasattr(civ, 'territorial_history') and civ.territorial_history:
                        info.append("=== TERRITORIAL CHANGES ===")
                        info.append("")
                        
                        for entry in sorted(civ.territorial_history, key=lambda x: x['year']):
                            year = entry['year']
                            event_name = entry.get('event_name', 'Unknown Event')
                            gained = entry.get('hexes_gained', 0)
                            lost = entry.get('hexes_lost', 0)
                            net = entry.get('net_change', 0)
                            total = entry.get('total_hexes', 0)
                            reason = entry.get('reason', 'Unknown reason')
                            
                            # Format change indicator
                            if net > 0:
                                change_indicator = f"[green]+{net}[/green]"
                                change_desc = f"gained {gained} region{'s' if gained != 1 else ''}"
                            elif net < 0:
                                change_indicator = f"[red]{net}[/red]"
                                change_desc = f"lost {lost} region{'s' if lost != 1 else ''}"
                            else:
                                change_indicator = "±0"
                                change_desc = "no net change"
                            
                            info.append(f"Year {year}: {event_name}")
                            info.append(f"  {change_indicator} {change_desc}")
                            info.append(f"  Total territory: {total} regions")
                            info.append(f"  Reason: {reason}")
                            info.append("")
                        
                        # Calculate total growth
                        if civ.territorial_history:
                            first_entry = min(civ.territorial_history, key=lambda x: x['year'])
                            last_entry = max(civ.territorial_history, key=lambda x: x['year'])
                            
                            # Estimate starting size (work backwards from first change)
                            first_total = first_entry.get('total_hexes', 0)
                            first_change = first_entry.get('net_change', 0)
                            starting_size = first_total - first_change
                            
                            current_size = len(civ.territory.hex_coordinates)
                            total_growth = current_size - starting_size
                            growth_pct = (total_growth / max(1, starting_size)) * 100
                            
                            info.append("=== GROWTH SUMMARY ===")
                            info.append(f"Starting Territory (~Year {first_entry['year']}): {starting_size} regions")
                            info.append(f"Current Territory: {current_size} regions")
                            info.append(f"Total Growth: {total_growth:+d} regions ({growth_pct:+.1f}%)")
                            info.append(f"Number of Territorial Events: {len(civ.territorial_history)}")
                    else:
                        info.append("No recorded territorial changes for this civilization.")
                else:
                    info.append("This civilization has no territory data.")
            
            else:
                # Show overview of all civilizations' territorial development
                info.append("Overview of all civilization territories:")
                info.append("")
                
                civs_with_territory = [c for c in world.civilizations if c.territory]
                
                for civ in sorted(civs_with_territory, key=lambda c: len(c.territory.hex_coordinates), reverse=True):
                    current_size = len(civ.territory.hex_coordinates)
                    info.append(f"{civ.name}")
                    info.append(f"  Current Territory: {current_size} regions")
                    info.append(f"  Founded: Year {civ.founded_year}")
                    
                    # Show territorial history stats
                    if hasattr(civ, 'territorial_history') and civ.territorial_history:
                        num_changes = len(civ.territorial_history)
                        total_gained = sum(e.get('hexes_gained', 0) for e in civ.territorial_history)
                        total_lost = sum(e.get('hexes_lost', 0) for e in civ.territorial_history)
                        net_change = total_gained - total_lost
                        
                        info.append(f"  Territorial Events: {num_changes}")
                        info.append(f"  Total Regions Gained: {total_gained}")
                        info.append(f"  Total Regions Lost: {total_lost}")
                        info.append(f"  Net Change: {net_change:+d}")
                    else:
                        info.append(f"  No recorded territorial changes")
                    
                    info.append("")
                
                info.append("\nUse 'research territorial <civilization name>' for detailed history")
            
            return ActionResult(
                success=True,
                message="\n".join(info),
                time_passed=0.0,
                action_type="research"
            )
        
        else:
            return ActionResult(
                False,
                f"Unknown research type: {research_type}\n"
                "Available types: events, figures, heroes, villains, artifacts, memory, civilizations, genealogy, territorial\n\n"
                "⚠️  DEBUG: This shows omniscient world knowledge. Your character would NOT know this in-game!"
            )
