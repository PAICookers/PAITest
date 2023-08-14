import unittest
from paitest.utils import bin_combine_x, bin_split, bin_combine


class BinUtilsTestCase(unittest.TestCase):
    def test_bin_split(self):
        n = 10
        for x in range(0, (1 << n) - 1):
            for i in range(x.bit_length() + 1):
                high, low = bin_split(x, i)

                if i == 0:
                    self.assertEqual(high, x)
                    self.assertEqual(low, 0)
                elif i == n:
                    self.assertEqual(high, 0)
                    self.assertEqual(low, x)
                else:
                    self.assertEqual(high, x // (2**i))
                    self.assertEqual(low, x % (2**i))

    def test_bin_combine(self):
        n = 10
        for x in range(0, (1 << n) - 1):
            for y in range(0, (1 << n) - 1):
                if y == 0:
                    with self.assertRaises(ValueError):
                        comb = bin_combine(x, y, -1)

                    comb = bin_combine(x, y, 0)
                    self.assertEqual(comb, x)
                else:
                    with self.assertRaises(ValueError):
                        bin_combine(x, y, y.bit_length() - 1)

                comb = bin_combine(x, y, n)
                self.assertEqual(comb, (x << n) | y)

    def test_bin_combine_x(self):
        n = 5
        for x in range(0, (1 << n) - 1):
            for y in range(0, (1 << n) - 1):
                for z in range(0, (1 << n) - 1):
                    for k in range(0, (1 << n) - 1):
                        comb = bin_combine_x(x, y, pos=n)
                        self.assertEqual(comb, (x << n) | y)

                        comb = bin_combine_x(x, y, pos=[n])
                        self.assertEqual(comb, (x << n) | y)

                        with self.assertRaises(ValueError):
                            bin_combine_x(x, pos=[1, 2])

                        with self.assertRaises(ValueError):
                            bin_combine_x(x, y, z, pos=1)

                        with self.assertRaises(ValueError):
                            bin_combine_x(x, y, z, k, pos=[1, 2])

                        with self.assertRaises(ValueError):
                            comb = bin_combine_x(x, y, z, k, pos=[n * 3, n * 2, -1])

                        comb = bin_combine_x(x, y, z, k, pos=[n * 3, n * 2, n])
                        self.assertEqual(
                            comb, ((x << (n * 3)) + (y << (n * 2)) + (z << n) + k)
                        )

                        comb = bin_combine_x(
                            x, y, z, k, pos=[3 * n + 2, 2 * n + 1, n + 1]
                        )
                        self.assertEqual(
                            comb,
                            (
                                (x << (3 * n + 2))
                                + (y << (2 * n + 1))
                                + (z << (n + 1))
                                + k
                            ),
                        )


class FrameTestCase(unittest.TestCase):
    def foo(self):
        pass
