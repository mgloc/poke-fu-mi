from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum

# ------------------------------ MATCH --------------------------------


@dataclass_json
@dataclass
class Round :
    player1_item_used : str
    player2_item_used :str
    winner : int # 1 or 2

@dataclass_json
@dataclass
class DualPlayers :
    player1 : str
    player2 : str

    def contains(self,player_id):
        return self.player1 == player_id or self.player2 == player_id

@dataclass_json
@dataclass
class Move :
    player_id : str
    item_id : str

@dataclass_json
@dataclass
class Match :
    match_id : str
    status : str # CREATED, IN_PROGRESS, COMPLETED
    players : DualPlayers


    round_history : list[Round] #round_left = len(round_history)
    current_round : Round

    winner : int # 0 : Draw, 1 : Player 1, 2 : Player 2, None : Match is IN_PROGRESS


# ------------------------------ POKEMON --------------------------------

@dataclass_json
@dataclass
class PokemonStats :
    pv : int
    power : int
    f_type : str
    s_type : str

@dataclass_json
@dataclass
class Pokemon :
    item_id : str
    in_game_id : str
    name : str
    stats : PokemonStats
