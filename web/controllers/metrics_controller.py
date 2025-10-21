import requests

from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

from app import app

from lizard import analyze_file
from datetime import datetime

import services.github_service as github_service
import services.repository_service as repository_service
import services.branch_service as branch_service
import services.commit_service as commit_service
import services.file_service as file_service
import services.function_service as function_service
import services.complexity_service as complexity_service


@app.route('/calculate_metrics', methods=['POST'])
def calculate_metrics():
    data = request.get_json()

    repository_id = data.get('repository_id')
    branch_id = data.get('branch_id')
    time_period = data.get('time_period')
    include_fixme = data.get('include_fixme')
    include_complexity = data.get('include_complexity')

    # get repository + branch
    repo = repository_service.get_repository_by_repository_id(repository_id)
    branch = branch_service.get_branch_by_branch_id(branch_id)

    # get closest commit
    repo_url = repository_service.get_repository_url_by_repository_id(repository_id)
    commit_sha, commit_date = github_service.get_closest_commit(repo_url, branch.name, time_period)

    # if no commit could be found/resolved, return a clear error instead of inserting nulls
    if not commit_sha or not commit_date:
        return jsonify({
            "error": "No commit found for the selected branch and time. Please pick a later date or verify the branch.",
            "details": {
                "branch": branch.name,
                "time_period": time_period
            }
        }), 400

    # check if commit already exists
    commit = commit_service.get_commit_by_sha(commit_sha)
    if not commit:
        # Preserve original string for UI while creating DB record
        commit_date_str = commit_date
        if isinstance(commit_date, str):
            commit_dt = datetime.strptime(commit_date, "%d/%m/%Y %H:%M")
        else:
            commit_dt = commit_date
        commit = commit_service.create_commit(commit_sha, commit_dt, branch.id)
    else:
        commit_date_str = commit_date if isinstance(commit_date, str) else commit.date.strftime("%d/%m/%Y %H:%M")

    metrics = {
        "commit_sha": commit_sha,
        "commit_date": commit_date_str,
        "commit_message": github_service.get_commit_message(repo_url, commit_sha),
    }

    # run cyclomatic complexity analysis if requested
    if include_complexity:
        files = github_service.fetch_files(repo.owner, repo.name, branch.name, commit_sha)
        cyclomatic_complexity_analysis = []

        for filename, code in files:
            # ensure file record exists in DB
            file = file_service.get_file_by_filename_and_commit(filename, commit.id)
            if not file:
                file = file_service.create_file(filename, commit.id)

            # analyze source code
            analysis = analyze_file.analyze_source_code(filename, code)
            for func in analysis.function_list:
                # ensure function record exists
                function = function_service.get_function_by_name_and_file(func.name, file.id)
                if not function:
                    function = function_service.create_function(func.name, func.start_line, file.id)

                # update or create complexity in DB
                if function.complexity:
                    function.complexity.value = func.cyclomatic_complexity
                else:
                    complexity_service.create_complexity(func.cyclomatic_complexity, function.id)

                cyclomatic_complexity_analysis.append({
                    "file": filename,
                    "function": func.name,
                    "start_line": func.start_line,
                    "cyclomatic_complexity": func.cyclomatic_complexity
                })

        metrics["cyclomatic_complexity_analysis"] = cyclomatic_complexity_analysis

    if include_fixme:
        import services.semgrep_service as semgrep_service
        import services.entity_service as entity_service
        
        files = github_service.fetch_files(repo.owner, repo.name, branch.name, commit_sha)
        fixme_todo_analysis = []

        for filename, code in files:
            # ensure file record exists in DB
            file = file_service.get_file_by_filename_and_commit(filename, commit.id)
            if not file:
                file = file_service.create_file(filename, commit.id)

            # analyze comments with semgrep
            entities = semgrep_service.analyze_comments_with_semgrep(code, filename)
            
            for entity_type, line_number in entities:
                # get or create entity
                entity = entity_service.get_or_create_entity(entity_type)
                
                # create file entity relationship
                file_entity = entity_service.create_file_entity(file.id, entity.id, line_number)
                
                fixme_todo_analysis.append({
                    "file": filename,
                    "entity": entity_type,
                    "line": line_number
                })

        metrics["fixme_analysis"] = fixme_todo_analysis


    return jsonify(metrics)


@app.route('/display_metrics', methods=['POST'])
def display_metrics():
    data = request.get_json()

    repository_id = data.get('repository_id')
    branch_id = data.get('branch_id')
    time_period = data.get('time_period')
    include_fixme = data.get('include_fixme')
    include_complexity = data.get('include_complexity')

    # --- Get repo and branch from DB ---
    branch = branch_service.get_branch_by_branch_id(branch_id)

    # --- Find closest commit from DB (already created by /calculate_metrics) ---
    repo_url = repository_service.get_repository_url_by_repository_id(repository_id)
    commit_sha, commit_date = github_service.get_closest_commit(repo_url, branch.name, time_period)

    commit = commit_service.get_commit_by_sha(commit_sha)
    if not commit:
        return jsonify({"error": "No commit data found for this time period"}), 404
    metrics = {
        "commit_sha": commit_sha,
        # commit_date returned from github_service is already formatted for UI
        "commit_date": commit_date,
        "commit_message": github_service.get_commit_message(repo_url, commit_sha),
    }

    # Get cyclomatic complexity
    if include_complexity:
        cyclomatic_complexity_analysis = []
        for file in commit.files:
            for function in file.functions:
                if function.complexity:
                    cyclomatic_complexity_analysis.append({
                        "file": file.name,
                        "function": function.name,
                        "start_line": function.line_position,
                        "cyclomatic_complexity": function.complexity.value
                    })

    metrics["cyclomatic_complexity_analysis"] = cyclomatic_complexity_analysis

    # --- Get FIXME / TODO occurrences (from DB if you persist them) ---
    if include_fixme:
        fixme_analysis = []
        for file in commit.files:
            for fe in file.file_entities:
                fixme_analysis.append({
                    "file": file.name,
                    "entity": fe.entity.name,
                    "line": fe.line_position
                })

    print("fixme_analysis:", fixme_analysis)
    metrics["fixme_analysis"] = fixme_analysis
   
    return jsonify(metrics)