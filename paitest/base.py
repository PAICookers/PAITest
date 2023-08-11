from enum import Enum, unique
from paitest.coord import CoordOffset


@unique
class Direction(Enum):
    """Left to right: +x, Top to bottom: +y

    NOTE: The priority of Y is higher than X.
    """

    EAST = CoordOffset(1, 0)
    SOUTH = CoordOffset(0, 1)
    WEST = CoordOffset(-1, 0)
    NORTH = CoordOffset(0, -1)
