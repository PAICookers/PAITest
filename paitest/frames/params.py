from abc import ABC, abstractmethod
import random
from typing import Optional, Tuple
import warnings
from paitest.utils import bin_split, bin_combine, bin_combine_x
from .mask import FrameMask as FM, OfflineConfigFrameMask as OFF_CFM
from paitest._types import PackageType
from paitest.coord import Coord


def test_chip_coord_split(coord: Coord) -> Tuple[int, int]:
    return bin_split(coord.address, 7, high_mask=OFF_CFM.TEST_CHIP_ADDR_HIGH3_MASK)


def test_chip_addr_combine(high3: int, low7: int) -> Coord:
    _high3 = high3 & OFF_CFM.TEST_CHIP_ADDR_HIGH3_MASK
    _low7 = low7 & OFF_CFM.TEST_CHIP_ADDR_LOW7_MASK
    addr = bin_combine(_high3, _low7, OFF_CFM.TEST_CHIP_ADDR_COMBINATION_OFFSET)

    return Coord.from_tuple(bin_split(addr, 5))


class ParamGen(ABC):
    @staticmethod
    @abstractmethod
    def GenParamConfig1() -> ...:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenParamConfig2() -> ...:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenParamConfig3() -> ...:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenParamConfig4() -> ...:
        raise NotImplementedError

    @staticmethod
    def GenRAMInfo(start_addr: int, _type: PackageType, n_package: int) -> int:
        return bin_combine_x(
            start_addr,
            _type.value,
            n_package,
            pos=[
                OFF_CFM.GENERAL_PACKAGE_SRAM_START_ADDR_OFFSET,
                OFF_CFM.GENERAL_PACKAGE_TYPE_OFFSET,
            ],
        )


class ParamGenOffline(ParamGen):
    """Parameter generation methods for offline cores"""

    @staticmethod
    def GenParamConfig1(
        is_random: bool = True, *, seed: Optional[int] = None
    ) -> Tuple[int, ...]:
        """Generate random seed for configuration frame & test output frame type I.

        Random seed = [30bit] + [30bit] + [26'b0 + 4bit]
        """
        if is_random:
            seed = random.randint(0, FM.GENERAL_MASK)
        else:
            if not isinstance(seed, int):
                raise ValueError

            if seed > FM.GENERAL_MASK:
                warnings.warn(
                    f"seed {seed} is too large, truncated into 64 bits!", UserWarning
                )

            seed = seed & FM.GENERAL_MASK

        return (
            (seed >> 34) & FM.GENERAL_PAYLOAD_MASK,
            (seed >> 4) & FM.GENERAL_PAYLOAD_MASK,
            seed & ((1 << 4) - 1),
        )

    @staticmethod
    def GenParamConfig2(
        test_chip_coord: Coord,
        is_random: bool = True,
        *,
        weight_width: Optional[int] = None,
        lcn_type: Optional[int] = None,
        input_width: Optional[int] = None,
        spike_width: Optional[int] = None,
        neuron_num: Optional[int] = None,
        pool_max: Optional[int] = None,
        tick_wait_start: Optional[int] = None,
        tick_wait_end: Optional[int] = None,
        snn_en: Optional[int] = None,
        target_lcn: Optional[int] = None,
    ) -> Tuple[int, ...]:
        """Generate parameter register for configuration frame and test out frame type II"""

        high3, low7 = test_chip_coord_split(test_chip_coord)

        params = []

        if is_random:
            for i in range(2):
                params.append(random.randint(0, FM.GENERAL_PAYLOAD_MASK))

            params[1] = (params[1] & (~OFF_CFM.TEST_CHIP_ADDR_HIGH3_MASK)) + high3
            params.append(low7 << OFF_CFM.TEST_CHIP_ADDR_LOW7_OFFSET)
        else:
            raise NotImplementedError

        return tuple(params)

    @staticmethod
    def GenParamConfig3(
        sram_start_addr: int, n_neuron_ram: int, is_random: bool = True
    ) -> Tuple[int, Tuple[int, ...]]:
        """Generate neuron RAM for configuration froame type III.

        Arguments:
            - sram_start_addr: the start address of SRAM.
            - n_neuron_ram: the number of neurons to be configured.
            - is_random: whether to gererate parameters randomly.(not implemented yet)

        For pattern III, the payload includes:
            - Packages info: the info of the package.
            - Content: the data of the package.

        NOTE: `n_package` = 4 * `n_neuron_ram`.
              `sram_start_addr` + `n_neuron_ram` <= 512.
        """
        if sram_start_addr + n_neuron_ram > 512:
            raise ValueError(
                f"SRAM start address + number of neuron rams exceeds the limit 512! {sram_start_addr + n_neuron_ram}"
            )

        info = super().GenRAMInfo(sram_start_addr, PackageType.CONFIG, 4 * n_neuron_ram)

        contents = []
        if is_random:
            for i in range(3):
                contents.append(random.randint(0, FM.GENERAL_MASK))

            contents.append(random.randint(0, (1 << 22) - 1))
        else:
            raise NotImplementedError

        return info, tuple(contents)

    @staticmethod
    def GenParamConfig4(
        sram_start_addr: int, n_weight_ram: int, is_random: bool = True
    ) -> Tuple[int, Tuple[int, ...]]:
        """Generate weight RAM for configuration frame IV.

        Arguments:
            - sram_start_addr: the start address of SRAM.
            - n_weight_ram: the number of weights to be configured.
            - is_random: whether to gererate parameters randomly.(not implemented yet)

        For pattern IV, the payload includes:
            - Packages info: the info of the package.
            - Content: the data of the package.

        NOTE: `n_package` = 18 * `n_weight_ram`.
              `sram_start_addr` + `n_weight_ram` <= 512
        """
        if sram_start_addr + n_weight_ram > 512:
            raise ValueError(
                f"SRAM start address + number of weight rams exceeds the limit 512! {sram_start_addr + n_weight_ram}"
            )

        info = super().GenRAMInfo(
            sram_start_addr, PackageType.CONFIG, 18 * n_weight_ram
        )

        contents = []
        if is_random:
            for i in range(n_weight_ram):
                contents.append(random.randint(0, FM.GENERAL_MASK))
        else:
            raise NotImplementedError

        return info, tuple(contents)

    GenRandomSeed = GenParamConfig1
    GenParamReg = GenParamConfig2
    GenNeuronRAM = GenParamConfig3
    GenWeightRAM = GenParamConfig4


class ParamGenOnline(ParamGen):
    """Parameter generation methods for online cores"""

    @staticmethod
    def GenParamConfig1():
        """Generate LUT for configuration frame I"""
        pass

    @staticmethod
    def GenParamConfig2():
        """Generate core parameter for configuration frame II"""
        pass

    @staticmethod
    def GenParamConfig3():
        """Generate neuron RAM for configuration frame III"""
        pass

    @staticmethod
    def GenParamConfig4():
        """Generate weight RAM for configuration frame IV"""
        pass

    GenLUT = GenParamConfig1
    GenCoreParam = GenParamConfig2
    GenNeuronRAM = GenParamConfig3
    GenWeightRAM = GenParamConfig4
