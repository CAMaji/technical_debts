from src.reports.tech_debt_report import TechDebtReport, FileDebtMetrics, RiskEnum
from src.utilities.smart_dict_iterator import SmartDictIterator
from enum import Enum
import statistics

class DebtStatsService: 
    class StatsEnum(Enum):
        MAXIMUMS = 0
        AVERAGES = 1
        MEDIANS = 2

    # constants
    WEIGHT = FileDebtMetrics(0.40, 0.30, 0.20, 0.10)
    FUNCS = (max, statistics.mean, statistics.median)

    def get_statistics(self, which_stat : StatsEnum, file_list : dict[str, FileDebtMetrics]) -> FileDebtMetrics:
        func = DebtStatsService.FUNCS[which_stat.value]
        result = FileDebtMetrics()

        for i in range(0, result.length()):
            iterator = SmartDictIterator(file_list, lambda file : float(file[1].get(i)))
            result.set(i, func(iterator))

        return result
    
    def get_priority(self, ratios : FileDebtMetrics) -> float:
        score : float = 0.0

        for i in range(0, ratios.length()):
            score += ratios.get(i) * DebtStatsService.WEIGHT.get(i)
        
        return score
    
    def get_ratios(self, metrics : FileDebtMetrics, maximums : FileDebtMetrics) -> FileDebtMetrics:
        result = FileDebtMetrics()

        for i in range(0, result.length()):
            if maximums.get(i) > 0.0:
                result.set(i, metrics.get(i) / maximums.get(i))
        
        return result
    
    def get_risk(self, complexity : float) -> RiskEnum:
        return RiskEnum.get_risk(complexity)

    def get_debt_report(self, file_list : dict[str, FileDebtMetrics]) -> TechDebtReport: 
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
        
        DebtStatsService._last_generated_report = report
        return report
    
    