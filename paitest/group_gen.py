from typing import Optional, Tuple
from .coord import Coord, ReplicationId
from .frames import Frame, FrameGroup, FramePackage, FrameGenOffline, ParamGenOffline
from .frames.params import gen_package_info_for_group


__all__ = ["GroupGenOffline"]


class GroupGenOffline:
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

        to = FrameGenOffline.gen_testout_frame2(chip_coord, core_coord, rid, param_reg)

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
        if sram_start_addr + n_neuron_ram > 512:
            raise ValueError(
                f"SRAM start address + number of neurons exceeds the limit 512!({sram_start_addr + n_neuron_ram})"
            )

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
        if sram_start_addr + n_weight_ram > 512:
            raise ValueError(
                f"SRAM start address + number of neurons exceeds the limit 512!({sram_start_addr + n_weight_ram})"
            )

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
