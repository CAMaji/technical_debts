import uuid
from datetime import datetime, timezone

from models import db
from models.model import *

from lizard import analyze_file
import services.function_service as function_service
import services.complexity_service as complexity_service
import services.identifiable_entity_service as identifiable_entity_service
import services.github_service as github_service
import services.repository_service as repository_service
import services.branch_service as branch_service
import services.commit_service as commit_service
import services.file_service as file_service


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
    identities = identifiable_entity_service.get_all_identifiable_entities()
    for identity in identities:
        # search the file for the identity (e.g. <TODO>, <FIXME>)
        found_identities = identifiable_entity_service.search_identifable_entity(code, identity.name)

        # link the found identity to the file it was found in
        for line in found_identities:
            identifiable_entity_service.create_file_entity(identity.id, file.id, line)

            identifiable_entity_analysis.append({
                "file": file.name,
                "start_line": line,
                "entity_name": identity.name,
            })

    return identifiable_entity_analysis


# get all the commits in the specified range of date
# commits_in_range = github_service.get_commits_in_date_range(repo.owner, repo.name, branch.name, start_date, end_date)

def ensure_branch_commit_history(repo_id, branch_id, commits_in_range):
    # check if the database contains each commit
    created_count = 0
    existing_count = 0
    failed_count = 0
    
    for commit_in_range in commits_in_range:
        try:
            found_commit = commit_service.get_commit_by_sha(commit_in_range["sha"])
            if not found_commit:
                # no commit found, so we create it
                # Convert date string to datetime object - GitHub API returns ISO format
                commit_date = datetime.fromisoformat(commit_in_range["date"].replace('Z', '+00:00'))
                commit = commit_service.create_commit(commit_in_range["sha"], commit_date, commit_in_range["author"], commit_in_range["message"], branch_id)
                ensure_metric_snapshots(repo_id, commit.id)
                created_count += 1
            else:
                # commit exists, but we still need to ensure metrics are calculated
                ensure_metric_snapshots(repo_id, found_commit.id)
                existing_count += 1
        except Exception as e:
            print(f"Error processing commit {commit_in_range.get('sha', 'unknown')}: {str(e)}")
            failed_count += 1
            continue
    
    print(f"Commit processing summary: {created_count} created, {existing_count} existing, {failed_count} failed")


def ensure_metric_snapshots(repo_id, commit_id):
    repo = repository_service.get_repository_by_repository_id(repo_id)
    commit = commit_service.get_commit_by_commit_id(commit_id)

    # check if there is a snapshot of the count of identifiable identities
    existing_counts = IdentifiableEntityCount.query.filter_by(commit_id=commit_id).all()
    existing_complexity = ComplexityCount.query.filter_by(commit_id=commit_id).first()
    
    if existing_counts and existing_complexity:
        # snapshots already calculated for this commit
        return

    try:
        # the snapshot has not yet been calculated, so we calculate it
        remote_files = github_service.fetch_files(repo.owner, repo.name, commit.sha)

        # Initialize counters for each identifiable entity type
        identifiable_entities = identifiable_entity_service.get_all_identifiable_entities()
        entity_totals = {}
        for entity in identifiable_entities:
            entity_totals[entity.id] = {"name": entity.name, "count": 0}

        # Initialize complexity tracking
        total_complexity = 0
        function_count = 0
        complexity_values = []

        # Process each file and accumulate counts
        for filename, code in remote_files:
            file = file_service.create_file(filename, commit.id)
            
            # calculate identifiable entities for this file
            identifiable_identities_analysis = calculate_identifiable_identities_analysis(file, code)
            
            # Count occurrences by entity type
            for entity_analysis in identifiable_identities_analysis:
                entity_name = entity_analysis["entity_name"]
                # Find the entity ID by name
                for entity_id, entity_info in entity_totals.items():
                    if entity_info["name"] == entity_name:
                        entity_totals[entity_id]["count"] += 1
                        break

            # calculate complexity for this file
            complexity_analysis = calculate_cyclomatic_complexity_analysis(file, code)
            
            # Accumulate complexity data
            for complexity_data in complexity_analysis:
                complexity_value = complexity_data["cyclomatic_complexity"]
                total_complexity += complexity_value
                function_count += 1
                complexity_values.append(complexity_value)

        # Store the entity counts in the database
        if not existing_counts:
            for entity_id, entity_info in entity_totals.items():
                db.session.add(IdentifiableEntityCount(
                    id=str(uuid.uuid4()),
                    identifiable_entity_id=entity_id,
                    commit_id=commit_id,
                    count=entity_info["count"],
                ))

        # Store the complexity summary in the database
        if not existing_complexity:
            average_complexity = total_complexity / function_count if function_count > 0 else 0
            db.session.add(ComplexityCount(
                id=str(uuid.uuid4()),
                commit_id=commit_id,
                total_complexity=total_complexity,
                function_count=function_count,
                average_complexity=average_complexity,
            ))
        
        db.session.commit()
        print(f"Calculated metrics for commit {commit.sha}: {sum(info['count'] for info in entity_totals.values())} total identifiable entities, {function_count} functions with total complexity {total_complexity}")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error calculating metrics for commit {commit.sha}: {str(e)}")
        raise

    return


