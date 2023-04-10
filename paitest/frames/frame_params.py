from dataclasses import dataclass
from enum import Flag, Enum, unique


@unique
class CoreType(Enum):
    CORE_TYPE_OFFLINE = 1
    CORE_TYPE_ONLINE = 0


@unique
class FrameTypes(Enum):
    '''Types of Frames'''
    FRAME_CONFIG = 0
    FRAME_TEST = 0x1
    FRAME_WORK = 0x2
    FRAME_UNKNOWN = 0x3


@unique
class FrameSubTypes(Flag):
    '''Sub-types of Configuration Frames'''
    CONFIG_TYPE1 = 0b0000
    CONFIG_TYPE2 = 0b0001
    CONFIG_TYPE3 = 0b0010
    CONFIG_TYPE4 = 0b0011
    
    '''Sub-types of Test Frames'''
    TEST_TYPE1 = 0b0100
    TEST_TYPE2 = 0b0101
    TEST_TYPE3 = 0b0110
    TEST_TYPE4 = 0b0111

    '''Sub-types of Work Frames'''
    WORK_TYPE1 = 0b1000
    WORK_TYPE2 = 0b1001
    WORK_TYPE3 = 0b1010
    WORK_TYPE4 = 0b1011


class ParamTypesForCheck(Enum):
    globalCoreId = 0
    starId = 1
    payload = 2
    chipId = 3
    sram = 4
    frameNum = 5


@dataclass
class FrameMasks:
    '''
        Format of data package or single frame for general usages:
    '''
    '''Format of single frame'''
    # General mask
    GENERAL_MASK = ((1 << 64) - 1)

    # Header
    GENERAL_HEADER_OFFSET = 60
    GENERAL_HEADER_MASK = ((1 << 4) - 1)

    GENERAL_FRAME_TYPE_OFFSET = GENERAL_HEADER_OFFSET
    GENERAL_FRAME_TYPE_MASK = GENERAL_HEADER_MASK

    # Chip address
    GENERAL_CHIP_ADDR_OFFSET = 50
    GENERAL_CHIP_ADDR_MASK = ((1 << 10) - 1)
    # Chip X/Y address
    GENERAL_CHIP_ADDR_X_OFFSET = 55
    GENERAL_CHIP_ADDR_X_MASK = ((1 << 5) - 1)
    GENERAL_CHIP_ADDR_Y_OFFSET = GENERAL_CHIP_ADDR_OFFSET
    GENERAL_CHIP_ADDR_Y_MASK = ((1 << 5) - 1)

    # Core address
    GENERAL_CORE_ADDR_OFFSET = 40
    GENERAL_CORE_ADDR_MASK = ((1 << 10) - 1)
    # Core X/Y address
    GENERAL_CORE_ADDR_X_OFFSET = 45
    GENERAL_CORE_ADDR_X_MASK = ((1 << 5) - 1)
    GENERAL_CORE_ADDR_Y_OFFSET = GENERAL_CORE_ADDR_OFFSET
    GENERAL_CORE_ADDR_Y_MASK = ((1 << 5) - 1)

    # Core* address
    GENERAL_CORE_STAR_ADDR_OFFSET = 30
    GENERAL_CORE_STAR_ADDR_MASK = ((1 << 10) - 1)
    # Core* X/Y address
    GENERAL_CORE_STAR_ADDR_X_OFFSET = 35
    GENERAL_CORE_STAR_ADDR_X_MASK = ((1 << 5) - 1)
    GENERAL_CORE_STAR_ADDR_Y_OFFSET = GENERAL_CORE_STAR_ADDR_OFFSET
    GENERAL_CORE_STAR_ADDR_Y_MASK = ((1 << 5) - 1)

    # Global core = Chip address + core address
    GENERAL_CORE_GLOBAL_ADDR_OFFSET = GENERAL_CORE_ADDR_OFFSET
    GENERAL_CORE_GLOBAL_ADDR_MASK = ((1 << 20) - 1)

    # Payload
    GENERAL_PAYLOAD_OFFSET = 0
    GENERAL_PAYLOAD_MASK = ((1 << 30) - 1)
    GENERAL_PAYLOAD_FILLED_MASK = ((1 << 4) - 1)

    '''Format of startup frame of data package'''
    GENERAL_PACKAGE_OFFSET = 0
    GENERAL_PACKAGE_MASK = ((1 << 20) - 1)

    GENERAL_PACKAGE_SRAM_START_ADDR_OFFSET = 20
    GENERAL_PACKAGE_SRAM_START_ADDR_MASK = ((1 << 10) - 1)

    GENERAL_PACKAGE_TYPE_OFFSET = 19
    GENERAL_PACKAGE_TYPE_MASK = 0x1

    GENERAL_PACKAGE_COUNT_OFFSET = GENERAL_PACKAGE_OFFSET
    GENERAL_PACKAGE_COUNT_MASK = ((1 << 19) - 1)


