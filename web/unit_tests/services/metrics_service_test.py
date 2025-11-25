# metrics_service_test.py

import pytest

from src.services.metrics_service import calculate_bug_counts_in_range

from src.services import metrics_service
from src.services.metrics_service import MetricsClass


# ---------- Fake classes to simulate dependencies ----------
class FakeRepo:
    owner = "test-owner"
    name = "test-repo"


class FakeBranch:
    name = "main"


# Fake services to inject
class FakeRepositoryService:
    @staticmethod
    def get_repository_by_repository_id(repo_id):
        assert repo_id == 123
        return FakeRepo()


class FakeBranchService:
    @staticmethod
    def get_branch_by_branch_id(branch_id):
        assert branch_id == 456
        return FakeBranch()


class FakeGithubService:
    captured = {}

    @staticmethod
    def get_commits_in_date_range(owner, repo_name, branch_name, start, end):
        FakeGithubService.captured["args"] = (owner, repo_name, branch_name, start, end)
        return [
            {"sha": "abc", "message": "fix bug"},
            {"sha": "def", "message": "refactor"},
        ]



class FakeDBSession:
    def __init__(self):
        self.added = []
        self.commit_called = False
        self.rollback_called = False

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True


class FakeDB:
    def __init__(self, session):
        self.session = session


class FakeCommit:
    def __init__(self, commit_id, sha):
        self.id = commit_id
        self.sha = sha



# ---------- Tests for metrics_service----------
def test_get_commits_in_date_range_uses_services_correctly(monkeypatch):
    # Patch services inside metrics_service module
    monkeypatch.setattr(metrics_service, "repository_service", FakeRepositoryService)
    monkeypatch.setattr(metrics_service, "branch_service", FakeBranchService)
    monkeypatch.setattr(metrics_service, "github_service", FakeGithubService)

    metrics = MetricsClass(repo_id=123, branch_id=456)

    start = "01/01/2025 00:00"
    end = "31/01/2025 23:59"

    # --- act ---
    result = metrics.get_commits_in_date_range(start, end)

    # --- assert ---
    assert result == [
        {"sha": "abc", "message": "fix bug"},
        {"sha": "def", "message": "refactor"},
    ]

    assert FakeGithubService.captured["args"] == (
        "test-owner",
        "test-repo",
        "main",
        start,
        end,
    )






# ---------- Shared test helpers / fixtures (for this module) ----------

@pytest.fixture
def sample_commits():
    return [
        {"message": "Bug: something is broken"},
        {"message": "FIX: capital letters should count"},
        {"message": "This fixes the previous issue"},
        {"message": "We finally fixed the login"},
        {"message": "Random commit without keyword"},
    ]


# ---------- Tests for calculate_bug_counts_in_range ----------

class TestCalculateBugCountsInRange:
    def test_empty_list_returns_zero(self):
        result = calculate_bug_counts_in_range([])
        assert result == {"total": 0}

    def test_no_bug_or_fix_returns_zero(self):
        commits = [
            {"message": "Refactor code"},
            {"message": "Add new feature"},
        ]
        result = calculate_bug_counts_in_range(commits)
        assert result == {"total": 0}

    def test_counts_all_matching_commits(self, sample_commits):
        result = calculate_bug_counts_in_range(sample_commits)
        assert result == {"total": 4}

    def test_ignores_missing_message_key(self):
        commits = [
            {},  # no message
            {"message": "fix small bug"},
            {"msg": "wrong key"},
        ]
        result = calculate_bug_counts_in_range(commits)
        assert result == {"total": 1}

    def test_missing_message_key(self):
        commits = [
            {},                           # no message
            {"msg": "this key is wrong"}, # still no "message"
            {"message": "fix bug"},       # valid one
        ]
        result = calculate_bug_counts_in_range(commits)
        assert result == {"total": 1}

    def test_no_matching_keywords(self):
        commits = [
            {"message": "refactor code"},
            {"message": "add new feature"},
            {"message": "update documentation"},
        ]
        result = calculate_bug_counts_in_range(commits)
        assert result == {"total": 0}

    def test_mixed_messages_counting_bug_fix_variants(self):
        commits = [
            {"message": "Bug: something happened"},         # bug
            {"message": "FIX this today"},                  # fix
            {"message": "this fixes issue #22"},            # fixes
            {"message": "login flow fixed last week"},      # fixed
            {"message": "random update"},                   # none
        ]
        result = calculate_bug_counts_in_range(commits)
        assert result == {"total": 4}

    def test_case_insensitive_matching(self):
        commits = [
            {"message": "BUG found"},     # uppercase
            {"message": "Fix auth"},      # capitalized
            {"message": "fIxEs logout"},  # mixed case
            {"message": "FiXeD it"},      # mixed case
        ]
        result = calculate_bug_counts_in_range(commits)
        assert result == {"total": 4}







