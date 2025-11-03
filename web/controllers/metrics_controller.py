import requests

from flask import Flask
from flask import request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

from app import app
from models import db
from models.model import *

from lizard import analyze_file
from datetime import datetime

import services.github_service as github_service
import services.repository_service as repository_service
import services.branch_service as branch_service
import services.commit_service as commit_service
import services.file_service as file_service
import services.function_service as function_service
import services.complexity_service as complexity_service
import services.file_entity_service as file_entity_service
import services.identifiable_entity_service as identifiable_entity_service


@app.route('/api/display_metrics_by_commit_id', methods=['POST'])
def display_metrics_by_commit_id():
    data = request.get_json()
    repository_id = data.get('repository_id')
    branch_id = data.get('branch_id')
    commit_id = data.get('commit_id')
    include_fixme = data.get('include_fixme')
    include_complexity = data.get('include_complexity')

    commit = commit_service.get_commit_by_commit_id(commit_id)
    repo = repository_service.get_repository_by_repository_id(repository_id)

    cyclomatic_complexity_analysis = []
    identifiable_identities_analysis = []
    code_duplication_analysis

    # check if the commit has files
    files = file_service.get_files_by_commit_id(commit_id)
    if files == []:
        # we need to get the files
        remote_files = github_service.fetch_files(repo.owner, repo.name, commit.commit_sha)

        # store the files in db
        for filename, code in files:
            file = file_service.create_file(filename, commit.id)
            
            # calculate the various metrics here
            cyclomatic_complexity_analysis = calculate_cyclomatic_complexity_analysis(file, code)


    metrics = {
        "commit_sha": commit.sha,
        "commit_date": commit.date,
        "commit_message": commit.message,
        "cyclomatic_complexity_analysis": [],
        "identifiable_identities_analysis": [],
        "duplicated_code_analysis": [],
    }

    # check if the files have their metrics calculated

    #


def calculate_cyclomatic_complexity_analysis(file, code):
    cyclomatic_complexity_analysis = []
    analysis = analyze_file.analyze_source_code(file.name, code)
    for func in analysis.function_list:
        # ensure function record exists
        function = function_service.get_function_by_name_and_file(func.name, file.id)
        if not function:
            function = function_service.create_function(func.name, func.start_line, file.id)

        # update or create complexity
        from web.models.model import Complexity
        existing_complexity = db.session.query(Complexity).filter(
            Complexity.function_id == function.id
        ).first()

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
    print("Files to analyze for TODO/FIXME:", [f[0] for f in files])

    # analyze source code
    analysis_result_list = file_entity_service.analyse(file.name, code)
    for file_entity in analysis_result_list:
        # ensure file entity record exists
        file_entity = file_entity_service.get_file_entity_by_name_and_file(file_entity.name, file.id, filfile_entitye_ent.start_line)
        if not file_entity:
            file_entity = file_entity_service.create_file_entity(file_entity.name, file_entity.start_line, file.id)
        print("file entity saved: ", file_entity.line_position, file_entity.name, file.name)
        # update or create identifiable entity ASK SIMON
        #if file_entity.entity:
            #  file_entity.entity.name = file_ent.kind
        # else:
        #    identifiable_entity_service.create_identifiable_entity(file_ent.kind, file_entity.id)

        identifiable_entity_analysis.append({
            "file": file.name,
            "start_line": file_entity.start_line,
            "entity_name": file_entity.name,
        })
    return identifiable_entity_analysis


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
        commit_date_str = commit_date
        if isinstance(commit_date, str):
            commit_dt = datetime.strptime(commit_date, "%d/%m/%Y %H:%M")
        else:
            commit_dt = commit_date
        commit = commit_service.create_commit(commit_sha, commit_dt, branch.id)
    else:
        commit_date_str = commit_date if isinstance(commit_date, str) else commit.date.strftime("%d/%m/%Y %H:%M")


    # run cyclomatic complexity analysis if requested
    if include_complexity:
        files = github_service.fetch_files(repo.owner, repo.name, commit_sha)
        cyclomatic_complexity_analysis = []

        for filename, code in files:
            # ensure file record exists
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

                # update or create complexity
                from web.models.model import Complexity
                existing_complexity = db.session.query(Complexity).filter(
                    Complexity.function_id == function.id
                ).first()
                
                if existing_complexity:
                    existing_complexity.value = func.cyclomatic_complexity
                    db.session.commit()
                else:
                    complexity_service.create_complexity(func.cyclomatic_complexity, function.id)

                cyclomatic_complexity_analysis.append({
                    "file": filename,
                    "function": func.name,
                    "start_line": func.start_line,
                    "cyclomatic_complexity": func.cyclomatic_complexity
                })

        metrics["cyclomatic_complexity_analysis"] = cyclomatic_complexity_analysis

    # run FIXME / TODO analysis if requested
    if include_fixme:
            files = github_service.fetch_files(repo.owner, repo.name, commit_sha)
            todo_fixme_analysis = []
            print("Files to analyze for TODO/FIXME:", [f[0] for f in files])
            for filename, code in files:
                # ensure file record exists
                file = file_service.get_file_by_filename_and_commit(filename, commit.id)
                if not file:
                    file = file_service.create_file(filename, commit.id)

                # analyze source code
                analysis_result_list = file_entity_service.analyse(filename, code)
                for file_ent in analysis_result_list:
                    print("Found for filename: ", filename)
                    print("found: ", file_ent)
                    # ensure file entity record exists
                    file_entity = file_entity_service.get_file_entity_by_name_and_file(file_ent.name, file.id, file_ent.start_line)
                    if not file_entity:
                        file_entity = file_entity_service.create_file_entity(file_ent.name, file_ent.start_line, file.id)
                    print("file entity saved: ", file_entity.line_position, file_entity.name, filename)
                    # update or create identifiable entity ASK SIMON
                    #if file_entity.entity:
                     #  file_entity.entity.name = file_ent.kind
                   # else:
                    #    identifiable_entity_service.create_identifiable_entity(file_ent.kind, file_entity.id)

                    todo_fixme_analysis.append({
                        "file": filename,
                        "start_line": file_ent.start_line,
                        "entity_name": file_ent.name,
                        #"entity_kind": file_ent.kind
                    })
           # print("metrics: ", todo_fixme_analysis)
            metrics["todo_fixme_analysis"] = todo_fixme_analysis

    return jsonify(metrics)

