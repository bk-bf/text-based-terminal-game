"""
Fantasy RPG - User Interface (Legacy)

This file now imports from the refactored UI module.
The UI has been split into:
- ui/panels.py - Visual display components
- ui/screens.py - Modal screens and main screen  
- ui/app.py - Main application and input handling
"""

# Import from the new modular UI structure
from .ui import FantasyRPGApp, run_ui

# Legacy compatibility - everything is now in the ui/ module
if __name__ == "__main__":
    from .ui.app import test_inventory_screen
    test_inventory_screen()