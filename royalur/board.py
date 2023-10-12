from .model import Tile, PlayerType
from .shape import BoardShape
from typing import Optional


class Piece:
    """
    A piece on a board.
    """

    owner: PlayerType
    """
    The player that owns this piece.
    """

    path_index: int
    """
    The index of the piece on its owner player's path.
    """

    def __init__(self, owner: PlayerType, path_index: int):
        if path_index < 0:
            raise ValueError(f"The path index cannot be negative: {path_index}")

        self.owner = owner
        self.path_index = path_index

    def __hash__(self) -> int:
        return hash((self.owner, self.path_index))

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False

        return self.owner == other.owner \
            and self.path_index == other.path_index

    @staticmethod
    def to_char(piece: Optional['Piece']) -> str:
        """
        Converts the given piece to a single character that can be used
        to textually represent the owner of a piece.
        """
        return PlayerType.to_char(piece.owner if piece is not None else None)


class Move:
    """
    A move that can be made on a board.
    """

    player: PlayerType
    """
    The instigator of this move.
    """

    source: Optional[Tile]
    """
    The origin of the move. If this is None, it represents
    that this move is introducing a new piece to the board.
    """

    source_piece: Optional[Piece]
    """
    The piece on the board to be moved, or None if this move
    is introducing a new piece to the board.
    """

    dest: Optional[Tile]
    """
    The destination of the move. If this is None, it represents
    that this move is scoring a piece.
    """

    dest_piece: Optional[Piece]
    """
    The piece to be placed at the destination, or None if
    this move is scoring a piece.
    """

    captured_piece: Optional[Piece]
    """
    The piece that will be captured by this move, or None if
    this move does not capture a piece.
    """

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
            raise ValueError("source and source_piece must either be both null, or both non-null")
        if (dest is None) != (dest_piece is None):
            raise ValueError("dest and dest_piece must either be both null, or both non-null")
        if dest is None and captured_piece is not None:
            raise ValueError("Moves without a destination cannot have captured a piece")

        self.player = player
        self.source = source
        self.source_piece = source_piece
        self.dest = dest
        self.dest_piece = dest_piece
        self.captured_piece = captured_piece

    def has_source(self) -> bool:
        """
        Determines whether this move is moving a piece on the board.
        """
        return self.source is not None

    def is_introducing_piece(self) -> bool:
        """
        Determines whether this move is moving a new piece onto the board.
        """
        return self.source is None

    def has_dest(self) -> bool:
        """
        Determines whether this moves a piece to a destination on the board.
        """
        return self.dest is not None

    def is_scoring_piece(self) -> bool:
        """
        Determines whether this move is moving a piece off of the board.
        """
        return self.dest is None

    def is_capture(self) -> bool:
        """
        Determines whether this move is capturing an existing piece on the board.
        """
        return self.captured_piece is not None

    def is_dest_rosette(self, shape: BoardShape) -> bool:
        """
        Determines whether this move will land a piece on a rosette. Under common
        rule sets, this will give another turn to the player.
        """
        return self.dest is not None and shape.is_rosette(self.dest)

    def get_source(self) -> Tile:
        """
        Gets the source piece of this move. If there is no source piece, in the
        case where a new piece is moved onto the board, this will throw an error.
        """
        if self.source is None:
            raise RuntimeError("This move has no source, as it is introducing a piece")

        return self.source

    def get_source_piece(self) -> Piece:
        """
        Gets the source piece of this move. If there is no source piece, in the
        case where a new piece is moved onto the board, this will throw an error.
        """
        if self.source_piece is None:
            raise RuntimeError("This move has no source, as it is introducing a piece")

        return self.source_piece

    def get_dest(self) -> Tile:
        """
        Gets the destination tile of this move. If there is no destination tile,
        in the case where a piece is moved off the board, this will throw an error.
        """
        if self.dest is None:
            raise RuntimeError("This move has no destination, as it is scoring a piece")

        return self.dest

    def get_dest_piece(self) -> Piece:
        """
        Gets the destination piece of this move. If there is no destination piece,
        in the case where a piece is moved off the board, this will throw an error.
        """
        if self.dest_piece is None:
            raise RuntimeError("This move has no destination, as it is scoring a piece")

        return self.dest_piece

    def get_captured_piece(self) -> Piece:
        """
        Gets the piece that will be captured by this move. If there is no piece
        that will be captured, this will throw an error.
        """
        if self.captured_piece is None:
            raise RuntimeError("This move does not capture a piece");

        return self.captured_piece

    def apply(self):
        # TODO : Need a Board implementation first
        pass

    def describe(self) -> str:
        """
        Generates an English description of this move.
        """
        scoring = self.is_scoring_piece()
        introducing = self.is_introducing_piece()

        if scoring and introducing:
            return "Introduce and score a piece."

        if scoring:
            return f"Score a piece from {self.get_source()}."

        builder = []
        if introducing:
            builder.append("Introduce a piece to ")
        else:
            builder.append(f"Move {self.get_source()} to ")

        if self.is_capture():
            builder.append("capture ")

        builder.append(f"{self.get_dest()}.")
        return "".join(builder)

    def __hash__(self) -> int:
        return hash((
            self.source, self.source_piece,
            self.dest, self.dest_piece,
            self.captured_piece
        ))

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False

        return self.source == other.source and self.source_piece == other.source_piece \
            and self.dest == other.dest and self.dest_piece == other.dest_piece \
            and self.captured_piece == other.captured_piece
