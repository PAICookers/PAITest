from typing import Tuple, List, Optional, Union, overload
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
from pathlib import Path

class paitest:
    if sys.version_info >= (3, 8):
        def __init__(
            self,
            direction: Literal["EAST", "SOUTH", "WEST", "NORTH"] = "EAST",
            fixed_chip_coord: Tuple[int, int] = (0, 0),
        ) -> None: ...
    else:
        def __init__(
            self,
            direction: str = "EAST",
            fixed_chip_coord: Tuple[int, int] = (0, 0),
        ) -> None: ...
    
    def Get1GroupForNCoresWithNParams(
        self,
        N: int,
        *,
        save_dir: Optional[Union[str, Path]] = None,
        masked_core_coord: Optional[Tuple[int, int]] = None
    ) -> Tuple[Tuple[int, ...], ...]: ...
    def Get1GroupForNCoresWith1Param(
        self,
        N: int,
        *,
        save_dir: Optional[Union[str, Path]] = None,
        masked_core_coord: Optional[Tuple[int, int]] = None
    ) -> Tuple[Tuple[int, ...], ...]: ...
    def GetNGroupsFor1CoreWithNParams(
        self,
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
    def ReplaceCoreCoord(self, frames: int, new_core_coord: Tuple[int, int]) -> int: ...
    @overload
    def ReplaceCoreCoord(
        self, frames: List[int], new_core_coord: Tuple[int, int]
    ) -> Tuple[int, ...]: ...
    @overload
    def ReplaceCoreCoord(
        self, frames: Tuple[int, ...], new_core_coord: Tuple[int, int]
    ) -> Tuple[int, ...]: ...
    @staticmethod
    def SaveFrames(
        save_path: Union[str, Path], frames: Union[int, List[int], Tuple[int, ...]]
    ) -> None: ...
