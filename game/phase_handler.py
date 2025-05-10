class PhaseHandler:
    def __init__(self):
        self.phase = "lobby"
    
    def set_phase(self,new_phase):
        self.phase = new_phase
    
    def is_night(self):
        return self.phase == 'night'
    
    def is_day(self):
        return self.phase == 'day'
    
