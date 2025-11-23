from src.interface.tech_debt_report import TechDebtReport, TechDebtMetrics, RiskEnum
from src.utilities.smart_dict_iterator import SmartDictIterator
from collections.abc import Iterable
from dataclasses import fields
from typing import Callable
from enum import Enum
import statistics
import math

class DebtStatsService: 
    WEIGHT = TechDebtMetrics(0.40, 0.30, 0.20, 0.10)
    FUNCS = (max, statistics.mean, statistics.median)

    class StatsEnum(Enum):
        MAXIMUMS = 0
        AVERAGES = 1
        MEDIANS = 2

    def get_statistics(self, which_stat : StatsEnum, file_list : dict[str, TechDebtMetrics]) -> TechDebtMetrics:
        func = DebtStatsService.FUNCS[which_stat.value]
        result = TechDebtMetrics()

        for i in range(0, result.length()):
            iterator = SmartDictIterator(file_list, lambda file : float(file[1].get(i)))
            result.set(i, func(iterator))

        return result
    
    def get_priority(self, ratios : TechDebtMetrics) -> float:
        score : float = 0.0

        for i in range(0, ratios.length()):
            score += ratios.get(i) * DebtStatsService.WEIGHT.get(i)
        
        return score
    
    def get_ratios(self, metrics : TechDebtMetrics, maximums : TechDebtMetrics) -> TechDebtMetrics:
        result = TechDebtMetrics()

        for i in range(0, result.length()):
            if maximums.get(i) > 0.0:
                result.set(i, metrics.get(i) / maximums.get(i))
        
        return result
    
    def get_risk(self, complexity : float) -> RiskEnum:
        return RiskEnum.get_risk(complexity)

    def get_debt_report(self, file_list : dict[str, TechDebtMetrics]) -> TechDebtReport: 
        maximums = self.get_statistics(DebtStatsService.StatsEnum.MAXIMUMS, file_list)
        averages = self.get_statistics(DebtStatsService.StatsEnum.AVERAGES, file_list)
        medians  = self.get_statistics(DebtStatsService.StatsEnum.MEDIANS, file_list)

        report = TechDebtReport(maximums, averages, medians)

        for filename in file_list:
            metrics = file_list[filename]
            ratios = self.get_ratios(metrics, maximums)
            priority = self.get_priority(ratios)
            risk = self.get_risk(metrics.average_complexity)
            file = TechDebtReport.File(filename, priority, risk, metrics)
            
            report.add_file(file)
        
        return report
    