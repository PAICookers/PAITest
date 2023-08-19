from abc import ABC, abstractmethod
from typing import Tuple, Optional
from .params import ParamGenOffline, ParamGenOnline
from .mask import FrameMask as FM
from paitest.coord import Coord, CoreType, ReplicationId
from paitest._types import (
    FrameMainType as FMT,
    FrameSubType as FST,
    FrameArray,
    PackageType,
)


def sub2main_type(subtype: FST) -> FMT:
    if subtype.value <= FST.CONFIG_TYPE4.value:
        return FMT.FRAME_CONFIG
    elif subtype.value <= FST.TEST_IN_TYPE4.value:
        return FMT.FRAME_TEST
    elif subtype.value <= FST.WORK_TYPE4.value:
        return FMT.FRAME_WORK

    return FMT.FRAME_UNKNOWN


def is_type_test_out(subtype: FST) -> bool:
    return (
        subtype is FST.TEST_OUT_TYPE1
        or subtype is FST.TEST_OUT_TYPE2
        or subtype is FST.TEST_OUT_TYPE3
        or subtype is FST.TEST_OUT_TYPE4
    )


class Frame:
    """Single frame which contains information.

    Single frame:
        [Header(sub type)] + [chip coordinate] + [core coordinate] + [replication id] + [payload]
            4 bits               10 bits             10 bits             10 bits         30 bits
    """

    def __init__(
        self,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        payload: int,
    ) -> None:
        """
        Arguments:
            - subtype: sub type of the frame.
            - chip_coord: coordinate of the destination chip.
            - core_coord: coordinate of the destination core.
            - replication_id: the replication identifier.
            - payload: 30-bit data.
        """
        self.sub_type = subtype
        self.chip_coord = chip_coord
        self.core_coord = core_coord
        self.replication_id = replication_id
        self.payload = payload

    @classmethod
    def GenFrame(
        cls,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        payload: int = 0,
    ) -> "Frame":
        return cls(subtype, chip_coord, core_coord, replication_id, payload)

    def __len__(self) -> int:
        return self.length

    @property
    def length(self) -> int:
        return 1

    @property
    def main_type(self) -> FMT:
        return sub2main_type(self.sub_type)

    @property
    def core_type(self) -> CoreType:
        return self.core_coord.core_type

    @property
    def header(self) -> FST:
        return self.sub_type

    @property
    def chip_address(self) -> int:
        return self.chip_coord.address

    @property
    def core_address(self) -> int:
        return self.core_coord.address

    @property
    def replication_address(self) -> int:
        return self.replication_id.address

    @property
    def value(self) -> int:
        return self._fill_payload(self.payload)

    @property
    def frame_common(self):
        header = self.header.value & FM.GENERAL_HEADER_MASK
        chip_addr = self.chip_address & FM.GENERAL_CHIP_ADDR_MASK
        core_addr = self.core_address & FM.GENERAL_CORE_ADDR_MASK
        replication_address = self.replication_address & FM.GENERAL_REPLICATION_ID_MASK

        return (
            (header << FM.GENERAL_HEADER_OFFSET)
            + (chip_addr << FM.GENERAL_CHIP_ADDR_OFFSET)
            + (core_addr << FM.GENERAL_CORE_ADDR_OFFSET)
            + (replication_address << FM.GENERAL_REPLICATION_ID_OFFSET)
        )

    def _fill_payload(self, payload: int) -> int:
        return self.frame_common + payload & FM.GENERAL_PAYLOAD_MASK

    def __repr__(self) -> str:
        return (
            f"Frame info:\n"
            f"Test for:         {self.core_type.value}\n"
            f"Subtype:          {self.sub_type}\n"
            f"Chip address:     {self.chip_coord}\n"
            f"Core address:     {self.core_coord}\n"
            f"Replication ID:   {self.replication_id}\n"
            f"Payload:          {self.payload}\n"
        )


