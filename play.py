#!/usr/bin/env python3
"""
Fantasy RPG - Game Launcher

Simple launcher to start the Fantasy RPG game.
Run this file to play the game.
"""

import sys
import os

def main():
    """Launch the Fantasy RPG game"""
    print("=" * 50)
    print("🗡️  FANTASY RPG - Text Adventure Game  🛡️")
    print("=" * 50)
    print()
    print("Loading game...")
    print()
    
    try:
        # Import and run the game
        from fantasy_rpg.ui import run_ui
        run_ui()
        
    except ImportError as e:
        print("❌ Error: Could not import game modules!")
        print(f"Details: {e}")
        print()
        print("Make sure you have installed the required dependencies:")
        print("  pip install -r requirements.txt")
        print()
        print("Or install manually:")
        print("  pip install textual>=0.40.0 rich>=13.0.0")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing Fantasy RPG!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your installation and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()