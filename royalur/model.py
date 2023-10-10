from typing import Iterable


from enum import Enum
from typing import Optional

class PlayerType(Enum):
    """
    Represents the players of a game.
    """
    LIGHT = (1, "Light", 'L')
    DARK = (2, "Dark", 'D')

    def __init__(self, value: int, name: str, character: str):
        self._value_ = value
        self.name = name
        self.character = character

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
        Convert the player to a single character.
        """
        return player.character if player else '.'


class Tile:
    """
    Represents a position on or off the board.
    """

    x: int
    """
    The x-coordinate of the tile. This coordinate is 1-based.
    """

    y: int
    """
    The y-coordinate of the tile. This coordinate is 1-based.
    """

    ix: int
    """
    The x-index of the tile. This coordinate is 0-based.
    """

    iy: int
    """
    The y-index of the tile. This coordinate is 0-based.
    """

    def __init__(self, x: int, y: int):
        if x < 1 or x > 26:
            raise ValueError(f"x must fall within the range [1, 26]. Invalid value: {x}")
        if y < 0:
            raise ValueError(f"y must not be negative. Invalid value: {y}");

        self.x = x
        self.y = y
        self.ix = x - 1
        self.iy = y - 1

    @staticmethod
    def from_indices(ix: int, iy: int) -> 'Tile':
        """
        Creates a new tile representing the tile at the
        indices (ix, iy), 0-based.
        """
        return Tile(ix + 1, iy + 1)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tile):
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        encoded_x = chr(self.x + (ord('A') - 1))
        return f"{encoded_x}{self.y}"

    def __str__(self) -> str:
        return repr(self)

    @staticmethod
    def from_string(encoded: str) -> 'Tile':
        """
        Decodes the tile coordinates from its encoded text (e.g., A4).
        """
        if len(encoded) < 2:
            raise ValueError("Incorrect format, expected at least two characters")

        x = ord(encoded[0]) - (ord('A') - 1)
        y = int(encoded[1:])
        return Tile(x, y)


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
        if not isinstance(other, PathPair):
            return False
        return self.name == other.name \
            and self.lightWithStartEnd == other.lightWithStartEnd \
            and self.darkWithStartEnd == other.darkWithStartEnd


class BoardShape:
    """
    Holds the shape of a board as a grid, and includes the location of all rosette tiles.
    """
    name: str
    tiles: set[Tile]
    rosettes: set[Tile]
    width: int
    height: int

    def __init__(
            self,
            name: str,
            tiles: set[Tile],
            rosettes: set[Tile]
    ):

        if len(tiles) == 0:
            raise ValueError("A board shape requires at least one tile")

        for rosette in rosettes:
            if rosette not in tiles:
                raise ValueError(f"Rosette at {rosette} does not exist on the board")

        self.name = name
        self.tiles = tiles
        self.rosettes = rosettes

        x_values = [tile.x for tile in tiles]
        y_values = [tile.y for tile in tiles]

        min_x = min(x_values)
        min_y = min(y_values)
        if min_x != 1 or min_y != 1:
            raise ValueError(
                f"The board shape must be translated such that it has tiles "
                f"at an x-coordinate of 1, and at a y-coordinate of 1. "
                f"Minimum X = {min_x}, Minimum Y = {min_y}"
            )

        self.width = max(x_values)
        self.height = max(y_values)

    @property
    def area(self) -> int:
        return self.width * self.height

    def contains(self, tile: Tile) -> bool:
        return tile in self.tiles

    def contains_indices(self, ix: int, iy: int) -> bool:
        if ix < 0 or iy < 0 or ix >= self.width or iy >= self.height:
            return False
        return self.contains(Tile.from_indices(ix, iy))

    def contains_all(self, tiles: Iterable[Tile]) -> bool:
        for tile in tiles:
            if not self.contains(tile):
                return False
        return True

    def is_rosette(self, tile: Tile) -> bool:
        return tile in self.rosettes

    def is_rosette_indices(self, ix: int, iy: int) -> bool:
        if ix < 0 or iy < 0 or ix >= self.width or iy >= self.height:
            return False
        return self.isRosette(Tile.from_indices(ix, iy))

    def is_equivalent(self, other: 'BoardShape') -> bool:
        """
        Determines whether this board shape covers the same tiles,
        and has the same rosettes, as other. This does not check
        that the names of the board shapes are the same.
        """
        return self.tiles == other.tiles and self.rosettes == other.rosettes

    def __eq__(self, other: 'BoardShape') -> bool:
        if not isinstance(other, BoardShape):
            return False
        return self.is_equivalent(other) and self.name == other.name


class AsebBoardShape(BoardShape):
    """
    The shape of the board used for the game Aseb.
    This board shape consists of 3 rows. The first row contains
    4 tiles, the second row contains 12 tiles, and the third
    also contains 4 tiles.
    """
    pass