class FrameGroup(Frame):
    """A group of frames of which the payload is split into `N` parts,
    carried by `N` frames which share other configuration items.

    Frame group for a length of `N` payload:
        1. [Header(sub type)] + [chip coordinate] + [core coordinate] + [replication id] + [payload[0]]
               4 bits                10 bits             10 bits             10 bits         30 bits
        2. Same as #1 + [payload[1]]
        N. Same as #1 + [payload[N-1]]

    NOTE: In group of frames, the `payload` is a list of payload in each frame.
    """

    def __init__(
        self,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        payload: FrameArray,
    ) -> None:
        super().__init__(subtype, chip_coord, core_coord, replication_id, 0)

        self._length = len(payload)
        self.payload = payload

        if is_type_test_out(subtype):
            setattr(self, "test_chip_coord", chip_coord)

    @classmethod
    def GenFrameGroup(
        cls,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        payload: FrameArray,
    ) -> "FrameGroup":
        return cls(
            subtype,
            chip_coord,
            core_coord,
            replication_id,
            payload,
        )

    def __getitem__(self, item) -> Frame:
        return super().GenFrame(
            self.sub_type,
            self.chip_coord,
            self.core_coord,
            self.replication_id,
            self.payload[item],
        )

    @property
    def length(self) -> int:
        return self._length

    @property
    def value(self) -> Tuple[int, ...]:
        """Get the full frames of the group."""
        val_list = []
        for load in self.payload:
            val_list.append(self._fill_payload(load))

        return tuple(val_list)

    def __repr__(self):
        _present = (
            f"FrameGroup info:\n"
            f"Type:             {self.sub_type}\n"
            f"Chip address:     {self.chip_coord}\n"
            f"Core address:     {self.core_coord}\n"
            f"Replication ID:   {self.replication_id}\n"
            f"Payload:\n"
        )

        for i in range(self.length):
            _present += f"#{i}: {self.payload[i]}\n"

        return _present


class FramePackage(Frame):
    """A package of frames for pattern III & IV.

    For pattern III & IV, the payload includes:
        - Packages info: the info of the package.
        - Content: the data of the package.

    Frame package for a length of `N` contents:
        1. [Header(sub type)] + [chip coordinate] + [core coordinate] + [replication id] + [info]
               4 bits                10 bits             10 bits             10 bits      30 bits
        2. [contents[0]], 64 bits.
        N+1. [contents[N-1]], 64 bits.

    NOTE: In package of frames, the `payload` is only the info in the first frame.
    """

    def __init__(
        self,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        info: int,
        contents: Optional[FrameArray] = None,
    ) -> None:
        super().__init__(subtype, chip_coord, core_coord, replication_id, info)

        self._info = info
        self.content = contents
        self._length = len(contents) + 1 if isinstance(contents, (list, tuple)) else 1

        if is_type_test_out(subtype):
            setattr(self, "test_chip_coord", chip_coord)

    @classmethod
    def GenFramePackage(
        cls,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        info: int,
        contents: Optional[FrameArray] = None,
    ) -> "FramePackage":
        return cls(
            subtype,
            chip_coord,
            core_coord,
            replication_id,
            info,
            contents,
        )

    @property
    def length(self) -> int:
        return self._length

    @property
    def package_type(self) -> PackageType:
        return PackageType(
            (self.payload >> FM.GENERAL_PACKAGE_TYPE_OFFSET)
            & FM.GENERAL_PACKAGE_TYPE_MASK
        )

    @property
    def start_addr(self) -> int:
        return (
            self._info >> FM.GENERAL_PACKAGE_SRAM_START_ADDR_OFFSET
        ) & FM.GENERAL_PACKAGE_SRAM_START_ADDR_MASK

    @property
    def n_package(self) -> int:
        return (
            self._info >> FM.GENERAL_PACKAGE_COUNT_OFFSET
        ) & FM.GENERAL_PACKAGE_COUNT_MASK

    @property
    def value(self) -> Tuple[int, ...]:
        """Get the full frames of the package."""
        val_list = []

        val_list.append(self._fill_payload(self.payload))
        if self.content:
            val_list.extend(self.content)

        return tuple(val_list)

    def __repr__(self):
        _present = (
            f"FrameGroup info:\n"
            f"Type:             {self.sub_type}\n"
            f"Chip address:     {self.chip_coord}\n"
            f"Core address:     {self.core_coord}\n"
            f"Replication ID:   {self.replication_id}\n"
            f"Start address:  {self.start_addr}\n"
            f"Packages:       {self.n_package}\n"
            f"Data:\n"
        )

        if self.content:
            for i in range(self.length):
                _present += f"#{i}: {self.content[i]}"

        return _present


