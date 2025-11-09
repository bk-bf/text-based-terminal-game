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
  
  research <type> - Access omniscient world knowledge (NOT character knowledge!)
    Types: events, figures, heroes, villains, artifacts, memory, civilizations
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
                "Usage: research <type> [name]\nTypes: events, figures, heroes, villains, artifacts, memory, civilizations\n\n⚠️  DEBUG: This shows omniscient world knowledge. Your character would NOT know this in-game!"
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
        
        else:
            return ActionResult(
                False,
                f"Unknown research type: {research_type}\n"
                "Available types: events, figures, heroes, villains, artifacts, memory, civilizations\n\n"
                "⚠️  DEBUG: This shows omniscient world knowledge. Your character would NOT know this in-game!"
            )
