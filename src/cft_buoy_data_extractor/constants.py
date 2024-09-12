from enum import Enum


class Station(str, Enum):
    BOA_GORGONA = "TOS25000001"
    BOA_GIANNUTRI = "TOS25000002"
    GOMBO = "TOS25000003"
    CASTIGLIONE_PESCAIA = "TOS25000004"


class GraphType(str, Enum):
    SIGNIFICANT_WAVE_HEIGHT = "Hm0"
    PEAK_PERIOD = "Tp"
    PEAK_DIRECTION = "Dirp"
    SEA_TEMPERATURE = "Tsea"

