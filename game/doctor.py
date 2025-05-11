from game.role import Role
from game.game_engine import GameEngine

game_engine = GameEngine()

class Doctor(Role):
    def __init__(self):
        super().__init__("Doctor")

    def night_action(self, game, actor, target):
        game_engine.saved_user_id = target.user_id
        print(f"{actor.username} (Doctor) is trying to save {target.username}")

    def description(self):
        return "You are the Doctor. Choose someone to save each night."
