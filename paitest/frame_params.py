from enum import Enum, unique
from typing import List
from pydantic import BaseModel, Field, Extra, root_validator
from .frame_utils import ConfigFrameMasks as CFM


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


class ParameterReg(BaseModel, extra=Extra.ignore):

    weight_width_type: WeightPrecisionTypes = Field(
        default=WeightPrecisionTypes.WEIGHT_WIDTH_1BIT)

    lcn_type: LCNTypes = Field(default=LCNTypes.LCN_1X)

    input_width_type: InputWidthTypes = Field(
        default=InputWidthTypes.INPUT_WIDTH_8BIT)

    spike_width_type: SpikeWidthTypes = Field(
        default=SpikeWidthTypes.SPIKE_WIDTH_8BIT)

    neuron_num: int = Field(default=4096)
    pool_max_en: bool = Field(default=False)
    tick_wait_start: int = Field(default=0)
    tick_wait_end: int = Field(default=0)
    snn_en: bool = Field(default=True)
    target_lcn: int = Field(default=0)
    test_chip_addr: int = Field(default=0)

    @root_validator
    def neuron_num_check(cls, values):
        if values.get("input_width_type") == InputWidthTypes.INPUT_WIDTH_8BIT:
            if values.get("neuron_num") > 4096:
                raise ValueError(
                    "When using 8-bit input mode, neuron_num <= 4096")
        else:
            if values.get("neuron_num") > 512:
                raise ValueError(
                    "When using 1-bit input mode, neuron_num <= 512")

        return values

    def GetPayloadList(self) -> List[int]:
        return [
            (self.weight_width_type.value << CFM.WEIGHT_WIDTH_OFFSET) |
            (self.lcn_type.value << CFM.LCN_OFFSET) |
            (self.input_width_type.value << CFM.INPUT_WIDTH_OFFSET) |
            (self.spike_width_type.value << CFM.SPIKE_WIDTH_OFFSET) |
            (self.neuron_num << CFM.NEURON_NUM_OFFSET) |
            (self.pool_max_en << CFM.POOL_MAX_OFFSET) |
            ((self.tick_wait_start >> CFM.TICK_WAIT_START_HIGH8_OFFSET)),

            ((self.tick_wait_start & CFM.TICK_WAIT_START_LOW7_MASK) << CFM.TICK_WAIT_START_LOW7_OFFSET) |
            (self.tick_wait_end << CFM.TICK_WAIT_END_OFFSET) |
            (self.snn_en << CFM.SNN_EN_OFFSET) |
            (self.target_lcn << CFM.TARGET_LCN_OFFSET) |
            ((self.test_chip_addr >> CFM.TEST_CHIP_ADDR_HIGH3_OFFSET)),

            (self.test_chip_addr &
             CFM.TEST_CHIP_ADDR_LOW7_MASK) << CFM.TEST_CHIP_ADDR_LOW7_OFFSET
        ]


if __name__ == "__main__":
    payload = ParameterReg(
        weight_width_type=WeightPrecisionTypes.WEIGHT_WIDTH_1BIT,
        lcn_type=LCNTypes.LCN_64X,
        input_width_type=InputWidthTypes.INPUT_WIDTH_1BIT,
        spike_width_type=SpikeWidthTypes.SPIKE_WIDTH_8BIT,
        neuron_num=122,
        pool_max_en=True,
        tick_wait_start=0x123f,
        tick_wait_end=0,
        snn_en=True,
        target_lcn=0,
        test_chip_addr=0x123
    )
