import pytest
from paitest.frames.params import ParamGenOffline, ParamGenOnline, gen_package_info
from paitest.coord import Coord
from paitest._types import PackageType
from paitest.frames.mask import OfflineConfigFrameMask as OFF_CFM


@pytest.mark.parametrize(
    "seed1, seed2, seed3",
    [
        (
            0b1111_1001_1010_1011_1100_1101_1110_01,
            0b1111_0000_0001_0010_0011_0100_0101_10,
            0b1011,
        ),
        (
            0b0110_1011_0111_1001_0001_1001_1101_11,
            0b1011_0011_1111_1010_0101_1101_0010_00,
            0b0111,
        ),
    ],
)
def test_Offline_GenParamConfig1(seed1, seed2, seed3):
    seed = (seed1 << 34) + (seed2 << 4) + seed3
    assert seed.bit_length() < 65

    params = ParamGenOffline.gen_random_seed(is_random=False, seed=seed)

    assert seed1 == params[0]
    assert seed2 == params[1]
    assert seed3 == params[2]
    assert params[2].bit_length() < 5

    for i in range(100):
        params = ParamGenOffline.gen_random_seed(True)
        assert params[2].bit_length() < 5


@pytest.mark.parametrize(
    "test_chip_coord",
    [Coord(4, 0), Coord(12, 12), Coord(24, 8), Coord(0, 0), Coord(0, 7)],
)
def test_Offiline_GenParamConfig2(test_chip_coord):
    params = ParamGenOffline.gen_param_reg(test_chip_coord, True)

    assert len(params) == 3

    low7 = test_chip_coord.address & ((1 << 7) - 1)
    high3 = test_chip_coord.address >> 7

    assert low7 == params[2] >> OFF_CFM.TEST_CHIP_ADDR_LOW7_OFFSET
    assert high3 == params[1] & ((1 << 3) - 1)


@pytest.mark.parametrize(
    "sram_start_addr, n_neuron_ram", [(0, 100), (0, 512), (100, 200), (200, 312)]
)
def test_Offiline_GenParamConfig3(sram_start_addr, n_neuron_ram):
    info = gen_package_info(sram_start_addr, 4 * n_neuron_ram, PackageType.CONFIG)
    contents = ParamGenOffline.gen_neuron_ram(sram_start_addr, n_neuron_ram, True)

    assert len(contents) == 4 * n_neuron_ram
    assert sram_start_addr == info >> 20
    assert 4 * n_neuron_ram == info & ((1 << 19) - 1)
    assert 0 == ((info >> 19) & 1)


@pytest.mark.parametrize(
    "sram_start_addr, n_weight_ram", [(0, 100), (0, 512), (100, 200), (200, 312)]
)
def test_Offiline_GenParamConfig4(sram_start_addr, n_weight_ram):
    info = gen_package_info(sram_start_addr, 18 * n_weight_ram, PackageType.CONFIG)
    contents = ParamGenOffline.gen_weight_ram(sram_start_addr, n_weight_ram, True)

    assert len(contents) == 18 * n_weight_ram
    assert sram_start_addr == info >> 20
    assert 18 * n_weight_ram == info & ((1 << 19) - 1)
    assert 0 == ((info >> 19) & 1)


def test_Online_GenParamConfig1():
    params = ParamGenOnline.gen_lut(is_random=True)
    assert len(params) == 16


@pytest.mark.parametrize(
    "test_chip_coord",
    [Coord(4, 0), Coord(12, 12), Coord(24, 8), Coord(0, 0), Coord(0, 7)],
)
def test_Online_GenParamConfig2(test_chip_coord: Coord):
    params = ParamGenOnline.gen_core_param(test_chip_coord, True)

    assert len(params) == 8
    assert params[7] == 0
    assert ((params[6] >> 28) & 1) == 0
    assert ((params[6] >> 16) & ((1 << 10) - 1)) == test_chip_coord.address


@pytest.mark.parametrize(
    "neuron_start_addr, n_neuron_ram", [(0, 1024), (100, 924), (100, 200)]
)
def test_Online_GenParamConfig3(neuron_start_addr, n_neuron_ram):
    info = gen_package_info(neuron_start_addr, 2 * n_neuron_ram, PackageType.CONFIG)
    contents = ParamGenOnline.gen_neuron_ram(neuron_start_addr, n_neuron_ram, True)

    assert 0 == ((info >> 19) & 1)
    assert neuron_start_addr == info >> 20
    assert 2 * n_neuron_ram == info & ((1 << 19) - 1)
    assert len(contents) == 2 * n_neuron_ram


@pytest.mark.parametrize(
    "neuron_start_addr, n_neuron_ram", [(0, 1024), (100, 924), (100, 200)]
)
def test_Online_GenParamConfig4(neuron_start_addr, n_neuron_ram):
    info = gen_package_info(neuron_start_addr, 16 * n_neuron_ram, PackageType.CONFIG)
    contents = ParamGenOnline.gen_weight_ram(neuron_start_addr, n_neuron_ram, True)

    assert 0 == ((info >> 19) & 1)
    assert neuron_start_addr == info >> 20
    assert 16 * n_neuron_ram == info & ((1 << 19) - 1)
    assert len(contents) == 16 * n_neuron_ram
