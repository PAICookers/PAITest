from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from .coord import Coord, ReplicationId
from .frames import (
    Frame,
    FrameGroup,
    FramePackage,
    FrameGenOffline,
    FrameGenOnline,
    ParamGenOffline,
    ParamGenOnline,
)
from .frames.params import gen_package_info_for_group


__all__ = ["GroupGenOffline", "GroupGenOnline"]


class GroupGen(ABC):
    @staticmethod
    @abstractmethod
    def gen_group1() -> ...:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def gen_group2() -> ...:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def gen_group3() -> ...:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def gen_group4() -> ...:
        raise NotImplementedError


class GroupGenOffline(GroupGen):
    @staticmethod
    def gen_group1(
        test_chip_coord: Coord,
        chip_coord: Coord,
        core_coord: Coord,
        rid: ReplicationId,
        *,
        is_random: bool,
        seed: Optional[int] = None,
    ) -> Tuple[FrameGroup, FrameGroup, Frame]:
        random_seed = ParamGenOffline.gen_param_config1(is_random, seed)

        c = FrameGenOffline.gen_config_frame1(chip_coord, core_coord, rid, random_seed)
        to = FrameGenOffline.gen_testout_frame1(
            test_chip_coord, core_coord, rid, random_seed
        )
        ti = FrameGenOffline.gen_testin_frame1(chip_coord, core_coord, rid)

        return c, to, ti

    @staticmethod
    def gen_group2(
        test_chip_coord: Coord,
        chip_coord: Coord,
        core_coord: Coord,
        rid: ReplicationId,
        *,
        is_random: bool,
        **kwargs,
    ) -> Tuple[FrameGroup, FrameGroup, Frame]:
        param_reg = ParamGenOffline.gen_param_config2(
            test_chip_coord, is_random, **kwargs
        )

        c = FrameGenOffline.gen_config_frame2(chip_coord, core_coord, rid, param_reg)
        to = FrameGenOffline.gen_testout_frame2(
            test_chip_coord, core_coord, rid, param_reg
        )
        ti = FrameGenOffline.gen_testin_frame2(chip_coord, core_coord, rid)

        return c, to, ti

    @staticmethod
    def gen_group3(
        test_chip_coord: Coord,
        chip_coord: Coord,
        core_coord: Coord,
        rid: ReplicationId,
        *,
        sram_start_addr: int,
        n_neuron_ram: int,
    ) -> Tuple[FramePackage, FramePackage, FramePackage]:
        infos = gen_package_info_for_group(sram_start_addr, 4 * n_neuron_ram)
        contents = ParamGenOffline.gen_param_config3(
            sram_start_addr, n_neuron_ram, True
        )
        c = FrameGenOffline.gen_config_frame3(
            chip_coord, core_coord, rid, infos[0], contents
        )

        to = FrameGenOffline.gen_testout_frame3(
            test_chip_coord,
            core_coord,
            rid,
            infos[1],
            contents,
        )

        ti = FrameGenOffline.gen_testin_frame3(chip_coord, core_coord, rid, infos[2])

        return c, to, ti

    @staticmethod
    def gen_group4(
        test_chip_coord: Coord,
        chip_coord: Coord,
        core_coord: Coord,
        rid: ReplicationId,
        *,
        sram_start_addr: int,
        n_weight_ram: int,
    ) -> Tuple[FramePackage, FramePackage, FramePackage]:
        infos = gen_package_info_for_group(sram_start_addr, 18 * n_weight_ram)
        contents = ParamGenOffline.gen_param_config4(
            sram_start_addr, n_weight_ram, True
        )
        c = FrameGenOffline.gen_config_frame4(
            chip_coord, core_coord, rid, infos[0], contents
        )

        to = FrameGenOffline.gen_testout_frame4(
            test_chip_coord,
            core_coord,
            rid,
            infos[1],
            contents,
        )

        ti = FrameGenOffline.gen_testin_frame4(chip_coord, core_coord, rid, infos[2])

        return c, to, ti


class GroupGenOnline(GroupGen):
    @staticmethod
    def gen_group1(
        test_chip_coord: Coord,
        chip_coord: Coord,
        core_coord: Coord,
        rid: ReplicationId,
        *,
        is_random: bool,
        lut: Optional[List[int]] = None,
    ) -> Tuple[FrameGroup, FrameGroup, Frame]:
        lut_params = ParamGenOnline.gen_param_config1(is_random, lut)

        c = FrameGenOnline.gen_config_frame1(chip_coord, core_coord, rid, lut_params)
        to = FrameGenOnline.gen_testout_frame1(
            test_chip_coord, core_coord, rid, lut_params
        )
        ti = FrameGenOnline.gen_testin_frame1(chip_coord, core_coord, rid)

        return c, to, ti

    @staticmethod
    def gen_group2(
        test_chip_coord: Coord,
        chip_coord: Coord,
        core_coord: Coord,
        rid: ReplicationId,
        *,
        is_random: bool,
    ) -> Tuple[FrameGroup, FrameGroup, Frame]:
        core_reg = ParamGenOnline.gen_param_config2(test_chip_coord, is_random)

        c = FrameGenOnline.gen_config_frame2(chip_coord, core_coord, rid, core_reg)
        to = FrameGenOnline.gen_testout_frame2(
            test_chip_coord, core_coord, rid, core_reg
        )
        ti = FrameGenOnline.gen_testin_frame2(chip_coord, core_coord, rid)

        return c, to, ti

    @staticmethod
    def gen_group3(
        test_chip_coord: Coord,
        chip_coord: Coord,
        core_coord: Coord,
        rid: ReplicationId,
        *,
        neuron_start_addr: int,
        n_neuron_ram: int,
    ) -> Tuple[FramePackage, FramePackage, FramePackage]:
        infos = gen_package_info_for_group(neuron_start_addr, 2 * n_neuron_ram)
        contents = ParamGenOnline.gen_param_config3(
            neuron_start_addr, n_neuron_ram, True
        )

        c = FrameGenOnline.gen_config_frame3(
            chip_coord, core_coord, rid, infos[0], contents
        )
        to = FrameGenOnline.gen_testout_frame3(
            test_chip_coord, core_coord, rid, infos[1], contents
        )
        ti = FrameGenOnline.gen_testin_frame3(chip_coord, core_coord, rid, infos[2])

        return c, to, ti

    @staticmethod
    def gen_group4(
        test_chip_coord: Coord,
        chip_coord: Coord,
        core_coord: Coord,
        rid: ReplicationId,
        *,
        neuron_start_addr: int,
        n_neuron_ram: int,
    ) -> Tuple[FramePackage, FramePackage, FramePackage]:
        infos = gen_package_info_for_group(neuron_start_addr, 16 * n_neuron_ram)
        contents = ParamGenOnline.gen_param_config4(
            neuron_start_addr, n_neuron_ram, True
        )

        c = FrameGenOnline.gen_config_frame4(
            chip_coord, core_coord, rid, infos[0], contents
        )
        to = FrameGenOnline.gen_testout_frame4(
            test_chip_coord, core_coord, rid, infos[1], contents
        )
        ti = FrameGenOnline.gen_testin_frame4(chip_coord, core_coord, rid, infos[2])

        return c, to, ti
