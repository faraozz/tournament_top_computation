class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.match_history = []  # Will store the history of matches played
        self.has_had_bye = False
        self.opponents_faced = set()  # Track player_ids of opponents already faced
        
    def has_played_against(self, other_player) -> bool:
        """Check if this player has already played against the given player."""
        return other_player.player_id in self.opponents_faced
    
    def add_opponent(self, other_player) -> None:
        """Record that this player has played against the given player."""
        if other_player is not None:  # Don't record None (bye) as an opponent
            self.opponents_faced.add(other_player.player_id) 