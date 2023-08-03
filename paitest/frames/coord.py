from typing import Optional, Tuple, Union, overload


class Coord:
    """Coordinates of the cores. Set coordinates (x, y) for every cores.

    Left to right, +X, up to down, +Y.
    """

    _COORD_MAX_LIMIT = (1 << 5) - 1
    _COORD_LOW_LIMIT = 0

    def __init__(
        self, _x: Union[Tuple[int, int], int], _y: Optional[int] = None
    ) -> None:
        if isinstance(_x, Tuple):
            x, y = _x[0], _x[1]
            if isinstance(_y, int):
                raise ValueError(f"Wrong Argument: {_y}")
        elif isinstance(_x, int):
            if isinstance(_y, int):
                x, y = _x, _y
            else:
                raise ValueError("Missing Argument: y")
        else:
            raise ValueError("Wrong Argument")

        if not (self._COORD_LOW_LIMIT <= x <= self._COORD_MAX_LIMIT and self._COORD_LOW_LIMIT <= y <= self._COORD_MAX_LIMIT):
            raise ValueError(f"{self._COORD_LOW_LIMIT} <= x <= {self._COORD_MAX_LIMIT}, {self._COORD_LOW_LIMIT} <= y <= {self._COORD_MAX_LIMIT}: ({x}, {y})")

        self.x: int = x
        self.y: int = y

    @classmethod
    def from_tuple(cls, pos) -> "Coord":
        return cls(*pos)

    @classmethod
    def default(cls) -> "Coord":
        return cls(0, 0)

    def __add__(self, __other: "CoordOffset") -> "Coord":
        """
        Examples:

        Coord = Coord + CoordOffset
        >>> c1 = Coord(1, 1)
        >>> c2 = c1 + CoordOffset(1, 1)
        c1: Coord(2, 2)

        NOTE: Coord + Coord is meaningless.
        """
        if not isinstance(__other, CoordOffset):
            raise TypeError(f"Unsupported type: {type(__other)}")

        return Coord(self.x + __other.delta_x, self.y + __other.delta_y)

    @overload
    def __sub__(self, __other: "Coord") -> "CoordOffset":
        ...

    @overload
    def __sub__(self, __other: "CoordOffset") -> "Coord":
        ...

    def __sub__(
        self, __other: Union["Coord", "CoordOffset"]
    ) -> Union["Coord", "CoordOffset"]:
        """
        Example:
        >>> c1 = Coord(1, 1)
        >>> c2 = Coord(2, 2) - c1
        c2: CoordOffset(1, 1)
        """
        if isinstance(__other, Coord):
            return CoordOffset(self.x - __other.x, self.y - __other.y)

        if isinstance(__other, CoordOffset):
            return Coord(self.x - __other.delta_x, self.y - __other.delta_y)

        raise TypeError(f"Unsupported type: {type(__other)}")

    """Operations below are used only when comparing with a Cooord."""

    def __eq__(self, __other: "Coord") -> bool:
        """
        Example:
        >>> Coord(4, 5) == Coord(4, 6)
        False
        """
        if not isinstance(__other, Coord):
            raise TypeError(f"Unsupported type: {type(__other)}")

        return self.x == __other.x and self.y == __other.y

    def __ne__(self, __other: "Coord") -> bool:
        """
        Examples:
        >>> Coord(4, 5) != Coord(4, 6)
        True

        >>> Coord(4, 5) != Coord(5, 5)
        True
        """
        if not isinstance(__other, Coord):
            raise TypeError(f"Unsupported type: {type(__other)}")

        return self.x != __other.x or self.y != __other.y

    def __lt__(self, __other: "Coord") -> bool:
        """Whether the coord is on the left OR below of __other.

        Examples:
        >>> Coord(4, 5) < Coord(4, 6)
        True

        >>> Coord(4, 5) < Coord(5, 5)
        True

        >>> Coord(4, 5) < Coord(5, 3)
        True
        """
        if not isinstance(__other, Coord):
            raise TypeError(f"Unsupported type: {type(__other)}")

        return self.x < __other.x or self.y < __other.y

    def __gt__(self, __other: "Coord") -> bool:
        """Whether the coord is on the right AND above of __other.

        Examples:
        >>> Coord(5, 5) > Coord(4, 5)
        True

        >>> Coord(4, 6) > Coord(4, 5)
        True

        >>> Coord(5, 4) > Coord(4, 5)
        False
        """
        if not isinstance(__other, Coord):
            raise TypeError(f"Unsupported type: {type(__other)}")

        # Except the `__eq__`
        return (
            (self.x > __other.x and self.y > __other.y)
            or (self.x == __other.x and self.y > __other.y)
            or (self.x > __other.x and self.y == __other.y)
        )

    def __le__(self, __other: "Coord") -> bool:
        return self.__lt__(__other) or self.__eq__(__other)

    def __ge__(self, __other: "Coord") -> bool:
        return self.__gt__(__other) or self.__eq__(__other)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Coord({self.x}, {self.y})"

    def to_tuple(self) -> Tuple[int, int]:
        """Convert to tuple"""
        return (self.x, self.y)

    def _to_address(self) -> int:
        """Convert to address, 10 bits"""
        return (self.x << 5) | self.y

    @property
    def address(self) -> int:
        return self._to_address()


