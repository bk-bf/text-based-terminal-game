"""MessageManager: Centralized message library with context-aware variance.

This module provides the MessageManager class which loads and manages
natural language message variants for game events, ensuring varied and
immersive text output without repetition.
"""

import json
import random
from pathlib import Path
from typing import Optional


class MessageManager:
    """Centralized message library with context-aware variance.
    
    Loads message variants from event_messages.json and provides methods
    to retrieve random variants for different event types (survival effects,
    equipment changes, environmental events, and player actions).
    
    All messages are sourced from JSON to avoid hardcoded strings and
    enable easy content updates without code changes.
    """
    
    def __init__(self, data_file: str = "event_messages.json"):
        """Initialize MessageManager and load messages from JSON.
        
        Args:
            data_file: Name of JSON file containing message library
                      (defaults to event_messages.json in dialogue directory)
        """
        self.data_file = Path(__file__).parent / data_file
        self.messages = self._load_messages()
        self._validate_structure()
    
    def _load_messages(self) -> dict:
        """Load all messages from JSON file.
        
        Returns:
            Dict containing all message categories and variants
            Empty dict if file not found (with warning logged)
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.data_file} not found. Using empty message library.")
            return {
                'survival_effects': {},
                'beneficial_effects': {},
                'equipment_effects': {},
                'environmental': {},
                'actions': {}
            }
        except json.JSONDecodeError as e:
            print(f"Warning: Error parsing {self.data_file}: {e}")
            return {
                'survival_effects': {},
                'beneficial_effects': {},
                'equipment_effects': {},
                'environmental': {},
                'actions': {}
            }
    
    def _validate_structure(self) -> None:
        """Ensure all expected message types exist.
        
        Logs warnings for missing categories or empty message arrays.
        Does not fail silently - validation errors are visible during development.
        """
        required_categories = ['survival_effects', 'beneficial_effects', 'equipment_effects', 'environmental', 'actions']
        
        for category in required_categories:
            if category not in self.messages:
                print(f"Warning: Missing message category '{category}' in {self.data_file}")
                self.messages[category] = {}
            elif not isinstance(self.messages[category], dict):
                print(f"Warning: Message category '{category}' is not a dict in {self.data_file}")
                self.messages[category] = {}
        
        # Validate individual event types have message arrays
        for category, events in self.messages.items():
            for event_type, messages in events.items():
                if not isinstance(messages, list):
                    print(f"Warning: Messages for '{category}.{event_type}' is not a list")
                elif len(messages) == 0:
                    print(f"Warning: Empty message array for '{category}.{event_type}'")
    
    def get_survival_message(self, event: str, context: Optional[dict] = None) -> str:
        """Returns random survival message variant.
        
        Args:
            event: Event type like 'COLD_triggered', 'HUNGER_triggered', etc
            context: Optional dict with context data (temperature, severity, etc)
                    Reserved for future context-aware selection
        
        Returns:
            Random message from pool, or fallback if event not found
            
        Examples:
            >>> manager.get_survival_message('COLD_triggered')
            'A chill runs through you. Your fingers grow stiff and numb from the cold.'
            
            >>> manager.get_survival_message('HUNGER_triggered', {'hunger_level': 800})
            'Your stomach growls loudly, demanding sustenance.'
        """
        messages = self.messages.get('survival_effects', {}).get(event, [])
        
        if not messages:
            # Fallback message if event not found
            event_name = event.replace('_triggered', '').replace('_', ' ').lower()
            return f"You experience {event_name}."
        
        return random.choice(messages)
    
    def get_equipment_message(self, event: str, **kwargs) -> str:
        """Returns random equipment message with template substitution.
        
        Args:
            event: Event type like 'armor_equipped', 'weapon_equipped', etc
            **kwargs: Template variables to interpolate
                     ({armor_name}, {weapon_name}, {item_name}, etc)
        
        Returns:
            Random message with variables interpolated
            
        Examples:
            >>> manager.get_equipment_message('armor_equipped', armor_name='Iron Breastplate')
            'You don the Iron Breastplate, settling into its familiar weight.'
            
            >>> manager.get_equipment_message('weapon_equipped', weapon_name='Longsword')
            'You draw the Longsword, feeling its weight in your hand.'
        """
        messages = self.messages.get('equipment_effects', {}).get(event, [])
        
        if not messages:
            # Fallback message if event not found
            event_name = event.replace('_', ' ').lower()
            return f"You {event_name}."
        
        # Select random message and interpolate template variables
        message = random.choice(messages)
        
        try:
            return message.format(**kwargs)
        except KeyError as e:
            # Handle missing template variable gracefully
            print(f"Warning: Missing template variable {e} for event '{event}'")
            # Return message with unsubstituted variables visible for debugging
            return message
    
    def get_environmental_message(self, event: str) -> str:
        """Returns random environmental/weather message or beneficial condition message.
        
        Args:
            event: Event type like 'weather_change_to_rain', 'enter_cold_area',
                  'LIT_FIRE_triggered', 'NATURAL_SHELTER_triggered', etc
        
        Returns:
            Random message from pool, or fallback if event not found
            
        Examples:
            >>> manager.get_environmental_message('weather_change_to_rain')
            'Dark clouds gather overhead. The first drops of rain begin to fall.'
            
            >>> manager.get_environmental_message('LIT_FIRE_triggered')
            'The dancing flames warm your skin and lift your spirits.'
        """
        # Check environmental category first
        messages = self.messages.get('environmental', {}).get(event, [])
        
        # If not found, check beneficial_effects category
        if not messages:
            messages = self.messages.get('beneficial_effects', {}).get(event, [])
        
        if not messages:
            # Fallback message if event not found
            event_name = event.replace('weather_change_to_', '').replace('enter_', '').replace('_triggered', '').replace('_', ' ').lower()
            return f"The environment changes to {event_name}."
        
        return random.choice(messages)
    
    def get_action_message(self, event: str, **kwargs) -> str:
        """Returns random action result message with templates.
        
        Args:
            event: Event type like 'forage_success', 'hunt_failure', etc
            **kwargs: Template variables to interpolate
                     ({item_name}, {quantity}, {prey_type}, etc)
        
        Returns:
            Random message with variables interpolated
            
        Examples:
            >>> manager.get_action_message('forage_success', item_name='mushroom', quantity=3)
            'Your search yields 3 mushroom. A fortunate find.'
            
            >>> manager.get_action_message('hunt_success', prey_type='deer')
            'You successfully hunt deer. Fresh meat is yours.'
        """
        messages = self.messages.get('actions', {}).get(event, [])
        
        if not messages:
            # Fallback message if event not found
            event_name = event.replace('_', ' ').lower()
            return f"Action result: {event_name}."
        
        # Select random message and interpolate template variables
        message = random.choice(messages)
        
        try:
            return message.format(**kwargs)
        except KeyError as e:
            # Handle missing template variable gracefully
            print(f"Warning: Missing template variable {e} for event '{event}'")
            # Return message with unsubstituted variables visible for debugging
            return message
