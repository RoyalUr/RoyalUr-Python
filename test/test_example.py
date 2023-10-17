import unittest
import random
from royalur import Game


class TestExample(unittest.TestCase):

    def test_example(self):
        game = Game.create_finkel()

        while not game.is_finished():
            turn_player_name = game.get_turn().text_name

            if game.is_waiting_for_roll():
                roll = game.roll_dice()
                print(f"{turn_player_name}: Roll {roll.value}")

            else:
                moves = game.find_available_moves()
                move = moves[random.randint(0, len(moves) - 1)]
                game.make_move(move)
                print(f"{turn_player_name}: {move.describe()}")

        print(f"{game.get_winner().text_name} won the game!")
