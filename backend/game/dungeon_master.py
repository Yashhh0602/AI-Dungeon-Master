import os
import re
import json
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()


class DungeonMaster:
    """AI Dungeon Master using Claude API"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def _get_system_prompt(self) -> str:
        """Return the core DM system prompt"""
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
2. If game state changes, end with a STATE block like:
   <STATE>{"hp": -5, "gold": 10}</STATE>
   for simple numeric changes, or describe complex changes in text

Remember: You're here to create a FUN, ENGAGING adventure. Be fair but don't shy away from consequences."""

    async def get_opening_narration(
        self,
        character_name: str,
        character_class: str,
        background: str
    ) -> str:
        """Generate the game's opening narration"""
        prompt = f"""The player is starting a new game.

CHARACTER:
- Name: {character_name}
- Class: {character_class}
- Background: {background if background else "A mysterious past"}

Create an atmospheric opening that:
1. Sets the scene - where are they and what's happening
2. Hints at adventure and danger
3. Ends with presenting the first choice or situation to react to

Make it compelling and invite the player into the world."""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=self._get_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    async def process_action(self, game_state: dict, player_action: str) -> str:
        """Process a player's action and return narration"""
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

Respond to what the player wants to do. Consider:
- Is this action risky? Call for a skill check
- Does this lead to combat? Set up the encounter
- Is this social? Create interesting NPC interaction
- Is this exploration? Describe what they find

Remember to end with <STATE> blocks for any mechanical changes."""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=600,
            system=self._get_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    async def parse_state_updates(self, narration: str) -> dict:
        """Parse STATE blocks from AI narration into game updates"""
        state_match = re.search(r'<STATE>\s*(\{[^}]+\})\s*</STATE>', narration)

        if not state_match:
            return {}

        try:
            state_changes = json.loads(state_match.group(1))
            updates = {"character": {}, "world": {}}

            # Map simple numeric changes to character stats
            simple_stats = ["hp", "gold", "xp", "level"]
            for key, value in state_changes.items():
                if key in simple_stats:
                    updates["character"][key] = value

            return updates if (updates["character"] or updates["world"]) else {}

        except json.JSONDecodeError:
            return {}
