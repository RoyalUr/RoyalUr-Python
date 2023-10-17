from royalur.model import (
    Board, BoardShape, GameMetadata, GameSettings,
    Move, PathPair, Piece, Dice,
    PlayerType, PlayerState, Roll
)
from royalur.rules.state import (
    GameState,
    WaitingForRollGameState,
    WaitingForMoveGameState,
    RolledGameState,
    MovedGameState,
    WinGameState,
)
from royalur.rules.rules import (
    PieceProvider, PlayerStateProvider,
    RuleSet, RuleSetProvider,
)
from overrides import overrides
from typing import Callable


class SimplePieceProvider(PieceProvider):
    """
    Provides new instances of, and manipulations to, simple pieces.
    """
    __slots__ = ()

    @overrides
    def create_introduced(
            self,
            owner: PlayerType,
            new_path_index: int
    ) -> Piece:

        return Piece(owner, new_path_index)

    @overrides
    def create_moved(
            self,
            origin_piece: Piece,
            new_path_index: int
    ) -> Piece:

        return Piece(origin_piece.owner, new_path_index)


class SimplePlayerStateProvider(PlayerStateProvider):
    """
    Provides new instances of, and manipulations to, simple player states.
    """
    __slots__ = ("_starting_piece_count",)

    _starting_piece_count: int

    def __init__(self, starting_piece_count: int):
        super().__init__()
        self._starting_piece_count = starting_piece_count

    @overrides
    def get_starting_piece_count(self) -> int:
        return self._starting_piece_count

    @overrides
    def create(self, player: PlayerType):
        return PlayerState(player, self._starting_piece_count, 0)

    @overrides
    def apply_piece_introduced(self, player_state: PlayerState, piece: Piece):
        return PlayerState(
            player_state.player,
            player_state.piece_count - 1,
            player_state.score
        )

    @overrides
    def apply_piece_captured(self, player_state: PlayerState, piece: Piece):
        return PlayerState(
            player_state.player,
            player_state.piece_count + 1,
            player_state.score
        )

    @overrides
    def apply_piece_scored(self, player_state: PlayerState, piece: Piece):
        return PlayerState(
            player_state.player,
            player_state.piece_count,
            player_state.score + 1
        )


