from dataclasses import dataclass
"""
	3 method
	Startup frame of data package:
	| Header | CHIP Address | CORE Address | CORE* Address | LOAD |
	

"""


@dataclass
class FrameHeader:
    FRAME_FLAG_CONFIG = 0x00
    FRAME_FLAG_TEST = 0x01
    FRAME_FLAG_WORK = 0x02
    FRAME_FLAG_RESERVED = 0x03

    CONFIG_TYPE_1 = 0x00
    CONFIG_TYPE_2 = 0x01
    CONFIG_NEURON_RAM = 0x02
    CONFIG_WEIGHT_RAM = 0x03
    TEST_TYPE_1 = CONFIG_TYPE_1
    TEST_TYPE_2 = CONFIG_TYPE_2
    TEST_NEURON_RAM = CONFIG_NEURON_RAM
    TEST_WEIGHT_RAM = CONFIG_WEIGHT_RAM

    WORK_COMMON_FRAME = 0x00
    WORK_SYNC_FRAME = 0x01
    WORK_CLEAR_FRAME = 0x02
    WORK_INITIAL_FRAME = 0x03


@dataclass
class SingleFrame:

    def __init__(self,
                 header: int,
                 chip_address: int,
                 core_address: int,
                 corex_address: int,
                 load: int
                 ):
        self.header = header
        self.chip_address = chip_address
        self.core_address = core_address
        self.corex_address = corex_address
        self.load = load

    def header_assert(self):
        assert (self.header >> 2 == FrameHeader.FRAME_FLAG_CONFIG or self.header >>
                2 == FrameHeader.FRAME_FLAG_TEST)
        assert (self.header & 0x03 == FrameHeader.TEST_TYPE_1 or self.header &
                0x03 == FrameHeader.TEST_TYPE_2)

    def chip_address_assert(self):
        pass

    def core_address_assert(self):
        pass

    def core_address_assert(self):
        pass

    def __repr__(self) -> str:
        pass

    __str__ = __repr__


@dataclass
class DataPackageStartup(SingleFrame):

    def __init__(self):
        super(SingleFrame, self).__init__()

    def header_assert(self):
        assert (self.header >> 2 == FrameHeader.FRAME_FLAG_CONFIG or self.header >>
                2 == FrameHeader.FRAME_FLAG_TEST)
        assert (self.header & 0x03 == FrameHeader.TEST_NEURON_RAM or self.header &
                0x03 == FrameHeader.TEST_WEIGHT_RAM)


@dataclass
class DataPackage:
    
    def __init__(self, load: int):
        self.load = load


'''
    Format of Offline Data Frame
'''
@dataclass
class TestInputFrameType1:
    pass