@app.route('/display_metrics', methods=['POST'])
def display_metrics2():
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
    cyclomatic_complexity_analysis = []
    if include_complexity:
        # Query files for this commit
        from web.models.model import File, Function, Complexity, IdentifiableEntity
        files = db.session.query(File).filter(File.commit_id == commit.id).all()
        
        for file in files:
            # Query functions for this file
            functions = db.session.query(Function).filter(Function.file_id == file.id).all()
            
            for function in functions:
                # Query complexity for this function
                complexity = db.session.query(Complexity).filter(Complexity.function_id == function.id).first()
                
                if complexity:
                    cyclomatic_complexity_analysis.append({
                        "file": file.name,
                        "function": function.name,
                        "start_line": function.line_position,
                        "cyclomatic_complexity": complexity.value
                    })

    metrics["cyclomatic_complexity_analysis"] = cyclomatic_complexity_analysis

    # --- Get FIXME / TODO occurrences (from DB if you persist them) ---
    fixme_analysis = []
    if include_fixme:
        # Models already imported above if include_complexity is true
        if not include_complexity:
            from web.models.model import File, FileIdentifiableIdentitty, IdentifiableEntity
        else:
            from web.models.model import FileIdentifiableIdentitty
        # Query files for this commit
        files = db.session.query(File).filter(File.commit_id == commit.id).all()
        
        for file in files:
            # Query file identifiable identities for this file
            file_entities = db.session.query(FileIdentifiableIdentitty).filter(
                FileIdentifiableIdentitty.file_id == file.id
            ).all()
            
            for fe in file_entities:
                # Get the identifiable entity details
                entity = db.session.query(IdentifiableEntity).filter(
                    IdentifiableEntity.id == fe.entity_id
                ).first()
                
                if entity:
                    fixme_analysis.append({
                        "file": file.name,
                        "entity": entity.name,
                        "line": getattr(fe, 'line_position', None)  # In case line_position exists
                    })

    metrics["fixme_analysis"] = fixme_analysis
    print("Fixme Analysis Metrics:", metrics.get("fixme_analysis", []))
    return jsonify(metrics)