from .tile import Tile
from .path import BellPathPair, AsebPathPair
from enum import Enum
from typing import Iterable, Callable


class BoardShape:
    """
    Holds the shape of a board as a grid, and includes
    the location of all rosette tiles.
    """
    __slots__ = ("_name", "_tiles", "_rosettes", "_width", "_height")

    _name: str
    _tiles: set[Tile]
    _rosettes: set[Tile]
    _width: int
    _height: int

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
                raise ValueError(
                    f"Rosette at {rosette} does not exist on the board"
                )

        self._name = name
        self._tiles = tiles
        self._rosettes = rosettes

        x_values = [tile._x for tile in tiles]
        y_values = [tile._y for tile in tiles]

        min_x = min(x_values)
        min_y = min(y_values)
        if min_x != 1 or min_y != 1:
            raise ValueError(
                f"The board shape must be translated such that it has tiles "
                f"at an x-coordinate of 1, and at a y-coordinate of 1. "
                f"Minimum X = {min_x}, Minimum Y = {min_y}"
            )

        self._width = max(x_values)
        self._height = max(y_values)

    @property
    def name(self) -> str:
        """
        The name of this board shape.
        """
        return self._name

    @property
    def tiles(self) -> set[Tile]:
        """
        The set of tiles that fall within the bounds of this board shape.
        """
        return self._tiles

    @property
    def rosettes(self) -> set[Tile]:
        """
        The set of tiles that represent rosette tiles in this board shape.
        """
        return self._rosettes

    @property
    def width(self) -> int:
        """
        The number of x-coordinates that exist in this board shape.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        The number of y-coordinates that exist in this board shape.
        """
        return self._height

    @property
    def area(self) -> int:
        """
        The number of tiles contained in this board shape.
        """
        return len(self._tiles)

    def contains(self, tile: Tile) -> bool:
        """
        Determines whether the given tile falls within this board shape.
        """
        return tile in self._tiles

    def contains_indices(self, ix: int, iy: int) -> bool:
        """
        Determines whether the tile at indices (ix, iy),
        0-based, falls within the bounds of this shape of board.
        """
        if ix < 0 or iy < 0 or ix >= self._width or iy >= self._height:
            return False
        return self.contains(Tile.from_indices(ix, iy))

    def contains_all(self, tiles: Iterable[Tile]) -> bool:
        """
        Determines whether all provided tiles fall
        within this board shape.
        """
        for tile in tiles:
            if not self.contains(tile):
                return False
        return True

    def is_rosette(self, tile: Tile) -> bool:
        """
        Determines whether the given tile is a rosette
        tile in this board shape.
        """
        return tile in self._rosettes

    def is_rosette_indices(self, ix: int, iy: int) -> bool:
        """
        Determines whether the tile at the indices (ix, iy), 0-based,
        is a rosette tile in this board shape.
        """
        if ix < 0 or iy < 0 or ix >= self._width or iy >= self._height:
            return False
        return self.isRosette(Tile.from_indices(ix, iy))

    def is_equivalent(self, other: 'BoardShape') -> bool:
        """
        Determines whether this board shape covers the same tiles,
        and has the same rosettes, as other. This does not check
        that the names of the board shapes are the same.
        """
        return self._tiles == other._tiles \
            and self._rosettes == other._rosettes

    def __eq__(self, other: 'BoardShape') -> bool:
        if type(other) is not type(self):
            return False
        return self.is_equivalent(other) and self._name == other._name


class AsebBoardShape(BoardShape):
    """
    The shape of the board used for the game Aseb.
    This board shape consists of 3 rows. The first row contains
    4 tiles, the second row contains 12 tiles, and the third
    also contains 4 tiles.
    """
    __slots__ = ()

    NAME: str = "Aseb"
    """
    The name given to this board shape.
    """

    BOARD_TILES: set[Tile] = (
        set(AsebPathPair.LIGHT_PATH[1:-1])
        .union(set(AsebPathPair.DARK_PATH[1:-1]))
    )
    """
    The set of all tiles that exist on the board.
    """

    ROSETTE_TILES: set[Tile] = {
        Tile(1, 1),
        Tile(3, 1),
        Tile(2, 4),
        Tile(2, 8),
        Tile(2, 12)
    }
    """
    The set of rosette tiles that exist on the board.
    """

    def __init__(self):
        super().__init__(
            AsebBoardShape.NAME,
            AsebBoardShape.BOARD_TILES,
            AsebBoardShape.ROSETTE_TILES
        )


class StandardBoardShape(BoardShape):
    """
    The standard shape of board used for The Royal Game of Ur that
    follows the game boards that were excavated by Sir Leonard Woolley.
    """
    __slots__ = ()

    NAME: str = "Standard"
    """
    The name given to this board shape.
    """

    BOARD_TILES: set[Tile] = (
        set(BellPathPair.LIGHT_PATH[1:-1])
        .union(set(BellPathPair.DARK_PATH[1:-1]))
    )
    """
    The set of all tiles that exist on the board.
    """

    ROSETTE_TILES: set[Tile] = {
        Tile(1, 1),
        Tile(3, 1),
        Tile(2, 4),
        Tile(1, 7),
        Tile(3, 7)
    }
    """
    The set of rosette tiles that exist on the board.
    """

    def __init__(self):
        super().__init__(
            StandardBoardShape.NAME,
            StandardBoardShape.BOARD_TILES,
            StandardBoardShape.ROSETTE_TILES
        )


class BoardType(Enum):
    """
    The type of board to use in a game.
    """

    STANDARD = (1, StandardBoardShape.NAME, lambda: StandardBoardShape())
    """
    The standard board shape.
    """

    ASEB = (2, AsebBoardShape.NAME, lambda: AsebBoardShape())
    """
    The Aseb board shape.
    """

    def __init__(
            self,
            value: int,
            text_name: str,
            create_board_shape: Callable[[], BoardShape]
    ):
        self._value_ = value
        self._text_name = text_name
        self._create_board_shape = create_board_shape

    @property
    def text_name(self) -> str:
        """
        The name of this board shape.
        """
        return self._text_name

    def create_board_shape(self) -> BoardShape:
        """
        Create an instance of the board shape.
        """
        return self._create_board_shape()
