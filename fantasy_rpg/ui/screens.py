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

try:
    from .panels import CharacterPanel, GameLogPanel, POIPanel
except ImportError:
    from panels import CharacterPanel, GameLogPanel, POIPanel


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
    """Interactive Caves of Qud-style inventory screen with tab navigation and shortkeys"""
    
    def __init__(self, character=None):
        super().__init__()
        # Don't store character reference - always get fresh from app
        self._initial_character = character
        self.selected_index = 0
        self.selected_category = "equipment"  # Start in equipment
        self.show_detail_panel = False
        self.equipment_items = []  # Equipment items
        self.inventory_items = []  # Inventory items
        self._build_item_lists()
    
    @property
    def character(self):
        """Always get fresh character reference from app"""
        return self.app.character if hasattr(self, 'app') else self._initial_character
    
    def on_mount(self) -> None:
        """Called when screen is mounted - hide detail panel initially"""
        try:
            detail_widget = self.query_one("#item-details")
            detail_widget.display = False
        except:
            pass
    
    def compose(self) -> ComposeResult:
        with Vertical(id="inventory-dialog"):
            yield Static("Inventory & Equipment", id="inventory-title", markup=False)
            yield Static("", id="inventory-spacer")
            
            with Horizontal(id="inventory-main-container"):
                # Left: Equipment column with selection highlighting
                with Vertical(id="equipment-column"):
                    yield Static(self._render_equipment(), id="equipment-display", markup=False)
                
                # Middle: Inventory column with selection highlighting
                with Vertical(id="inventory-column"):
                    yield Static(self._render_inventory(), id="inventory-display", markup=False)
                
                # Right: Item details panel (initially hidden, shown with E key)
                with Vertical(id="detail-column"):
                    yield Static("", id="item-details", markup=False)
            
            yield Static("", id="inventory-spacer2")
            yield Static(self._render_controls(), id="inventory-controls", markup=False)
    
    def _build_item_lists(self):
        """Build separate lists for equipment and inventory"""
        if not self.character:
            return
        
        self.equipment_items = []
        self.inventory_items = []
        
        # Build equipment items list
        slots = [
            ("main_hand", "Main Hand"),
            ("off_hand", "Off Hand"),
            ("body", "Body"),
            ("head", "Helmet"),
            ("feet", "Boots"),
            ("hands", "Gloves"),
            ("ring_1", "Ring 1"),
            ("ring_2", "Ring 2"),
            ("amulet", "Amulet")
        ]
        
        for slot_id, slot_name in slots:
            try:
                equipped_item = self.character.get_equipped_item(slot_id)
                if equipped_item:
                    item_data = {
                        "source": "equipped",
                        "slot": slot_id,
                        "slot_name": slot_name,
                        "item": equipped_item,
                        "name": equipped_item.name,
                        "type": getattr(equipped_item, 'item_type', 'unknown')
                    }
                    self.equipment_items.append(item_data)
            except:
                pass
        
        # Build inventory items list
        try:
            if hasattr(self.character, 'inventory') and self.character.inventory:
                for inv_item in self.character.inventory.items:
                    item_data = {
                        "source": "inventory",
                        "item": inv_item,
                        "name": inv_item.name,
                        "type": inv_item.item_type,
                        "quantity": inv_item.quantity
                    }
                    self.inventory_items.append(item_data)
        except Exception as e:
            pass
    
    def _render_equipment(self) -> str:
        """Render equipped items with selection highlighting"""
        if not self.character:
            return "equipment:\n\nNo character data available"
        
        equipment_text = "═══ EQUIPMENT ═══\n\n"
        
        slots = [
            ("main_hand", "Main Hand"),
            ("off_hand", "Off Hand"),
            ("body", "Body"),
            ("head", "Helmet"),
            ("feet", "Boots"),
            ("hands", "Gloves"),
            ("ring_1", "Ring 1"),
            ("ring_2", "Ring 2"),
            ("amulet", "Amulet")
        ]
        
        # Count only equipped items for indexing
        item_index = 0
        for slot_id, slot_name in slots:
            try:
                equipped_item = self.character.get_equipped_item(slot_id)
                if equipped_item:
                    is_selected = (self.selected_category == "equipment" and 
                                 item_index == self.selected_index)
                    
                    if is_selected:
                        equipment_text += f"▶ {slot_name}: {equipped_item.name} ◀\n"
                    else:
                        equipment_text += f"  {slot_name}: {equipped_item.name}\n"
                    item_index += 1
                else:
                    equipment_text += f"  {slot_name}: (empty)\n"
            except:
                equipment_text += f"  {slot_name}: (empty)\n"
        
        return equipment_text
    
    def _render_inventory(self) -> str:
        """Render inventory items with selection highlighting"""
        if not self.character:
            return "inventory:\n\nNo character data available"
        
        inventory_text = "═══ INVENTORY ═══\n\n"
        
        try:
            if hasattr(self.character, 'inventory') and self.character.inventory:
                items = self.character.inventory.items
                if items:
                    for idx, inventory_item in enumerate(items):
                        is_selected = (self.selected_category == "inventory" and 
                                     idx == self.selected_index)
                        
                        if inventory_item.quantity > 1:
                            item_line = f"{inventory_item.name} x{inventory_item.quantity}"
                        else:
                            item_line = f"{inventory_item.name}"
                        
                        if is_selected:
                            inventory_text += f"▶ {item_line} ◀\n"
                        else:
                            inventory_text += f"  {item_line}\n"
                else:
                    inventory_text += "No items in inventory\n"
                
                # Inventory stats - simplified with gold
                try:
                    total_weight = self.character.get_total_carrying_weight()
                    carrying_capacity = self.character.get_carrying_capacity()
                    encumbrance = self.character.get_encumbrance_level()
                    
                    # Get gold amount (assuming character has gold/currency)
                    gold = 0
                    if hasattr(self.character, 'gold'):
                        gold = self.character.gold
                    elif hasattr(self.character, 'currency'):
                        gold = self.character.currency.get('gold', 0)
                    
                    inventory_text += f"\n{total_weight:.0f}/{carrying_capacity:.0f} lbs ({encumbrance}), {gold} gp"
                except:
                    inventory_text += f"\n0/0 lbs (Light), 0 gp"
                
            else:
                inventory_text += "No items in inventory\n"
                
        except Exception as e:
            inventory_text += f"Error: {str(e)}\n"
        
        return inventory_text
    
    def _render_item_details(self) -> str:
        """Render detailed information about selected item (shown when 'e' is pressed)"""
        items_list = self.equipment_items if self.selected_category == "equipment" else self.inventory_items
        
        if not items_list or self.selected_index >= len(items_list):
            return "No item selected"
        
        item_data = items_list[self.selected_index]
        item = item_data["item"]
        
        details = []
        details.append("═══ DETAILS ═══\n")
        details.append(f"{item_data['name']}")
        details.append(f"Type: {item_data['type'].capitalize()}")
        
        if item_data["source"] == "equipped":
            details.append(f"Slot: {item_data['slot_name']}")
            details.append("Status: EQUIPPED")
        else:
            details.append(f"Qty: {item_data.get('quantity', 1)}")
        
        details.append("")
        
        # Item stats
        if hasattr(item, 'weight') and item.weight > 0:
            total_weight = item.weight * item_data.get("quantity", 1)
            details.append(f"Weight: {total_weight:.1f} lbs")
        
        if hasattr(item, 'value') and item.value > 0:
            total_value = item.value * item_data.get("quantity", 1)
            details.append(f"Value: {total_value} gp")
        
        # Combat stats
        if hasattr(item, 'damage_dice') and item.damage_dice:
            details.append(f"Damage: {item.damage_dice}")
            if hasattr(item, 'damage_type') and item.damage_type:
                details.append(f"  ({item.damage_type})")
        
        if hasattr(item, 'ac_bonus') and item.ac_bonus:
            details.append(f"AC: +{item.ac_bonus}")
        
        # Magical
        if hasattr(item, 'magical') and item.magical:
            details.append("\nMAGICAL")
            if hasattr(item, 'enchantment_bonus') and item.enchantment_bonus > 0:
                details.append(f"+{item.enchantment_bonus}")
        
        # Properties
        if hasattr(item, 'special_properties') and item.special_properties:
            details.append("\nProperties:")
            for prop in item.special_properties:
                details.append(f"• {prop}")
        
        # Description
        if hasattr(item, 'description') and item.description:
            details.append("\n" + self._wrap_text(item.description, 30))
        
        return "\n".join(details)
    
    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= width:
                line += word + " "
            else:
                if line:
                    lines.append(line.strip())
                line = word + " "
        if line:
            lines.append(line.strip())
        return "\n".join(lines)
    
    def _render_controls(self) -> str:
        """Render control instructions (simplified)"""
        return "TAB/←/→ Switch | ↑/↓ Navigate | E Examine | U Use/Equip | ESC Close"
    
    def _update_display(self):
        """Refresh the display after selection changes"""
        try:
            equip_widget = self.query_one("#equipment-display")
            equip_widget.update(self._render_equipment())
            
            inv_widget = self.query_one("#inventory-display")
            inv_widget.update(self._render_inventory())
            
            # Update detail panel - always exists now, just show/hide content
            detail_widget = self.query_one("#item-details")
            if self.show_detail_panel:
                detail_widget.update(self._render_item_details())
                detail_widget.display = True
            else:
                detail_widget.update("")
                detail_widget.display = False
            
            controls_widget = self.query_one("#inventory-controls")
            controls_widget.update(self._render_controls())
        except Exception as e:
            import traceback
            traceback.print_exc()  # Debug output
    
    def _get_selected_item(self):
        """Get currently selected item data"""
        items_list = self.equipment_items if self.selected_category == "equipment" else self.inventory_items
        if items_list and self.selected_index < len(items_list):
            return items_list[self.selected_index]
        return None
    
    def _use_selected_item(self):
        """Use, equip, or unequip the selected item"""
        item_data = self._get_selected_item()
        if not item_data:
            return
        
        item = item_data["item"]
        
        try:
            if item_data["source"] == "equipped":
                # Unequip the item
                slot = item_data["slot"]
                unequipped = self.character.unequip_item(slot)
                
                if unequipped:
                    # Ensure inventory exists before adding
                    if not hasattr(self.character, 'inventory') or self.character.inventory is None:
                        self.character.initialize_inventory()
                    
                    # Add the unequipped item back to inventory
                    # Need to convert Item to InventoryItem
                    # CRITICAL: Check 'is not None' because empty inventory (len=0) is falsy!
                    if hasattr(self.character, 'inventory') and self.character.inventory is not None:
                        from fantasy_rpg.core.inventory import InventoryItem
                        import uuid
                        
                        # Create InventoryItem from Item with unique ID for each instance
                        inv_item = InventoryItem(
                            item_id=f"{unequipped.name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}",
                            name=unequipped.name,
                            item_type=unequipped.item_type,
                            weight=unequipped.weight,
                            value=unequipped.value,
                            quantity=1,
                            description=unequipped.description,
                            properties=unequipped.properties.copy(),
                            equippable=unequipped.equippable,
                            slot=unequipped.slot,
                            ac_bonus=unequipped.ac_bonus,
                            armor_type=unequipped.armor_type,
                            damage_dice=unequipped.damage_dice,
                            damage_type=unequipped.damage_type,
                            magical=unequipped.magical,
                            enchantment_bonus=unequipped.enchantment_bonus,
                            special_properties=unequipped.special_properties.copy(),
                            capacity_bonus=unequipped.capacity_bonus
                        )
                        
                        added = self.character.inventory.add_item(inv_item)
                        
                        if added:
                            self.app.log_message(f"Unequipped {item_data['name']} (returned to inventory)")
                        else:
                            self.app.log_message(f"Unequipped {item_data['name']} (but couldn't add to inventory - weight limit?)")
                    else:
                        self.app.log_message(f"Unequipped {item_data['name']} (no inventory to return to)")
                    
                    self._build_item_lists()
                    self.selected_index = 0  # Reset selection
                    self.show_detail_panel = False  # Hide details
                    self._update_display()  # Update UI
                else:
                    self.app.log_message(f"Failed to unequip {item_data['name']}")
                
            elif item_data["type"] in ["weapon", "armor", "shield"]:
                # Convert InventoryItem to Item if needed
                if hasattr(item, 'to_item'):
                    # It's an InventoryItem, convert to Item
                    equipment_item = item.to_item()
                else:
                    # Already an Item
                    equipment_item = item
                
                # Equip the item - use character.equip_item() which initializes equipment
                slot = self._determine_equip_slot(equipment_item)
                if slot:
                    # Use character's equip_item method which handles equipment initialization
                    success = self.character.equip_item(equipment_item, slot)
                    if success:
                        self.app.log_message(f"Equipped {item_data['name']} to {slot}")
                        # Remove from inventory
                        # CRITICAL: Check 'is not None' because empty inventory (len=0) is falsy!
                        if hasattr(self.character, 'inventory') and self.character.inventory is not None:
                            self.character.inventory.remove_item(item.item_id, 1)
                        self._build_item_lists()
                        self.selected_category = "equipment"  # Switch to equipment view
                        self.selected_index = 0
                        self.show_detail_panel = False  # Hide details
                        self._update_display()  # Update UI
                    else:
                        self.app.log_message(f"Failed to equip {item_data['name']}")
                else:
                    self.app.log_message(f"Cannot determine slot for {item_data['name']}")
            
            elif item_data["type"] == "consumable":
                # Use/consume the item
                self.app.log_message(f"Used {item_data['name']} (consumable system TODO)")
                # TODO: Implement consumable effects
            
            else:
                self.app.log_message(f"Cannot use {item_data['name']}")
            
        except Exception as e:
            import traceback
            self.app.log_message(f"Error: {str(e)}")
            traceback.print_exc()  # Debug output
    
    def _determine_equip_slot(self, item) -> str:
        """Determine which slot to equip an item to"""
        item_type = getattr(item, 'item_type', '').lower()
        
        if item_type == "weapon":
            # Check if main_hand is free
            if not self.character.get_equipped_item('main_hand'):
                return 'main_hand'
            # Otherwise try off_hand (unless it's two-handed)
            if hasattr(item, 'special_properties'):
                if 'two-handed' not in item.special_properties:
                    if not self.character.get_equipped_item('off_hand'):
                        return 'off_hand'
            return 'main_hand'  # Replace main hand
        
        elif item_type == "armor":
            return 'body'  # Fixed: Equipment class uses 'body' not 'armor'
        
        elif item_type == "shield":
            return 'off_hand'
        
        elif hasattr(item, 'slot'):
            # Use the item's defined slot
            return item.slot
        
        return None
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses in inventory screen"""
        if event.key == "escape":
            self.dismiss()
        
        elif event.key == "tab" or event.key == "right":
            # Switch between equipment and inventory panels
            if self.selected_category == "equipment":
                if self.inventory_items:  # Only switch if inventory has items
                    self.selected_category = "inventory"
                    self.selected_index = 0
            else:
                if self.equipment_items:  # Only switch if equipment has items
                    self.selected_category = "equipment"
                    self.selected_index = 0
            self._update_display()
        
        elif event.key == "left":
            # Switch to equipment panel
            if self.selected_category == "inventory" and self.equipment_items:
                self.selected_category = "equipment"
                self.selected_index = 0
                self._update_display()
        
        elif event.key == "down":
            # Navigate down within current panel
            items_list = self.equipment_items if self.selected_category == "equipment" else self.inventory_items
            if items_list and len(items_list) > 0:
                self.selected_index = (self.selected_index + 1) % len(items_list)
                self._update_display()
        
        elif event.key == "up":
            # Navigate up within current panel
            items_list = self.equipment_items if self.selected_category == "equipment" else self.inventory_items
            if items_list and len(items_list) > 0:
                self.selected_index = (self.selected_index - 1) % len(items_list)
                self._update_display()
        
        elif event.key == "e":
            # Toggle item details panel on the right
            item_data = self._get_selected_item()
            if item_data:
                self.show_detail_panel = not self.show_detail_panel
                self._update_display()  # Update display instead of full refresh
        
        elif event.key == "u":
            # Use/equip/unequip selected item
            self._use_selected_item()


class LoadGameConfirmationScreen(ModalScreen):
    """Modal screen to confirm loading saved game"""
    
    def __init__(self):
        super().__init__()
        self.selected_option = 0  # 0 = No (default), 1 = Yes
        self.options = ["No", "Yes"]
        self.load_confirmed = False
    
    def compose(self) -> ComposeResult:
        with Vertical(id="load-dialog"):
            yield Static("Save file found! Load saved game?", id="load-message", markup=False)
            yield Static("", id="load-spacer")
            yield Static(self._render_options(), id="load-options", markup=False)
            yield Static("", id="load-spacer2")
            yield Static("Use TAB/Left/Right to select, ENTER to confirm, ESC to cancel", id="load-instruction", markup=False)
    
    def _render_options(self) -> str:
        """Render the checkbox options with current selection side by side"""
        no_option = ""
        yes_option = ""
        
        # Render No option
        if self.selected_option == 0:
            no_option = "> [X] No (New Game)"
        else:
            no_option = "  [ ] No (New Game)"
            
        # Render Yes option  
        if self.selected_option == 1:
            yes_option = "> [X] Yes (Load Save)"
        else:
            yes_option = "  [ ] Yes (Load Save)"
        
        # Side by side layout with spacing
        return f"{no_option}        {yes_option}"
    
    def _update_display(self):
        """Update the options display"""
        options_widget = self.query_one("#load-options")
        options_widget.update(self._render_options())
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses in the load dialog"""
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
                self.load_confirmed = True
            self.dismiss(self.load_confirmed)
        elif event.key == "escape":
            # Cancel (default to new game)
            self.dismiss(False)


