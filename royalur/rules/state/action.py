from royalur.model import Board, PlayerState, PlayerType, Roll, Move
from .state import OngoingGameState
from overrides import overrides


class ActionGameState(OngoingGameState):
    """
    A game state that is included in the middle of a
    game to record an action that was taken, but that
    is not a valid state to be in.
    """
    __slots__ = ()

    @overrides
    def is_playable(self) -> bool:
        return False


class RolledGameState(ActionGameState):
    """
    A game state that represents a roll that was made in a game.
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
        The roll of the dice that was used for the move.
        """
        return self._roll

    @property
    def available_moves(self) -> list[Move]:
        """
        The moves that are available from this position
        using the given roll.
        """
        return self._available_moves

    @overrides
    def describe(self) -> str:
        builder = []
        builder.append("The ")
        builder.append(self.get_turn().text_name.lower())
        builder.append(" player rolled ")
        builder.append(str(self.roll))

        if not self._available_moves:
            if self._roll.value() == 0:
                builder.append(", and had no moves")
            else:
                builder.append(", and all moves were blocked")

        builder.append(".")
        return "".join(builder)


class MovedGameState(ActionGameState):
    """
    A game state that represents a move of a piece on the board.
    """
    __slots__ = ("_roll", "_move")

    _roll: Roll
    _move: Move

    def __init__(
            self,
            board: Board,
            light_player: PlayerState,
            dark_player: PlayerState,
            turn: PlayerType,
            roll: Roll,
            move: Move
    ):
        super().__init__(board, light_player, dark_player, turn)
        self._roll = roll
        self._move = move

    @property
    def roll(self) -> Roll:
        """
        The roll of the dice that was used for the move.
        """
        return self._roll

    @property
    def move(self) -> Move:
        """
        The move that was made.
        """
        return self._move

    @overrides
    def describe(self) -> str:
        builder = []
        builder.append("The ")
        builder.append(self.get_turn().text_name.lower())
        builder.append(" player ")

        introducing = self.move.is_introducing_piece()
        scoring = self.move.is_scoring_piece()

        if introducing and scoring:
            builder.append("scored a newly introduced piece.")
        elif scoring:
            builder.append("scored their ")
            builder.append(str(self.move.get_source()))
            builder.append("piece.")
        elif introducing:
            builder.append("introduced a piece to ")
            builder.append(str(self.move.get_dest()))
            builder.append(".")
        else:
            builder.append("moved their ")
            builder.append(str(self.move.get_source()))
            builder.append(" piece to ")
            if self.move.is_capture():
                builder.append("capture ")
            builder.append(str(self.move.get_dest()))
            builder.append(".")

        return "".join(builder)
