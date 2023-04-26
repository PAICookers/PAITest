import sys
from typing import List, Optional, Tuple, Union

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
        masked_core_coord: Optional[Tuple[int, int]] = None,
        gen_txt: bool = False,
        verbose: bool = False
    ) -> Tuple[Tuple[int, ...], ...]: ...
    def Get1GroupForNCoresWith1Param(
        self,
        N: int,
        *,
        save_dir: Optional[Union[str, Path]] = None,
        masked_core_coord: Optional[Tuple[int, int]] = None,
        gen_txt: bool = False,
        verbose: bool = False
    ) -> Tuple[Tuple[int, ...], ...]: ...
    def GetNGroupsFor1CoreWithNParams(
        self,
        N: int,
        *,
        save_dir: Optional[Union[str, Path]] = None,
        masked_core_coord: Optional[Tuple[int, int]] = None,
        gen_txt: bool = False,
        verbose: bool = False
    ) -> Tuple[Tuple[int, ...], ...]: ...
    def ReplaceCoreCoord(
        self,
        frames: Union[int, List[int], Tuple[int, ...]],
        new_core_coord: Tuple[int, int],
    ) -> int: ...
    @staticmethod
    def SaveFrames(
        save_path: Union[str, Path],
        frames: Union[int, List[int], Tuple[int, ...]],
        verbose: bool = False,
    ) -> None: ...
