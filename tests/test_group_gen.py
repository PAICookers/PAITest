import pytest
from typing import Callable, List, Tuple, Union
from paitest._types import CoordLike
from paitest.coord import Coord, ReplicationId
from paitest.frames import Frame, FrameGroup, FramePackage, FT
from paitest.group_gen import GroupGenOffline, GroupGenOnline
from paitest.utils import to_coords

global test_chip_coord
test_chip_coord = Coord(0, 1)


def _traverse_gen_group(
    core_coords: Union[CoordLike, List[CoordLike]],
    rid: ReplicationId,
    gen_group: Callable[..., Tuple[FT, FT, FT]],
    **kwargs,
) -> Tuple[List[FT], List[FT], List[FT]]:
    _chip_coord = [Coord(0, 0)]
    coords = to_coords(core_coords)
    c_list = []
    to_list = []
    ti_list = []

    for chip in _chip_coord:
        for coord in coords:
            c, to, ti = gen_group(test_chip_coord, chip, coord, rid, **kwargs)

            c_list.append(c)
            to_list.append(to)
            ti_list.append(ti)

    return c_list, to_list, ti_list


def test_offline_gen_group1():
    core_coords = [Coord(0, 0), Coord(1, 0), Coord(2, 0)]
    c, to, ti = _traverse_gen_group(
        core_coords,
        ReplicationId(0, 0),
        GroupGenOffline.gen_group1,
        is_random=True,
    )

    for c_item, to_item in zip(c, to):
        assert c_item.payload == to_item.payload
        assert getattr(to_item, "test_chip_coord") == test_chip_coord

    assert type(c[0]) == FrameGroup
    assert type(to[0]) == FrameGroup
    assert type(ti[0]) == Frame


def test_offline_gen_group2():
    core_coords = [Coord(0, 0), Coord(1, 0), Coord(2, 0)]
    c, to, ti = _traverse_gen_group(
        core_coords,
        ReplicationId(0, 0),
        GroupGenOffline.gen_group2,
        is_random=True,
    )

    for c_item, to_item in zip(c, to):
        assert c_item.payload == to_item.payload
        assert getattr(to_item, "test_chip_coord") == test_chip_coord

    assert type(c[0]) == FrameGroup
    assert type(to[0]) == FrameGroup
    assert type(ti[0]) == Frame


def test_offline_gen_group3():
    core_coords = [Coord(0, 0), Coord(1, 0), Coord(2, 0)]
    c, to, ti = _traverse_gen_group(
        core_coords,
        ReplicationId(0, 0),
        GroupGenOffline.gen_group3,
        sram_start_addr=100,
        n_neuron_ram=100,
    )

    for c_item, to_item in zip(c, to):
        assert c_item.content == to_item.content
        assert getattr(to_item, "test_chip_coord") == test_chip_coord

    assert type(c[0]) == FramePackage
    assert type(to[0]) == FramePackage
    assert type(ti[0]) == FramePackage

    with pytest.raises(ValueError):
        c, to, ti = _traverse_gen_group(
            core_coords,
            ReplicationId(0, 0),
            GroupGenOffline.gen_group3,
            sram_start_addr=0,
            n_neuron_ram=513,
        )


def test_offline_gen_group4():
    core_coords = [Coord(0, 0), Coord(1, 0), Coord(2, 0)]
    c, to, ti = _traverse_gen_group(
        core_coords,
        ReplicationId(0, 0),
        GroupGenOffline.gen_group4,
        sram_start_addr=0,
        n_weight_ram=512,
    )

    for c_item, to_item in zip(c, to):
        assert c_item.content == to_item.content
        assert getattr(to_item, "test_chip_coord") == test_chip_coord

    assert type(c[0]) == FramePackage
    assert type(to[0]) == FramePackage
    assert type(ti[0]) == FramePackage

    with pytest.raises(ValueError):
        c, to, ti = _traverse_gen_group(
            core_coords,
            ReplicationId(0, 0),
            GroupGenOffline.gen_group4,
            sram_start_addr=0,
            n_weight_ram=513,
        )


def test_online_gen_group1():
    core_coords = [Coord(0, 0), Coord(1, 0), Coord(2, 0)]
    c, to, ti = _traverse_gen_group(
        core_coords,
        ReplicationId(0, 0),
        GroupGenOnline.gen_group1,
        is_random=True,
    )

    for c_item, to_item in zip(c, to):
        assert c_item.payload == to_item.payload
        assert getattr(to_item, "test_chip_coord") == test_chip_coord

    assert type(c[0]) == FrameGroup
    assert type(to[0]) == FrameGroup
    assert type(ti[0]) == Frame


def test_online_gen_group2():
    core_coords = [Coord(0, 0), Coord(1, 0), Coord(2, 0)]
    c, to, ti = _traverse_gen_group(
        core_coords,
        ReplicationId(0, 0),
        GroupGenOnline.gen_group2,
        is_random=True,
    )

    for c_item, to_item in zip(c, to):
        assert c_item.payload == to_item.payload
        assert getattr(to_item, "test_chip_coord") == test_chip_coord

    assert type(c[0]) == FrameGroup
    assert type(to[0]) == FrameGroup
    assert type(ti[0]) == Frame


def test_online_gen_group3():
    core_coords = [Coord(0, 0), Coord(1, 0), Coord(2, 0)]
    c, to, ti = _traverse_gen_group(
        core_coords,
        ReplicationId(0, 0),
        GroupGenOnline.gen_group3,
        neuron_start_addr=0,
        n_neuron_ram=1024,
    )

    for c_item, to_item in zip(c, to):
        assert c_item.content == to_item.content
        assert getattr(to_item, "test_chip_coord") == test_chip_coord

    assert type(c[0]) == FramePackage
    assert type(to[0]) == FramePackage
    assert type(ti[0]) == FramePackage

    with pytest.raises(ValueError):
        c, to, ti = _traverse_gen_group(
            core_coords,
            ReplicationId(0, 0),
            GroupGenOnline.gen_group3,
            neuron_start_addr=0,
            n_neuron_ram=1025,
        )


def test_online_gen_group4():
    core_coords = [Coord(0, 0), Coord(1, 0), Coord(2, 0)]
    c, to, ti = _traverse_gen_group(
        core_coords,
        ReplicationId(0, 0),
        GroupGenOnline.gen_group4,
        neuron_start_addr=0,
        n_neuron_ram=1024,
    )

    for c_item, to_item in zip(c, to):
        assert c_item.content == to_item.content
        assert getattr(to_item, "test_chip_coord") == test_chip_coord

    assert type(c[0]) == FramePackage
    assert type(to[0]) == FramePackage
    assert type(ti[0]) == FramePackage

    with pytest.raises(ValueError):
        c, to, ti = _traverse_gen_group(
            core_coords,
            ReplicationId(0, 0),
            GroupGenOnline.gen_group4,
            neuron_start_addr=0,
            n_neuron_ram=1025,
        )
