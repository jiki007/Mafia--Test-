class GameEngine:
    def __init__(self):
        self.players = []
        self.phase = 'lobby'
        self.kill_queue = []
        self.save_queue = []
        self.investigate_reslut = None

    def add_player(self, player):
        self.players.append(player)

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

        for plyrs in self.players[3:]:
            plyrs.assign_roles(Civilian())

    def queue_kill(self,player):
        self.kill_queue.append(player)

    def queue_save(self,player):
        self.save_queue.append(player)

    def resolve_night(self):
        #Killing or Saving procces
        killed = None
        if self.kill_queue:
            target = self.kill_queue[0]
            if target not in self.save_queue:
                target.eliminate()
                killed = target.username
        self.kill_queue.clear()
        self.save_queue.clear()
        return killed

    def check_win_condition(self):
        alive_players = [p for p in self.players if p.alive]
        mafia = [p for p in alive_players if p.role.name == "Mafia"]
        town = [p for p in alive_players if p.role.name != "Mafia"]

        if not mafia:
            return "Town"
        elif len(mafia) >= len(town):
            return "Mafia"
        return None



