from game.role import Role

class Mafia(Role):
    def __init__(self):
        super().__init__("Mafia")

    def night_action(self, game, actor, target):
        print(f"{actor.username} (Mafia) wants to kill {target.username}")

    def description(self):
        return "You are Mafia. Eliminate one player at night."
