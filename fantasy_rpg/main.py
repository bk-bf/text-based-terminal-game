#!/usr/bin/env python3
"""
Fantasy RPG - Main Entry Point

Entry point for the Fantasy RPG game. Initializes the game and starts the main loop.
"""

def main():
    """Main entry point for the Fantasy RPG game."""
    print("Fantasy RPG - Starting...")
    print("Initializing game systems...")
    
    # For now, just verify the entry point works
    # Future tasks will add character creation, UI, and game loop
    print("Game systems initialized successfully!")
    print("Entry point working - ready for next implementation phase")
    print("Use Ctrl+C to exit")
    
    try:
        # Simple input loop to keep the program running
        while True:
            user_input = input("\n> ").strip().lower()
            if user_input in ['quit', 'exit', 'q']:
                print("Thanks for playing Fantasy RPG!")
                break
            elif user_input == 'help':
                print("Available commands: help, quit")
            else:
                print(f"Unknown command: {user_input}")
                print("Type 'help' for available commands or 'quit' to exit")
    except KeyboardInterrupt:
        print("\nThanks for playing Fantasy RPG!")
    except Exception as e:
        print(f"Error: {e}")
        print("Game encountered an error. Please restart.")

if __name__ == "__main__":
    main()