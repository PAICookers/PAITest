from .frame_params import FrameType, FrameSubType as FST, FrameMask as FM, ConfigFrameMask as CFM
from .frame_params import *
from typing import List, Tuple, Union, Dict, Optional, Any
import random


__all__ = [
    "Addr2Coord",
    "Coord2Addr",
    "FrameGen",
    "FrameDecoder"
]


def Addr2Coord(addr: int) -> Coord:
    return Coord(addr >> 5, addr & ((1 << 5) - 1))


def Coord2Addr(coord: Coord) -> int:
    return (coord.x << 5) | coord.y


def test_chip_coord_split(coord: Coord) -> Tuple[int, int]:
    addr = Coord2Addr(coord)
    high3 = (
        addr >> CFM.TEST_CHIP_ADDR_COMBINATION_OFFSET) & CFM.TEST_CHIP_ADDR_HIGH3_MASK
    low7 = addr & CFM.TEST_CHIP_ADDR_LOW7_MASK

    return high3, low7


def test_chip_addr_combine(high3: int, low7: int) -> Coord:
    _high3 = high3 & CFM.TEST_CHIP_ADDR_HIGH3_MASK
    _low7 = low7 & CFM.TEST_CHIP_ADDR_LOW7_MASK

    addr = (_high3 << CFM.TEST_CHIP_ADDR_COMBINATION_OFFSET) | _low7

    return Addr2Coord(addr)


class FrameGen:

    @staticmethod
    def _GenFrame(header: int,
                  chip_addr: int,
                  core_addr: int,
                  core_star_addr: int,
                  payload: int
                  ) -> int:
        header = header & FM.GENERAL_HEADER_MASK
        chip_addr = chip_addr & FM.GENERAL_CHIP_ADDR_MASK
        core_addr = core_addr & FM.GENERAL_CORE_ADDR_MASK
        core_star_addr = core_star_addr & FM.GENERAL_CORE_STAR_ADDR_MASK
        payload = payload & FM.GENERAL_PAYLOAD_MASK

        return (header << FM.GENERAL_HEADER_OFFSET) |               \
            (chip_addr << FM.GENERAL_CHIP_ADDR_OFFSET) |            \
            (core_addr << FM.GENERAL_CORE_ADDR_OFFSET) |            \
            (core_star_addr << FM.GENERAL_CORE_STAR_ADDR_OFFSET) |  \
            (payload << FM.GENERAL_PAYLOAD_OFFSET)

    @staticmethod
    def GenConfigFrame(header: FST,
                       chip_coord: Coord,
                       core_coord: Coord,
                       core_star_coord: Coord,
                       payload: int
                       ) -> int:

        chip_addr = Coord2Addr(chip_coord)
        core_addr = Coord2Addr(core_coord)
        core_star_addr = Coord2Addr(core_star_coord)

        return FrameGen._GenFrame(header.value, chip_addr, core_addr, core_star_addr, payload)

    @staticmethod
    def GenConfigGroup(header: FST,
                       chip_coord: Coord,
                       core_coord: Coord,
                       core_star_coord: Coord,
                       test_chip_coord: Coord
                       ) -> List[int]:

        ConfigFrameGroup: List[int] = []

        param_reg = FrameGen._GenParamReg(test_chip_coord)

        for i in range(3):
            ConfigFrameGroup.append(
                FrameGen.GenConfigFrame(header, chip_coord, core_coord, core_star_coord, param_reg[i]))

        return ConfigFrameGroup

    @staticmethod
    def _GenParamReg(test_chip_coord: Coord,
                     *,
                     is_random: bool = True,
                     is_legal: bool = False,
                     weight_width_type: Optional[WeightPrecisionType] = None,
                     lcn_type: Optional[LCNTypes] = None,
                     input_width_type: Optional[InputWidthType] = None,
                     spike_width_type: Optional[SpikeWidthType] = None,
                     neuron_num: Optional[int] = None,
                     pool_max_en: Optional[bool] = None,
                     tick_wait_start: Optional[int] = None,
                     tick_wait_end: Optional[int] = None,
                     snn_en: Optional[bool] = None,
                     target_lcn: Optional[int] = None,
                     ) -> List[int]:

        high3, low7 = test_chip_coord_split(
            test_chip_coord)

        param_reg: List[int] = []

        if is_random:
            if not is_legal:
                # Don't care 'tick_wait_start' split in #1 and #2
                for _ in range(2):
                    param_reg.append(random.randint(
                        0, FM.GENERAL_PAYLOAD_MASK))

                param_reg[1] = (param_reg[1] & (
                    ~CFM.TEST_CHIP_ADDR_HIGH3_MASK)) | high3
                param_reg.append(low7 << CFM.TEST_CHIP_ADDR_LOW7_OFFSET)
            else:
                # Do legal geenration
                pass
        else:
            pass

        return param_reg

    '''Functions of Test Frames Generation'''
    @staticmethod
    def _GenTestFrame(header: FST,
                      chip_coord: Coord,
                      core_coord: Coord,
                      core_star_coord: Coord,
                      payload: int = 0
                      ) -> int:

        chip_addr = Coord2Addr(chip_coord)
        core_addr = Coord2Addr(core_coord)
        core_star_addr = Coord2Addr(core_star_coord)

        return FrameGen._GenFrame(header.value, chip_addr, core_addr, core_star_addr, payload)

    @staticmethod
    def GenTest1InFrame(chip_coord: Coord,
                        core_coord: Coord,
                        core_star_coord: Coord
                        ) -> int:
        return FrameGen._GenTestFrame(FST.TEST_TYPE1, chip_coord, core_coord, core_star_coord)

    @staticmethod
    def GenTest1OutFrame(test_chip_coord: Coord,
                         core_coord: Coord,
                         core_star_coord: Coord,
                         random_seed: int
                         ) -> int:
        return FrameGen._GenTestFrame(FST.TEST_TYPE1, test_chip_coord, core_coord, core_star_coord, random_seed)

    @staticmethod
    def GenTest2InFrame(chip_coord: Coord,
                        core_coord: Coord,
                        core_star_coord: Coord
                        ) -> int:
        return FrameGen._GenTestFrame(FST.TEST_TYPE2, chip_coord, core_coord, core_star_coord)

    @staticmethod
    def GenTest2OutFrame(test_chip_coord: Coord,
                         core_coord: Coord,
                         core_star_coord: Coord,
                         param_reg: int
                         ) -> int:
        return FrameGen._GenTestFrame(FST.TEST_TYPE2, test_chip_coord, core_coord, core_star_coord, param_reg)


