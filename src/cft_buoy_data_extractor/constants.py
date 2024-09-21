from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class Station(str, Enum):
    BOA_GORGONA = "TOS25000001"
    BOA_GIANNUTRI = "TOS25000002"
    GOMBO = "TOS25000003"
    CASTIGLIONE_PESCAIA = "TOS25000004"


@dataclass
class Graph(ABC):
    date: str
    hours: int

    @property
    @abstractmethod
    def unit(cls):
        pass

    @property
    @abstractmethod
    def type(cls):
        pass

    def get_xaxis_value(self, value: float) -> float:
        return value / 10 * self.hours

    @staticmethod
    def get_yaxis_value(value: float) -> float:
        pass


class SignificantWaveHeight(Graph):
    unit = "cm"
    type = "Hm0"

    @staticmethod
    def get_yaxis_value(value: float) -> float:
        """From 0 to 800 cm"""
        return value * 800


class PeakPeriod(Graph):
    unit = "s"
    type = "Tp"

    @staticmethod
    def get_yaxis_value(value: float) -> float:
        """From 0 to 30 seconds"""
        return value * 30


class PeakDirection(Graph):
    unit = "°"
    type = "Dirp"

    @staticmethod
    def get_yaxis_value(value: float) -> float:
        """From 0 to 360 degrees"""
        return value * 360
        

class SeaTemperature(Graph):
    unit = "°C"
    type = "Tsea"

    @staticmethod
    def get_yaxis_value(value: float) -> float:
        """From 10 to 30 degrees Celsius"""
        return value * 20 + 10
