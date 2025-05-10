from collections import Counter

class VoteManager:
    def __init__(self):
        self.votes = {}
        
    def cast_vote(self,voter_id: int, target_id: int):
        self.votes[voter_id] = target_id

    def clear_votes(self):
        self.votes.clear()

    def get_vote_result(self):
        if not self.votes:
            return None
        
        vote_counts = Counter(self.votes.values())
        most_voted = vote_counts.most_common(1)[0]

        return most_voted[0]
    
    def get_vote_counts(self):
        return dict(Counter(self.votes.values()))
