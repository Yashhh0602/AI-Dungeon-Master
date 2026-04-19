# Getting Started

Follow these steps to run your AI Dungeon Master game:

## Step 1: Get Your API Key

1. Go to https://console.anthropic.com
2. Sign up or log in
3. Create an API key
4. Copy the key

## Step 2: Configure Backend

Open `backend\.env` and paste your API key:

```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

## Step 3: Start the Backend

Open a terminal in VS Code:

```bash
cd backend
venv\Scripts\activate
python main.py
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

## Step 4: Start the Frontend

Open another terminal in VS Code:

```bash
cd frontend
npm start
```

Your browser should open to `http://localhost:3000`

## Step 5: Play!

1. Enter your character name
2. Choose a class
3. Optionally add a background
4. Click "Begin Adventure"
5. Type actions like "look around", "attack", "explore the cave"

---

## Troubleshooting

**Frontend says "Failed to start game"**
- Make sure backend is running on port 8000
- Check your API key is correct in `.env`

**Backend won't start**
- Run `pip install -r requirements.txt` again
- Make sure virtual environment is activated

**Game feels slow**
- AI responses take 2-5 seconds - this is normal!
- Check your internet connection
