from utilities.custom_json_encoder import CustomJsonEncoder, CustomJsonEncoderInterface
from services.file_metrics_service import FileMetrics
from enum import Enum
from typing import TypeAlias
import heapq
import sys
import math

Filename_str : TypeAlias = str
Priority_float : TypeAlias = float

MaxAvgComplexity_float : TypeAlias = float
MaxIdentifiableEntity_float : TypeAlias = float
MaxDuplicationCount_float : TypeAlias = float
MaxLinesDupped_float : TypeAlias = float

AvgAvgComplexity_float : TypeAlias = float
AvgIdentifiableEntity_float : TypeAlias = float
AvgDuplicationCount_float : TypeAlias = float
AvgLinesDupped_float : TypeAlias = float

MedAvgComplexity_float : TypeAlias = float
MedIdentifiableEntity_float : TypeAlias = float
MedDuplicationCount_float : TypeAlias = float
MedLinesDupped_float : TypeAlias = float

class RiskLevelEnum(Enum):
    LOW_RISK = 0,
    MEDIUM_RISK = 1,
    HIGH_RISK = 2,
    VERY_HIGH_RISK = 3
    
class FilesDebtStatistics(CustomJsonEncoderInterface):
    stats    : dict[Filename_str, FileMetrics]
    priorities : list[tuple[Priority_float, Filename_str]]
    risks     : dict[Filename_str, RiskLevelEnum]
    maximums : tuple[MaxAvgComplexity_float, 
                     MaxIdentifiableEntity_float, 
                     MaxDuplicationCount_float, 
                     MaxLinesDupped_float]
    averages : tuple[AvgAvgComplexity_float, 
                     AvgIdentifiableEntity_float, 
                     AvgDuplicationCount_float, 
                     AvgLinesDupped_float]
    medians : tuple[MedAvgComplexity_float, 
                    MedIdentifiableEntity_float, 
                    MedDuplicationCount_float, 
                    MedLinesDupped_float]
    
    def __init__(self): 
        self.stats = {}
        self.priorities = []
        self.risks = {}
        self.maximums = ()
        self.averages = ()
        self.medians = ()
    
    def encode(self):
        return CustomJsonEncoder.breakdown(self.__dict__)

class StatisticsCalculator: 
    def get_maximums(self, file_metrics : list[FileMetrics]) -> tuple[MaxAvgComplexity_float, 
                                                                      MaxIdentifiableEntity_float, 
                                                                      MaxDuplicationCount_float, 
                                                                      MaxLinesDupped_float]:
        min_val = 0.0
        max_tuple = (min_val, min_val, min_val, min_val) 
        
        # trouver valeurs maximales
        for f in file_metrics:
            max_tuple[0] = max(max_tuple[0], f.avg_complexity)
            max_tuple[1] = max(max_tuple[0], f.identifiable_entities)
            max_tuple[2] = max(max_tuple[0], f.duplication_count)
            max_tuple[3] = max(max_tuple[0], f.lines_duplicated)

        return max_tuple

    def get_averages(self, file_metrics : list[FileMetrics]) -> tuple[AvgAvgComplexity_float, 
                                                                      AvgIdentifiableEntity_float, 
                                                                      AvgDuplicationCount_float, 
                                                                      AvgLinesDupped_float]: 
        avg_tuple = (0.0, 0.0, 0.0, 0.0)

        for f in file_metrics:
            avg_tuple[0] += f.avg_complexity
            avg_tuple[1] += f.identifiable_entities
            avg_tuple[2] += f.duplication_count
            avg_tuple[3] += f.lines_duplicated    

        nb_of_files = len(file_metrics)
        if(nb_of_files > 0):
            avg_tuple[0] /= nb_of_files
            avg_tuple[1] /= nb_of_files
            avg_tuple[2] /= nb_of_files
            avg_tuple[3] /= nb_of_files

        return avg_tuple

    def get_medians(self, file_metrics : list[FileMetrics]) -> tuple[MedAvgComplexity_float, 
                                                                     MedIdentifiableEntity_float, 
                                                                     MedDuplicationCount_float, 
                                                                     MedLinesDupped_float]: 
        med_tuple : tuple = (0.0, 0.0, 0.0, 0.0)

        nb_of_files = len(file_metrics)
        if(nb_of_files % 2 == 0 and nb_of_files >= 2):
            low_index = math.floor((nb_of_files + 1) / 2.0) - 1
            high_index = math.ceil((nb_of_files + 1) / 2.0) - 1
            
            med_tuple[0] = (file_metrics[low_index].avg_complexity + file_metrics[high_index].avg_complexity) / 2.0
            med_tuple[1] = (file_metrics[low_index].identifiable_entities + file_metrics[high_index].identifiable_entities) / 2.0
            med_tuple[2] = (file_metrics[low_index].duplication_count + file_metrics[high_index].duplication_count) / 2.0
            med_tuple[3] = (file_metrics[low_index].lines_duplicated + file_metrics[high_index].lines_duplicated) / 2.0
        else:
            index = ((nb_of_files + 1) / 2) - 1
            
            med_tuple[0] = (file_metrics[index].avg_complexity) / 2.0
            med_tuple[1] = (file_metrics[index].identifiable_entities) / 2.0
            med_tuple[2] = (file_metrics[index].duplication_count) / 2.0
            med_tuple[3] = (file_metrics[index].lines_duplicated) / 2.0

        return med_tuple

    def get_priority(self, avg_complexity_ratio : float, identifiable_entity_ratio : float, duplication_count_ratio : float, lines_duplicated_ratio : float) -> float:
        return 1.0 - (
            avg_complexity_ratio * 0.40 + 
            identifiable_entity_ratio * 0.30 + 
            duplication_count_ratio * 0.20 + 
            lines_duplicated_ratio + 0.10
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

    def get_statistics_for_many_files(self, file_metrics : list[FileMetrics]) -> FilesDebtStatistics: 
        maximums = self.get_maximums(file_metrics)
        averages = self.get_averages(file_metrics)
        medians = self.get_medians(file_metrics)
        stats : dict[Filename_str, FileMetrics] = {}
        priorities : list[(Priority_float, Filename_str)] = []
        risks : dict[Filename_str, RiskLevelEnum] = {}

        for f in file_metrics: 
            avg_complexity_ratio = 0.0
            identifiable_entity_ratio = 0.0
            duplication_count_ratio = 0.0 
            lines_duplicated_ratio = 0.0

            if(maximums[0] > 0):
                avg_complexity_ratio = f.avg_complexity / maximums[0]
            if(maximums[1] > 0): 
                identifiable_entity_ratio = f.identifiable_entities / maximums[1]
            if(maximums[2] > 0):
                duplication_count_ratio = f.duplication_count / maximums[2]
            if(maximums[3] > 0): 
                lines_duplicated_ratio = f.lines_duplicated / maximums[3]

            risks[f.file_name] = self.get_risk_level(f.avg_complexity)
            stats[f.file_name] = f
            score = self.get_priority(avg_complexity_ratio, identifiable_entity_ratio, duplication_count_ratio, lines_duplicated_ratio)
            heapq.heappush(priorities, (score, f.file_name))
        
        result = FilesDebtStatistics()
        result.stats = stats
        result.risks = risks
        result.priorities = priorities
        result.maximums = maximums
        result.medians = medians
        result.averages = averages
        
        return result
