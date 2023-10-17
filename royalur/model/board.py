from .tile import Tile
from .player import PlayerType
from .shape import BoardShape
from .path import PathPair
from typing import Optional, Union


class Piece:
    """
    A piece on a board.
    """
    __slots__ = ("_owner", "_path_index")

    _owner: PlayerType
    _path_index: int

    def __init__(self, owner: PlayerType, path_index: int):
        """
        Initializes a new Piece instance with the given owner and path index.

        Parameters:
            owner (PlayerType): The player that owns this piece.
            path_index (int):
                The index of the piece on its owner's path.
                Must be non-negative.

        Raises:
            ValueError: If the provided path_index is negative.
        """
        if path_index < 0:
            raise ValueError(
                f"The path index cannot be negative: {path_index}"
            )

        self._owner = owner
        self._path_index = path_index

    @property
    def owner(self) -> PlayerType:
        """
        The player that owns this piece.
        """
        return self._owner

    @property
    def path_index(self) -> int:
        """
        The index of the piece on its owner player's path.
        """
        return self._path_index

    def __hash__(self) -> int:
        return hash((self._owner, self._path_index))

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False

        return self._owner == other._owner \
            and self._path_index == other._path_index

    @staticmethod
    def to_char(piece: Optional['Piece']) -> str:
        """
        Converts the given piece to a single character that can be used
        to textually represent the owner of a piece.
        """
        return PlayerType.to_char(piece.owner if piece is not None else None)


class Board:
    """
    Stores the placement of pieces on the tiles of a Royal Game of Ur board.
    """
    __slots__ = ("_shape", "_width", "_height", "_pieces")

    _shape: BoardShape
    _width: int
    _height: int
    _pieces: list[Optional[Piece]]

    def __init__(
            self, board_or_shape: Union[BoardShape, 'Board']
    ):
        if isinstance(board_or_shape, BoardShape):
            shape = board_or_shape
        else:
            shape = board_or_shape.shape

        self._shape = shape
        self._width = shape.width
        self._height = shape.height

        if isinstance(board_or_shape, Board):
            self._pieces = [*board_or_shape._pieces]
        else:
            self._pieces = [None for _ in range(self._width * self._height)]

    def copy(self) -> 'Board':
        """
        Creates an exact copy of this board.
        """
        return Board(self)

    def _calc_tile_index(self, ix: int, iy: int) -> int:
        """
        We use a 1d array for storing pieces. This converts
        from 2d indices into an index to access that 1d array.
        """
        if ix < 0 or iy < 0 or ix >= self._width or iy >= self._height:
            raise ValueError(f"There is no tile at the indices ({ix}, {iy})")

        return iy * self._width + ix

    @property
    def shape(self) -> BoardShape:
        """
        The shape of this board.
        """
        return self._shape

    @property
    def width(self) -> int:
        """
        The width of this board.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        The height of this board.
        """
        return self._height

    def contains(self, tile: Tile) -> bool:
        """
        Determines whether the given tile falls
        within the bounds of this board.
        """
        return self._shape.contains(tile)

    def contains_indices(self, ix: int, iy: int) -> bool:
        """
        Determines whether the tile at the indices (ix, iy),
        0-based, falls within the bounds of this board.
        """
        return self._shape.contains_indices(ix, iy)

    def get(self, tile: Tile) -> Optional[Piece]:
        """
        Gets the piece on the given tile. Returns None if there
        is no piece on the tile.
        """
        if not self._shape.contains(tile):
            raise ValueError(f"There is no tile at {tile}")

        index = self._calc_tile_index(tile.ix, tile.iy)
        return self._pieces[index]

    def get_by_indices(self, ix: int, iy: int) -> Optional[Piece]:
        """
        Gets the piece on the tile at the indices (ix, iy), 0-based.
        Returns None if there is no piece on the tile.
        """
        if not self._shape.contains_indices(ix, iy):
            raise ValueError(f"There is no tile at the indices ({ix}, {iy})")

        index = self._calc_tile_index(ix, iy)
        return self._pieces[index]

    def set(self, tile: Tile, piece: Optional[Piece]) -> Optional[Piece]:
        """
        Sets the piece on the given tile to the provided piece. If the
        provided piece is None, it removes any piece on the tile. Returns
        the piece that was previously on the tile, or None if there was no
        piece on the tile.
        """
        if not self._shape.contains(tile):
            raise ValueError(f"There is no tile at {tile}")

        index = self._calc_tile_index(tile.ix, tile.iy)
        previous = self._pieces[index]
        self._pieces[index] = piece
        return previous

    def set_by_indices(
            self,
            ix: int,
            iy: int,
            piece: Optional[Piece]
    ) -> Optional[Piece]:
        """
        Sets the piece on the tile at the indices (ix, iy), 0-based,
        to the provided piece. If the provided piece is None, it removes
        any piece on the tile. Returns the piece that was previously
        on the tile, or None if there was no piece on the tile.
        """
        if not self._shape.contains_indices(ix, iy):
            raise ValueError(f"There is no tile at the indices ({ix}, {iy})")

        index = self._calc_tile_index(ix, iy)
        previous = self._pieces[index]
        self._pieces[index] = piece
        return previous

    def clear(self):
        """
        Removes all pieces from this board.
        """
        for index in range(len(self._pieces)):
            self._pieces[index] = None

    def count_pieces(self, player: PlayerType) -> int:
        """
        Counts the number of pieces that are on the board
        for the given player.
        """
        piece_count = 0
        for piece in self._pieces:
            if piece is not None and piece.owner == player:
                piece_count += 1

        return piece_count

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False

        return self._shape == other._shape \
            and self._pieces == other._pieces

    def to_string(
            self,
            column_delimiter: str = "\n",
            include_off_board_tiles: bool = True
    ):
        """
        Writes the contents of this board into a String, where
        each column is separated by a delimiter.
        """
        builder = []
        for ix in range(self._width):
            if ix > 0:
                builder.append(column_delimiter)

            for iy in range(self._height):
                if self._shape.contains_indices(ix, iy):
                    piece = self.get_by_indices(ix, iy)
                    builder.append(Piece.to_char(piece))

                elif include_off_board_tiles:
                    builder.append(" ")

        return "".join(builder)

    def __repr__(self) -> str:
        return self.to_string()


