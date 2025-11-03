"""
Fantasy RPG - Conditions System

Manages status conditions, their effects, and interactions.
Handles environmental exposure mechanics like wetness, wind chill, temperature effects.
Includes shelter system integration.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# DEBUG TOGGLE - Set to True to enable location entry debugging
DEBUG_SHELTER = True


class ShelterType(Enum):
    """Types of shelter available"""
    NONE = "none"
    NATURAL_OVERHANG = "natural_overhang"
    CAVE_ENTRANCE = "cave_entrance"
    DENSE_TREES = "dense_trees"
    MAKESHIFT_LEAN_TO = "makeshift_lean_to"
    PROPER_CAMP = "proper_camp"
    STRUCTURE_INTERIOR = "structure_interior"


class ShelterQuality(Enum):
    """Quality levels of shelter"""
    EXPOSED = 0      # No protection
    MINIMAL = 1      # Slight protection from elements
    BASIC = 2        # Basic protection from rain/wind
    GOOD = 3         # Good protection from weather
    EXCELLENT = 4    # Excellent protection, comfortable rest


class ConditionSeverity(Enum):
    """Condition severity levels"""
    MILD = "mild"
    MODERATE = "moderate"
    CRITICAL = "critical"
    LIFE_THREATENING = "life_threatening"


@dataclass
class ConditionEffect:
    """Represents the effects of a single condition"""
    name: str
    description: str
    severity: ConditionSeverity
    category: str
    
    # Ability score modifiers
    strength_modifier: int = 0
    dexterity_modifier: int = 0
    constitution_modifier: int = 0
    intelligence_modifier: int = 0
    wisdom_modifier: int = 0
    charisma_modifier: int = 0
    all_ability_modifiers: int = 0
    
    # Skill penalties (dict of skill_name: penalty)
    skill_penalties: Dict[str, int] = field(default_factory=dict)
    
    # Saving throw penalties
    saving_throw_penalties: Dict[str, int] = field(default_factory=dict)
    
    # Combat effects
    attack_penalty: int = 0
    damage_penalty: int = 0
    armor_ac_penalty: int = 0
    
    # Movement effects
    movement_penalty: float = 0.0  # Fraction of movement lost (0.5 = half speed)
    
    # Special effects
    disadvantage_on: List[str] = field(default_factory=list)
    cold_vulnerability: bool = False
    fire_resistance: bool = False
    unconscious_risk: bool = False
    
    # Damage over time
    damage_over_time: Optional[Dict[str, Any]] = None
    
    # Fainting mechanics
    faint_chance: float = 0.0
    unconscious: bool = False
    helpless: bool = False


class ConditionsManager:
    """Manages all conditions and their effects"""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            # Try to find the data directory
            current_dir = Path(__file__).parent
            parent_data_dir = current_dir.parent / "data"
            
            if parent_data_dir.exists():
                self.data_dir = parent_data_dir
            else:
                self.data_dir = Path("fantasy_rpg/data")
        else:
            self.data_dir = Path(data_dir)
        
        self.conditions_data = {}
        self.severity_levels = {}
        self._load_conditions()
    
    def _load_conditions(self):
        """Load conditions from JSON file"""
        conditions_file = self.data_dir / "conditions.json"
        
        if not conditions_file.exists():
            print(f"Warning: {conditions_file} not found, using empty conditions")
            return
        
        try:
            with open(conditions_file, 'r') as f:
                data = json.load(f)
            
            # Load conditions from the "conditions" section
            if "conditions" in data:
                self.conditions_data = data["conditions"]
            
            # Load severity levels only
            # Hierarchies, exclusions, and interactions are handled per-condition
            self.severity_levels = data.get("severity_levels", {})
            
            print(f"Loaded {len(self.conditions_data)} conditions from {conditions_file}")
            
        except Exception as e:
            print(f"Error loading conditions: {e}")
    
    def evaluate_conditions(self, player_state) -> List[str]:
        """Evaluate which conditions apply to the current player state"""
        # First, get all potentially active conditions
        potentially_active = []
        
        for condition_name, condition_data in self.conditions_data.items():
            if self._check_condition_trigger(condition_data["trigger"], player_state):
                potentially_active.append(condition_name)
        
        # Apply hierarchies and exclusions
        active_conditions = self._apply_hierarchies_and_exclusions(potentially_active)
        
        return active_conditions
    
    def get_newly_triggered_conditions(self, previous_conditions: List[str], current_conditions: List[str]) -> List[dict]:
        """
        Compare previous and current condition lists to find newly triggered conditions.
        Returns a list of dicts with 'name' and 'message' for each newly triggered condition.
        """
        newly_triggered = []
        
        for condition_name in current_conditions:
            if condition_name not in previous_conditions:
                condition_data = self.conditions_data.get(condition_name, {})
                trigger_message = condition_data.get("trigger_message", "")
                
                if trigger_message:
                    newly_triggered.append({
                        "name": condition_name,
                        "message": trigger_message
                    })
        
        return newly_triggered
    
    def _apply_hierarchies_and_exclusions(self, potentially_active: List[str]) -> List[str]:
        """Apply condition hierarchies and exclusions to filter the final active conditions"""
        active_conditions = potentially_active.copy()
        
        # Group conditions by hierarchy
        hierarchies = {}
        exclusion_groups = {}
        
        for condition_name in potentially_active:
            condition_data = self.conditions_data.get(condition_name, {})
            
            # Group by hierarchy
            hierarchy = condition_data.get("hierarchy")
            if hierarchy:
                if hierarchy not in hierarchies:
                    hierarchies[hierarchy] = []
                hierarchies[hierarchy].append({
                    "name": condition_name,
                    "priority": condition_data.get("priority", 0)
                })
            
            # Group by exclusion group
            exclusion_group = condition_data.get("exclusion_group")
            if exclusion_group:
                if exclusion_group not in exclusion_groups:
                    exclusion_groups[exclusion_group] = []
                exclusion_groups[exclusion_group].append({
                    "name": condition_name,
                    "priority": condition_data.get("priority", 0)
                })
        
        # Apply hierarchy rules - keep only highest priority in each hierarchy
        for hierarchy_name, conditions in hierarchies.items():
            if len(conditions) > 1:
                # Sort by priority (highest first)
                conditions.sort(key=lambda x: x["priority"], reverse=True)
                highest_priority_condition = conditions[0]["name"]
                
                # Remove all other conditions from this hierarchy
                for condition_info in conditions[1:]:
                    if condition_info["name"] in active_conditions:
                        active_conditions.remove(condition_info["name"])
        
        # Apply exclusion rules - keep only highest priority in each exclusion group
        for exclusion_group_name, conditions in exclusion_groups.items():
            if len(conditions) > 1:
                # Sort by priority (highest first)
                conditions.sort(key=lambda x: x["priority"], reverse=True)
                highest_priority_condition = conditions[0]["name"]
                
                # Remove all other conditions from this exclusion group
                for condition_info in conditions[1:]:
                    if condition_info["name"] in active_conditions:
                        active_conditions.remove(condition_info["name"])
        
        return active_conditions
    
    def _check_condition_trigger(self, trigger: str, player_state) -> bool:
        """Check if a condition trigger is met"""
        try:
            # Handle special environmental triggers
            if trigger == "has_warmth_source_in_location":
                return self._check_warmth_source_in_location(player_state)
            elif trigger in ["provides_some_shelter", "provides_good_shelter", "provides_excellent_shelter"]:
                return self._check_shelter_flag_in_location(player_state, trigger)
            elif trigger == "manual":
                return False  # Manual conditions are applied explicitly
            
            # Create a safe evaluation context with the player state values
            context = {
                'hunger': player_state.survival.hunger,
                'thirst': player_state.survival.thirst,
                'fatigue': player_state.survival.fatigue,
                'body_temperature': player_state.survival.body_temperature,
                'wetness': player_state.survival.wetness,
                'wind_chill': player_state.survival.wind_chill,
                'has_warmth_source_in_location': self._check_warmth_source_in_location(player_state)
            }
            
            # Safely evaluate the condition trigger expression
            return self._safe_eval_trigger(trigger, context)
            
        except Exception as e:
            print(f"Error evaluating trigger '{trigger}': {e}")
            return False
    
    def _safe_eval_trigger(self, expression: str, context: dict) -> bool:
        """
        Safely evaluate a condition trigger expression without using eval().
        Only allows comparison and logical operators with whitelisted variables.
        
        Args:
            expression: The trigger expression (e.g., "hunger <= 200 and hunger > 50")
            context: Dictionary of allowed variable names and their values
            
        Returns:
            Boolean result of the expression evaluation
        """
        import ast
        import operator
        
        # Whitelist of allowed operators
        allowed_ops = {
            ast.Lt: operator.lt,      # <
            ast.LtE: operator.le,     # <=
            ast.Gt: operator.gt,      # >
            ast.GtE: operator.ge,     # >=
            ast.Eq: operator.eq,      # ==
            ast.NotEq: operator.ne,   # !=
            ast.And: lambda: None,    # and (handled specially)
            ast.Or: lambda: None,     # or (handled specially)
        }
        
        def eval_node(node):
            """Recursively evaluate AST nodes"""
            if isinstance(node, ast.Constant):
                # Allow numeric constants
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError(f"Unsupported constant type: {type(node.value)}")
            
            elif isinstance(node, ast.Name):
                # Only allow whitelisted variable names from context
                if node.id in context:
                    return context[node.id]
                raise ValueError(f"Variable '{node.id}' not in allowed context")
            
            elif isinstance(node, ast.Compare):
                # Handle comparison operations (e.g., a < b, a <= b <= c)
                left = eval_node(node.left)
                for op, comparator in zip(node.ops, node.comparators):
                    if type(op) not in allowed_ops:
                        raise ValueError(f"Unsupported operator: {type(op)}")
                    right = eval_node(comparator)
                    if not allowed_ops[type(op)](left, right):
                        return False
                    left = right  # For chained comparisons
                return True
            
            elif isinstance(node, ast.BoolOp):
                # Handle boolean operations (and, or)
                if type(node.op) not in allowed_ops:
                    raise ValueError(f"Unsupported boolean operator: {type(node.op)}")
                
                if isinstance(node.op, ast.And):
                    return all(eval_node(value) for value in node.values)
                elif isinstance(node.op, ast.Or):
                    return any(eval_node(value) for value in node.values)
            
            elif isinstance(node, ast.UnaryOp):
                # Handle unary operations (e.g., not)
                if isinstance(node.op, ast.Not):
                    return not eval_node(node.operand)
                raise ValueError(f"Unsupported unary operator: {type(node.op)}")
            
            raise ValueError(f"Unsupported AST node type: {type(node)}")
        
        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode='eval')
            # Evaluate the AST safely
            result = eval_node(tree.body)
            return bool(result)
        except (SyntaxError, ValueError) as e:
            print(f"Invalid trigger expression '{expression}': {e}")
            return False
    
    def _check_warmth_source_in_location(self, player_state) -> bool:
        """Check if there's an object with provides_warmth: true in the current location"""
        try:
            # Check if player_state has game_engine reference
            if hasattr(player_state, 'game_engine') and player_state.game_engine:
                game_engine = player_state.game_engine
            elif hasattr(player_state, 'character') and hasattr(player_state.character, 'game_engine'):
                game_engine = player_state.character.game_engine
            else:
                # Try to get game_engine from global context or other means
                return False
            
            # Check if player is in a location
            if not game_engine.game_state.world_position.current_location_id:
                return False
            
            # Get current location data
            location_data = game_engine.game_state.world_position.current_location_data
            if not location_data:
                return False
            
            # Get current area
            current_area_id = game_engine.game_state.world_position.current_area_id
            areas = location_data.get("areas", {})
            
            if current_area_id not in areas:
                return False
            
            area_data = areas[current_area_id]
            objects = area_data.get("objects", [])
            
            # Check if any object provides warmth
            for obj in objects:
                properties = obj.get("properties", {})
                if properties.get("provides_warmth", False):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking warmth source: {e}")
            return False
    
    def _check_shelter_flag_in_location(self, player_state, shelter_flag: str) -> bool:
        """Check if current location has the specified shelter flag (like warmth source checking)"""
        try:
            # Check if player_state has game_engine reference
            if hasattr(player_state, 'game_engine') and player_state.game_engine:
                game_engine = player_state.game_engine
            elif hasattr(player_state, 'character') and hasattr(player_state.character, 'game_engine'):
                game_engine = player_state.character.game_engine
            else:
                return False
            
            # Check if player is in a location
            if not game_engine.game_state.world_position.current_location_id:
                return False
            
            # Get current location data
            location_data = game_engine.game_state.world_position.current_location_data
            if not location_data:
                return False
            
            # Check if location has the shelter flag
            return location_data.get(shelter_flag, False)
            
        except Exception as e:
            print(f"Error checking shelter flag: {e}")
            return False
    
    def _check_shelter_in_location(self, player_state, required_quality: str) -> bool:
        """Check if current location provides shelter of the required quality
        
        Uses location flags (provides_some_shelter, provides_good_shelter, provides_excellent_shelter)
        as the single source of truth for shelter quality.
        """
        try:
            # Get game engine reference
            if hasattr(player_state, 'game_engine') and player_state.game_engine:
                game_engine = player_state.game_engine
            elif hasattr(player_state, 'character') and hasattr(player_state.character, 'game_engine'):
                game_engine = player_state.character.game_engine
            else:
                return False
            
            # Check if player is in a location
            if not game_engine.game_state.world_position.current_location_id:
                return False
            
            # Get current location data
            location_data = game_engine.game_state.world_position.current_location_data
            if not location_data:
                return False
            
            # Determine current shelter quality from location flags
            current_quality = "none"
            if location_data.get("provides_excellent_shelter", False):
                current_quality = "excellent"
            elif location_data.get("provides_good_shelter", False):
                current_quality = "good"
            elif location_data.get("provides_some_shelter", False):
                current_quality = "some"
            
            # Map quality levels for comparison
            quality_levels = {
                "none": 0,
                "some": 1,
                "good": 2,
                "excellent": 3
            }
            
            current_level = quality_levels.get(current_quality, 0)
            required_level = quality_levels.get(required_quality, 1)
            
            return current_level >= required_level
            
        except Exception as e:
            print(f"Error checking shelter: {e}")
            return False
    
    def get_condition_effects(self, condition_name: str) -> Optional[ConditionEffect]:
        """Get the effects of a specific condition"""
        if condition_name not in self.conditions_data:
            return None
        
        condition_data = self.conditions_data[condition_name]
        effects_data = condition_data.get("effects", {})
        
        # Create ConditionEffect object
        effect = ConditionEffect(
            name=condition_name,
            description=condition_data.get("description", ""),
            severity=ConditionSeverity(condition_data.get("severity", "mild")),
            category=condition_data.get("category", "unknown")
        )
        
        # Apply effects
        for effect_name, value in effects_data.items():
            if hasattr(effect, effect_name):
                setattr(effect, effect_name, value)
        
        return effect
    
    def calculate_total_effects(self, active_conditions: List[str]) -> Dict[str, Any]:
        """Calculate the total combined effects of all active conditions"""
        total_effects = {
            "ability_modifiers": {
                "strength": 0, "dexterity": 0, "constitution": 0,
                "intelligence": 0, "wisdom": 0, "charisma": 0
            },
            "skill_penalties": {},
            "saving_throw_penalties": {},
            "attack_penalty": 0,
            "armor_ac_penalty": 0,
            "movement_penalty": 0.0,
            "special_effects": {
                "disadvantage_on": [],
                "cold_vulnerability": False,
                "fire_resistance": False,
                "unconscious_risk": False
            }
        }
        
        # Apply each condition's effects
        for condition_name in active_conditions:
            effect = self.get_condition_effects(condition_name)
            if not effect:
                continue
            
            # Ability modifiers
            total_effects["ability_modifiers"]["strength"] += effect.strength_modifier + effect.all_ability_modifiers
            total_effects["ability_modifiers"]["dexterity"] += effect.dexterity_modifier + effect.all_ability_modifiers
            total_effects["ability_modifiers"]["constitution"] += effect.constitution_modifier + effect.all_ability_modifiers
            total_effects["ability_modifiers"]["intelligence"] += effect.intelligence_modifier + effect.all_ability_modifiers
            total_effects["ability_modifiers"]["wisdom"] += effect.wisdom_modifier + effect.all_ability_modifiers
            total_effects["ability_modifiers"]["charisma"] += effect.charisma_modifier + effect.all_ability_modifiers
            
            # Skill penalties
            for skill, penalty in effect.skill_penalties.items():
                if skill == "all":
                    # Apply to all skills (we'll handle this when calculating specific skills)
                    total_effects["skill_penalties"]["all"] = total_effects["skill_penalties"].get("all", 0) + penalty
                else:
                    total_effects["skill_penalties"][skill] = total_effects["skill_penalties"].get(skill, 0) + penalty
            
            # Saving throw penalties
            for save, penalty in effect.saving_throw_penalties.items():
                if save == "all":
                    total_effects["saving_throw_penalties"]["all"] = total_effects["saving_throw_penalties"].get("all", 0) + penalty
                else:
                    total_effects["saving_throw_penalties"][save] = total_effects["saving_throw_penalties"].get(save, 0) + penalty
            
            # Combat effects
            total_effects["attack_penalty"] += effect.attack_penalty
            total_effects["armor_ac_penalty"] += effect.armor_ac_penalty
            
            # Movement (cumulative penalties, but cap at 95% to allow minimal movement)
            total_effects["movement_penalty"] = min(0.95, total_effects["movement_penalty"] + effect.movement_penalty)
            
            # Special effects
            total_effects["special_effects"]["disadvantage_on"].extend(effect.disadvantage_on)
            if effect.cold_vulnerability:
                total_effects["special_effects"]["cold_vulnerability"] = True
            if effect.fire_resistance:
                total_effects["special_effects"]["fire_resistance"] = True
            if effect.unconscious_risk:
                total_effects["special_effects"]["unconscious_risk"] = True
        
        # Check for condition interactions
        self._apply_condition_interactions(active_conditions, total_effects)
        
        return total_effects
    
    def _apply_condition_interactions(self, active_conditions: List[str], total_effects: Dict[str, Any]):
        """Apply additional effects from condition interactions defined within each condition"""
        for condition_name in active_conditions:
            condition_data = self.conditions_data.get(condition_name, {})
            interactions = condition_data.get("interactions", {})
            
            for interaction_name, interaction_data in interactions.items():
                condition_check = interaction_data.get("condition_check", "")
                
                # Check if the interaction condition is met
                if self._check_interaction_condition(condition_check, active_conditions):
                    additional_effects = interaction_data.get("additional_effects", {})
                    
                    # Apply additional effects
                    for effect_name, value in additional_effects.items():
                        if effect_name.endswith("_modifier"):
                            ability = effect_name.replace("_modifier", "")
                            if ability in total_effects["ability_modifiers"]:
                                total_effects["ability_modifiers"][ability] += value
                        elif effect_name == "movement_penalty":
                            total_effects["movement_penalty"] += value
                        elif effect_name == "unconscious_risk":
                            total_effects["special_effects"]["unconscious_risk"] = True
    
    def _check_interaction_condition(self, condition_check: str, active_conditions: List[str]) -> bool:
        """Check if an interaction condition is met"""
        if not condition_check:
            return False
        
        try:
            # Parse different types of condition checks
            if condition_check.startswith("has_condition:"):
                required_condition = condition_check.replace("has_condition:", "")
                return required_condition in active_conditions
            
            elif condition_check.startswith("has_condition_category:"):
                parts = condition_check.split(" AND ")
                category_check = parts[0].replace("has_condition_category:", "")
                
                # Check if any active condition has the specified category
                for condition_name in active_conditions:
                    condition_data = self.conditions_data.get(condition_name, {})
                    if condition_data.get("category") == category_check:
                        # If there's a severity requirement, check it too
                        if len(parts) > 1 and "condition_severity_at_least:" in parts[1]:
                            severity_req = parts[1].replace("condition_severity_at_least:", "")
                            condition_severity = condition_data.get("severity", "mild")
                            severity_levels = {"mild": 1, "moderate": 2, "critical": 3, "life_threatening": 4}
                            if severity_levels.get(condition_severity, 1) >= severity_levels.get(severity_req, 1):
                                return True
                        else:
                            return True
                return False
            
            else:
                # Fallback - assume it's a direct condition name
                return condition_check in active_conditions
                
        except Exception as e:
            print(f"Error checking interaction condition '{condition_check}': {e}")
            return False
    
    def get_condition_severity_color(self, condition_name: str) -> str:
        """Get the color for a condition based on its severity"""
        if condition_name not in self.conditions_data:
            return "#FFFFFF"
        
        severity = self.conditions_data[condition_name].get("severity", "mild")
        return self.severity_levels.get(severity, {}).get("color", "#FFFFFF")
    
    def format_condition_for_display(self, condition_name: str) -> str:
        """Format a condition name for display with color"""
        color = self.get_condition_severity_color(condition_name)
        return f"[{color}]{condition_name}[/]"


    def check_for_fainting(self, player_state) -> bool:
        """Check if the character should faint based on active conditions"""
        import random
        
        active_conditions = self.evaluate_conditions(player_state)
        
        # Don't faint if already fainted
        if "Fainted" in active_conditions:
            return False
        
        # Calculate total faint chance from all conditions
        total_faint_chance = 0.0
        
        for condition_name in active_conditions:
            condition_data = self.conditions_data.get(condition_name, {})
            effects = condition_data.get("effects", {})
            faint_chance = effects.get("faint_chance", 0.0)
            
            # Accumulate faint chances (but cap at 80% max)
            total_faint_chance = min(0.8, total_faint_chance + faint_chance)
        
        # Roll for fainting
        if total_faint_chance > 0:
            roll = random.random()
            if roll < total_faint_chance:
                return True
        
        return False
    
    def apply_fainting(self, player_state):
        """Apply the Fainted condition to the character"""
        import random
        
        # Random duration between 30-180 minutes
        duration_minutes = random.randint(30, 180)
        
        return {
            "condition": "Fainted",
            "duration_minutes": duration_minutes,
            "message": f"You collapse from exhaustion and remain unconscious for {duration_minutes} minutes!",
            "effects": {
                "fatigue_recovery": 100,
                "forced_rest": True,
                "vulnerable_to_conditions": True
            }
        }


# Global conditions manager instance
conditions_manager = ConditionsManager()


def get_conditions_manager() -> ConditionsManager:
    """Get the global conditions manager instance"""
    return conditions_manager
