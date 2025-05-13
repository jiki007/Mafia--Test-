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