class FrameGen(ABC):
    @staticmethod
    @abstractmethod
    def GenConfigFrame1() -> FrameGroup:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenConfigFrame2() -> FrameGroup:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenConfigFrame3() -> FramePackage:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenConfigFrame4() -> FramePackage:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestInFrame1() -> Frame:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestOutFrame1() -> FramePackage:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestInFrame2() -> Frame:
        return NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestOutFrame2() -> FrameGroup:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestInFrame3() -> Frame:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestOutFrame3() -> FramePackage:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestInFrame4() -> Frame:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestOutFrame4() -> FramePackage:
        raise NotImplementedError


class FrameGenOffline(FrameGen):
    @staticmethod
    def GenConfigFrame1(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        random_seed: FrameArray,
    ) -> FrameGroup:
        return FrameGroup.GenFrameGroup(
            FST.CONFIG_TYPE1,
            chip_coord,
            core_coord,
            replication_id,
            random_seed,
        )

    @staticmethod
    def GenConfigFrame2(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        param_reg: FrameArray,
    ) -> FrameGroup:
        return FrameGroup.GenFrameGroup(
            FST.CONFIG_TYPE2,
            chip_coord,
            core_coord,
            replication_id,
            param_reg,
        )

    @staticmethod
    def GenConfigFrame3(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int = 0,
        n_neuron_ram: int = 512,
        is_random: bool = True,
    ) -> FramePackage:
        info, contents = ParamGenOffline.GenParamConfig3(
            sram_start_addr, n_neuron_ram, is_random
        )

        return FramePackage.GenFramePackage(
            FST.CONFIG_TYPE3,
            chip_coord,
            core_coord,
            replication_id,
            info,
            contents,
        )

    @staticmethod
    def GenConfigFrame4(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int = 0,
        n_weight_ram: int = 512,
        is_random: bool = True,
    ) -> FramePackage:
        info, contents = ParamGenOffline.GenParamConfig4(
            sram_start_addr, n_weight_ram, is_random
        )

        return FramePackage.GenFramePackage(
            FST.CONFIG_TYPE4,
            chip_coord,
            core_coord,
            replication_id,
            info,
            contents,
        )

    @staticmethod
    def GenTestInFrame1(
        chip_coord: Coord, core_coord: Coord, replication_id: ReplicationId
    ) -> Frame:
        """Test input frame type I"""
        return Frame.GenFrame(
            FST.TEST_IN_TYPE1,
            chip_coord,
            core_coord,
            replication_id,
        )

    @staticmethod
    def GenTestOutFrame1(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        random_seed: FrameArray,
    ) -> FrameGroup:
        return FrameGroup.GenFrameGroup(
            FST.TEST_OUT_TYPE1,
            test_chip_coord,
            core_coord,
            replication_id,
            random_seed,
        )

    @staticmethod
    def GenTestInFrame2(
        chip_coord: Coord, core_coord: Coord, replication_id: ReplicationId
    ) -> Frame:
        return Frame.GenFrame(
            FST.TEST_IN_TYPE2,
            chip_coord,
            core_coord,
            replication_id,
        )

    @staticmethod
    def GenTestOutFrame2(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        param_reg: FrameArray,
    ) -> FrameGroup:
        return FrameGroup.GenFrameGroup(
            FST.TEST_OUT_TYPE2,
            test_chip_coord,
            core_coord,
            replication_id,
            param_reg,
        )

    @staticmethod
    def GenTestInFrame3(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int,
        n_neuron_ram: int,
    ) -> FramePackage:
        if sram_start_addr + n_neuron_ram > 512:
            raise ValueError(
                f"SRAM start address + number of neurons exceeds the limit 512!({sram_start_addr + n_neuron_ram})"
            )

        info = ParamGenOffline.GenRAMInfo(
            sram_start_addr, PackageType.TEST_IN, 4 * n_neuron_ram
        )

        return FramePackage.GenFramePackage(
            FST.TEST_IN_TYPE3,
            chip_coord,
            core_coord,
            replication_id,
            info,
        )

    @staticmethod
    def GenTestOutFrame3(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int,
        n_neuron_ram: int,
        contents: FrameArray,
    ) -> FramePackage:
        if sram_start_addr + n_neuron_ram > 512:
            raise ValueError(
                f"SRAM start address + number of neurons exceeds the limit 512!({sram_start_addr + n_neuron_ram})"
            )

        info = ParamGenOffline.GenRAMInfo(
            sram_start_addr, PackageType.TEST_OUT, 4 * n_neuron_ram
        )

        return FramePackage.GenFramePackage(
            FST.TEST_OUT_TYPE3,
            test_chip_coord,
            core_coord,
            replication_id,
            info,
            contents,
        )

    @staticmethod
    def GenTestInFrame4(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int,
        n_weight_ram: int,
    ) -> FramePackage:
        if sram_start_addr + n_weight_ram > 512:
            raise ValueError(
                f"SRAM start address + number of weight rams exceeds the limit 512!({sram_start_addr + n_weight_ram})"
            )

        info = ParamGenOffline.GenRAMInfo(
            sram_start_addr, PackageType.TEST_IN, 18 * n_weight_ram
        )

        return FramePackage.GenFramePackage(
            FST.TEST_IN_TYPE4,
            chip_coord,
            core_coord,
            replication_id,
            info,
        )

    @staticmethod
    def GenTestOutFrame4(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int,
        n_weight_ram: int,
        contents: FrameArray,
    ) -> FramePackage:
        if sram_start_addr + n_weight_ram > 512:
            raise ValueError(
                f"SRAM start address + number of weight rams exceeds the limit 512!({sram_start_addr + n_weight_ram})"
            )

        info = ParamGenOffline.GenRAMInfo(
            sram_start_addr, PackageType.TEST_OUT, 18 * n_weight_ram
        )

        return FramePackage.GenFramePackage(
            FST.TEST_OUT_TYPE4,
            test_chip_coord,
            core_coord,
            replication_id,
            info,
            contents,
        )


