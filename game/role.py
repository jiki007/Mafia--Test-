from abc import ABC, abstractmethod

class Role(ABC):
    def __init__(self,name:str):
        self.name = name
    
    @abstractmethod
    def night_action(self,game,actor,target):
        pass

    @abstractmethod
    def description(self):
        pass