import unittest
from paitest.frames import ParamGenOffline


class ParamGenOfflineTestCase(unittest.TestCase):

    def test_GenParamConfig1(self):
        seed1 = 0b1111_1001_1010_1011_1100_1101_1110_01
        seed2 = 0b1111_0000_0001_0010_0011_0100_0101_10
        seed3 = 0b0000_0000_0000_0000_0000_0000_0010_11
        seed = 0b1111_1001_1010_1011_1100_1101_1110_0111_1100_0000_0100_1000_1101_0001_0110_1011
        self.assertEqual(64, seed.bit_length())
        
        params = ParamGenOffline.GenParamConfig1(is_random=False, seed=seed)
        self.assertEqual(len(params), 3)

        self.assertEqual(seed1, params[0])
        self.assertEqual(seed2, params[1])
        self.assertEqual(seed3, params[2])

        params = ParamGenOffline.GenParamConfig1()