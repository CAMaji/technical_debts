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
from services.project_search_handler import ProjectSearchHandler


class MetricsCalculator:
    """
    A class for calculating and managing technical debt metrics.
    Handles cyclomatic complexity analysis, identifiable entity counting,
    and debt evolution tracking.
    """
    
    def __init__(self, search_handler=None, repo_id=None, branch_id=None, start_date=None, end_date=None):
        """
        Initialize the MetricsCalculator.
        
        Args:
            search_handler (ProjectSearchHandler, optional): Pre-configured search handler (preferred)
            repo_id (str, optional): Repository ID (fallback if no search_handler)
            branch_id (str, optional): Branch ID (fallback if no search_handler)  
            start_date (str, optional): Start date (fallback if no search_handler)
            end_date (str, optional): End date (fallback if no search_handler)
        """
        if search_handler:
            # Preferred: Use provided search handler as the single source of truth
            self.search_handler = search_handler
        elif repo_id and branch_id:
            # Fallback: Create search handler from individual parameters
            repo = repository_service.get_repository_by_repository_id(repo_id)
            branch = branch_service.get_branch_by_branch_id(branch_id)
            self.search_handler = ProjectSearchHandler(repo, branch, start_date, end_date)
        else:
            raise ValueError("Must provide either search_handler or repo_id/branch_id")

    @property
    def repo(self):
        """Get repository from search handler."""
        return self.search_handler.repository if self.search_handler else None
    
    @property
    def branch(self):
        """Get branch from search handler."""
        return self.search_handler.branch if self.search_handler else None
    
    @property
    def repo_id(self):
        """Get repository ID."""
        return getattr(self.repo, 'id', None) if self.repo else None
    
    @property
    def branch_id(self):
        """Get branch ID."""
        return getattr(self.branch, 'id', None) if self.branch else None

    def update_date_range(self, start_date, end_date):
        """
        Update the date range for the search handler.
        
        Args:
            start_date (str): New start date
            end_date (str): New end date
        """
        if not self.search_handler:
            raise ValueError("No search handler available")
        
        # Only create new handler if dates are different
        if (self.search_handler.start_date != start_date or 
            self.search_handler.end_date != end_date):
            self.search_handler = ProjectSearchHandler(
                self.search_handler.repository, 
                self.search_handler.branch, 
                start_date, 
                end_date
            )

    def _initialize_empty_entity_counts(self):
        """Initialize empty counts for all known entities."""
        all_entities = identifiable_entity_service.get_all_identifiable_entities()
        return {entity.name: 0 for entity in all_entities}
    
    def _initialize_empty_complexity_data(self):
        """Initialize empty complexity data structure."""
        return {
            "total_complexity": 0,
            "function_count": 0,
            "average_complexity": 0.0
        }
    
    def calculate_cyclomatic_complexity_analysis(self, file, code):
        """
        Calculate cyclomatic complexity analysis for a file.
        
        Args:
            file: File object
            code (str): Source code content
            
        Returns:
            list: List of complexity analysis data
        """
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

    def calculate_identifiable_identities_analysis(self, file, code):
        """
        Calculate identifiable entities analysis for a file.
        
        Args:
            file: File object
            code (str): Source code content
            
        Returns:
            list: List of identifiable entity analysis data
        """
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

    def _process_file_metrics(self, filename, code, commit_id, entity_totals):
        """
        Process a single file for both identifiable entities and complexity.
        
        Args:
            filename (str): Name of the file
            code (str): Source code content
            commit_id (str): Commit ID
            entity_totals (dict): Dictionary to accumulate entity counts
            
        Returns:
            tuple: (total_complexity, function_count) for this file
        """
        file = file_service.create_file(filename, commit_id)
        
        # Calculate identifiable entities for this file
        identifiable_identities_analysis = self.calculate_identifiable_identities_analysis(file, code)
        
        # Count occurrences by entity type
        for entity_analysis in identifiable_identities_analysis:
            entity_name = entity_analysis["entity_name"]
            # Find the entity ID by name and increment count
            for entity_id, entity_info in entity_totals.items():
                if entity_info["name"] == entity_name:
                    entity_totals[entity_id]["count"] += 1
                    break
        
        # Calculate complexity for this file
        complexity_analysis = self.calculate_cyclomatic_complexity_analysis(file, code)
        
        # Accumulate complexity data
        file_complexity = 0
        file_function_count = len(complexity_analysis)
        for complexity_data in complexity_analysis:
            file_complexity += complexity_data["cyclomatic_complexity"]
        
        return file_complexity, file_function_count

    def _store_metrics_to_database(self, commit_id, entity_totals, total_complexity, function_count, existing_counts, existing_complexity):
        """Store calculated metrics to the database."""
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

    def ensure_branch_commit_history(self, commits_in_range=None):
        """
        Ensure commits from date range are in the database with calculated metrics.
        
        Args:
            commits_in_range (list, optional): List of commit data. If None, uses search handler.
        """
        if not self.search_handler:
            raise ValueError("Search handler must be available")
            
        # Use search handler's commits if not provided
        if commits_in_range is None:
            if self.search_handler.commits_in_range is None:
                commits_in_range = self.search_handler.get_commits_in_date_range()
            else:
                commits_in_range = self.search_handler.commits_in_range
            
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
                    commit = commit_service.create_commit(commit_in_range["sha"], commit_date, commit_in_range["author"], commit_in_range["message"], self.branch_id)
                    self.ensure_metric_snapshots(commit.id)
                    created_count += 1
                else:
                    # commit exists, but we still need to ensure metrics are calculated
                    self.ensure_metric_snapshots(found_commit.id)
                    existing_count += 1
            except Exception as e:
                print(f"Error processing commit {commit_in_range.get('sha', 'unknown')}: {str(e)}")
                failed_count += 1
                continue
        
        print(f"Commit processing summary: {created_count} created, {existing_count} existing, {failed_count} failed")
            
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
                    commit = commit_service.create_commit(commit_in_range["sha"], commit_date, commit_in_range["author"], commit_in_range["message"], self.branch_id)
                    self.ensure_metric_snapshots(commit.id)
                    created_count += 1
                else:
                    # commit exists, but we still need to ensure metrics are calculated
                    self.ensure_metric_snapshots(found_commit.id)
                    existing_count += 1
            except Exception as e:
                print(f"Error processing commit {commit_in_range.get('sha', 'unknown')}: {str(e)}")
                failed_count += 1
                continue
        
        print(f"Commit processing summary: {created_count} created, {existing_count} existing, {failed_count} failed")

    def ensure_metric_snapshots(self, commit_id):
        """
        Ensure metric snapshots are calculated for a commit.
        
        Args:
            commit_id (str): Commit ID
        """
        if not self.search_handler:
            raise ValueError("Search handler must be available")
            
        commit = commit_service.get_commit_by_commit_id(commit_id)

        # Check if there is a snapshot of the count of identifiable identities
        existing_counts = IdentifiableEntityCount.query.filter_by(commit_id=commit_id).all()
        existing_complexity = ComplexityCount.query.filter_by(commit_id=commit_id).first()
        
        if existing_counts and existing_complexity:
            # snapshots already calculated for this commit
            return

        try:
            # The snapshot has not yet been calculated, so we calculate it
            remote_files = github_service.fetch_files(self.repo.owner, self.repo.name, commit.sha)

            # Initialize counters for each identifiable entity type
            identifiable_entities = identifiable_entity_service.get_all_identifiable_entities()
            entity_totals = {entity.id: {"name": entity.name, "count": 0} for entity in identifiable_entities}

            # Initialize complexity tracking
            total_complexity = 0
            function_count = 0

            # Process each file and accumulate counts
            for filename, code in remote_files:
                file_complexity, file_function_count = self._process_file_metrics(filename, code, commit_id, entity_totals)
                total_complexity += file_complexity
                function_count += file_function_count

            # Store metrics to database
            self._store_metrics_to_database(commit_id, entity_totals, total_complexity, function_count, existing_counts, existing_complexity)
            
            db.session.commit()
            print(f"Calculated metrics for commit {commit.sha}: {sum(info['count'] for info in entity_totals.values())} total identifiable entities, {function_count} functions with total complexity {total_complexity}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error calculating metrics for commit {commit.sha}: {str(e)}")
            raise

    def get_identifiable_entity_counts_for_commit(self, commit_id):
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

    def get_identifiable_entity_counts_for_commits(self, commit_ids):
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

    def get_complexity_counts_for_commits(self, commit_ids):
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

    def calculate_debt_evolution(self, start_date=None, end_date=None):
        """
        Calculate the evolution of technical debt (identifiable entities) over time.
        
        Args:
            start_date (str, optional): Start date in format "dd/mm/YYYY HH:MM". 
                                       If None, uses search handler's dates.
            end_date (str, optional): End date in format "dd/mm/YYYY HH:MM".
                                     If None, uses search handler's dates.
            
        Returns:
            list: List of debt evolution data points
        """
        # Update dates if provided
        if start_date and end_date:
            self.update_date_range(start_date, end_date)
        elif not self.search_handler:
            raise ValueError("Must provide dates or have search handler with dates")
            
        debt_evolution = []

        try:
            # Use search handler to get commits in the date range
            commits_in_range = self.search_handler.get_commits_in_date_range()
            
            print(f"Found {len(commits_in_range)} commits from GitHub API in date range")
            
            # Ensure all commits are in database with calculated metrics
            self.ensure_branch_commit_history()
            
            # Process commits for database lookup
            commit_ids, commit_lookup, missing_commits = self.search_handler.process_commits_for_database()
            
            # Get entity counts for all commits
            entity_counts = self.get_identifiable_entity_counts_for_commits(commit_ids)
            
            # Get complexity counts for all commits
            complexity_counts = self.get_complexity_counts_for_commits(commit_ids)
            
            # Build evolution data - include all commits even if they don't have entity data
            for commit_id in commit_ids:
                commit_info = commit_lookup[commit_id]
                counts = entity_counts.get(commit_id, {}) or self._initialize_empty_entity_counts()
                complexity_data = complexity_counts.get(commit_id, {}) or self._initialize_empty_complexity_data()
                
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


