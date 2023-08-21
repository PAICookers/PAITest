import unittest
import pytest
from paitest.coord import Coord, ReplicationId
from paitest.utils import (
    bin_combine_x,
    bin_split,
    bin_combine,
    get_replication_id,
    get_multicast_cores,
)


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

        high, low = bin_split(4, 7)
        self.assertEqual(high, 0)
        self.assertEqual(low, 4)

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


@pytest.mark.parametrize(
    "coords, expected",
    [
        (
            [
                Coord(0b00000, 0b00000),
                Coord(0b00000, 0b00001),
                Coord(0b00001, 0b00000),
                Coord(0b00001, 0b00001),
            ],
            Coord(0b00001, 0b00001),
        ),
        (
            [
                Coord(0b00101, 0b00101),
                Coord(0b00101, 0b00111),
                Coord(0b00111, 0b00101),
                Coord(0b00011, 0b00011),
            ],
            Coord(0b00110, 0b00110),
        ),
        (
            [
                Coord(0b00101, 0b00101),
                Coord(0b00101, 0b00111),
                Coord(0b00111, 0b00101),
                Coord(0b10111, 0b00101),
            ],
            Coord(0b10010, 0b00010),
        ),
    ],
)
def test_get_replication_id(coords, expected):
    rid = get_replication_id(coords)

    assert rid == expected


@pytest.mark.parametrize(
    "base, rid, expected",
    [
        (Coord(0, 0), ReplicationId(0b11110, 0b11100), 128),
        (Coord(0b01100, 0b01100), ReplicationId(0b01101, 0), 8),
        (Coord(0b10101, 0b00111), ReplicationId(1, 0b10001), 8),
    ],
)
def test_multicast_length(base, rid, expected):
    cores = get_multicast_cores(base, rid)

    assert len(cores) == expected


def test_nulticast_contents():
    cores = get_multicast_cores(Coord(0b10101, 0b00111), ReplicationId(1, 0b10001))
    cores.sort()

    assert cores == [
        Coord(0b10100, 0b00110),
        Coord(0b10100, 0b00111),
        Coord(0b10100, 0b10110),
        Coord(0b10100, 0b10111),
        Coord(0b10101, 0b00110),
        Coord(0b10101, 0b00111),
        Coord(0b10101, 0b10110),
        Coord(0b10101, 0b10111),
    ]
