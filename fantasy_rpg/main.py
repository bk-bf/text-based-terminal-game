#!/usr/bin/env python3
"""
Fantasy RPG - Main Entry Point

Demonstrates the character creation flow and basic game functionality.
"""

from fantasy_rpg.character_creation import CharacterCreationFlow, create_character_quick


def main():
    """Main game entry point"""
    print("Welcome to Fantasy RPG!")
    print("=" * 40)
    print()
    
    while True:
        print("What would you like to do?")
        print("1. Create character interactively")
        print("2. Quick character creation demo")
        print("3. Exit")
        print()
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            # Interactive character creation
            print("\nStarting interactive character creation...")
            flow = CharacterCreationFlow()
            character, race, char_class = flow.create_character_interactive()
            
            print(f"\nYour {character.race} {character.character_class} '{character.name}' is ready for adventure!")
            
            # Ask if they want to create another character
            again = input("\nWould you like to create another character? (y/n): ").strip().lower()
            if again not in ['y', 'yes']:
                break
                
        elif choice == "2":
            # Quick demo
            print("\nQuick Character Creation Demo:")
            print("Creating some example characters...")
            print()
            
            examples = [
                ("Aragorn", "Human", "Fighter"),
                ("Legolas", "Elf", "Rogue"),
                ("Gimli", "Dwarf", "Cleric"),
                ("Gandalf", "Human", "Wizard")
            ]
            
            for name, race, char_class in examples:
                print(f"--- {name} ---")
                character, race_obj, class_obj = create_character_quick(name, race, char_class)
                print()
            
            input("Press Enter to continue...")
            
        elif choice == "3":
            print("Thanks for playing Fantasy RPG!")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
        
        print()


if __name__ == "__main__":
    main()