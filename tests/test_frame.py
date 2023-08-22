import pytest

from paitest.coord import Coord, ReplicationId
from paitest.frames import FrameGenOffline, FrameGenOnline
from paitest.frames.params import ParamGenOffline, ParamGenOnline, gen_package_info
from paitest._types import FrameSubType as FST, PackageType


@pytest.mark.parametrize(
    "random_seed",
    [
        0b1111_1001_1010_1011_1100_1101_1110_011111_0000_0001_0010_0011_0100_0101_101011,
        0b0110_1011_0111_1001_0001_1001_1101_111011_0011_1111_1010_0101_1101_0010_000111,
    ],
)
def test_Offline_GenConfigFrame1(random_seed):
    params = ParamGenOffline.gen_random_seed(False, random_seed)

    config1 = FrameGenOffline.gen_config_frame1(
        Coord(0, 0), Coord(1, 1), ReplicationId(2, 2), params
    )

    assert config1.length == 3
    assert config1.sub_type == FST.CONFIG_TYPE1
    assert config1.chip_coord == Coord(0, 0)
    assert config1.core_coord == Coord(1, 1)
    assert config1.rid == ReplicationId(2, 2)

    payloads = config1.payload
    seed = (payloads[0] << 34) + (payloads[1] << 4) + payloads[2]

    assert random_seed == seed


@pytest.mark.parametrize(
    "test_chip_coord", [Coord(1, 1), Coord(20, 10), Coord(0, 1), Coord(1, 0)]
)
def test_Offline_GenConfigFrame2(test_chip_coord: Coord):
    params = ParamGenOffline.gen_param_reg(test_chip_coord, True)

    config2 = FrameGenOffline.gen_config_frame2(
        Coord(0, 0), Coord(1, 1), ReplicationId(3, 4), params
    )

    assert config2.length == 3
    assert config2.sub_type == FST.CONFIG_TYPE2
    assert config2.chip_coord == Coord(0, 0)
    assert config2.core_coord == Coord(1, 1)
    assert config2.rid == ReplicationId(3, 4)

    payloads = config2.value
    now = ((payloads[1] & ((1 << 3) - 1)) << 7) + (payloads[2] >> 23)

    assert now == test_chip_coord.address


