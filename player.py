from typing import List, Optional

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
            
    def get_points(self) -> int:
        """
        Calculate total points:
        - Win: 3 points
        - Draw: 1 point
        - Loss: 0 points
        """
        return (self.wins * 3) + self.draws
    
    def get_win_percentage(self) -> float:
        """Calculate win percentage."""
        total_matches = self.wins + self.losses + self.draws
        if total_matches == 0:
            return 0.0
        return (self.wins + (self.draws / 2)) / total_matches * 100
    
    def get_opponents(self) -> List['Player']:
        """Get list of all opponents (excluding byes)."""
        return [match.player2 if match.player1 == self else match.player1 
                for match in self.match_history 
                if match.player2 is not None]  # Exclude byes
    
    def calculate_loss_rounds_score(self) -> int:
        """
        Calculate the sum of squares of rounds where the player lost.
        Returns a 3-digit maximum number.
        """
        loss_rounds_sum = 0
        for match in self.match_history:
            # Skip byes
            if match.player2 is None:
                continue
            
            # Check if this player lost the match
            if match.result is not None and match.result != self:
                loss_rounds_sum += match.round_number * match.round_number
        
        # Ensure it's maximum 3 digits
        return min(loss_rounds_sum, 999)
    
    def calculate_tiebreaker(self) -> str:
        """
        Calculate tiebreaker score in format XYYZZZAAA where:
        X = points
        YY = average opponent win percentage (2 digits)
        ZZZ = average opponent's opponents win percentage (3 digits)
        AAA = sum of squares of loss rounds (3 digits)
        TODO: should bye be considered as best or worst tiebreaker?
        """
        # Get points (X)
        points = self.get_points()
        
        # Calculate average opponent win percentage (YY)
        opponents = self.get_opponents()
        if not opponents:
            return f"{points}00000000"  # If no opponents, return just points with zeros
            
        avg_opp_winrate = sum(opp.get_win_percentage() for opp in opponents) / len(opponents)
        
        # Calculate average opponent's opponents win percentage (ZZZ)
        opp_opp_winrates = []
        for opp in opponents:
            opp_opponents = opp.get_opponents()
            if opp_opponents:
                avg_opp_opp_winrate = sum(opp_opp.get_win_percentage() 
                                        for opp_opp in opp_opponents) / len(opp_opponents)
                opp_opp_winrates.append(avg_opp_opp_winrate)
        
        avg_opp_opp_winrate = (sum(opp_opp_winrates) / len(opp_opp_winrates)) if opp_opp_winrates else 0
        
        # Calculate loss rounds score (AAA)
        loss_rounds_score = self.calculate_loss_rounds_score()
        
        # Format the tiebreaker string
        # For 75.3% -> 753, for 67.9% -> 679
        return f"{points}{avg_opp_winrate:.1f}{avg_opp_opp_winrate:.1f}{loss_rounds_score:03d}".replace(".", "") 