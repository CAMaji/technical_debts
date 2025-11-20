from src.models.model import Repository, Commit
from src.tools.pmd_cpd_wrapper import PmdCpdWrapper
from src.utilities.pmd_cpd_xml_parser import PmdCdpXmlParser
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.services.code_duplication_service import CodeDuplicationService
from src.services.file_metrics_service import FileMetricsService
from src.utilities.custom_json_encoder import CustomJsonEncoder
from src.utilities.debt_statistics_calculator import DebtStatisticsCalculator, DebtStatisticsForManyFiles

import src.services.github_service as github_service
import src.services.file_service as file_service
import json

def get_metrics(commit : Commit, files): 
    facade = FileMetricsDatabaseFacade()
    service = FileMetricsService(facade)
    calculator = DebtStatisticsCalculator()

    file_metrics = service.get_metrics_for_many_files(files)
    debt = calculator.get_debt_statistics_for_many_files(file_metrics)

    metrics = CustomJsonEncoder.breakdown(debt) 
    #print(json.dumps(metrics, indent=4))

    return metrics