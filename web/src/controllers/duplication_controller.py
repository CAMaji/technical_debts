from src.models.model import Repository, Commit, File
from src.tools.pmd_copy_paste_detector import PMD_CopyPasteDetector
from src.tools.pmd_cpd_xml_reader import PMD_CPD_XmlReader
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.services.code_duplication_service import CodeDuplicationService
from src.utilities.json_encoder import JsonEncoder

import src.services.github_service as github_service
import json

def analyse_repo(repo : Repository, files : list[File]): 
    repo_dir = github_service.ensure_local_repo(repo.owner, repo.name) 

    #print(type(files).__name__) 
    #print(CustomJsonEncoder.breakdown(files)) 

    facade = CodeDuplicationDatabaseFacade()
    service = CodeDuplicationService(facade)
    parser = PMD_CPD_XmlReader(repo_dir)
    lang_list = [PMD_CopyPasteDetector.Language.PYTHON]       
    wrapper = PMD_CopyPasteDetector(20, lang_list, repo_dir)

    xml_list = wrapper.run()
    report_list = []

    for xml in xml_list:
        new_report_list = parser.read(xml)
        report_list.extend(new_report_list)
        continue

    service.insert_from_report(report_list, files)
    return 

#def get_metrics(commit : Commit, files):
#    facade = CodeDuplicationDatabaseFacade()
#    service = CodeDuplicationService(facade)
#
#    duplications = service.get_reports_for_many_files(files)
#    metrics = JsonEncoder.breakdown(duplications) 
#    
#    #print(json.dumps(metrics, indent=4)) 
#
#    return metrics