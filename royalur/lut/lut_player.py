from royalur.game import Game
from royalur.lut.board_encoder import SimpleGameStateEncoding
from royalur.lut.reader import LutReader
from royalur.model.player import PlayerType


class LutAgent:
    """
    An agent that uses a look-up table to play the game.

    NOTE: This agent is only for the light player.
    It will invert the game state if the current turn is not the light

    NOTE: The class does many things and could be split into smaller classes,
    such as a class to handle the encoding and inverting the game state.
    """

    def __init__(self, lut_path: str):
        r = LutReader(lut_path)
        lut = r.read()
        self.lut = lut
        self.encoding = SimpleGameStateEncoding()

    def play(self, game: Game):
        """
        Play a move in the game using the look-up table.
        :param game: The game to play.

        :return: The move to play.
        """
        highest_value = 0
        highest_move = None
        moves = game.find_available_moves()
        for move in moves:
            game_copy = game.copy()
            game_copy.make_move(move)
            game_state = game_copy.get_current_state()
            inverted = False
            if game_state.is_finished():
                if game_state.get_winner() == PlayerType.DARK:
                    value = 0
                else:
                    value = 65535
            else:
                if not game_state.is_finished() \
                        and game_state.get_turn() != PlayerType.LIGHT:
                    # invert the state because
                    # the LUT is only for the light player
                    game_state = game_state.copy_inverted()
                    assert game_state.get_turn() == PlayerType.LIGHT
                    inverted = True
                state = self.encoding.encode_game_state(game_state)
                value = self.lut.lookup(0, state)
            if inverted:
                value = 65535 - value
            if value > highest_value:
                highest_value = value
                highest_move = move
        return highest_move
