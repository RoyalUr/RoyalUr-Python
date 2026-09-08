import unittest
from royalur.lut.generate_states import loop_light_game_states


class TestGenerateStates(unittest.TestCase):

    def test_generate_states(self):
        #profiler = cProfile.Profile()
        #profiler.enable()
        loop_light_game_states()
        #profiler.disable()
        #profiler.print_stats()
