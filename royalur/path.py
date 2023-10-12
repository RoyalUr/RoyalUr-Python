from .model import Tile, PlayerType
from enum import Enum


class PathPair:
    """
    Represents a pair of paths for the light and dark players to
    move their pieces along in a game of the Royal Game of Ur.
    """

    name: str
    """
    The name of this path pair.
    """

    lightWithStartEnd: list[Tile]
    """
    The path that light players take around the board, including
    the start and end tiles that exist off the board.
    """

    darkWithStartEnd: list[Tile]
    """
    The path that darj players take around the board, including
    the start and end tiles that exist off the board.
    """

    light: list[Tile]
    """
    The path that light players take around the board, excluding
    the start and end tiles that exist off the board.
    """

    dark: list[Tile]
    """
    The path that darj players take around the board, excluding
    the start and end tiles that exist off the board.
    """

    lightStart: Tile
    """
    The start tile of the light player that exists off the board.
    """

    lightEnd: Tile
    """
    The end tile of the light player that exists off the board.
    """

    darkStart: Tile
    """
    The start tile of the dark player that exists off the board.
    """

    darkEnd: Tile
    """
    The end tile of the dark player that exists off the board.
    """

    def __init__(
            self,
            name: str,
            lightWithStartEnd: list[Tile],
            darkWithStartEnd: list[Tile],
    ):

        self.name = name
        self.lightWithStartEnd = [*lightWithStartEnd]
        self.darkWithStartEnd = [*darkWithStartEnd]
        self.light = self.lightWithStartEnd[1:-1]
        self.dark = self.darkWithStartEnd[1:-1]
        self.lightStart = lightWithStartEnd[0]
        self.lightEnd = lightWithStartEnd[-1]
        self.darkStart = darkWithStartEnd[0]
        self.darkEnd = darkWithStartEnd[-1]

    def get(self, player: PlayerType) -> list[Tile]:
        """
        Gets the path of the given player, excluding the start and
        end tiles that exist off the board.
        """
        if player == PlayerType.LIGHT:
            return self.light
        elif player == PlayerType.DARK:
            return self.dark
        else:
            raise ValueError(f"Unknown PlayerType {player}")

    def getWithStartEnd(self, player: PlayerType) -> list[Tile]:
        """
        Gets the path of the given player, including the start and
        end tiles that exist off the board.
        """
        if player == PlayerType.LIGHT:
            return self.lightWithStartEnd
        elif player == PlayerType.DARK:
            return self.darkWithStartEnd
        else:
            raise ValueError(f"Unknown PlayerType {player}")

    def getStart(self, player: PlayerType) -> list[Tile]:
        """
        Gets the start tile of the given player, which exists off the board.
        """
        if player == PlayerType.LIGHT:
            return self.lightStart
        elif player == PlayerType.DARK:
            return self.darkStart
        else:
            raise ValueError(f"Unknown PlayerType {player}")

    def getEnd(self, player: PlayerType) -> list[Tile]:
        """
        Gets the end tile of the given player, which exists off the board.
        """
        if player == PlayerType.LIGHT:
            return self.lightEnd
        elif player == PlayerType.DARK:
            return self.darkEnd
        else:
            raise ValueError(f"Unknown PlayerType {player}")

    def isEquivalent(self, other: 'PathPair') -> bool:
        """
        Determines whether this set of paths and other cover the same tiles,
        in the same order. This does not check the start and end tiles that
        exist off the board, or the name of the paths.
        """
        return self.light == other.light

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False

        return self.name == other.name \
            and self.lightWithStartEnd == other.lightWithStartEnd \
            and self.darkWithStartEnd == other.darkWithStartEnd


class AsebPathPair(PathPair):
    """
    The standard paths that are used for Aseb.

    Citation: W. Crist, A.E. Dunn-Vaturi, and A. de Voogt,
    Ancient Egyptians at Play: Board Games Across Borders,
    Bloomsbury Egyptology, Bloomsbury Academic, London, 2016.
    """

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

    Citation: R.C. Bell, Board and Table Games From Many Civilizations,
    revised ed., Vol. 1 and 2, Dover Publications, Inc., New York, 1979.
    """

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

    Citation: J. Masters, The Royal Game of Ur &amp; The Game of 20 Squares (2021).
    Available at https://www.tradgames.org.uk/games/Royal-Game-Ur.htm.
    """

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

    Citation: H.J.R. Murray, A History of Board-games Other Than Chess,
    Oxford University Press, Oxford, 1952.
    """

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
        super().__init__(SkiriukPathPair.NAME, SkiriukPathPair.LIGHT_PATH, SkiriukPathPair.DARK_PATH)


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

    def __init__(self, value: int, name: str, create_path_pair: callable[[], PathPair]):
        self._value_ = value
        self.name = name
        self.create_path_pair = create_path_pair
