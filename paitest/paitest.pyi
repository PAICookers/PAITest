from typing import Literal, List, Optional
from .frames.frame import Coord

class paitest:
    def __init__(self, direction: Literal["EAST", "SOUTH", "WEST", "NORTH"]): ...

    def GetRandomCasesForNCores(self,
                                N: int,
                                *,
                                masked_core_coord: Optional[Coord] = None,
                                is_param_legal: bool = False,
                                verbose: bool = True
                                ) -> None: ...
    
    def Get1CaseForNCores(self,
                          N: int,
                          *,
                          masked_core_coord: Optional[Coord] = None,
                          is_param_legal: bool = False,
                          verbose: bool = True
                          ) -> List[int]: ...
