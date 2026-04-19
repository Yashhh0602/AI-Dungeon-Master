import os
import re
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

class DungeonMaster:
    """AI Dungeon Master using Ollama (local)"""

    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model = "llama3.2"

    def _get_system_prompt(self) -> str:
        return """You are an expert Dungeon Master running a fantasy RPG adventure.

STYLE GUIDELINES:
- Write in second person ("You see...", "You feel...")
- Be descriptive but concise (2-4 paragraphs max)
- Create atmosphere and tension
- Present meaningful choices
- Never decide player actions - only describe outcomes

WORLD SETTING:
- Classic high fantasy with magic, monsters, and adventure
- The world is dangerous but rewarding
- NPCs have their own motivations
- Actions have consequences

MECHANICS:
- When the player attempts something risky, call for a skill check
- Combat is turn-based - describe the situation and ask what they do
- Track consequences logically (getting hurt reduces HP, etc.)

FORMAT YOUR RESPONSE:
1. First, narrate what happens in the story
2. If game state changes, end with a STATE block at the very end like:
   <STATE>{"hp": -5, "gold": 10}</STATE>

CRITICAL STATE RULES:
- Always use valid JSON with double quotes around keys and string values
- hp changes must be NEGATIVE for damage (e.g. -3 means lost 3 HP)
- hp changes must be POSITIVE for healing (e.g. 5 means gained 5 HP)
- gold changes are also deltas (e.g. -10 means spent 10 gold, 20 means earned 20 gold)
- Never use backticks, single quotes, or any other formatting inside the STATE block
- If no state changes occurred, do not include a STATE block at all

Remember: You're here to create a FUN, ENGAGING adventure."""

    async def _call_ollama(self, system: str, user_prompt: str) -> str:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )
            data = response.json()
            return data["message"]["content"]

    async def get_opening_narration(self, character_name: str, character_class: str, background: str) -> str:
        prompt = f"""The player is starting a new game.

CHARACTER:
- Name: {character_name}
- Class: {character_class}
- Background: {background if background else "A mysterious past"}

Create an atmospheric opening that:
1. Sets the scene - where are they and what's happening
2. Hints at adventure and danger
3. Ends with presenting the first choice or situation to react to"""

        return await self._call_ollama(self._get_system_prompt(), prompt)

    async def process_action(self, game_state: dict, player_action: str) -> str:
        character = game_state.get("character", {})
        world = game_state.get("world", {})

        prompt = f"""CURRENT SITUATION:
Location: {world.get('location', 'Unknown')}
Character: {character.get('name', 'Unknown')} ({character.get('class', 'Warrior')})
HP: {character.get('hp', 10)}/{character.get('max_hp', 10)}
Inventory: {', '.join(character.get('inventory', []))}
Equipment: {', '.join(character.get('equipment', []))}
Gold: {character.get('gold', 0)}

PLAYER ACTION: {player_action}

Respond to what the player wants to do. If any stats change, end with a <STATE> block using delta values (negative for loss, positive for gain)."""

        return await self._call_ollama(self._get_system_prompt(), prompt)

    async def parse_state_updates(self, narration: str) -> dict:
        # Clean up common Ollama formatting issues
        cleaned = narration.replace('`', '').replace("'", '"')

        # Match <STATE>{...}</STATE> or STATE{...} variants
        state_match = re.search(r'<?\bSTATE\b>?\s*(\{.*?\})\s*<?\/?STATE>?', cleaned, re.DOTALL)

        if not state_match:
            return {}

        try:
            state_changes = json.loads(state_match.group(1))
            updates = {"character": {}, "world": {}}

            for key, value in state_changes.items():
                if key in ["hp", "gold", "xp", "level"]:
                    updates["character"][key] = value
                elif key in ["location", "in_combat"]:
                    updates["world"][key] = value

            return updates if (updates["character"] or updates["world"]) else {}

        except json.JSONDecodeError:
            return {}