from dataclasses import dataclass
from enum import Flag, Enum


class FrameTypes(Flag):
    '''
        For general usages:
    '''
    '''Types of Frames'''
    FRAME_CONFIG = 0
    FRAME_TEST = 0x1
    FRAME_WORK = 0x2
    FRAME_RESERVED = 0x3
    FRAME_UNKNOWN = 0x3

    '''Types of Configuration Frames'''
    CONFIG_RANDOM_SEED = (FRAME_CONFIG << 2) | 0
    CONFIG_PARAMETER_REG = (FRAME_CONFIG << 2) | 0x1
    CONFIG_NEURON_RAM = (FRAME_CONFIG << 2) | 0x2
    CONFIG_WEIGHT_RAM = (FRAME_CONFIG << 2) | 0x3

    CONFIG_TYPE1 = CONFIG_RANDOM_SEED
    CONFIG_TYPE2 = CONFIG_PARAMETER_REG
    CONFIG_TYPE3 = CONFIG_NEURON_RAM
    CONFIG_TYPE4 = CONFIG_WEIGHT_RAM

    '''Types of Test Frames'''
    TEST_RANDOM_SEED_REG = (FRAME_TEST << 2) | 0
    TEST_PARAMETER_REG = (FRAME_TEST << 2) | 0x01
    TEST_NEURON_RAM = (FRAME_TEST << 2) | 0x02
    TEST_WEIGHT_RAM = (FRAME_TEST << 2) | 0x03

    TEST_TYPE1 = TEST_RANDOM_SEED_REG
    TEST_TYPE2 = TEST_PARAMETER_REG
    TEST_TYPE3 = TEST_NEURON_RAM
    TEST_TYPE4 = TEST_WEIGHT_RAM


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
    # Header
    GENERAL_HEADER_OFFSET = 60
    GENERAL_HEADER_MASK = (1 << 4) - 1

    GENERAL_FRAME_TYPE_OFFSET = GENERAL_HEADER_OFFSET
    GENERAL_FRAME_TYPE_MASK = GENERAL_HEADER_MASK

    # Chip address
    GENERAL_CHIP_ADDR_OFFSET = 50
    GENERAL_CHIP_ADDR_MASK = (1 << 10) - 1

    # Core address
    GENERAL_CORE_ADDR_OFFSET = 40
    GENERAL_CORE_ADDR_MASK = (1 << 10) - 1

    # Core* address
    GENERAL_CORE_STAR_ADDR_OFFSET = 30
    GENERAL_CORE_STAR_ADDR_MASK = (1 << 10) - 1

    # Global core = Chip address + core address
    GENERAL_CORE_GLOBAL_ADDR_OFFSET = GENERAL_CORE_ADDR_OFFSET
    GENERAL_CORE_GLOBAL_ADDR_MASK = (1 << 20) - 1

    # Payload
    GENERAL_PAYLOAD_OFFSET = 0
    GENERAL_PAYLOAD_MASK = (1 << 30) - 1
    GENERAL_PAYLOAD_FILLED_MASK = (1 << 4) - 1

    '''Format of startup frame of data package'''
    GENERAL_PACKAGE_OFFSET = 0
    GENERAL_PACKAGE_MASK = (1 << 20) - 1

    GENERAL_PACKAGE_SRAM_START_ADDR_OFFSET = 20
    GENERAL_PACKAGE_SRAM_START_ADDR_MASK = (1 << 10) - 1

    GENERAL_PACKAGE_TYPE_OFFSET = 19
    GENERAL_PACKAGE_TYPE_MASK = 0x1

    GENERAL_PACKAGE_COUNT_OFFSET = GENERAL_PACKAGE_OFFSET
    GENERAL_PACKAGE_COUNT_MASK = (1 << 19) - 1


@dataclass
class ConfigFrameMasks(FrameMasks):
    '''Specific for Conguration Frame Type II'''

    '''Frame #1'''
    WEIGHT_WIDTH_OFFSET = 28
    WEIGHT_WIDTH_MASK = (1 << 2) - 1

    LCN_OFFSET = 24
    LCN_MASK = (1 << 4) - 1

    INPUT_WIDTH_OFFSET = 23
    INPUT_WIDTH_MASK = 1

    SPIKE_WIDTH_OFFSET = 22
    SPIKE_WIDTH_MASK = 1

    NEURON_NUM_OFFSET = 9
    NEURON_NUM_MASK = (1 << 13) - 1

    POOL_MAX_OFFSET = 8
    POOL_MAX_MASK = 1

    TICK_WAIT_START_HIGH8_OFFSET = 0
    TICK_WAIT_START_HIGH8_OFFSET = 7
    TICK_WAIT_START_HIGH8_MASK = (1 << 8) - 1

    '''Frame #2'''
    TICK_WAIT_START_LOW7_OFFSET = 23
    TICK_WAIT_START_LOW7_MASK = (1 << 7) - 1

    TICK_WAIT_END_OFFSET = 8
    TICK_WAIT_END_MASK = (1 << 15) - 1

    SNN_EN_OFFSET = 7
    SNN_EN_MASK = 1

    TARGET_LCN_OFFSET = 3
    TARGET_LCN_MASK = (1 << 4) - 1

    TEST_CHIP_ADDR_HIGH3_OFFSET = 0
    TEST_CHIP_ADDR_HIGH3_OFFSET = 7
    TEST_CHIP_ADDR_HIGH3_MASK = (1 << 3) - 1

    '''Frame #3'''
    TEST_CHIP_ADDR_LOW7_OFFSET = 23
    TEST_CHIP_ADDR_LOW7_MASK = (1 << 7) - 1
