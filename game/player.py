class Player:
    def __init__(self,user_id:int, username:str):
        self.user_id = user_id
        self.username = username
        self.role = None
        self.alive = True
        self.vote_target = None

    def assign_role(self,role):
        self.role = role
    
    def eliminate(self):
        self.alive = False
    
    def reset_vote(self):
        self.vote_target = None
        