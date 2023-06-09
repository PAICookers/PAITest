from typing import Tuple, overload

class Coord:
    x: int = ...
    y: int = ...
    @overload
    def __init__(self, _x: Tuple[int, int]) -> None: ...
    @overload
    def __init__(self, _x: int, _y: int) -> None: ...
    def __add__(self, other) -> Coord: ...
    def __sub__(self, other) -> CoordOffset: ...
    def __eq__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __str__(self) -> str: ...

    __repr__ = __str__

    ...

class CoordOffset(Coord):
    def __init__(self, _x: int, _y: int) -> None: ...
    def __add__(self, other) -> CoordOffset | Coord: ...
    def __sub__(self, other) -> CoordOffset: ...

    ...
