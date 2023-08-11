from typing import Optional, Tuple
from paitest._types import CoordLike
from paitest.coord import Coord, CoreType


def get_core_type(coord: CoordLike) -> CoreType:
    if isinstance(coord, Coord):
        return coord.core_type

    if isinstance(coord, (list, tuple)):
        if not len(coord) == 2:
            raise ValueError(f"Length of coord must be 2: {len(coord)}")

        if tuple(coord) >= (0b11100, 0b11100):
            return CoreType.TYPE_ONLINE
        else:
            return CoreType.TYPE_OFFLINE

    raise TypeError(f"Unsupported type: {type(coord)}")


def bin_split(x: int, pos: int, high_mask: Optional[int] = None) -> Tuple[int, int]:
    """Split an integer, return the high and low part.

    Argument:
        - x: the integer
        - pos: the position(LSB) of splitting.
        - high_mask: mask for the high part. Optional.

    Example: split 0b11000_01000 on the position of bit 3.
    >>> bin_split(0b1100001001, 3)
    97(0b1100001), 1
    """

    if pos > x.bit_length():
        raise ValueError("position is larger than the integer")

    low = x & ((1 << pos) - 1)

    if isinstance(high_mask, int):
        high = (x >> pos) & high_mask
    else:
        high = x >> pos

    return high, low


def bin_combine(high: int, low: int, pos: Optional[int] = None) -> int:
    """Combine two integers, return the result.

    Argument:
        - high: the integer on the high bit
        - low: the integer on the low bit
        - pos: the combination bit if provided. Otherwise the position is `low.bit_length()`

    Example: combine 0b11000, 0b101
    >>> bin_combine(0b11000, 0b101, 5)
    773(0b1100000101)

    >>> bin_combine(0b11000, 0b101)
    197(0b11000101)
    """

    if isinstance(pos, int):
        if pos < low.bit_length():
            raise ValueError(f"Postion of combination must greater than the bit length of low({low.bit_length()})")
        _pos = pos
    
    else:
        _pos = low.bit_length()

    return (high << _pos) + low
