"""
Fantasy RPG - UI Screens

Modal screens and main game screen components.
"""

try:
    from textual.app import ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Static, Input
    from textual.screen import Screen, ModalScreen
    from textual import events
except ImportError:
    import sys
    print("Error: Textual library not found!")
    exit(1)

from .panels import CharacterPanel, GameLogPanel, POIPanel


class CharacterScreen(ModalScreen):
    """Modal screen to display full character stats and information"""
    
    def __init__(self, character=None):
        super().__init__()
        self.character = character
    
    def compose(self) -> ComposeResult:
        with Vertical(id="character-dialog"):
            yield Static("Character Sheet", id="character-title", markup=False)
            yield Static("", id="character-spacer")
            
            with Horizontal():
                # Left column - Basic info and abilities
                with Vertical(id="character-left-column"):
                    yield Static(self._render_basic_info(), id="character-basic", markup=False)
                
                # Right column - Combat stats and progression
                with Vertical(id="character-right-column"):
                    yield Static(self._render_combat_stats(), id="character-combat", markup=False)
            
            yield Static("", id="character-spacer2")
            yield Static(self._render_skills_and_features(), id="character-features", markup=False)
            yield Static("", id="character-spacer3")
            yield Static("Press ESC to close", id="character-instruction", markup=False)
    
    def _render_basic_info(self) -> str:
        """Render basic character information and ability scores"""
        if not self.character:
            return "basic information:\n\nNo character data available"
        
        char = self.character
        
        # Basic character info
        basic_text = f"""basic information:

Name: {char.name}
Race: {char.race}
Class: {char.character_class}
Level: {char.level}
Background: {getattr(char, 'background', 'Unknown')}

ability scores:
"""
        
        # Ability scores with modifiers
        abilities = [
            ('Strength', 'strength'),
            ('Dexterity', 'dexterity'), 
            ('Constitution', 'constitution'),
            ('Intelligence', 'intelligence'),
            ('Wisdom', 'wisdom'),
            ('Charisma', 'charisma')
        ]
        
        for ability_name, ability_attr in abilities:
            score = getattr(char, ability_attr, 10)
            modifier = char.ability_modifier(ability_attr)
            basic_text += f"{ability_name:12}: {score:2d} ({modifier:+d})\n"
        
        return basic_text
    
    def _render_combat_stats(self) -> str:
        """Render combat statistics and defenses"""
        if not self.character:
            return "combat statistics:\n\nNo character data available"
        
        char = self.character
        
        combat_text = f"""combat statistics:

Hit Points: {char.hp}/{char.max_hp}
Armor Class: {char.armor_class}
Proficiency Bonus: +{getattr(char, 'proficiency_bonus', 2)}

saving throws:
"""
        
        # Saving throws
        saving_throws = [
            ('Strength', 'strength'),
            ('Dexterity', 'dexterity'),
            ('Constitution', 'constitution'), 
            ('Intelligence', 'intelligence'),
            ('Wisdom', 'wisdom'),
            ('Charisma', 'charisma')
        ]
        
        for save_name, save_attr in saving_throws:
            try:
                modifier = char.calculate_saving_throw_modifier(save_attr)
                combat_text += f"{save_name:12}: {modifier:+d}\n"
            except:
                modifier = char.ability_modifier(save_attr)
                combat_text += f"{save_name:12}: {modifier:+d}\n"
        
        # Experience and progression
        try:
            xp_info = char.get_xp_progress_info()
            combat_text += f"\nexperience & progression:\n"
            combat_text += f"Current XP: {xp_info['current_xp']}\n"
            if not xp_info['max_level_reached']:
                combat_text += f"Next Level: {xp_info['xp_to_next_level']} XP needed\n"
                combat_text += f"Progress: {xp_info['progress_percentage']:.1f}%\n"
            else:
                combat_text += f"Maximum level reached!\n"
        except:
            combat_text += f"\nexperience & progression:\n"
            combat_text += f"Current XP: {getattr(char, 'experience_points', 0)}\n"
        
        return combat_text
    
    def _render_skills_and_features(self) -> str:
        """Render skills, proficiencies, and special features"""
        if not self.character:
            return "skills & features:\n\nNo character data available"
        
        char = self.character
        features_text = "skills & features:\n\n"
        
        # Skills (if skill system is available)
        try:
            if hasattr(char, 'skill_proficiencies') and char.skill_proficiencies:
                features_text += "skill proficiencies:\n"
                # This would need the actual skill system implementation
                features_text += "  (Skill system integration needed)\n"
            else:
                features_text += "skill proficiencies:\n"
                features_text += "  None currently defined\n"
        except:
            features_text += "skill proficiencies:\n"
            features_text += "  None currently defined\n"
        
        # Feats
        try:
            feats = char.get_feats()
            if feats:
                features_text += f"\nfeats:\n"
                for feat in feats:
                    features_text += f"  • {feat}\n"
            else:
                features_text += f"\nfeats:\n"
                features_text += f"  None acquired\n"
        except:
            features_text += f"\nfeats:\n"
            features_text += f"  None acquired\n"
        
        # Equipment summary
        try:
            equipment_weight = char.get_total_equipment_weight()
            equipment_value = char.get_total_equipment_value()
            features_text += f"\nequipment summary:\n"
            features_text += f"  Total Weight: {equipment_weight:.1f} lbs\n"
            features_text += f"  Total Value: {equipment_value} gp\n"
        except:
            features_text += f"\nequipment summary:\n"
            features_text += f"  No equipment data available\n"
        
        # Encumbrance
        try:
            encumbrance = char.get_encumbrance_level()
            carrying_capacity = char.get_carrying_capacity()
            total_weight = char.get_total_carrying_weight()
            features_text += f"\nencumbrance:\n"
            features_text += f"  Carrying: {total_weight:.1f}/{carrying_capacity:.1f} lbs\n"
            features_text += f"  Status: {encumbrance}\n"
            
            # Show penalties if any
            penalties = char.get_encumbrance_penalties()
            if penalties['movement_speed_modifier'] < 1.0 or penalties['disadvantage_on_ability_checks']:
                features_text += f"  Penalties: {penalties['description']}\n"
        except:
            features_text += f"\nencumbrance:\n"
            features_text += f"  Status: Light\n"
        
        return features_text
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses in character screen"""
        if event.key == "escape":
            self.dismiss()


class InventoryScreen(ModalScreen):
    """Modal screen to display character inventory and equipment"""
    
    def __init__(self, character=None):
        super().__init__()
        self.character = character
    
    def compose(self) -> ComposeResult:
        with Vertical(id="inventory-dialog"):
            yield Static("Inventory & Equipment", id="inventory-title", markup=False)
            yield Static("", id="inventory-spacer")
            
            with Horizontal():
                # Equipment column (left)
                with Vertical(id="equipment-column"):
                    yield Static(self._render_equipment(), id="equipment-display", markup=False)
                
                # Inventory column (right)  
                with Vertical(id="inventory-column"):
                    yield Static(self._render_inventory(), id="inventory-display", markup=False)
            
            yield Static("", id="inventory-spacer2")
            yield Static("Press ESC to close", id="inventory-instruction", markup=False)
    
    def _render_equipment(self) -> str:
        """Render equipped items"""
        if not self.character:
            return "equipment:\n\nNo character data available"
        
        equipment_text = "equipment:\n\n"
        
        # Equipment slots
        slots = [
            ("main_hand", "Main Hand"),
            ("off_hand", "Off Hand"),
            ("armor", "Armor"),
            ("helmet", "Helmet"),
            ("boots", "Boots"),
            ("gloves", "Gloves"),
            ("ring1", "Ring 1"),
            ("ring2", "Ring 2"),
            ("amulet", "Amulet")
        ]
        
        for slot_id, slot_name in slots:
            try:
                equipped_item = self.character.get_equipped_item(slot_id)
                if equipped_item:
                    equipment_text += f"{slot_name}: {equipped_item.name}\n"
                else:
                    equipment_text += f"{slot_name}: (empty)\n"
            except:
                equipment_text += f"{slot_name}: (empty)\n"
        
        # Equipment stats
        try:
            total_weight = self.character.get_total_equipment_weight()
            total_value = self.character.get_total_equipment_value()
            equipment_text += f"\nEquipment Weight: {total_weight:.1f} lbs"
            equipment_text += f"\nEquipment Value: {total_value} gp"
        except:
            equipment_text += f"\nEquipment Weight: 0.0 lbs"
            equipment_text += f"\nEquipment Value: 0 gp"
        
        return equipment_text
    
    def _render_inventory(self) -> str:
        """Render inventory items"""
        if not self.character:
            return "inventory:\n\nNo character data available"
        
        inventory_text = "inventory:\n\n"
        
        try:
            if hasattr(self.character, 'inventory') and self.character.inventory:
                # Use new inventory system
                items = self.character.inventory.items
                if items:
                    for item_id, inventory_item in items.items():
                        inventory_text += f"{inventory_item.name} x{inventory_item.quantity}\n"
                        if inventory_item.weight > 0:
                            total_weight = inventory_item.weight * inventory_item.quantity
                            inventory_text += f"  Weight: {total_weight:.1f} lbs\n"
                        inventory_text += "\n"
                else:
                    inventory_text += "No items in inventory\n"
                
                # Inventory stats
                total_weight = self.character.get_inventory_weight()
                carrying_capacity = self.character.get_carrying_capacity()
                encumbrance = self.character.get_encumbrance_level()
                
                inventory_text += f"\nInventory Weight: {total_weight:.1f} lbs"
                inventory_text += f"\nCarrying Capacity: {carrying_capacity:.1f} lbs"
                inventory_text += f"\nEncumbrance: {encumbrance}"
                
            elif hasattr(self.character, '_legacy_inventory') and self.character._legacy_inventory:
                # Use legacy inventory system
                for item in self.character._legacy_inventory:
                    name = item.get('name', 'Unknown Item')
                    quantity = item.get('quantity', 1)
                    weight = item.get('weight', 0)
                    
                    inventory_text += f"{name} x{quantity}\n"
                    if weight > 0:
                        total_weight = weight * quantity
                        inventory_text += f"  Weight: {total_weight:.1f} lbs\n"
                    inventory_text += "\n"
            else:
                inventory_text += "No items in inventory\n"
                
        except Exception as e:
            inventory_text += f"Error loading inventory: {str(e)}\n"
        
        return inventory_text
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses in inventory screen"""
        if event.key == "escape":
            self.dismiss()


