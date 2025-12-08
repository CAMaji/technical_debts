from flask import request, jsonify

from src.app import app, db
from src.models.model import *
import src.services.github_service as github_service
import src.services.repository_service as repository_service
import src.services.commit_service as commit_service
import src.services.file_service as file_service
import src.services.complexity_service as complexity_service
import src.services.identifiable_entity_service as identifiable_entity_service
import src.services.metrics_service as metrics_service
import src.services.branch_service as branch_service
from src.services.code_duplication_service import *
from src.database.code_duplication_db_facade import *
from src.services.metrics_service import * 
import time
import json

from src.controllers.recommendation_controller import RecommendationController
from src.controllers.duplication_controller import DuplicationController
from src.utilities.json_encoder import JsonEncoder

def save_commit_and_analyse(repo : Repository, commit : Commit) -> list[File]: 
    files = file_service.get_files_by_commit_id(commit.id)
    
    if len(files) == 0: 
        # we need to get the files
        remote_files = github_service.fetch_files(repo.owner, repo.name, commit.sha)

        # store the files in db 
        for filename, code in remote_files:
            file = file_service.create_file(filename, commit.id)

            # calculate the various metrics here
            metrics_service.calculate_cyclomatic_complexity_analysis(file, code)
            metrics_service.calculate_identifiable_identities_analysis(file, code)
    
        files = file_service.get_files_by_commit_id(commit.id)
        dir = github_service.ensure_local_repo(repo.owner, repo.name)
        
        # duplications 
        duplication_controller : DuplicationController = DuplicationController.singleton()
        duplication_controller.find_duplications("pmd_cpd", dir, files) 

    return files

def get_complexity(files : list[File]) -> list:
    cyclomatic_complexity_analysis = []
    for file in files:
        cyclomatic_complexity_analysis.append(complexity_service.get_complexity_by_file_id_verbose(file.id))
    return cyclomatic_complexity_analysis

def get_todofixme(files : list[File]) -> list:
    todofixme_analysis = []
    for file in files:
        entities = identifiable_entity_service.get_identifiable_entity_by_file_id_verbose(file.id)
        for entity in entities:
            todofixme_analysis.append(entity) 
    return todofixme_analysis

def get_duplications(files : list[File]) -> dict[str, DuplicationReport]:
    controller : DuplicationController = DuplicationController.singleton()
    return controller.get_report_dict(files)

def get_recommendations(files : list[File], complexity : list, todofixme : list, duplication : dict[str, DuplicationReport]):
    controller : RecommendationController = RecommendationController.singleton()
    return controller.get_recommendations(files, complexity, todofixme, duplication)
    

@app.route('/api/display_metrics_by_commit_id', methods=['POST'])
def display_metrics_by_commit_id():
    data = request.get_json()
    repository_id = data.get('repository_id')
    branch_id = data.get('branch_id')
    commit_id = data.get('commit_id')
    include_complexity = data.get('include_complexity')
    include_identifiable_identities = data.get('include_identifiable_identities')
    include_code_duplication = data.get('include_code_duplication')
    commit = commit_service.get_commit_by_commit_id(commit_id)
    repo = repository_service.get_repository_by_repository_id(repository_id)
    files = save_commit_and_analyse(repo, commit)
    
    metrics = {
        "commit_sha": commit.sha,
        "commit_date": commit.date,
        "commit_message": commit.message,
        "cyclomatic_complexity_analysis": [],
        "identifiable_identities_analysis": [],
        "duplicated_code_analysis": {},
    }

    cyclomatic_complexity_analysis = get_complexity(files)
    identifiable_identities_analysis = get_todofixme(files)
    duplication_analysis = get_duplications(files)
    recommendation_analysis = get_recommendations(files, cyclomatic_complexity_analysis, identifiable_identities_analysis, duplication_analysis)

    # add the metrics analysis only if requested 
    if include_complexity:
        
        metrics["cyclomatic_complexity_analysis"] = cyclomatic_complexity_analysis

    if include_identifiable_identities:
        metrics["identifiable_identities_analysis"] = identifiable_identities_analysis
    
    metrics["duplicated_code_analysis"]["recommendations"] = JsonEncoder.breakdown(recommendation_analysis) 
    if include_code_duplication: 
        metrics["duplicated_code_analysis"]["duplications"] = JsonEncoder.breakdown(duplication_analysis)
    else: 
        metrics["duplicated_code_analysis"]["duplications"] = {} 

    return jsonify(metrics)


@app.route('/api/display_debt_evolution', methods=['POST'])
def display_debt_evolution():
    data = request.get_json()

    return
