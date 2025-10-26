"""
Fantasy RPG - Action Handler

Coordinates action execution and logging between UI components.
"""

from typing import Dict, Any, Optional
from .action_logger import get_action_logger


class ActionHandler:
    """Handles action execution and coordinates logging"""
    
    def __init__(self, app):
        self.app = app
        self.action_logger = get_action_logger()
        
        # Set up action logger with game log
        if hasattr(app, 'game_log_panel'):
            self.action_logger.set_game_log(app.game_log_panel)
    
    def handle_movement(self, direction: str):
        """Handle movement actions"""
        if not self.app.poi_panel or not self.app.poi_panel.can_travel_to(direction):
            self.action_logger.game_log_panel.add_message(f"Cannot travel {direction} from here.")
            self.action_logger.game_log_panel.add_message("")
            return
        
        destination_hex = self.app.poi_panel.get_destination_hex(direction)
        destination_info = self.app.poi_panel.get_location_by_hex(destination_hex)
        
        # Execute travel through time system
        result = {"success": True, "message": ""}
        if self.app.time_system:
            result = self.app.time_system.perform_activity("travel", destination=destination_info["name"])
        
        if result["success"]:
            # Update location
            self.app.update_location(destination_hex, destination_info["name"], "320 ft")
            
            # Get nearby locations for logging
            nearby_locations = []
            if self.app.poi_panel:
                nearby = self.app.poi_panel.get_nearby_locations()
                for loc in nearby:
                    nearby_locations.append({
                        'symbol': self.app.poi_panel._get_location_symbol(loc["type"]),
                        'name': loc["name"],
                        'direction': loc["direction"]
                    })
            
            # Log the complete action
            self.action_logger.log_action_result(
                "move",
                result,
                character=self.app.character,
                player_state=self.app.player_state,
                destination=destination_info["name"],
                hex_id=destination_hex,
                elevation="320 ft",
                nearby_locations=nearby_locations
            )
        else:
            # Log failed travel
            self.action_logger.log_action_result(
                "move",
                result,
                character=self.app.character,
                player_state=self.app.player_state,
                destination=destination_info["name"]
            )
    
    def handle_look(self):
        """Handle look actions"""
        result = {"success": True, "message": ""}
        if self.app.time_system:
            result = self.app.time_system.perform_activity("look")
        
        # Get location info
        location_info = None
        weather_desc = None
        
        if self.app.poi_panel:
            location_info = self.app.poi_panel.get_current_location_info()
        
        if self.app.player_state and self.app.player_state.current_weather:
            weather_desc = self.app.player_state.current_weather.get_description()
        
        # Log the complete action
        self.action_logger.log_action_result(
            "look",
            result,
            character=self.app.character,
            player_state=self.app.player_state,
            location_info=location_info,
            weather_desc=weather_desc
        )
    
    def handle_rest(self):
        """Handle rest actions"""
        result = {"success": True, "message": "You rest for a while..."}
        if self.app.time_system:
            result = self.app.time_system.perform_activity("short_rest")
        
        # Log the complete action
        self.action_logger.log_action_result(
            "rest",
            result,
            character=self.app.character,
            player_state=self.app.player_state
        )
        
        # Apply healing after logging
        if result["success"]:
            self.app.heal_character(5)
    
    def handle_eat(self):
        """Handle eating actions"""
        result = {"success": True, "message": "You eat some food and feel less hungry."}
        if self.app.time_system:
            result = self.app.time_system.perform_activity("eat", nutrition_value=200)
        
        # Log the complete action
        self.action_logger.log_action_result(
            "eat",
            result,
            character=self.app.character,
            player_state=self.app.player_state
        )
    
    def handle_drink(self):
        """Handle drinking actions"""
        result = {"success": True, "message": "You drink some water and feel less thirsty."}
        if self.app.time_system:
            result = self.app.time_system.perform_activity("drink", hydration_value=300)
        
        # Log the complete action
        self.action_logger.log_action_result(
            "drink",
            result,
            character=self.app.character,
            player_state=self.app.player_state
        )
    
    def handle_sleep(self):
        """Handle sleep actions"""
        result = {"success": True, "message": "You sleep and wake up refreshed."}
        if self.app.time_system:
            result = self.app.time_system.perform_activity("sleep", sleep_quality="normal")
        
        # Log the complete action
        self.action_logger.log_action_result(
            "sleep",
            result,
            character=self.app.character,
            player_state=self.app.player_state
        )
    
    def handle_map(self):
        """Handle map actions"""
        result = {"success": True, "message": ""}
        
        # Get map info
        current_location = None
        nearby_locations = []
        
        if self.app.poi_panel:
            current_info = self.app.poi_panel.get_current_location_info()
            current_location = {
                'name': current_info['name'],
                'hex': self.app.poi_panel.current_hex
            }
            
            nearby = self.app.poi_panel.get_nearby_locations()
            for loc in nearby:
                nearby_locations.append({
                    'symbol': self.app.poi_panel._get_location_symbol(loc["type"]),
                    'name': loc["name"],
                    'direction': loc["direction"]
                })
        
        # Log the complete action
        self.action_logger.log_action_result(
            "map",
            result,
            character=self.app.character,
            player_state=self.app.player_state,
            current_location=current_location,
            nearby_locations=nearby_locations
        )
    
    def handle_survival_status(self):
        """Handle survival status actions"""
        result = {"success": True, "message": ""}
        
        # Get survival info
        survival_summary = None
        current_time = None
        
        if self.app.player_state:
            survival_summary = self.app.player_state.get_survival_summary()
            current_time = self.app.player_state.get_time_string()
        
        # Log the complete action
        self.action_logger.log_action_result(
            "survival",
            result,
            character=self.app.character,
            player_state=self.app.player_state,
            survival_summary=survival_summary,
            current_time=current_time
        )
    
    def handle_help(self):
        """Handle help actions"""
        result = {"success": True, "message": ""}
        
        # Log the action (help content is handled by the app)
        self.action_logger.log_action_result(
            "help",
            result,
            character=self.app.character,
            player_state=self.app.player_state
        )
        
        # Show help content
        self.app.show_help()
    
    def handle_inventory(self):
        """Handle inventory actions"""
        result = {"success": True, "message": ""}
        
        # Log the action
        self.action_logger.log_action_result(
            "inventory",
            result,
            character=self.app.character,
            player_state=self.app.player_state
        )
        
        # Open inventory screen
        from .screens import InventoryScreen
        self.app.push_screen(InventoryScreen(self.app.character))
    
    def handle_character(self):
        """Handle character sheet actions"""
        result = {"success": True, "message": ""}
        
        # Log the action
        self.action_logger.log_action_result(
            "character",
            result,
            character=self.app.character,
            player_state=self.app.player_state
        )
        
        # Open character screen
        from .screens import CharacterScreen
        self.app.push_screen(CharacterScreen(self.app.character))