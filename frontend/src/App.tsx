import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

interface Character {
  name: string;
  class: string;
  level: number;
  hp: number;
  max_hp: number;
  xp: number;
  gold: number;
  stats: { [key: string]: number };
  inventory: string[];
  equipment: string[];
  skills: string[];
}

interface WorldState {
  location: string;
  in_combat: boolean;
  current_enemy: Enemy | null;
}

interface Enemy {
  type: string;
  hp: number;
  max_hp: number;
}

interface GameState {
  character: Character;
  world: WorldState;
  story_log: string[];
}

interface Message {
  text: string;
  isPlayer: boolean;
  id: number;
}

type GamePhase = 'start' | 'playing' | 'gameover';

function App() {
  const [phase, setPhase] = useState<GamePhase>('start');
  const [gameId, setGameId] = useState<string>('');
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [playerAction, setPlayerAction] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [charName, setCharName] = useState('');
  const [charClass, setCharClass] = useState('warrior');
  const [background, setBackground] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startGame = async () => {
    if (!charName.trim()) return;

    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/game/new`, {
        character_name: charName,
        character_class: charClass,
        background: background
      });

      // ✅ FIX: Use the actual game_id returned by the backend
      setGameId(response.data.game_id);
      setGameState(response.data.game_state);
      setMessages([{
        text: response.data.narration,
        isPlayer: false,
        id: Date.now()
      }]);
      setPhase('playing');
    } catch (error) {
      console.error('Failed to start game:', error);
      alert('Failed to start game. Make sure the backend is running.');
    }
    setIsLoading(false);
  };

  const sendAction = async () => {
    if (!playerAction.trim() || !gameId) return;

    const userMessage: Message = {
      text: playerAction,
      isPlayer: true,
      id: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setPlayerAction('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/game/action`, {
        game_id: gameId,
        action: playerAction
      });

      // ✅ FIX: Keep game_id from backend response, don't overwrite with character name
      if (response.data.game_id) {
        setGameId(response.data.game_id);
      }

      setGameState(response.data.game_state);
      setMessages(prev => [...prev, {
        text: response.data.narration,
        isPlayer: false,
        id: Date.now() + 1
      }]);

      if (response.data.game_state.character.hp <= 0) {
        setPhase('gameover');
      }
    } catch (error) {
      console.error('Failed to send action:', error);
      setMessages(prev => [...prev, {
        text: 'Error: Could not process your action. Is the backend running?',
        isPlayer: false,
        id: Date.now() + 1
      }]);
    }
    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendAction();
    }
  };

  if (phase === 'start') {
    return (
      <div className="App">
        <div className="start-screen">
          <h1>AI Dungeon Master</h1>
          <p className="subtitle">A Fantasy RPG Adventure</p>

          <div className="character-creation">
            <div className="form-group">
              <label>Character Name</label>
              <input
                type="text"
                value={charName}
                onChange={(e) => setCharName(e.target.value)}
                placeholder="Enter your hero's name"
                maxLength={20}
              />
            </div>

            <div className="form-group">
              <label>Class</label>
              <select value={charClass} onChange={(e) => setCharClass(e.target.value)}>
                <option value="warrior">Warrior - Strong and sturdy</option>
                <option value="rogue">Rogue - Quick and cunning</option>
                <option value="mage">Mage - Powerful magic user</option>
                <option value="cleric">Cleric - Holy healer</option>
              </select>
            </div>

            <div className="form-group">
              <label>Background (Optional)</label>
              <textarea
                value={background}
                onChange={(e) => setBackground(e.target.value)}
                placeholder="A brief backstory..."
                maxLength={200}
                rows={3}
              />
            </div>

            <button
              onClick={startGame}
              disabled={!charName.trim() || isLoading}
              className="start-btn"
            >
              {isLoading ? 'Creating World...' : 'Begin Adventure'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (phase === 'gameover') {
    return (
      <div className="App">
        <div className="gameover-screen">
          <h1>You Have Fallen</h1>
          <p>Your adventure has come to an end...</p>
          <button onClick={() => {
            setPhase('start');
            setMessages([]);
            setGameState(null);
            setGameId('');
            setCharName('');
          }} className="start-btn">
            Start New Adventure
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="App game-container">
      <div className="game-main">
        <div className="chat-panel">
          <div className="messages-container">
            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.isPlayer ? 'player' : 'dm'}`}>
                <div className="message-content">{msg.text}</div>
              </div>
            ))}
            {isLoading && <div className="message dm loading">DM is thinking...</div>}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <input
              type="text"
              value={playerAction}
              onChange={(e) => setPlayerAction(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="What do you want to do?"
              disabled={isLoading}
            />
            <button onClick={sendAction} disabled={isLoading || !playerAction.trim()}>
              {isLoading ? '...' : 'Send'}
            </button>
          </div>
        </div>
      </div>

      <div className="sidebar">
        {gameState && (
          <>
            <div className="character-panel">
              <h3>{gameState.character.name}</h3>
              <p className="class-level">
                Level {gameState.character.level} {gameState.character.class}
              </p>

              <div className="stat-bar hp-bar">
                <span>HP</span>
                <div className="bar-container">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${(gameState.character.hp / gameState.character.max_hp) * 100}%`,
                      backgroundColor: gameState.character.hp < gameState.character.max_hp * 0.3 ? '#e74c3c' : '#27ae60'
                    }}
                  />
                </div>
                <span>{gameState.character.hp}/{gameState.character.max_hp}</span>
              </div>

              <div className="stat-bar xp-bar">
                <span>XP</span>
                <div className="bar-container">
                  <div
                    className="bar-fill xp-fill"
                    style={{ width: `${(gameState.character.xp % 100)}%` }}
                  />
                </div>
                <span>{gameState.character.xp}</span>
              </div>

              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">STR</span>
                  <span className="stat-value">{gameState.character.stats.str}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">DEX</span>
                  <span className="stat-value">{gameState.character.stats.dex}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">CON</span>
                  <span className="stat-value">{gameState.character.stats.con}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">INT</span>
                  <span className="stat-value">{gameState.character.stats.int}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">WIS</span>
                  <span className="stat-value">{gameState.character.stats.wis}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">CHA</span>
                  <span className="stat-value">{gameState.character.stats.cha}</span>
                </div>
              </div>

              <div className="gold-display">
                💰 {gameState.character.gold} Gold
              </div>
            </div>

            <div className="inventory-panel">
              <h4>Equipment</h4>
              <ul>
                {gameState.character.equipment.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>

              <h4>Inventory</h4>
              <ul>
                {gameState.character.inventory.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>

              <h4>Skills</h4>
              <ul>
                {gameState.character.skills.map((skill, idx) => (
                  <li key={idx}>{skill}</li>
                ))}
              </ul>
            </div>

            {gameState.world.in_combat && gameState.world.current_enemy && (
              <div className="combat-panel">
                <h4>⚔️ Combat!</h4>
                <div className="enemy-stat">
                  <strong>{gameState.world.current_enemy.type}</strong>
                  <div className="stat-bar hp-bar">
                    <div className="bar-container">
                      <div
                        className="bar-fill enemy-fill"
                        style={{
                          width: `${(gameState.world.current_enemy.hp / gameState.world.current_enemy.max_hp) * 100}%`
                        }}
                      />
                    </div>
                    <span>{gameState.world.current_enemy.hp}/{gameState.world.current_enemy.max_hp} HP</span>
                  </div>
                </div>
              </div>
            )}

            <div className="location-panel">
              <h4>📍 Location</h4>
              <p>{gameState.world.location}</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;