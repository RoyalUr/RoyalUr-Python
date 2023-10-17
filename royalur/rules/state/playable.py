from royalur.model import Board, PlayerState, PlayerType, Roll, Move
from .state import OngoingGameState
from overrides import overrides


class PlayableGameState(OngoingGameState):
    """
    A game state where we are waiting for interactions from a player.
    """
    __slots__ = ()

    @overrides
    def is_playable(self) -> bool:
        return True


class WaitingForRollGameState(PlayableGameState):
    """
    A game state where the game is waiting for a player to roll the dice.
    """

    @overrides
    def describe(self) -> str:
        turn = self.get_turn().text_name.lower()
        return f"Waiting for the {turn} player to roll the dice."


class WaitingForMoveGameState(PlayableGameState):
    """
    A game state where the game is waiting for a player to roll the dice.
    """
    __slots__ = ("_roll", "_available_moves")

    _roll: Roll
    _available_moves: list[Move]

    def __init__(
            self,
            board: Board,
            light_player: PlayerState,
            dark_player: PlayerState,
            turn: PlayerType,
            roll: Roll,
            available_moves: list[Move]
    ):
        super().__init__(board, light_player, dark_player, turn)
        self._roll = roll
        self._available_moves = available_moves

    @property
    def roll(self) -> Roll:
        """
        The roll that represents the number of places the
        player can move a piece.
        """
        return self._roll

    @property
    def available_moves(self) -> list[Move]:
        """
        The moves that are available to be made from this position.
        """
        return self._available_moves

    @overrides
    def describe(self) -> str:
        turn = self.get_turn().text_name.lower()
        return f"Waiting for the {turn} player to make a " \
            f"move with their roll of {self._roll.value}"