# Backwards compatibility - function wrappers for existing API
def calculate_cyclomatic_complexity_analysis(file, code):
    """Backwards compatibility wrapper."""
    calculator = MetricsCalculator()
    return calculator.calculate_cyclomatic_complexity_analysis(file, code)


def calculate_identifiable_identities_analysis(file, code):
    """Backwards compatibility wrapper."""
    calculator = MetricsCalculator()
    return calculator.calculate_identifiable_identities_analysis(file, code)


def ensure_branch_commit_history(repo_id, branch_id, commits_in_range):
    """Backwards compatibility wrapper."""
    calculator = MetricsCalculator(repo_id, branch_id)
    return calculator.ensure_branch_commit_history(commits_in_range)


def ensure_metric_snapshots(repo_id, commit_id):
    """Backwards compatibility wrapper."""
    calculator = MetricsCalculator(repo_id)
    return calculator.ensure_metric_snapshots(commit_id)


def get_identifiable_entity_counts_for_commit(commit_id):
    """Backwards compatibility wrapper."""
    calculator = MetricsCalculator()
    return calculator.get_identifiable_entity_counts_for_commit(commit_id)


def get_identifiable_entity_counts_for_commits(commit_ids):
    """Backwards compatibility wrapper."""
    calculator = MetricsCalculator()
    return calculator.get_identifiable_entity_counts_for_commits(commit_ids)


def get_complexity_counts_for_commits(commit_ids):
    """Backwards compatibility wrapper."""
    calculator = MetricsCalculator()
    return calculator.get_complexity_counts_for_commits(commit_ids)


def calculate_debt_evolution(repo_id, branch_id, start_date, end_date):
    """Backwards compatibility wrapper."""
    calculator = MetricsCalculator(repo_id, branch_id)
    return calculator.calculate_debt_evolution(start_date, end_date)