class FrameDecoder:

    def __init__(self, frames: Union[List[int], Tuple[int, ...]]):

        self._len = len(frames)
        self._frame = frames[0]
        self._frames_group = tuple(frames)

        '''For type II'''
        self._param_reg_dict: Dict[str, Union[int, bool, Coord]] = {
            "weight_width": 0,
            "LCN": 0,
            "input_width": 0,
            "spike_width": 0,
            "neuron_num": 0,
            "pool_max": True,
            "tick_wait_start": 0,
            "tick_wait_end": 0,
            "SNN_EN": 0,
            "target_LCN": 0,
            "test_chip_coord": Coord(0, 0)
        }

        self._decode()

    @property
    def subtype(self) -> FST:
        _header: int = (
            self._frame >> FM.GENERAL_HEADER_OFFSET) & FM.GENERAL_HEADER_MASK
        try:
            _type = FrameSubType(_header)
            return _type
        except:
            raise ValueError(f"Frame header {_header} is illigal!")

    @property
    def type(self) -> FrameType:
        subtype_v = self.subtype.value

        if subtype_v < 0b0100:
            return FrameType.FRAME_CONFIG
        elif subtype_v < 0b1000:
            return FrameType.FRAME_TEST
        elif subtype_v < 0b1100:
            return FrameType.FRAME_WORK

        return FrameType.FRAME_UNKNOWN

    @property
    def chip_coord(self) -> Coord:
        _chip_addr: int = (
            self._frame >> FM.GENERAL_CHIP_ADDR_OFFSET) & FM.GENERAL_CHIP_ADDR_MASK
        return Addr2Coord(_chip_addr)

    @property
    def core_coord(self) -> Coord:
        _core_addr: int = (
            self._frame >> FM.GENERAL_CORE_ADDR_OFFSET) & FM.GENERAL_CORE_ADDR_MASK
        return Addr2Coord(_core_addr)

    @property
    def core_star_coord(self) -> Coord:
        _core_star_addr: int = (
            self._frame >> FM.GENERAL_CORE_STAR_ADDR_OFFSET) & FM.GENERAL_CORE_STAR_ADDR_MASK
        return Addr2Coord(_core_star_addr)

    @property
    def payload(self) -> Union[List[int], int]:
        if self._len == 1:
            return (self._frame >> FM.GENERAL_PAYLOAD_OFFSET) & FM.GENERAL_PAYLOAD_MASK

        _payload: List[int] = []

        for i in range(self._len):
            _payload.append(
                (self._frames_group[i] >> FM.GENERAL_PAYLOAD_OFFSET) & FM.GENERAL_PAYLOAD_MASK)

        return _payload

    @property
    def param_reg(self) -> Dict[str, Any]:
        return self._param_reg_dict

    def _decode(self) -> None:
        if self.subtype == FST.CONFIG_TYPE2:
            self._param_reg_parse()
        else:
            raise NotImplementedError

    def info(self) -> None:
        self._general_info()

        if self.type == FrameType.FRAME_CONFIG:
            return self._config_info()
        else:
            raise NotImplementedError

    def _general_info(self) -> None:
        print("General info of frame: 0x%x" % self._frame)
        print("#1  Frame type:         %s" % self.subtype)
        print("#2  Chip address:       [0x%02x | 0x%02x]" % (
            self.chip_coord.x, self.chip_coord.y))
        print("#3  Core address:       [0x%02x | 0x%02x]" % (
            self.core_coord.x, self.core_coord.y))
        print("#4  Core* address:      [0x%02x | 0x%02x]" %
              (self.core_star_coord.x, self.core_star_coord.y))

    def _config_info(self) -> None:
        if self.subtype == FST.CONFIG_TYPE2:
            print("Info of parameter registers")
            print("#1  Weight width:       0x%x" %
                  self._param_reg_dict["weight_width"])
            print("#2  LCN:                0x%x" % self._param_reg_dict["LCN"])
            print("#3  Input width:        0x%x" %
                  self._param_reg_dict["input_width"])
            print("#4  Spike width:        0x%x" %
                  self._param_reg_dict["spike_width"])
            print("#5  Neuron num:         %d" %
                  self._param_reg_dict["neuron_num"])
            print("#6  Pool max enable:    %d" %
                  self._param_reg_dict["pool_max"])
            print("#7  Tick wait start:    0x%x" %
                  self._param_reg_dict["tick_wait_start"])
            print("#8  Tick wait end:      0x%x" %
                  self._param_reg_dict["tick_wait_end"])
            print("#9  SNN enable:         %d" %
                  self._param_reg_dict["SNN_EN"])
            print("#10 Target LCN:         0x%x" %
                  self._param_reg_dict["target_LCN"])
            
            test_chip_coord: Coord = self._param_reg_dict["test_chip_coord"] # type: ignore
            print("#11 Test chip addr:     [0x%02x | 0x%02x]" % (
                test_chip_coord.x, test_chip_coord.y))
        else:
            raise NotImplementedError

    def _test_info(self) -> None:
        if self.subtype == FST.TEST_TYPE2:
            pass
        else:
            raise NotImplementedError

    def _param_reg_parse(self) -> None:
        self._param_reg_dict["weight_width"] = (
            self._frames_group[0] >> CFM.WEIGHT_WIDTH_OFFSET) & CFM.WEIGHT_WIDTH_MASK
        self._param_reg_dict["LCN"] = (
            self._frames_group[0] >> CFM.LCN_OFFSET) & CFM.LCN_MASK
        self._param_reg_dict["input_width"] = (
            self._frames_group[0] >> CFM.INPUT_WIDTH_OFFSET) & CFM.INPUT_WIDTH_MASK
        self._param_reg_dict["spike_width"] = (
            self._frames_group[0] >> CFM.SPIKE_WIDTH_OFFSET) & CFM.SPIKE_WIDTH_MASK
        self._param_reg_dict["neuron_num"] = (
            self._frames_group[0] >> CFM.NEURON_NUM_OFFSET) & CFM.NEURON_NUM_MASK
        self._param_reg_dict["pool_max"] = (
            self._frames_group[0] >> CFM.POOL_MAX_OFFSET) & CFM.POOL_MAX_MASK

        tick_wait_high8 = (
            self._frames_group[0] >> CFM.TICK_WAIT_START_HIGH8_OFFSET) & CFM.TICK_WAIT_START_HIGH8_MASK
        tick_wait_low7 = (
            self._frames_group[1] >> CFM.TICK_WAIT_START_LOW7_OFFSET) & CFM.TICK_WAIT_START_LOW7_MASK
        self._param_reg_dict["tick_wait_start"] = \
            (tick_wait_high8 << CFM.TICK_WAIT_START_COMBINATION_OFFSET) | tick_wait_low7

        self._param_reg_dict["tick_wait_end"] = (
            self._frames_group[1] >> CFM.TICK_WAIT_END_OFFSET) & CFM.TICK_WAIT_END_MASK
        self._param_reg_dict["SNN_EN"] = (
            self._frames_group[1] >> CFM.SNN_EN_OFFSET) & CFM.SNN_EN_MASK
        self._param_reg_dict["target_LCN"] = (
            self._frames_group[1] >> CFM.TARGET_LCN_OFFSET) & CFM.TARGET_LCN_MASK

        high3 = self._frames_group[1] >> CFM.TEST_CHIP_ADDR_HIGH3_OFFSET
        low7 = self._frames_group[2] >> CFM.TEST_CHIP_ADDR_LOW7_OFFSET
        self._param_reg_dict["test_chip_addr"] = test_chip_addr_combine(
            high3, low7)

    def _test_chip_direction(self) -> Direction:
        offset: CoordOffset = self._param_reg_dict["test_chip_coord"] - self.chip_coord # type: ignore

        try:
            direction = Direction(offset)
            return direction
        except ValueError:
            print("Offset is invalid, return the default direction: EAST")
            return Direction("EAST")
