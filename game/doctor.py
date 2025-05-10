from game.role import Role

class Doctor(Role):
    def __init__(self):
        super().__init__("Doctor")

    def night_action(self, game, actor, target):
        print(f"{actor.username} (Doctor) is trying to save {target.username}")

    def description(self):
        return "You are the Doctor. Choose someone to save each night."
