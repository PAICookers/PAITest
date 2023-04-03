from .frame_utils import FrameTypes as FT, FrameMasks as FM
from .frame_params import *
from typing import List, Tuple, Union


def GenFrame(
    header: int,
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

    return (header << FM.GENERAL_HEADER_OFFSET) | \
        (chip_addr << FM.GENERAL_CORE_ADDR_OFFSET) | \
        (core_addr << FM.GENERAL_CORE_ADDR_OFFSET) | \
        (core_star_addr << FM.GENERAL_CORE_STAR_ADDR_OFFSET) | \
        (payload << FM.GENERAL_PAYLOAD_OFFSET)


def GenConfig1Frame(
    chip_addr: int = 0,
    core_addr: int = 0,
    core_star_addr: int = 0,
    random_seed: int = ...,
    test_ref_out_included: bool = ...
) -> Union[List[int], Tuple[List[int], List[int]]]:

    payload_list: List[int] = [
        random_seed >> 34,
        random_seed >> 4,
        random_seed & 0xf << 26
    ]
    frames: List[int] = []
    ref_out_frames: List[int] = []

    for p in payload_list:
        frames.append(GenFrame(FT.CONFIG_TYPE1.value,
                      chip_addr, core_addr, core_star_addr, p))

    if test_ref_out_included:
        ref_out_frames.append(
            GenFrame(FT.TEST_TYPE1.value, chip_addr, core_addr, core_star_addr, p))

        return frames, ref_out_frames

    return frames


def GenConfig2Frame(
    chip_addr: int = 0,
    core_addr: int = 0,
    core_star_addr: int = 0,
    weight_width_type: WeightPrecisionTypes = ...,
    lcn_type: LCNTypes = ...,
    input_width_type: InputWidthTypes = ...,
    spike_width_type: SpikeWidthTypes = ...,
    neuron_num: int = ...,
    pool_max_en: bool = ...,
    tick_wait_start: int = ...,
    tick_wait_end: int = ...,
    snn_en: bool = ...,
    target_lcn: int = ...,
    test_chip_addr: int = ...,
    test_ref_out_included: bool = ...
) -> Union[List[int], Tuple[List[int], List[int]]]:

    payload_list: List[int] = []
    frames: List[int] = []
    ref_out_frames: List[int] = []

    pr = ParameterReg(
        weight_width_type=weight_width_type,
        lcn_type=lcn_type,
        input_width_type=input_width_type,
        spike_width_type=spike_width_type,
        neuron_num=neuron_num,
        pool_max_en=pool_max_en,
        tick_wait_start=tick_wait_start,
        tick_wait_end=tick_wait_end,
        snn_en=snn_en,
        target_lcn=target_lcn,
        test_chip_addr=test_chip_addr
    )
    payload_list = pr.GetPayloadList()

    for p in payload_list:
        frames.append(GenFrame(FT.CONFIG_TYPE2.value,
                      chip_addr, core_addr, core_star_addr, p))

        if test_ref_out_included:
            ref_out_frames.append(
                GenFrame(FT.TEST_TYPE2.value, chip_addr, core_addr, core_star_addr, p))

    if test_ref_out_included:
        return frames, ref_out_frames

    return frames


def GenTestInFrame(
    header_type: FT,
    chip_addr: int = 0,
    core_addr: int = 0,
    core_star_addr: int = 0,
    sram_start_addr: int = ...,
    package_num: int = ...,
) -> int:

    header: int = header_type.value

    if header_type == FT.TEST_TYPE1:
        payload = 0
    elif header_type == FT.TEST_TYPE2:
        payload = 0
    else:
        payload = (sram_start_addr << FM.GENERAL_PACKAGE_SRAM_START_ADDR_OFFSET) | \
            (1 << FM.GENERAL_PACKAGE_TYPE_OFFSET) | \
            (package_num << FM.GENERAL_PACKAGE_COUNT_OFFSET)

    return GenFrame(header, chip_addr, core_addr, core_star_addr, payload)


class FrameGen:

    @staticmethod
    def GenConfig1FrameGroup(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0,
        random_seed: int = ...,
        test_ref_out_included: bool = ...
    ) -> Union[List[int], Tuple[List[int], List[int]]]:
        return GenConfig1Frame(chip_addr, core_addr, core_star_addr, random_seed, test_ref_out_included)

    @staticmethod
    def GenConfig2FrameGroup(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0,
        weight_width_type: WeightPrecisionTypes = ...,
        lcn_type: LCNTypes = ...,
        input_width_type: InputWidthTypes = ...,
        spike_width_type: SpikeWidthTypes = ...,
        neuron_num: int = ...,
        pool_max_en: bool = ...,
        tick_wait_start: int = ...,
        tick_wait_end: int = ...,
        snn_en: bool = ...,
        target_lcn: int = ...,
        test_chip_addr: int = ...,
        test_ref_out_included: bool = ...
    ) -> Union[List[int], Tuple[List[int], List[int]]]:
        return GenConfig2Frame(
            chip_addr, core_addr, core_star_addr,
            weight_width_type=weight_width_type, lcn_type=lcn_type, input_width_type=input_width_type,
            spike_width_type=spike_width_type, neuron_num=neuron_num, pool_max_en=pool_max_en, tick_wait_start=tick_wait_start,
            tick_wait_end=tick_wait_end, snn_en=snn_en, target_lcn=target_lcn, test_chip_addr=test_chip_addr,
            test_ref_out_included=test_ref_out_included
        )

    @staticmethod
    def GenTest1InFrame(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0
    ) -> int:
        return GenTestInFrame(FT.TEST_TYPE1, chip_addr, core_addr, core_star_addr)

    @staticmethod
    def GenTest1OutRef(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0
    ) -> int:
        return GenTestInFrame(FT.TEST_TYPE1, chip_addr, core_addr, core_star_addr)

    @staticmethod
    def GenTest2InFrame(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0
    ) -> int:
        return GenTestInFrame(FT.TEST_TYPE2, chip_addr, core_addr, core_star_addr)

    @staticmethod
    def GenTest3InFrame(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0,
        sram_start_addr: int = 0,
        package_num: int = 0
    ) -> int:
        return GenTestInFrame(
            FT.TEST_TYPE3, chip_addr, core_addr, core_star_addr, sram_start_addr=sram_start_addr, package_num=package_num)

    @staticmethod
    def GenTest4InFrame(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0,
        sram_start_addr: int = 0,
        package_num: int = 0
    ) -> int:
        return GenTestInFrame(
            FT.TEST_TYPE4, chip_addr, core_addr, core_star_addr, sram_start_addr=sram_start_addr, package_num=package_num)
