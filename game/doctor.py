from game.role import Role
from game.game_engine import GameEngine

game_engine = GameEngine()

class Doctor(Role):
    def __init__(self):
        super().__init__("Doctor")

    def night_action(self, game_engine, actor, target):
        print(f"Doctor ({actor.username}) wants to save {target.username}")
        game_engine.queue_save(target)

    def description(self):
        return "You are the Doctor. Choose someone to save each night."
