import unittest
from royalur import LutReader


class TestLut(unittest.TestCase):

    def test_lut_read(self):
        expected_dict_values = {
            7: 0,
            10: 15,
            13: -2,
            16: 13,
            19: -4,
            22: 11,
            25: -6,
            28: 9,
            31: -8,
            34: 7,
            37: -10,
            40: 5,
            43: -12,
            46: 3,
            49: -14,
            52: 1,
        }
        r = LutReader("test/lut/sample_small.rgu")
        lut = r.read()
        self.assertEqual(len(lut), 16)

        for key, value in expected_dict_values.items():
            self.assertEqual(lut[key], value)
