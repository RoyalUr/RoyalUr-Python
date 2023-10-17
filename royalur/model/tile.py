

class Tile:
    """
    Represents a position on or off the board.
    """
    __slots__ = ("_x", "_y", "_ix", "_iy")

    _x: int
    _y: int
    _ix: int
    _iy: int

    def __init__(self, x: int, y: int):
        if x < 1 or x > 26:
            raise ValueError(
                f"x must fall within the range [1, 26]. Invalid value: {x}"
            )
        if y < 0:
            raise ValueError(
                f"y must not be negative. Invalid value: {y}"
            )

        self._x = x
        self._y = y
        self._ix = x - 1
        self._iy = y - 1

    @property
    def x(self) -> int:
        """
        The x-coordinate of the tile. This coordinate is 1-based.
        """
        return self._x

    @property
    def y(self) -> int:
        """
        The y-coordinate of the tile. This coordinate is 1-based.
        """
        return self._y

    @property
    def ix(self) -> int:
        """
        The x-index of the tile. This coordinate is 0-based.
        """
        return self._ix

    @property
    def iy(self) -> int:
        """
        The y-index of the tile. This coordinate is 0-based.
        """
        return self._iy

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
        dx = other._x - self._x
        dy = other._y - self._y

        if abs(dx) + abs(dy) <= 1:
            return other

        if abs(dx) < abs(dy):
            return Tile(self._x, self._y + (1 if dy > 0 else -1))
        else:
            return Tile(self._x + (1 if dx > 0 else -1), self._y)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False

        return self._x == other._x and self._y == other._y

    def __repr__(self) -> str:
        encoded_x = chr(self._x + (ord('A') - 1))
        return f"{encoded_x}{self._y}"

    def __str__(self) -> str:
        return repr(self)

    @staticmethod
    def from_string(encoded: str) -> 'Tile':
        """
        Decodes the tile coordinates from its encoded text (e.g., A4).
        """
        if len(encoded) < 2:
            raise ValueError(
                "Incorrect format, expected at least two characters"
            )

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
        waypoints = Tile.create_list(*coordinates)
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
