# 🔗Links for bot and groupchat where we had tests. 
https://t.me/InhaMafiaTestBot (Bot)
https://t.me/+kdhhGBEqme0zYWU1 (Group)


# 🕵️‍♂️ Mafia Game Telegram Bot

A fully playable, multiplayer Mafia game implemented using **Python** and **Object-Oriented Programming (OOP)**, designed for Telegram. Players interact through buttons, receive private role assignments, and vote to eliminate the Mafia — all managed automatically by the bot.

---

## 📌 Features

- 🎮 Interactive game with up to 10 players
- 🔁 Game phases: Lobby → Night → Day → Voting
- 🎭 Roles: Mafia, Doctor, Detective, Civilian
- ✉️ Private actions (kill, investigate, save)
- 🔐 Admin checks before game start
- 🔴 Mafia teammates shown during kill selection
- 📊 Voting system with public and private handling
- 📝 Final summary and game log saved to JSON
- 📂 Modular OOP architecture

---

## 🛠 Technologies Used

- Python 3
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/) (`v20+`)
- `asyncio`, `json`, `collections`, `datetime`
- Telegram Bot API

---

## 🚀 How to Run

### 1. 🔧 Setup

Install dependencies:

```bash
pip install python-telegram-bot
```

### 2. 🤖 Configure Your Bot

Replace the bot token in `telegram_bot.py`:

```python
app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
```

### 3. ▶️ Start the Bot

```bash
python main.py
```

---

## 👥 How to Play
IMPORTANT: Group should be created and bot should be added as an admin.
1. A player starts the game with `/startgame`
2. Others join via **Join button**
3. After 40 seconds, the game auto-starts if 5+ players
4. Roles are assigned privately
5. Mafia, Doctor, Detective take **night actions**
6. Daytime voting begins (private voting)
7. Players are eliminated, and game continues until:
   - All Mafia are eliminated — Town wins 🎉
   - Mafia outnumber Town — Mafia wins 🔪

---

## 📦 Project Structure

```
MafiaBot/
├── bot/
│   └── telegram_bot.py       # Main game bot logic and handlers
├── game/
│   ├── player.py             # Player class
│   ├── game_engine.py        # Game rules and logic
│   ├── vote_manager.py       # Voting system
│   ├── role.py               # Abstract Role base class
│   ├── mafia.py              # Mafia class
│   ├── doctor.py             # Doctor class
│   ├── detective.py          # Detective class
│   ├── civilian.py           # Civilian class
│   └── logger.py             # Game logger
├── data/
│   └── game_data.json        # Automatically saved match data
├── utilities.py              # Final summary and saving to JSON
├── main.py                   # Entry point
└── README.md                 # This file
```

---

## 📊 Sample Output

- Role assignment via private messages
- Voting buttons during day
- Final message:
```
🏁 Game Over!
🏆 Winner: Town

👥 Final Player Roles:
• @user1 — Mafia (☠️ Dead)
• @user2 — Detective (✅ Alive)
...
```

---

## 📚 OOP Concepts Used

- ✅ Inheritance (`Role` → Mafia, Doctor, etc.)
- ✅ Polymorphism (`night_action` methods)
- ✅ Abstraction (Abstract base classes)
- ✅ Encapsulation (player states)
- ✅ Modular structure with multiple classes/files

---

## 🧠 Authors

- 🔸 Developed by [Inha Students (ISE)]

---

## 📥 Data & Privacy

- All game data is ephemeral and saved only locally to `game_data.json`.
- Bot requires **admin rights** to manage messages properly in groups.

---

## 📃 License

This project is part of an academic assignment and is intended for educational purposes only.
