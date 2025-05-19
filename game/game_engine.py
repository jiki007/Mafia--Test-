from collections import Counter

class GameEngine:
    def __init__(self):
        self.players = []
        self.phase = 'lobby'
        self.night_kill = []
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

        total_players = len(self.players)
        random.shuffle(self.players)

        mafia_count = max(1, total_players // 4)

        print(f"[DBUG] Assigning roles: {mafia_count} Mafia for {total_players} players.")

        for i in range(mafia_count):
            self.players[i].assign_role(Mafia())

        if mafia_count < total_players:
            self.players[mafia_count].assign_role(Detective())

        if mafia_count + 1 < total_players:
            self.players[mafia_count + 1].assign_role(Doctor())

        for i in range(mafia_count + 2, total_players):
            self.players[i].assign_role(Civilian())

    def queue_kill(self,player):
        self.night_kill.append(player.user_id)

    def queue_save(self,player):
        self.saved_user_id = player.user_id
    
    def queue_investigation(self, detective, target):
        self.investigated = (detective, target)

    def reset_night_action(self):
        self.night_kill = []
        self.saved_user_id = None
        self.investigated = None

    def resolve_night(self):
        print(f"[DEBUG] resolve_night: night_kill={self.night_kill}, saved_user_id={self.saved_user_id}")

        #Killing or Saving procces
        killed_player = None

        if self.night_kill:
            vote_counts = Counter(self.night_kill)
            most_common_id, count = vote_counts.most_common(1)[0]

            if most_common_id != self.saved_user_id:
                target = self.get_player_by_id(most_common_id)
                if target and target.alive:
                    target.eliminate()
                    killed_player = target
            else:
                print("[DEBUG] Doctro saved the Mafia target")
        else:
            print("[DEBUG] No mafia votes cast")

        investigation = self.investigated

        self.reset_night_action()

        return killed_player,investigation

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



