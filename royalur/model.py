import random
from enum import Enum
from typing import Optional, Iterable
from abc import ABC, abstractmethod
from overrides import overrides

from royalur.model import Roll


class PlayerType(Enum):
    """
    Represents the players of a game.
    """
    LIGHT = (1, "Light", 'L')
    """
    The light player.
    """

    DARK = (2, "Dark", 'D')
    """
    The dark player.
    """

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

    def step_towards(self, other: 'Tile') -> 'Tile':
        """
        Takes a unit length step towards the other tile.
        """
        dx = other.x - self.x
        dy = other.y - self.y

        if abs(dx) + abs(dy) <= 1:
            return other

        if abs(dx) < abs(dy):
            return Tile(self.x, self.y + (1 if dy > 0 else -1))
        else:
            return Tile(self.x + (1 if dx > 0 else -1), self.y)

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

    @staticmethod
    def create_list(*coordinates: list[tuple[int, int]]) -> list['Tile']:
        """
        Constructs a list of tiles from the tile coordinates.
        """
        return [Tile(x, y) for x, y in coordinates]

    @staticmethod
    def create_path(*coordinates: list[tuple[int, int]]) -> list['Tile']:
        """
        Constructs a path from waypoints on the board.
        """
        waypoints = Tile.create_list(coordinates)
        if len(waypoints) == 0:
            raise ValueError("No coordinates provided")

        path = [waypoints[0]]
        for index in range(1, len(waypoints)):
            current = waypoints[index - 1]
            next = waypoints[index]
            while current != next:
                current = current.step_towards(next)
                path.append(current)

        return path


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
    ASEB = (2, AsebPathPair.NAME, lambda: AsebPathPair())
    MASTERS = (3, MastersPathPair.NAME, lambda: MastersPathPair())
    MURRAY = (4, MurrayPathPair.NAME, lambda: MurrayPathPair())
    SKIRIUK = (5, SkiriukPathPair.NAME, lambda: SkiriukPathPair())

    def __init__(self, value: int, name: str, create_path_pair: callable[[], PathPair]):
        self._value_ = value
        self.name = name
        self.create_path_pair = create_path_pair


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


class Roll:
    """
    A roll of the dice.
    """

    value: int
    """
    The value of the dice that was rolled.
    """

    def __init__(self, value: int):
        self.value = value


class Dice(ABC):
    """
    A generator of dice rolls.
    """

    name: str
    """
    The name of this dice.
    """

    def __init__(self, name: str):
        self.name = name

    def has_state() -> bool:
        """
        Returns whether this dice holds any state that affects its dice rolls.
        If this is overriden, then copy_from should also be overriden.
        """
        return False

    def copy_from(self, other: 'Dice') -> bool:
        """
        Copies the state of the other dice into this dice. If the dice does
        not have state, this is a no-op.
        """
        pass

    @abstractmethod
    def get_max_roll_value(self) -> int:
        """
        Gets the maximum value that could be rolled by this dice.
        """
        pass

    @abstractmethod
    def get_roll_probabilities(self) -> list[float]:
        """
        Gets the probability of rolling each value of the dice, where the
        index into the returned array represents the value of the roll.
        """
        pass

    @abstractmethod
    def roll_value(self) -> int:
        """
        Generates a random roll using this dice, and returns just the value.
        If this dice has state, this should call record_roll.
        """
        pass

    def record_roll(self, value: int):
        """
        Updates the state of this dice after having rolled value.
        """
        pass

    @abstractmethod
    def generate_roll(self, value: int) -> Roll:
        """
        Generates a roll with the given value using this dice.
        """
        pass

    def roll(self) -> Roll:
        """
        Generates a random roll using this dice.
        """
        return self.generate_roll(self.roll_value())


class BinaryDice(Dice):
    """
    Rolls a number of binary die and counts the result.
    """

    num_die: int
    """
    The number of binary dice to roll.
    """

    roll_probabilities: list[float]
    """
    The probability of rolling each value with these dice.
    """

    def __init__(self, name: str, num_die: int):
        super().__init__(name)
        self.num_die = num_die
        self.roll_probabilities = []

        # Binomial Distribution
        baseProb = 0.5 ** num_die
        nChooseK = 1
        for roll in range(0, num_die + 1):
            self.roll_probabilities.append(baseProb * nChooseK)
            nChooseK = nChooseK * (num_die - roll) // (roll + 1)

    @overrides
    def get_max_roll_value(self) -> int:
        return self.num_die

    @overrides
    def get_roll_probabilities(self) -> list[float]:
        return self.roll_probabilities

    @overrides
    def roll_value(self) -> int:
        value = 0
        for _ in range(self.num_die):
            # Simulate rolling a single D2 dice.
            if random.random() >= 0.5:
                value += 1

        return value

    @overrides
    def generate_roll(self, value: int) -> Roll:
        if value < 0 or value > self.num_die:
            raise ValueError(f"This dice cannot roll {value}");

        return Roll(value)

