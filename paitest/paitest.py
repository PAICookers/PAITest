from enum import Enum
from pathlib import Path
import random
from .frame import FrameGen
from .frame_params import *


'''
    1. Input configuration frame II
    2. Input test frame II
    3. Compare the test output frame II with expected
'''


class TestChipDirection(Enum):
    '''
        For [x, y]
        Left to right: +x
        Top to bottom: +y
    '''
    EAST = [1, 0]
    SOUTH = [0, 1]
    WEST = [-1, 0]
    NORTH = [0, -1]


def GenTestCases(
    frames_dir: Path,
    direction: TestChipDirection,
    groups: int = 1,
) -> None:
    if not frames_dir.exists():
        frames_dir.mkdir(parents=True, exist_ok=True)

    with open(frames_dir / "config.bin", "wb") as fc, \
            open(frames_dir / "testin.bin", "wb") as fi, \
            open(frames_dir / "testout.bin", "wb") as fo:

        for i in range(groups):
            chip_addr_x, chip_addr_y = random.randrange(
                0, 2**5), random.randrange(0, 2**5)
            chip_addr: int = (chip_addr_x << 5) | chip_addr_y

            core_addr_x, core_addr_y = random.randrange(
                0, 2**5), random.randrange(0, 2**5)
            core_addr: int = (core_addr_x << 5) | core_addr_y

            core_star_addr_x, core_star_addr_y = random.randrange(
                0, 2**5), random.randrange(0, 2**5)
            core_star_addr: int = (core_star_addr_x << 5) | core_star_addr_y

            config_frames_group: List[int] = []
            test_outframe_group: List[int] = []

            test_chip_addr_x, test_chip_addr_y = chip_addr_x + \
                direction.value[0], chip_addr_y + direction.value[1]
            test_chip_addr: int = (test_chip_addr_x << 5) | test_chip_addr_y

            weight_width_type = random.choice(list(WeightPrecisionTypes))
            lcn_type = random.choice(list(LCNTypes))
            input_width_type = random.choice(list(InputWidthTypes))
            spike_width_type = random.choice(list(SpikeWidthTypes))

            print(input_width_type)

            if input_width_type == InputWidthTypes.INPUT_WIDTH_8BIT:
                neuron_num = random.randrange(0, 4096)
            else:
                neuron_num = random.randrange(0, 512)

            pool_max_en = random.choice([0, 1])
            tick_wait_start = random.randrange(0, 2**15)
            tick_wait_end = random.randrange(0, 2**15)

            snn_en = random.choice([0, 1])
            target_lcn = random.randrange(0, 2**4)

            print(f"----- Configuration frame: {i+1}/{groups} Start -----")
            print("#1  Chip address:       [0x%02x | 0x%02x]" % (
                chip_addr_x, chip_addr_y))
            print("#2  Core address:       [0x%02x | 0x%02x]" % (
                core_addr_x, core_addr_y))
            print("#3  Core star address:  [0x%02x | 0x%02x]" % (
                core_star_addr_x, core_star_addr_y))
            print("#4  Weight width:       0x%x" % weight_width_type.value)
            print("#5  LCN:                0x%x" % lcn_type.value)
            print("#6  Input width:        0x%x" % input_width_type.value)
            print("#7  Spike width:        0x%x" % spike_width_type.value)
            print("#8  Neuron num:         %d" % neuron_num)
            print("#9  Pool max enable:    %s" %
                  ("True" if target_lcn else "False"))
            print("#10 Tick wait start:    0x%x" % tick_wait_start)
            print("#11 Tick wait end:      0x%x" % tick_wait_end)
            print("#12 SNN enable:         %s" %
                  ("True" if target_lcn else "False"))
            print("#13 Target LCN:         0x%x" % target_lcn)
            print(f"----- Configuration frame: {i+1}/{groups} End -----")

            config_frames_group, test_outframe_group = FrameGen.GenConfig2FrameGroup(
                chip_addr, core_addr, core_star_addr,
                weight_width_type=weight_width_type,
                lcn_type=lcn_type,
                input_width_type=input_width_type,
                spike_width_type=spike_width_type,
                neuron_num=neuron_num,
                pool_max_en=pool_max_en,
                tick_wait_start=tick_wait_start,
                tick_wait_end=tick_wait_end,
                snn_en=snn_en,
                target_lcn=target_lcn,
                test_chip_addr=test_chip_addr,
                test_ref_out_included=True
            )

            test_inframe = FrameGen.GenTest2InFrame(
                chip_addr, core_addr, core_star_addr)

            for j in range(3):
                fc.write(config_frames_group[j].to_bytes(
                    length=8, byteorder="big"))
                fo.write(test_outframe_group[j].to_bytes(
                    length=8, byteorder="big"))

            fi.write(test_inframe.to_bytes(length=8, byteorder="big"))


if __name__ == "__main__":
    test_time = 1000

    for _ in range(test_time):
        groups = random.randrange(1, 100)
        try:
            GenTestCases(Path("./test"), TestChipDirection.EAST, groups)
        except Exception as e:
            print(e)

    print("Test ok")
