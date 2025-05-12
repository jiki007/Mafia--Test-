from game.role import Role
from game.game_engine import GameEngine

game_engine = GameEngine()

class Detective(Role):
    def __init__(self):
        super().__init__("Detective")

    def night_action(self, game_engine, actor, target):
        print(f"Detective ({actor.username}) investigates {target.username}")
        game_engine.queue_investigation(actor, target)


    def description(self):
        return "You are the Detective. Investigate one player each night."
