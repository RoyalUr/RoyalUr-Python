from .model import (
    GameMetadata, Dice, Roll,
    Board, Move, Piece, Tile,
    PlayerState, PlayerType,
)
from .rules import (
    RuleSet, GameState,
    ActionGameState,
    PlayableGameState,
    WaitingForRollGameState,
    WaitingForMoveGameState,
    MovedGameState,
    WinGameState,
)
from typing import Iterable


class Game:
    """
    A game of the Royal Game of Ur. Provides methods to allow the playing of games,
    and methods to support the retrieval of history about the moves that were made.
    """
    __slots__ = ("_rules", "_dice", "_metadata", "_states")

    _rules: RuleSet
    _dice: Dice
    _metadata: GameMetadata
    _states: list[GameState]

    def __init__(
            self,
            rules: RuleSet,
            metadata: GameMetadata | None = None,
            states: list[GameState] | None = None
    ):
        if metadata is None:
            metadata = GameMetadata.create_for_new_game(rules)
        if states is None:
            states = [rules.generate_initial_game_state()]

        if len(states) == 0:
            raise ValueError("Games must have at least one state")

        self._rules = rules
        self._metadata = metadata
        self._dice = rules.dice_factory()
        self._states = []

        self.add_states(states)

    def copy(self) -> 'Game':
        """
        Create an exact copy of this game.
        """
        if type(self) != Game:
            raise RuntimeError(f"{type(self)} does not support copy")

        new_game = Game(
            self._rules, self._metadata.copy(), self._states
        )
        new_game._dice.copy_from(self._dice)
        return new_game

    def add_states(self, states: Iterable[GameState]):
        """
        Adds all the given states to this game.
        """
        seen = 0
        for state in states:
            seen += 1
            self.add_state(state)

        if seen == 0:
            raise ValueError("There were no states to add")

    def add_state(self, state: GameState):
        """
        Adds the given state to this game.
        """
        self._states.append(state)

    @property
    def rules(self) -> RuleSet:
        """
        The set of rules that are being used for this game.
        """
        return self._rules

    @property
    def metadata(self) -> GameMetadata:
        """
        The metadata of this game.
        """
        return self._metadata

    @property
    def dice(self) -> Dice:
        """
        The dice to be used to make dice rolls.
        """
        return self._dice

    @property
    def states(self) -> list[GameState]:
        """
        The states that have occurred so far in the game.
        """
        return [*self._states]

    def get_current_state(self) -> GameState:
        """
        Gets the current state of the game.
        """
        return self._states[-1]

    def get_action_states(self) -> list[ActionGameState]:
        """
        Gets the states that represent the actions that have been
        made so far in the game. The last state in the list represents
        the last action that was taken in this game.
        """
        return [state for state in self._states if isinstance(state, ActionGameState)]

    def get_landmark_states(self) -> list[ActionGameState]:
        """
        Gets all moves that were made in the game, as well as
        the current state of the game. These states are considered
        landmark states as they contain all the information required
        to recreate everything that happened in the game so far.
        """
        return [
            state for index, state in enumerate(self._states)
            if isinstance(state, MovedGameState) or index == len(self._states) - 1
        ]

    def is_playable(self) -> bool:
        """
        Determines whether the game is currently in a playable state.
        """
        return isinstance(self.get_current_state(), PlayableGameState)

    def is_waiting_for_roll(self) -> bool:
        """
        Determines whether the game is currently waiting for a roll from a player.
        """
        return isinstance(self.get_current_state(), WaitingForRollGameState)

    def is_waiting_for_move(self) -> bool:
        """
        Determines whether the game is currently waiting for a move from a player.
        """
        return isinstance(self.get_current_state(), WaitingForMoveGameState)

    def is_finished(self) -> bool:
        """
        Determines whether the game is currently in a finished state.
        """
        return isinstance(self.get_current_state(), WinGameState)

    def get_current_playable_state(self) -> PlayableGameState:
        """
        Gets the current state of this game as a PlayableGameState.
        This will throw an error if the game is not in a playable state.
        """
        state = self.get_current_state()
        if not isinstance(state, PlayableGameState):
            raise RuntimeError("This game is not in a playable state")

        return state

    def get_current_waiting_for_roll_state(self) -> WaitingForRollGameState:
        """
        Gets the current state of this game as an instance of WaitingForRollGameState.
        This will throw an error if the game is not waiting for a roll from a player.
        """
        state = self.get_current_state()
        if not isinstance(state, WaitingForRollGameState):
            raise RuntimeError("This game is not in a waiting for roll state")

        return state

    def get_current_waiting_for_move_state(self) -> WaitingForMoveGameState:
        """
        Gets the current state of this game as an instance of WaitingForMoveGameState.
        This will throw an error if the game is not waiting for a  move from a player.
        """
        state = self.get_current_state()
        if not isinstance(state, WaitingForMoveGameState):
            raise RuntimeError("This game is not in a waiting for move state")

        return state

    def get_current_win_state(self) -> WinGameState:
        """
        Gets the current state of this game as an instance of WinGameState.
        This will throw an error if the game has not been won.
        """
        state = self.get_current_state()
        if not isinstance(state, WinGameState):
            raise RuntimeError("This game is not in a win state")

        return state

    def roll_dice(self, value: Roll | int | None = None) -> Roll:
        """
        Rolls the dice, and updates the state of the game accordingly.
        If a value is supplied, then the roll will have that value.
        """
        if value is None or not isinstance(value, Roll):
            roll = self._dice.roll(value)
        else:
            roll = value

        # Update the state of the game after rolling.
        state = self.get_current_waiting_for_roll_state()
        self.add_states(self._rules.apply_roll(state, roll))
        return roll

    def find_available_moves(self) -> list[Move]:
        """
        Finds all moves that can be made from the current position.
        """
        return self.get_current_waiting_for_move_state().available_moves

    def _make_move(self, move: Move):
        """
        Applies a move.
        """
        state = self.get_current_waiting_for_move_state()
        self.add_states(self._rules.apply_move(state, move))


    def make_move(self, move: Move | Piece | Tile):
        """
        Applies the given move to update the state of the game.
        If a piece or tile is provided, this will look for a move that
        moves the given piece, or a piece from the given tile.
        If a move is provided, this does not check whether it is valid.
        """
        if isinstance(move, Move):
            self._make_move(move)
            return

        # Find the move for the given piece.
        if isinstance(move, Piece):
            piece = move
            state = self.get_current_waiting_for_move_state()
            for avail_move in state.available_moves:
                if avail_move.has_source() and avail_move.get_source_piece() == piece:
                    self._make_move(avail_move)
                    return

            raise ValueError(f"The piece cannot be moved, {piece}")

        # Find the move for the given tile.
        if isinstance(move, Tile):
            tile = move
            paths = self._rules.paths
            state = self.get_current_waiting_for_move_state()
            for avail_move in state.available_moves:
                if avail_move.get_source(paths) == tile:
                    self._make_move(avail_move)
                    return

            raise ValueError(f"There is no available move from {piece}")

        raise RuntimeError("move is not a Move, Piece, or Tile")

    def make_move_introducing_piece(self):
        """
        Moves a new piece onto the board.
        """
        state = self.get_current_waiting_for_move_state()
        for move in state.available_moves:
            if move.is_introducing_piece():
                self._make_move(move)
                return

        raise ValueError(f"There is no available move to introduce a piece to the board")

    def get_board(self) -> Board:
        """
        Gets the current state of the board.
        """
        return self.get_current_state().board

    def get_light_player(self) -> PlayerState:
        """
        Gets the current state of the light player.
        """
        return self.get_current_state().light_player

    def get_dark_player(self) -> PlayerState:
        """
        Gets the current state of the dark player.
        """
        return self.get_current_state().dark_player

    def get_player(self, player: PlayerType) -> PlayerState:
        """
        Gets the current state of the given player.
        """
        return self.get_current_state().get_player(player)

    def get_turn(self) -> PlayerType:
        """
        Gets the player who can make the next interaction with the game.
        """
        return self.get_current_playable_state().get_turn()

    def get_turn_or_winner(self) -> PlayerType:
        """
        Gets the player who can make the next interaction with the game,
        or the winner of the game if it is finished.
        """
        state = self.get_current_state()
        if isinstance(state, PlayableGameState):
            return state.get_turn()

        if isinstance(state, WinGameState):
            return state.get_winner()

        raise RuntimeError("The game is not in a playable or won state")

    def get_turn_player(self) -> PlayerState:
        """
        Gets the state of the player whose turn it is.
        """
        return self.get_current_playable_state().get_turn_player()

    def get_waiting_player(self) -> PlayerState:
        """
        Gets the state of the player that is waiting as it is not their turn.
        """
        return self.get_current_playable_state().get_waiting_player()

    def get_winner(self) -> PlayerType:
        """
        Gets the player that won the game.
        """
        return self.get_current_win_state().get_winner()

    def get_loser(self) -> PlayerType:
        """
        Gets the player that lost the game.
        """
        return self.get_current_win_state().get_loser()

    def get_winning_player(self) -> PlayerState:
        """
        Gets the state of the winning player.
        """
        return self.get_current_win_state().get_winning_player()

    def get_losing_player(self) -> PlayerState:
        """
        Gets the state of the losing player.
        """
        return self.get_current_win_state().get_losing_player()

    def get_roll(self) -> Roll:
        """
        Gets the roll that was made that can be used by the
        current turn player to make a move.
        """
        return self.get_current_waiting_for_move_state().roll


class GameBuilder:
    """
    A builder to help in the creation of custom games of the Royal Game of Ur.
    """
    pass
