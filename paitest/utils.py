from typing import List, Optional, Set, Tuple, Union
from paitest._types import CoordLike
from paitest.coord import Coord, CoreType, ReplicationId


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
    low = x & ((1 << pos) - 1)

    if isinstance(high_mask, int):
        high = (x >> pos) & high_mask
    else:
        high = x >> pos

    return high, low


def bin_combine(high: int, low: int, pos: int) -> int:
    """Combine two integers, return the result.

    Argument:
        - high: the integer on the high bit.
        - low: the integer on the low bit.
        - pos: the combination bit if provided. Must be equal or greater than `low.bit_length()`.

    Example: combine 0b11000, 0b101
    >>> bin_combine(0b11000, 0b101, 5)
    773(0b11000_00101)
    """
    if pos < 0:
        raise ValueError("position must be greater than 0")

    if low > 0 and pos < low.bit_length():
        raise ValueError(
            f"Postion of combination must be greater than the bit length of low({low.bit_length()})"
        )

    return (high << pos) + low


def bin_combine_x(*components: int, pos: Union[int, List[int], Tuple[int, ...]]) -> int:
    """Combine more than two integers, return the result.

    Argument:
        - components: the list of integers to be combined.
        - pos: the combination bit(s) if provided. Every bit must be equal or greater than `low.bit_length()`.

    Example: combine 0b11000, 0b101, 0b01011
    >>> bin_combine_x(0b11000, 0b101, 0b1011, pos=[10, 5])
    24747(0b11000_00101_01011)
    """
    if isinstance(pos, (list, tuple)):
        if len(components) != len(pos) + 1:
            raise ValueError(
                f"Length of components and positions illegal: {len(components)}, {len(pos)}"
            )
    else:
        if len(components) != 2:
            raise ValueError(
                f"Length of components must be 2: {len(components)} when position is an integer."
            )

        return bin_combine(*components, pos=pos)

    result = components[-1]

    # Traverse every position from the end to the start
    for i in range(len(pos) - 1, -1, -1):
        result = bin_combine(components[i], result, pos[i])

    return result


def get_replication_id(dest_coords: List[Coord]) -> ReplicationId:
    """
    Arguments:
        - dest_coords: the list of coordinates which are the destinations of a frame.
    
    Return:
        The replication ID.
    """
    baseCore = dest_coords[0]
    rid = ReplicationId(0, 0)
    
    for coord in dest_coords:
        rid |= baseCore ^ coord
    
    return rid


def get_multicast_cores(base_coord: Coord, repilication_id: ReplicationId) -> List[Coord]:
    cores: List[Coord] = []
    cores.append(base_coord)
    
    for i in range(10):
        if (repilication_id >> i) & 1:
            temp = []
            for core in cores:
                temp.append(core ^ ReplicationId.from_tuple(bin_split(1 << i, 5)))
            
            cores.extend(temp)
    
    return cores


def to_coord(coordlike: CoordLike) -> Coord:
    if isinstance(coordlike, (list, tuple)):
        if len(coordlike) != 2:
            raise ValueError(
                f"Must be a tuple or list of 2 elements to represent a coordinate: {len(coordlike)}"
            )

        return Coord.from_tuple(coordlike)
    
    return coordlike