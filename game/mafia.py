from game.role import Role
from game.game_engine import GameEngine

game_engine = GameEngine()

class Mafia(Role):
    def __init__(self):
        super().__init__("Mafia")
        
    def night_action(self, game_engine, actor, target):
        print(f"Mafia ({actor.username}) wants to kill {target.username}")
        game_engine.queue_kill(target)


    def description(self):
        return "You are Mafia. Eliminate one player at night."
