from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.utilities.smart_list_iterator import SmartListIterator
from src.reports.tech_debt_report import FileDebtMetrics, FunctionDebtMetrics
from src.models.model import File
    
class FileMetricsService: 
    _facade : FileMetricsDatabaseFacade

    def __init__(self, facade : FileMetricsDatabaseFacade): 
        self._facade = facade
        return
    
    def get_file_metrics(self, file_list : list[File]) -> dict[str, FileDebtMetrics]: 
        complexities = self._facade.get_average_complexities(file_list)
        entities = self._facade.get_identifiable_entities_count(file_list)
        duplications = self._facade.get_duplications_metrics(file_list)

        metrics_dict = {}
        for file in file_list:
            metrics = FileDebtMetrics()

            if file.id in complexities:
                metrics.average_complexity = complexities[file.id]
            
            if file.id in entities:
                metrics.entities = entities[file.id]

            if file.id in duplications:
                metrics.duplications = duplications[file.id][0]
                metrics.duplicated_lines = duplications[file.id][1]

            metrics_dict[file.name] = metrics
        return metrics_dict
    
    def get_files_function_metrics(self, file_list : list[File]) -> dict[str, list[FunctionDebtMetrics]]: 
        functions = self._facade.get_functions_complexity(file_list)

        metrics_dict : dict[str, list[FunctionDebtMetrics]] = {}
        for file in file_list:
            if file.name not in metrics_dict:
                metrics_dict[file.name] = []

            if file.id in functions:
                for func_metrics in functions[file.id]:
                    metrics = FunctionDebtMetrics()
                    metrics.filename = file.name
                    metrics.funcname = func_metrics[0]
                    metrics.complexity = func_metrics[1]
                    metrics_dict[file.name].append(metrics)
        
        return metrics_dict