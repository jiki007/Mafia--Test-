import json
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "game_data.json")

def save_game_to_json(players, winner, chat_title, chat_id,file_path=FILE_PATH):

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    data = {
        "group_name":chat_title,
        "group_id": chat_id,
        "winner":winner,
        "timestamp":datetime.now().isoformat(),
        "players": []
    }

    for player in players:
        data["players"].append({
            "username": player.username,
            "role": player.role.name,
            "status": "Alive" if player.alive else "Dead"
        })

    if os.path.exists(file_path):
        with open(file_path, "r+", encoding="utf-8") as f:
            try:
                games = json.load(f)
            except json.JSONDecodeError:
                games = []
            games.append(data)
            f.seek(0)
            json.dump(games, f, indent=4)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([data], f, indent=4)

def generate_final_summary(players, winning_team):
    role_emojis = {
        "Mafia": "🕵️‍♂️",
        "Detective": "🔍",
        "Doctor": "🩺",
        "Civilian": "👤"
    }

    summary = f"🏁 *Game Over!*\n🏆 *Winner:* {winning_team}\n\n👥 *Final Player Roles:*\n"
    for player in players:
        emoji = role_emojis.get(player.role.name, "")
        status = "☠️ Dead" if not player.alive else "✅ Alive"
        summary += f"• @{player.username} — {player.role.name} {emoji} ({status})\n"

    summary += "\nThanks for playing!"
    return summary
