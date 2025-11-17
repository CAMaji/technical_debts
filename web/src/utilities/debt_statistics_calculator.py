from src.utilities.custom_json_encoder import CustomJsonEncoder, CustomJsonEncoderInterface
from src.services.file_metrics_service import FileMetrics
from enum import Enum
import math

class RiskLevelEnum(Enum):
    LOW_RISK = 0,
    MEDIUM_RISK = 1,
    HIGH_RISK = 2,
    VERY_HIGH_RISK = 3

class MetricStatistics:
    avg_complexity : float
    identifiable_entities : float
    duplication_count : float
    lines_duplicated : float

    def __init__(self, c : float, ie : float, dc : float, ld : float): 
        self.avg_complexity = c
        self.identifiable_entities = ie
        self.duplication_count = dc
        self.lines_duplicated = ld
        return
    
class DebtStatisticsForManyFiles(CustomJsonEncoderInterface):
    metrics    : dict[str, FileMetrics]             # dict of keys (filename) for values (FileMetrics)
    priorities : list[tuple[str, float]]            # list of tuple of (priority, filename)
    risks      : list[tuple[str, RiskLevelEnum]]    # dict of keys (filename) for values (RiskLevelEnum)
    maximums   : MetricStatistics
    averages   : MetricStatistics
    medians    : MetricStatistics
    
    def __init__(self): 
        self.metrics = {}
        self.priorities = []
        self.risks = {}
        self.maximums = MetricStatistics(0.0, 0.0, 0.0, 0.0)
        self.averages = MetricStatistics(0.0, 0.0, 0.0, 0.0)
        self.medians = MetricStatistics(0.0, 0.0, 0.0, 0.0)
    
    def encode(self):
        return CustomJsonEncoder.breakdown(self.__dict__)

class DebtStatisticsCalculator: 
    def get_maximums(self, file_metrics : list[FileMetrics]) -> MetricStatistics:
        maximums = MetricStatistics(0.0, 0.0, 0.0, 0.0)
        
        # trouver valeurs maximales
        for f in file_metrics:
            maximums.avg_complexity        = max(maximums.avg_complexity, f.avg_complexity)
            maximums.identifiable_entities = max(maximums.identifiable_entities, f.identifiable_entities)
            maximums.duplication_count     = max(maximums.duplication_count, f.duplication_count)
            maximums.lines_duplicated      = max(maximums.lines_duplicated, f.lines_duplicated)

        return maximums

    def get_averages(self, file_metrics : list[FileMetrics]) -> MetricStatistics: 
        average = MetricStatistics(0.0, 0.0, 0.0, 0.0)
        nb_of_files = len(file_metrics)
        
        if nb_of_files == 0:
            return average

        for f in file_metrics:
            average.avg_complexity        += f.avg_complexity
            average.identifiable_entities += f.identifiable_entities
            average.duplication_count     += f.duplication_count 
            average.lines_duplicated      += f.lines_duplicated

        average.avg_complexity        /= nb_of_files
        average.identifiable_entities /= nb_of_files
        average.duplication_count     /= nb_of_files
        average.lines_duplicated      /= nb_of_files

        return average

    def get_medians(self, file_metrics : list[FileMetrics]) -> MetricStatistics: 
        nb_of_files = len(file_metrics)
        
        if nb_of_files == 0:
            return MetricStatistics(0.0, 0.0, 0.0, 0.0)
        
        if nb_of_files == 1:
            f = file_metrics[0]
            return MetricStatistics(f.avg_complexity, f.identifiable_entities, f.duplication_count, f.lines_duplicated)
        
        medians = MetricStatistics(0.0, 0.0, 0.0, 0.0)
        avg_complexity_list = []
        identifiable_entities_list = []
        duplication_count_list = []
        lines_duplicated_list = []

        # on met en ordre les metriques pour trouver les valeurs centrales
        # https://www.alloprof.qc.ca/fr/eleves/bv/mathematiques/la-mediane-m1412 
        for f in file_metrics:
            avg_complexity_list.append(f.avg_complexity)
            identifiable_entities_list.append(f.identifiable_entities)
            duplication_count_list.append(f.duplication_count)
            lines_duplicated_list.append(f.lines_duplicated)

        avg_complexity_list.sort()
        identifiable_entities_list.sort()
        duplication_count_list.sort()
        lines_duplicated_list.sort()

        if nb_of_files % 2 == 0: 
            low_index = int(math.floor((nb_of_files + 1) / 2.0) - 1.0)
            high_index = int(math.ceil((nb_of_files + 1) / 2.0) - 1.0)

            medians.avg_complexity        = (avg_complexity_list[low_index] + avg_complexity_list[high_index]) / 2.0
            medians.identifiable_entities = (identifiable_entities_list[low_index] + identifiable_entities_list[high_index]) / 2.0
            medians.duplication_count     = (duplication_count_list[low_index] + duplication_count_list[high_index]) / 2.0
            medians.lines_duplicated      = (lines_duplicated_list[low_index] + lines_duplicated_list[high_index]) / 2.0
        else: 
            index = int(((nb_of_files + 1) / 2) - 1)

            medians.avg_complexity        = avg_complexity_list[index]
            medians.identifiable_entities = identifiable_entities_list[index]
            medians.duplication_count     = duplication_count_list[index]
            medians.lines_duplicated      = lines_duplicated_list[index]

        return medians
    
    def get_priority(self, f : FileMetrics, maximums : MetricStatistics) -> float:
        avg_complexity_ratio      = self.get_ratio(maximums.avg_complexity, f.avg_complexity)
        identifiable_entity_ratio = self.get_ratio(maximums.identifiable_entities, f.identifiable_entities)
        duplication_count_ratio   = self.get_ratio(maximums.duplication_count, f.duplication_count)
        lines_duplicated_ratio    = self.get_ratio(maximums.lines_duplicated, f.lines_duplicated)

        return (
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
        if max_val <= 0: return 0.0
        else:            return value / max_val

    def get_debt_statistics_for_many_files(self, file_metrics : list[FileMetrics]) -> DebtStatisticsForManyFiles: 
        maximums = self.get_maximums(file_metrics)
        averages = self.get_averages(file_metrics)
        medians = self.get_medians(file_metrics)
        metrics : dict[str, FileMetrics] = {}           # dict of keys (filename) for values (FileMetrics)
        priorities : list[tuple[str, float]] = []       # list of tuple of (priority, filename)
        risks : list[tuple[str, RiskLevelEnum]] = []    # dict of keys (filename) for values (RiskLevelEnum)

        for f in file_metrics: 
            score = self.get_priority(f, maximums)
            risk = self.get_risk_level(f.avg_complexity)

            priorities.append((f.file_name, score))
            risks.append((f.file_name, risk))
            metrics[f.file_name] = f

        priorities.sort(key=lambda item: item[1], reverse=True) 
        risks.sort(key=lambda item: item[1].value)
    
        result = DebtStatisticsForManyFiles()
        result.metrics = metrics
        result.risks = risks
        result.priorities = priorities
        result.maximums = maximums
        result.medians = medians
        result.averages = averages
        
        return result
