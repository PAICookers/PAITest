from .frame_params import FrameConfigTypes as FCT, \
    FrameTestTypes as FTT, FrameWorkTypes as FWT, \
    FrameMasks as FM
from .frame_params import *
from typing import List, Tuple, Union, TypeVar

SUB_TYPES = TypeVar('SUB_TYPES', FCT, FTT, FWT)
T = TypeVar('T')
R = TypeVar('R')


class FrameGen:

    @staticmethod
    def GenFrame(header: int,
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
            frames.append(FrameGen.GenConfigFrame(FCT.CONFIG_TYPE2,
                                                  chip_addr, core_addr, core_star_addr, p))

            if test_ref_out_included:
                ref_out_frames.append(
                    FrameGen.GenTest2OutFrame(
                        test_chip_addr, core_addr, core_star_addr, p)
                )

        if test_ref_out_included:
            return frames, ref_out_frames

        return frames

    @staticmethod
    def GenConfigFrame(header: FCT,
                       chip_addr: int,
                       core_addr: int,
                       core_star_addr: int,
                       payload: int
                       ) -> int:
        return FrameGen.GenFrame(header.value, chip_addr, core_addr, core_star_addr, payload)

    '''Functions of Test Frames Generation'''
    @staticmethod
    def GenTestFrame(header: FTT,
                     chip_addr: int,
                     core_addr: int,
                     core_star_addr: int,
                     payload: int = 0
                     ) -> int:
        return FrameGen.GenFrame(header.value, chip_addr, core_addr, core_star_addr, payload)

    @staticmethod
    def GenTest1InFrame(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0
    ) -> int:
        return FrameGen.GenTestFrame(FTT.TEST_TYPE1, chip_addr, core_addr, core_star_addr)

    @staticmethod
    def GenTest1OutFrame(
        test_chip_addr: int = ...,
        core_addr: int = 0,
        core_star_addr: int = 0,
        random_seed: int = ...
    ) -> int:
        return FrameGen.GenTestFrame(FTT.TEST_TYPE1, test_chip_addr, core_addr, core_star_addr, random_seed)

    @staticmethod
    def GenTest2InFrame(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0
    ) -> int:
        return FrameGen.GenTestFrame(FTT.TEST_TYPE2, chip_addr, core_addr, core_star_addr)

    @staticmethod
    def GenTest2OutFrame(
        test_chip_addr: int = ...,
        core_addr: int = 0,
        core_star_addr: int = 0,
        reg_parameters: int = ...
    ) -> int:
        return FrameGen.GenTestFrame(FTT.TEST_TYPE2, test_chip_addr, core_addr, core_star_addr, reg_parameters)

    @staticmethod
    def GenTest3InFrame(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0,
        package_info: int = ...
    ) -> int:
        return FrameGen.GenTestFrame(FTT.TEST_TYPE3, chip_addr, core_addr, core_star_addr, package_info)

    @staticmethod
    def GenTest3OutFrame(
        test_chip_addr: int = ...,
        core_addr: int = 0,
        core_star_addr: int = 0
    ) -> None:
        pass

    @staticmethod
    def GenTest4InFrame(
        chip_addr: int = 0,
        core_addr: int = 0,
        core_star_addr: int = 0,
        package_info: int = ...
    ) -> int:
        return FrameGen.GenTestFrame(FTT.TEST_TYPE4, chip_addr, core_addr, core_star_addr, package_info)


class FrameUtils:

    @staticmethod
    def isFrame(frame: bytes, frame_type: FrameTypes) -> bool:
        return frame_type.value == frame[0] >> 4

    @staticmethod
    def isSubFrame(frame: bytes, frame_subtype: SUB_TYPES) -> bool:
        return frame_subtype.value == frame[0] >> 4
