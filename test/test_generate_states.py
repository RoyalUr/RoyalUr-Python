import unittest
from royalur import LutReader
from royalur.game import Game
import random
from royalur.lut.generate_states import loop_light_game_states, final_consume
from royalur.lut.lut_player import LutAgent
from royalur.model.player import PlayerType
from huggingface_hub import hf_hub_download
import cProfile


class TestGenerateStates(unittest.TestCase):

    def test_generate_states(self):
        #profiler = cProfile.Profile()
        #profiler.enable()
        loop_light_game_states()
        #profiler.disable()
        #profiler.print_stats()
