from .frames.frame import Addr2Coord, Coord2Addr, Coord, FrameGen
from .frames.frame_params import Direction, FrameMask as FM, FrameSubType as FST
from pathlib import Path
from typing import List, Union, Literal, Tuple, Optional
import random
import io
from .log import logger


__all__ = [
    "paitest"
]


class paitest:

    def __init__(self, direction: Literal["EAST", "SOUTH", "WEST", "NORTH"]):
        self._error_code = 0
        self._work_dir: Path
        self._groups: int = 1

        self._verbose: bool = True
        self._fixed_chip_coord: Coord = Coord(0, 0)
        self._fixed_core_coord: Coord
        self._fixed_core_star_coord: Coord = Coord(0, 0)
        self._test_chip_coord: Coord
        self._config_f: io.BytesIO
        self._testin_f: io.BytesIO
        self._testout_f: io.BytesIO

        self._ensure_direction(direction)

    def GetRandomCasesForNCores(self,
                                N: int,
                                save_dir: Union[str, Path],
                                *,
                                config_f: Optional[io.BytesIO] = None,
                                testin_f: Optional[io.BytesIO] = None,
                                testout_f: Optional[io.BytesIO] = None,
                                masked_core_coord: Optional[Coord] = None,
                                is_param_legal: bool = False,
                                verbose: bool = True
                                ) -> None:
        '''
            Generate 'N' different parameters for 'N' cores coordinates. N cores coordinates with N parameters randomly.

            1. save_dir: Where to save the frames file
            2. direction: Test chip direction relative to the location of the core
            3. N: How many groups of configuration-test frames to be generated
            4. masked_core_coord: to avoid genif save_dir:
            self._ensure_dir(save_dir)erating this core coordinate
            5. verbose: Display the logs
        '''
        self._verbose = verbose
        self._ensure_groups(N)

        if save_dir:
            self._ensure_dir(save_dir)

        test_chip_coord: Coord = self._direction.value + self._fixed_core_coord
        params = self._GetNParameters(N, is_param_legal)
        core_coord_list = self._GetNCoresCoord(N, masked_core_coord)

        with open(self._work_dir / "config.bin", "wb") as fc, \
            open(self._work_dir / "testin.bin", "wb") as fi, \
            open(self._work_dir / "testin.bin", "wb") as fo:

            for i in range(N):
                logger.info(f"Generating group #{i+1}/{N}...")
                core_coord = core_coord_list[i]
                param = params[i]

                for j in range(3):
                    config_frame = FrameGen.GenConfigFrame(
                        FST.CONFIG_TYPE2, self._fixed_chip_coord, core_coord, self._fixed_core_star_coord, param[j])

                    fc.write(config_frame.to_bytes(length=8, byteorder="big"))
                    logger.info("Config frame #%d/3: 0x%x in group #%d/%d" %
                                (j+1, config_frame, i+1, N))

                    testout_frame = FrameGen.GenTest2OutFrame(
                        test_chip_coord, core_coord, self._fixed_core_star_coord, param[j])

                    fo.write(testout_frame.to_bytes(length=8, byteorder="big"))
                    logger.info("Test out frame #%d/3: 0x%x in group #%d/%d" %
                                (j+1, testout_frame, i+1, N))

                testin_frame = FrameGen.GenTest2InFrame(
                    test_chip_coord, core_coord, self._fixed_core_star_coord)

                fi.write(testin_frame.to_bytes(length=8, byteorder="big"))
                logger.info("Test out frame #1/1: 0x%x in group #%d/%d" %
                            (testin_frame, i+1, N))

    def Get1CaseForNCores(self,
                          N: int,
                          save_dir: Union[str, Path],
                          *,
                          config_f: Optional[io.BytesIO] = None,
                          testin_f: Optional[io.BytesIO] = None,
                          testout_f: Optional[io.BytesIO] = None,
                          masked_core_coord: Optional[Coord] = None,
                          is_param_legal: bool = False,
                          verbose: bool = True
                          ) -> List[int]:
        '''
            Generate one parameter with N random cores coordinates.

            N cores coordinates with the same parameter.
        '''
        self._verbose = verbose
        self._ensure_groups(N)

        if save_dir:
            self._ensure_dir(save_dir)

        test_chip_coord = self._direction.value + self._fixed_core_coord
        param = self._Get1Parameter(is_param_legal)
        core_coord_list = self._GetNCoresCoord(
            N, masked_coord=masked_core_coord)

        self._config_frames = []
        self._testin_frames = []
        self._testout_frames = []

        with open(self._work_dir / "config.bin", "wb") as fc, \
            open(self._work_dir / "testin.bin", "wb") as fi, \
            open(self._work_dir / "testin.bin", "wb") as fo:

            for i in range(N):
                logger.info(f"Generating group #{i+1}/{N}...")
                core_coord = core_coord_list[i]

                for j in range(3):
                    config_frame = FrameGen.GenConfigFrame(
                        FST.CONFIG_TYPE2, self._fixed_chip_coord, core_coord, self._fixed_core_star_coord, param[j])

                    fc.write(config_frame.to_bytes(length=8, byteorder="big"))
                    logger.info("Config frame #%d/3: 0x%x in group #%d/%d" %
                                (j+1, config_frame, i+1, N))

                    testout_frame = FrameGen.GenTest2OutFrame(
                        test_chip_coord, core_coord, self._fixed_core_star_coord, param[j])

                    fo.write(testout_frame.to_bytes(length=8, byteorder="big"))
                    logger.info("Test out frame #%d/3: 0x%x in group #%d/%d" %
                                (j+1, testout_frame, i+1, N))

                testin_frame = FrameGen.GenTest2InFrame(
                    test_chip_coord, core_coord, self._fixed_core_star_coord)

                fi.write(testin_frame.to_bytes(length=8, byteorder="big"))
                logger.info("Test out frame #1/1: 0x%x in group #%d/%d" %
                            (testin_frame, i+1, N))

        return self._config_frames

    def _Get1CoreCoord(self, masked_coord: Optional[Coord]) -> Coord:
        '''
            Generate a random core coordinate. Indicate the masked one to avoid generating the same one
        '''
        return self._GetNCoresCoord(N=1, masked_coord=masked_coord)[0]

    def _GetNCoresCoord(self,
                        N: Optional[int],
                        masked_coord: Optional[Coord]
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

    def _Coord2Addr(self, coord: Tuple[int, int]) -> int:
        _coord_x = coord[0] & FM.GENERAL_CORE_ADDR_X_MASK
        _coord_y = coord[1] & FM.GENERAL_CORE_ADDR_Y_MASK
        return (_coord_x << 5) | _coord_y

    def _Addr2Coord(self, addr: int) -> Tuple[int, int]:
        _addr = addr & FM.GENERAL_CORE_ADDR_MASK
        return (_addr >> 5, _addr & ((1 << 5) - 1))

    def _Get1Parameter(self,
                       is_legal: bool = False
                       ) -> List[int]:
        '''Generate one group parameter for parameter register'''
        return self._GetNParameters(1, is_legal)[0]

    def _GetNParameters(self,
                        N: Optional[int],
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

    def _ReplaceCoreCoordOf1Frame(self, frame: int, core_coord: Tuple[int, int]) -> int:
        '''Replace the original core coordinate of a frame with a new one.'''
        mask = FM.GENERAL_MASK & \
            (~(FM.GENERAL_CORE_ADDR_MASK << FM.GENERAL_CORE_ADDR_OFFSET))

        core_addr = self._Coord2Addr(core_coord)

        return (frame & mask) | (core_addr << FM.GENERAL_CORE_ADDR_OFFSET)

    def _ReplaceCoreCoordOfNFrames(self,
                                   frames: List[int],
                                   is_random: bool = False,
                                   core_coord: Optional[Coord] = None,
                                   ) -> List[int]:
        '''
            Replace the core coordinate of frames with a specific or random one.

            Indicate the core coordinate to specify it. Keep the parameters still.
        '''
        sample_frame = frames[0]
        assert len(frames) > 1

        # Get the old core coordinate
        if is_random:
            old_core_addr = (
                sample_frame >> FM.GENERAL_CORE_ADDR_OFFSET) & FM.GENERAL_CORE_ADDR_MASK
            old_core_coord = Addr2Coord(old_core_addr)
            self._fixed_core_coord = self._Get1CoreCoord(
                masked_coord=old_core_coord)

        elif isinstance(core_coord, Tuple):
            self._ensure_coord(core_coord)

        else:
            raise ValueError(
                "Please specify the core coordinate when 'is_random' is False")

        mask = FM.GENERAL_MASK & \
            (~(FM.GENERAL_CORE_ADDR_MASK << FM.GENERAL_CORE_ADDR_OFFSET))

        fixed_core_addr = Coord2Addr(self._fixed_core_coord)

        for frame in frames:
            frame = (frame & mask) | (
                fixed_core_addr << FM.GENERAL_CORE_ADDR_OFFSET)

        return frames

    def _ReplaceHeader(self, frame: int, header: FST) -> int:
        '''Replace the header of a frame with the new one.'''
        mask = FM.GENERAL_MASK & \
            (~(FM.GENERAL_HEADER_MASK << FM.GENERAL_HEADER_OFFSET))

        return (frame & mask) | (header.value << FM.GENERAL_HEADER_OFFSET)

    def _ensure_dir(self, user_dir: Union[str, Path]) -> None:
        path_dir: Path = Path(user_dir) if isinstance(
            user_dir, str) else user_dir

        if not path_dir.exists():
            logger.warning(f"Creating directory {path_dir}...")
            path_dir.mkdir(parents=True, exist_ok=True)

        self._work_dir = path_dir

    def _ensure_groups(self, groups: int) -> None:
        if groups > 1024 - 16:
            raise ValueError("Value of groups is no more than 1008")

        self._groups = groups

        logger.info(f"{groups} groups cases will be generated...")

    def _ensure_direction(self, direction: Literal["EAST", "SOUTH", "WEST", "NORTH"]) -> None:
        self._direction = Direction[direction.upper()]

    def _ensure_coord(self, coord: Coord) -> None:
        if coord >= Coord(0b11100, 0b11100):
            raise ValueError("Address coordinate must: x < 28 or y < 28")
