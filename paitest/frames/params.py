from abc import ABC, abstractmethod
import random
from typing import Optional
from .mask import FrameMask as FM


class ParamGen(ABC):
    @staticmethod
    @abstractmethod
    def GenParamConfig1() -> ...:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenParamConfig2() -> ...:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenParamConfig3() -> ...:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def GenParamConfig4() -> ...:
        raise NotImplementedError


class ParamGenOffline(ParamGen):
    """Parameter generation methods for offline cores"""

    @staticmethod
    def GenParamConfig1(seed: Optional[int] = None) -> int:
        """Generate random seed for configuration frame I"""
        if isinstance(seed, int):
            return seed

        return random.randint(0, FM.GENERAL_PAYLOAD_MASK)

    @staticmethod
    def GenParamConfig2():
        """Generate parameter register for configuration frame II"""
        pass

    @staticmethod
    def GenParamConfig3():
        """Generate neuron RAM for configuration frame III"""
        pass

    @staticmethod
    def GenParamConfig4():
        """Generate weight RAM for configuration frame IV"""
        pass

    GenRandomSeed = GenParamConfig1
    GenParamReg = GenParamConfig2
    GenNeuronRAM = GenParamConfig3
    GenWeightRAM = GenParamConfig4


class ParamGenOnline(ParamGen):
    """Parameter generation methods for online cores"""

    @staticmethod
    def GenParamConfig1():
        """Generate LUT for configuration frame I"""
        pass

    @staticmethod
    def GenParamConfig2():
        """Generate core parameter for configuration frame II"""
        pass

    @staticmethod
    def GenParamConfig3():
        """Generate neuron RAM for configuration frame III"""
        pass

    @staticmethod
    def GenParamConfig4():
        """Generate weight RAM for configuration frame IV"""
        pass

    GenLUT = GenParamConfig1
    GenCoreParam = GenParamConfig2
    GenNeuronRAM = GenParamConfig3
    GenWeightRAM = GenParamConfig4