@pytest.mark.parametrize(
    "sram_start_addr, n_neuron_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenConfigFrame3(sram_start_addr, n_neuron_ram):
    info = gen_package_info(sram_start_addr, 4 * n_neuron_ram, PackageType.CONFIG)
    contents = ParamGenOffline.gen_neuron_ram(sram_start_addr, n_neuron_ram, True)

    config3 = FrameGenOffline.gen_config_frame3(
        Coord(1, 1), Coord(2, 2), ReplicationId(10, 10), info, contents
    )

    assert config3.length == config3.n_package + 1
    assert config3.sub_type == FST.CONFIG_TYPE3
    assert config3.chip_coord == Coord(1, 1)
    assert config3.core_coord == Coord(2, 2)
    assert config3.rid == ReplicationId(10, 10)
    assert config3.start_addr == sram_start_addr
    assert config3.package_type == PackageType.CONFIG
    assert config3.n_package == 4 * n_neuron_ram


@pytest.mark.parametrize(
    "sram_start_addr, n_weight_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenConfigFrame4(sram_start_addr, n_weight_ram):
    info = gen_package_info(sram_start_addr, 18 * n_weight_ram, PackageType.CONFIG)
    contents = ParamGenOffline.gen_weight_ram(sram_start_addr, n_weight_ram, True)

    config4 = FrameGenOffline.gen_config_frame4(
        Coord(1, 1), Coord(2, 2), ReplicationId(10, 10), info, contents
    )

    assert config4.length == config4.n_package + 1
    assert config4.sub_type == FST.CONFIG_TYPE4
    assert config4.chip_coord == Coord(1, 1)
    assert config4.core_coord == Coord(2, 2)
    assert config4.rid == ReplicationId(10, 10)
    assert config4.start_addr == sram_start_addr
    assert config4.package_type == PackageType.CONFIG
    assert config4.n_package == 18 * n_weight_ram

    with pytest.raises(ValueError):
        contents = ParamGenOffline.gen_weight_ram(0, 513, True)
        config4 = FrameGenOffline.gen_config_frame4(
            Coord(1, 1), Coord(2, 2), ReplicationId(10, 10), info, contents
        )


def test_Offline_GenTestInFrame1():
    testin1 = FrameGenOffline.gen_testin_frame1(
        Coord(0, 0), Coord(2, 1), ReplicationId(3, 3)
    )

    assert testin1.length == 1
    assert testin1.sub_type == FST.TEST_IN_TYPE1
    assert testin1.chip_coord == Coord(0, 0)
    assert testin1.core_coord == Coord(2, 1)
    assert testin1.rid == ReplicationId(3, 3)
    assert testin1.payload == 0


def test_Offline_GenTestInFrame2():
    testin2 = FrameGenOffline.gen_testin_frame2(
        Coord(0, 0), Coord(2, 1), ReplicationId(3, 3)
    )

    assert testin2.length == 1
    assert testin2.sub_type == FST.TEST_IN_TYPE2
    assert testin2.chip_coord == Coord(0, 0)
    assert testin2.core_coord == Coord(2, 1)
    assert testin2.rid == ReplicationId(3, 3)
    assert testin2.payload == 0


@pytest.mark.parametrize(
    "sram_start_addr, n_neuron_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenTestInFrame3(sram_start_addr, n_neuron_ram):
    info = gen_package_info(sram_start_addr, 4 * n_neuron_ram, PackageType.TEST_IN)

    testin3 = FrameGenOffline.gen_testin_frame3(
        Coord(0, 0), Coord(2, 1), ReplicationId(3, 3), info
    )

    assert testin3.length == 1
    assert testin3.sub_type == FST.TEST_IN_TYPE3
    assert testin3.chip_coord == Coord(0, 0)
    assert testin3.core_coord == Coord(2, 1)
    assert testin3.rid == ReplicationId(3, 3)
    assert testin3.package_type == PackageType.TEST_IN
    assert testin3.start_addr == sram_start_addr
    assert testin3.n_package == 4 * n_neuron_ram


@pytest.mark.parametrize(
    "sram_start_addr, n_weight_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenTestInFrame4(sram_start_addr, n_weight_ram):
    info = gen_package_info(sram_start_addr, 18 * n_weight_ram, PackageType.TEST_IN)

    testin4 = FrameGenOffline.gen_testin_frame4(
        Coord(0, 0), Coord(2, 1), ReplicationId(3, 3), info
    )

    assert testin4.length == 1
    assert testin4.sub_type == FST.TEST_IN_TYPE4
    assert testin4.chip_coord == Coord(0, 0)
    assert testin4.core_coord == Coord(2, 1)
    assert testin4.rid == ReplicationId(3, 3)
    assert testin4.package_type == PackageType.TEST_IN
    assert testin4.start_addr == sram_start_addr
    assert testin4.n_package == 18 * n_weight_ram


def test_Offline_GenTestOutFrame1():
    params = ParamGenOffline.gen_random_seed(True)

    testout1 = FrameGenOffline.gen_testout_frame1(
        Coord(1, 0), Coord(2, 1), ReplicationId(6, 7), params
    )

    assert testout1.length == 3
    assert testout1.sub_type == FST.TEST_OUT_TYPE1
    assert testout1.chip_coord == Coord(1, 0)
    assert testout1.core_coord == Coord(2, 1)
    assert testout1.rid == ReplicationId(6, 7)
    assert testout1.payload == params

    assert getattr(testout1, "test_chip_coord") == Coord(1, 0)


def test_Offline_GenTestOutFrame2():
    params = ParamGenOffline.gen_param_reg(Coord(2, 0), True)

    testout2 = FrameGenOffline.gen_testout_frame2(
        Coord(2, 0), Coord(2, 1), ReplicationId(6, 7), params
    )

    assert testout2.length == 3
    assert testout2.sub_type == FST.TEST_OUT_TYPE2
    assert testout2.chip_coord == Coord(2, 0)
    assert testout2.core_coord == Coord(2, 1)
    assert testout2.rid == ReplicationId(6, 7)
    assert testout2.payload == params

    assert getattr(testout2, "test_chip_coord") == Coord(2, 0)


@pytest.mark.parametrize(
    "sram_start_addr, n_neuron_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenTestOutFrame3(sram_start_addr, n_neuron_ram):
    info = gen_package_info(sram_start_addr, 4 * n_neuron_ram, PackageType.TEST_OUT)
    contents = ParamGenOffline.gen_neuron_ram(sram_start_addr, n_neuron_ram, True)

    testout3 = FrameGenOffline.gen_testout_frame3(
        Coord(1, 0),
        Coord(2, 1),
        ReplicationId(6, 7),
        info,
        contents,
    )

    assert testout3.sub_type == FST.TEST_OUT_TYPE3
    assert testout3.chip_coord == Coord(1, 0)
    assert testout3.core_coord == Coord(2, 1)
    assert testout3.rid == ReplicationId(6, 7)
    assert testout3.package_type == PackageType.TEST_OUT
    assert testout3.start_addr == sram_start_addr
    assert testout3.n_package == 4 * n_neuron_ram
    assert testout3.length == testout3.n_package + 1
    assert getattr(testout3, "test_chip_coord") == Coord(1, 0)


@pytest.mark.parametrize(
    "sram_start_addr, n_weight_ram", [(0, 512), (100, 200), (511, 1)]
)
def test_Offline_GenTestOutFrame4(sram_start_addr, n_weight_ram):
    info = gen_package_info(sram_start_addr, 18 * n_weight_ram, PackageType.TEST_OUT)
    contents = ParamGenOffline.gen_weight_ram(sram_start_addr, n_weight_ram, True)

    testout4 = FrameGenOffline.gen_testout_frame4(
        Coord(1, 0),
        Coord(2, 1),
        ReplicationId(6, 7),
        info,
        contents,
    )

    assert testout4.sub_type == FST.TEST_OUT_TYPE4
    assert testout4.chip_coord == Coord(1, 0)
    assert testout4.core_coord == Coord(2, 1)
    assert testout4.rid == ReplicationId(6, 7)
    assert testout4.package_type == PackageType.TEST_OUT
    assert testout4.start_addr == sram_start_addr
    assert testout4.n_package == 18 * n_weight_ram
    assert testout4.length == testout4.n_package + 1

    assert getattr(testout4, "test_chip_coord") == Coord(1, 0)


def test_Online_GenConfigFrame1():
    params = ParamGenOnline.gen_lut(True)

    config1 = FrameGenOnline.gen_config_frame1(
        Coord(1, 1), Coord(1, 2), ReplicationId(3, 3), params
    )

    assert config1.length == 16
    assert config1.sub_type == FST.CONFIG_TYPE1
    assert config1.payload == params
    assert config1.chip_coord == Coord(1, 1)
    assert config1.core_coord == Coord(1, 2)
    assert config1.rid == ReplicationId(3, 3)


@pytest.mark.parametrize("test_chip_addr", [Coord(1, 1), Coord(2, 4), Coord(27, 27)])
def test_Online_GenConfigFrame2(test_chip_addr: Coord):
    params = ParamGenOnline.gen_core_param(test_chip_addr, True)

    config2 = FrameGenOnline.gen_config_frame2(
        Coord(1, 1), Coord(1, 2), ReplicationId(3, 3), params
    )

    assert config2.length == 8
    assert config2.sub_type == FST.CONFIG_TYPE2
    assert config2.payload == params
    assert config2.chip_coord == Coord(1, 1)
    assert config2.core_coord == Coord(1, 2)
    assert config2.rid == ReplicationId(3, 3)

    assert config2.payload[7] == 0
    assert (config2.payload[6] >> 28) & 1 == 0
    assert (config2.payload[6] >> 16) & ((1 << 10) - 1) == test_chip_addr.address


@pytest.mark.parametrize(
    "neuron_start_addr, n_neuron_ram", [(0, 1024), (600, 400), (512, 512)]
)
def test_Online_GenConfigFrame3(neuron_start_addr, n_neuron_ram):
    info = gen_package_info(neuron_start_addr, 2 * n_neuron_ram, PackageType.CONFIG)
    contents = ParamGenOnline.gen_neuron_ram(neuron_start_addr, n_neuron_ram, True)

    config3 = FrameGenOnline.gen_config_frame3(
        Coord(1, 1), Coord(1, 2), ReplicationId(3, 3), info, contents
    )

    assert config3.length == config3.n_package + 1
    assert config3.sub_type == FST.CONFIG_TYPE3
    assert config3.chip_coord == Coord(1, 1)
    assert config3.core_coord == Coord(1, 2)
    assert config3.rid == ReplicationId(3, 3)
    assert config3.start_addr == neuron_start_addr
    assert config3.package_type == PackageType.CONFIG
    assert config3.n_package == 2 * n_neuron_ram


@pytest.mark.parametrize(
    "neuron_start_addr, n_neuron_ram", [(0, 1024), (600, 400), (512, 512)]
)
def test_Online_GenConfigFrame4(neuron_start_addr, n_neuron_ram):
    info = gen_package_info(neuron_start_addr, 16 * n_neuron_ram, PackageType.CONFIG)
    contents = ParamGenOnline.gen_weight_ram(neuron_start_addr, n_neuron_ram, True)

    config4 = FrameGenOnline.gen_config_frame4(
        Coord(1, 1), Coord(1, 2), ReplicationId(3, 3), info, contents
    )

    assert config4.length == config4.n_package + 1
    assert config4.sub_type == FST.CONFIG_TYPE4
    assert config4.chip_coord == Coord(1, 1)
    assert config4.core_coord == Coord(1, 2)
    assert config4.rid == ReplicationId(3, 3)
    assert config4.start_addr == neuron_start_addr
    assert config4.package_type == PackageType.CONFIG
    assert config4.n_package == 16 * n_neuron_ram


def test_Online_GenTestInFrame1():
    testin1 = FrameGenOnline.gen_testin_frame1(
        Coord(1, 1), Coord(1, 2), ReplicationId(3, 3)
    )

    assert testin1.length == 1
    assert testin1.sub_type == FST.TEST_IN_TYPE1
    assert testin1.chip_coord == Coord(1, 1)
    assert testin1.core_coord == Coord(1, 2)
    assert testin1.rid == ReplicationId(3, 3)
    assert testin1.payload == 0


def test_Online_GenTestInFrame2():
    testin2 = FrameGenOnline.gen_testin_frame2(
        Coord(1, 1), Coord(1, 2), ReplicationId(3, 3)
    )

    assert testin2.length == 1
    assert testin2.sub_type == FST.TEST_IN_TYPE2
    assert testin2.chip_coord == Coord(1, 1)
    assert testin2.core_coord == Coord(1, 2)
    assert testin2.rid == ReplicationId(3, 3)
    assert testin2.payload == 0


@pytest.mark.parametrize(
    "neuron_start_addr, n_neuron_ram", [(0, 1024), (100, 900), (512, 512)]
)
def test_Online_GenTestInFrame3(neuron_start_addr, n_neuron_ram):
    info = gen_package_info(neuron_start_addr, 2 * n_neuron_ram, PackageType.TEST_IN)

    testin3 = FrameGenOnline.gen_testin_frame3(
        Coord(1, 1), Coord(1, 2), ReplicationId(3, 3), info
    )

    assert testin3.length == 1
    assert testin3.sub_type == FST.TEST_IN_TYPE3
    assert testin3.chip_coord == Coord(1, 1)
    assert testin3.core_coord == Coord(1, 2)
    assert testin3.rid == ReplicationId(3, 3)
    assert testin3.package_type == PackageType.TEST_IN
    assert testin3.start_addr == neuron_start_addr
    assert testin3.n_package == 2 * n_neuron_ram


@pytest.mark.parametrize(
    "neuron_start_addr, n_neuron_ram", [(0, 1024), (100, 900), (512, 512)]
)
def test_Online_GenTestInFrame4(neuron_start_addr, n_neuron_ram):
    info = gen_package_info(neuron_start_addr, 16 * n_neuron_ram, PackageType.TEST_IN)

    testin4 = FrameGenOnline.gen_testin_frame4(
        Coord(1, 1), Coord(1, 2), ReplicationId(3, 3), info
    )

    assert testin4.length == 1
    assert testin4.sub_type == FST.TEST_IN_TYPE4
    assert testin4.chip_coord == Coord(1, 1)
    assert testin4.core_coord == Coord(1, 2)
    assert testin4.rid == ReplicationId(3, 3)
    assert testin4.package_type == PackageType.TEST_IN
    assert testin4.start_addr == neuron_start_addr
    assert testin4.n_package == 16 * n_neuron_ram


def test_Online_GenTestOutFrame1():
    params = ParamGenOnline.gen_lut(True)

    testout1 = FrameGenOnline.gen_testout_frame1(
        Coord(1, 0), Coord(2, 1), ReplicationId(6, 7), params
    )

    assert testout1.length == 16
    assert testout1.sub_type == FST.TEST_OUT_TYPE1
    assert testout1.chip_coord == Coord(1, 0)
    assert testout1.core_coord == Coord(2, 1)
    assert testout1.rid == ReplicationId(6, 7)
    assert testout1.payload == params

    assert getattr(testout1, "test_chip_coord") == Coord(1, 0)


def test_Online_GenTestOutFrame2():
    params = ParamGenOnline.gen_core_param(Coord(2, 0), True)

    testout2 = FrameGenOnline.gen_testout_frame2(
        Coord(2, 0), Coord(2, 1), ReplicationId(6, 7), params
    )

    assert testout2.length == 8
    assert testout2.sub_type == FST.TEST_OUT_TYPE2
    assert testout2.chip_coord == Coord(2, 0)
    assert testout2.core_coord == Coord(2, 1)
    assert testout2.rid == ReplicationId(6, 7)
    assert testout2.payload == params

    assert getattr(testout2, "test_chip_coord") == Coord(2, 0)


@pytest.mark.parametrize(
    "neuron_start_addr, n_neuron_ram", [(0, 1024), (100, 900), (512, 512)]
)
def test_Online_GenTestOutFrame3(neuron_start_addr, n_neuron_ram):
    info = gen_package_info(neuron_start_addr, 2 * n_neuron_ram, PackageType.TEST_OUT)
    contents = ParamGenOnline.gen_neuron_ram(neuron_start_addr, n_neuron_ram, True)

    testout3 = FrameGenOnline.gen_testout_frame3(
        Coord(1, 0),
        Coord(2, 1),
        ReplicationId(6, 7),
        info,
        contents,
    )

    assert testout3.sub_type == FST.TEST_OUT_TYPE3
    assert testout3.chip_coord == Coord(1, 0)
    assert testout3.core_coord == Coord(2, 1)
    assert testout3.rid == ReplicationId(6, 7)
    assert testout3.package_type == PackageType.TEST_OUT
    assert testout3.start_addr == neuron_start_addr
    assert testout3.n_package == 2 * n_neuron_ram
    assert testout3.length == testout3.n_package + 1

    assert getattr(testout3, "test_chip_coord") == Coord(1, 0)


@pytest.mark.parametrize(
    "neuron_start_addr, n_neuron_ram", [(0, 1024), (100, 900), (512, 512)]
)
def test_Online_GenTestOutFrame4(neuron_start_addr, n_neuron_ram):
    info = gen_package_info(neuron_start_addr, 16 * n_neuron_ram, PackageType.TEST_OUT)
    contents = ParamGenOnline.gen_weight_ram(neuron_start_addr, n_neuron_ram, True)

    testout4 = FrameGenOnline.gen_testout_frame4(
        Coord(15, 0),
        Coord(2, 1),
        ReplicationId(6, 7),
        info,
        contents,
    )

    assert testout4.sub_type == FST.TEST_OUT_TYPE4
    assert testout4.chip_coord == Coord(15, 0)
    assert testout4.core_coord == Coord(2, 1)
    assert testout4.rid == ReplicationId(6, 7)
    assert testout4.package_type == PackageType.TEST_OUT
    assert testout4.start_addr == neuron_start_addr
    assert testout4.n_package == 16 * n_neuron_ram
    assert testout4.length == testout4.n_package + 1

    assert getattr(testout4, "test_chip_coord") == Coord(15, 0)
