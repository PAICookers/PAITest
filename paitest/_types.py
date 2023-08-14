from enum import Enum, IntEnum, unique
from typing import TypeVar, List, Tuple
from paitest.coord import Coord


@unique
class FrameType(Enum):
    """Types of Frames"""

    FRAME_CONFIG = 0
    FRAME_TEST = 1
    FRAME_WORK = 2
    FRAME_UNKNOWN = 3


@unique
class FrameSubType(IntEnum):
    """Sub-types of Configuration Frames"""

    CONFIG_TYPE1 = 0
    CONFIG_TYPE2 = 1
    CONFIG_TYPE3 = 2
    CONFIG_TYPE4 = 3

    """Sub-types of Test Frames"""
    TEST_TYPE1 = 4
    TEST_TYPE2 = 5
    TEST_TYPE3 = 6
    TEST_TYPE4 = 7


class PackageType(IntEnum):
    """ID in payload for config & test in/out frame type III & IV"""
    CONFIG = 0
    TEST_IN = 1
    TEST_OUT = 0


CoordLike = TypeVar("CoordLike", Coord, Tuple[int, ...], List[int])
FrameArray = TypeVar("FrameArray", List[int], Tuple[int, ...])