from royalur.model import Board, PlayerType, PlayerState
from abc import ABC, abstractmethod
from overrides import overrides


class GameState(ABC):
    """
    A game state represents a single point within a game.
    """
    __slots__ = ("_board", "_light_player", "_dark_player")

    _board: Board
    _light_player: PlayerState
    _dark_player: PlayerState

    def __init__(
            self,
            board: Board,
            light_player: PlayerState,
            dark_player: PlayerState
    ):
        super().__init__()
        self._board = board
        self._light_player = light_player
        self._dark_player = dark_player

    @property
    def board(self) -> Board:
        """
        The state of the pieces on the board.
        """
        return self._board

    @property
    def light_player(self) -> PlayerState:
        """
        The state of the light player.
        """
        return self._light_player

    @property
    def dark_player(self) -> PlayerState:
        """
        The state of the dark player.
        """
        return self._dark_player

    def get_player(self, player: PlayerType) -> PlayerState:
        """
        Gets the state of the given player.
        """
        if player == PlayerType.LIGHT:
            return self._light_player
        if player == PlayerType.DARK:
            return self._dark_player

        raise ValueError(f"Unknown player {player}")

    @abstractmethod
    def is_playable(self) -> bool:
        """
        Returns whether this state is a valid state to be played from.
        """
        pass

    @abstractmethod
    def is_finished(self) -> bool:
        """
        Returns whether this state represents a finished game.
        """
        pass

    @abstractmethod
    def describe(self) -> str:
        """
        Generates an English text description of the state of the game.
        """
        pass


class OngoingGameState(GameState):
    """
    A game state from within a game where a winner has
    not yet been determined.
    """
    __slots__ = ("_turn",)

    _turn: PlayerType

    def __init__(
            self,
            board: Board,
            light_player: PlayerState,
            dark_player: PlayerState,
            turn: PlayerType
    ):
        super().__init__(board, light_player, dark_player)
        self._turn = turn

    @overrides
    def is_finished(self) -> bool:
        return False

    def get_turn(self) -> PlayerType:
        """
        Gets the player who made an action or that should make an action.
        """
        return self._turn

    def get_waiting(self) -> PlayerType:
        """
        Gets the player that is waiting whilst the other player makes the
        next interaction with the game.
        """
        return self._turn.get_other_player()

    def get_turn_player(self) -> PlayerState:
        """
        Gets the state of the player that we are waiting
        on to interact with the game.
        """
        return self.get_player(self._turn)

    def get_waiting_player(self) -> PlayerState:
        """
        Gets the state of the player that is waiting whilst
        the other player makes the next interaction with
        the game.
        """
        return self.get_player(self.get_waiting())


class WinGameState(GameState):
    """
    A game state where a player has won the game.
    """
    __slots__ = ("_winner",)

    _winner: PlayerType

    def __init__(
            self,
            board: Board,
            light_player: PlayerState,
            dark_player: PlayerState,
            winner: PlayerType
    ):
        super().__init__(board, light_player, dark_player)
        self._winner = winner

    @overrides
    def is_playable(self) -> bool:
        return False

    @overrides
    def is_finished(self) -> bool:
        return True

    def get_winner(self) -> PlayerType:
        """
        Gets the player that won the game.
        """
        return self._winner

    def get_loser(self) -> PlayerType:
        """
        Gets the player that lost the game.
        """
        return self._winner.get_other_player()

    def get_winning_player(self) -> PlayerState:
        """
        Gets the state of the player that won the game.
        """
        return self.get_player(self._winner)

    def get_losing_player(self) -> PlayerState:
        """
        Gets the state of the player that lost the game.
        """
        return self.get_player(self.get_loser())

    @overrides
    def describe(self) -> str:
        winner = self._winner.text_name.lower()
        return f"The {winner} player has won!"
