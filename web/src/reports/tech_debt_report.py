from src.utilities.json_encoder import JsonEncoder
from enum import Enum
from dataclasses import dataclass, fields

class RiskEnum(Enum):
    LOW_RISK = 0
    MEDIUM_RISK = 1
    HIGH_RISK = 2
    VERY_HIGH_RISK = 3

    def get_risk(complexity : float) -> Enum: 
        # Source: Murphy, James & Robinson III, John. (2007). Design of a Research Platform 
        #         for En Route Conflict Detection and Resolution. 10.2514/6.2007-7803. 
        # https://www.researchgate.net/figure/Cyclomatic-Complexity-Thresholds_tbl2_238659831

        if(complexity <= 10): return RiskEnum.LOW_RISK
        if(complexity <= 20): return RiskEnum.MEDIUM_RISK
        if(complexity <= 50): return RiskEnum.HIGH_RISK
        else:                 return RiskEnum.VERY_HIGH_RISK

@dataclass
class FunctionDebtMetrics(JsonEncoder.Interface):
    """
    Represents the metrics of a function, contained in a file.
    """
    filename : str = ""
    funcname : str = ""
    complexity : float = 0.0

@dataclass
class FileDebtMetrics(JsonEncoder.Interface):
    """
    Represents the metrics of a file.
    """
    average_complexity : float = 0.0
    entities : float = 0.0
    duplications : float = 0.0
    duplicated_lines : float = 0.0

    def get(self, index : int) -> float:
        _fields = fields(FileDebtMetrics)
        return getattr(self, _fields[index].name)
    
    def set(self, index : int, value : float):
        _fields = fields(FileDebtMetrics)
        return setattr(self, _fields[index].name, value)
    
    def length(self) -> int:
        _fields = fields(FileDebtMetrics)
        return len(_fields)

class TechDebtReport(JsonEncoder.Interface):
    """
    Represents a document with statistics of tech debt for a collection of files.
    """

    class File(JsonEncoder.Interface): 
        """
        Represents a row of metrics and statistics for a given file.
        """

        metrics : FileDebtMetrics
        priority : float
        risk : RiskEnum
        filename : str
        
        def __init__(self, filename : str, priority : float, risk : RiskEnum, metrics : FileDebtMetrics):
            self.risk = risk
            self.metrics = metrics
            self.priority = priority
            self.filename = filename
    
    _metrics    : list[File]
    _maximums   : FileDebtMetrics
    _averages   : FileDebtMetrics
    _medians    : FileDebtMetrics
    _i          : int
    
    def __init__(self, maxs : FileDebtMetrics, avg : FileDebtMetrics, medians : FileDebtMetrics): 
        self._metrics = []
        self._maximums = maxs
        self._averages = avg
        self._medians = medians
        self._i = 0

    def add_file(self, file : File):
        self._metrics.append(file)

    def get_maximums(self) -> FileDebtMetrics: 
        return self._maximums
    
    def get_averages(self) -> FileDebtMetrics:
        return self._averages
    
    def get_medians(self) -> FileDebtMetrics:
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
    