import pytest

from paitest.coord import Coord
from paitest.frames import FrameGenOffline, FrameGenOnline
from paitest.frames import ParamGenOffline
from paitest._types import FrameSubType as FST, PackageType


@pytest.mark.parametrize(
    "random_seed",
    [
        0b1111_1001_1010_1011_1100_1101_1110_011111_0000_0001_0010_0011_0100_0101_101011,
        0b0110_1011_0111_1001_0001_1001_1101_111011_0011_1111_1010_0101_1101_0010_000111,
    ],
)
def test_Offline_GenConfigFrame1(random_seed):
    params = ParamGenOffline.GenParamConfig1(False, random_seed)
    config1 = FrameGenOffline.GenConfigFrame1(
        Coord(0, 0), Coord(1, 1), Coord(2, 2), params
    )

    assert config1.length == 3
    assert config1.sub_type == FST.CONFIG_TYPE1
    assert config1.chip_address == 0
    assert config1.core_address == 0b100001

    payloads = config1.payload
    seed = (payloads[0] << 34) + (payloads[1] << 4) + payloads[2]

    assert random_seed == seed


@pytest.mark.parametrize(
    "test_chip_coord", [Coord(1, 1), Coord(20, 10), Coord(0, 1), Coord(1, 0)]
)
def test_Offline_GenConfigFrame2(test_chip_coord: Coord):
    params = ParamGenOffline.GenParamConfig2(test_chip_coord, True)
    config1 = FrameGenOffline.GenConfigFrame2(
        Coord(0, 0), Coord(1, 1), Coord(3, 4), params
    )

    assert config1.length == 3
    assert config1.sub_type == FST.CONFIG_TYPE2
    assert config1.chip_address == 0
    assert config1.core_coord == Coord(1, 1)
    assert config1.replication_id == Coord(3, 4)

    payloads = config1.value
    now = ((payloads[1] & ((1 << 3) - 1)) << 7) + (payloads[2] >> 23)

    assert test_chip_coord.address == now


