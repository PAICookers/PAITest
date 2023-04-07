from typing import List, Tuple, Optional
import random


def GenCoordinates(groups: int = ...) -> List[Tuple[int, int]]:

    def CoordGenerator():
        coordinates = set()

        while True:
            x = random.randint(0, 31)
            y = random.randint(0, 31)
            if (x, y) not in coordinates and (x < 0b11100 or y < 0b11100):
                coordinates.add((x, y))
                yield (x, y)

    generator = CoordGenerator()
    coordinates = [next(generator) for _ in range(groups)]

    return coordinates


def GenCoreAddr(
    groups: int = ...,
    fixed_core_addr: Optional[Tuple[int, int]] = ...
) -> List[Tuple[int, int]]:
    '''
        Generate random core address ONCE ONLY in range of OFFLINE CORE
    '''
    core_addr_list: List[Tuple[int, int]] = []

    if isinstance(fixed_core_addr, Tuple):
        assert fixed_core_addr[0] < 32 and fixed_core_addr[1] < 32
        assert not (fixed_core_addr[0] >=
                    0b11100 and fixed_core_addr[1] >= 0b11100)

        print(f"Core addr is fixed with: {fixed_core_addr}")
        for _ in range(groups):
            core_addr_list.append(fixed_core_addr)

    else:
        core_addr_list = GenCoordinates(groups)

    return core_addr_list
