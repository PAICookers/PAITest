from enum import Enum, IntEnum, unique
from typing import TypeVar, List, Tuple
from paitest.coord import Coord


@unique
class FrameMainType(Enum):
    """Main types of Frames"""

    FRAME_CONFIG = 0
    FRAME_TEST = 1
    FRAME_WORK = 2
    FRAME_UNKNOWN = 3


class FrameSubType(Enum):
    """Sub-types of configuration frames"""

    CONFIG_TYPE1 = 0
    CONFIG_TYPE2 = 1
    CONFIG_TYPE3 = 2
    CONFIG_TYPE4 = 3

    """Sub-types of test frames"""
    TEST_IN_TYPE1 = 4
    TEST_IN_TYPE2 = 5
    TEST_IN_TYPE3 = 6
    TEST_IN_TYPE4 = 7
    TEST_OUT_TYPE1 = 4
    TEST_OUT_TYPE2 = 5
    TEST_OUT_TYPE3 = 6
    TEST_OUT_TYPE4 = 7
    
    """Sub-types of working frames"""
    WORK_TYPE1 = 8
    WORK_TYPE2 = 9
    WORK_TYPE3 = 10
    WORK_TYPE4 = 11


class PackageType(Enum):
    """Package ID for config & test in/out frame type III & IV"""
    CONFIG = 0
    TEST_IN = 1
    TEST_OUT = 0


CoordLike = TypeVar("CoordLike", Coord, Tuple[int, ...], List[int])
FrameArray = TypeVar("FrameArray", List[int], Tuple[int, ...])