from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class GameStats:
    game_id: str
    win:int
    lose:int

@dataclass_json
@dataclass
class Stats:
    username: str
    gamestats:list[GameStats]

@dataclass_json
@dataclass
class StatAndUser:
    username: str
    game_id: str