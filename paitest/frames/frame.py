from abc import ABC, abstractmethod
from typing import Tuple
from .params import ParamGenOffline
from .mask import FrameMask as FM
from paitest.coord import Coord, ReplicationId
from paitest._types import FrameSubType as FST, FrameArray, PackageType


class Frame:
    """Single frame which contains information.

    Single frame:
        [Header(sub type)] + [chip coordinate] + [core coordinate] + [replication id] + [payload]
              4 bits             10 bits             10 bits             10 bits         30 bits
    """

    def __init__(
        self,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        payload: int = 0,
    ) -> None:
        """
        Arguments:
            - subtype: sub type of frame.
            - chip_coord: coordinate of the destination chip.
            - core_coord: coordinate of the destination core.
            - replication_id: the replication identifier.
            - payload: 30-bit data.
        """
        self.subtype = subtype
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
        payload: int,
    ) -> "Frame":
        return cls(subtype, chip_coord, core_coord, replication_id, payload)

    def __len__(self) -> int:
        return self.length

    @property
    def length(self) -> int:
        return 1

    @property
    def frame_type(self) -> FST:
        return self.subtype

    @property
    def header(self) -> FST:
        return self.subtype

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
        header = self.header & FM.GENERAL_HEADER_MASK
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


class FrameGroup(Frame):
    """A group of frames of which the payload is split into `N` parts,
    carried by `N` frames which share other configuration items.

    Frame group for a length of `N` payload:
        1. [Header(sub type)] + [chip coordinate] + [core coordinate] + [replication id] + [payload[0]]
               4 bits                10 bits             10 bits             10 bits         30 bits
        2. Same as #1 + [payload[1]]
        N. Same as #1 + [payload[N-1]]
    """

    def __init__(
        self,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        payload: FrameArray,
    ) -> None:
        super().__init__(subtype, chip_coord, core_coord, replication_id)

        self._length = len(payload)
        self.payload = payload

    @classmethod
    def GenFrameGroup(
        cls,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        payload: FrameArray,
    ) -> "FrameGroup":
        return cls(subtype, chip_coord, core_coord, replication_id, payload)

    def __getitem__(self, item) -> Frame:
        return super().GenFrame(
            self.subtype,
            self.chip_coord,
            self.core_coord,
            self.replication_id,
            self.payload[item],
        )

    def __len__(self) -> int:
        return self.length

    @property
    def length(self) -> int:
        return self._length

    @property
    def value(self) -> Tuple[int, ...]:
        val_list = []
        for load in self.payload:
            val_list.append(self._fill_payload(load))

        return tuple(val_list)


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
    """

    def __init__(
        self,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        info: int,
        contents: FrameArray,
    ) -> None:
        super().__init__(subtype, chip_coord, core_coord, replication_id, info)

        self._info = info
        self.content = contents
        self._length = len(contents) + 1

    @classmethod
    def GenFramePackage(
        cls,
        subtype: FST,
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        info: int,
        contents: FrameArray,
    ) -> "FramePackage":
        return cls(subtype, chip_coord, core_coord, replication_id, info, contents)

    def __len__(self) -> int:
        return self.length

    @property
    def length(self) -> int:
        return self._length

    @property
    def value(self) -> Tuple[int, ...]:
        val_list = []

        val_list.append(self._fill_payload(self.payload))
        val_list.extend(self.content)

        return tuple(val_list)


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
    def GenTestInFrame1(
        chip_coord: Coord, core_coord: Coord, replication_id: ReplicationId
    ) -> Frame:
        """Test input frame type I. Generic for offline & onlines."""
        return Frame.GenFrame(FST.TEST_TYPE1, chip_coord, core_coord, replication_id, 0)

    @staticmethod
    @abstractmethod
    def GenTestOutFrame1() -> FramePackage:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestInFrame2(
        chip_coord: Coord, core_coord: Coord, replication_id: ReplicationId
    ) -> Frame:
        """Test output frame type II. Generic for offline & onlines."""
        return Frame.GenFrame(FST.TEST_TYPE2, chip_coord, core_coord, replication_id, 0)

    @staticmethod
    @abstractmethod
    def GenTestOutFrame2() -> FramePackage:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestInFrame3() -> Frame:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestOutFrame3() -> FrameArray:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestInFrame4() -> Frame:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenTestOutFrame4() -> FrameArray:
        raise NotImplementedError


class FrameGenOffline(FrameGen):
    @staticmethod
    @abstractmethod
    def GenConfigFrame1(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        random_seed: FrameArray,
    ) -> FrameGroup:
        return FrameGroup.GenFrameGroup(
            FST.CONFIG_TYPE1, chip_coord, core_coord, replication_id, random_seed
        )

    @staticmethod
    @abstractmethod
    def GenConfigFrame2(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        *,
        param_reg: FrameArray,
    ) -> FrameGroup:
        return FrameGroup.GenFrameGroup(
            FST.CONFIG_TYPE2, chip_coord, core_coord, replication_id, param_reg
        )

    @staticmethod
    @abstractmethod
    def GenConfigFrame3(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int,
        n_neurons: int,
        is_random: bool = True,
    ) -> FramePackage:
        info, contents = ParamGenOffline.GenParamConfig3(
            sram_start_addr, n_neurons, is_random
        )

        return FramePackage.GenFramePackage(
            FST.CONFIG_TYPE3, chip_coord, core_coord, replication_id, info, contents
        )

    @staticmethod
    @abstractmethod
    def GenConfigFrame4(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr,
        n_weight_ram: int = 18,
        is_random: bool = True,
    ) -> FramePackage:
        info, contents = ParamGenOffline.GenParamConfig4(
            sram_start_addr, n_weight_ram, is_random
        )

        return FramePackage.GenFramePackage(
            FST.CONFIG_TYPE4, chip_coord, core_coord, replication_id, info, contents
        )

    @staticmethod
    @abstractmethod
    def GenTestOutFrame1(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        random_seed: FrameArray,
    ) -> FramePackage:
        return FrameGroup.GenFrameGroup(
            FST.TEST_TYPE1, test_chip_coord, core_coord, replication_id, random_seed
        )

    @staticmethod
    @abstractmethod
    def GenTestOutFrame2(
        test_chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        param_reg: FrameArray,
    ) -> FramePackage:
        return FrameGroup.GenFrameGroup(
            FST.TEST_TYPE2, test_chip_coord, core_coord, replication_id, param_reg
        )

    @staticmethod
    @abstractmethod
    def GenTestInFrame3(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int,
        n_neuron_ram: int,
    ) -> Frame:
        if sram_start_addr + n_neuron_ram > 512:
            raise ValueError(
                f"SRAM start address + number of neurons exceeds the limit 512! {sram_start_addr + n_neuron_ram}"
            )

        info = ParamGenOffline.GenRAMInfo(
            sram_start_addr, PackageType.TEST_IN, 4 * n_neuron_ram
        )

        return Frame.GenFrame(
            FST.TEST_TYPE3, chip_coord, core_coord, replication_id, info
        )

    @staticmethod
    @abstractmethod
    def GenTestOutFrame3(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int,
        n_neuron_ram: int,
        contents: FrameArray,
    ) -> FramePackage:
        if sram_start_addr + n_neuron_ram > 512:
            raise ValueError(
                f"SRAM start address + number of neurons exceeds the limit 512! {sram_start_addr + n_neuron_ram}"
            )

        info = ParamGenOffline.GenRAMInfo(
            sram_start_addr, PackageType.TEST_OUT, 4 * n_neuron_ram
        )

        return FramePackage.GenFramePackage(
            FST.TEST_TYPE3, chip_coord, core_coord, replication_id, info, contents
        )

    @staticmethod
    @abstractmethod
    def GenTestInFrame4(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int,
        n_weight_ram: int,
    ) -> Frame:
        if sram_start_addr + n_weight_ram > 512:
            raise ValueError(
                f"SRAM start address + number of weight rams exceeds the limit 512! {sram_start_addr + n_weight_ram}"
            )

        info = ParamGenOffline.GenRAMInfo(
            sram_start_addr, PackageType.TEST_IN, 18 * n_weight_ram
        )

        return Frame.GenFrame(
            FST.TEST_TYPE4, chip_coord, core_coord, replication_id, info
        )

    @staticmethod
    @abstractmethod
    def GenTestOutFrame4(
        chip_coord: Coord,
        core_coord: Coord,
        replication_id: ReplicationId,
        sram_start_addr: int,
        n_weight_ram: int,
        contents: FrameArray,
    ) -> FramePackage:
        if sram_start_addr + n_weight_ram > 512:
            raise ValueError(
                f"SRAM start address + number of weight rams exceeds the limit 512! {sram_start_addr + n_weight_ram}"
            )

        info = ParamGenOffline.GenRAMInfo(
            sram_start_addr, PackageType.TEST_OUT, 18 * n_weight_ram
        )

        return FramePackage.GenFramePackage(
            FST.TEST_TYPE4, chip_coord, core_coord, replication_id, info, contents
        )
