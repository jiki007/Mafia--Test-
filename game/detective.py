from game.role import Role
from game.game_engine import GameEngine

game_engine = GameEngine()

class Detective(Role):
    def __init__(self):
        super().__init__("Detective")

    def night_action(self, game, actor, target):
        game_engine.queue_investigation(actor, target)
        print(f"{actor.username} (Detective) is investigating {target.username}")

    def description(self):
        return "You are the Detective. Investigate one player each night."
