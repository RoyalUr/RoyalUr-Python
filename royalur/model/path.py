from .tile import Tile
from .player import PlayerType
from enum import Enum
from typing import Callable


class PathPair:
    """
    Represents a pair of paths for the light and dark players to
    move their pieces along in a game of the Royal Game of Ur.
    """
    __slots__ = (
        "_name", "_light_with_ends", "_dark_with_ends",
        "_light", "_dark",
    )

    _name: str
    _light_with_ends: list[Tile]
    _dark_with_ends: list[Tile]
    _light: list[Tile]
    _dark: list[Tile]

    def __init__(
            self,
            name: str,
            lightWithStartEnd: list[Tile],
            darkWithStartEnd: list[Tile],
    ):
        self._name = name
        self._light_with_ends = [*lightWithStartEnd]
        self._dark_with_ends = [*darkWithStartEnd]
        self._light = self._light_with_ends[1:-1]
        self._dark = self._dark_with_ends[1:-1]

    @property
    def name(self) -> str:
        """
        The name of this path pair.
        """
        return self.name

    @property
    def light_with_ends(self) -> list[Tile]:
        """
        The path that light players take around the board, including
        the start and end tiles that exist off the board.
        """
        return self._light_with_ends

    @property
    def dark_with_ends(self) -> list[Tile]:
        """
        The path that dark players take around the board, including
        the start and end tiles that exist off the board.
        """
        return self._dark_with_ends

    @property
    def light(self) -> list[Tile]:
        """
        The path that light players take around the board, excluding
        the start and end tiles that exist off the board.
        """
        return self._light

    @property
    def dark(self) -> list[Tile]:
        """
        The path that dark players take around the board, excluding
        the start and end tiles that exist off the board.
        """
        return self._dark

    @property
    def light_start(self) -> Tile:
        """
        The start tile of the light player that exists off the board.
        """
        return self._light_with_ends[0]

    @property
    def light_end(self) -> Tile:
        """
        The end tile of the light player that exists off the board.
        """
        return self._light_with_ends[-1]

    @property
    def dark_start(self) -> Tile:
        """
        The start tile of the dark player that exists off the board.
        """
        return self._dark_with_ends[0]

    @property
    def dark_end(self) -> Tile:
        """
        The end tile of the dark player that exists off the board.
        """
        return self._dark_with_ends[-1]

    def get(self, player: PlayerType) -> list[Tile]:
        """
        Gets the path of the given player, excluding the start and
        end tiles that exist off the board.
        """
        if player == PlayerType.LIGHT:
            return self._light
        elif player == PlayerType.DARK:
            return self._dark
        else:
            raise ValueError(f"Unknown PlayerType {player}")

    def get_with_ends(self, player: PlayerType) -> list[Tile]:
        """
        Gets the path of the given player, including the start and
        end tiles that exist off the board.
        """
        if player == PlayerType.LIGHT:
            return self._light_with_ends
        elif player == PlayerType.DARK:
            return self._dark_with_ends
        else:
            raise ValueError(f"Unknown PlayerType {player}")

    def get_start(self, player: PlayerType) -> list[Tile]:
        """
        Gets the start tile of the given player, which exists off the board.
        """
        return self.get_with_ends(player)[0]

    def get_end(self, player: PlayerType) -> list[Tile]:
        """
        Gets the end tile of the given player, which exists off the board.
        """
        return self.get_with_ends(player)[-1]

    def is_equivalent(self, other: 'PathPair') -> bool:
        """
        Determines whether this set of paths and other cover the
        same tiles, in the same order. This does not check the
        start and end tiles that exist off the board, or the name
        of the paths.
        """
        return self._light == other._light

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False

        return self._name == other._name \
            and self._light_with_ends == other._light_with_ends \
            and self._dark_with_ends == other._dark_with_ends


class AsebPathPair(PathPair):
    """
    The standard paths that are used for Aseb.

    Citation: W. Crist, A.E. Dunn-Vaturi, and A. de Voogt,
    Ancient Egyptians at Play: Board Games Across Borders,
    Bloomsbury Egyptology, Bloomsbury Academic, London, 2016.
    """
    __slots__ = ()

    NAME: str = "Aseb"
    """
    The name of this type of path pair.
    """

    LIGHT_PATH: list[Tile] = Tile.create_path(
        (1, 5),
        (1, 1),
        (2, 1),
        (2, 12),
        (1, 12),
    )
    """
    The path of the light player's pieces.
    """

    DARK_PATH: list[Tile] = Tile.create_path(
        (3, 5),
        (3, 1),
        (2, 1),
        (2, 12),
        (3, 12),
    )
    """
    The path of the dark player's pieces.
    """

    def __init__(self):
        super().__init__(
            AsebPathPair.NAME,
            AsebPathPair.LIGHT_PATH,
            AsebPathPair.DARK_PATH
        )


class BellPathPair(PathPair):
    """
    The paths proposed by Bell for the Royal Game of Ur.

    Citation: R.C. Bell, Board and Table Games From Many
    Civilizations, revised ed., Vol. 1 and 2, Dover
    Publications, Inc., New York, 1979.
    """
    __slots__ = ()

    NAME: str = "Bell"
    """
    The name of this type of path pair.
    """

    LIGHT_PATH: list[Tile] = Tile.create_path(
        (1, 5),
        (1, 1),
        (2, 1),
        (2, 8),
        (1, 8),
        (1, 6),
    )
    """
    The path of the light player's pieces.
    """

    DARK_PATH: list[Tile] = Tile.create_path(
        (3, 5),
        (3, 1),
        (2, 1),
        (2, 8),
        (3, 8),
        (3, 6),
    )
    """
    The path of the dark player's pieces.
    """

    def __init__(self):
        super().__init__(
            BellPathPair.NAME,
            BellPathPair.LIGHT_PATH,
            BellPathPair.DARK_PATH
        )


