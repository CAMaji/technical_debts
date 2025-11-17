from utilities.custom_json_encoder import CustomJsonEncoder, CustomJsonEncoderInterface
from services.file_metrics_service import FileMetrics
from enum import Enum
from typing import TypeAlias
import heapq
import sys
import math

class RiskLevelEnum(Enum):
    LOW_RISK = 0,
    MEDIUM_RISK = 1,
    HIGH_RISK = 2,
    VERY_HIGH_RISK = 3

# using this class instead of unreadable tuples
class MetricStatistics:
    avg_complexity : float
    identifiable_entities : float
    duplication_count : float
    lines_duplicated : float

    def __init__(self, c, ie, dc, ld): 
        self.avg_complexity = c
        self.identifiable_entities = ie
        self.duplication_count = dc
        self.lines_duplicated = ld
        return
    
    def get(self, i : int) -> float:
        if i == 0: return self.avg_complexity
        if i == 1: return self.identifiable_entities
        if i == 2: return self.duplication_count
        if i == 3: return self.lines_duplicated
        raise Exception("out of bound for metrics statistics")
    
    def set(self, i : int, v : float):
        if i == 0: self.avg_complexity = v;         return
        if i == 1: self.identifiable_entities = v;  return
        if i == 2: self.duplication_count = v;      return
        if i == 3: self.lines_duplicated = v;       return
        raise Exception("out of bound for metrics statistics")

class DebtStatisticsForManyFiles(CustomJsonEncoderInterface):
    metrics    : dict[str, FileMetrics]     # dict of keys (filename) for values (FileMetrics)
    priorities : list[tuple[float, str]]    # list of tuple of (priority, filename)
    risks     : dict[str, RiskLevelEnum]    # dict of keys (filename) for values (RiskLevelEnum)
    maximums : MetricStatistics
    averages : MetricStatistics
    medians : MetricStatistics
    
    def __init__(self): 
        self.metrics = {}
        self.priorities = []
        self.risks = {}
        self.maximums = ()
        self.averages = ()
        self.medians = ()
    
    def encode(self):
        return CustomJsonEncoder.breakdown(self.__dict__)

class DebtStatisticsCalculator: 
    def get_maximums(self, file_metrics : list[FileMetrics]) -> MetricStatistics:
        min_val = 0.0
        maximums = MetricStatistics(min_val, min_val, min_val, min_val)
        
        # trouver valeurs maximales
        for f in file_metrics:
            maximums.set(0, max(maximums.get(0), f.avg_complexity))
            maximums.set(1, max(maximums.get(1), f.identifiable_entities))
            maximums.set(2, max(maximums.get(2), f.duplication_count))
            maximums.set(3, max(maximums.get(3), f.lines_duplicated))

        return maximums

    def get_averages(self, file_metrics : list[FileMetrics]) -> MetricStatistics: 
        average = MetricStatistics(0.0, 0.0, 0.0, 0.0)
        nb_of_files = len(file_metrics)
        if(nb_of_files == 0):
            return average

        for f in file_metrics:
            average.set(0, average.get(0) + f.avg_complexity)
            average.set(1, average.get(1) + f.identifiable_entities)
            average.set(2, average.get(2) + f.duplication_count)
            average.set(3, average.get(3) + f.lines_duplicated)

        average.set(0, average.get(0) / nb_of_files)
        average.set(1, average.get(1) / nb_of_files)
        average.set(2, average.get(2) / nb_of_files)
        average.set(3, average.get(3) / nb_of_files)

        return average

    def get_medians(self, file_metrics : list[FileMetrics]) -> MetricStatistics: 
        medians = MetricStatistics(0.0, 0.0, 0.0, 0.0)

        # il faut qu'une liste soit ordonnée pour calculer la médiane.
        #
        #nb_of_files = len(file_metrics)
        #if(nb_of_files % 2 == 0 and nb_of_files >= 2):
        #    low_index = math.floor((nb_of_files + 1) / 2.0) - 1
        #    high_index = math.ceil((nb_of_files + 1) / 2.0) - 1
        #    
        #    medians.set(0, (file_metrics[low_index].avg_complexity + file_metrics[high_index].avg_complexity) / 2.0)
        #    medians.set(0, (file_metrics[low_index].identifiable_entities + file_metrics[high_index].identifiable_entities) / 2.0)
        #    medians.set(0, (file_metrics[low_index].duplication_count + file_metrics[high_index].duplication_count) / 2.0)
        #    medians.set(0, (file_metrics[low_index].lines_duplicated + file_metrics[high_index].lines_duplicated) / 2.0)
        #else:
        #    index = ((nb_of_files + 1) / 2) - 1
        #    medians.set(0, file_metrics[index].avg_complexity)
        #    medians.set(0, file_metrics[index].identifiable_entities)
        #    medians.set(0, file_metrics[index].duplication_count)
        #    medians.set(0, file_metrics[index].lines_duplicated)

        return medians

    def get_priority(self, avg_complexity_ratio : float, identifiable_entity_ratio : float, duplication_count_ratio : float, lines_duplicated_ratio : float) -> float:
        return 1.0 - (
            avg_complexity_ratio * 0.40 + 
            identifiable_entity_ratio * 0.30 + 
            duplication_count_ratio * 0.20 + 
            lines_duplicated_ratio * 0.10
        )
    
    def get_risk_level(self, complexity) -> RiskLevelEnum:
        # Source: Murphy, James & Robinson III, John. (2007). Design of a Research Platform 
        #         for En Route Conflict Detection and Resolution. 10.2514/6.2007-7803. 
        # https://www.researchgate.net/figure/Cyclomatic-Complexity-Thresholds_tbl2_238659831

        if(complexity <= 10):
            return RiskLevelEnum.LOW_RISK
        if(complexity <= 20): 
            return RiskLevelEnum.MEDIUM_RISK
        if(complexity <= 50): 
            return RiskLevelEnum.HIGH_RISK
        else:
            return RiskLevelEnum.VERY_HIGH_RISK

    def get_ratio(self, max_val : float, value : float) -> float:
        if max_val <= 0: return 0
        else:            return value / max_val

    def get_debt_statistics_for_many_files(self, file_metrics : list[FileMetrics]) -> DebtStatisticsForManyFiles: 
        maximums = self.get_maximums(file_metrics)
        averages = self.get_averages(file_metrics)
        medians = self.get_medians(file_metrics)
        metrics : dict[str, FileMetrics] = {}           # dict of keys (filename) for values (FileMetrics)
        priorities : list[(float, str)] = []            # list of tuple of (priority, filename)
        risks : dict[str, RiskLevelEnum] = {}           # dict of keys (filename) for values (RiskLevelEnum)

        for f in file_metrics: 
            metrics[f.file_name] = f
            risks[f.file_name] = self.get_risk_level(f.avg_complexity)
            avg_complexity_ratio = self.get_ratio(maximums.get(0), f.avg_complexity)
            identifiable_entity_ratio = self.get_ratio(maximums.get(1), f.identifiable_entities)
            duplication_count_ratio = self.get_ratio(maximums.get(2), f.duplication_count)
            lines_duplicated_ratio = self.get_ratio(maximums.get(3), f.lines_duplicated)
            score = self.get_priority(avg_complexity_ratio, identifiable_entity_ratio, duplication_count_ratio, lines_duplicated_ratio)
            heapq.heappush(priorities, (score, f.file_name))
        
        result = DebtStatisticsForManyFiles()
        result.metrics = metrics
        result.risks = risks
        result.priorities = priorities
        result.maximums = maximums
        result.medians = medians
        result.averages = averages
        
        return result
