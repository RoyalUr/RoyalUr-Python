from royalur.model import (
    Piece, PlayerType, PlayerState, BoardShape, PathPair, Dice,
    Board, Roll, Move, GameSettings, GameMetadata
)
from .state import GameState, WaitingForRollGameState, WaitingForMoveGameState
from abc import ABC, abstractmethod
from typing import Callable


class PieceProvider(ABC):
    """
    An interface that provides instances of pieces. This may be used
    to store custom information with each piece, for situations such
    as adding stacking or unique piece behavior.
    """
    __slots__ = ()

    @abstractmethod
    def create_introduced(
            self,
            owner: PlayerType,
            new_path_index: int
    ) -> Piece:
        """
        Generates a new piece to be introduced to the board.
        """
        pass

    @abstractmethod
    def create_moved(
            self,
            origin_piece: Piece,
            new_path_index: int
    ) -> Piece:
        """
        Generates a piece that has been moved from
        another tile on the board.
        """
        pass


class PlayerStateProvider(ABC):
    """
    An interface that provides the manipulation of
    PlayerStates as a game progresses.
    """
    __slots__ = ()

    @abstractmethod
    def get_starting_piece_count(self) -> int:
        """
        Gets the number of pieces that players start with.
        """
        pass

    @abstractmethod
    def create(self, player: PlayerType):
        """
        Generates the starting state for the given player.
        """
        pass

    @abstractmethod
    def apply_piece_introduced(self, player_state: PlayerState, piece: Piece):
        """
        Generates a new player state that is a copy of
        the given player state, with the given piece
        introduced to the board.
        """
        pass

    @abstractmethod
    def apply_piece_captured(self, player_state: PlayerState, piece: Piece):
        """
        Generates a new player state that is a copy of
        the given player state, with the given piece
        captured.
        """
        pass

    @abstractmethod
    def apply_piece_scored(self, player_state: PlayerState, piece: Piece):
        """
        Generates a new player state that is a copy of
        the given player state, with the given piece scored.
        """
        pass


class RuleSet(ABC):
    """
    A set of rules that govern the play of a game of the Royal Game of Ur.
    """
    __slots__ = (
        "_board_shape", "_paths", "_dice_factory",
        "_piece_provider", "_player_state_provider",
    )

    _board_shape: BoardShape
    _paths: PathPair
    _dice_factory: Callable[[], Dice]
    _piece_provider: PieceProvider
    _player_state_provider: PlayerStateProvider

    def __init__(
            self,
            board_shape: BoardShape,
            paths: PathPair,
            dice_factory: Callable[[], Dice],
            piece_provider: PieceProvider,
            player_state_provider: PlayerStateProvider
    ):
        self._board_shape = board_shape
        self._paths = paths
        self._dice_factory = dice_factory
        self._piece_provider = piece_provider
        self._player_state_provider = player_state_provider

    @property
    def settings(self) -> GameSettings:
        """
        The settings used for this rule set.
        """
        return GameSettings(
            self._board_shape,
            self._paths,
            self._dice_factory,
            self._player_state_provider.get_starting_piece_count(),
            self.are_rosettes_safe(),
            self.do_rosettes_grant_extra_rolls(),
            self.do_captures_grant_extra_rolls()
        )

    @property
    def board_shape(self) -> BoardShape:
        """
        The shape of the game board.
        """
        return self._board_shape

    @property
    def paths(self) -> PathPair:
        """
        The paths that each player must take around the board.
        """
        self._paths

    @property
    def dice_factory(self) -> Callable[[], Dice]:
        """
        The generator of dice that are used to generate dice rolls.
        """
        return self._dice_factory

    @property
    def piece_provider(self) -> PieceProvider:
        """
        Provides the manipulation of piece values.
        """
        return self._piece_provider

    @property
    def player_state_provider(self) -> PlayerStateProvider:
        """
        Provides the manipulation of player state values.
        """
        return self._player_state_provider

    @abstractmethod
    def are_rosettes_safe(self) -> bool:
        """
        Gets whether rosettes are considered safe squares in this rule set.
        """
        pass

    @abstractmethod
    def do_rosettes_grant_extra_rolls(self) -> bool:
        """
        Gets whether landing on rosette tiles grants an additional roll.
        """
        pass

    @abstractmethod
    def do_captures_grant_extra_rolls(self) -> bool:
        """
        Gets whether capturing a piece grants an additional roll.
        """
        pass

    @abstractmethod
    def generate_initial_game_state(self) -> GameState:
        """
        Generates the initial state for a game.
        """
        pass

    @abstractmethod
    def find_available_moves(
            self,
            board: Board,
            player: PlayerState,
            roll: Roll,
    ) -> list[Move]:
        """
        Finds all available moves from the given state.
        """
        pass

    @abstractmethod
    def apply_roll(
        self,
        state: WaitingForRollGameState,
        roll: Roll,
    ) -> list[GameState]:
        """
        Applies the given roll to the given state to generate
        the new state of the game. Multiple game states will be
        returned to include action game states for maintaining
        history. However, the latest or highest-index game
        state will represent the state of the game after
        the roll was made.
        """
        pass

    @abstractmethod
    def apply_move(
        self,
        state: WaitingForMoveGameState,
        move: Move,
    ) -> list[GameState]:
        """
        Applies the given move to the given state to generate
        the new state of the game. Multiple game states may be
        returned to include action game states for maintaining
        history. However, the latest or highest-index game state
        will represent the state of the game after the move
        was made.

        This method does not check that the given move is valid.
        """
        pass


class RuleSetProvider(ABC):
    """
    Creates rule sets to match game settings.
    """
    __slots__ = ()

    @abstractmethod
    def create(
            self,
            settings: GameSettings,
            metadata: GameMetadata,
    ) -> RuleSet:
        """
        Creates a rule set to match the given settings and game metadata.
        """
        pass
