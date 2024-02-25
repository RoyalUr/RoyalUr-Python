import unittest
from royalur import LutReader
from royalur.game import Game
import random
from royalur.lut.lut_player import LutAgent
from royalur.model.player import PlayerType


class TestLut(unittest.TestCase):

    def test_lut_read(self):
        expected_dict_values = {
            603979776: 33985,  # Is a starting state
            67108864: 65535,  # Is a winning state
            33554432: 65535,  # Is a winning state
        }
        r = LutReader("test/lut/finkel2p.rgu")
        lut = r.read()
        lut_meta = lut.get_metadata()

        numpy_keys = lut.keys_as_numpy(0)
        numpy_values = lut.values_as_numpy(0)
        self.assertRaises(IndexError, lut.keys_as_numpy, 1)
        self.assertRaises(IndexError, lut.values_as_numpy, 1)

        self.assertEqual(lut_meta["number_of_maps"], 1)
        self.assertEqual(
            lut_meta["decoded_header"]["author"],
            "Padraig Lamont"
        )
        self.assertEqual(lut_meta["size_of_maps"][0], 12990)
        self.assertEqual(len(lut), 12990)
        self.assertEqual(len(numpy_keys), 12990)
        self.assertEqual(len(numpy_values), 12990)

        for key, value in expected_dict_values.items():
            self.assertEqual(lut.lookup(0, key), value)

    def test_lut_plays_against_random_and_wins(self):
        random.seed(99_999_999)
        # Create a new game using the Finkel rules.
        light_wins = 0
        lut_player = LutAgent("test/lut/finkel2p.rgu")
        for _ in range(100):
            game = self.play_random(lut_player)
            print(f"{game.get_winner().text_name} won the game!")
            if game.get_winner() == PlayerType.LIGHT:
                light_wins += 1

        self.assertGreater(light_wins, 75)

    def play_random(self, lut_player):
        game = Game.create_finkel(2)

        while not game.is_finished():
            turn_player_name = game.get_turn().text_name

            if game.is_waiting_for_roll():
                # Roll the dice!
                roll = game.roll_dice()
                print(f"{turn_player_name}: Roll {roll.value}")

            else:
                if game.get_turn() == PlayerType.LIGHT:
                    move = lut_player.play(game)
                else:
                    # Make a random move.
                    moves = game.find_available_moves()
                    move = moves[random.randint(0, len(moves) - 1)]
                game.make_move(move)
                print(f"{turn_player_name}: {move.describe()}")
        return game