def get_identifiable_entity_counts_for_commit(commit_id):
    """
    Get the total counts of identifiable entities for a specific commit.
    
    Args:
        commit_id (str): The commit ID
        
    Returns:
        dict: Dictionary with entity names as keys and counts as values
    """
    counts = IdentifiableEntityCount.query.filter_by(commit_id=commit_id).all()
    result = {}
    
    for count in counts:
        entity = IdentifiableEntity.query.get(count.identifiable_entity_id)
        if entity:
            result[entity.name] = count.count
    
    return result


def get_identifiable_entity_counts_for_commits(commit_ids):
    """
    Get the total counts of identifiable entities for multiple commits.
    
    Args:
        commit_ids (list): List of commit IDs
        
    Returns:
        dict: Dictionary with commit_id as keys and entity counts as values
    """
    if not commit_ids:
        return {}
        
    counts = IdentifiableEntityCount.query.filter(
        IdentifiableEntityCount.commit_id.in_(commit_ids)
    ).all()
    
    result = {}
    for count in counts:
        if count.commit_id not in result:
            result[count.commit_id] = {}
        
        entity = IdentifiableEntity.query.get(count.identifiable_entity_id)
        if entity:
            result[count.commit_id][entity.name] = count.count
    
    return result


def get_complexity_counts_for_commits(commit_ids):
    """
    Get the complexity counts for multiple commits.
    
    Args:
        commit_ids (list): List of commit IDs
        
    Returns:
        dict: Dictionary with commit_id as keys and complexity data as values
    """
    if not commit_ids:
        return {}
        
    complexity_counts = ComplexityCount.query.filter(
        ComplexityCount.commit_id.in_(commit_ids)
    ).all()
    
    result = {}
    for complexity_count in complexity_counts:
        result[complexity_count.commit_id] = {
            "total_complexity": complexity_count.total_complexity,
            "function_count": complexity_count.function_count,
            "average_complexity": complexity_count.average_complexity
        }
    
    return result


def calculate_debt_evolution(repo_id, branch_id, start_date, end_date):
    """
    Calculate the evolution of technical debt (identifiable entities) over time.
    
    Args:
        repo_id (str): Repository ID
        branch_id (str): Branch ID
        start_date (str): Start date in format "dd/mm/YYYY HH:MM"
        end_date (str): End date in format "dd/mm/YYYY HH:MM"
        
    Returns:
        list: List of debt evolution data points
    """
    debt_evolution = []

    repo = repository_service.get_repository_by_repository_id(repo_id)
    branch = branch_service.get_branch_by_branch_id(branch_id)

    try:
        # Get commits in the date range
        commits_in_range = github_service.get_commits_in_date_range(
            repo.owner, repo.name, branch.name, start_date, end_date
        )
        
        print(f"Found {len(commits_in_range)} commits from GitHub API in date range")
        
        # Ensure all commits are in database with calculated metrics
        ensure_branch_commit_history(repo_id, branch_id, commits_in_range)
        
        # Get commit IDs for the commits in range
        commit_ids = []
        commit_lookup = {}
        missing_commits = []
        
        for commit_data in commits_in_range:
            commit = commit_service.get_commit_by_sha(commit_data["sha"])
            if commit:
                commit_ids.append(commit.id)
                commit_lookup[commit.id] = {
                    "sha": commit.sha,
                    "date": commit.date,
                    "author": commit.author,
                    "message": commit.message
                }
            else:
                missing_commits.append(commit_data["sha"])
        
        if missing_commits:
            print(f"Warning: {len(missing_commits)} commits were not found in database: {missing_commits[:5]}{'...' if len(missing_commits) > 5 else ''}")
        
        print(f"Processing {len(commit_ids)} commits found in database")
        
        # Get entity counts for all commits
        entity_counts = get_identifiable_entity_counts_for_commits(commit_ids)
        
        # Get complexity counts for all commits
        complexity_counts = get_complexity_counts_for_commits(commit_ids)
        
        # Build evolution data - include all commits even if they don't have entity data
        for commit_id in commit_ids:
            commit_info = commit_lookup[commit_id]
            counts = entity_counts.get(commit_id, {})
            complexity_data = complexity_counts.get(commit_id, {})
            
            # If no entity counts found, initialize with zeros for all known entities
            if not counts:
                all_entities = identifiable_entity_service.get_all_identifiable_entities()
                counts = {entity.name: 0 for entity in all_entities}
            
            # If no complexity data found, initialize with zeros
            if not complexity_data:
                complexity_data = {
                    "total_complexity": 0,
                    "function_count": 0,
                    "average_complexity": 0.0
                }
            
            total_debt = sum(counts.values())
            
            debt_evolution.append({
                "commit_sha": commit_info["sha"],
                "commit_date": commit_info["date"].isoformat() if commit_info["date"] else None,
                "commit_author": commit_info["author"],
                "commit_message": commit_info["message"],
                "total_identifiable_entities": total_debt,
                "entity_breakdown": counts,
                "complexity_data": complexity_data
            })
        
        # Sort by date
        debt_evolution.sort(key=lambda x: x["commit_date"] or "")
        
    except Exception as e:
        print(f"Error calculating debt evolution: {str(e)}")
        raise

    return debt_evolution
