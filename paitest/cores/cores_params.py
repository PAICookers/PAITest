from enum import Enum, unique


@unique
class CoreType(Enum):
    CORE_TYPE_OFFLINE = 1
    CORE_TYPE_ONLINE = 0
