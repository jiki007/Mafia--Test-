from game.role import Role
from game.game_engine import GameEngine

game_engine = GameEngine()

class Mafia(Role):
    def __init__(self):
        super().__init__("Mafia")

    def night_action(self, game, actor, target):
        game_engine.night_kill = target.user_id
        print(f"{actor.username} (Mafia) wants to kill {target.username}")

    def description(self):
        return "You are Mafia. Eliminate one player at night."
