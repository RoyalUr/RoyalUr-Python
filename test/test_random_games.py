import unittest
import random
from royalur import Game


class TestRandomGames(unittest.TestCase):

    def _play_randomly(self, game: Game):
        while not game.is_finished():
            if game.is_waiting_for_roll():
                game.roll_dice()

            else:
                moves = game.find_available_moves()
                move = moves[random.randint(0, len(moves) - 1)]
                game.make_move(move)

    def test_finkel(self):
        for _ in range(3):
            game = Game.create_finkel()
            self._play_randomly(game)

    def test_masters(self):
        for _ in range(3):
            game = Game.create_masters()
            self._play_randomly(game)

    def test_aseb(self):
        for _ in range(3):
            game = Game.create_aseb()
            self._play_randomly(game)
