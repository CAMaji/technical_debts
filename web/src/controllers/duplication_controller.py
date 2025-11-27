from src.models.model import Repository, File
from src.tools.pmd_copy_paste_detector import PMD_CopyPasteDetector
from src.database.code_duplication_db_facade import CodeDuplicationDatabaseFacade
from src.services.code_duplication_service import CodeDuplicationService

import src.services.github_service as github_service

def analyse_repo(repo : Repository, files : list[File]): 
    repo_dir = github_service.ensure_local_repo(repo.owner, repo.name) 
    
    # --temporaire--
    # pour trouver les langages utilisés dans le projet
    file_extensions = set()
    for f in files: 
        filename = str(f.name)
        tokens = filename.split(".")
        token_nb = len(tokens)
        if token_nb == 0:
            continue
        
        extension = "." + tokens[token_nb - 1]
        file_extensions.add(extension)
        continue

    facade = CodeDuplicationDatabaseFacade()
    service = CodeDuplicationService(facade)
    wrapper = PMD_CopyPasteDetector()
    
    report_list = wrapper.run(repo_dir, file_extensions)
    service.insert_from_report(report_list, files)
    return 