@dataclass
class ConfigFrameMasks(FrameMasks):
    '''Specific for Conguration Frame Type II'''
    
    '''General'''
    TOTAL_RANDOM_BITS = 57

    '''Frame #1'''
    WEIGHT_WIDTH_OFFSET = 28
    WEIGHT_WIDTH_MASK = ((1 << 2) - 1)

    LCN_OFFSET = 24
    LCN_MASK = ((1 << 4) - 1)

    INPUT_WIDTH_OFFSET = 23
    INPUT_WIDTH_MASK = 1

    SPIKE_WIDTH_OFFSET = 22
    SPIKE_WIDTH_MASK = 1

    NEURON_NUM_OFFSET = 9
    NEURON_NUM_MASK = ((1 << 13) - 1)

    POOL_MAX_OFFSET = 8
    POOL_MAX_MASK = 1

    TICK_WAIT_START_HIGH8_OFFSET = 0
    TICK_WAIT_START_COMBINATION_OFFSET = 7
    TICK_WAIT_START_HIGH8_MASK = ((1 << 8) - 1)

    '''Frame #2'''
    TICK_WAIT_START_LOW7_OFFSET = 23
    TICK_WAIT_START_LOW7_MASK = ((1 << 7) - 1)

    TICK_WAIT_END_OFFSET = 8
    TICK_WAIT_END_MASK = ((1 << 15) - 1)

    SNN_EN_OFFSET = 7
    SNN_EN_MASK = 1

    TARGET_LCN_OFFSET = 3
    TARGET_LCN_MASK = ((1 << 4) - 1)

    TEST_CHIP_ADDR_HIGH3_OFFSET = 0
    TEST_CHIP_ADDR_COMBINATION_OFFSET = 7
    TEST_CHIP_ADDR_HIGH3_MASK = ((1 << 3) - 1)

    '''Frame #3'''
    TEST_CHIP_ADDR_LOW7_OFFSET = 23
    TEST_CHIP_ADDR_LOW7_MASK = ((1 << 7) - 1)


@unique
class WeightPrecisionTypes(Enum):
    '''Wight precision of crossbar'''
    WEIGHT_WIDTH_1BIT = 0
    WEIGHT_WIDTH_2BIT = 1
    WEIGHT_WIDTH_4BIT = 2
    WEIGHT_WIDTH_8BIT = 3


@unique
class LCNTypes(Enum):
    '''Scale of Fan-in extension'''
    LCN_1X = 0
    LCN_2X = 1
    LCN_4X = 2
    LCN_8X = 3
    LCN_16X = 4
    LCN_32X = 5
    LCN_64X = 6


@unique
class InputWidthTypes(Enum):
    '''Format of Input Spike'''
    INPUT_WIDTH_1BIT = 0
    INPUT_WIDTH_8BIT = 1


@unique
class SpikeWidthTypes(Enum):
    '''Format of Output Spike'''
    SPIKE_WIDTH_1BIT = 0
    SPIKE_WIDTH_8BIT = 1
    

class Coord:
    
    def __init__(self, x, y):
        assert -31 < x < 32
        assert -31 < y < 32
        self.x, self.y = x, y
        
    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)
 
    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)
    
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y
    
    def __lt__(self, other) -> bool:
        '''Whether on the left or below'''
        return not (self.x > other.x and self.y > other.y)

    def __gt__(self, other) -> bool:
        '''Whether on the right and above'''
        return (self.x > other.x and self.y > other.y) or \
            (self.x == other.x and self.y > other.y) or \
                (self.x > other.x and self.y == other.y)
    
    def __str__(self) -> str:
        return f"{self.x}, {self.y}"
    
    __repr__ = __str__


@unique
class Direction(Enum):
    '''
        For [x, y]
        Left to right: +x
        Top to bottom: +y
    '''
    EAST = Coord(1, 0)
    SOUTH = Coord(0, 1)
    WEST = Coord(-1, 0)
    NORTH = Coord(0, -1)
