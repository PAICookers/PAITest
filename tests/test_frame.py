import random
import pytest

from paitest.coord import Coord
from paitest.frames import FrameGenOffline, FrameGenOnline
from paitest.frames import ParamGenOffline
from paitest.frames.mask import FrameMask as FM
from paitest._types import FrameSubType as FST


@pytest.mark.parametrize("random_seed", [random.randint(0, FM.GENERAL_MASK)])
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
