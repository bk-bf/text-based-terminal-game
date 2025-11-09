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
  debug - Show debug information
  dump_location - Dump current location data to JSON file
  dump_hex - Dump current hex data to JSON file
  dump_world - Dump entire world data to JSON file
  help/? - Show this help
  
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
        """Handle researching historical events, figures, and artifacts"""
        if not self.game_engine or not self.game_engine.world_coordinator:
            return ActionResult(False, "Research system not available.")
        
        if not args:
            return ActionResult(
                False, 
                "Usage: research <type> [name]\nTypes: events, figures, heroes, villains, artifacts"
            )
        
        research_type = args[0].lower()
        world = self.game_engine.world_coordinator
        
        # Research mythic events
        if research_type in ["events", "event", "history"]:
            if not hasattr(world, 'mythic_events') or not world.mythic_events:
                return ActionResult(False, "No historical events found in this world.")
            
            info = [f"=== MYTHIC EVENTS ({len(world.mythic_events)}) ===\n"]
            
            for event in sorted(world.mythic_events, key=lambda e: e.get('year', 0)):
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
            
            info = [f"=== {title} ({len(figures)}) ===\n"]
            
            for figure in sorted(figures, key=lambda f: f.birth_year):
                info.append(f"{figure.name} {figure.title}")
                info.append(f"  Race: {figure.race.title()}")
                info.append(f"  Role: {figure.alignment.title()} ({figure.archetype.replace('_', ' ').title()})")
                info.append(f"  Born: Year {figure.birth_year}")
                if figure.death_year:
                    info.append(f"  Died: Year {figure.death_year}")
                else:
                    info.append(f"  Death: Unknown/Mythic")
                info.append(f"  Significance: {figure.cultural_significance}/10")
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
            
            info = [f"=== LEGENDARY ARTIFACTS ({len(artifacts)}) ===\n"]
            
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
        
        else:
            return ActionResult(
                False,
                f"Unknown research type: {research_type}\n"
                "Available types: events, figures, heroes, villains, artifacts"
            )
