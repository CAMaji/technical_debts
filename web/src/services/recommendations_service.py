from src.reports.recommendation_report import (RecommendationReport,
                                               RecommendationEnum,
                                               ProblemEnum)
from src.reports.tech_debt_report import (FunctionDebtMetrics,
                                          FileDebtMetrics,
                                          TechDebtReport,
                                          RiskEnum)
from src.reports.duplication_report import DuplicationReport
from src.utilities.pair import Pair

class RecommendationsService:
    
    def get_no_problem(self) -> Pair[str, str]:
        return Pair[str, str](ProblemEnum.NO_PROBLEM.value, "")
    
    def get_global_risk(self, median_metrics : FileDebtMetrics) -> Pair[str, str]:
        global_risk : RiskEnum = RiskEnum.get_risk(median_metrics.average_complexity)

        if global_risk.value < RiskEnum.MEDIUM_RISK.value:
            return self.get_no_problem()

        problem = ProblemEnum.GLOBAL_RISK_PROBLEM.value
        recomm = RecommendationEnum.GLOBAL_RISK_RECOMMENDATION.value
        problem = problem.replace("@1", global_risk.name)
        return Pair[str, str](problem, recomm)
    
    def get_global_duplication(self, dup_reports : dict[str, DuplicationReport]) -> Pair[str, str]:
        MINIMUM_DUPLICATION_COUNT = 5
        nb_bad_duplications = 0
    
        for frag_id in dup_reports:
            report = dup_reports[frag_id]
            file_nb = report.get_file_nb()
            if(file_nb >= MINIMUM_DUPLICATION_COUNT): 
                nb_bad_duplications += 1
        
        if nb_bad_duplications == 0:
            return self.get_no_problem()
        
        problem = ProblemEnum.GLOBAL_DUPLICATION_PROBLEM.value
        recomm = RecommendationEnum.GLOBAL_DUPLICATION_RECOMMENDATION.value
        problem = problem.replace("@1", str(nb_bad_duplications))
        problem = problem.replace("@2", str(MINIMUM_DUPLICATION_COUNT))
        return Pair[str, str](problem, recomm)
        
    def get_file_avg_risk(self, filename : str, risk : RiskEnum) -> Pair[str, str]:
        if risk.value < RiskEnum.MEDIUM_RISK.value:
            return self.get_no_problem()
        
        problem = ProblemEnum.FILE_AVG_RISK_PROBLEM.value
        recomm = RecommendationEnum.FILE_RISK_RECOMMENDATION.value
        problem = problem.replace("@1", filename)
        problem = problem.replace("@2", risk.name)
        return Pair[str, str](problem, recomm)
        
    def get_file_func_risk(self, filename : str, func_name : str, complexity : float) -> Pair[str, str]:
        risk : RiskEnum = RiskEnum.get_risk(complexity)

        if risk.value < RiskEnum.MEDIUM_RISK.value: 
            return self.get_no_problem()
        
        problem = ProblemEnum.FILE_FUNC_RISK_PROBLEM.value
        recomm = RecommendationEnum.FILE_RISK_RECOMMENDATION.value
        problem = problem.replace("@1", filename)
        problem = problem.replace("@2", func_name)
        problem = problem.replace("@3", risk.name)
        return Pair[str, str](problem, recomm)

    def get_file_func_nb(self, filename : str, func_nb : int) -> Pair[str, str]:
        MINIMUM_FUNC_NUMBER = 30

        if func_nb < MINIMUM_FUNC_NUMBER:
            return self.get_no_problem()
        
        problem = ProblemEnum.FILE_FUNC_NUMBER_PROBLEM.value
        recomm = RecommendationEnum.FILE_FUNC_NUMBER_RECOMMENDATION.value
        problem = problem.replace("@1", filename)
        problem = problem.replace("@2", str(func_nb))
        return Pair[str, str](problem, recomm)

    def get_bug_to_func(self, filename : str, func_nb : int, todofixme_nb : int) -> Pair[str, str]: 
        MINIMUM_BUG_TO_FUNC_RATIO = 0.5
        
        if todofixme_nb == 0:
            return self.get_no_problem()
        
        ratio = float(todofixme_nb) / float(func_nb)
        if(ratio < MINIMUM_BUG_TO_FUNC_RATIO):
            return self.get_no_problem()
        
        problem = ProblemEnum.FILE_BUG_TO_FUNCTION_PROBLEM.value
        recomm = RecommendationEnum.FILE_BUG_TO_FUNCTION_RECOMMENDATION.value
        problem = problem.replace("@1", filename)
        problem = problem.replace("@2", str(func_nb))
        problem = problem.replace("@3", str(todofixme_nb))
        return Pair[str, str](problem, recomm)

    def get_global_subreport_elements(self, tech_debt : TechDebtReport, duplications : dict[str, DuplicationReport]) -> list[Pair[str, str]]: 
        global_risk = self.get_global_risk(tech_debt.get_medians())
        global_dupl = self.get_global_duplication(duplications)
        return [global_risk, global_dupl]
    
    def get_file_subreport_elements(self, file_debt : TechDebtReport.File, func_nb : int) -> list[Pair[str, str]]:
        file_avg_risk = self.get_file_avg_risk(file_debt.filename, file_debt.risk)
        file_func_nb = self.get_file_func_nb(file_debt.filename, func_nb)
        bug_to_func = self.get_bug_to_func(file_debt.filename, func_nb, file_debt.metrics.entities)
        return [file_avg_risk, file_func_nb, bug_to_func]

    def get_file_func_subreport_elements(self, func_metrics_list : list[FunctionDebtMetrics]) -> list[Pair[str, str]]:
        element_list : list[Pair[str, str]] = [] 

        for func_metrics in func_metrics_list:
            file_func_risk = self.get_file_func_risk(func_metrics.filename, func_metrics.funcname, func_metrics.complexity)
            element_list.append(file_func_risk)

        return element_list

    def get_report(self, tech_debt : TechDebtReport, duplications : dict[str, DuplicationReport], funcs : dict[str, list[FunctionDebtMetrics]]) -> RecommendationReport:
        global_subreport = RecommendationReport.Summary("")
        global_elements = self.get_global_subreport_elements(tech_debt, duplications)
        global_subreport.add_list(global_elements)
        report = RecommendationReport(global_subreport)

        
        for element in tech_debt:
            func_metrics = funcs[element.filename]
            file_subreport = RecommendationReport.Summary(element.filename)
            file_elements = self.get_file_subreport_elements(element, len(func_metrics))
            file_func_elements = self.get_file_func_subreport_elements(func_metrics)
            file_subreport.add_list(file_elements)
            file_subreport.add_list(file_func_elements)
            report.add_file(file_subreport)

        return report

        