class MastersPathPair(PathPair):
    """
    The paths proposed by Masters for the Royal Game of Ur.

    Citation: J. Masters, The Royal Game of Ur &amp; The
    Game of 20 Squares (2021). Available at
    https://www.tradgames.org.uk/games/Royal-Game-Ur.htm.
    """
    __slots__ = ()

    NAME: str = "Masters"
    """
    The name of this type of path pair.
    """

    LIGHT_PATH: list[Tile] = Tile.create_path(
        (1, 5),
        (1, 1),
        (2, 1),
        (2, 7),
        (3, 7),
        (3, 8),
        (1, 8),
        (1, 6),
    )
    """
    The path of the light player's pieces.
    """

    DARK_PATH: list[Tile] = Tile.create_path(
        (3, 5),
        (3, 1),
        (2, 1),
        (2, 7),
        (1, 7),
        (1, 8),
        (3, 8),
        (3, 6),
    )
    """
    The path of the dark player's pieces.
    """

    def __init__(self):
        super().__init__(
            MastersPathPair.NAME,
            MastersPathPair.LIGHT_PATH,
            MastersPathPair.DARK_PATH
        )


class MurrayPathPair(PathPair):
    """
    The paths proposed by Murray for the Royal Game of Ur.

    Citation: H.J.R. Murray, A History of Board-games
    Other Than Chess, Oxford University Press, Oxford, 1952.
    """
    __slots__ = ()

    NAME: str = "Murray"
    """
    The name of this type of path pair.
    """

    LIGHT_PATH: list[Tile] = Tile.create_path(
        (1, 5),
        (1, 1),
        (2, 1),
        (2, 7),
        (3, 7),
        (3, 8),
        (1, 8),
        (1, 7),
        (2, 7),
        (2, 1),
        (3, 1),
        (3, 5),
    )
    """
    The path of the light player's pieces.
    """

    DARK_PATH: list[Tile] = Tile.create_path(
        (3, 5),
        (3, 1),
        (2, 1),
        (2, 7),
        (1, 7),
        (1, 8),
        (3, 8),
        (3, 7),
        (2, 7),
        (2, 1),
        (1, 1),
        (1, 5),
    )
    """
    The path of the dark player's pieces.
    """

    def __init__(self):
        super().__init__(
            MurrayPathPair.NAME,
            MurrayPathPair.LIGHT_PATH,
            MurrayPathPair.DARK_PATH
        )


class SkiriukPathPair(PathPair):
    """
    The paths proposed by Skiriuk for the Royal Game of Ur.

    Citation: D. Skiriuk, The rules of royal game of ur (2021).
    Available at https://skyruk.livejournal.com/231444.html.
    """
    __slots__ = ()

    NAME: str = "Skiriuk"
    """
    The name of this type of path pair.
    """

    LIGHT_PATH: list[Tile] = Tile.create_path(
        (1, 5),
        (1, 1),
        (2, 1),
        (2, 7),
        (3, 7),
        (3, 8),
        (1, 8),
        (1, 7),
        (2, 7),
        (2, 0),
    )
    """
    The path of the light player's pieces.
    """

    DARK_PATH: list[Tile] = Tile.create_path(
        (3, 5),
        (3, 1),
        (2, 1),
        (2, 7),
        (1, 7),
        (1, 8),
        (3, 8),
        (3, 7),
        (2, 7),
        (2, 0),
    )
    """
    The path of the dark player's pieces.
    """

    def __init__(self):
        super().__init__(
            SkiriukPathPair.NAME,
            SkiriukPathPair.LIGHT_PATH,
            SkiriukPathPair.DARK_PATH
        )


class PathType(Enum):
    """
    The type of path to use in a game.
    """

    BELL = (1, BellPathPair.NAME, lambda: BellPathPair())
    """
    The path proposed by Bell for the Royal Game of Ur.
    """

    ASEB = (2, AsebPathPair.NAME, lambda: AsebPathPair())
    """
    The standard path used for Aseb.
    """

    MASTERS = (3, MastersPathPair.NAME, lambda: MastersPathPair())
    """
    The path proposed by Masters for the Royal Game of Ur.
    """

    MURRAY = (4, MurrayPathPair.NAME, lambda: MurrayPathPair())
    """
    The path proposed by Murray for the Royal Game of Ur.
    """

    SKIRIUK = (5, SkiriukPathPair.NAME, lambda: SkiriukPathPair())
    """
    The path proposed by Skiriuk for the Royal Game of Ur.
    """

    def __init__(
            self,
            value: int,
            text_name: str,
            create_path_pair: Callable[[], PathPair]
    ):
        self._value_ = value
        self._text_name = text_name
        self._create_path_pair = create_path_pair

    @property
    def text_name(self) -> str:
        """
        The name of these paths.
        """
        return self._text_name

    def create_path_pair(self) -> PathPair:
        """
        Create an instance of the paths.
        """
        return self._create_path_pair()