class QuitConfirmationScreen(ModalScreen):
    """Modal screen to confirm quitting the game"""
    
    def __init__(self):
        super().__init__()
        self.selected_option = 0  # 0 = No (default), 1 = Yes
        self.options = ["No", "Yes"]
    
    def compose(self) -> ComposeResult:
        with Vertical(id="quit-dialog"):
            yield Static("Save game and quit?", id="quit-message", markup=False)
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
                # Save game before quitting
                if hasattr(self.app, 'game_engine') and self.app.game_engine:
                    success, message = self.app.game_engine.save_game("save")
                    if success:
                        # Show save confirmation briefly before quitting
                        self.app.log_message(f"✓ {message}")
                        self.app.log_message("Goodbye!")
                    else:
                        self.app.log_message(f"⚠ Save failed: {message}")
                        self.app.log_message("Quitting without saving...")
                else:
                    self.app.log_message("⚠ No game engine available - quitting without saving...")
                
                # Small delay to show the message, then quit
                self.app.set_timer(0.5, self.app.exit)
                self.dismiss()
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
            self.title_bar = Static("Fantasy RPG | Type 'help' for commands", id="title-bar", markup=False)
            yield self.title_bar
            
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
    
    def update_title_bar(self, player_state=None):
        """Update the title bar with current game state"""
        if player_state and hasattr(player_state, 'get_time_string'):
            time_desc = self._get_natural_time_description(player_state)
            title_text = f"Fantasy RPG - {time_desc} | Type 'help' for commands"
        else:
            title_text = "Fantasy RPG | Type 'help' for commands"
        
        if hasattr(self, 'title_bar'):
            self.title_bar.update(title_text)
    
    def _get_natural_time_description(self, player_state) -> str:
        """Get natural language time description for title bar"""
        # Get approximate time of day based on game hour
        hour = int(player_state.game_hour)  # Convert to int to avoid float precision issues
        day = player_state.game_day
        
        # Time of day descriptions
        if 5 <= hour < 7:
            time_desc = "Early dawn"
        elif 7 <= hour < 9:
            time_desc = "Morning"
        elif 9 <= hour < 12:
            time_desc = "Late morning"
        elif 12 <= hour < 14:
            time_desc = "Midday"
        elif 14 <= hour < 17:
            time_desc = "Afternoon"
        elif 17 <= hour < 19:
            time_desc = "Late afternoon"
        elif 19 <= hour < 21:
            time_desc = "Evening"
        elif 21 <= hour < 23:
            time_desc = "Late evening"
        elif 23 <= hour or hour < 2:
            time_desc = "Deep night"
        elif 2 <= hour < 5:
            time_desc = "Before dawn"
        else:
            time_desc = "Night"
        
        # Shorter day descriptions for title bar
        if day == 1:
            day_desc = "Day 1"
        elif day <= 7:
            day_desc = f"Day {day}"
        else:
            weeks = day // 7
            remaining_days = day % 7
            if weeks == 1 and remaining_days == 0:
                day_desc = "Week 1"
            elif weeks == 1:
                day_desc = f"Week 1, Day {remaining_days}"
            else:
                day_desc = f"Week {weeks}"
        
        return f"{time_desc}, {day_desc}"
    
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