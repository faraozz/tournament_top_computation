from typing import List, Optional, Tuple
from tournament import Tournament
from match import Match
import itertools
import random
import time

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
        #TODO: add a progress bar
        #TODO: simulate many tournaments at once and average the results
        
        for round_num in range(self.tournament.number_of_rounds):
            round_start = time.time()
            self.current_round = round_num + 1
            self._simulate_round()
            round_end = time.time()
            round_time = round_end - round_start
            print(f"Round {self.current_round} completed in {round_time:.2f} seconds")
            
    def _get_lowest_scoring_player(self, available_players: List['Player']) -> Optional['Player']:
        """Returns the player with the lowest total score who hasn't had a bye."""
        eligible_players = [p for p in available_players if not p.has_had_bye]
        if not eligible_players:
            # If all players have had byes, pick the lowest scoring from available
            return min(available_players, key=lambda p: (p.get_points(), p.calculate_tiebreaker()))
        return min(eligible_players, key=lambda p: (p.get_points(), p.calculate_tiebreaker()))
    
    def _find_best_opponent(self, player: 'Player', available_players: List['Player']) -> Optional['Player']:
        """
        Find the best opponent for the given player.
        First priority: Haven't played against each other
        Second priority: Score difference no more than 3
        Third priority: Closest score within allowed range
        """
        # Get all valid opponents (not played against yet)
        valid_opponents = [p for p in available_players 
                         if p != player 
                         and not player.has_played_against(p)
                         and abs(p.get_points() - player.get_points()) <= 3]  # Score difference check
        
        if not valid_opponents:
            # If no opponents within 3 points, try again without score restriction
            valid_opponents = [p for p in available_players 
                             if p != player 
                             and not player.has_played_against(p)]
            if not valid_opponents:
                return None
        
        # Group valid opponents by points
        opponents_by_points = {}
        for p in valid_opponents:
            points = p.get_points()
            if points not in opponents_by_points:
                opponents_by_points[points] = []
            opponents_by_points[points].append(p)
        
        # Find closest point total that has available opponents
        player_points = player.get_points()
        point_totals = sorted(opponents_by_points.keys())
        closest_points = min(point_totals, key=lambda x: abs(x - player_points))
        
        # Return random player from the closest points group
        return random.choice(opponents_by_points[closest_points])
    
    def _find_valid_pairing(self, available_players: List['Player']) -> Tuple[Optional['Player'], Optional['Player']]:
        """
        Find a valid pairing of players who haven't played each other yet.
        Tries all possible combinations to ensure no players are left out unnecessarily.
        """
        if len(available_players) < 2:
            return None, None
        
        # Sort players by number of potential opponents (ascending)
        # This helps match players with fewer options first
        players_by_options = []
        for player in available_players:
            valid_opponents = sum(1 for p in available_players 
                                if p != player and not player.has_played_against(p))
            players_by_options.append((valid_opponents, player))
        
        # Sort by number of valid opponents (first element of tuple)
        players_by_options.sort(key=lambda x: x[0])  # Sort by the opponent count
        
        # Try each player as potential first player, starting with those with fewest options
        for _, player1 in players_by_options:
            opponent = self._find_best_opponent(player1, available_players)
            if opponent:
                return player1, opponent
        
        return None, None
            
    def _simulate_round(self) -> None:
        """
        Simulates a single round of matches between players.
        Matches players with similar win counts who haven't played each other yet.
        """
        available_players = self.tournament.players.copy()
        random.shuffle(available_players)  # Randomize initial player order
        
        # Handle odd number of players
        if len(available_players) % 2 == 1:
            lowest_scorer = self._get_lowest_scoring_player(available_players)
            if lowest_scorer:
                available_players.remove(lowest_scorer)
                
                # Create a bye match
                bye_match = Match(lowest_scorer, None, lowest_scorer, self.current_round)
                self.matches.append(bye_match)
                lowest_scorer.wins += 1
                lowest_scorer.has_had_bye = True
                lowest_scorer.match_history.append(bye_match)
        # Create matches between remaining players
        #TODO: speed up this somehow...
        while len(available_players) >= 2:
            player1, player2 = self._find_valid_pairing(available_players)
            if player1 is None or player2 is None:
                # No valid pairings found among remaining players
                break
            available_players.remove(player1)
            available_players.remove(player2)
            
            # Generate random number between 0 and 100
            random_number = random.randint(0, 100)
            
            # Determine match result
            if random_number < self.tournament.draw_percentage:
                result = None
            else:
                result = player1 if player1.player_id < player2.player_id else player2
            
            # Create match with result
            match = Match(player1, player2, result, self.current_round)
            self.matches.append(match)
            
            # Update player statistics
            if result is None:
                player1.draws += 1
                player2.draws += 1
            else:
                winner = result
                loser = player2 if winner == player1 else player1
                winner.wins += 1
                loser.losses += 1
            
            # Record that these players have faced each other
            player1.add_opponent(player2)
            player2.add_opponent(player1)
            
            # Add match to both players' match history
            player1.match_history.append(match)
            player2.match_history.append(match)