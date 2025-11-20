from src.models.model import *
from src.models.file_metrics import FileMetrics
from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.database.file_metrics_db_facade import FuncName_str, Complexity_int, LinesDuppedCount_int
from src.utilities.smart_list_iterator import SmartListIterator
from typing import TypeAlias

DuplicationCount_int : TypeAlias = int
    
class FileMetricsService: 
    _facade : FileMetricsDatabaseFacade

    def __init__(self, facade : FileMetricsDatabaseFacade): 
        self._facade = facade
        return

    def get_function_complexities_for_one_file(self, file_id : str) -> dict[FuncName_str, Complexity_int]:
        return self._facade.get_function_complexities_for_one_file(file_id)

    def count_identifiable_identities_for_one_file(self, file_id : str) -> int:
        return self._facade.count_identifiable_entities_for_one_file(file_id)

    def get_complexity_average_for_one_file(self, file_id : str) -> float:
        function_complexities = self.get_function_complexities_for_one_file(file_id)
        count = len(function_complexities)
        
        if count == 0: # prevents a divison by zero exception
            return 0

        sum : float = 0.0
        for k in function_complexities: 
            sum += function_complexities[k]

        return sum / count
        
    def get_code_duplications_for_one_file(self, file_id : str) -> tuple[DuplicationCount_int, LinesDuppedCount_int]:
        code_duplications = self._facade.get_code_duplications_for_one_file(file_id)
        duplication_count : int = len(code_duplications)
        lines_duplicated : int = 0

        for cd in code_duplications:
            lines_duplicated += cd[0]

        return (duplication_count, lines_duplicated)

    def get_metrics_for_one_file(self, file_id : str, file_name : str) -> FileMetrics:
        complexity_avg = self.get_complexity_average_for_one_file(file_id)
        identifiable_entities_count = self.count_identifiable_identities_for_one_file(file_id)
        duplication_metrics = self.get_code_duplications_for_one_file(file_id)

        return FileMetrics(
            file_id,
            file_name,
            complexity_avg,
            #{"0":complexity_avg},  
            identifiable_entities_count, 
            duplication_metrics[0], 
            duplication_metrics[1]
        )
    
    def get_metrics_for_many_files(self, file_list : list[File]) -> list[FileMetrics]: 
        result : list[FileMetrics] = []
        for f in file_list:
            metrics = self.get_metrics_for_one_file(f.id, f.name)
            result.append(metrics)
        return result
