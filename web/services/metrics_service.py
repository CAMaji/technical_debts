from models import db
from models.model import *

from lizard import analyze_file
import services.function_service as function_service
import services.complexity_service as complexity_service
import services.identifiable_entity_service as identifiable_entity_service
import services.github_service as github_service
import services.file_service as file_service
import xml.etree.ElementTree as ElementTree # https://www.geeksforgeeks.org/python/xml-parsing-python/
import services.file_duplication_service as file_duplication_service
import services.duplication_service as duplication_service
import subprocess


def calculate_cyclomatic_complexity_analysis(file, code):
    cyclomatic_complexity_analysis = []
    analysis = analyze_file.analyze_source_code(file.name, code)
    for func in analysis.function_list:
        # ensure function record exists
        function = function_service.get_function_by_name_and_file(func.name, file.id)
        if not function:
            function = function_service.create_function(func.name, func.start_line, file.id)

        # update or create complexity
        existing_complexity = Complexity.query.filter_by(function_id=function.id).first()

        if existing_complexity:
            existing_complexity.value = func.cyclomatic_complexity
            db.session.commit()
        else:
            complexity_service.create_complexity(func.cyclomatic_complexity, function.id)

        cyclomatic_complexity_analysis.append({
            "file": file.name,
            "function": func.name,
            "start_line": func.start_line,
            "cyclomatic_complexity": func.cyclomatic_complexity
        })

    return cyclomatic_complexity_analysis


def calculate_identifiable_identities_analysis(file, code):
    identifiable_entity_analysis = []

    # get all the identifiable identities to search for
    identities = identifiable_entity_service.get_all_identifiable_identities()
    for identity in identities:
        # search the file for the identity (e.g. <TODO>, <FIXME>)
        found_identities = identifiable_entity_service.search_identifable_identity(code, identity.name)

        # link the found identity to the file it was found in
        for line in found_identities:
            identifiable_entity_service.create_file_entity(identity.id, file.id, line)

            identifiable_entity_analysis.append({
                "file": file.name,
                "start_line": line,
                "entity_name": identity.name,
            })

    return identifiable_entity_analysis


# mettre dans metric services
def calculate_duplication_analysis(repo: Repository, branch : Branch, commit : Commit): 
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

    github_service.fetch_files(repo.owner, repo.name, branch.name, commit.sha)
    repo_path : str = github_service.repo_dir(repo.owner, repo.name)

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
        if xml_node.tag == pmd_duplication_tag: 
            list_of_file : list[File] = []

            for xml_sub_node in xml_node: 
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

                    filename = xml_sub_node.get("path")
                    file : File = file_service.get_file_by_filename_and_commit(filename, commit.id)
                    if not file: 
                        file = file_service.create_file(filename, commit.id)
                    list_of_file.append(file)
                
                # tag <codefragment> qui contient le texte dupliqué. Si aucune
                # duplication est trouvée, le XML retourné par PMD n'aura pas de 
                # <codefragment>. 
                elif xml_sub_node.tag == pmd_codefragment_tag:
                    instance_duplication : Duplication = duplication_service.duplication_create(xml_sub_node.text)
                    for file in list_of_file:
                        file_duplication_service.file_duplication_create(file.id, instance_duplication.id)
    return