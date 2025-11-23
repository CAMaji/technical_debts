from src.models.model import File
from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.services.file_metrics_service import FileMetricsService
from src.services.debt_stats_service import DebtStatsService
from src.utilities.json_encoder import JsonEncoder

def get_metrics(files : list[File]): 
    assert type(files) == list
    assert len(files) > 0
    assert type(files[0]) == File

    facade = FileMetricsDatabaseFacade()
    file_metric_service = FileMetricsService(facade)
    debt_stats_service = DebtStatsService()

    metric_report = file_metric_service.get_tech_debt_metrics(files)
    tech_dept_report = debt_stats_service.get_debt_report(metric_report)

    json_dumpable_report = JsonEncoder.breakdown(tech_dept_report)
    return json_dumpable_report
