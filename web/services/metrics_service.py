import uuid
import time
from collections import defaultdict

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


class MetricsClass:
    repo = None
    branch = None

    def __init__(self, repo_id, branch_id):
        self.repo = repository_service.get_repository_by_repository_id(repo_id)
        self.branch = branch_service.get_branch_by_branch_id(branch_id)

    def get_commits_in_date_range(self, start_date, end_date):
        commits_in_range = github_service.get_commits_in_date_range(
            self.repo.owner, self.repo.name, self.branch.name, start_date, end_date
        )

        return commits_in_range

    def ensure_metric_snapshot(self, commit_to_check):
        # check if there is a snapshot of the count of identifiable identities
        existing_counts = IdentifiableEntityCount.query.filter_by(commit_id=commit_to_check.id).all()
        existing_complexity = ComplexityCount.query.filter_by(commit_id=commit_to_check.id).first()

        if existing_counts and existing_complexity:
            # snapshots already calculated for this commit
            return

        try:
            # the snapshot has not yet been calculated, so we calculate it
            remote_files = github_service.fetch_files(self.repo.owner, self.repo.name, commit_to_check.sha)

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
                file = file_service.create_file(filename, commit_to_check.id)

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
                        id = str(uuid.uuid4()),
                        identifiable_entity_id = entity_id,
                        commit_id = commit_to_check.id,
                        count = entity_info["count"],
                    ))

            # Store the complexity summary in the database
            if not existing_complexity:
                average_complexity = total_complexity / function_count if function_count > 0 else 0
                db.session.add(ComplexityCount(
                    id = str(uuid.uuid4()),
                    commit_id = commit_to_check.id,
                    total_complexity = total_complexity,
                    function_count = function_count,
                    average_complexity = average_complexity,
                ))

            db.session.commit()
            print(f"Calculated metrics for commit {commit_to_check.sha}: {sum(info['count'] for info in entity_totals.values())} total identifiable entities, {function_count} functions with total complexity {total_complexity}")

        except Exception as e:
            db.session.rollback()
            print(f"Error calculating metrics for commit {commit_to_check.sha}: {str(e)}")
            raise



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





    

def get_identifiable_entity_counts_for_commit(commit_id):
    """
    Count the number of times an identifiable identity for each one
    
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


def get_complexity_count_for_commit(commit_id):
    """
    Get the complexity counts for multiple commits.
    
    Args:
        commit_ids (list): List of commit IDs
        
    Returns:
        dict: Dictionary with commit_id as keys and complexity data as values
    """

    complexity_count = ComplexityCount.query.filter_by(commit_id=commit_id).first()

    return {
        "total_complexity": complexity_count.total_complexity,
        "function_count": complexity_count.function_count,
        "average_complexity": complexity_count.average_complexity
    }

def calculate_bug_counts_in_range(commits_in_range):
    """
    Receives a list of commits (each being a dict with a 'message' field)
    Counts how many commit messages contain 'bug' or 'fix' (case-insensitive)
    Returns a dict like: {"total": 7}
    """
    linked_bugs = {"total": 0}

    if not commits_in_range:
        return linked_bugs
    else:
        count = 0
        for commit in commits_in_range:
            message = commit.get("message", "").lower()
            if "bug" in message or "fix" in message or "fixes" in message or "fixed" in message:
                count += 1
        linked_bugs["total"] = count
    
    print("Linked bugs count: ", linked_bugs["total"])
    return linked_bugs

def calculate_bug_counts_in_range(commits_in_range):
    """
    Receives a list of commits (each being a dict with a 'message' field)
    Counts how many commit messages contain 'bug' or 'fix' (case-insensitive)
    Returns a dict like: {"total": 7}
    """
    linked_bugs = {"total": 0}

    if not commits_in_range:
        return linked_bugs
    else:
        count = 0
        for commit in commits_in_range:
            message = commit.get("message", "").lower()
            if "bug" in message or "fix" in message or "fixes" in message or "fixed" in message:
                count += 1
        linked_bugs["total"] = count
    
    print("Linked bugs count: ", linked_bugs["total"])
    return linked_bugs


def calculate_debt_evolution(repo_id, branch_id, start_date, end_date):
    print("Calculating bug-related commit counts...")
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

    try:
        metrics_class = MetricsClass(repo_id, branch_id)

        # Get commits in the date range
        commits_in_range = metrics_class.get_commits_in_date_range(start_date, end_date)

        # Initialize timing statistics
        timing_stats = defaultdict(list)
        total_iterations = len(commits_in_range)
        
        print(f"Processing {total_iterations} commits...")

        for i, found_commit in enumerate(commits_in_range, 1):
            iteration_start = time.time()
            
            # 1 - Create commit in database, if missing
            step_start = time.time()
            commit = commit_service.ensure_commit_exists_by_sha(found_commit, branch_id)
            timing_stats['ensure_commit'].append(time.time() - step_start)

            # 2 - Calculate metrics, if the commit was missing
            step_start = time.time()
            metrics_class.ensure_metric_snapshot(commit)
            timing_stats['ensure_metric_snapshot'].append(time.time() - step_start)

            # Get entity counts for current commit, if missing
            step_start = time.time()
            entity_counts = get_identifiable_entity_counts_for_commit(commit.id)
            total_identifiable_entities = 0
            for count in entity_counts.values():
                total_identifiable_entities += count
            timing_stats['get_entity_counts'].append(time.time() - step_start)

            # Get complexity counts for current commit, if missing
            step_start = time.time()
            complexity_count = get_complexity_count_for_commit(commit.id)
            timing_stats['get_complexity_counts'].append(time.time() - step_start)

            # Build result data
            step_start = time.time()
            debt_evolution.append({
                "commit_sha": commit.sha,
                "commit_date": commit.date,
                "commit_author": commit.author,
                "commit_message": commit.message,
                "total_identifiable_entities": total_identifiable_entities,
                "entity_breakdown": entity_counts,
                "complexity_data": complexity_count,
            })
            timing_stats['build_result'].append(time.time() - step_start)
            
            iteration_time = time.time() - iteration_start
            timing_stats['total_iteration'].append(iteration_time)
            
            # Print progress every 10% or every 10 commits (whichever is more frequent)
            progress_interval = max(1, min(10, total_iterations // 10))
            if i % progress_interval == 0 or i == total_iterations:
                print(f"Progress: {i}/{total_iterations} commits processed ({i/total_iterations*100:.1f}%)")

        # Print overall timing statistics
        if timing_stats['total_iteration']:
            total_time = sum(timing_stats['total_iteration'])
            print(f"\n=== Execution Time Analysis ===")
            print(f"Total execution time: {total_time:.2f} seconds")
            print(f"Average time per commit: {total_time/total_iterations:.3f} seconds")
            print(f"\nTime breakdown by function:")

        # Sort by date
        debt_evolution.sort(key=lambda x: x["commit_date"] or "")

        #Bug: this line breaks the a part in debt_evolution.js because it is not json
        #debt_evolution.append({"linked_bugs_total": linked_bugs["total"]})
    except Exception as e:
        print(f"Error calculating debt evolution: {str(e)}")
        raise

    return debt_evolution
