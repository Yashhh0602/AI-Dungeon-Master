# AI Dungeon Master

A fantasy RPG adventure game powered by Claude AI. Explore a dynamic world, fight monsters, collect loot, and shape your own story with an AI Dungeon Master that responds to your choices.

![AI Dungeon Master](https://img.shields.io/badge/React-18-blue?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)

## Features

- **AI-Powered Dungeon Master**: Claude AI narrates your adventure, reacts to your choices, and creates dynamic storylines
- **Full RPG Character System**: Choose from 4 classes (Warrior, Rogue, Mage, Cleric), each with unique stats, skills, and equipment
- **Turn-Based Combat**: Strategic combat with dice rolls, skill checks, and enemy AI
- **Persistent Game State**: Your progress is saved automatically - continue your adventure anytime
- **Responsive Web UI**: Clean, dark-themed interface with real-time chat and character panel

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Anthropic SDK** - Claude AI integration
- **SQLite** - Persistent game state storage
- **AsyncIO** - Async operations for responsive API

### Frontend
- **React 18** with TypeScript
- **Axios** - API communication
- **CSS3** - Custom dark fantasy theme

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- An Anthropic API key ([get one here](https://console.anthropic.com))

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
copy .env.example .env  # Windows
# or
cp .env.example .env    # macOS/Linux

# Edit .env and add your ANTHROPIC_API_KEY

# Run the server
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will open on `http://localhost:3000`

## Gameplay

1. **Create Your Character**: Choose a name, class, and optional background
2. **Start Your Adventure**: The AI will generate an opening narration
3. **Type Actions**: Enter any action you want to take - the AI will respond
4. **Combat**: When enemies appear, use actions like "attack", "defend", or "flee"
5. **Explore**: Discover new locations, find items, and progress your story

### Example Actions
- "Look around the room"
- "Talk to the innkeeper"
- "Attack the goblin"
- "Search for traps"
- "Cast fireball at the orc"
- "Buy a potion from the merchant"

## Project Structure

```
ai-dungeon-master/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── game/
│   │   ├── state.py         # Game state management (SQLite)
│   │   ├── dungeon_master.py # AI DM integration
│   │   └── combat.py        # Combat system
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main game component
│   │   └── App.css          # Styling
│   └── package.json
└── README.md
```

## Classes

| Class | HP | Primary Stats | Starting Skills |
|-------|-----|---------------|-----------------|
| Warrior | 12 + CON | STR 16, CON 15 | Slash, Defend, Second Wind |
| Rogue | 8 + CON | DEX 16, INT 13 | Backstab, Hide, Pick Lock |
| Mage | 6 + CON | INT 16, WIS 13 | Fireball, Magic Missile, Shield |
| Cleric | 8 + CON | WIS 16, CON 13 | Smite, Heal, Bless |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/game/new` | Start a new game |
| POST | `/game/action` | Process player action |
| GET | `/game/{id}` | Get game state |
| DELETE | `/game/{id}` | Delete game session |

## Development

### Adding New Features

- **New Enemies**: Add to `backend/game/combat.py` in the `enemies` dict
- **New Skills**: Add to `backend/game/state.py` in `_get_starting_skills()`
- **New Classes**: Add stats to `_generate_character()` and equipment to `_get_starting_equipment()`

### Running Tests

```bash
# Backend tests (coming soon)
pytest backend/

# Frontend tests
cd frontend
npm test
```

## Troubleshooting

**Backend won't start:**
- Ensure your API key is set in `.env`
- Check that the virtual environment is activated
- Verify port 8000 isn't in use

**Frontend shows connection error:**
- Make sure the backend is running
- Check that CORS is configured correctly
- Verify the API_URL in `App.tsx`

**AI responses are slow:**
- This is normal - Claude takes a few seconds to generate responses
- Check your internet connection
- Verify your API key has available credits

## License

MIT License - feel free to use this for your portfolio or learning!

## Acknowledgments

- Built with [Claude](https://claude.ai) by Anthropic
- Inspired by classic tabletop RPGs and text adventure games
