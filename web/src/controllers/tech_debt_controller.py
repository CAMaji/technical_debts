from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.services.code_duplication_service import CodeDuplicationService
from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.services.recommendations_service import RecommendationsService
from src.services.file_metrics_service import FileMetricsService
from src.services.debt_stats_service import DebtStatsService
from src.reports.duplication_report import DuplicationReport
from src.reports.tech_debt_report import (FunctionDebtMetrics,
                                          FileDebtMetrics, 
                                          TechDebtReport)
from src.utilities.json_encoder import JsonEncoder
from src.models.model import File
from typing import TypeAlias

DuplicationReportDict : TypeAlias = dict[str, DuplicationReport]
FileDebtMetricsReportDict : TypeAlias = dict[str, FileDebtMetrics]
FuncDebtMetricsReportDict : TypeAlias = dict[str, list[FunctionDebtMetrics]]

def get_duplications_reports(files : list[File]) -> DuplicationReportDict:
    facade = CodeDuplicationDatabaseFacade()
    service = CodeDuplicationService(facade)
    report = service.get_reports_for_many_files(files)
    return report

def get_file_metrics_report(files : list[File]) -> FileDebtMetricsReportDict:
    facade = FileMetricsDatabaseFacade()
    service = FileMetricsService(facade)
    report = service.get_file_metrics(files)
    return report

def get_tech_debt_report(file_debt_metrics : dict[str, FileDebtMetrics]) -> TechDebtReport:
    service = DebtStatsService()
    report = service.get_debt_report(file_debt_metrics)
    return report

def get_file_function_metrics_report(files : list[File]) -> FuncDebtMetricsReportDict:
    facade = FileMetricsDatabaseFacade()
    service = FileMetricsService(facade)
    report = service.get_files_function_metrics(files)
    return report 

def get_recommendations_report(duplications : DuplicationReportDict, tech_debt : TechDebtReport, funcs : FuncDebtMetricsReportDict):
    service = RecommendationsService()
    report = service.get_report(tech_debt, duplications, funcs)
    return report
    
#import json
def get_reports(files : list[File]) -> dict[str, object]:
    d_reports = get_duplications_reports(files)
    fm_reports = get_file_metrics_report(files)
    td_report = get_tech_debt_report(fm_reports)
    ffm_report = get_file_function_metrics_report(files)
    r_report = get_recommendations_report(d_reports, td_report, ffm_report)

    #result = {
    #    "recommendations": JsonEncoder.breakdown(r_report),   # <---- fonctionnel, mais reste bug à répliquer, tester, et corriger.
    #    "duplications": JsonEncoder.breakdown(d_reports),
    #    "tech_debt": JsonEncoder.breakdown(td_report)
    #}

    #print(json.dumps(result["recommendations"], indent=4))

    result = JsonEncoder.breakdown(d_reports)
    return result