@pytest.mark.parametrize(
    "sram_start_addr, n_neuron_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenConfigFrame3(sram_start_addr, n_neuron_ram):
    config1 = FrameGenOffline.GenConfigFrame3(
        Coord(1, 1), Coord(2, 2), Coord(10, 10), sram_start_addr, n_neuron_ram
    )

    assert config1.length == config1.n_package + 1
    assert config1.sub_type == FST.CONFIG_TYPE3
    assert config1.chip_coord == Coord(1, 1)
    assert config1.core_coord == Coord(2, 2)
    assert config1.replication_id == Coord(10, 10)
    assert config1.start_addr == sram_start_addr
    assert config1.package_type == PackageType.CONFIG
    assert config1.n_package == 4 * n_neuron_ram

    with pytest.raises(ValueError):
        config1 = FrameGenOffline.GenConfigFrame3(
            Coord(1, 1), Coord(2, 2), Coord(10, 10), 0, 513
        )


@pytest.mark.parametrize(
    "sram_start_addr, n_weight_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenConfigFrame4(sram_start_addr, n_weight_ram):
    config1 = FrameGenOffline.GenConfigFrame4(
        Coord(1, 1), Coord(2, 2), Coord(10, 10), sram_start_addr, n_weight_ram
    )

    assert config1.length == config1.n_package + 1
    assert config1.sub_type == FST.CONFIG_TYPE4
    assert config1.chip_coord == Coord(1, 1)
    assert config1.core_coord == Coord(2, 2)
    assert config1.replication_id == Coord(10, 10)
    assert config1.start_addr == sram_start_addr
    assert config1.package_type == PackageType.CONFIG
    assert config1.n_package == 18 * n_weight_ram

    with pytest.raises(ValueError):
        config1 = FrameGenOffline.GenConfigFrame4(
            Coord(1, 1), Coord(2, 2), Coord(10, 10), 0, 513
        )


def test_Offline_GenTestInFrame1():
    testin1 = FrameGenOffline.GenTestInFrame1(Coord(0, 0), Coord(2, 1), Coord(3, 3))

    assert testin1.length == 1
    assert testin1.sub_type == FST.TEST_IN_TYPE1
    assert testin1.chip_coord == Coord(0, 0)
    assert testin1.core_coord == Coord(2, 1)
    assert testin1.replication_id == Coord(3, 3)
    assert testin1.payload == 0


def test_Offline_GenTestInFrame2():
    testin2 = FrameGenOffline.GenTestInFrame2(Coord(0, 0), Coord(2, 1), Coord(3, 3))

    assert testin2.length == 1
    assert testin2.sub_type == FST.TEST_IN_TYPE2
    assert testin2.chip_coord == Coord(0, 0)
    assert testin2.core_coord == Coord(2, 1)
    assert testin2.replication_id == Coord(3, 3)
    assert testin2.payload == 0


@pytest.mark.parametrize(
    "sram_start_addr, n_neuron_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenTestInFrame3(sram_start_addr, n_neuron_ram):
    testin3 = FrameGenOffline.GenTestInFrame3(
        Coord(0, 0), Coord(2, 1), Coord(3, 3), sram_start_addr, n_neuron_ram
    )

    assert testin3.length == 1
    assert testin3.sub_type == FST.TEST_IN_TYPE3
    assert testin3.chip_coord == Coord(0, 0)
    assert testin3.core_coord == Coord(2, 1)
    assert testin3.replication_id == Coord(3, 3)
    assert testin3.package_type == PackageType.TEST_IN
    assert testin3.start_addr == sram_start_addr
    assert testin3.n_package == 4 * n_neuron_ram

    with pytest.raises(ValueError):
        testin3 = FrameGenOffline.GenTestInFrame3(
            Coord(1, 1), Coord(2, 2), Coord(10, 10), 0, 513
        )


@pytest.mark.parametrize(
    "sram_start_addr, n_weight_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenTestInFrame4(sram_start_addr, n_weight_ram):
    testin4 = FrameGenOffline.GenTestInFrame4(
        Coord(0, 0), Coord(2, 1), Coord(3, 3), sram_start_addr, n_weight_ram
    )

    assert testin4.length == 1
    assert testin4.sub_type == FST.TEST_IN_TYPE4
    assert testin4.chip_coord == Coord(0, 0)
    assert testin4.core_coord == Coord(2, 1)
    assert testin4.replication_id == Coord(3, 3)
    assert testin4.package_type == PackageType.TEST_IN
    assert testin4.start_addr == sram_start_addr
    assert testin4.n_package == 18 * n_weight_ram

    with pytest.raises(ValueError):
        testin4 = FrameGenOffline.GenTestInFrame4(
            Coord(1, 1), Coord(2, 2), Coord(10, 10), 0, 513
        )


def test_Offline_GenTestOutFrame1():
    params = ParamGenOffline.GenParamConfig1(True)
    testout1 = FrameGenOffline.GenTestOutFrame1(
        Coord(1, 0), Coord(2, 1), Coord(6, 7), params
    )

    assert testout1.length == 3
    assert testout1.sub_type == FST.TEST_OUT_TYPE1
    assert testout1.chip_coord == Coord(1, 0)
    assert testout1.core_coord == Coord(2, 1)
    assert testout1.replication_id == Coord(6, 7)
    assert testout1.payload == params
    
    assert getattr(testout1, "test_chip_coord") == Coord(1, 0)


def test_Offline_GenTestOutFrame2():
    params = ParamGenOffline.GenParamConfig2(Coord(2, 0), True)
    testout2 = FrameGenOffline.GenTestOutFrame2(
        Coord(2, 0), Coord(2, 1), Coord(6, 7), params
    )

    assert testout2.length == 3
    assert testout2.sub_type == FST.TEST_OUT_TYPE2
    assert testout2.chip_coord == Coord(2, 0)
    assert testout2.core_coord == Coord(2, 1)
    assert testout2.replication_id == Coord(6, 7)
    assert testout2.payload == params
    
    assert getattr(testout2, "test_chip_coord") == Coord(2, 0)


@pytest.mark.parametrize(
    "sram_start_addr, n_neuron_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenTestOutFrame3(sram_start_addr, n_neuron_ram):
    info, contents = ParamGenOffline.GenParamConfig3(
        sram_start_addr, n_neuron_ram, True
    )
    testout3 = FrameGenOffline.GenTestOutFrame3(
        Coord(1, 0), Coord(2, 1), Coord(6, 7), sram_start_addr, n_neuron_ram, contents
    )

    assert testout3.sub_type == FST.TEST_OUT_TYPE3
    assert testout3.chip_coord == Coord(1, 0)
    assert testout3.core_coord == Coord(2, 1)
    assert testout3.replication_id == Coord(6, 7)
    assert testout3.package_type == PackageType.TEST_OUT
    assert testout3.start_addr == sram_start_addr
    assert testout3.n_package == 4 * n_neuron_ram
    assert testout3.length == testout3.n_package + 1
    
    assert getattr(testout3, "test_chip_coord") == Coord(1, 0)

    with pytest.raises(ValueError):
        testout3 = FrameGenOffline.GenTestOutFrame3(
            Coord(1, 1), Coord(2, 2), Coord(10, 10), 0, 513, contents
        )


@pytest.mark.parametrize(
    "sram_start_addr, n_weight_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenTestOutFrame4(sram_start_addr, n_weight_ram):
    info, contents = ParamGenOffline.GenParamConfig4(
        sram_start_addr, n_weight_ram, True
    )
    testout4 = FrameGenOffline.GenTestOutFrame4(
        Coord(1, 0), Coord(2, 1), Coord(6, 7), sram_start_addr, n_weight_ram, contents
    )

    assert testout4.sub_type == FST.TEST_OUT_TYPE4
    assert testout4.chip_coord == Coord(1, 0)
    assert testout4.core_coord == Coord(2, 1)
    assert testout4.replication_id == Coord(6, 7)
    assert testout4.package_type == PackageType.TEST_OUT
    assert testout4.start_addr == sram_start_addr
    assert testout4.n_package == 18 * n_weight_ram
    assert testout4.length == testout4.n_package + 1
    
    assert getattr(testout4, "test_chip_coord") == Coord(1, 0)

    with pytest.raises(ValueError):
        testout4 = FrameGenOffline.GenTestOutFrame4(
            Coord(1, 1), Coord(2, 2), Coord(10, 10), 0, 513, contents
        )
