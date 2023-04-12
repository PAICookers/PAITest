from typing import Literal, Tuple, List, Optional, Union, overload
from pathlib import Path
from .frames.frame import Coord


class paitest:
    def __init__(self,
                 direction: Literal["EAST", "SOUTH", "WEST", "NORTH"],
                 core_coord: Tuple[int, int] = (0, 0)
                 ) -> None: ...

    def GetRandomCasesForNCores(self,
                                N: int,
                                *,
                                save_dir: Optional[Union[str, Path]] = None,
                                masked_core_coord: Optional[Tuple[int, int]] = None
                                ) -> Tuple[Tuple[int, ...], ...]: ...

    def Get1CaseForNCores(self,
                          N: int,
                          *,
                          save_dir: Optional[Union[str, Path]] = None,
                          masked_core_coord: Optional[Tuple[int, int]] = None
                          ) -> Tuple[Tuple[int, ...], ...]: ...

    @overload
    def ReplaceCoreCoord(self, frames: int) -> int: ...
    @overload
    def ReplaceCoreCoord(self, frames: List[int]) -> Tuple[int, ...]: ...
    @overload
    def ReplaceCoreCoord(self, frames: Tuple[int, ...]) -> Tuple[int, ...]: ...

    @overload
    def ReplaceCoreCoord(
        self, frames: int, new_core_coord: Tuple[int, int]) -> int: ...

    @overload
    def ReplaceCoreCoord(
        self, frames: List[int], new_core_coord: Tuple[int, int]) -> Tuple[int, ...]: ...

    @overload
    def ReplaceCoreCoord(
        self, frames: Tuple[int, ...], new_core_coord: Tuple[int, int]) -> Tuple[int, ...]: ...

    @staticmethod
    def SaveFrames(save_path: Union[str, Path],
                   frames: Union[int, List[int], Tuple[int, ...]]
                   ) -> None: ...