# ---------- Tests for ensure_metric_snapshot ----------
class TestEnsureMetricSnapshot:

    def test_returns_early_when_snapshot_already_exists(self, monkeypatch):
        """
        If IdentifiableEntityCount and ComplexityCount already exist,
        ensure_metric_snapshot should RETURN without:
        - calling github_service.fetch_files
        - calling calculate_* functions
        - adding anything to the DB
        - committing
        """

        # Fake queries that simulate existing data
        class FakeICQuery:
            def filter_by(self, **kwargs):
                return self

            def all(self):
                return ["existing-entity-count"]  # non-empty => truthy

        class FakeCCQuery:
            def filter_by(self, **kwargs):
                return self

            def first(self):
                return "existing-complexity-count"

        class FakeIdentifiableEntityCount:
            query = FakeICQuery()

        class FakeComplexityCount:
            query = FakeCCQuery()

        # Fake github + calc functions that should NOT be called
        class FakeGithubService:
            called = False

            @staticmethod
            def fetch_files(*args, **kwargs):
                FakeGithubService.called = True
                return []

        def fake_calc_identifiable(*args, **kwargs):
            raise AssertionError("calculate_identifiable_identities_analysis should not be called")

        def fake_calc_complexity(*args, **kwargs):
            raise AssertionError("calculate_cyclomatic_complexity_analysis should not be called")

        # Fake DB
        fake_session = FakeDBSession()
        fake_db = FakeDB(fake_session)

        # Patch everything into metrics_service
        monkeypatch.setattr(metrics_service, "repository_service", FakeRepositoryService)
        monkeypatch.setattr(metrics_service, "branch_service", FakeBranchService)
        monkeypatch.setattr(metrics_service, "IdentifiableEntityCount", FakeIdentifiableEntityCount)
        monkeypatch.setattr(metrics_service, "ComplexityCount", FakeComplexityCount)
        monkeypatch.setattr(metrics_service, "github_service", FakeGithubService)
        monkeypatch.setattr(metrics_service, "calculate_identifiable_identities_analysis", fake_calc_identifiable)
        monkeypatch.setattr(metrics_service, "calculate_cyclomatic_complexity_analysis", fake_calc_complexity)
        monkeypatch.setattr(metrics_service, "db", fake_db)

        metrics = MetricsClass(repo_id=123, branch_id=456)
        commit = FakeCommit(commit_id=1, sha="abc123")

        # act
        result = metrics.ensure_metric_snapshot(commit)

        # assert
        assert result is None
        assert FakeGithubService.called is False
        assert fake_session.added == []
        assert fake_session.commit_called is False
        assert fake_session.rollback_called is False



    def test_creates_metrics_when_no_snapshot_exists(self, monkeypatch):
        """
        When there is NO IdentifiableEntityCount / ComplexityCount yet:
        - fetch_files should be called
        - calculate_* should be called for each file
        - IdentifiableEntityCount + ComplexityCount rows should be added
        - db.session.commit() should be called
        """

        # --- Fake queries: no existing rows --- #
        class FakeICQuery:
            def filter_by(self, **kwargs):
                return self

            def all(self):
                return []  # no existing entity counts

        class FakeCCQuery:
            def filter_by(self, **kwargs):
                return self

            def first(self):
                return None  # no existing complexity summary

        class FakeIdentifiableEntityCount:
            query = FakeICQuery()

            def __init__(self, id, identifiable_entity_id, commit_id, count):
                self.id = id
                self.identifiable_entity_id = identifiable_entity_id
                self.commit_id = commit_id
                self.count = count

        class FakeComplexityCount:
            query = FakeCCQuery()

            def __init__(self, id, commit_id, total_complexity, function_count, average_complexity):
                self.id = id
                self.commit_id = commit_id
                self.total_complexity = total_complexity
                self.function_count = function_count
                self.average_complexity = average_complexity

        # --- Fake identifiable entities --- #
        class FakeIdentifiableEntity:
            def __init__(self, entity_id, name):
                self.id = entity_id
                self.name = name

        class FakeIdentifiableEntityService:
            @staticmethod
            def get_all_identifiable_entities():
                return [
                    FakeIdentifiableEntity("e1", "PASSWORD"),
                    FakeIdentifiableEntity("e2", "API_KEY"),
                ]

        # --- Fake files returned by github_service --- #
        class FakeGithubService:
            called_with = None

            @staticmethod
            def fetch_files(owner, repo_name, sha):
                FakeGithubService.called_with = (owner, repo_name, sha)
                # (filename, code)
                return [
                    ("file1.py", "code1"),
                    ("file2.py", "code2"),
                ]

        # --- Fake file objects + file_service --- #
        class FakeFile:
            def __init__(self, name, commit_id):
                self.id = f"file-{name}"
                self.name = name
                self.commit_id = commit_id

        class FakeFileService:
            @staticmethod
            def create_file(filename, commit_id):
                return FakeFile(filename, commit_id)

        # --- Fake analysis functions --- #
        ident_calls = []
        cycl_calls = []

        def fake_calc_identifiable(file, code):
            ident_calls.append((file.name, code))
            if file.name == "file1.py":
                # Two PASSWORD occurrences
                return [
                    {"file": file.name, "start_line": 10, "entity_name": "PASSWORD"},
                    {"file": file.name, "start_line": 20, "entity_name": "PASSWORD"},
                ]
            else:
                # One API_KEY occurrence
                return [
                    {"file": file.name, "start_line": 5, "entity_name": "API_KEY"},
                ]

        def fake_calc_complexity(file, code):
            cycl_calls.append((file.name, code))
            if file.name == "file1.py":
                return [
                    {
                        "file": file.name,
                        "function": "f1",
                        "start_line": 1,
                        "cyclomatic_complexity": 3,
                    }
                ]
            else:
                return [
                    {
                        "file": file.name,
                        "function": "f2",
                        "start_line": 1,
                        "cyclomatic_complexity": 7,
                    }
                ]

        # --- Fake DB --- #
        fake_session = FakeDBSession()
        fake_db = FakeDB(fake_session)

        # --- Patch everything into metrics_service --- #
        monkeypatch.setattr(metrics_service, "repository_service", FakeRepositoryService)
        monkeypatch.setattr(metrics_service, "branch_service", FakeBranchService)
        monkeypatch.setattr(metrics_service, "IdentifiableEntityCount", FakeIdentifiableEntityCount)
        monkeypatch.setattr(metrics_service, "ComplexityCount", FakeComplexityCount)
        monkeypatch.setattr(metrics_service, "identifiable_entity_service", FakeIdentifiableEntityService)
        monkeypatch.setattr(metrics_service, "github_service", FakeGithubService)
        monkeypatch.setattr(metrics_service, "file_service", FakeFileService)
        monkeypatch.setattr(metrics_service, "calculate_identifiable_identities_analysis", fake_calc_identifiable)
        monkeypatch.setattr(metrics_service, "calculate_cyclomatic_complexity_analysis", fake_calc_complexity)
        monkeypatch.setattr(metrics_service, "db", fake_db)

        metrics = MetricsClass(repo_id=123, branch_id=456)
        commit = FakeCommit(commit_id=42, sha="abc123")

        # --- act ---
        result = metrics.ensure_metric_snapshot(commit)

        # --- assert ---
        assert result is None

        # github_service called correctly
        assert FakeGithubService.called_with == ("test-owner", "test-repo", "abc123")

        # analysis functions called for each file
        assert {name for (name, _) in ident_calls} == {"file1.py", "file2.py"}
        assert {name for (name, _) in cycl_calls} == {"file1.py", "file2.py"}

        # DB: check what was added
        entity_counts = [obj for obj in fake_session.added if isinstance(obj, FakeIdentifiableEntityCount)]
        complexity_rows = [obj for obj in fake_session.added if isinstance(obj, FakeComplexityCount)]

        # 2 entity types (PASSWORD, API_KEY)
        assert len(entity_counts) == 2
        counts_by_entity = {ec.identifiable_entity_id: ec.count for ec in entity_counts}
        # PASSWORD (e1) seen twice, API_KEY (e2) once
        assert counts_by_entity == {"e1": 2, "e2": 1}
        # commit id propagated
        assert {ec.commit_id for ec in entity_counts} == {42}

        # 1 complexity summary
        assert len(complexity_rows) == 1
        row = complexity_rows[0]
        # complexity values from fake_calc_complexity: 3 + 7
        assert row.total_complexity == 10
        assert row.function_count == 2
        assert row.average_complexity == 5
        assert row.commit_id == 42

        # commit should be called once, rollback not
        assert fake_session.commit_called is True
        assert fake_session.rollback_called is False



    def test_error_rolls_back_and_reraises(self, monkeypatch):
        """
        If something fails while calculating metrics,
        - db.session.rollback() must be called
        - exception must be re-raised
        - commit must NOT be called
        """

        # No existing rows
        class FakeICQuery:
            def filter_by(self, **kwargs):
                return self

            def all(self):
                return []

        class FakeCCQuery:
            def filter_by(self, **kwargs):
                return self

            def first(self):
                return None

        class FakeIdentifiableEntityCount:
            query = FakeICQuery()

            def __init__(self, *args, **kwargs):
                pass  # won't be used in this error scenario

        class FakeComplexityCount:
            query = FakeCCQuery()

            def __init__(self, *args, **kwargs):
                pass  # won't be used in this error scenario

        # Fake services
        class FakeIdentifiableEntity:
            def __init__(self, entity_id, name):
                self.id = entity_id
                self.name = name

        class FakeIdentifiableEntityService:
            @staticmethod
            def get_all_identifiable_entities():
                return [FakeIdentifiableEntity("e1", "PASSWORD")]

        class FakeGithubService:
            @staticmethod
            def fetch_files(owner, repo_name, sha):
                return [("file1.py", "code1")]

        class FakeFile:
            def __init__(self, name, commit_id):
                self.id = f"file-{name}"
                self.name = name
                self.commit_id = commit_id

        class FakeFileService:
            @staticmethod
            def create_file(filename, commit_id):
                return FakeFile(filename, commit_id)

        def fake_calc_identifiable(file, code):
            # one entity, but we're going to blow up on complexity
            return [{"file": file.name, "start_line": 10, "entity_name": "PASSWORD"}]

        def exploding_complexity(*args, **kwargs):
            raise RuntimeError("boom during complexity")

        fake_session = FakeDBSession()
        fake_db = FakeDB(fake_session)

        # Patch into metrics_service
        monkeypatch.setattr(metrics_service, "repository_service", FakeRepositoryService)
        monkeypatch.setattr(metrics_service, "branch_service", FakeBranchService)
        monkeypatch.setattr(metrics_service, "IdentifiableEntityCount", FakeIdentifiableEntityCount)
        monkeypatch.setattr(metrics_service, "ComplexityCount", FakeComplexityCount)
        monkeypatch.setattr(metrics_service, "identifiable_entity_service", FakeIdentifiableEntityService)
        monkeypatch.setattr(metrics_service, "github_service", FakeGithubService)
        monkeypatch.setattr(metrics_service, "file_service", FakeFileService)
        monkeypatch.setattr(metrics_service, "calculate_identifiable_identities_analysis", fake_calc_identifiable)
        monkeypatch.setattr(metrics_service, "calculate_cyclomatic_complexity_analysis", exploding_complexity)
        monkeypatch.setattr(metrics_service, "db", fake_db)

        metrics = MetricsClass(repo_id=123, branch_id=456)
        commit = FakeCommit(commit_id=99, sha="deadbeef")

        with pytest.raises(RuntimeError, match="boom during complexity"):
            metrics.ensure_metric_snapshot(commit)

        # rollback should be called, commit must not
        assert fake_session.rollback_called is True
        assert fake_session.commit_called is False
