"""
Fantasy RPG - User Interface Module

Clean separation of UI components:
- panels: Visual display panels (Character, GameLog, POI)
- screens: Modal screens and main screen
- app: Main application and input handling
"""

from .app import FantasyRPGApp, run_ui

__all__ = ['FantasyRPGApp', 'run_ui']