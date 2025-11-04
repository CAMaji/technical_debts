from flask import request, jsonify

from app import app

import services.github_service as github_service
import services.repository_service as repository_service
import services.commit_service as commit_service
import services.file_service as file_service
import services.complexity_service as complexity_service
import services.identifiable_entity_service as identifiable_entity_service
import services.metrics_service as metrics_service


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

    cyclomatic_complexity_analysis = []
    identifiable_identities_analysis = []
    code_duplication_analysis = []

    # check if the commit has files
    files = file_service.get_files_by_commit_id(commit_id)
    if files == []:
        # we need to get the files
        remote_files = github_service.fetch_files(repo.owner, repo.name, commit.sha)

        # store the files in db
        for filename, code in remote_files:
            print(filename)
            file = file_service.create_file(filename, commit.id)
            
            # calculate the various metrics here
            cyclomatic_complexity_analysis = metrics_service.calculate_cyclomatic_complexity_analysis(file, code)
            identifiable_identities_analysis = metrics_service.calculate_identifiable_identities_analysis(file, code)
    else:
        for file in files:
            cyclomatic_complexity_analysis.append(complexity_service.get_complexity_by_file_id_verbose(file.id))

            entities = identifiable_entity_service.get_identifiable_entity_by_file_id_verbose(file.id)
            for entity in entities:
                identifiable_identities_analysis.append(entity)

    metrics = {
        "commit_sha": commit.sha,
        "commit_date": commit.date,
        "commit_message": commit.message,
        "cyclomatic_complexity_analysis": [],
        "identifiable_identities_analysis": [],
        "duplicated_code_analysis": [],
    }

    # add the metrics analysis only if requested
    if include_complexity:
        metrics["cyclomatic_complexity_analysis"] = cyclomatic_complexity_analysis

    if include_identifiable_identities:
        metrics["identifiable_identities_analysis"] = identifiable_identities_analysis

    return jsonify(metrics)
