import unittest
from royalur import LutReader


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
