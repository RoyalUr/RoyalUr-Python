from .shape import BoardShape, BoardType
from .path import PathPair, PathType
from .dice import Dice, DiceType
from typing import Union, Callable


class GameSettings:
    """
    Settings for running games of the Royal Game of Ur. This is built for
    convenience, and cannot represent all possible combinations of rules
    that can be used to play the Royal Game of Ur. If a more exotic set of
    rules is desired, then you will need to construct your games manually.
    """
    __slots__ = (
        "_board_shape", "_paths", "_dice_factory",
        "_starting_piece_count", "_safe_rosettes",
        "_rosettes_grant_extra_rolls",
        "_captures_grant_extra_rolls"
    )

    _board_shape: BoardShape
    _paths: PathPair
    _dice_factory: Callable[[], Dice]
    _starting_piece_count: int
    _safe_rosettes: bool
    _rosettes_grant_extra_rolls: bool
    _captures_grant_extra_rolls: bool

    def __init__(
            self,
            board_shape: BoardShape,
            paths: PathPair,
            dice_factory: Callable[[], Dice],
            starting_piece_count: int,
            safe_rosettes: bool,
            rosettes_grant_extra_rolls: bool,
            captures_grant_extra_rolls: bool,
    ):
        if starting_piece_count < 1:
            raise ValueError("starting piece count must be at least 1")

        self._board_shape = board_shape
        self._paths = paths
        self._dice_factory = dice_factory
        self._starting_piece_count = starting_piece_count
        self._safe_rosettes = safe_rosettes
        self._rosettes_grant_extra_rolls = rosettes_grant_extra_rolls
        self._captures_grant_extra_rolls = captures_grant_extra_rolls

    @staticmethod
    def create_finkel() -> 'GameSettings':
        """
        Creates an instance of the rules used in the YouTube
        video Tom Scott vs. Irving Finkel.
        """
        return GameSettings(
            BoardType.STANDARD.create_board_shape(),
            PathType.BELL.create_path_pair(),
            lambda: DiceType.FOUR_BINARY.create_dice(),
            7,
            True,
            True,
            False,
        )

    @staticmethod
    def create_masters() -> 'GameSettings':
        """
        Creates an instance of the settings proposed by James Masters.
        """
        return GameSettings(
            BoardType.STANDARD.create_board_shape(),
            PathType.MASTERS.create_path_pair(),
            lambda: DiceType.FOUR_BINARY.create_dice(),
            7,
            False,
            True,
            False,
        )

    @staticmethod
    def create_aseb() -> 'GameSettings':
        """
        Creates an instance of the settings used for Aseb.
        """
        return GameSettings(
            BoardType.ASEB.create_board_shape(),
            PathType.ASEB.create_path_pair(),
            lambda: DiceType.FOUR_BINARY.create_dice(),
            5,
            True,
            True,
            False,
        )

    @property
    def board_shape(self) -> BoardShape:
        """
        The shape of the game board.
        """
        return self._board_shape

    def with_board_shape(
            self,
            board_shape: Union[BoardShape, BoardType]
    ) -> 'GameSettings':
        """
        Generates new game settings with a new board shape.
        """
        if isinstance(board_shape, BoardType):
            board_shape = board_shape.create_board_shape()

        return GameSettings(
            board_shape, self._paths, self._dice_factory,
            self._starting_piece_count, self._safe_rosettes,
            self._rosettes_grant_extra_rolls,
            self._captures_grant_extra_rolls
        )

    @property
    def paths(self) -> PathPair:
        """
        The paths that each player must take around the board.
        """
        return self._paths

    def with_paths(self, paths: Union[PathPair, PathType]) -> 'GameSettings':
        """
        Generates new game settings with new paths.
        """
        if isinstance(paths, PathType):
            paths = paths.create_path_pair()

        return GameSettings(
            self._board_shape, paths, self._dice_factory,
            self._starting_piece_count, self._safe_rosettes,
            self._rosettes_grant_extra_rolls,
            self._captures_grant_extra_rolls
        )

    @property
    def dice(self) -> Callable[[], Dice]:
        """
        A generator for the dice that should be used to
        generate dice rolls in games.
        """
        return self._dice_factory

    def with_dice(
            self,
            dice: Union[Callable[[], Dice], DiceType]
    ) -> 'GameSettings':
        """
        Generates new game settings with new dice.
        """
        if isinstance(dice, DiceType):
            def create_from_dice_type():
                return dice.create_dice()

            dice = create_from_dice_type

        return GameSettings(
            self._board_shape, self._paths, dice,
            self._starting_piece_count, self._safe_rosettes,
            self._rosettes_grant_extra_rolls,
            self._captures_grant_extra_rolls
        )

    @property
    def starting_piece_count(self) -> int:
        """
        The number of pieces that each player starts with.
        """
        return self._starting_piece_count

    def with_starting_piece_count(
            self,
            starting_piece_count: int
    ) -> 'GameSettings':
        """
        Generates new game settings with a new starting piece count.
        """
        return GameSettings(
            self._board_shape, self._paths, self._dice_factory,
            starting_piece_count, self._safe_rosettes,
            self._rosettes_grant_extra_rolls,
            self._captures_grant_extra_rolls
        )

    @property
    def safe_rosettes(self) -> bool:
        """
        Whether pieces on rosette tiles are safe from capture.
        """
        return self._safe_rosettes

    def with_safe_rosettes(self, safe_rosettes: bool) -> 'GameSettings':
        """
        Generates new game settings with a new value
        for whether rosettes are safe.
        """
        return GameSettings(
            self._board_shape, self._paths, self._dice_factory,
            self._starting_piece_count, safe_rosettes,
            self._rosettes_grant_extra_rolls,
            self._captures_grant_extra_rolls
        )

    @property
    def rosettes_grant_extra_rolls(self) -> bool:
        """
        Whether landing on a rosette tile grants the player an
        additional roll of the dice.
        """
        return self._rosettes_grant_extra_rolls

    def with_rosettes_grant_extra_rolls(
            self, rosettes_grant_extra_rolls: bool
    ) -> 'GameSettings':
        """
        Generates new game settings with a new value for whether
        landing on a rosette grants an extra roll.
        """
        return GameSettings(
            self._board_shape, self._paths, self._dice_factory,
            self._starting_piece_count, self._safe_rosettes,
            rosettes_grant_extra_rolls,
            self._captures_grant_extra_rolls
        )

    @property
    def captures_grant_extra_rolls(self) -> bool:
        """
        Whether capturing a piece grants the player an additional
        roll of the dice.
        """
        return self._captures_grant_extra_rolls

    def with_captures_grant_extra_rolls(
            self, captures_grant_extra_rolls: bool
    ) -> 'GameSettings':
        """
        Generates new game settings with a new value for whether
        capturing a piece grants an extra roll.
        """
        return GameSettings(
            self._board_shape, self._paths, self._dice_factory,
            self._starting_piece_count, self._safe_rosettes,
            self._rosettes_grant_extra_rolls,
            captures_grant_extra_rolls
        )
