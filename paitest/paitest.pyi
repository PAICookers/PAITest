from typing import Literal, Tuple, List, Optional, Union
from pathlib import Path
import io
from .frames.frame import Coord

class paitest:
    def __init__(self,
                 direction: Literal["EAST", "SOUTH", "WEST", "NORTH"],
                 core_coord: Tuple[int, int] = (0, 0)
                 ) -> None: ...

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
                                ) -> None: ...
    
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
                          ) -> List[int]: ...