class Move:
    """
    A move that can be made on a board.
    """
    __slots__ = (
        "_player", "_source", "_source_piece",
        "_dest", "_dest_piece", "_captured_piece"
    )

    _player: PlayerType
    _source: Optional[Tile]
    _source_piece: Optional[Piece]
    _dest: Optional[Tile]
    _dest_piece: Optional[Piece]
    _captured_piece: Optional[Piece]

    def __init__(
            self,
            player: PlayerType,
            source: Optional[Tile],
            source_piece: Optional[Piece],
            dest: Optional[Tile],
            dest_piece: Optional[Piece],
            captured_piece: Optional[Piece],
    ):
        if (source is None) != (source_piece is None):
            raise ValueError(
                "source and source_piece must either "
                "be both null, or both non-null"
            )
        if (dest is None) != (dest_piece is None):
            raise ValueError(
                "dest and dest_piece must either be both null, "
                "or both non-null"
            )
        if dest is None and captured_piece is not None:
            raise ValueError(
                "Moves without a destination "
                "cannot have captured a piece"
            )

        self._player = player
        self._source = source
        self._source_piece = source_piece
        self._dest = dest
        self._dest_piece = dest_piece
        self._captured_piece = captured_piece

    @property
    def player(self) -> PlayerType:
        """
        The instigator of this move.
        """
        return self._player

    @property
    def source(self) -> Optional[Tile]:
        """
        The origin of the move. If this is None, it represents
        that this move is introducing a new piece to the board.
        """
        return self._source

    @property
    def source_piece(self) -> Optional[Piece]:
        """
        The piece on the board to be moved, or None if this move
        is introducing a new piece to the board.
        """
        return self._source_piece

    @property
    def dest(self) -> Optional[Tile]:
        """
        The destination of the move. If this is None, it represents
        that this move is scoring a piece.
        """
        return self._dest

    @property
    def dest_piece(self) -> Optional[Piece]:
        """
        The piece to be placed at the destination, or None if
        this move is scoring a piece.
        """
        return self._dest_piece

    @property
    def captured_piece(self) -> Optional[Piece]:
        """
        The piece that will be captured by this move, or None if
        this move does not capture a piece.
        """
        return self._captured_piece

    def has_source(self) -> bool:
        """
        Determines whether this move is moving a piece on the board.
        """
        return self._source is not None

    def is_introducing_piece(self) -> bool:
        """
        Determines whether this move is moving a new piece onto the board.
        """
        return self._source is None

    def has_dest(self) -> bool:
        """
        Determines whether this moves a piece to a destination on the board.
        """
        return self._dest is not None

    def is_scoring_piece(self) -> bool:
        """
        Determines whether this move is moving a piece off of the board.
        """
        return self._dest is None

    def is_capture(self) -> bool:
        """
        Determines whether this move is capturing an existing
        piece on the board.
        """
        return self._captured_piece is not None

    def is_dest_rosette(self, shape: BoardShape) -> bool:
        """
        Determines whether this move will land a piece on a
        rosette. Under common rule sets, this will give
        another turn to the player.
        """
        return self._dest is not None and shape.is_rosette(self._dest)

    def get_source(self, paths: PathPair | None = None) -> Tile:
        """
        Gets the source piece of this move. If there is no
        source piece, in the case where a new piece is moved
        onto the board, this will throw an error.
        """
        if self._source is None:
            if paths is not None:
                return paths.get_start(self._player)

            raise RuntimeError(
                "This move has no source, as it is introducing a piece"
            )

        return self._source

    def get_source_piece(self) -> Piece:
        """
        Gets the source piece of this move. If there is no
        source piece, in the case where a new piece is moved
        onto the board, this will throw an error.
        """
        if self._source_piece is None:
            raise RuntimeError(
                "This move has no source, as it is introducing a piece"
            )

        return self._source_piece

    def get_dest(self, paths: PathPair | None = None) -> Tile:
        """
        Gets the destination tile of this move. If there
        is no destination tile, in the case where a piece
        is moved off the board, this will throw an error.
        """
        if self._dest is None:
            if paths is not None:
                return paths.get_end(self._player)

            raise RuntimeError(
                "This move has no destination, as it is scoring a piece"
            )

        return self._dest

    def get_dest_piece(self) -> Piece:
        """
        Gets the destination piece of this move. If there
        is no destination piece, in the case where a piece
        is moved off the board, this will throw an error.
        """
        if self._dest_piece is None:
            raise RuntimeError(
                "This move has no destination, as it is scoring a piece"
            )

        return self._dest_piece

    def get_captured_piece(self) -> Piece:
        """
        Gets the piece that will be captured by this move.
        If there is no piece that will be captured, this
        will throw an error.
        """
        if self._captured_piece is None:
            raise RuntimeError("This move does not capture a piece")

        return self._captured_piece

    def apply(self, board: Board):
        """
        Apply this move to update the given board.
        """
        if self.source is not None:
            board.set(self.source, None)
        if self.dest is not None:
            board.set(self.dest, self.dest_piece)

    def describe(self) -> str:
        """
        Generates an English description of this move.
        """
        scoring = self.is_scoring_piece()
        introducing = self.is_introducing_piece()

        if scoring and introducing:
            return "Introduce and score a piece"

        if scoring:
            return f"Score a piece from {self.get_source()}"

        builder = []
        if introducing:
            builder.append("Introduce a piece to ")
        else:
            builder.append(f"Move {self.get_source()} to ")

        if self.is_capture():
            builder.append("capture ")

        builder.append(str(self.get_dest()))
        return "".join(builder)

    def __hash__(self) -> int:
        return hash((
            self._source, self._source_piece,
            self._dest, self._dest_piece,
            self._captured_piece
        ))

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False

        return self._source == other._source \
            and self._source_piece == other._source_piece \
            and self._dest == other._dest \
            and self._dest_piece == other._dest_piece \
            and self._captured_piece == other._captured_piece
