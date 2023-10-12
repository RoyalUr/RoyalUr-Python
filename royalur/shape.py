from .model import Tile
from .path import BellPathPair, AsebPathPair
from enum import Enum
from typing import Iterable


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
        if type(other) is not type(self):
            return False
        return self.is_equivalent(other) and self.name == other.name


class AsebBoardShape(BoardShape):
    """
    The shape of the board used for the game Aseb.
    This board shape consists of 3 rows. The first row contains
    4 tiles, the second row contains 12 tiles, and the third
    also contains 4 tiles.
    """

    NAME: str = "Aseb"
    """
    The name given to this board shape.
    """

    BOARD_TILES: set[Tile] = set(AsebPathPair.LIGHT_PATH).union(set(AsebPathPair.DARK_PATH))
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

    NAME: str = "Standard"
    """
    The name given to this board shape.
    """

    BOARD_TILES: set[Tile] = set(BellPathPair.LIGHT_PATH).union(set(BellPathPair.DARK_PATH))
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

    def __init__(self, value: int, name: str, create_board_shape: callable[[], BoardShape]):
        self._value_ = value
        self.name = name
        self.create_board_shape = create_board_shape
