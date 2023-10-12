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

    def __init__(self, value: int, display_name: str, character: str):
        self._value_ = value
        self._display_name = display_name
        self._character = character

    @property
    def display_name(self) -> str:
        """
        The name of this player.
        """
        return self._display_name

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
        Convert the player to a single character used to represent the
        player in shorthand notations.
        """
        return player.character if player else '.'
