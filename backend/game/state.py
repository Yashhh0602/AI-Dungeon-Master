import aiosqlite
import json
import uuid
from datetime import datetime
from typing import Any


class GameStateManager:
    """Manages persistent game state using SQLite"""

    def __init__(self, db_path: str = "game saves.db"):
        self.db_path = db_path
        self._init_db()

    async def _init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    character_data TEXT,
                    world_state TEXT,
                    story_log TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            await db.commit()

    async def create_game(
        self,
        character_name: str,
        character_class: str,
        background: str = ""
    ) -> str:
        """Create a new game session"""
        game_id = str(uuid.uuid4())

        # Initialize character with full RPG stats
        character_data = self._generate_character(character_name, character_class, background)

        # Initialize world state
        world_state = {
            "location": "Starting Area",
            "in_combat": False,
            "current_enemy": None,
            "quest_stage": 0,
            "flags": {}
        }

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO games
                   (id, character_data, world_state, story_log, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    game_id,
                    json.dumps(character_data),
                    json.dumps(world_state),
                    json.dumps([]),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                )
            )
            await db.commit()

        return game_id

    def _generate_character(self, name: str, char_class: str, background: str) -> dict:
        """Generate character stats based on class"""
        # Base stats
        base_stats = {
            "warrior": {"str": 16, "dex": 12, "con": 15, "int": 10, "wis": 11, "cha": 10},
            "rogue": {"str": 10, "dex": 16, "con": 12, "int": 13, "wis": 11, "cha": 12},
            "mage": {"str": 8, "dex": 12, "con": 12, "int": 16, "wis": 13, "cha": 11},
            "cleric": {"str": 12, "dex": 10, "con": 13, "int": 11, "wis": 16, "cha": 12}
        }

        stats = base_stats.get(char_class.lower(), base_stats["warrior"])

        # Calculate derived stats
        con_mod = (stats["con"] - 10) // 2
        max_hp = 10 + con_mod  # Level 1 HP

        return {
            "name": name,
            "class": char_class,
            "background": background,
            "level": 1,
            "xp": 0,
            "hp": max_hp,
            "max_hp": max_hp,
            "stats": stats,
            "inventory": ["Rations (5)", "Torch", "Flint & Steel"],
            "equipment": self._get_starting_equipment(char_class),
            "gold": 50,
            "skills": self._get_starting_skills(char_class)
        }

    def _get_starting_equipment(self, char_class: str) -> list:
        """Get starting equipment based on class"""
        equipment = {
            "warrior": ["Longsword", "Chain Mail", "Shield", "Backpack"],
            "rogue": ["Shortsword", "Dagger", "Leather Armor", "Thieves' Tools", "Backpack"],
            "mage": ["Quarterstaff", "Robes", "Spellbook", "Backpack"],
            "cleric": ["Mace", "Scale Mail", "Holy Symbol", "Backpack"]
        }
        return equipment.get(char_class.lower(), equipment["warrior"])

    def _get_starting_skills(self, char_class: str) -> list:
        """Get starting skills based on class"""
        skills = {
            "warrior": ["Slash", "Defend", "Second Wind"],
            "rogue": ["Backstab", "Hide", "Pick Lock"],
            "mage": ["Fireball", "Magic Missile", "Shield"],
            "cleric": ["Smite", "Heal", "Bless"]
        }
        return skills.get(char_class.lower(), skills["warrior"])

    async def get_game_state(self, game_id: str) -> dict:
        """Get full game state"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT character_data, world_state, story_log FROM games WHERE id = ?",
                (game_id,)
            )
            row = await cursor.fetchone()

        if not row:
            return {}

        character_data, world_state, story_log = row
        return {
            "character": json.loads(character_data),
            "world": json.loads(world_state),
            "story_log": json.loads(story_log)
        }

    async def update_game_state(self, game_id: str, updates: dict) -> dict:
        """Update specific parts of game state"""
        current = await self.get_game_state(game_id)

        if "character" in updates:
            current["character"].update(updates["character"])

        if "world" in updates:
            current["world"].update(updates["world"])

        if "story_log" in updates:
            current["story_log"].extend(updates["story_log"])

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE games
                   SET character_data = ?, world_state = ?, story_log = ?, updated_at = ?
                   WHERE id = ?""",
                (
                    json.dumps(current["character"]),
                    json.dumps(current["world"]),
                    json.dumps(current["story_log"]),
                    datetime.now().isoformat(),
                    game_id
                )
            )
            await db.commit()

        return current

    async def delete_game(self, game_id: str) -> bool:
        """Delete a game session"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM games WHERE id = ?",
                (game_id,)
            )
            await db.commit()
            return cursor.rowcount > 0
