from player import Player
from typing import Optional

class Match:
    def __init__(self, player1: Player, player2: Optional[Player], result: Optional[Player] = None, round_number: int = 0):
        self.player1 = player1
        self.player2 = player2
        self.result = result
        self.round_number = round_number 