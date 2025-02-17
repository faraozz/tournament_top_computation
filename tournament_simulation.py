from typing import List, Optional, Tuple
from tournament import Tournament
from match import Match
import itertools
import random

class Simulation:
    def __init__(self, tournament: Tournament):
        self.tournament = tournament
        self.matches: List[Match] = []
        self.current_round = 0
        
    def simulate(self) -> None:
        """
        Simulates multiple rounds of matches between players.
        """
        self.current_round = 0
        
        for round_num in range(self.tournament.number_of_rounds):
            self.current_round = round_num + 1
            self._simulate_round()
            
    def _get_lowest_scoring_player(self) -> 'Player':
        """Returns the player with the lowest total score (wins - losses) who hasn't had a bye."""
        eligible_players = [p for p in self.tournament.players if not p.has_had_bye]
        if not eligible_players:
            return min(self.tournament.players, key=lambda p: (p.wins - p.losses))
        return min(eligible_players, key=lambda p: (p.wins - p.losses))
    
    def _find_best_opponent(self, player: 'Player', available_players: List['Player']) -> Optional['Player']:
        """Find the best opponent for the given player based on win count and previous matches."""
        # Group available players by number of wins
        players_by_wins = {}
        for p in available_players:
            if p != player and not player.has_played_against(p):
                players_by_wins.setdefault(p.wins, []).append(p)
        
        if not players_by_wins:
            return None
        
        # Find closest win count that has available players
        player_win_counts = sorted(players_by_wins.keys())
        target_wins = player.wins
        closest_win_count = min(player_win_counts, 
                              key=lambda x: abs(x - target_wins))
        
        # Return random player from the closest win count group
        return random.choice(players_by_wins[closest_win_count])
            
    def _simulate_round(self) -> None:
        """
        Simulates a single round of matches between players.
        Matches players with similar win counts who haven't played each other yet.
        """
        available_players = self.tournament.players.copy()
        
        # Handle odd number of players
        if len(available_players) % 2 == 1:
            lowest_scorer = self._get_lowest_scoring_player()
            if lowest_scorer and not lowest_scorer.has_had_bye:
                available_players.remove(lowest_scorer)
                
                # Create a bye match
                bye_match = Match(lowest_scorer, None, lowest_scorer, self.current_round)
                self.matches.append(bye_match)
                lowest_scorer.wins += 1
                lowest_scorer.has_had_bye = True
                lowest_scorer.match_history.append(bye_match)
        
        # Create matches between remaining players
        while len(available_players) >= 2:
            player1 = available_players.pop(0)  # Take first available player
            opponent = self._find_best_opponent(player1, available_players)
            
            if opponent is None:
                # No valid opponent found, put player back in pool
                available_players.append(player1)
                continue
                
            available_players.remove(opponent)
            
            # Generate random number between 0 and 100
            random_number = random.randint(0, 100)
            
            # Determine match result
            if random_number < self.tournament.draw_percentage:
                result = None
            else:
                result = player1 if player1.player_id < opponent.player_id else opponent
            
            # Create match with result
            match = Match(player1, opponent, result, self.current_round)
            self.matches.append(match)
            
            # Update player statistics
            if result is None:
                player1.draws += 1
                opponent.draws += 1
            else:
                winner = result
                loser = opponent if winner == player1 else player1
                winner.wins += 1
                loser.losses += 1
            
            # Record that these players have faced each other
            player1.add_opponent(opponent)
            opponent.add_opponent(player1)
            
            # Add match to both players' match history
            player1.match_history.append(match)
            opponent.match_history.append(match)
        
        print(f"Round {self.current_round} completed") 