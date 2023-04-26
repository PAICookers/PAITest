import random
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union

from .frames import Addr2Coord, Coord, Coord2Addr, Direction, FrameGen
from .frames import FrameMask as FM
from .frames import FrameSubType as FST
from .log import logger

if sys.version_info >= (3, 8):
    from typing import Literal


__all__ = ["paitest"]


class paitest:
    def __init__(
        self,
        direction="EAST",
        fixed_chip_coord: Tuple[int, int] = (0, 0),
    ) -> None:
        """
        :param direction: The direction relative to the PAICORE. Default is 'EAST'.
        :param fixed_chip_coord: The chip address of the PAICORE under test. Default is (0, 0).
        """
        self._verbose: bool = True
        self._fixed_chip_coord: Coord = Coord(fixed_chip_coord)
        self._masked_core_coord: Coord
        self._fixed_core_star_coord: Coord = Coord(0, 0)
        self._test_chip_coord: Coord

        self._ensure_direction(direction)

    def Get1GroupForNCoresWithNParams(
        self,
        N: int,
        *,
        save_dir: Optional[Union[str, Path]] = None,
        masked_core_coord: Optional[Tuple[int, int]] = None,
        gen_txt: bool = False,
        verbose: bool = False,
    ) -> Tuple[Tuple[int, ...], ...]:
        """
        Generate 1 group(case) for 'N' random cores coordinates with 'N' different parameters.

        - `N`: How many cores coordinates under test.
        - `save_dir`: Where to save the frames files.
        - `masked_core_coord`: to avoid generating the specific core coordinate.
        - `gen_txt`: to save frames into text files instead of default binary files.
        - `verbose`: whether to display the log.

        :return: 3 tuples including config, testin & testout tuples. 3*N frames in config & testout tuple and N frames in testin tuple.
        """
        self._ensure_cores(N)

        if save_dir:
            work_dir = self._ensure_dir(save_dir)
        else:
            work_dir = None

        # 1. Get the test chip coordinate.
        test_chip_coord: Coord = self._direction.value + self._fixed_chip_coord

        # 2. Get N core coordinates list.
        if isinstance(masked_core_coord, Tuple):
            _masked_core_coord = Coord(masked_core_coord)
        else:
            _masked_core_coord = None

        core_coords = self._GetNCoresCoord(N, _masked_core_coord)

        # 3. Get N parameters reg.
        params = self._GetNParams(N, core_coords, False)

        cf_list: List[int] = []
        ti_list: List[int] = []
        to_list: List[int] = []

        for i in range(N):
            if verbose:
                logger.info(f"Generating test group #{i+1}/{N}...")
            core_coord = core_coords[i]
            param = params[i]

            for j in range(3):
                config_frame = FrameGen.GenConfigFrame(
                    FST.CONFIG_TYPE2,
                    self._fixed_chip_coord,
                    core_coord,
                    self._fixed_core_star_coord,
                    param[j],
                )
                testout_frame = FrameGen.GenTest2OutFrame(
                    test_chip_coord, core_coord, self._fixed_core_star_coord, param[j]
                )
                cf_list.append(config_frame)
                to_list.append(testout_frame)

                if verbose:
                    logger.info(
                        "Config frame   #%d/3:  0x%x in group #%d/%d"
                        % (j + 1, config_frame, i + 1, N)
                    )
                    logger.info(
                        "Test out frame #%d/3:  0x%x in group #%d/%d"
                        % (j + 1, testout_frame, i + 1, N)
                    )

            testin_frame = FrameGen.GenTest2InFrame(
                self._fixed_chip_coord, core_coord, self._fixed_core_star_coord
            )
            ti_list.append(testin_frame)

            if verbose:
                logger.info(
                    "Test in frame  #1/1:  0x%x in group #%d/%d"
                    % (testin_frame, i + 1, N)
                )

        if isinstance(work_dir, Path):
            _suffix = ".txt" if gen_txt else ".bin"
            self.SaveFrames(work_dir / ("config" + _suffix), cf_list, verbose)
            self.SaveFrames(work_dir / ("testin" + _suffix), ti_list, verbose)
            self.SaveFrames(work_dir / ("testout" + _suffix), to_list, verbose)

        return tuple(cf_list), tuple(ti_list), tuple(to_list)

    def Get1GroupForNCoresWith1Param(
        self,
        N: int,
        *,
        save_dir: Optional[Union[str, Path]] = None,
        masked_core_coord: Optional[Tuple[int, int]] = None,
        gen_txt: bool = False,
        verbose: bool = False,
    ) -> Tuple[Tuple[int, ...], ...]:
        """
        Generate 1 group(case) for 'N' random cores coordinates with the same parameters.

        - `N`: How many cores coordinates under test.
        - `save_dir`: Where to save the frames files.
        - `masked_core_coord`: to avoid generating the specific core coordinate.
        - `gen_txt`: to save frames into text files instead of default binary files.
        - `verbose`: whether to display the log.

        :return: 3 tuples including config, testin & testout tuples. 3*N frames in config & testout tuple and N frames in testin tuple.
        """
        self._ensure_cores(N)

        if save_dir:
            work_dir = self._ensure_dir(save_dir)
        else:
            work_dir = None

        # 1. Get the test chip coordinate.
        test_chip_coord = self._direction.value + self._fixed_chip_coord

        # 2. Get N core coordinates list.
        if isinstance(masked_core_coord, Tuple):
            _masked_core_coord = Coord(masked_core_coord)
        else:
            _masked_core_coord = None

        core_coords = self._GetNCoresCoord(N, _masked_core_coord)

        # 3. Get the parameters reg.
        param: Tuple[int, ...] = self._Get1Param(core_coords, False)

        cf_list: List[int] = []
        ti_list: List[int] = []
        to_list: List[int] = []

        for i in range(N):
            if verbose:
                logger.info(f"Generating test group #{i+1}/{N}...")
            core_coord = core_coords[i]

            for j in range(3):
                config_frame = FrameGen.GenConfigFrame(
                    FST.CONFIG_TYPE2,
                    self._fixed_chip_coord,
                    core_coord,
                    self._fixed_core_star_coord,
                    param[j],
                )
                testout_frame = FrameGen.GenTest2OutFrame(
                    test_chip_coord, core_coord, self._fixed_core_star_coord, param[j]
                )
                cf_list.append(config_frame)
                to_list.append(testout_frame)

                if verbose:
                    logger.info(
                        "Config frame   #%d/3:  0x%x in group #%d/%d"
                        % (j + 1, config_frame, i + 1, N)
                    )
                    logger.info(
                        "Test out frame #%d/3:  0x%x in group #%d/%d"
                        % (j + 1, testout_frame, i + 1, N)
                    )

            testin_frame = FrameGen.GenTest2InFrame(
                self._fixed_chip_coord, core_coord, self._fixed_core_star_coord
            )
            ti_list.append(testin_frame)

            if verbose:
                logger.info(
                    "Test in frame  #1/1:  0x%x in group #%d/%d"
                    % (testin_frame, i + 1, N)
                )

        if isinstance(work_dir, Path):
            _suffix = ".txt" if gen_txt else ".bin"
            self.SaveFrames(work_dir / ("config" + _suffix), cf_list, verbose)
            self.SaveFrames(work_dir / ("testin" + _suffix), ti_list, verbose)
            self.SaveFrames(work_dir / ("testout" + _suffix), to_list, verbose)

        return tuple(cf_list), tuple(ti_list), tuple(to_list)

    def GetNGroupsFor1CoreWithNParams(
        self,
        N: int,
        *,
        save_dir: Optional[Union[str, Path]] = None,
        masked_core_coord: Optional[Tuple[int, int]] = None,
        gen_txt: bool = False,
        verbose: bool = False,
    ) -> Tuple[Tuple[int, ...], ...]:
        """
        Generate 'N' groups(cases) for 1 random core coordinate with 'N' different parameters.

        - `N`: How many test groups(cases) of 1 core will be generated.
        - `save_dir`: Where to save the frames files.
        - `masked_core_coord`: to avoid generating the specific core coordinate.
        - `gen_txt`: to save frames into text files instead of default binary files.
        - `verbose`: whether to display the log.

        :return: 3 tuples including config, testin & testout tuples. 3*N frames in config & testout tuple and N frames in testin tuple.
        """
        self._ensure_cores(N)

        if save_dir:
            work_dir = self._ensure_dir(save_dir)
        else:
            work_dir = None

        # 1. Get the test chip coordinate.
        test_chip_coord = self._direction.value + self._fixed_chip_coord

        # 2. Get the core coordinates list.
        if isinstance(masked_core_coord, Tuple):
            _masked_core_coord = Coord(masked_core_coord)
        else:
            _masked_core_coord = None

        core_coord = self._Get1CoreCoord(_masked_core_coord)

        # 3. Get the parameters reg.
        params = self._GetNParams(N, core_coord, False)

        cf_list: List[int] = []
        ti_list: List[int] = []
        to_list: List[int] = []

        for i in range(N):
            if verbose:
                logger.info(f"Generating test group #{i+1}/{N}...")
            param = params[i]

            for j in range(3):
                config_frame = FrameGen.GenConfigFrame(
                    FST.CONFIG_TYPE2,
                    self._fixed_chip_coord,
                    core_coord,
                    self._fixed_core_star_coord,
                    param[j],
                )
                testout_frame = FrameGen.GenTest2OutFrame(
                    test_chip_coord, core_coord, self._fixed_core_star_coord, param[j]
                )
                cf_list.append(config_frame)
                to_list.append(testout_frame)

                if verbose:
                    logger.info(
                        "Config frame   #%d/3:  0x%x in group #%d/%d"
                        % (j + 1, config_frame, i + 1, N)
                    )
                    logger.info(
                        "Test out frame #%d/3:  0x%x in group #%d/%d"
                        % (j + 1, testout_frame, i + 1, N)
                    )

            testin_frame = FrameGen.GenTest2InFrame(
                self._fixed_chip_coord, core_coord, self._fixed_core_star_coord
            )
            ti_list.append(testin_frame)

            if verbose:
                logger.info(
                    "Test in frame  #1/1:  0x%x in group #%d/%d"
                    % (testin_frame, i + 1, N)
                )

        if isinstance(work_dir, Path):
            _suffix = ".txt" if gen_txt else ".bin"
            self.SaveFrames(work_dir / ("config" + _suffix), cf_list, verbose)
            self.SaveFrames(work_dir / ("testin" + _suffix), ti_list, verbose)
            self.SaveFrames(work_dir / ("testout" + _suffix), to_list, verbose)

        return tuple(cf_list), tuple(ti_list), tuple(to_list)

    def ReplaceCoreCoord(
        self,
        frames: Union[int, List[int], Tuple[int, ...]],
        new_core_coord: Optional[Union[Tuple[int, int], Coord]] = None,
    ) -> Union[int, Tuple[int, ...]]:
        """
        Replace the core coordinate with the new one.

        - frames: of which the core coordinate you want to replace. It can be a single frame, or a list or tuple.
        - new_core_coord: The new core coordinate. If not specified, it will generate one randomly.
        """
        if isinstance(frames, int):
            _frame = frames
        else:
            _frame = frames[0]

        if isinstance(new_core_coord, Tuple):
            _new_core_coord = Coord(new_core_coord)
            self._ensure_coord(_new_core_coord)
        elif isinstance(new_core_coord, Coord):
            _new_core_coord = new_core_coord
            self._ensure_coord(_new_core_coord)
        else:
            # Auto mask the old core coordinate then random pick one
            old_core_addr = (
                _frame >> FM.GENERAL_CORE_ADDR_OFFSET
            ) & FM.GENERAL_CORE_ADDR_MASK
            old_core_coord = Addr2Coord(old_core_addr)
            _new_core_coord = self._Get1CoreCoord(old_core_coord)

        if isinstance(frames, int):
            return self._ReplaceCoreCoordIn1Frame(_frame, _new_core_coord)
        else:
            _frames = list(frames)
            return self._ReplaceCoreCoordInNFrames(_frames, _new_core_coord)

    @staticmethod
    def SaveFrames(
        save_path: Union[str, Path],
        frames: Union[int, List[int], Tuple[int, ...]],
        verbose: bool = False,
    ) -> None:
        """
        Write frames into specific binary file. Files with '.bin' suffix is recommended

        Support .txt files as well.

        - gen_txt: Wether to generate txt files.
        """

        _path = Path(save_path)
        _suffix: str = _path.suffix

        if _suffix != ".bin" and _suffix != ".txt":
            raise NotImplementedError(
                f"File with suffix {_suffix} is not supported!")

        if _suffix == ".bin":
            with open(_path, "wb") as f:
                if isinstance(frames, int):
                    f.write(frames.to_bytes(8, "big"))
                else:
                    for frame in frames:
                        f.write(frame.to_bytes(8, "big"))

        else:
            with open(_path, "w") as f:  # Open with "w"
                if isinstance(frames, int):
                    _str64 = bin(frames).split("0b")[1]
                    _str64 = _str64.zfill(64)
                    f.write(_str64 + "\n")
                else:
                    for frame in frames:
                        _str64 = bin(frame).split("0b")[1]
                        _str64 = _str64.zfill(64)
                        f.write(_str64 + "\n")

        if verbose:
            logger.info(f"Saved frame(s) into {_path} OK")

    def _Get1CoreCoord(self, masked_coord: Optional[Coord] = None) -> Coord:
        """
        Generate a random core coordinate. Indicate the masked one to avoid generating the same one
        """
        return self._GetNCoresCoord(N=1, masked_coord=masked_coord)[0]

    def _GetNCoresCoord(
        self, N: int, masked_coord: Optional[Coord] = None
    ) -> List[Coord]:
        """
        Generate 'N' unique cores coordinates. Optional for excluding one masked core address
        """

        def _CoordGenerator():
            coordinates = set()

            if isinstance(masked_coord, Coord):
                coordinates.add((masked_coord.x, masked_coord.y))

            while True:
                x = random.randint(0, FM.GENERAL_CHIP_ADDR_X_MASK)
                y = random.randint(0, FM.GENERAL_CHIP_ADDR_Y_MASK)

                if (x, y) not in coordinates and Coord(x, y) < Coord(0b11100, 0b11100):
                    coordinates.add((x, y))
                    yield Coord(x, y)

        if isinstance(masked_coord, Coord):
            self._ensure_coord(masked_coord)
            if N > 1007:
                raise ValueError(
                    "When choose to mask a core, the max value of cores to be generated is 1007"
                )

        generator = _CoordGenerator()
        core_coord_list = [next(generator) for _ in range(N)]

        return core_coord_list

    def _Get1Param(
        self, core_coords: Union[List[Coord], Coord], is_legal: bool = False
    ) -> Tuple[int, ...]:
        """Generate one group parameter for parameter register"""
        return self._GetNParams(1, core_coords, is_legal)[0]

    def _GetNParams(
        self,
        N: int,
        core_coords: Union[List[Coord], Coord],
        is_legal: bool = False,
    ) -> List[Tuple[int, ...]]:
        """
        Generate 'N' random parameters register.
        - `is_legal`: whether to generate legal parameters for every core
        """

        def _ParamGenerator():
            test_chip_coord: Coord = self._direction.value + self._fixed_chip_coord

            while True:
                for core_coord in _core_coords:
                    if is_legal:
                        # TODO: Do legal generation here, including direction config
                        raise NotImplementedError
                    else:
                        param = FrameGen.GenConfigGroup(
                            FST.CONFIG_TYPE2,
                            self._fixed_chip_coord,
                            core_coord,
                            self._fixed_core_star_coord,
                            test_chip_coord,
                        )

                    yield param

        if isinstance(core_coords, Coord):
            _core_coords = [core_coords]
        else:
            _core_coords = core_coords

        generator = _ParamGenerator()
        parameters = [next(generator) for _ in range(N)]

        return parameters

    def _ReplaceCoreCoordIn1Frame(self, frame: int, new_core_coord: Coord) -> int:
        """Replace the original core coordinate of a frame with a new one."""
        mask = FM.GENERAL_MASK & (
            ~(FM.GENERAL_CORE_ADDR_MASK << FM.GENERAL_CORE_ADDR_OFFSET)
        )

        new_core_addr = Coord2Addr(new_core_coord)

        return (frame & mask) | (new_core_addr << FM.GENERAL_CORE_ADDR_OFFSET)

    def _ReplaceCoreCoordInNFrames(
        self,
        frames: List[int],
        new_core_coord: Coord,
    ) -> Tuple[int, ...]:
        """
        Replace the core coordinate of frames with a specific or random one. Keep the parameters still.
        """
        mask = FM.GENERAL_MASK & (
            ~(FM.GENERAL_CORE_ADDR_MASK << FM.GENERAL_CORE_ADDR_OFFSET)
        )

        new_core_addr = Coord2Addr(new_core_coord)

        for i, frame in enumerate(frames):
            frames[i] = (frame & mask) | (
                new_core_addr << FM.GENERAL_CORE_ADDR_OFFSET)

        return tuple(frames)

    def _ReplaceHeader(self, frame: int, header: FST) -> int:
        """Replace the header of a frame with the new one."""
        mask = FM.GENERAL_MASK & (
            ~(FM.GENERAL_HEADER_MASK << FM.GENERAL_HEADER_OFFSET))

        return (frame & mask) | (header.value << FM.GENERAL_HEADER_OFFSET)

    def _ensure_dir(self, user_dir: Union[str, Path]) -> Path:
        _user_dir: Path = Path(user_dir)

        if not _user_dir.exists():
            logger.warning(f"Creating directory {_user_dir}...")
            _user_dir.mkdir(parents=True, exist_ok=True)

        return _user_dir

    def _ensure_cores(self, Ncores: int) -> None:
        if Ncores > 1024 - 16 or Ncores < 1:
            raise ValueError("Range of Ncores is 0 < N < 1008")

    if sys.version_info >= (3, 8):

        def _ensure_direction(
            self, direction: Literal["EAST", "SOUTH", "WEST", "NORTH"]
        ) -> None:
            try:
                self._direction = Direction[direction.upper()]
            except KeyError:
                raise KeyError(f"{direction} is an illegal direction!")

    else:

        def _ensure_direction(self, direction: str) -> None:
            try:
                self._direction = Direction[direction.upper()]
            except KeyError:
                raise KeyError(f"{direction} is an illegal direction!")

    def _ensure_coord(self, coord: Coord) -> None:
        if coord >= Coord(0b11100, 0b11100):
            raise ValueError(
                "Address coordinate must: 0 <= x < 28 or 0 <= y < 28")

        self._masked_core_coord = coord
