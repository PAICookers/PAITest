from .frames import Addr2Coord, Coord2Addr, Coord, FrameGen, \
    Direction, FrameMask as FM, FrameSubType as FST
from pathlib import Path
from typing import List, Union, Literal, Tuple, Optional
import random
import io
from .log import logger


__all__ = [
    "paitest"
]


class paitest:

    def __init__(self,
                 direction: Literal["EAST", "SOUTH", "WEST", "NORTH"],
                 core_coord: Tuple[int, int] = (0, 0)
                 ) -> None:

        self._work_dir: Union[Path, None] = None
        self._fc: io.BufferedWriter
        self._fi: io.BufferedWriter
        self._fo: io.BufferedWriter
        self._groups: int = 1

        self._verbose: bool = True
        self._fixed_chip_coord: Coord = Coord(0, 0)
        self._fixed_core_coord: Coord = Coord(core_coord)
        self._masked_core_coord: Coord
        self._fixed_core_star_coord: Coord = Coord(0, 0)
        self._test_chip_coord: Coord

        self._ensure_direction(direction)

    def GetRandomCasesForNCores(self,
                                N: int,
                                *,
                                save_dir: Optional[Union[str, Path]] = None,
                                masked_core_coord: Optional[Tuple[int, int]] = None
                                ) -> Tuple[Tuple[int, ...], ...]:
        '''
            Generate 1 group case for 'N' cores coordinates with 'N' different parameters.

            1. save_dir: Where to save the frames file
            2. direction: Test chip direction relative to the location of the core
            3. N: How many groups of configuration-test frames to be generated
            4. masked_core_coord: to avoid genif save_dir:
            5. verbose: Display the logs
        '''
        self._ensure_groups(N)

        if save_dir:
            self._ensure_dir(save_dir)
        else:
            self._work_dir = None

        test_chip_coord: Coord = self._direction.value + self._fixed_core_coord
        params = self._GetNParameters(N, False)

        _masked_core_coord = Coord(masked_core_coord) if isinstance(
            masked_core_coord, Tuple) else None

        core_coord_list = self._GetNCoresCoord(N, _masked_core_coord)

        cf_list: List[int] = []
        ti_list: List[int] = []
        to_list: List[int] = []

        if self._work_dir:
            self._fc = open(self._work_dir / "config.bin", "wb")
            self._fi = open(self._work_dir / "testin.bin", "wb")
            self._fo = open(self._work_dir / "testout.bin", "wb")

        for i in range(N):
            logger.info(f"Generating group #{i+1}/{N}...")
            core_coord = core_coord_list[i]
            param = params[i]

            for j in range(3):
                config_frame = FrameGen.GenConfigFrame(
                    FST.CONFIG_TYPE2, self._fixed_chip_coord, core_coord, self._fixed_core_star_coord, param[j])
                cf_list.append(config_frame)
                logger.info("Config frame   #%d/3:  0x%x in group #%d/%d" %
                            (j+1, config_frame, i+1, N))

                testout_frame = FrameGen.GenTest2OutFrame(
                    test_chip_coord, core_coord, self._fixed_core_star_coord, param[j])
                to_list.append(testout_frame)
                logger.info("Test out frame #%d/3:  0x%x in group #%d/%d" %
                            (j+1, testout_frame, i+1, N))

                if self._work_dir:
                    self._fc.write(config_frame.to_bytes(
                        length=8, byteorder="big"))
                    self._fo.write(testout_frame.to_bytes(
                        length=8, byteorder="big"))

            testin_frame = FrameGen.GenTest2InFrame(
                test_chip_coord, core_coord, self._fixed_core_star_coord)
            ti_list.append(testin_frame)
            logger.info("Test in frame  #1/1:  0x%x in group #%d/%d" %
                        (testin_frame, i+1, N))

            if self._work_dir:
                self._fi.write(testin_frame.to_bytes(
                    length=8, byteorder="big"))

        if self._work_dir:
            self._fc.close()
            self._fi.close()
            self._fo.close()

        return tuple(cf_list), tuple(ti_list), tuple(to_list)

    def Get1CaseForNCores(self,
                          N: int,
                          *,
                          save_dir: Optional[Union[str, Path]] = None,
                          masked_core_coord: Optional[Tuple[int, int]] = None
                          ) -> Tuple[Tuple[int, ...], ...]:
        '''
            Generate 1 group case for 'N' random cores coordinates with the same parameters.

            Always return 3 tuples including 'N' tuples.
        '''
        self._ensure_groups(N)

        if save_dir:
            self._ensure_dir(save_dir)
        else:
            self._work_dir = None

        test_chip_coord = self._direction.value + self._fixed_core_coord
        param = self._Get1Parameter(False)

        _masked_core_coord = Coord(masked_core_coord) if isinstance(
            masked_core_coord, Tuple) else None

        core_coord_list = self._GetNCoresCoord(
            N, masked_coord=_masked_core_coord)

        cf_list: List[int] = []
        ti_list: List[int] = []
        to_list: List[int] = []

        if self._work_dir:
            self._fc = open(self._work_dir / "config.bin", "wb")
            self._fi = open(self._work_dir / "testin.bin", "wb")
            self._fo = open(self._work_dir / "testout.bin", "wb")

        for i in range(N):
            logger.info(f"Generating group #{i+1}/{N}...")
            core_coord = core_coord_list[i]

            for j in range(3):
                config_frame = FrameGen.GenConfigFrame(
                    FST.CONFIG_TYPE2, self._fixed_chip_coord, core_coord, self._fixed_core_star_coord, param[j])
                cf_list.append(config_frame)
                logger.info("Config frame   #%d/3:  0x%x in group #%d/%d" %
                            (j+1, config_frame, i+1, N))

                testout_frame = FrameGen.GenTest2OutFrame(
                    test_chip_coord, core_coord, self._fixed_core_star_coord, param[j])
                to_list.append(testout_frame)
                logger.info("Test out frame #%d/3:  0x%x in group #%d/%d" %
                            (j+1, testout_frame, i+1, N))

                if self._work_dir:
                    self._fc.write(config_frame.to_bytes(
                        length=8, byteorder="big"))
                    self._fo.write(testout_frame.to_bytes(
                        length=8, byteorder="big"))

            testin_frame = FrameGen.GenTest2InFrame(
                test_chip_coord, core_coord, self._fixed_core_star_coord)
            ti_list.append(testin_frame)
            logger.info("Test in frame  #1/1:  0x%x in group #%d/%d" %
                        (testin_frame, i+1, N))

            if self._work_dir:
                self._fi.write(testin_frame.to_bytes(
                    length=8, byteorder="big"))

        return tuple(cf_list), tuple(ti_list), tuple(to_list)

    def ReplaceCoreCoord(self,
                         frames: Union[int, List[int], Tuple[int, ...]],
                         new_core_coord: Optional[Tuple[int, int]] = None,
                         ) -> Union[int, Tuple[int, ...]]:

        if isinstance(frames, int):
            _frame = frames
        else:
            _frame = frames[0]

        if isinstance(new_core_coord, Tuple):
            _new_core_coord = Coord(new_core_coord)
        else:
            # Auto mask the old core coordinate then random pick one
            old_core_addr = (
                _frame >> FM.GENERAL_CORE_ADDR_OFFSET) & FM.GENERAL_CORE_ADDR_MASK
            old_core_coord = Addr2Coord(old_core_addr)
            _new_core_coord = self._Get1CoreCoord(old_core_coord)

        if isinstance(frames, int):
            return self._ReplaceCoreCoordIn1Frame(_frame, _new_core_coord)
        else:
            _frames = list(frames)
            return self._ReplaceCoreCoordInNFrames(_frames, _new_core_coord)

    @staticmethod
    def SaveFrames(save_path: Union[str, Path],
                   frames: Union[int, List[int], Tuple[int, ...]]
                   ) -> None:
        '''Write frames into specific binary file. Must be '.bin' suffix.'''

        _path = Path(save_path)

        if not _path.suffix == ".bin":
            raise ValueError

        with open(_path, "wb") as f:
            if isinstance(frames, int):
                f.write(frames.to_bytes(8, "big"))
            else:
                for frame in frames:
                    f.write(frame.to_bytes(8, "big"))

    def _Get1CoreCoord(self, masked_coord: Optional[Coord] = None) -> Coord:
        '''
            Generate a random core coordinate. Indicate the masked one to avoid generating the same one
        '''
        return self._GetNCoresCoord(N=1, masked_coord=masked_coord)[0]

    def _GetNCoresCoord(self,
                        N: Optional[int] = None,
                        masked_coord: Optional[Coord] = None
                        ) -> List[Coord]:
        '''
            Generate 'N' unique cores coordinates. Optional for excluding one masked core address
        '''
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

        if not isinstance(N, int):
            N = self._groups

        if isinstance(masked_coord, Tuple):
            self._ensure_coord(masked_coord)

        if N == 1008 and isinstance(masked_coord, Tuple):
            N = 1007

        generator = _CoordGenerator()
        core_addr_list = [next(generator) for _ in range(N)]

        return core_addr_list

    def _Get1Parameter(self, is_legal: bool = False) -> List[int]:
        '''Generate one group parameter for parameter register'''
        return self._GetNParameters(1, is_legal)[0]

    def _GetNParameters(self,
                        N: Optional[int] = None,
                        is_legal: bool = False,
                        ) -> List[List[int]]:
        '''
            Generate 'N' groups parameter for parameter register.

            is_legal: whether to generate legal parameters for every core
        '''
        def _ParamGenerator():
            test_chip_coord: Coord = self._direction.value + self._fixed_core_coord

            while True:

                if is_legal:
                    # TODO: Do legal generation here, including direction config
                    param = [0, 0, 0]
                    pass
                else:
                    param = FrameGen.GenConfigGroup(
                        FST.CONFIG_TYPE2, self._fixed_chip_coord, self._fixed_core_coord,
                        self._fixed_core_star_coord, test_chip_coord)

                yield param

        if not isinstance(N, int):
            N = self._groups

        generator = _ParamGenerator()
        parameters = [next(generator) for _ in range(N)]

        return parameters

    def _ReplaceCoreCoordIn1Frame(self, frame: int, new_core_coord: Coord) -> int:
        '''Replace the original core coordinate of a frame with a new one.'''
        mask = FM.GENERAL_MASK & \
            (~(FM.GENERAL_CORE_ADDR_MASK << FM.GENERAL_CORE_ADDR_OFFSET))

        new_core_addr = Coord2Addr(new_core_coord)

        return (frame & mask) | (new_core_addr << FM.GENERAL_CORE_ADDR_OFFSET)

    def _ReplaceCoreCoordInNFrames(self,
                                   frames: List[int],
                                   new_core_coord: Coord,
                                   ) -> Tuple[int, ...]:
        '''
            Replace the core coordinate of frames with a specific or random one.

            Indicate the core coordinate to specify it. Keep the parameters still.
        '''
        mask = FM.GENERAL_MASK & \
            (~(FM.GENERAL_CORE_ADDR_MASK << FM.GENERAL_CORE_ADDR_OFFSET))

        new_core_addr = Coord2Addr(new_core_coord)

        for frame in frames:
            frame = (frame & mask) | (
                new_core_addr << FM.GENERAL_CORE_ADDR_OFFSET)

        return tuple(frames)

    def _ReplaceHeader(self, frame: int, header: FST) -> int:
        '''Replace the header of a frame with the new one.'''
        mask = FM.GENERAL_MASK & \
            (~(FM.GENERAL_HEADER_MASK << FM.GENERAL_HEADER_OFFSET))

        return (frame & mask) | (header.value << FM.GENERAL_HEADER_OFFSET)

    def _ensure_dir(self, user_dir: Union[str, Path]) -> None:
        _user_dir: Path = Path(user_dir)

        if not _user_dir.exists():
            logger.warning(f"Creating directory {_user_dir}...")
            _user_dir.mkdir(parents=True, exist_ok=True)

        self._work_dir = _user_dir

    def _ensure_groups(self, groups: int) -> None:
        if groups > 1024 - 16:
            raise ValueError("Value of groups is no more than 1008")

        self._groups = groups

        logger.info(f"{groups} groups cases will be generated...")

    def _ensure_direction(self, direction: Literal["EAST", "SOUTH", "WEST", "NORTH"]) -> None:
        self._direction = Direction[direction.upper()]

    def _ensure_coord(self, coord: Coord) -> None:
        if coord >= Coord(0b11100, 0b11100):
            raise ValueError(
                "Address coordinate must: 0 <= x < 28 or 0 <= y < 28")

        self._masked_core_coord = coord
