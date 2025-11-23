from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.utilities.smart_list_iterator import SmartListIterator
from src.interface.tech_debt_report import TechDebtMetrics
from src.models.model import File
    
class FileMetricsService: 
    _facade : FileMetricsDatabaseFacade

    def __init__(self, facade : FileMetricsDatabaseFacade): 
        self._facade = facade
        return
    
    def get_tech_debt_metrics(self, file_list : list[File]) -> dict[str, TechDebtMetrics]: 
        complexities = self._facade.get_average_complexities(file_list)
        entities = self._facade.get_identifiable_entities_count(file_list)
        duplications = self._facade.get_duplications_metrics(file_list)

        metrics_dict = {}
        for file in file_list:
            metrics = TechDebtMetrics()

            if file.id in complexities:
                metrics.average_complexity = complexities[file.id]
            
            if file.id in entities:
                metrics.entities = entities[file.id]

            if file.id in duplications:
                metrics.duplications = duplications[file.id][0]
                metrics.duplicated_lines = duplications[file.id][1]
        
            metrics_dict[file.name] = metrics
        return metrics_dict
