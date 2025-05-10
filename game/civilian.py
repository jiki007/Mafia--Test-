from game.role import Role

class Civilian(Role):
    def __init__(self):
        super().__init__("Civilian")

    def night_action(self, game, actor, target):
        # Civilians have no night actions
        print(f"{actor.username} (Civilian) does nothing at night.")

    def description(self):
        return "You are a Civilian. You have no night powers. Use logic and discussion to find the Mafia."
