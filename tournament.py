from typing import List
import math
from player import Player

class Tournament:
    def __init__(self, number_of_players: int, draw_percentage: int):
        self.number_of_players = number_of_players
        self.draw_percentage = draw_percentage
        self.number_of_rounds = self._calculate_rounds()
        self.players = self._initialize_players()
        
    def _calculate_rounds(self) -> int:
        """Calculate number of rounds based on log2(number_of_players), rounded up."""
        return math.ceil(math.log2(self.number_of_players))
    
    def _initialize_players(self) -> List[Player]:
        """Initialize the list of players based on the number_of_players."""
        return [Player(player_id=i) for i in range(self.number_of_players)] 