from src.reports.function_complexity_report import FunctionComplexityReport
from src.reports.file_complexity_report import FileComplexityReport
from src.reports.recommendation_generator import RecommendationGenerator
from src.reports.entity_report import EntityReport
from src.reports.recommendation_report import *
from src.reports.duplication_report import *
from src.models.model import File

class RecommendationService:
    _generator : RecommendationGenerator

    def __init__(self, generator : RecommendationGenerator):
        self._generator = generator
        return

    def get_global_summary(self, 
                           total_file_nb : int,
                           complexity    : dict[str, FileComplexityReport], 
                           entity        : dict[str, list[EntityReport]], 
                           duplication   : dict[str, DuplicationReport]) -> RecommendationReport.Summary:
        summary = RecommendationReport.Summary("All")
        summary.add(self._generator._global_risk(complexity))
        summary.add(self._generator._global_duplication(duplication))
        summary.add(self._generator._global_bug(entity, total_file_nb))
        return summary
    
    def get_file_complexity_summary(self,  
                                    summary : RecommendationReport.Summary, 
                                    complexity : FileComplexityReport) -> RecommendationReport.Summary:
        summary.add(self._generator._file_avg_risk(complexity))
        summary.add(self._generator._file_func_nb(complexity))

        for function_complexity in complexity.functions:
            summary.add(self._generator._file_func_risk(function_complexity))
            continue
 
        return summary
     
    def get_file_summary(self, 
                         filename    : str, 
                         complexity  : dict[str, FileComplexityReport],
                         entity      : dict[str, list[EntityReport]],
                         duplication : dict[str, DuplicationReport]) -> RecommendationReport.Summary:
        summary = RecommendationReport.Summary(filename)
        if filename in complexity:
            summary = self.get_file_complexity_summary(summary, complexity[filename])
            
        #if filename in entity:
            #...

        #if filename in duplication:
            #...

        return summary
    
    def get_recommendations(self, 
                            file_list   : list[File],
                            complexity  : dict[str, FileComplexityReport], 
                            entity      : dict[str, list[EntityReport]], 
                            duplication : dict[str, DuplicationReport]) -> RecommendationReport:
        total_file_nb = len(file_list)
        global_summary = self.get_global_summary(total_file_nb, complexity, entity, duplication)
        file_summaries = list[RecommendationReport.Summary]()

        for file in file_list:
            summary = self.get_file_summary(file.name, complexity, entity, duplication)
            file_summaries.append(summary)
            continue
        
        report = RecommendationReport(global_summary, file_summaries)
        return report