class QuitConfirmationScreen(ModalScreen):
    """Modal screen to confirm quitting the game"""
    
    def __init__(self):
        super().__init__()
        self.selected_option = 0  # 0 = No (default), 1 = Yes
        self.options = ["No", "Yes"]
    
    def compose(self) -> ComposeResult:
        with Vertical(id="quit-dialog"):
            yield Static("Are you sure you want to quit?", id="quit-message", markup=False)
            yield Static("", id="quit-spacer")
            yield Static(self._render_options(), id="quit-options", markup=False)
            yield Static("", id="quit-spacer2")
            yield Static("Use TAB/Left/Right to select, ENTER to confirm, ESC to cancel", id="quit-instruction", markup=False)
    
    def _render_options(self) -> str:
        """Render the checkbox options with current selection side by side"""
        no_option = ""
        yes_option = ""
        
        # Render No option
        if self.selected_option == 0:
            no_option = "> [X] No"
        else:
            no_option = "  [ ] No"
            
        # Render Yes option  
        if self.selected_option == 1:
            yes_option = "> [X] Yes"
        else:
            yes_option = "  [ ] Yes"
        
        # Side by side layout with spacing
        return f"{no_option}        {yes_option}"
    
    def _update_display(self):
        """Update the options display"""
        options_widget = self.query_one("#quit-options")
        options_widget.update(self._render_options())
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses in the quit dialog"""
        if event.key == "tab" or event.key == "right" or event.key == "down":
            # Move to next option
            self.selected_option = (self.selected_option + 1) % len(self.options)
            self._update_display()
        elif event.key == "shift+tab" or event.key == "left" or event.key == "up":
            # Move to previous option
            self.selected_option = (self.selected_option - 1) % len(self.options)
            self._update_display()
        elif event.key == "enter":
            # Confirm selection
            if self.options[self.selected_option] == "Yes":
                self.app.exit()
            else:
                self.dismiss()
        elif event.key == "escape":
            # Cancel (always go back)
            self.dismiss()


class MainGameScreen(Screen):
    """Main game screen with three-panel layout"""
    
    def __init__(self):
        super().__init__()
        self.character_panel = CharacterPanel()
        self.game_log_panel = GameLogPanel()
        self.poi_panel = POIPanel()
        self.command_input = Input(placeholder="> Enter command (help for list)", id="command-input")
    
    def compose(self) -> ComposeResult:
        """Create the three-panel layout"""
        with Vertical():
            # Title bar
            yield Static("Fantasy RPG - Turn 1847, Day 5 | Type 'help' for commands", id="title-bar", markup=False)
            
            # Main three-panel layout
            with Horizontal():
                yield self.character_panel
                yield self.game_log_panel
                yield self.poi_panel
            
            # Command input area
            yield self.command_input
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses"""
        if event.key == "escape":
            self.app.push_screen(QuitConfirmationScreen())
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input submission"""
        command = event.value.strip().lower()
        self.command_input.value = ""  # Clear input
        
        if not command:
            return
        
        # Delegate command processing to the app
        self.app.process_command(command)
    
    def show_help(self):
        """Show available commands"""
        self.app.log_command("help")
        self.app.log_message("Available commands:")
        self.app.log_message("")
        self.app.log_message("Movement:")
        self.app.log_message("  n, north - Move north")
        self.app.log_message("  s, south - Move south")
        self.app.log_message("  e, east - Move east")
        self.app.log_message("  w, west - Move west")
        self.app.log_message("")
        self.app.log_message("Actions:")
        self.app.log_message("  look, l - Examine current location")
        self.app.log_message("  rest, r - Rest and recover health")
        self.app.log_message("  inventory, i - View inventory and equipment")
        self.app.log_message("  map, m - View map and nearby locations")
        self.app.log_message("")
        self.app.log_message("System:")
        self.app.log_message("  heal - Heal 10 HP (debug)")
        self.app.log_message("  xp - Gain 100 XP (debug)")
        self.app.log_message("  save - Save game log")
        self.app.log_message("  clear - Clear game log")
        self.app.log_message("  quit, exit - Quit game")
        self.app.log_message("")