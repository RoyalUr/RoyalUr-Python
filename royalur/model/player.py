from enum import Enum
from typing import Optional


class PlayerType(Enum):
    """
    Represents the players of a game.
    """
    LIGHT = (1, "Light", 'L')
    """
    The light player.
    """

    DARK = (2, "Dark", 'D')
    """
    The dark player.
    """

    def __init__(self, value: int, text_name: str, character: str):
        self._value_ = value
        self._text_name = text_name
        self._character = character

    @property
    def text_name(self) -> str:
        """
        The name of this player.
        """
        return self._text_name

    @property
    def character(self) -> str:
        """
        The character used to represent this player in shorthand notations.
        """
        return self._character

    def get_other_player(self) -> 'PlayerType':
        """
        Retrieve the PlayerType representing the other player.
        """
        if self == PlayerType.LIGHT:
            return PlayerType.DARK
        elif self == PlayerType.DARK:
            return PlayerType.LIGHT
        else:
            raise ValueError(f"Unknown PlayerType {self}")

    @staticmethod
    def to_char(player: Optional['PlayerType']) -> str:
        """
        Convert the player to a single character used to
        represent the player in shorthand notations.
        """
        return player.character if player else '.'


class PlayerState:
    """
    A player state represents the state of a single player
    at a point in the game. This includes the player's score
    and number of pieces left to play.
    """
    __slots__ = ("_player", "_piece_count", "_score")

    _player: PlayerType
    _piece_count: int
    _score: int

    def __init__(self, player: PlayerType, piece_count: int, score: int):
        if piece_count < 0:
            raise ValueError("piece_count cannot be negative")
        if score < 0:
            raise ValueError("score cannot be negative")

        self._player = player
        self._piece_count = piece_count
        self._score = score

    @property
    def player(self) -> PlayerType:
        """
        The player that this state represents.
        """
        return self._player

    @property
    def piece_count(self) -> int:
        """
        The number of pieces that the player has available to introduce
        to the board.
        """
        return self._piece_count

    @property
    def score(self) -> int:
        """
        The number of pieces that the player has taken off the board.
        """
        return self._score

    def __hash__(self) -> int:
        return hash((self._player, self._piece_count, self._score))

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False

        return self._player == other._player \
            and self._piece_count == other._piece_count \
            and self._score == other._score
