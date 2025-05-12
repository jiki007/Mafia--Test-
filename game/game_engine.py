class GameEngine:
    def __init__(self):
        self.players = []
        self.phase = 'lobby'
        self.night_kill = None
        self.saved_user_id = None
        self.investigated = None

    def add_player(self, player):
        self.players.append(player)

    def get_player_by_id(self, user_id):
        for p in self.players:
            if p.user_id == user_id:
                return p
        return None

    def assign_roles(self):
        from game.mafia import Mafia
        from game.detective import Detective
        from game.doctor import Doctor
        from game.civilian import Civilian
        import random

        random.shuffle(self.players)
        self.players[0].assign_role(Mafia())
        self.players[1].assign_role(Detective())
        self.players[2].assign_role(Doctor())

        for p in self.players[3:]:
            p.assign_role(Civilian())

    def queue_kill(self,player):
        self.night_kill = player.user_id

    def queue_save(self,player):
        self.saved_user_id = player.user_id
    
    def queue_investigation(self, detective, target):
        self.investigated = (detective, target)

    def reset_night_action(self):
        self.night_kill = None
        self.saved_user_id = None
        self.investigated = None

    def resolve_night(self):
        print(f"[DEBUG] resolve_night: night_kill={self.night_kill}, saved_user_id={self.saved_user_id}")

        #Killing or Saving procces
        killed_player = None

        if self.night_kill is not None:
            if self.night_kill != self.saved_user_id:
                target = self.get_player_by_id(self.night_kill)
                if target:
                    print(f"[DEBUG]: Target to eliminate: {target.username}")
                    if target and target.alive:
                        target.eliminate()
                        killed_player = target
                else:
                    print(f"[ERROR] No player found with ID {self.night_kill}")
            else:
                print("[DEBUG] Target was saved by doctor")

        killed_name = killed_player.username if killed_player else None
        investigation = self.investigated

        self.reset_night_action()

        return killed_name,investigation

    def check_win_condition(self):
        alive_players = [p for p in self.players if p.alive]
        mafia = [p for p in alive_players if p.role.name == "Mafia"]
        town = [p for p in alive_players if p.role.name != "Mafia"]

        if not town:
            return "No one"
        elif not mafia:
            return "Town"
        elif len(mafia) >= len(town):
            return "Mafia"
        return None



