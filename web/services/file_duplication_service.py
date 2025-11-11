import uuid
from app import db
from models.model import *
import services.file_service as file_service
import xml.etree.ElementTree as ElementTree # https://www.geeksforgeeks.org/python/xml-parsing-python/
import services.github_service as github_service
import services.duplication_service as duplication_service
import subprocess
import json

# Creates and commits a FileDuplication row.
def file_duplication_create(file_id, duplication_id, start_line, end_line): 
    file_duplication = FileDuplication(
        id = str(uuid.uuid4()),
        start_line=start_line,
        end_line=end_line,
        file_id = file_id,
        duplication_id = duplication_id
    )

    db.session.add(file_duplication)
    db.session.commit()

    return file_duplication 

# Obtains all file-duplication objects for a given file id
def file_duplication_get_from_file(file_id):
    return db.session.query(FileDuplication).filter_by(file_id=file_id).all()
        
# Obtains a JSON representation of a FileDuplication object
def file_duplication_to_json(file : File, file_duplications : list[FileDuplication]): 
    duplication_id_list = []
    for fd in file_duplications: 
        duplication_id_list.append(fd.duplication_id)

    return {
        "filename": file.name,
        "count": len(file_duplications),
        "duplication_ids": json.dumps(duplication_id_list)
    }

# Obtains a json object of duplications for each files in a commit
def file_duplication_get_json_from_commit(commit : Commit): 
    # retourne un JSON qui contient les champs suivants: 
    #
    # {
    #    "file_duplications": [
    #       {
    #           "filename": "filename.py",
    #           "count": 3,
    #           "duplication_ids": ["id1", ...]
    #       },
    #       ...
    #    ],
    #    "unique_duplication_ids" = ["id1", ...]
    # }
    #

    json_list = []
    files : list[File] = file_service.get_files_by_commit_id(commit.id)
    duplications : set = set()

    for f in files: 
        file_duplications : list[FileDuplication] = file_duplication_get_from_file(f.id)

        # On ajoute au set le ID de duplication
        # Le nombre de ID ajouté au set = le nombre
        # de duplications pour le commit sélectionné
        for fd in file_duplications: 
            duplications.add(fd.duplication_id)

        json_fd = file_duplication_to_json(f, file_duplications)
        json_list.append(json_fd)

    # copie le contenu du set vers une liste
    duplication_list : list = []
    for d in duplications:
        duplication_list.append(d)

    result = {
        "file_duplications": json.dumps(json_list),
        "unique_duplication_ids": json.dumps(duplication_list)
    }

    #print(result) 

    return result

def calculate_file_duplication_analysis(repo: Repository, commit : Commit): 
    class FileObject: 
        path : str
        start_line : int
        end_line : int

        def __init__(self):
            self.path = ""
            self.start_line = 0
            self.end_line = 0

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

    #github_service.fetch_files(repo.owner, repo.name, commit.sha)
    repo_path : str = github_service.repo_dir(repo.owner, repo.name)
    #print(repo_path)

    # https://pmd.github.io/pmd/pmd_userdocs_cpd_report_formats.html
    # Note: PMD-CDP supporte plusieurs langages, mais pour faire simple
    # et avoir une base, python est hard codé dans la ligne de commande.
    pmd_cmd : list[str] = ["./tools/pmd/bin/pmd", "cpd", "--minimum-tokens", "20", "--language", "python", "--format", "xml", "--dir", repo_path]
    completed_process : subprocess.CompletedProcess = subprocess.run(pmd_cmd, capture_output=True, text=True)
    xml_root : ElementTree.Element[str] = ElementTree.fromstring(completed_process.stdout)
    
    # Constantes. Le parser XML ajoute le lien ci-dessous aux tags du XML...
    # Je ne sais pas pourquoi.
    pmd_schema_link = "https://pmd-code.org/schema/cpd-report"
    pmd_duplication_tag = "{" + pmd_schema_link + "}duplication"
    pmd_file_tag = "{" + pmd_schema_link + "}file"
    pmd_codefragment_tag = "{" + pmd_schema_link + "}codefragment"

    for xml_node in xml_root:
        # tag <duplication>
        #print(xml_node.tag)
        if xml_node.tag == pmd_duplication_tag: 
            list_of_file : list[FileObject] = []

            for xml_sub_node in xml_node: 
                #print(xml_sub_node.tag)
                # tag <file> qui indique le fichier trouvé par PMD dans le 
                # dossier spécifié.
                if xml_sub_node.tag == pmd_file_tag : 
                    # Pour l'instant, on prend juste le path du 
                    # fichier trouvé. 
                    #
                    # Attributs disponibles: 
                    # - column
                    # - endcolumn
                    # - endline
                    # - endtoken
                    # - line
                    # - path


                    fo = FileObject()
                    fo.path = xml_sub_node.get("path")
                    fo.path = fo.path.removeprefix(repo_path + "/")
                    fo.start_line = xml_sub_node.get("line")
                    fo.end_line = xml_sub_node.get("endline")
                    list_of_file.append(fo)
                    
                # tag <codefragment> qui contient le texte dupliqué. Si aucune
                # duplication est trouvée, le XML retourné par PMD n'aura pas de 
                # <codefragment>. 
                elif xml_sub_node.tag == pmd_codefragment_tag:
                    instance_duplication : Duplication = duplication_service.duplication_create(xml_sub_node.text)
                    for fo in list_of_file:
                        file = file_service.get_file_by_filename_and_commit(fo.path, commit.id)
                        if not file:
                            file = file_service.create_file(fo.path, commit.id)
                        file_duplication_create(file.id, instance_duplication.id, fo.start_line, fo.end_line)
    return