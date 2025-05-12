from collections import Counter

class VoteManager:
    def __init__(self, allow_revoting=True):
        self.votes = {}
        self.allow_revoting = allow_revoting

    def cast_vote(self,voter_id:int,target_id:int):
        if self.allow_revoting or voter_id not in self.votes:
            self.votes[voter_id] = target_id

    def clear_votes(self):
        self.votes.clear()

    def get_vote_result(self):
        if not self.votes:
            return None
        vote_counts = Counter(self.votes.values())
        top_votes = vote_counts.most_common()

        if len(top_votes) < 1:
            return None

        # Tie detection
        if len(top_votes) > 1 and top_votes[0][1] == top_votes[1][1]:
            return "tie"

        return top_votes[0][0]  # user_id of most voted player
    
    def get_vote_counts(self):

        return dict(Counter(self.votes.values()))
    
    def get_vote_map(self):

        return self.votes.copy()
    


    

