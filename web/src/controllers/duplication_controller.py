from src.models.model import Repository, Commit
from src.tools.pmd_cpd_wrapper import PmdCpdWrapper
from src.utilities.pmd_cpd_xml_parser import PmdCdpXmlParser
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.database.file_metrics_db_facade import FileMetricsDatabaseFacade
from src.services.code_duplication_service import CodeDuplicationService
from src.services.file_metrics_service import FileMetricsService
from src.utilities.custom_json_encoder import CustomJsonEncoder

import src.services.github_service as github_service
import src.services.file_service as file_service
import json

def analyse_repo(repo : Repository, commit : Commit): 
    files = file_service.get_files_by_commit_id(commit.id)
    repo_dir = github_service.ensure_local_repo(repo.owner, repo.name)

    facade = CodeDuplicationDatabaseFacade()
    service = CodeDuplicationService(facade)

    wrapper = PmdCpdWrapper(20, PmdCpdWrapper.Language.PYTHON, PmdCpdWrapper.ReportFormat.XML, repo_dir)
    parser = PmdCdpXmlParser(repo_dir)

    xml = wrapper.run()
    parser.parse(xml)
    reports = parser.get_reports()

    service.insert_elements_from_parsed_xml(reports, files)
    return 


def get_metrics(commit : Commit, files): 
    facade = CodeDuplicationDatabaseFacade()
    service = CodeDuplicationService(facade)

    duplications = service.get_fragments_for_many_files(files)
    metrics = CustomJsonEncoder.breakdown(duplications) 
    print(json.dumps(metrics, indent=4)) 

    return metrics