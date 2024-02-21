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
        r = LutReader("test/lut/finkel_bad.rgu")
        lut = r.read()
        print(lut.get_metadata())
        self.assertEqual(len(lut), 137892016)
        print(lut.lookup_detailed(0, lut._get_key_at_index(0, 0)["value"]))
        print(lut.lookup_detailed(0, lut._get_key_at_index(0, 1)["value"]))

        numpy_keys = lut.keys_as_numpy()
        numpy_values = lut.values_as_numpy()

        # print the first 10 keys and values
        for i in range(200):
            print(numpy_keys[i], round(numpy_values[i] / 65535, 4))
        for key, value in expected_dict_values.items():
            self.assertEqual(lut.lookup(0, key), value)