class CoordOffset:
    """Offset of coordinates"""

    _COORDOFFSET_MAX_LIMIT = (1 << 5) - 1
    _COORDOFFSET_LOW_LIMIT = -(1 << 5)

    def __init__(self, _delta_x: int, _delta_y: int) -> None:
        if not (self._COORDOFFSET_LOW_LIMIT < _delta_x <= self._COORDOFFSET_MAX_LIMIT and self._COORDOFFSET_LOW_LIMIT < _delta_y <= self._COORDOFFSET_MAX_LIMIT):
            raise ValueError(f"{self._COORDOFFSET_LOW_LIMIT} < delta_x <= {self._COORDOFFSET_MAX_LIMIT}, {self._COORDOFFSET_LOW_LIMIT} < delta_y <= {self._COORDOFFSET_MAX_LIMIT}: ({_delta_x}, {_delta_y})")

        self.delta_x: int = _delta_x
        self.delta_y: int = _delta_y

    @overload
    def __add__(self, __other: Coord) -> Coord:
        ...

    @overload
    def __add__(self, __other: "CoordOffset") -> "CoordOffset":
        ...

    def __add__(
        self, __other: Union["CoordOffset", Coord]
    ) -> Union["CoordOffset", Coord]:
        """
        Examples:
        >>> delta_c1 = CoordOffset(1, 1)
        >>> delta_c2 = delta_c1 + CoordOffset(1, 1)
        delta_c2: CoordOffset(2, 2)

        Coord = CoordOffset + Coord
        >>> delta_c = CoordOffset(1, 1)
        >>> c1 = Coord(2, 3)
        >>> c2 = delta_c + c1
        c2: Coord(3, 4)
        """
        if isinstance(__other, CoordOffset):
            return CoordOffset(
                self.delta_x + __other.delta_x, self.delta_y + __other.delta_y
            )

        if isinstance(__other, Coord):
            return Coord(self.delta_x + __other.x, self.delta_y + __other.y)

        raise TypeError(f"Unsupported type: {type(__other)}")

    def __iadd__(self, __other: "CoordOffset") -> "CoordOffset":
        """
        Example:
        >>> delta_c = CoordOffset(1, 1)
        >>> delta_c += CoordOffset(1, 1)
        delta_c: CoordOffset(2, 2)
        """
        if not isinstance(__other, CoordOffset):
            raise TypeError(f"Unsupported type: {type(__other)}")

        self.delta_x += __other.delta_x
        self.delta_y += __other.delta_y

        return self

    def __sub__(self, __other: "CoordOffset") -> "CoordOffset":
        """
        Example:
        >>> delta_c1 = CoordOffset(1, 1)
        >>> delta_c2 = CoordOffset(2, 2)
        >>> delta_c = delta_c1 - delta_c2
        delta_c: CoordOffset(-1, -1)
        """
        if not isinstance(__other, CoordOffset):
            raise TypeError(f"Unsupported type: {type(__other)}")

        return CoordOffset(
            self.delta_x - __other.delta_x, self.delta_y - __other.delta_y
        )

    def __isub__(self, __other: "CoordOffset") -> "CoordOffset":
        """
        Example:
        >>> delta_c = CoordOffset(1, 1)
        >>> delta_c -= CoordOffset(1, 1)
        delta_c: CoordOffset(0, 0)
        """
        if not isinstance(__other, CoordOffset):
            raise TypeError(f"Unsupported type: {type(__other)}")

        self.delta_x -= __other.delta_x
        self.delta_y -= __other.delta_y

        return self

    def __eq__(self, __other: "CoordOffset") -> bool:
        """
        Example:
        >>> CoordOffset(4, 5) == CoordOffset(4, 6)
        False
        """
        if not isinstance(__other, CoordOffset):
            raise TypeError(f"Unsupported type: {type(__other)}")

        return self.delta_x == __other.delta_x and self.delta_y == __other.delta_y

    def __ne__(self, __other: "CoordOffset") -> bool:
        """
        Example:
        >>> CoordOffset(4, 5) != CoordOffset(4, 6)
        True
        """
        if not isinstance(__other, CoordOffset):
            raise TypeError(f"Unsupported type: {type(__other)}")

        return self.delta_x != __other.delta_x or self.delta_y != __other.delta_y
