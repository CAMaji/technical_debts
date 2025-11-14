from flask import request, jsonify

from app import app, db
from models.model import *
import services.github_service as github_service
import services.repository_service as repository_service
import services.commit_service as commit_service
import services.file_service as file_service
import services.complexity_service as complexity_service
import services.identifiable_entity_service as identifiable_entity_service
import services.metrics_service as metrics_service
import services.branch_service as branch_service
from services.code_duplication_service import *
import services.file_prioritisation_service as file_prioritisation_service
from database.code_duplication_db_facade import *
from services.metrics_service import * 
import time
import json

def analyse_repo(repo : Repository, commit : Commit):
    calculator : MetricsCalculator = MetricsCalculator(None, repo.id, commit.branch_id, None, None)

    # we need to get the files
    remote_files = github_service.fetch_files(repo.owner, repo.name, commit.sha)

    # store the files in db
    for filename, code in remote_files:
        file = file_service.create_file(filename, commit.id)

        # calculate the various metrics here
        calculator.calculate_cyclomatic_complexity_analysis(file, code)
        calculator.calculate_identifiable_identities_analysis(file, code)

    # duplication analysis with PMD-CPD
    repo_dir = github_service.ensure_local_repo(repo.owner, repo.name)
    db_facade = CodeDuplicationDatabaseFacade()
    cds = CodeDuplicationService(db_facade)
    cds.run_duplication_analyser(20, PmdCdpLanguage.PYTHON, repo_dir)

    return

def get_metrics(commit : Commit, files, include_complexity, include_identifiable_identities, include_code_duplication): 
    metrics = {
        "commit_sha": commit.sha,
        "commit_date": commit.date,
        "commit_message": commit.message,
        "cyclomatic_complexity_analysis": [],
        "identifiable_identities_analysis": [],
        "duplicated_code_analysis": [],
    }

    for file in files:
        if(include_complexity):
             metrics['cyclomatic_complexity_analysis'].append(complexity_service.get_complexity_by_file_id_verbose(file.id))

        if(include_identifiable_identities):
            entities = identifiable_entity_service.get_identifiable_entity_by_file_id_verbose(file.id)
            for entity in entities:
                metrics['identifiable_identities_analysis'].append(entity)
                
    include_code_duplication = True
    if(include_code_duplication):
        db_facade = CodeDuplicationDatabaseFacade()
        cds = CodeDuplicationService(db_facade)
        dup_per_files = cds.get_duplications_for_many_files(files)
        json_list = []

        for k in dup_per_files: 
            json_dup_list = []
            code_dup_list = dup_per_files[k]
            for cd in code_dup_list:
                json_dup_list.append({
                    "id": cd.id,
                    "text": cd.text
                })

            json_list.append({
                "filename": k,
                "duplications": json.dumps(json_dup_list)
            })

        metrics['code_duplication_analysis'] = json.dumps(json_list)

        ##### TEST
        print(metrics['code_duplication_analysis'])

    return metrics

@app.route('/api/display_metrics_by_commit_id', methods=['POST'])
def display_metrics_by_commit_id():
    data = request.get_json()
    repository_id = data.get('repository_id') 
    branch_id = data.get('branch_id')
    commit_id = data.get('commit_id')
    include_complexity = data.get('include_complexity')
    include_identifiable_identities = data.get('include_identifiable_identities')
    include_code_duplication = data.get('include_code_duplication')

    #branch = branch_service.get_branch_by_branch_id(branch_id)
    commit = commit_service.get_commit_by_commit_id(commit_id)
    repo = repository_service.get_repository_by_repository_id(repository_id)

    files = file_service.get_files_by_commit_id(commit.id)
    if(files == []): 
        analyse_repo(repo, commit)
        files = file_service.get_files_by_commit_id(commit.id)
    
    # get metrics
    metrics = get_metrics(commit, files, include_complexity, include_identifiable_identities, include_code_duplication)
    return jsonify(metrics)

@app.route('/api/display_debt_evolution', methods=['POST'])
def display_debt_evolution():
    data = request.get_json()

    return