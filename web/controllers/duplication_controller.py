import lizard
import os
import subprocess
import services.github_service
import xml.etree.ElementTree as ET # https://www.geeksforgeeks.org/python/xml-parsing-python/ 
from models import Repository

def duplication_analysis(repo: Repository): 
    # prérequis : 
    # 1. avoir cloné un repo localement
    # 2. avoir inséré les infos de fichiers dans la DB
    # 3. avoir sélectionné un commit/branche (checkout) sur lequel lancer l'analyse

    # todo : 
    # 1. lancer Lizard pour qu'il analyse les fichiers du commit 
    #    pour de la duplication de code. 
    # 2. lire le résultat donné par Lizard et insérer les données
    #    dans les objets modèles
    # 3. Inserer les objets modèles dans la DB

    repo_path : str = services.github_service.repo_dir(repo.owner, repo.name)
    print(repo_path)
    print('\n')
    pmd_cmd : list[str] = ["./pmd/bin/pmd", "cpd", "--minimum-tokens", "100", "--language", "python", "--format", "xml", "--dir", repo_path]
    # Note: 
    # Je ne sais pas si c'est comme ça dans tout les projets git, mais on a un 
    # dossier './web/.repo_cache' qui est une copie de notre projet. PMD va le 
    # détecter et dire que notre projet est quasiment à 100% dupliqué. 
    # Ajouter l'argument: "--exclude {repo_path}/.repo_cache" pour exclude la cache.
    #
    # https://pmd.github.io/pmd/pmd_userdocs_cpd_report_formats.html
    
    completed_process : subprocess.CompletedProcess = subprocess.run(pmd_cmd, capture_output=True, text=True)
    root : ET.Element[str] = ET.fromstring(completed_process.stdout)

    print(completed_process.stdout)
    print('\n')
    print(root.tag)
    
    return

def duplication_search(): 
    # prérequis: 
    # 1. avoir sélectionné un repo
    # 2. avoir sélectionné un commit de début et un commit de fin
    # 3. avoir activé l'option "duplication" 

    # todo : 
    # 1. pour chaque commit entre le début et la fin: 
    #   a. calculer le nombre total de duplication trouvé dans chaque fichier
    #   b. calculer le nombre total d'instances de duplications dans le commit
    # 2. calculer la moyenne de duplications pour la période donnée

    return

