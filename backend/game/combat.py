import random
from typing import Dict, List, Optional, Tuple


class CombatSystem:
    """Handles turn-based combat mechanics"""

    def __init__(self):
        self.enemies = {
            "goblin": {"hp": 15, "ac": 12, "damage": 4, "xp": 50},
            "skeleton": {"hp": 20, "ac": 13, "damage": 5, "xp": 75},
            "orc": {"hp": 30, "ac": 14, "damage": 6, "xp": 100},
            "dragon_whelp": {"hp": 50, "ac": 15, "damage": 8, "xp": 250},
        }

    def roll_die(self, sides: int) -> int:
        """Roll a die with specified sides"""
        return random.randint(1, sides)

    def roll_skill_check(self, stats: dict, skill: str) -> int:
        """Roll a d20 + modifier for a skill check"""
        stat_modifiers = {
            "str": (stats.get("str", 10) - 10) // 2,
            "dex": (stats.get("dex", 10) - 10) // 2,
            "con": (stats.get("con", 10) - 10) // 2,
            "int": (stats.get("int", 10) - 10) // 2,
            "wis": (stats.get("wis", 10) - 10) // 2,
            "cha": (stats.get("cha", 10) - 10) // 2,
        }

        # Default to relevant stat based on skill
        skill_stats = {
            "attack": "str",
            "stealth": "dex",
            "perception": "wis",
            "persuasion": "cha",
        }

        relevant_stat = skill_stats.get(skill, "str")
        modifier = stat_modifiers.get(relevant_stat, 0)

        return self.roll_die(20) + modifier

    async def start_combat(self, game_state: dict, enemy_type: str) -> dict:
        """Initialize combat with an enemy"""
        enemy = self.enemies.get(enemy_type, self.enemies["goblin"])

        return {
            "in_combat": True,
            "current_enemy": {
                "type": enemy_type,
                "hp": enemy["hp"],
                "max_hp": enemy["hp"],
                "ac": enemy["ac"],
                "damage": enemy["damage"],
            },
            "combat_log": [f"A wild {enemy_type} appears!"],
        }

    async def resolve_action(self, game_state: dict, player_action: str) -> dict:
        """Resolve a combat action"""
        character = game_state.get("character", {})
        enemy = game_state.get("world", {}).get("current_enemy", {})

        if not enemy:
            return {"narration": "There's nothing to fight!", "combat_ended": True}

        result = {
            "narration": "",
            "updates": {"character": {}, "world": {"combat_log": []}},
            "combat_ended": False,
        }

        action = player_action.lower()

        # Player turn
        if "attack" in action or "hit" in action or "strike" in action:
            attack_roll = self.roll_skill_check(character.get("stats", {}), "attack")
            ac = enemy.get("ac", 12)

            if attack_roll >= ac:
                # Hit!
                damage_die = 8  # Default d8
                if "sword" in str(character.get("equipment", [])).lower():
                    damage_die = 8
                elif "axe" in str(character.get("equipment", [])).lower():
                    damage_die = 10

                damage = self.roll_die(damage_die)
                str_mod = (character.get("stats", {}).get("str", 10) - 10) // 2
                damage += max(0, str_mod)

                enemy["hp"] -= damage
                result["narration"] = (
                    f"You attack and hit! (rolled {attack_roll} vs AC {ac}) "
                    f"Dealing {damage} damage. Enemy has {max(0, enemy['hp'])} HP left."
                )
            else:
                result["narration"] = (
                    f"You attack but miss! (rolled {attack_roll} vs AC {ac})"
                )

        elif "defend" in action or "block" in action:
            result["narration"] = "You brace yourself, ready to defend."
            result["updates"]["world"]["defending"] = True

        elif "flee" in action or "run" in action:
            flee_check = self.roll_skill_check(character.get("stats", {}), "stealth")
            if flee_check >= 15:
                result["narration"] = "You manage to escape!"
                result["combat_ended"] = True
                result["updates"]["world"]["in_combat"] = False
                result["updates"]["world"]["current_enemy"] = None
                return result
            else:
                result["narration"] = "You try to flee but fail!"

        else:
            result["narration"] = f"You attempt: {player_action}"

        # Enemy turn (if still in combat)
        if not result["combat_ended"] and enemy.get("hp", 0) > 0:
            enemy_attack = self.roll_die(20)
            player_ac = 15  # Simplified AC calculation

            if enemy_attack >= player_ac:
                enemy_damage = enemy.get("damage", 4)
                current_hp = character.get("hp", 10)
                new_hp = current_hp - enemy_damage

                result["narration"] += f"\nThe enemy attacks and hits you for {enemy_damage} damage! "
                result["narration"] += f"(You have {new_hp} HP left)"

                result["updates"]["character"]["hp"] = new_hp

                if new_hp <= 0:
                    result["narration"] += "\n\nYOU HAVE BEEN DEFEATED! Game Over."
                    result["combat_ended"] = True
            else:
                result["narration"] += f"\nThe enemy attacks but misses!"

        # Check if enemy defeated
        if enemy.get("hp", 0) <= 0 and not result["combat_ended"]:
            xp_reward = enemy.get("xp", 50)
            result["narration"] += f"\n\nYou defeated the {enemy.get('type', 'enemy')}! "
            result["narration"] += f"You gain {xp_reward} XP."

            result["updates"]["character"]["xp"] = character.get("xp", 0) + xp_reward
            result["updates"]["world"]["in_combat"] = False
            result["updates"]["world"]["current_enemy"] = None
            result["combat_ended"] = True

        result["updates"]["world"]["current_enemy"] = enemy if enemy.get("hp", 0) > 0 else None
        result["updates"]["world"]["combat_log"].append(result["narration"])

        return result
