import lizard
import os
import services.github_service
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

    repo_path : str = services.github_service.repo_dir(repo.name, repo.name)
    lizard.analyze_files()


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