class FrameGenOnline(FrameGen):
    @staticmethod
    def GenConfigFrame1(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        lut: FrameArray,
    ) -> FrameGroup:
        return FrameGroup.GenFrameGroup(
            FST.CONFIG_TYPE1, chip_coord, core_coord, replication_id, lut
        )

    @staticmethod
    def GenConfigFrame2(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        core_reg: FrameArray,
    ) -> FrameGroup:
        return FrameGroup.GenFrameGroup(
            FST.CONFIG_TYPE2, chip_coord, core_coord, replication_id, core_reg
        )

    @staticmethod
    def GenConfigFrame3(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        neuron_start_addr: int = 0,
        n_neuron_ram: int = 1024,
        is_random: bool = True,
    ) -> FramePackage:
        info, contents = ParamGenOnline.GenParamConfig3(
            neuron_start_addr, n_neuron_ram, is_random
        )

        return FramePackage.GenFramePackage(
            FST.CONFIG_TYPE3, chip_coord, core_coord, replication_id, info, contents
        )

    @staticmethod
    def GenConfigFrame4(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        neuron_start_addr: int = 0,
        n_neuron_ram: int = 1024,
        is_random: bool = True,
    ) -> FramePackage:
        info, contents = ParamGenOnline.GenParamConfig4(
            neuron_start_addr, n_neuron_ram, is_random
        )

        return FramePackage.GenFramePackage(
            FST.CONFIG_TYPE4, chip_coord, core_coord, replication_id, info, contents
        )

    @staticmethod
    def GenTestInFrame1(
        chip_coord: Coord, core_coord: Coord, replication_id: ReplicationId
    ) -> Frame:
        return Frame.GenFrame(
            FST.TEST_IN_TYPE1,
            chip_coord,
            core_coord,
            replication_id,
        )

    @staticmethod
    def GenTestOutFrame1(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        lut: FrameArray,
    ) -> FrameGroup:
        return FrameGroup.GenFrameGroup(
            FST.TEST_OUT_TYPE1, test_chip_coord, core_coord, replication_id, lut
        )

    @staticmethod
    def GenTestInFrame2(
        chip_coord: Coord, core_coord: Coord, replication_id: ReplicationId
    ) -> Frame:
        return Frame.GenFrame(
            FST.TEST_IN_TYPE2,
            chip_coord,
            core_coord,
            replication_id,
        )

    @staticmethod
    def GenTestOutFrame2(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        core_reg: FrameArray,
    ) -> Frame:
        return FrameGroup.GenFrameGroup(
            FST.TEST_OUT_TYPE2, test_chip_coord, core_coord, replication_id, core_reg
        )

    @staticmethod
    def GenTestInFrame3(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        neuron_start_addr: int,
        n_neuron_ram: int,
    ) -> FramePackage:
        if neuron_start_addr + n_neuron_ram > 1024:
            raise ValueError(
                f"Neurons start address + number of neuron rams exceeds the limit 1024!({neuron_start_addr + n_neuron_ram})"
            )

        n_package = 2 * n_neuron_ram
        info = ParamGenOnline.GenRAMInfo(
            neuron_start_addr, PackageType.TEST_IN, n_package
        )

        return FramePackage.GenFramePackage(
            FST.TEST_IN_TYPE3,
            chip_coord,
            core_coord,
            replication_id,
            info,
        )

    @staticmethod
    def GenTestOutFrame3(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        neuron_start_addr: int,
        n_neuron_ram: int,
        contents: FrameArray,
    ) -> FramePackage:
        if neuron_start_addr + n_neuron_ram > 1024:
            raise ValueError(
                f"Neurons start address + number of neuron rams exceeds the limit 1024!({neuron_start_addr + n_neuron_ram})"
            )

        n_package = 2 * n_neuron_ram
        info = ParamGenOnline.GenRAMInfo(
            neuron_start_addr, PackageType.TEST_OUT, n_package
        )

        return FramePackage.GenFramePackage(
            FST.TEST_OUT_TYPE3,
            test_chip_coord,
            core_coord,
            replication_id,
            info,
            contents,
        )

    @staticmethod
    def GenTestInFrame4(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        neuron_start_addr: int,
        n_neuron_ram: int,
    ) -> FramePackage:
        if neuron_start_addr + n_neuron_ram > 1024:
            raise ValueError(
                f"Neurons start address + number of neuron rams exceeds the limit 1024!({neuron_start_addr + n_neuron_ram})"
            )

        n_package = 16 * n_neuron_ram
        info = ParamGenOnline.GenRAMInfo(
            neuron_start_addr, PackageType.TEST_IN, n_package
        )

        return FramePackage.GenFramePackage(
            FST.TEST_IN_TYPE4,
            chip_coord,
            core_coord,
            replication_id,
            info,
        )

    @staticmethod
    def GenTestOutFrame4(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        neuron_start_addr: int,
        n_neuron_ram: int,
        contents: FrameArray,
    ) -> FramePackage:
        if neuron_start_addr + n_neuron_ram > 1024:
            raise ValueError(
                f"Neurons start address + number of neuron rams exceeds the limit 1024!({neuron_start_addr + n_neuron_ram})"
            )

        n_package = 16 * n_neuron_ram
        info = ParamGenOnline.GenRAMInfo(
            neuron_start_addr, PackageType.TEST_OUT, n_package
        )

        return FramePackage.GenFramePackage(
            FST.TEST_OUT_TYPE4,
            test_chip_coord,
            core_coord,
            replication_id,
            info,
            contents,
        )
