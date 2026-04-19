from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

from game.state import GameStateManager
from game.dungeon_master import DungeonMaster
from game.combat import CombatSystem

app = FastAPI(title="AI Dungeon Master")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize game systems
state_manager = GameStateManager()
dungeon_master = DungeonMaster()
combat_system = CombatSystem()


class PlayerAction(BaseModel):
    game_id: str
    action: str


class NewGameRequest(BaseModel):
    character_name: str
    character_class: str
    background: Optional[str] = ""


class GameResponse(BaseModel):
    narration: str
    game_state: dict


@app.post("/game/new")
async def new_game(request: NewGameRequest) -> GameResponse:
    """Start a new game session"""
    game_id = await state_manager.create_game(
        character_name=request.character_name,
        character_class=request.character_class,
        background=request.background
    )

    # Get opening narration from AI
    narration = await dungeon_master.get_opening_narration(
        character_name=request.character_name,
        character_class=request.character_class,
        background=request.background
    )

    game_state = await state_manager.get_game_state(game_id)

    return GameResponse(narration=narration, game_state=game_state)


@app.post("/game/action")
async def player_action(request: PlayerAction) -> GameResponse:
    """Process a player action"""
    # Get current game state
    game_state = await state_manager.get_game_state(request.game_id)

    if not game_state:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if in combat
    if game_state.get("in_combat", False):
        combat_result = await combat_system.resolve_action(
            game_state=game_state,
            player_action=request.action
        )

        if combat_result.get("combat_ended", False):
            game_state = await state_manager.update_game_state(
                request.game_id,
                combat_result["updates"]
            )

        narration = combat_result.get("narration", "")
    else:
        # Normal action - get AI response
        narration = await dungeon_master.process_action(
            game_state=game_state,
            player_action=request.action
        )

        # Parse and update game state based on AI response
        updates = await dungeon_master.parse_state_updates(narration)
        if updates:
            game_state = await state_manager.update_game_state(
                request.game_id,
                updates
            )

    game_state = await state_manager.get_game_state(request.game_id)

    return GameResponse(narration=narration, game_state=game_state)


@app.get("/game/{game_id}")
async def get_game_state(game_id: str):
    """Get current game state"""
    game_state = await state_manager.get_game_state(game_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_state


@app.delete("/game/{game_id}")
async def delete_game(game_id: str):
    """Delete a game session"""
    success = await state_manager.delete_game(game_id)
    if not success:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"message": "Game deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
