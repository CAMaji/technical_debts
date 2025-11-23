from src.utilities.json_encoder import JsonEncoder
from enum import Enum
from dataclasses import dataclass, fields

class RiskEnum(Enum):
        LOW_RISK = 0
        MEDIUM_RISK = 1
        HIGH_RISK = 2
        VERY_HIGH_RISK = 3

@dataclass
class TechDebtMetrics(JsonEncoder.Interface):
    average_complexity : float = 0.0
    entities : float = 0.0
    duplications : float = 0.0
    duplicated_lines : float = 0.0

    def get(self, index : int) -> float:
        _fields = fields(TechDebtMetrics)
        return getattr(self, _fields[index].name)
    
    def set(self, index : int, value : float):
        _fields = fields(TechDebtMetrics)
        return setattr(self, _fields[index].name, value)
    
    def length(self) -> int:
        _fields = fields(TechDebtMetrics)
        return len(_fields)

class TechDebtReport(JsonEncoder.Interface):
    """
    Represents a document with statistics of tech debt for a collection of files.
    """

    class File(JsonEncoder.Interface): 
        """
        Represents a row of metrics and statistics for a given file.
        """

        metrics : TechDebtMetrics
        priority : float
        risk : RiskEnum
        filename : str
        
        def __init__(self, filename : str, priority : float, risk : RiskEnum, metrics : TechDebtMetrics):
            self.risk = risk
            self.metrics = metrics
            self.priority = priority
            self.filename = filename

    _metrics    : list[File]
    _maximums   : TechDebtMetrics
    _averages   : TechDebtMetrics
    _medians    : TechDebtMetrics
    _i          : int
    
    def __init__(self, maxs : TechDebtMetrics, avg : TechDebtMetrics, medians : TechDebtMetrics): 
        self._metrics = []
        self._maximums = maxs
        self._averages = avg
        self._medians = medians
        self._i = 0

    def add_file(self, file : File):
        self._metrics.append(file)

    def get_maximums(self) -> TechDebtMetrics: 
        return self._maximums
    
    def get_averages(self) -> TechDebtMetrics:
        return self._averages
    
    def get_medians(self) -> TechDebtMetrics:
        return self._medians
    
    def get_length(self) -> int:
        return len(self._metrics)
    
    def __iter__(self):
        self._i = 0
        return self
    
    def __next__(self) -> File:
        if self._i >= len(self._metrics):
            self._i = 0
            raise StopIteration()
        
        value = self._metrics[self._i]
        self._i += 1
        return value
    