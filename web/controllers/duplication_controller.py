import lizard
import os
import subprocess
import services.github_service as SGS
import services.file_service as SFS
import services.duplication_service as SDS
import services.file_duplication_service as SFDS
import xml.etree.ElementTree as ET # https://www.geeksforgeeks.org/python/xml-parsing-python/ 
from models import Repository
from models import Branch
from models import File
from models import FileDuplication
from models import Duplication
from models import Commit

def duplication_analysis(repo: Repository, branch : Branch, commit : Commit): 
    # prérequis : 
    # 1. avoir cloné un repo localement
    # 2. avoir inséré les infos de fichiers dans la DB
    # 3. avoir sélectionné un commit/branche (checkout) sur lequel lancer l'analyse

    # todo : 
    # 1. lancer PMD pour qu'il analyse les fichiers du commit 
    #    pour de la duplication de code. 
    # 2. lire le résultat donné par PMD et insérer les données
    #    dans les objets modèles
    # 3. Inserer les objets modèles dans la DB

    SGS.fetch_files(repo.owner, repo.name, branch.name, commit.sha)
    repo_path : str = SGS.repo_dir(repo.owner, repo.name)
    pmd_cmd : list[str] = ["./pmd/bin/pmd", "cpd", "--minimum-tokens", "20", "--language", "python", "--format", "xml", "--dir", repo_path]
    # https://pmd.github.io/pmd/pmd_userdocs_cpd_report_formats.html
    
    completed_process : subprocess.CompletedProcess = subprocess.run(pmd_cmd, capture_output=True, text=True)
    xml_root : ET.Element[str] = ET.fromstring(completed_process.stdout)
    print(xml_root.items(), end='\n')
    pmd_schema_link = "https://pmd-code.org/schema/cpd-report"
    pmd_duplication_tag = "{" + pmd_schema_link + "}duplication"
    pmd_file_tag = "{" + pmd_schema_link + "}file"
    pmd_codefragment_tag = "{" + pmd_schema_link + "}codefragment"

    print(pmd_duplication_tag, end='\n')
    print(pmd_file_tag, end='\n')
    print(pmd_codefragment_tag, end='\n')

    for xml_node in xml_root:
        print(xml_node.tag, end='\n')

        if xml_node.tag == pmd_duplication_tag: 
            list_of_file : list[File] = []

            for xml_sub_node in xml_node: 
                if xml_sub_node.tag == pmd_file_tag : 
                    # attributs disponibles: 
                    # - column
                    # - endcolumn
                    # - endline
                    # - endtoken
                    # - line
                    # - path

                    filename = xml_sub_node.get("path")
                    file : File = SFS.get_file_by_filename_and_commit(filename, commit.id)
                    if not file: 
                        file = SFS.create_file(filename, commit.id)

                    #print(file)
                    list_of_file.append(file)
                
                elif xml_sub_node.tag == pmd_codefragment_tag:
                    #print(xml_sub_node.text, end = '\n')
                    instance_duplication : Duplication = SDS.duplication_create(xml_sub_node.text)
                    #print(instance_duplication)
                    #list_of_fileDuplication : list[FileDuplication] = []
                    for file in list_of_file: 
                        #print(file)
                        #file_duplication : FileDuplication = SFDS.file_duplication_create(file.id, instance_duplication.id)
                        #print(file_duplication)
                        #list_of_fileDuplication.append(file_duplication)
                        SFDS.file_duplication_create(file.id, instance_duplication.id)
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