class SimpleRuleSet(RuleSet):
    """
    The most common, simple, rules of the Royal Game of Ur.
    This still allows a large range of custom rules.
    """
    __slots__ = (
        "_safe_rosettes",
        "_rosettes_grant_extra_rolls",
        "_captures_grant_extra_rolls"
    )

    _safe_rosettes: bool
    _rosettes_grant_extra_rolls: bool
    _captures_grant_extra_rolls: bool

    def __init__(
            self,
            board_shape: BoardShape,
            paths: PathPair,
            dice_factory: Callable[[], Dice],
            piece_provider: PieceProvider,
            player_state_provider: PlayerStateProvider,
            safe_rosettes: bool,
            rosettes_grant_extra_rolls: bool,
            captures_grant_extra_rolls: bool,
    ):
        super().__init__(
            board_shape, paths, dice_factory,
            piece_provider, player_state_provider
        )
        self._safe_rosettes = safe_rosettes
        self._rosettes_grant_extra_rolls = rosettes_grant_extra_rolls
        self._captures_grant_extra_rolls = captures_grant_extra_rolls

    @overrides
    def are_rosettes_safe(self) -> bool:
        return self._safe_rosettes

    @overrides
    def do_rosettes_grant_extra_rolls(self) -> bool:
        return self._rosettes_grant_extra_rolls

    @overrides
    def do_captures_grant_extra_rolls(self) -> bool:
        return self._captures_grant_extra_rolls

    @overrides
    def generate_initial_game_state(self) -> GameState:
        return WaitingForRollGameState(
            Board(self._board_shape),
            self._player_state_provider.create(PlayerType.LIGHT),
            self._player_state_provider.create(PlayerType.DARK),
            PlayerType.LIGHT,
        )

    @overrides
    def find_available_moves(
        self,
        board: Board,
        player: PlayerState,
        roll: Roll
    ) -> list[Move]:

        if roll.value == 0:
            return []

        player_type = player.player
        path = self._paths.get(player_type)
        moves = []

        # Check if a piece can be taken off the board.
        if roll.value <= len(path):
            score_path_index = len(path) - roll.value
            score_tile = path[score_path_index]
            score_piece = board.get(score_tile)
            if score_piece is not None \
                    and score_piece.owner == player_type \
                    and score_piece.path_index == score_path_index:

                moves.append(Move(
                    player_type, score_tile, score_piece,
                    None, None, None
                ))

        # Check for pieces on the board that can be moved
        # to another tile on the board.
        for path_index in range(-1, len(path) - roll.value):

            if path_index >= 0:
                # Move a piece on the board.
                tile = path[path_index]
                piece = board.get(tile)
                if piece is None \
                        or piece.owner != player_type \
                        or piece.path_index != path_index:
                    continue

            elif player.piece_count > 0:
                # Introduce a piece to the board.
                tile = None
                piece = None

            else:
                continue

            # Check if the destination is free.
            dest_path_index = path_index + roll.value
            dest = path[dest_path_index]
            dest_piece = board.get(dest)

            if dest_piece is not None:
                # Cannot capture your own piece.
                if dest_piece.owner == player_type:
                    continue

                # Can't capture pieces on rosettes if they are safe.
                if self._safe_rosettes and self._board_shape.is_rosette(dest):
                    continue

            # Generate the move.
            if path_index >= 0:
                moved_piece = self._piece_provider.create_moved(
                    piece, dest_path_index
                )
            else:
                moved_piece = self._piece_provider.create_introduced(
                    player_type, dest_path_index
                )

            moves.append(Move(
                player_type, tile, piece, dest, moved_piece, dest_piece
            ))

        return moves

    @overrides
    def apply_roll(
            self,
            state: WaitingForRollGameState,
            roll: Roll
    ) -> list[GameState]:

        available_moves = self.find_available_moves(
            state.board, state.get_turn_player(), roll
        )
        rolled_state = RolledGameState(
            state.board, state.light_player, state.dark_player,
            state.get_turn(), roll, available_moves
        )

        # Swap turn when rolling the player has no available moves.
        if len(available_moves) == 0:
            new_turn = state.get_turn().get_other_player()
            return [rolled_state, WaitingForRollGameState(
                state.board, state.light_player, state.dark_player, new_turn
            )]

        # The player has available moves.
        return [rolled_state, WaitingForMoveGameState(
            state.board, state.light_player, state.dark_player,
            state.get_turn(), roll, available_moves
        )]

    def should_grant_extra_roll(self, moved_state: MovedGameState) -> bool:
        """
        Determines whether the move represent by the given moved state
        should grant another roll to the player that made the move.
        """
        move = moved_state.move

        if self._rosettes_grant_extra_rolls \
                and move.is_dest_rosette(self._board_shape):

            return True

        return self._captures_grant_extra_rolls and move.is_capture()

    @overrides
    def apply_move(
            self,
            state: WaitingForMoveGameState,
            move: Move
    ) -> list[GameState]:

        # Generate the state representing the move that was made.
        moved_state = MovedGameState(
            state.board, state.light_player, state.dark_player,
            state.get_turn(), state.roll, move
        )

        # Apply the move to the board.
        board = state.board.copy()
        move.apply(board)

        # Apply the move to the player that made the move.
        turn_player = state.get_turn_player()

        if move.is_introducing_piece():
            introduced_piece = move.get_dest_piece()
            turn_player = self._player_state_provider.apply_piece_introduced(
                turn_player, introduced_piece
            )

        elif move.is_scoring_piece():
            scored_piece = move.get_source_piece()
            turn_player = self._player_state_provider.apply_piece_scored(
                turn_player, scored_piece
            )

        # Apply the effects of the move to the other player.
        other_player = state.get_waiting_player()
        if move.is_capture():
            captured_piece = move.get_captured_piece()
            other_player = self._player_state_provider.apply_piece_captured(
                other_player, captured_piece
            )

        # Determine which player is which.
        turn = turn_player.player
        light_player = (
            turn_player if turn == PlayerType.LIGHT else other_player
        )
        dark_player = (
            turn_player if turn == PlayerType.DARK else other_player
        )

        # Check if the player has won the game.
        turn_player_pieces = turn_player.piece_count
        if move.is_scoring_piece() \
                and turn_player_pieces + board.count_pieces(turn) <= 0:

            return [moved_state, WinGameState(
                board, light_player, dark_player, turn
            )]

        # Determine whose turn it will be in the next state.
        grant_extra_roll = self.should_grant_extra_roll(moved_state)
        next_turn = (turn if grant_extra_roll else turn.get_other_player())
        return [moved_state, WaitingForRollGameState(
            board, light_player, dark_player, next_turn
        )]


class SimpleRuleSetProvider(RuleSetProvider):
    """
    A provider that creates simple rule sets.
    """
    __slots__ = ()

    @overrides
    def create(
            self,
            settings: GameSettings,
            metadata: GameMetadata
    ) -> RuleSet:

        piece_provider = SimplePieceProvider()
        player_state_provider = SimplePlayerStateProvider(
            settings.starting_piece_count
        )
        return SimpleRuleSet(
            settings.board_shape,
            settings.paths,
            settings.dice,
            piece_provider,
            player_state_provider,
            settings.safe_rosettes,
            settings.rosettes_grant_extra_rolls,
            settings.captures_grant_extra_rolls
        )
