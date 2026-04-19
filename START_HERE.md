# Getting Started

Follow these steps to run your AI Dungeon Master game:

## Step 1: Install Ollama

1. Go to https://ollama.ai
2. Download and install Ollama
3. Open a terminal and pull the model:
   ```bash
   ollama pull llama3.2
   ```
4. Keep Ollama running in the background

## Step 2: Start the Backend

Open a terminal in VS Code:

```bash
cd backend
venv\Scripts\activate
python main.py
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

## Step 3: Start the Frontend

Open another terminal in VS Code:

```bash
cd frontend
npm start
```

Your browser should open to `http://localhost:3000`

## Step 4: Play!

1. Enter your character name
2. Choose a class
3. Optionally add a background
4. Click "Begin Adventure"
5. Type actions like "look around", "attack", "explore the cave"

---

## Troubleshooting

**Frontend says "Failed to start game"**
- Make sure backend is running on port 8000
- Check that Ollama is running

**Backend won't start**
- Run `pip install -r requirements.txt` again
- Make sure virtual environment is activated

**Ollama errors**
- Make sure Ollama is running: `ollama serve`
- Verify model is installed: `ollama pull llama3.2`

**Game feels slow**
- AI responses take 2-5 seconds - this is normal!
- First response may be slower due to model loading
